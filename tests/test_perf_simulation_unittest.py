import os
import tempfile
import time
import unittest
import sqlite3
from datetime import datetime, timezone

from fastapi import Response

from tests._db_snapshot import snapshot_main_db


class TestUserSimulationPerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("RUN_PERF_TESTS") != "1":
            raise unittest.SkipTest("Nastav RUN_PERF_TESTS=1 pro performance scénáře.")

        cls._snapshot = snapshot_main_db()
        os.environ["MARKETS_DB_PATH"] = str(cls._snapshot.path)

        import main as app_main

        cls.app_main = app_main
        cls.app_main.ensure_indices()

        cls._conn = sqlite3.connect(str(cls._snapshot.path))
        cls._conn.row_factory = sqlite3.Row

        tags = [r["tag_label"] for r in cls._conn.execute(
            "SELECT tag_label FROM market_tags GROUP BY tag_label ORDER BY COUNT(*) DESC LIMIT 10"
        ).fetchall()]
        if len(tags) < 3:
            raise RuntimeError("Nedostatek tagů v DB pro performance scénáře.")
        cls.tag_a, cls.tag_b, cls.tag_c = tags[0], tags[1], tags[2]

        def _percentile_value(col: str, quantile: float) -> float | None:
            total = cls._conn.execute(
                f"SELECT COUNT(*) AS n FROM active_market_outcomes WHERE {col} IS NOT NULL"
            ).fetchone()["n"]
            if not total:
                return None
            offset = int(total * quantile)
            row = cls._conn.execute(
                f"SELECT {col} AS v FROM active_market_outcomes WHERE {col} IS NOT NULL ORDER BY {col} ASC LIMIT 1 OFFSET ?",
                (offset,),
            ).fetchone()
            return float(row["v"]) if row and row["v"] is not None else None

        cls.median_price = _percentile_value("price", 0.5) or 0.5
        cls.max_spread_threshold = _percentile_value("spread", 0.25) or 0.05
        cls.min_volume_threshold = _percentile_value("volume_usd", 0.75) or 1000.0
        cls.min_liquidity_threshold = _percentile_value("liquidity_usd", 0.75) or 100.0

        soonest = cls._conn.execute(
            """
            SELECT end_date FROM active_market_outcomes
            WHERE end_date IS NOT NULL AND datetime(end_date) > datetime('now')
            ORDER BY datetime(end_date) ASC
            LIMIT 1
            """
        ).fetchone()
        cls.has_future_end_dates = bool(soonest and soonest["end_date"])
        cls.expiry_hours = None
        if cls.has_future_end_dates:
            s = (soonest["end_date"] or "").strip()
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            try:
                parsed = datetime.fromisoformat(s)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                hours = int(((parsed - now).total_seconds() / 3600.0) + 1.0)
                cls.expiry_hours = max(1, min(hours, 24 * 14))
            except Exception:
                cls.expiry_hours = None

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("MARKETS_DB_PATH", None)
        cls._conn.close()
        cls._snapshot.cleanup()

    def _time_request_ms(self, path: str, params: dict) -> float:
        t0 = time.perf_counter()
        if path != "/api/markets":
            raise ValueError("Zatím měříme jen /api/markets")
        rows = self.app_main.get_markets(Response(), **params)
        t1 = time.perf_counter()
        self.assertIsInstance(rows, list)
        return (t1 - t0) * 1000.0

    def _budget(self, env_key: str) -> float:
        try:
            return float(os.environ.get(env_key, "0") or "0")
        except Exception:
            return 0.0

    def _assert_budget(self, ms: float, env_key: str) -> None:
        budget_ms = self._budget(env_key)
        if budget_ms > 0:
            self.assertLess(ms, budget_ms, msg=f"{env_key}: {ms:.1f}ms > {budget_ms}ms")

    def test_perf_excluded_single_tag(self):
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": None,
                "excluded_tags": [self.tag_a],
                "sort_by": "volume_usd",
                "sort_dir": "desc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_EXCLUDED_SINGLE_MS")

    def test_perf_excluded_multiple_tags(self):
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": None,
                "excluded_tags": [self.tag_a, self.tag_b],
                "sort_by": "volume_usd",
                "sort_dir": "desc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_EXCLUDED_MULTI_MS")

    def test_perf_included_multiple_tags(self):
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": [self.tag_a, self.tag_b],
                "excluded_tags": None,
                "sort_by": "volume_usd",
                "sort_dir": "desc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_INCLUDED_MULTI_MS")

    def test_perf_included_comma_separated(self):
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": [f"{self.tag_a},{self.tag_b}"],
                "excluded_tags": None,
                "sort_by": "volume_usd",
                "sort_dir": "desc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_INCLUDED_CSV_MS")

    def test_perf_included_excluded_combo(self):
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": [self.tag_a, self.tag_b],
                "excluded_tags": [self.tag_a],
                "min_volume": 1000,
                "max_spread": 0.05,
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_INCLUDED_EXCLUDED_MS")

    def test_perf_price_probability_range(self):
        center = float(self.median_price)
        lo = max(0.0, center - 0.05)
        hi = min(1.0, center + 0.05)
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": None,
                "excluded_tags": None,
                "min_price": lo,
                "max_price": hi,
                "sort_by": "volume_usd",
                "sort_dir": "desc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_PRICE_RANGE_MS")

    def test_perf_spread_max(self):
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": None,
                "excluded_tags": None,
                "max_spread": float(self.max_spread_threshold),
                "sort_by": "volume_usd",
                "sort_dir": "desc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_SPREAD_MAX_MS")

    def test_perf_volume_liquidity_min(self):
        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": None,
                "excluded_tags": None,
                "min_volume": float(self.min_volume_threshold),
                "min_liquidity": float(self.min_liquidity_threshold),
                "sort_by": "volume_usd",
                "sort_dir": "desc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_VOL_LIQ_MS")

    def test_perf_expiring_soon(self):
        if not self.expiry_hours:
            self.skipTest("V DB nejsou budoucí end_date záznamy.")

        ms = self._time_request_ms(
            "/api/markets",
            {
                "included_tags": None,
                "excluded_tags": None,
                "max_hours_to_expire": int(self.expiry_hours),
                "include_expired": False,
                "sort_by": "end_date",
                "sort_dir": "asc",
                "limit": 100,
            },
        )
        self._assert_budget(ms, "PERF_BUDGET_EXPIRING_SOON_MS")
