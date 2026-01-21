import requests
import time
import logging
import os # Import os for environment variables
from typing import List, Dict, Any, Optional

logger = logging.getLogger("polylab.holders.goldsky_backup")

class GoldskyClient:
    USER_BALANCES_QUERY = """
    query GetUserBalances(
      $conditionId: String!
      $outcomeIndex: BigInt!
      $first: Int!
      $skip: Int!
    ) {
      userBalances(
        first: $first
        skip: $skip
        orderBy: balance
        orderDirection: desc
        where: {
          asset_: { condition: $conditionId, outcomeIndex: $outcomeIndex }
          balance_gt: 0
        }
      ) {
        user
        balance
      }
    }
    """

    def __init__(self):
        self.url = os.getenv(
            "GOLDSKY_SUBGRAPH_URL",
            "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn"
        )

    def fetch_holders_subgraph(self, condition_id: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches top holders for a market from the Goldsky subgraph with retries.
        Returns None if an error occurs after all retries.
        """
        capped_limit = min(limit, 20)
        retries = 3
        for attempt in range(retries):
            all_holders = []
            try:
                # Fetch for both Yes (1) and No (0) outcomes
                for outcome_index in [0, 1]:
                    payload = {
                        "query": self.USER_BALANCES_QUERY,
                        "variables": {
                            "conditionId": condition_id,
                            "outcomeIndex": str(outcome_index),
                            "first": capped_limit,
                            "skip": 0,
                        },
                    }
                    response = requests.post(self.url, json=payload, timeout=15)
                    
                    if response.status_code == 429:
                        wait_time = (2 ** attempt) + 1
                        logger.warning(f"Goldsky rate limited (429) for {condition_id}, waiting {wait_time}s (attempt {attempt+1}/{retries})")
                        time.sleep(wait_time)
                        raise requests.exceptions.RequestException("Rate limited")

                    response.raise_for_status()
                    data = response.json()

                    if "errors" in data:
                        logger.error(f"GraphQL error for {condition_id} (outcome {outcome_index}): {data['errors']}")
                        # If it's a GraphQL error, retrying might not help unless it's a transient server error
                        continue

                    balances = data.get("data", {}).get("userBalances", [])
                    for item in balances:
                        all_holders.append({
                            "address": item.get("user"),
                            "positionSize": float(item.get("balance", 0)) / 1_000_000,
                            "outcomeIndex": outcome_index,
                        })
                
                # If we successfully got data (even if empty list), we return it
                # Sort by position size descending, as we merged two separate queries
                all_holders.sort(key=lambda x: x["positionSize"], reverse=True)
                return all_holders

            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                if attempt < retries - 1:
                    wait_time = (2 ** attempt) + 0.5
                    logger.warning(f"Goldsky connection error for {condition_id} (attempt {attempt+1}/{retries}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch subgraph holders for {condition_id} after {retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in GoldskyClient for {condition_id}: {e}")
                break
        
        return None
