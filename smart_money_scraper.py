import time
import logging
import sqlite3
import argparse
import concurrent.futures
from datetime import datetime, timezone
from typing import List, Set, Dict, Tuple, Optional

from holders_client import HoldersClient, PnLClient
from main import get_db_connection
from logging_setup import setup_logging

setup_logging("smart_money")
logger = logging.getLogger("polylab.smart_money")

def get_active_market_ids(limit: Optional[int] = None) -> List[str]:
    conn = get_db_connection()
    try:
        # We need the condition_id for the Holders API
        sql = "SELECT DISTINCT condition_id FROM active_market_outcomes WHERE condition_id IS NOT NULL"
        if limit:
            sql += f" LIMIT {limit}"
        rows = conn.execute(sql).fetchall()
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

def save_wallet_stats(conn: sqlite3.Connection, wallet: str, pnl: float):
    last_updated = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT OR REPLACE INTO wallets_stats (wallet_address, total_pnl, last_updated)
        VALUES (?, ?, ?)
    """, (wallet, pnl, last_updated))

def process_market_holders_worker(condition_id: str) -> List[str]:
    """
    Worker function to fetch holders for a single market.
    """
    # Small sleep to distribute load and respect rate limits
    time.sleep(0.3)
    
    holders_client = HoldersClient()
    unique_wallets = []
    try:
        data = holders_client.fetch_holders(condition_id, limit=1000)
        if data is not None:
            # We need a fresh connection per thread for SQLite safety
            conn = get_db_connection()
            try:
                save_holders_batch(conn, condition_id, data)
                conn.commit()
            finally:
                conn.close()
            
            # Extract unique wallets
            for h in data:
                addr = h.get("address") or h.get("user")
                if addr:
                    unique_wallets.append(addr)
        else:
            logger.warning(f"Skipping market {condition_id} due to validation failure or API error.")
    except Exception as e:
        logger.error(f"Failed to process holders for market {condition_id}: {e}")
    
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

def get_unique_wallets_from_db() -> Set[str]:
    """
    Fetches all unique wallet addresses from the holders table.
    """
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT DISTINCT wallet_address FROM holders").fetchall()
        return {r["wallet_address"] for r in rows if r["wallet_address"]}
    finally:
        conn.close()

def run(args_list: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="Scrape Smart Money data.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of markets to process (for testing)")
    parser.add_argument("--resume", action="store_true", help="Only fetch PnL for existing wallets in DB")
    args = parser.parse_args(args_list)

    start_time = time.time()
    logger.info(f"Starting Smart Money Scraper job... (Resume mode: {args.resume})")
    
    all_unique_wallets = set()

    if args.resume:
        logger.info("Načítám unikátní peněženky z existující tabulky holders...")
        all_unique_wallets = get_unique_wallets_from_db()
    else:
        try:
            condition_ids = get_active_market_ids(limit=args.limit)
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
                wallets = future.result()
                all_unique_wallets.update(wallets)
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
            future_to_wallet = {executor.submit(fetch_pnl_worker, w): w for w in all_unique_wallets}
            
            count = 0
            for future in concurrent.futures.as_completed(future_to_wallet):
                w = future_to_wallet[future]
                try:
                    wallet, pnl = future.result()
                    save_wallet_stats(conn, wallet, pnl)
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
