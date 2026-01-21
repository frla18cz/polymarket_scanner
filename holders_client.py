import requests
import time
import logging
import os # Import os for environment variables
from typing import List, Dict, Any, Optional

logger = logging.getLogger("polylab.holders")

class HoldersClient:
    def __init__(self):
        self.base_url = "https://data-api.polymarket.com"

    def fetch_holders(self, market_id: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches top holders for a market with retries.
        Returns None if an error occurs after all retries.
        """
        url = f"{self.base_url}/holders"
        # We want top N per outcome. For binary markets, that's 2*N total.
        # Legacy API likely applies limit per request, so we request more to be safe.
        per_outcome_limit = min(limit, 20)
        request_limit = per_outcome_limit * 2 
        params = {"market": market_id, "limit": request_limit}
        
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
                    # Sort and take top N for THIS outcome
                    outcome_holders = []
                    for h in token_holders:
                        h["address"] = h.get("proxyWallet")
                        h["positionSize"] = h.get("amount")
                        outcome_holders.append(h)
                    
                    # Sort by size just in case API didn't
                    outcome_holders.sort(key=lambda x: float(x.get("positionSize", 0)), reverse=True)
                    # Take top N for this outcome
                    flattened_holders.extend(outcome_holders[:per_outcome_limit])

                # Re-sort total list descending by size
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
