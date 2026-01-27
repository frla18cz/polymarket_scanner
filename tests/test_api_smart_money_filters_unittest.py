import os
import sqlite3
import unittest
from fastapi import Response
import tempfile
from pathlib import Path

class TestSmartMoneyFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary database for testing
        cls.db_fd, cls.db_path = tempfile.mkstemp()
        os.environ["MARKETS_DB_PATH"] = cls.db_path

        import main as app_main
        app_main.DB_PATH = cls.db_path
        cls.app_main = app_main
        
        conn = sqlite3.connect(cls.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS active_market_outcomes (
                market_id TEXT,
                condition_id TEXT,
                outcome_index INTEGER,
                question TEXT,
                outcome_name TEXT,
                price REAL,
                volume_usd REAL,
                liquidity_usd REAL,
                spread REAL,
                end_date TEXT,
                snapshot_at TEXT,
                apr REAL
            );
            CREATE TABLE IF NOT EXISTS market_tags (
                market_id TEXT,
                tag_label TEXT
            );
            CREATE TABLE IF NOT EXISTS holders (
                market_id TEXT,
                outcome_index INTEGER,
                wallet_address TEXT,
                position_size REAL,
                snapshot_at TEXT
            );
            CREATE TABLE IF NOT EXISTS wallets_stats (
                wallet_address TEXT PRIMARY KEY,
                total_pnl REAL,
                last_updated TEXT,
                alias TEXT,
                wallet_tag TEXT
            );
        """)
        
        # Run app's own initialization
        app_main.ensure_indices()

        # Mock Data
        # Market 1: High Smart Money Dominance (3 profitable holders on Yes, 2 losing on No)
        conn.execute("INSERT INTO active_market_outcomes (market_id, condition_id, outcome_index, question, outcome_name, volume_usd, liquidity_usd, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     ("m1", "c1", 0, "Smart Market?", "Yes", 10000, 5000, 0.5))
        conn.execute("INSERT INTO active_market_outcomes (market_id, condition_id, outcome_index, question, outcome_name, volume_usd, liquidity_usd, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     ("m1", "c1", 1, "Smart Market?", "No", 10000, 5000, 0.5))
        
        # Holders for c1 Outcome 0 (Yes)
        profitable_wallets = ["w1", "w2", "w3"]
        for w in profitable_wallets:
            conn.execute("INSERT INTO holders (market_id, outcome_index, wallet_address) VALUES (?, ?, ?)", ("c1", 0, w))
            conn.execute("INSERT OR REPLACE INTO wallets_stats (wallet_address, total_pnl) VALUES (?, ?)", (w, 5000))
        # Neutral wallet (PnL == 0) should not be counted as profitable or losing
        conn.execute("INSERT INTO holders (market_id, outcome_index, wallet_address) VALUES (?, ?, ?)", ("c1", 0, "w0"))
        conn.execute("INSERT OR REPLACE INTO wallets_stats (wallet_address, total_pnl) VALUES (?, ?)", ("w0", 0))
            
        # Holders for c1 Outcome 1 (No)
        losing_wallets = ["w4", "w5"]
        for w in losing_wallets:
            conn.execute("INSERT INTO holders (market_id, outcome_index, wallet_address) VALUES (?, ?, ?)", ("c1", 1, w))
            conn.execute("INSERT OR REPLACE INTO wallets_stats (wallet_address, total_pnl) VALUES (?, ?)", (w, -2000))
            
        # Market 2: Low Smart Money (1 profitable holder)
        conn.execute("INSERT INTO active_market_outcomes (market_id, condition_id, outcome_index, question, outcome_name, volume_usd, liquidity_usd, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     ("m2", "c2", 0, "Dumb Market?", "Yes", 5000, 1000, 0.5))
        conn.execute("INSERT INTO holders (market_id, outcome_index, wallet_address) VALUES (?, ?, ?)", ("c2", 0, "w6"))
        conn.execute("INSERT OR REPLACE INTO wallets_stats (wallet_address, total_pnl) VALUES (?, ?)", ("w6", 500))
        
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        os.close(cls.db_fd)
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_filter_min_profitable(self):
        res = self.app_main.get_markets(Response(), min_profitable=2, profit_threshold=1000)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["market_id"], "m1")

    def test_filter_min_losing_opposite(self):
        # We want markets where current outcome has X losing holders on the OTHER side
        res = self.app_main.get_markets(Response(), min_losing_opposite=2, profit_threshold=1000)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["market_id"], "m1")
        self.assertEqual(res[0]["outcome_name"], "Yes")

    def test_profit_threshold_is_ignored_for_sign_logic(self):
        # Large threshold should not change sign-based counts
        res = self.app_main.get_markets(Response(), min_profitable=1, profit_threshold=100000)
        market_ids = [r["market_id"] for r in res]
        self.assertIn("m1", market_ids)
        self.assertIn("m2", market_ids)

    def test_counts_use_positive_negative_pnl(self):
        res = self.app_main.get_markets(Response(), limit=10)
        target = next(r for r in res if r["market_id"] == "m1" and r["outcome_name"] == "Yes")
        self.assertEqual(target["smart_profitable_count"], 3)
        self.assertEqual(target["smart_losing_opposite_count"], 2)
        self.assertEqual(target["smart_profitable_total"], 4)

    def test_no_results(self):
        res = self.app_main.get_markets(Response(), min_profitable=10)
        self.assertEqual(len(res), 0)

if __name__ == "__main__":
    unittest.main()
