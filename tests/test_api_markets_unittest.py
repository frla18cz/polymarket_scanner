import os
import sqlite3
import unittest
from datetime import datetime, timezone
from typing import Iterable

from fastapi import Response

from tests._db_snapshot import snapshot_main_db


class TestMarketsFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
            raise RuntimeError("Nedostatek tagů v DB pro kombinace testů.")
        cls.tag_a, cls.tag_b, cls.tag_c = tags[0], tags[1], tags[2]

        cls._tag_sets: dict[str, set[str]] = {}

        def _tag_set(tag: str) -> set[str]:
            if tag not in cls._tag_sets:
                rows = cls._conn.execute(
                    "SELECT DISTINCT market_id FROM market_tags WHERE tag_label = ?",
                    (tag,),
                ).fetchall()
                cls._tag_sets[tag] = {r["market_id"] for r in rows}
            return cls._tag_sets[tag]

        # Vyber dvojici pro "included+excluded konflikt" tak, aby to mělo výsledky.
        conflict_a = cls.tag_a
        conflict_b = cls.tag_b
        for a in tags[:6]:
            for b in tags[:6]:
                if a == b:
                    continue
                if len(_tag_set(b) - _tag_set(a)) > 0:
                    conflict_a, conflict_b = a, b
                    break
            else:
                continue
            break
        cls.conflict_included_a = conflict_a
        cls.conflict_included_b = conflict_b

        q = cls._conn.execute(
            "SELECT question FROM active_market_outcomes WHERE question IS NOT NULL AND LENGTH(question) > 10 LIMIT 1"
        ).fetchone()
        cls.search_term = (q["question"].split(" ")[0] if q and q["question"] else "the").strip(" ?!.,").lower()

        soonest = cls._conn.execute(
            """
            SELECT end_date FROM active_market_outcomes
            WHERE end_date IS NOT NULL AND datetime(end_date) > datetime('now')
            ORDER BY datetime(end_date) ASC
            LIMIT 1
            """
        ).fetchone()
        cls.has_future_end_dates = bool(soonest and soonest["end_date"])

        def _parse_end(dt_str: str | None):
            s = (dt_str or "").strip()
            if not s:
                return None
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None

        cls.expiry_hours = None
        if cls.has_future_end_dates:
            parsed = _parse_end(soonest["end_date"])
            if parsed is not None:
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                hours = int(((parsed - now).total_seconds() / 3600.0) + 1.0)
                cls.expiry_hours = max(1, min(hours, 24 * 14))

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

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("MARKETS_DB_PATH", None)
        cls._conn.close()
        cls._snapshot.cleanup()

    def _market_ids(self, rows):
        return {row["market_id"] for row in rows}

    def _market_ids_with_tag(self, tag: str) -> set[str]:
        if tag in self._tag_sets:
            return self._tag_sets[tag]
        rows = self._conn.execute(
            "SELECT DISTINCT market_id FROM market_tags WHERE tag_label = ?",
            (tag,),
        ).fetchall()
        out = {r["market_id"] for r in rows}
        self._tag_sets[tag] = out
        return out

    def _assert_all_ids_in(self, ids: Iterable[str], allowed: set[str]) -> None:
        for mid in ids:
            self.assertIn(mid, allowed)

    def _assert_all_ids_not_in(self, ids: Iterable[str], forbidden: set[str]) -> None:
        for mid in ids:
            self.assertNotIn(mid, forbidden)

    def test_excluded_single_tag(self):
        excluded = [self.tag_a]
        forbidden = self._market_ids_with_tag(self.tag_a)
        rows = self.app_main.get_markets(Response(), included_tags=None, excluded_tags=excluded, limit=200)
        ids = self._market_ids(rows)
        self.assertGreater(len(ids), 0)
        self._assert_all_ids_not_in(ids, forbidden)

    def test_excluded_multiple_tags(self):
        excluded = [self.tag_a, self.tag_b]
        forbidden = self._market_ids_with_tag(self.tag_a) | self._market_ids_with_tag(self.tag_b)
        rows = self.app_main.get_markets(Response(), included_tags=None, excluded_tags=excluded, limit=200)
        ids = self._market_ids(rows)
        self.assertGreater(len(ids), 0)
        self._assert_all_ids_not_in(ids, forbidden)

    def test_included_single_tag(self):
        included = [self.tag_a]
        allowed = self._market_ids_with_tag(self.tag_a)
        rows = self.app_main.get_markets(Response(), included_tags=included, excluded_tags=None, limit=200)
        ids = self._market_ids(rows)
        self.assertGreater(len(ids), 0)
        self._assert_all_ids_in(ids, allowed)

    def test_included_multiple_tags(self):
        included = [self.tag_a, self.tag_b]
        allowed = self._market_ids_with_tag(self.tag_a) | self._market_ids_with_tag(self.tag_b)
        rows = self.app_main.get_markets(Response(), included_tags=included, excluded_tags=None, limit=200)
        ids = self._market_ids(rows)
        self.assertGreater(len(ids), 0)
        self._assert_all_ids_in(ids, allowed)

    def test_included_comma_separated_is_parsed(self):
        included_str = f"{self.tag_a},{self.tag_b}"
        allowed = self._market_ids_with_tag(self.tag_a) | self._market_ids_with_tag(self.tag_b)
        rows = self.app_main.get_markets(Response(), included_tags=[included_str], excluded_tags=None, limit=200)
        ids = self._market_ids(rows)
        self.assertGreater(len(ids), 0)
        self._assert_all_ids_in(ids, allowed)

    def test_included_excluded_conflict(self):
        included = [self.conflict_included_a, self.conflict_included_b]
        excluded = [self.conflict_included_a]
        expected = self._market_ids_with_tag(self.conflict_included_b) - self._market_ids_with_tag(self.conflict_included_a)
        if not expected:
            self.skipTest("Nenašla se vhodná kombinace tagů pro konflikt.")
        rows = self.app_main.get_markets(Response(), included_tags=included, excluded_tags=excluded, limit=200)
        ids = self._market_ids(rows)
        self.assertGreater(len(ids), 0)
        self._assert_all_ids_in(ids, expected)

    def test_price_probability_range(self):
        center = float(self.median_price)
        lo = max(0.0, center - 0.05)
        hi = min(1.0, center + 0.05)
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            min_price=lo,
            max_price=hi,
            limit=200,
        )
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertGreaterEqual(row["price"], lo)
            self.assertLessEqual(row["price"], hi)

    def test_spread_max(self):
        threshold = float(self.max_spread_threshold)
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            max_spread=threshold,
            limit=200,
        )
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertLessEqual(row["spread"], threshold)

    def test_volume_and_liquidity_min(self):
        min_volume = float(self.min_volume_threshold)
        min_liquidity = float(self.min_liquidity_threshold)
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            min_volume=min_volume,
            min_liquidity=min_liquidity,
            limit=200,
        )
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertGreaterEqual(row["volume_usd"], min_volume)
            self.assertGreaterEqual(row["liquidity_usd"], min_liquidity)

    def test_expiring_soon_filter(self):
        if not self.expiry_hours:
            self.skipTest("V DB nejsou budoucí end_date záznamy.")

        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            max_hours_to_expire=int(self.expiry_hours),
            include_expired=False,
            limit=200,
        )
        self.assertGreater(len(rows), 0)

        from datetime import timedelta

        now = datetime.now(timezone.utc)
        max_dt = now + timedelta(hours=int(self.expiry_hours))

        def _parse(dt_str: str):
            s = (dt_str or "").strip()
            if not s:
                return None
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return None

        for row in rows:
            parsed = _parse(row.get("end_date"))
            if parsed is None:
                continue
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            self.assertGreaterEqual(parsed, now - timedelta(minutes=5))
            self.assertLessEqual(parsed, max_dt + timedelta(minutes=5))

    def test_search_term_filters(self):
        term = self.search_term
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            search=term,
            limit=200,
        )
        self.assertGreater(len(rows), 0)
        for row in rows:
            q = (row.get("question") or "").lower()
            o = (row.get("outcome_name") or "").lower()
            self.assertTrue(term in q or term in o)

    def test_tags_endpoint_returns_data(self):
        data = self.app_main.get_tags()
        self.assertGreater(len(data), 0)
