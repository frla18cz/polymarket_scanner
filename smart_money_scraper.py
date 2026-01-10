import time
import logging
import sqlite3
import concurrent.futures
from datetime import datetime, timezone
from typing import List, Set, Dict, Tuple, Optional

from holders_client import HoldersClient, PnLClient
from main import get_db_connection
from logging_setup import setup_logging

setup_logging("smart_money")
logger = logging.getLogger("polylab.smart_money")

def get_active_market_ids() -> List[str]:
    conn = get_db_connection()
    try:
        # Get distinct market IDs
        rows = conn.execute("SELECT DISTINCT market_id FROM active_market_outcomes").fetchall()
        return [r["market_id"] for r in rows if r["market_id"]]
    finally:
        conn.close()

def save_holders_batch(conn: sqlite3.Connection, market_id: str, holders: List[Dict]):
    # Delete existing for this market to avoid duplicates/stale data for the current snapshot
    conn.execute("DELETE FROM holders WHERE market_id = ?", (market_id,))
    
    snapshot_at = datetime.now(timezone.utc).isoformat()
    
    records = []
    for h in holders:
        addr = h.get("address") or h.get("user")
        # outcomeIndex might be string or int in API
        out_idx = h.get("outcomeIndex") 
        
        pos_size = float(h.get("positionSize") or h.get("size") or 0.0)
        
        if addr:
             records.append((market_id, out_idx, addr, pos_size, snapshot_at))

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

def process_market_holders(market_id: str, holders_client: HoldersClient) -> List[str]:
    """
    Fetches holders for a market, saves them to DB, and returns list of unique wallet addresses found.
    """
    conn = get_db_connection()
    unique_wallets = []
    try:
        data = holders_client.fetch_holders(market_id, limit=50)
        if data:
            save_holders_batch(conn, market_id, data)
            conn.commit()
            
            # Extract unique wallets
            for h in data:
                addr = h.get("address") or h.get("user")
                if addr:
                    unique_wallets.append(addr)
    except Exception as e:
        logger.error(f"Failed to process holders for market {market_id}: {e}")
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

def run():
    logger.info("Starting Smart Money Scraper job...")
    start_time = time.time()
    
    try:
        market_ids = get_active_market_ids()
    except Exception as e:
        logger.error(f"Failed to get active markets: {e}")
        return

    logger.info(f"Found {len(market_ids)} active markets.")
    
    holders_client = HoldersClient()
    
    all_unique_wallets = set()
    
    # 1. Fetch Holders
    # Running serially for now to be gentle on Data API, usually fast enough.
    for i, m_id in enumerate(market_ids):
        wallets = process_market_holders(m_id, holders_client)
        all_unique_wallets.update(wallets)
        if (i + 1) % 50 == 0:
            logger.info(f"Processed holders for {i+1}/{len(market_ids)} markets.")
            
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
    finally:
        conn.close()

    duration = time.time() - start_time
    logger.info(f"Smart Money Scrape completed in {duration:.2f}s")

if __name__ == "__main__":
    run()
