import time
import datetime
import sys
import os
import csv
import logging
from pathlib import Path

from logging_setup import setup_logging
from runtime_paths import ensure_dir, resolve_repo_path

INTERVAL_SECONDS = 3600  # Update every 1 hour (testing)

setup_logging("worker")
logger = logging.getLogger("polylab.worker")

# Ensure we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper import run_scrape


def _default_stats_path() -> Path:
    log_dir = Path(os.environ.get("LOG_DIR", "logs"))
    if not log_dir.is_absolute():
        log_dir = resolve_repo_path(log_dir)
    ensure_dir(log_dir)
    return log_dir / "scrape_stats.csv"


STATS_FILE = Path(os.environ.get("SCRAPE_STATS_PATH") or _default_stats_path())

def log_stats(duration):
    file_exists = STATS_FILE.exists()
    with open(STATS_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "duration_seconds"])
        writer.writerow([datetime.datetime.now().isoformat(), f"{duration:.2f}"])

def start_loop():
    logger.info("Starting auto-refresh loop (interval=%ss)", INTERVAL_SECONDS)
    
    while True:
        try:
            logger.info("Running update task...")
            t0 = time.time()
            run_scrape()
            duration = time.time() - t0
            log_stats(duration)
            logger.info("Update finished in %.2fs; sleeping for %ss", duration, INTERVAL_SECONDS)
        except Exception as e:
            logger.exception("Error during scrape: %s", e)
        
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        # Check if interval is passed as arg
        if len(sys.argv) > 1:
            INTERVAL_SECONDS = int(sys.argv[1])
    except:
        pass
        
    start_loop()
