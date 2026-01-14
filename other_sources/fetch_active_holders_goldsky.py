import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests

from services.db import get_connection, init_db

SUBGRAPH_URL = (
    "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/"
    "subgraphs/positions-subgraph/0.0.7/gn"
)
MARKETS_FILE = "data/markets_current.csv"
DEFAULT_PAGE_SIZE = 1000
DEFAULT_SLEEP_SECONDS = 0.2
DEFAULT_MAX_WORKERS = 4
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 0.5
DEFAULT_BATCH_SIZE_INSERT = 5000
DEFAULT_MIN_BALANCE = 1
DEFAULT_COUNTS_CSV = "data/market_holders_goldsky_counts.csv"
LOG_EVERY_OUTCOMES = 50

USER_BALANCES_QUERY = """
query GetUserBalances(
  $conditionId: String!
  $outcomeIndex: BigInt!
  $first: Int!
  $skip: Int!
  $minBalance: BigInt!
) {
  userBalances(
    first: $first
    skip: $skip
    where: {
      asset_: { condition: $conditionId, outcomeIndex: $outcomeIndex }
      balance_gt: $minBalance
    }
  ) {
    user
    balance
  }
}
"""


def _safe_json_loads(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, list):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


def _should_retry(status_code: int | None) -> bool:
    return status_code in {429, 500, 502, 503, 504}


