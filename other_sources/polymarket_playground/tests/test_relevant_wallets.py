"""Quick smoke test for Step 1B wallet extraction."""

import json
from pathlib import Path
from statistics import median
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import events
from get_relevant_wallets import RELEVANT_WALLETS_FILE, fetch_wallets_for_active_markets

ACTIVE_MARKETS_PATH = Path("data/markets_current.csv")
TEST_OUTPUT_PATH = Path("tests/output/relevant_wallets_test.json")


def ensure_market_snapshot() -> None:
    if ACTIVE_MARKETS_PATH.exists():
        return
    print("markets_current.csv missing – running Step 1A snapshot...")
    events.refresh_active_markets_snapshot()


def summarize_wallets(wallets: set[str]) -> None:
    if not wallets:
        print("No wallets collected; aborting summary.")
        return

    wallet_lengths = [len(w) for w in wallets]
    print(f"Collected {len(wallets)} wallets. Length median: {median(wallet_lengths)}")
    print(f"Sample: {sorted(wallets)[:10]}")

    existing_path = Path(RELEVANT_WALLETS_FILE)
    if existing_path.exists():
        with existing_path.open("r") as handle:
            existing_wallets = json.load(handle)
        print(f"Existing Step 1B wallet count: {len(existing_wallets)}")
        print(f"Existing Step 1B file size: {existing_path.stat().st_size} bytes")


if __name__ == "__main__":
    ensure_market_snapshot()

    TEST_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    wallets = fetch_wallets_for_active_markets(
        max_markets=1,
        per_market_limit=50,
        output_path=str(TEST_OUTPUT_PATH),
    )

    print(f"Saved sample wallets to {TEST_OUTPUT_PATH}.")
    summarize_wallets(wallets)
