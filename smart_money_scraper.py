import time
import logging
import sqlite3
import argparse
import concurrent.futures
from datetime import datetime, timezone
from typing import List, Set, Dict, Tuple, Optional

from holders_client import HoldersClient, PnLClient, GoldskyClient
from main import get_db_connection
from logging_setup import setup_logging

setup_logging("smart_money")
logger = logging.getLogger("polylab.smart_money")

def get_active_market_ids(limit: Optional[int] = None, randomize: bool = False) -> List[str]:
    conn = get_db_connection()
    try:
        # We need the condition_id for the Holders API
        sql = "SELECT DISTINCT condition_id FROM active_market_outcomes WHERE condition_id IS NOT NULL"
        params = []
        if randomize:
            sql += " ORDER BY RANDOM()"
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return [r["condition_id"] for r in rows if r["condition_id"]]
    finally:
        conn.close()

def save_holders_batch(conn: sqlite3.Connection, condition_id: str, holders: List[Dict]):
    # Delete existing for this market to avoid duplicates/stale data for the current snapshot
    conn.execute("DELETE FROM holders WHERE market_id = ?", (condition_id,))
    
    snapshot_at = datetime.now(timezone.utc).isoformat()
    
    records = []
    for h in holders:
        addr = h.get("address") or h.get("user")
        # outcomeIndex might be string or int in API
        out_idx = h.get("outcomeIndex") 
        
        pos_size = float(h.get("positionSize") or h.get("size") or 0.0)
        
        if addr:
             records.append((condition_id, out_idx, addr, pos_size, snapshot_at))

    if records:
        conn.executemany("""
            INSERT INTO holders (market_id, outcome_index, wallet_address, position_size, snapshot_at)
            VALUES (?, ?, ?, ?, ?)
        """, records)

def save_wallet_stats(conn: sqlite3.Connection, wallet: str, pnl: float, alias: Optional[str] = None):
    last_updated = datetime.now(timezone.utc).isoformat()
    
    # Logic: 
    # 1. If alias is provided, update it.
    # 2. If alias is None, keep existing alias (COALESCE).
    
    conn.execute("""
        INSERT INTO wallets_stats (wallet_address, total_pnl, last_updated, alias)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(wallet_address) DO UPDATE SET
            total_pnl = excluded.total_pnl,
            last_updated = excluded.last_updated,
            alias = COALESCE(excluded.alias, wallets_stats.alias)
    """, (wallet, pnl, last_updated, alias))

def process_market_holders_worker(condition_id: str) -> Dict[str, Optional[str]]:
    """
    Worker function to fetch holders for a single market.
    Returns a dict mapping wallet_address -> alias (or None).
    """
    # Small sleep to distribute load
    time.sleep(0.3)
    
    unique_wallets = {} # address -> alias
    data = None

    # 1. Try Goldsky Subgraph
    try:
        goldsky_client = GoldskyClient()
        data = goldsky_client.fetch_holders_subgraph(condition_id)
        if data:
            logger.info(f"Fetched {len(data)} holders from Goldsky for {condition_id}")
    except Exception as e:
        logger.warning(f"Goldsky fetch failed for {condition_id}: {e}")

    # 2. Fallback to Legacy API
    if not data:
        try:
            holders_client = HoldersClient()
            data = holders_client.fetch_holders(condition_id, limit=1000)
            if data:
                logger.info(f"Fetched {len(data)} holders from Legacy API for {condition_id}")
        except Exception as e:
            logger.error(f"Legacy API fetch failed for {condition_id}: {e}")

    if data:
        try:
            # We need a fresh connection per thread for SQLite safety
            conn = get_db_connection()
            try:
                save_holders_batch(conn, condition_id, data)
                conn.commit()
            finally:
                conn.close()
            
            # Extract unique wallets and aliases
            for h in data:
                addr = h.get("address") or h.get("user")
                if addr:
                    # Prefer existing alias if we already found one (though specific to this batch)
                    # Legacy API provides 'name' which is the alias
                    alias = h.get("name") 
                    # If alias is empty string, treat as None
                    if alias == "": 
                        alias = None
                    unique_wallets[addr] = alias
        except Exception as e:
            logger.error(f"Failed to save holders for {condition_id}: {e}")
    else:
        logger.warning(f"No holders data found for market {condition_id} (both Goldsky and Legacy failed).")
    
    return unique_wallets

