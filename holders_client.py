import requests
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("polylab.holders")

class HoldersClient:
    def __init__(self):
        self.base_url = "https://data-api.polymarket.com"

    def fetch_holders(self, market_id: str, limit: int = 1000) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches top holders for a market with retries and validation.
        Returns None if validation fails after all retries.
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
                outcome_counts = {}
                
                for token_entry in data:
                    token_holders = token_entry.get("holders", [])
                    for h in token_holders:
                        # outcomeIndex might be 0, 1, etc.
                        oi = h.get("outcomeIndex")
                        if oi is not None:
                            outcome_counts[oi] = outcome_counts.get(oi, 0) + 1
                            
                        # Normalize keys to what the scraper expects
                        h["address"] = h.get("proxyWallet")
                        h["positionSize"] = h.get("amount")
                        flattened_holders.append(h)

                # Validation logic: At least 20 holders for outcome 0 AND at least 20 for outcome 1
                # (Assuming binary markets are the priority, multi-outcome might need adjustment but
                # spec says "apply to outcome 0 and 1").
                c0 = outcome_counts.get(0, 0)
                c1 = outcome_counts.get(1, 0)
                
                if c0 < 20 or c1 < 20:
                    msg = f"Validation failed for {market_id}: Only {c1} YES / {c0} NO holders found (attempt {attempt+1}/{retries})"
                    if attempt < retries - 1:
                        logger.warning(f"{msg}, retrying in 2s...")
                        time.sleep(2)
                        continue
                    else:
                        logger.error(f"Insufficient data for {market_id} after {retries} attempts ({c1} YES, {c0} NO). Skipping.")
                        return None

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
