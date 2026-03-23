import os
import sqlite3
import tempfile
import unittest

from smart_money_materialized import rebuild_market_smart_money_stats


class TestSmartMoneyMaterializedStats(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(
            """
            CREATE TABLE holders (
                market_id TEXT,
                outcome_index INTEGER,
                wallet_address TEXT,
                position_size REAL,
                snapshot_at TEXT
            );
            CREATE TABLE wallets_stats (
                wallet_address TEXT PRIMARY KEY,
                total_pnl REAL,
                last_updated TEXT,
                alias TEXT,
                wallet_tag TEXT
            );
            """
        )
        self.conn.executemany(
            "INSERT INTO holders (market_id, outcome_index, wallet_address, position_size, snapshot_at) VALUES (?, ?, ?, ?, ?)",
            [
                ("c1", 0, "w1", 10, "2026-03-23T00:00:00+00:00"),
                ("c1", 0, "w2", 9, "2026-03-23T00:00:00+00:00"),
                ("c1", 0, "w3", 8, "2026-03-23T00:00:00+00:00"),
                ("c1", 1, "w4", 7, "2026-03-23T00:00:00+00:00"),
                ("c1", 1, "w5", 6, "2026-03-23T00:00:00+00:00"),
                ("c1", 1, "w6", 5, "2026-03-23T00:00:00+00:00"),
            ],
        )
        self.conn.executemany(
            "INSERT INTO wallets_stats (wallet_address, total_pnl, last_updated) VALUES (?, ?, ?)",
            [
                ("w1", 1000, "2026-03-23T00:00:00+00:00"),
                ("w2", 500, "2026-03-23T00:00:00+00:00"),
                ("w3", -10, "2026-03-23T00:00:00+00:00"),
                ("w4", -250, "2026-03-23T00:00:00+00:00"),
                ("w5", 80, "2026-03-23T00:00:00+00:00"),
                ("w6", -90, "2026-03-23T00:00:00+00:00"),
            ],
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_rebuild_populates_full_per_side_counts(self):
        rebuild_market_smart_money_stats(self.conn, generated_at="2026-03-23T01:00:00+00:00")
        row = self.conn.execute(
            "SELECT * FROM market_smart_money_stats WHERE condition_id = 'c1'"
        ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["yes_profitable_count"], 2)
        self.assertEqual(row["yes_losing_count"], 1)
        self.assertEqual(row["yes_total"], 3)
        self.assertEqual(row["no_profitable_count"], 1)
        self.assertEqual(row["no_losing_count"], 2)
        self.assertEqual(row["no_total"], 3)
        self.assertEqual(row["last_updated_at"], "2026-03-23T01:00:00+00:00")
        self.assertAlmostEqual(row["smart_money_win_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
