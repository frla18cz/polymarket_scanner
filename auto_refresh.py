import time
import datetime
import sys
import os
import csv

# Ensure we can import scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper import run_scrape

INTERVAL_SECONDS = 300  # Update every 5 minutes (adjust as needed)
STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrape_stats.csv")

def log_stats(duration):
    file_exists = os.path.isfile(STATS_FILE)
    with open(STATS_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "duration_seconds"])
        writer.writerow([datetime.datetime.now().isoformat(), f"{duration:.2f}"])

def start_loop():
    print(f"[{datetime.datetime.now()}] Starting Auto-Refresh Loop (Interval: {INTERVAL_SECONDS}s)", flush=True)
    
    while True:
        try:
            print(f"\n--- Running Update Task ---", flush=True)
            t0 = time.time()
            run_scrape()
            duration = time.time() - t0
            log_stats(duration)
            print(f"--- Update Finished in {duration:.2f}s. Sleeping for {INTERVAL_SECONDS}s ---", flush=True)
        except Exception as e:
            print(f"!!! Error during scrape: {e}", flush=True)
        
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        # Check if interval is passed as arg
        if len(sys.argv) > 1:
            INTERVAL_SECONDS = int(sys.argv[1])
    except:
        pass
        
    start_loop()
