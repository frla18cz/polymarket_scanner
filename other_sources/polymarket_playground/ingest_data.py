import time
import pandas as pd
import os
from services.db import get_connection, init_db
from services.state import update_stage_completion

CSV_FILE = "data/subgraph_pnl_analysis.csv"
CHUNK_SIZE = 200_000


def ingest_csv_to_duckdb():
    """
    Reads the huge CSV file in chunks and loads it into DuckDB.
    Uses the 'user_positions' table.
    """
    if not os.path.exists(CSV_FILE):
        print(f"Error: Input file {CSV_FILE} not found.")
        return

    print("Initializing database...")
    init_db()
    conn = get_connection()

    print(f"Starting ingestion of {CSV_FILE} into DuckDB...")
    print("Clearing old data from 'user_positions' (full refresh)...")
    conn.execute("DELETE FROM user_positions")

    start_time = time.time()
    total_rows = 0

    try:
        # Using DuckDB's native CSV reader is MUCH faster than Pandas chunking
        # We can use read_csv_auto directly in SQL
        print("Executing bulk load via DuckDB native CSV reader (fast mode)...")

        # We map CSV columns to table columns
        # CSV header: id,user,realizedPnl,avgPrice,totalBought
        # Table: id, user_addr, realizedPnl, avgPrice, totalBought

        # Use INSERT OR IGNORE to skip duplicates (e.g. from retry logic)
        conn.execute(
            f"""
            INSERT OR IGNORE INTO user_positions (id, user_addr, realizedPnl, avgPrice, totalBought)
            SELECT 
                id, 
                "user" as user_addr, 
                CAST(realizedPnl AS DOUBLE), 
                avgPrice, 
                totalBought 
            FROM read_csv_auto('{CSV_FILE}', header=True)
        """
        )

        # Get count
        total_rows = conn.execute("SELECT COUNT(*) FROM user_positions").fetchone()[0]

    except Exception as e:
        print(f"Native load failed ({e}).")
        # Only rollback if a transaction was actually active
        try:
            conn.rollback()
        except Exception:
            pass
        return

    duration = time.time() - start_time
    print(f"Ingestion complete in {duration:.2f} seconds.")
    print(f"Total rows in DB: {total_rows:,}")

    # Update pipeline state
    update_stage_completion("ingestion", stats={"ingested_positions": total_rows})

    conn.close()


if __name__ == "__main__":
    ingest_csv_to_duckdb()
