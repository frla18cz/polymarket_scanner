import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import requests

BASE_URL = "https://gamma-api.polymarket.com/markets"
ACTIVE_MARKETS_JSON_PATH = Path("data/markets_current.json")
ACTIVE_MARKETS_CSV_PATH = Path("data/markets_current.csv")
DEFAULT_LIMIT_PER_PAGE = 100
DEFAULT_SLEEP_SECONDS = 0.2


def _fetch_active_markets(
    limit_per_page: int = DEFAULT_LIMIT_PER_PAGE,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
) -> list[dict[str, Any]]:
    """
    Retrieve a list of all currently active markets from the Polymarket Gamma API.
    Pagination uses the documented offset/limit parameters.
    """
    print(
        f"Fetching active markets from {BASE_URL} "
        f"(limit={limit_per_page}, sleep={sleep_seconds}s)..."
    )
    all_markets: list[dict[str, Any]] = []
    offset = 0

    while True:
        params = {"offset": offset, "limit": limit_per_page, "closed": "false"}
        print(f"Requesting offset={offset}...")
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        markets_on_page = response.json()

        if not markets_on_page:
            print("No markets returned for this page – pagination finished.")
            break

        all_markets.extend(markets_on_page)
        print(
            f"Fetched {len(markets_on_page)} markets "
            f"(running total={len(all_markets)})."
        )

        if len(markets_on_page) < limit_per_page:
            print("Last page reached (received less than requested limit).")
            break

        offset += limit_per_page
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return all_markets


def _prepare_dataframe(
    markets: list[dict[str, Any]], fetched_at: datetime
) -> pd.DataFrame:
    """
    Deduplicate markets dataframe and stamp snapshot metadata.
    """
    df = pd.DataFrame(markets)
    if df.empty:
        return df

    df = df.drop_duplicates(subset=["id"], keep="first")
    df["snapshot_fetched_at"] = fetched_at.isoformat()
    return df


def refresh_active_markets_snapshot(
    *,
    limit_per_page: int = DEFAULT_LIMIT_PER_PAGE,
    sleep_seconds: float = DEFAULT_SLEEP_SECONDS,
    json_path: Path | str = ACTIVE_MARKETS_JSON_PATH,
    csv_path: Path | str = ACTIVE_MARKETS_CSV_PATH,
) -> dict[str, Any]:
    """
    Pull the latest active market snapshot and persist it to JSON/CSV.
    Returns metadata useful for UI confirmations.
    """
    fetched_at = datetime.now(timezone.utc)
    try:
        markets = _fetch_active_markets(
            limit_per_page=limit_per_page, sleep_seconds=sleep_seconds
        )
    except requests.exceptions.RequestException as exc:
        print(f"API request failed: {exc}")
        raise

    df = _prepare_dataframe(markets, fetched_at)
    if df.empty:
        print("No active markets fetched – snapshot files not updated.")
        return {
            "markets_count": 0,
            "fetched_at": fetched_at.isoformat(),
            "csv_path": str(csv_path),
            "json_path": str(json_path),
            "updated": False,
        }

    json_path = Path(json_path)
    csv_path = Path(csv_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    final_markets = df.to_dict("records")
    with open(json_path, "w") as json_file:
        json.dump(final_markets, json_file, indent=4)
    print(
        f"Wrote {len(final_markets)} markets to JSON: {json_path} "
        f"(snapshot={fetched_at.isoformat()})."
    )

    df.to_csv(csv_path, index=False)
    print(
        f"Wrote {len(final_markets)} markets to CSV: {csv_path} "
        f"(snapshot={fetched_at.isoformat()})."
    )

    return {
        "markets_count": len(final_markets),
        "fetched_at": fetched_at.isoformat(),
        "csv_path": str(csv_path),
        "json_path": str(json_path),
        "updated": True,
    }


def get_market_snapshot_metadata(
    csv_path: Path | str = ACTIVE_MARKETS_CSV_PATH,
) -> Optional[dict[str, Any]]:
    """
    Inspect the latest market snapshot CSV and return metadata for UI display.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return None

    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Unable to read {csv_path}: {exc}")
        return None

    if df.empty:
        return {
            "markets_count": 0,
            "fetched_at": None,
            "csv_path": str(csv_path),
        }

    fetched_at_value = None
    if (
        "snapshot_fetched_at" in df.columns
        and not df["snapshot_fetched_at"].isna().all()
    ):
        fetched_at_value = df["snapshot_fetched_at"].iloc[0]

    return {
        "markets_count": len(df),
        "fetched_at": fetched_at_value,
        "csv_path": str(csv_path),
    }


if __name__ == "__main__":
    refresh_active_markets_snapshot()
