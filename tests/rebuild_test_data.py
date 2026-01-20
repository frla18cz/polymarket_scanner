import os
import sys
import logging
import argparse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from scraper import run_scrape
from smart_money_scraper import run as run_smart_money

def rebuild_data(limit: int = 100):
    """
    Rebuilds the local database with fresh data from Polymarket and Goldsky.
    Useful for ensuring integration tests have realistic data.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logger = logging.getLogger("rebuild_test_data")
    
    db_path = BASE_DIR / "data" / "markets.db"
    logger.info(f"Targeting database: {db_path}")
    logger.warning("This will overwrite existing market data in the local database!")
    
    # 1. Scrape Markets
    logger.info(f"--- Step 1: Scraping {limit} markets ---")
    try:
        run_scrape(limit_count=limit)
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        sys.exit(1)

    # 2. Scrape Holders & Smart Money Stats
    logger.info("--- Step 2: Fetching Holders & Calculating Metrics ---")
    try:
        # Pass explicit limit to smart money scraper as well
        # Note: smart_money_scraper filters by active markets in DB, so it processes what step 1 downloaded.
        # We pass ['--limit', str(limit)] just in case, though it usually iterates over active markets.
        run_smart_money(args_list=[]) 
    except Exception as e:
        logger.error(f"Smart Money Scraper failed: {e}")
        sys.exit(1)

    logger.info("--- Rebuild Complete ---")
    logger.info(f"Database updated at: {db_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild local DB with fresh data for testing.")
    parser.add_argument("--limit", type=int, default=100, help="Number of markets to fetch (default: 100)")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    if not args.yes:
        confirm = input(f"This will OVERWRITE data in {BASE_DIR / 'data' / 'markets.db'}. Continue? [y/N] ")
        if confirm.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    rebuild_data(limit=args.limit)