def _post_with_retries(
    session: requests.Session,
    payload: dict,
    *,
    max_retries: int,
    backoff_seconds: float,
    condition_id: str,
    outcome_index: int,
):
    attempt = 0
    while attempt < max_retries:
        try:
            response = session.post(SUBGRAPH_URL, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            if data.get("errors"):
                raise ValueError(data["errors"])
            return data
        except (requests.exceptions.RequestException, ValueError) as exc:
            attempt += 1
            status = (
                exc.response.status_code
                if isinstance(exc, requests.exceptions.RequestException)
                and getattr(exc, "response", None)
                else None
            )
            if _should_retry(status) and attempt < max_retries:
                delay = backoff_seconds * (2 ** (attempt - 1))
                time.sleep(delay)
                continue
            print(
                f"  - Error fetching balances for {condition_id} "
                f"(outcome {outcome_index}): {exc}"
            )
            return None


def _fetch_outcome_balances(
    market_id: str,
    condition_id: str,
    outcome_index: int,
    *,
    page_size: int,
    sleep_seconds: float,
    max_pages: int | None,
    min_balance: int,
    max_retries: int,
    backoff_seconds: float,
    counts_only: bool,
):
    session = requests.Session()
    skip = 0
    page = 0
    total = 0
    rows = []

    while True:
        payload = {
            "query": USER_BALANCES_QUERY,
            "variables": {
                "conditionId": condition_id,
                "outcomeIndex": str(outcome_index),
                "first": page_size,
                "skip": skip,
                "minBalance": str(min_balance),
            },
        }
        data = _post_with_retries(
            session,
            payload,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            condition_id=condition_id,
            outcome_index=outcome_index,
        )
        if not data:
            break

        balances = data.get("data", {}).get("userBalances", [])
        if not balances:
            break

        total += len(balances)
        if not counts_only:
            for item in balances:
                user = (item.get("user") or "").lower()
                if not user:
                    continue
                try:
                    balance_raw = int(item.get("balance") or 0)
                except (TypeError, ValueError):
                    balance_raw = 0
                if balance_raw <= 0:
                    continue
                rows.append((market_id, user, outcome_index, balance_raw))

        page += 1
        if len(balances) < page_size:
            break
        if max_pages and page >= max_pages:
            break

        skip += page_size
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return rows, total


def _load_markets(
    markets_file: str,
    limit_markets: int | None,
    condition_ids: list[str] | None,
):
    path = Path(markets_file)
    if not path.exists():
        print(f"Error: {markets_file} not found. Run events.py first.")
        return []

    df = pd.read_csv(path, low_memory=False)
    if condition_ids:
        df = df[df["conditionId"].isin(condition_ids)].copy()
    if limit_markets:
        df = df.head(limit_markets).copy()

    if df.empty:
        print("No markets matched the filters.")
        return []

    # JSON parsing is row-specific; the apply keeps the logic simple and reliable.
    df["outcomes_list"] = df["outcomes"].apply(_safe_json_loads)
    df = df[df["conditionId"].notna() & df["outcomes_list"].notna()].copy()
    df["outcome_count"] = df["outcomes_list"].apply(len)

    if df.empty:
        print("No markets with valid outcomes/conditionId found.")
        return []

    if condition_ids:
        found_ids = set(df["conditionId"].dropna().unique())
        missing = sorted(set(condition_ids) - found_ids)
        if missing:
            print(
                f"Warning: {len(missing)} condition IDs not found in {markets_file}."
            )

    return list(df[["id", "conditionId", "outcome_count"]].itertuples(index=False, name=None))


def fetch_active_holders_goldsky(
    *,
    limit_markets: int | None = None,
    condition_ids: list[str] | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
    max_workers: int = DEFAULT_MAX_WORKERS,
    max_pages: int | None = None,
    min_balance: int = DEFAULT_MIN_BALANCE,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
    counts_only: bool = False,
    counts_csv: str = DEFAULT_COUNTS_CSV,
    append: bool = False,
):
    print("--- Starting Goldsky Holders Fetch (positions subgraph) ---")
    markets = _load_markets(MARKETS_FILE, limit_markets, condition_ids)
    if not markets:
        return

    tasks = []
    for market_id, condition_id, outcome_count in markets:
        for outcome_index in range(int(outcome_count)):
            tasks.append((str(market_id), str(condition_id), int(outcome_index)))

    total_tasks = len(tasks)
    print(f"Queued {total_tasks} outcomes across {len(markets)} markets.")

    conn = None
    if not counts_only:
        init_db()
        conn = get_connection()
        if not append:
            print("Clearing old goldsky holders snapshot...")
            conn.execute("DELETE FROM active_market_holders_goldsky")

    start_time = time.time()
    processed = 0
    total_holders = 0
    data_buffer = []
    counts_rows = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(
                _fetch_outcome_balances,
                market_id,
                condition_id,
                outcome_index,
                page_size=page_size,
                sleep_seconds=sleep_seconds,
                max_pages=max_pages,
                min_balance=min_balance,
                max_retries=max_retries,
                backoff_seconds=backoff_seconds,
                counts_only=counts_only,
            ): (market_id, condition_id, outcome_index)
            for market_id, condition_id, outcome_index in tasks
        }

        for future in as_completed(future_to_task):
            market_id, condition_id, outcome_index = future_to_task[future]
            processed += 1
            try:
                rows, holders_count = future.result()
            except Exception as exc:
                print(
                    f"  - Error processing {condition_id} outcome {outcome_index}: {exc}"
                )
                continue

            total_holders += holders_count
            if counts_only:
                counts_rows.append(
                    {
                        "market_id": market_id,
                        "condition_id": condition_id,
                        "outcome_index": outcome_index,
                        "holders_count": holders_count,
                    }
                )
            else:
                data_buffer.extend(rows)
                if len(data_buffer) >= DEFAULT_BATCH_SIZE_INSERT:
                    conn.executemany(
                        """
                        INSERT OR REPLACE INTO active_market_holders_goldsky (
                            market_id, user_addr, outcome_index, balance_raw, updated_at
                        ) VALUES (?, ?, ?, ?, now())
                        """,
                        data_buffer,
                    )
                    data_buffer = []

            if processed % LOG_EVERY_OUTCOMES == 0 or processed == total_tasks:
                elapsed = time.time() - start_time
                rate = total_holders / elapsed if elapsed > 0 else 0
                print(
                    f"Processed {processed}/{total_tasks} outcomes | "
                    f"holders={total_holders:,} | {rate:,.1f} holders/s"
                )

    if not counts_only and data_buffer:
        conn.executemany(
            """
            INSERT OR REPLACE INTO active_market_holders_goldsky (
                market_id, user_addr, outcome_index, balance_raw, updated_at
            ) VALUES (?, ?, ?, ?, now())
            """,
            data_buffer,
        )

    elapsed = time.time() - start_time
    if counts_only:
        output_path = Path(counts_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_counts = pd.DataFrame(counts_rows)
        df_counts.to_csv(output_path, index=False)
        print(
            f"Saved {len(df_counts):,} outcome rows to CSV: {output_path}"
        )
    else:
        row_count = conn.execute(
            "SELECT COUNT(*) FROM active_market_holders_goldsky"
        ).fetchone()[0]
        print(
            "Done! Stored "
            f"{row_count:,} holder balances in DuckDB "
            "(table active_market_holders_goldsky)."
        )
        conn.close()

    print(
        f"Goldsky fetch complete in {elapsed:.2f} seconds "
        f"(holders={total_holders:,})."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch full holders from the positions subgraph (Goldsky)."
    )
    parser.add_argument("--limit", type=int, help="Limit number of markets")
    parser.add_argument(
        "--condition-id",
        action="append",
        dest="condition_ids",
        help="Condition ID to fetch (repeatable)",
    )
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS)
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--min-balance", type=int, default=DEFAULT_MIN_BALANCE)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--backoff", type=float, default=DEFAULT_BACKOFF_SECONDS)
    parser.add_argument(
        "--counts-only",
        action="store_true",
        help="Only compute holders count per outcome and write a CSV.",
    )
    parser.add_argument("--counts-csv", default=DEFAULT_COUNTS_CSV)
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing goldsky holders table instead of clearing.",
    )

    args = parser.parse_args()
    max_pages = args.max_pages if args.max_pages and args.max_pages > 0 else None

    fetch_active_holders_goldsky(
        limit_markets=args.limit,
        condition_ids=args.condition_ids,
        page_size=args.page_size,
        sleep_seconds=args.sleep,
        max_workers=args.max_workers,
        max_pages=max_pages,
        min_balance=args.min_balance,
        max_retries=args.max_retries,
        backoff_seconds=args.backoff,
        counts_only=args.counts_only,
        counts_csv=args.counts_csv,
        append=args.append,
    )
