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

def job_scrape():
    logger.info("Starting scheduled job: SCRAPE")
    t0 = time.time()
    try:
        run_scrape()
        duration = time.time() - t0
        log_stats("scrape", duration)
        logger.info("Job SCRAPE finished in %.2fs", duration)
    except Exception as e:
        logger.exception("Error during SCRAPE: %s", e)

def job_smart_money():
    logger.info("Starting scheduled job: SMART_MONEY")
    t0 = time.time()
    try:
        run_smart_money()
        duration = time.time() - t0
        log_stats("smart_money", duration)
        logger.info("Job SMART_MONEY finished in %.2fs", duration)
    except Exception as e:
        logger.exception("Error during SMART_MONEY: %s", e)

def start_scheduler():
    scheduler = BlockingScheduler()
    
    # Job 1: Market data every 1 hour
    scheduler.add_job(
        job_scrape,
        trigger=IntervalTrigger(minutes=60),
        id='scrape_job',
        name='Market Data Scrape',
        replace_existing=True,
        next_run_time=datetime.now() # Start immediately
    )
    
    # Job 2: Smart Money every 6 hours
    scheduler.add_job(
        job_smart_money,
        trigger=IntervalTrigger(minutes=360),
        id='smart_money_job',
        name='Smart Money Analysis',
        replace_existing=True,
        next_run_time=datetime.now() # Start immediately
    )
    
    logger.info("Starting scheduler (Scrape: 1h, Smart Money: 6h)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()