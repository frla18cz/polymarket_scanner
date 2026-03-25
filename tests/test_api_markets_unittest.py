import os
import sqlite3
import unittest
from datetime import datetime, timedelta, timezone
from typing import Iterable

from fastapi import Response

from tests._db_snapshot import snapshot_main_db


class TestMarketsFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._snapshot = snapshot_main_db()
        os.environ["MARKETS_DB_PATH"] = str(cls._snapshot.path)

        import main as app_main
        import market_queries as market_queries_module
        # CRITICAL: Overwrite module-level constant if already imported by other tests
        app_main.DB_PATH = str(cls._snapshot.path)
        cls.app_main = app_main
        cls.market_queries = market_queries_module
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

        cls.expiry_regression_search = "expiry-regression-case"
        now = datetime.now(timezone.utc)
        cls._insert_market(
            market_id="expiry_future_case",
            condition_id="cond_expiry_future_case",
            question=f"{cls.expiry_regression_search} future market",
            end_date=(now + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        cls._insert_market(
            market_id="expiry_expired_case",
            condition_id="cond_expiry_expired_case",
            question=f"{cls.expiry_regression_search} expired market",
            end_date=(now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        cls._insert_market(
            market_id="expiry_null_case",
            condition_id="cond_expiry_null_case",
            question=f"{cls.expiry_regression_search} null end market",
            end_date=None,
        )
        cls._conn.commit()

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

    @classmethod
    def _insert_market(
        cls,
        *,
        market_id: str,
        condition_id: str,
        question: str,
        end_date: str | None,
        outcome_name: str = "Yes",
        outcome_index: int = 0,
    ) -> None:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        cls._conn.execute(
            """
            INSERT INTO active_market_outcomes (
                snapshot_at, market_id, condition_id, outcome_index, event_slug, question, url,
                outcome_name, price, apr, spread, volume_usd, liquidity_usd, start_date, end_date,
                category, icon_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now_str,
                market_id,
                condition_id,
                outcome_index,
                market_id,
                question,
                f"https://example.com/{market_id}",
                outcome_name,
                0.55,
                None,
                0.01,
                250000.0,
                25000.0,
                now_str,
                end_date,
                "Regression",
                None,
            ),
        )

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

    def test_min_hours_to_expire_filter(self):
        candidates = [1, 6, 12, 24, 48, 24 * 7]
        chosen = None
        for h in candidates:
            soon = self._conn.execute(
                """
                SELECT COUNT(*) AS n FROM active_market_outcomes
                WHERE end_date IS NOT NULL
                  AND datetime(end_date) > datetime('now')
                  AND datetime(end_date) < datetime('now', ?)
                """,
                (f"+{int(h)} hours",),
            ).fetchone()["n"]
            later = self._conn.execute(
                """
                SELECT COUNT(*) AS n FROM active_market_outcomes
                WHERE end_date IS NOT NULL
                  AND datetime(end_date) >= datetime('now', ?)
                """,
                (f"+{int(h)} hours",),
            ).fetchone()["n"]
            if soon and later:
                chosen = int(h)
                break

        if not chosen:
            self.skipTest("V DB nejsou vhodné end_date intervaly pro test min_hours_to_expire.")

        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            min_hours_to_expire=chosen,
            include_expired=False,
            limit=200,
        )
        self.assertGreater(len(rows), 0)

        from datetime import timedelta

        now = datetime.now(timezone.utc)
        min_dt = now + timedelta(hours=chosen)

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
            self.assertGreaterEqual(parsed, min_dt - timedelta(minutes=5))

    def test_expiry_window_filter_24h_to_7d(self):
        min_h = 24
        max_h = 24 * 7
        count = self._conn.execute(
            """
            SELECT COUNT(*) AS n FROM active_market_outcomes
            WHERE end_date IS NOT NULL
              AND datetime(end_date) >= datetime('now', ?)
              AND datetime(end_date) <= datetime('now', ?)
            """,
            (f"+{min_h} hours", f"+{max_h} hours"),
        ).fetchone()["n"]
        if not count:
            self.skipTest("V DB nejsou záznamy v okně 24h–7d.")

        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            min_hours_to_expire=min_h,
            max_hours_to_expire=max_h,
            include_expired=False,
            limit=200,
        )
        self.assertGreater(len(rows), 0)

        from datetime import timedelta

        now = datetime.now(timezone.utc)
        min_dt = now + timedelta(hours=min_h)
        max_dt = now + timedelta(hours=max_h)

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
            self.assertGreaterEqual(parsed, min_dt - timedelta(minutes=5))
            self.assertLessEqual(parsed, max_dt + timedelta(minutes=5))

    def test_hide_expired_without_window_excludes_expired_rows(self):
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            search=self.expiry_regression_search,
            include_expired=False,
            min_volume=0,
            min_liquidity=0,
            limit=200,
        )
        ids = self._market_ids(rows)
        self.assertIn("expiry_future_case", ids)
        self.assertIn("expiry_null_case", ids)
        self.assertNotIn("expiry_expired_case", ids)

    def test_include_expired_true_keeps_expired_rows(self):
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            search=self.expiry_regression_search,
            include_expired=True,
            min_volume=0,
            min_liquidity=0,
            limit=200,
        )
        ids = self._market_ids(rows)
        self.assertIn("expiry_future_case", ids)
        self.assertIn("expiry_null_case", ids)
        self.assertIn("expiry_expired_case", ids)

    def test_hide_expired_keeps_null_end_date_rows_without_window(self):
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            search="null end market",
            include_expired=False,
            min_volume=0,
            min_liquidity=0,
            limit=50,
        )
        ids = self._market_ids(rows)
        self.assertIn("expiry_null_case", ids)

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

    def test_apr_index_exists(self):
        rows = self._conn.execute("PRAGMA index_list(active_market_outcomes)").fetchall()
        idx_names = {r["name"] for r in rows if r and r["name"]}
        self.assertIn("idx_amo_apr", idx_names)

    def test_end_date_index_exists(self):
        rows = self._conn.execute("PRAGMA index_list(active_market_outcomes)").fetchall()
        idx_names = {r["name"] for r in rows if r and r["name"]}
        self.assertIn("idx_amo_end_date", idx_names)

    def test_expiry_query_plan_uses_end_date_index_when_windowed(self):
        sql, params = self.market_queries.build_markets_sql(
            self._conn,
            include_expired=False,
            max_hours_to_expire=24 * 7,
            sort_by="end_date",
            sort_dir="asc",
            min_volume=0,
            min_liquidity=0,
            limit=100,
            offset=0,
        )
        plan_rows = self._conn.execute(f"EXPLAIN QUERY PLAN {sql}", params).fetchall()
        details = " | ".join(
            str(row["detail"] if hasattr(row, "keys") and "detail" in row.keys() else row)
            for row in plan_rows
        )
        self.assertIn("idx_amo_end_date", details)

    def test_min_apr_filters_and_sorts(self):
        total = self._conn.execute(
            "SELECT COUNT(*) AS n FROM active_market_outcomes WHERE apr IS NOT NULL AND apr > 0"
        ).fetchone()["n"]
        if not total:
            self.skipTest("V DB nejsou k dispozici žádné APR hodnoty.")

        offset = int(total * 0.5)
        row = self._conn.execute(
            """
            SELECT apr FROM active_market_outcomes
            WHERE apr IS NOT NULL AND apr > 0
            ORDER BY apr ASC
            LIMIT 1 OFFSET ?
            """,
            (offset,),
        ).fetchone()
        if not row or row["apr"] is None:
            self.skipTest("Nenašla se vhodná APR hodnota pro threshold.")

        threshold = float(row["apr"])
        rows = self.app_main.get_markets(
            Response(),
            included_tags=None,
            excluded_tags=None,
            min_apr=threshold,
            sort_by="apr",
            sort_dir="desc",
            limit=200,
        )
        self.assertGreater(len(rows), 0)

        prev = float("inf")
        for r in rows:
            apr = r.get("apr")
            self.assertIsNotNone(apr)
            self.assertGreaterEqual(float(apr), threshold)
            self.assertLessEqual(float(apr), prev + 1e-12)
            prev = float(apr)

    def test_apr_formula_matches_snapshot(self):
        import math

        row = self._conn.execute(
            """
            SELECT price, end_date, snapshot_at, apr
            FROM active_market_outcomes
            WHERE apr IS NOT NULL AND apr > 0
              AND price IS NOT NULL AND price > 0 AND price < 1
              AND end_date IS NOT NULL AND snapshot_at IS NOT NULL
            LIMIT 1
            """
        ).fetchone()
        if not row:
            self.skipTest("V DB nejsou vhodné záznamy pro ověření APR.")

        price = float(row["price"])
        apr = float(row["apr"])
        self.assertTrue(math.isfinite(apr))

        snap_s = str(row["snapshot_at"]).strip()
        end_s = str(row["end_date"]).strip()
        if end_s.endswith("Z"):
            end_s = end_s[:-1] + "+00:00"
        snap_dt = datetime.fromisoformat(snap_s)
        end_dt = datetime.fromisoformat(end_s)
        if snap_dt.tzinfo is None:
            snap_dt = snap_dt.replace(tzinfo=timezone.utc)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)

        days = (end_dt - snap_dt).total_seconds() / 86400.0
        if not math.isfinite(days) or days <= 0:
            self.skipTest("Neplatný interval pro APR výpočet.")

        roi = (1.0 / price) - 1.0
        expected = roi * (365.0 / days)
        self.assertTrue(math.isfinite(expected))
        self.assertGreater(expected, 0.0)

        tol = max(1e-9, expected * 1e-4)
        self.assertLess(abs(apr - expected), tol)

    def test_apr_null_visibility(self):
        """Verify that markets with NULL APR are visible by default (min_apr=0)."""
        self._conn.execute("""
            INSERT INTO active_market_outcomes (
                market_id, condition_id, outcome_name, question, price, volume_usd, liquidity_usd, 
                apr, end_date, snapshot_at
            ) VALUES (
                'test_apr_null', 'cond_apr_null', 'Yes', 'APR test?', 0.5, 1000, 500,
                NULL, '2026-12-31T23:59:59Z', '2026-01-20T00:00:00Z'
            )
        """)
        self._conn.commit()

        response = Response()
        # Frontend sends min_apr=0 by default
        markets = self.app_main.get_markets(response=response, min_apr=0.0, limit=2000)
        
        null_market = next((m for m in markets if m["market_id"] == 'test_apr_null'), None)
        self.assertIsNotNone(null_market, "Market with NULL APR should be visible when filter is 0.0")
        self.assertIsNone(null_market.get("apr"))
