import requests
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("polylab.holders")

class HoldersClient:
    def __init__(self):
        self.base_url = "https://data-api.polymarket.com"

    def fetch_holders(self, market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetches top holders for a market.
        Flattens the per-token holders list.
        """
        url = f"{self.base_url}/holders"
        params = {"market": market_id, "limit": limit}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, list):
                logger.warning(f"Unexpected response format for market {market_id}: {type(data)}")
                return []

            flattened_holders = []
            for token_entry in data:
                token_holders = token_entry.get("holders", [])
                for h in token_holders:
                    # Normalize keys to what the scraper expects
                    h["address"] = h.get("proxyWallet")
                    h["positionSize"] = h.get("amount")
                    # outcomeIndex is already there
                    flattened_holders.append(h)

            # Re-sort because we merged multiple tokens
            flattened_holders.sort(key=lambda x: float(x.get("positionSize", 0)), reverse=True)
            
            return flattened_holders
            
        except Exception as e:
            logger.error(f"Error fetching holders for {market_id}: {e}")
            return []

class PnLClient:
    def __init__(self):
        self.base_url = "https://user-pnl-api.polymarket.com"

    def fetch_user_pnl(self, wallet_address: str) -> Optional[float]:
        """
        Fetches user PnL history and returns the latest value.
        """
        url = f"{self.base_url}/user-pnl"
        params = {"user_address": wallet_address}
        
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 429:
                    logger.warning(f"Rate limited (429) for {wallet_address}, retrying...")
                    time.sleep(1 * (attempt + 1))
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                # Expecting list of time-series points. 
                if isinstance(data, list) and len(data) > 0:
                    last_point = data[-1]
                    # API returns 'p' for profit/value? Or is it 'pnl'? 
                    # User spec says "vezmi poslední bod p".
                    return float(last_point.get("p", 0.0))
                
                # Empty history or different format
                return 0.0 
                
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch PnL for {wallet_address} after retries: {e}")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Unexpected error for {wallet_address}: {e}")
                break
        
        return None
