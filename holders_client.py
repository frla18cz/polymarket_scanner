import requests
import time
import logging
import os # Import os for environment variables
from typing import List, Dict, Any, Optional

logger = logging.getLogger("polylab.holders")

# Default Goldsky Subgraph URL
DEFAULT_GOLDSKY_SUBGRAPH_URL = os.getenv(
    "GOLDSKY_SUBGRAPH_URL",
    "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn"
)

class HoldersClient:
    def __init__(self):
        self.base_url = "https://data-api.polymarket.com"

    def fetch_holders(self, market_id: str, limit: int = 1000) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches top holders for a market with retries.
        Returns None if an error occurs after all retries.
        """
        url = f"{self.base_url}/holders"
        params = {"market": market_id, "limit": limit}
        
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=15)
                
                # Handle 429 specifically
                if response.status_code == 429:
                    logger.warning(f"Rate limited (429) for market {market_id}, waiting 5s (attempt {attempt+1}/{retries})")
                    time.sleep(5)
                    continue

                response.raise_for_status()
                data = response.json()

                if not isinstance(data, list):
                    logger.warning(f"Unexpected response format for market {market_id}: {type(data)}")
                    # If format is wrong, we probably can't recover by retrying
                    return None

                flattened_holders = []
                
                for token_entry in data:
                    token_holders = token_entry.get("holders", [])
                    for h in token_holders:
                        # Normalize keys to what the scraper expects
                        h["address"] = h.get("proxyWallet")
                        h["positionSize"] = h.get("amount")
                        flattened_holders.append(h)

                # Re-sort because we merged multiple tokens
                flattened_holders.sort(key=lambda x: float(x.get("positionSize", 0)), reverse=True)
                return flattened_holders

            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                if attempt < retries - 1:
                    logger.warning(f"Connection error for {market_id} (attempt {attempt+1}/{retries}), retrying in 2s: {e}")
                    time.sleep(2)
                else:
                    logger.error(f"Failed to fetch holders for {market_id} after {retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {market_id}: {e}")
                break
        
        return None

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
                            "first": limit,
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


class PnLClient:
    def __init__(self):
        self.base_url = "https://user-pnl-api.polymarket.com"

    def fetch_user_pnl(self, wallet_address: str) -> Optional[float]:
        """
        Fetches user PnL history and returns the latest value.
        Implements exponential backoff for retries.
        """
        url = f"{self.base_url}/user-pnl"
        params = {"user_address": wallet_address}
        
        retries = 5
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 429:
                    wait_time = (2 ** attempt) + 1
                    logger.warning(f"Rate limited (429) for {wallet_address}, waiting {wait_time}s (attempt {attempt+1}/{retries})")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    last_point = data[-1]
                    return float(last_point.get("p", 0.0))
                
                return 0.0 
                
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                wait_time = (2 ** attempt) + 0.5
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch PnL for {wallet_address} after {retries} retries: {e}")
                else:
                    logger.warning(f"Connection error for {wallet_address}, retrying in {wait_time}s... ({e})")
                    time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Unexpected error for {wallet_address}: {e}")
                break
        
        return None
