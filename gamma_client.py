import requests
import time
from typing import List, Dict, Any, Optional

class GammaClient:
    """
    Standalone client for Polymarket Gamma API.
    Removed dependency on 'agents' package.
    """
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com"
        
    def get_markets(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/markets"
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"[GammaClient] Error fetching markets (attempt {attempt+1}/{retries}): {e}")
                time.sleep(2 ** attempt)
        return []

    def get_events(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/events"
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"[GammaClient] Error fetching events (attempt {attempt+1}/{retries}): {e}")
                time.sleep(2 ** attempt)
        return []

class MarketFetcher:
    """
    Logic to fetch all pages of markets/events.
    """
    def __init__(self):
        self.client = GammaClient()

    def fetch_all_markets(self, limit=100) -> List[Dict[str, Any]]:
        results = []
        offset = 0
        while True:
            params = {
                "active": True,
                "closed": False,
                "archived": False,
                "limit": limit,
                "offset": offset,
                "enableOrderBook": False # We don't need OB for dashboard, basic info is enough
            }
            batch = self.client.get_markets(params)
            if not batch:
                break
            results.extend(batch)
            offset += limit
            # print(f"Fetched markets offset {offset}...")
            if len(batch) < limit:
                break
        return results

    def fetch_all_events(self, limit=100) -> List[Dict[str, Any]]:
        results = []
        offset = 0
        while True:
            params = {
                "active": True,
                "closed": False,
                "archived": False,
                "limit": limit,
                "offset": offset
            }
            batch = self.client.get_events(params)
            if not batch:
                break
            results.extend(batch)
            offset += limit
            # print(f"Fetched events offset {offset}...")
            if len(batch) < limit:
                break
        return results
