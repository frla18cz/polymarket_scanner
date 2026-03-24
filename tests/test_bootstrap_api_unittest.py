import os
import sqlite3
import unittest

from fastapi import Response

from tests._db_snapshot import snapshot_main_db


class TestBootstrapApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._snapshot = snapshot_main_db()
        os.environ["MARKETS_DB_PATH"] = str(cls._snapshot.path)

        import main as app_main

        app_main.DB_PATH = str(cls._snapshot.path)
        cls.app_main = app_main
        cls.app_main.ensure_indices()
        cls.app_main.refresh_materialized_smart_money_stats()
        cls.app_main.refresh_bootstrap_snapshots()

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("MARKETS_DB_PATH", None)
        cls._snapshot.cleanup()

    def test_homepage_bootstrap_returns_ready_payload(self):
        response = Response()
        payload = self.app_main.get_homepage_bootstrap(response)

        self.assertEqual(
            response.headers.get("cache-control"),
            "public, s-maxage=300, stale-while-revalidate=3600",
        )
        self.assertIn("spotlight_markets", payload)
        self.assertIn("playbook_previews", payload)
        self.assertIsInstance(payload["spotlight_markets"], list)
        self.assertIsInstance(payload["playbook_previews"], dict)
        self.assertIn("smart_money_edge", payload["playbook_previews"])

    def test_app_bootstrap_default_scanner_contains_filters_tags_and_markets(self):
        response = Response()
        payload = self.app_main.get_app_bootstrap(response, view="scanner")

        self.assertEqual(payload["view"], "scanner")
        self.assertIsNone(payload["active_preset_id"])
        self.assertIn("filters", payload)
        self.assertIn("markets", payload)
        self.assertIn("tags", payload)
        self.assertIsInstance(payload["markets"], list)
        self.assertIsInstance(payload["tags"], list)
        self.assertEqual(payload["filters"]["min_volume"], 5000)
        self.assertEqual(
            response.headers.get("cache-control"),
            "public, s-maxage=300, stale-while-revalidate=3600",
        )

    def test_app_bootstrap_smart_money_preset_resolves_view_and_filters(self):
        payload = self.app_main.get_app_bootstrap(Response(), view="scanner", preset="smart_money_edge")

        self.assertEqual(payload["view"], "smart")
        self.assertEqual(payload["active_preset_id"], "smart_money_edge")
        self.assertEqual(payload["filters"]["min_profitable"], 15)
        self.assertEqual(payload["filters"]["min_losing_opposite"], 15)
        self.assertEqual(payload["filters"]["max_spread"], 0.05)
        self.assertEqual(payload["filters"]["min_liquidity"], 1000)

    def test_app_bootstrap_default_smart_contains_ten_and_ten_thresholds(self):
        payload = self.app_main.get_app_bootstrap(Response(), view="smart")

        self.assertEqual(payload["view"], "smart")
        self.assertEqual(payload["filters"]["min_profitable"], 10)
        self.assertEqual(payload["filters"]["min_losing_opposite"], 10)

    def test_refresh_snapshots_persists_expected_keys(self):
        conn = sqlite3.connect(str(self._snapshot.path))
        try:
            keys = {
                row[0]
                for row in conn.execute("SELECT snapshot_key FROM precomputed_snapshots").fetchall()
            }
        finally:
            conn.close()

        self.assertIn("homepage", keys)
        self.assertIn("app_default_scanner", keys)
        self.assertIn("app_default_smart", keys)
        self.assertIn("app_preset_smart_money_edge", keys)
        self.assertIn("app_preset_safe_haven", keys)


if __name__ == "__main__":
    unittest.main()
