import json
import unittest
from unittest.mock import patch

import gamma_client


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return json.loads(json.dumps(self._payload))


class TestMarketFetcherPagination(unittest.TestCase):
    def test_fetch_all_markets_paginates_until_short_page(self):
        fetcher = gamma_client.MarketFetcher()

        pages = {
            0: [{"id": "m1"}] * 2,
            2: [{"id": "m3"}] * 1,
        }

        def _fake_get(url, params=None, timeout=None):
            offset = int((params or {}).get("offset", 0))
            limit = int((params or {}).get("limit", 100))
            payload = pages.get(offset, [])
            self.assertEqual(limit, 2)
            self.assertIn("/markets", url)
            return _FakeResponse(payload)

        with patch("requests.get", side_effect=_fake_get):
            markets = fetcher.fetch_all_markets(limit=2)

        self.assertEqual(len(markets), 3)

    def test_fetch_all_events_stops_on_empty_batch(self):
        fetcher = gamma_client.MarketFetcher()

        def _fake_get(url, params=None, timeout=None):
            self.assertIn("/events", url)
            return _FakeResponse([])

        with patch("requests.get", side_effect=_fake_get):
            events = fetcher.fetch_all_events(limit=50)

        self.assertEqual(events, [])

    def test_gamma_client_retries_then_succeeds(self):
        client = gamma_client.GammaClient()

        call_count = {"n": 0}

        def _fake_get(url, params=None, timeout=None):
            call_count["n"] += 1
            if call_count["n"] < 3:
                raise RuntimeError("boom")
            return _FakeResponse([{"id": "ok"}])

        with patch("requests.get", side_effect=_fake_get), patch("time.sleep", return_value=None):
            markets = client.get_markets({"limit": 1, "offset": 0})

        self.assertEqual(markets, [{"id": "ok"}])
        self.assertEqual(call_count["n"], 3)