def fetch_pnl_worker(wallet: str) -> Tuple[str, float]:
    """
    Worker function to fetch PnL for a single wallet with a safety sleep.
    """
    # Sleep to respect rate limits (distributes load across workers)
    time.sleep(0.3)
    client = PnLClient() 
    val = client.fetch_user_pnl(wallet)
    return wallet, (val if val is not None else 0.0)

def get_unique_wallets_from_db() -> Dict[str, Optional[str]]:
    """
    Fetches all unique wallet addresses from the holders table.
    Returns dict {address: None} to match the structure.
    """
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT DISTINCT wallet_address FROM holders").fetchall()
        # We don't have aliases in holders table, so return None
        return {r["wallet_address"]: None for r in rows if r["wallet_address"]}
    finally:
        conn.close()

def run(args_list: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="Scrape Smart Money data.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of markets to process (for testing)")
    parser.add_argument("--randomize", action="store_true", help="Randomize market selection (use with --limit)")
    parser.add_argument("--resume", action="store_true", help="Only fetch PnL for existing wallets in DB")
    args = parser.parse_args(args_list)

    start_time = time.time()
    logger.info(f"Starting Smart Money Scraper job... (Resume mode: {args.resume})")
    
    all_unique_wallets = {} # address -> alias

    if args.resume:
        logger.info("Načítám unikátní peněženky z existující tabulky holders...")
        all_unique_wallets = get_unique_wallets_from_db()
    else:
        try:
            condition_ids = get_active_market_ids(limit=args.limit, randomize=args.randomize)
        except Exception as e:
            logger.error(f"Failed to get active markets: {e}")
            return

        logger.info(f"Found {len(condition_ids)} active markets to process.")
        
        # 1. Fetch Holders (Parallelized)
        logger.info("Faze 1: Stahování holderů pro trhy...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_cid = {executor.submit(process_market_holders_worker, cid): cid for cid in condition_ids}
            
            count = 0
            for future in concurrent.futures.as_completed(future_to_cid):
                wallets_dict = future.result()
                # Update our master dict. If we find an alias later, it overwrites None.
                # If we have an alias and new one is None, we should keep the alias.
                for addr, alias in wallets_dict.items():
                    if addr not in all_unique_wallets:
                        all_unique_wallets[addr] = alias
                    elif all_unique_wallets[addr] is None and alias is not None:
                        all_unique_wallets[addr] = alias
                        
                count += 1
                if count % 100 == 0:
                    logger.info(f"Zpracováno držitelů pro {count}/{len(condition_ids)} trhů.")
            
    logger.info(f"Nalezeno {len(all_unique_wallets)} unikátních peněženek k analýze.")
    
    # 2. Fetch PnL (Parallelized with robust Retry)
    if not all_unique_wallets:
        logger.info("Žádné peněženky ke zpracování.")
        return

    logger.info("Faze 2: Stahování P/L pro peněženky (s Retry logikou)...")
    conn = get_db_connection()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_wallet = {executor.submit(fetch_pnl_worker, w): w for w in all_unique_wallets.keys()}
            
            count = 0
            for future in concurrent.futures.as_completed(future_to_wallet):
                w = future_to_wallet[future]
                try:
                    wallet, pnl = future.result()
                    # Retrieve the alias we found earlier
                    alias = all_unique_wallets.get(wallet)
                    save_wallet_stats(conn, wallet, pnl, alias=alias)
                    count += 1
                    if count % 100 == 0:
                        conn.commit() # Batch commit
                        logger.info(f"Zpracováno P/L pro {count}/{len(all_unique_wallets)} peněženek.")
                except Exception as e:
                    logger.error(f"Kritická chyba při zpracování workeru pro {w}: {e}")
            
            conn.commit() 
        
        # 3. Calculate and Update Metrics
        logger.info("Faze 3: Výpočet a aktualizace Smart Money metrik...")
        conn.execute("""
            UPDATE active_market_outcomes
            SET smart_money_win_rate = (
                SELECT CAST(SUM(CASE WHEN ws.total_pnl > 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*)
                FROM holders h
                JOIN wallets_stats ws ON h.wallet_address = ws.wallet_address
                WHERE h.market_id = active_market_outcomes.condition_id
            )
            WHERE EXISTS (
                SELECT 1 FROM holders h 
                WHERE h.market_id = active_market_outcomes.condition_id
            );
        """)
        conn.commit()
        logger.info("Všechny metriky byly úspěšně aktualizovány.")

    finally:
        conn.close()

    duration = time.time() - start_time
    logger.info(f"Smart Money Scraper dokončen za {duration:.2f}s")

if __name__ == "__main__":
    run()
