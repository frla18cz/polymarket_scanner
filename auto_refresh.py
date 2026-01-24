import logging
import sys
import os
import csv
import time
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from logging_setup import setup_logging
from runtime_paths import ensure_dir, resolve_repo_path

setup_logging("worker")
logger = logging.getLogger("polylab.worker")

# Ensure we can import scraper and smart money scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper import run_scrape
from smart_money_scraper import run as run_smart_money

def _default_stats_path() -> Path:
    log_dir = Path(os.environ.get("LOG_DIR", "logs"))
    if not log_dir.is_absolute():
        log_dir = resolve_repo_path(log_dir)
    ensure_dir(log_dir)
    return log_dir / "scrape_stats.csv"

STATS_FILE = Path(os.environ.get("SCRAPE_STATS_PATH") or _default_stats_path())

# State for scheduling
_last_smart_money_run = 0
SMART_MONEY_INTERVAL_SECONDS = 6 * 3600  # 6 hours

def log_stats(job_name, duration):
    file_exists = STATS_FILE.exists()
    try:
        with open(STATS_FILE, mode="a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "job_name", "duration_seconds"])
            writer.writerow([datetime.now().isoformat(), job_name, f"{duration:.2f}"])
    except Exception as e:
        logger.warning("Failed to log stats: %s", e)

def job_coordinated_refresh():
    """
    Executes scraper and smart money analysis sequentially to prevent DB locking.
    """
    global _last_smart_money_run
    logger.info("Starting COORDINATED REFRESH cycle")
    
    # 1. Scrape (Market Data)
    logger.info("Step 1/2: Market Data Scrape")
    t0_scrape = time.time()
    scrape_success = False
    try:
        run_scrape()
        duration_scrape = time.time() - t0_scrape
        log_stats("scrape", duration_scrape)
        logger.info("Job SCRAPE finished in %.2fs", duration_scrape)
        scrape_success = True
    except Exception as e:
        logger.exception("Error during SCRAPE: %s. Aborting Smart Money step.", e)
        # We do NOT run smart money if scrape failed to ensure data consistency
        return

    # 2. Smart Money (Holders)
    # Check interval
    now = time.time()
    time_since_last = now - _last_smart_money_run
    
    # We run smart money if interval passed OR if it's the first run (huge time_since_last)
    if time_since_last >= SMART_MONEY_INTERVAL_SECONDS:
        logger.info("Step 2/2: Smart Money Analysis (Interval reached: %.1fh >= 6.0h)", time_since_last / 3600)
        t0_sm = time.time()
        try:
            run_smart_money()
            duration_sm = time.time() - t0_sm
            log_stats("smart_money", duration_sm)
            logger.info("Job SMART_MONEY finished in %.2fs", duration_sm)
            # Only update timestamp if successful? Or always?
            # To avoid retry loops on failure, we update timestamp even if it fails?
            # No, if it fails, maybe we want to retry next hour.
            # But the spec says "Error should be logged".
            # For robustness, let's update timestamp only on success or partial success.
            # But if it fails consistently, we might want to back off.
            # Given "Simple" requirement, let's update timestamp to prevent running it every hour if it fails.
            _last_smart_money_run = time.time() 
        except Exception as e:
            logger.exception("Error during SMART_MONEY: %s", e)
            # We still update timestamp to avoid hammering if it's broken?
            # Or should we try again next hour?
            # Let's NOT update timestamp, so it retries next hour.
            pass
    else:
        logger.info("Step 2/2: Skipping Smart Money (Next run in %.1fh)", (SMART_MONEY_INTERVAL_SECONDS - time_since_last) / 3600)

def start_scheduler():
    scheduler = BlockingScheduler()
    
    # Unified Job: Runs every 1 hour
    # Replaces the previous separate jobs
    scheduler.add_job(
        job_coordinated_refresh,
        trigger=IntervalTrigger(minutes=60),
        id='coordinated_refresh',
        name='Coordinated Refresh (Scrape + Smart Money)',
        replace_existing=True,
        next_run_time=datetime.now() # Start immediately
    )
    
    logger.info("Starting scheduler (Coordinated Refresh: 1h)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()
