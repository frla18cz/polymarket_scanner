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

def process_market_holders(condition_id: str, holders_client: HoldersClient) -> List[str]:
    """
    Fetches holders for a market, saves them to DB, and returns list of unique wallet addresses found.
    """
    conn = get_db_connection()
    unique_wallets = []
    try:
        data = holders_client.fetch_holders(condition_id, limit=50)
        if data:
            save_holders_batch(conn, condition_id, data)
            conn.commit()
            
            # Extract unique wallets
            for h in data:
                addr = h.get("address") or h.get("user")
                if addr:
                    unique_wallets.append(addr)
    except Exception as e:
        logger.error(f"Failed to process holders for market {condition_id}: {e}")
    finally:
        conn.close()
    
    return unique_wallets

def fetch_pnl_worker(wallet: str) -> Tuple[str, float]:
    # Instantiate client per worker (safe)
    client = PnLClient() 
    # Sleep to respect rate limits (distributes load)
    time.sleep(0.3)
    val = client.fetch_user_pnl(wallet)
    return wallet, (val if val is not None else 0.0)

def run(args_list: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="Scrape Smart Money data.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of markets to process (for testing)")
    args = parser.parse_args(args_list)

    logger.info(f"Starting Smart Money Scraper job... (Limit: {args.limit})")
    start_time = time.time()
    
    try:
        condition_ids = get_active_market_ids(limit=args.limit)
    except Exception as e:
        logger.error(f"Failed to get active markets: {e}")
        return

    logger.info(f"Found {len(condition_ids)} active markets to process.")
    
    holders_client = HoldersClient()
    
    all_unique_wallets = set()
    
    # 1. Fetch Holders
    # Running serially for now to be gentle on Data API, usually fast enough.
    for i, c_id in enumerate(condition_ids):
        wallets = process_market_holders(c_id, holders_client)
        all_unique_wallets.update(wallets)
        if (i + 1) % 50 == 0:
            logger.info(f"Processed holders for {i+1}/{len(condition_ids)} markets.")
            
    logger.info(f"Found {len(all_unique_wallets)} unique wallets to analyze.")
    
    # 2. Fetch PnL
    if not all_unique_wallets:
        logger.info("No wallets to process.")
        return

    conn = get_db_connection()
    try:
        # Using 10 workers as per spec
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_wallet = {executor.submit(fetch_pnl_worker, w): w for w in all_unique_wallets}
            
            count = 0
            for future in concurrent.futures.as_completed(future_to_wallet):
                w = future_to_wallet[future]
                try:
                    wallet, pnl = future.result()
                    save_wallet_stats(conn, wallet, pnl)
                    count += 1
                    if count % 50 == 0:
                        conn.commit() # Commit in batches
                        logger.info(f"Processed PnL for {count}/{len(all_unique_wallets)} wallets.")
                except Exception as e:
                    logger.error(f"Error fetching PnL for {w}: {e}")
            
            conn.commit() # Final commit
        
        # 3. Calculate and Update Metrics
        logger.info("Calculating and updating Smart Money metrics...")
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
        logger.info("Metrics update complete.")

    finally:
        conn.close()

    duration = time.time() - start_time
    logger.info(f"Smart Money Scrape completed in {duration:.2f}s")

if __name__ == "__main__":
    run()
