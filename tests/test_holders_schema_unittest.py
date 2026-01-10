import unittest
import os
import sqlite3
from pathlib import Path

# Adjust path to import main
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main

class TestHoldersSchema(unittest.TestCase):
    def setUp(self):
        # Use an in-memory DB or a temp file for testing
        self.db_path = "test_holders_schema.db"
        os.environ["MARKETS_DB_PATH"] = self.db_path
        # Force main to reload DB path if it was cached (it's a global var in main, tricky)
        # But main.get_db_connection uses the global DB_PATH which is set at module level.
        # We need to monkeypatch or reload. Monkeypatching main.DB_PATH is easier.
        main.DB_PATH = self.db_path
        
        # Ensure clean slate
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_tables_created(self):
        """Test that holders and wallets_stats tables are created by ensure_indices."""
        # This calls the function that should create the tables
        main.ensure_indices()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check holders table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='holders'")
        self.assertIsNotNone(cursor.fetchone(), "Table 'holders' should exist")
        
        # Check wallets_stats table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wallets_stats'")
        self.assertIsNotNone(cursor.fetchone(), "Table 'wallets_stats' should exist")
        
        # Check columns in holders
        cursor.execute("PRAGMA table_info(holders)")
        cols = {row[1] for row in cursor.fetchall()}
        expected_cols = {'market_id', 'outcome_index', 'wallet_address', 'position_size', 'snapshot_at'}
        self.assertTrue(expected_cols.issubset(cols), f"Missing columns in holders: {expected_cols - cols}")

        conn.close()

if __name__ == '__main__':
    unittest.main()
