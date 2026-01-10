import requests
import json
import pandas as pd

# --- Constants ---
SUBGRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn"
USER_TO_TEST = "0x908355107b56e0a66b4fd0e06b059899aec8d27b".lower()
MARKETS_FILE = "data/markets_current.csv"  # To get market titles

# --- GraphQL Query ---
# This query works and does NOT ask for conditionId
POSITIONS_QUERY = """
query GetSingleUserPositions($user: String!) {
  userPositions(where: {user: $user, realizedPnl_not: "0"}) {
    id
    user
    realizedPnl
  }
}
"""


def test_single_user_pnl_from_subgraph():
    print(f"--- Testing P/L for single user from Subgraph (Functional Version) ---")
    print(f"Target User: {USER_TO_TEST}")

    try:
        payload = {"query": POSITIONS_QUERY, "variables": {"user": USER_TO_TEST}}
        response = requests.post(SUBGRAPH_URL, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        positions = data.get("data", {}).get("userPositions", [])

        # Save raw response for debugging
        with open("data/raw_subgraph_positions.json", "w") as f:
            json.dump(data, f, indent=2)

        if not positions:
            print("\nResult: No closed positions found.")
            return

        print(f"\n--- Detailed P/L Breakdown for {len(positions)} Positions ---")
        print(f"{'Raw PNL':>20} | {'Calculated P/L (USD)':>25}")
        print("-" * 48)

        total_pl_numeric = 0
        for item in positions:
            raw_pnl = float(item.get("realizedPnl", 0))
            pnl_usd = raw_pnl / 1_000_000
            total_pl_numeric += raw_pnl

            print(f"{raw_pnl:>20,.0f} | ${pnl_usd:>24,.2f}")

        print("-" * 48)
        final_total_usd = total_pl_numeric / 1_000_000
        print(f"{'TOTAL:':>20} | ${final_total_usd:>24,.2f}")

    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    test_single_user_pnl_from_subgraph()
