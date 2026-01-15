import unittest
import sqlite3
import os
from unittest.mock import MagicMock, patch
from smart_money_scraper import save_wallet_stats, get_db_connection

class TestSmartMoneyScraperAlias(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_alias_scraper.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # Patch DB connection to use our test DB
        self.patcher = patch('smart_money_scraper.get_db_connection')
        self.mock_get_db = self.patcher.start()
        
        # Setup DB schema
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("CREATE TABLE wallets_stats (wallet_address TEXT PRIMARY KEY, total_pnl REAL, last_updated TEXT, alias TEXT)")
        conn.commit()
        conn.close()
        
        self.mock_get_db.side_effect = lambda: sqlite3.connect(self.test_db_path)

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_save_wallet_stats_saves_alias(self):
        conn = self.mock_get_db()
        
        # Should be able to save with alias
        # Note: current implementation signature is save_wallet_stats(conn, wallet, pnl)
        # We expect to change it to save_wallet_stats(conn, wallet, pnl, alias=None)
        
        try:
            save_wallet_stats(conn, "0x123", 100.0, alias="WhaleUser")
        except TypeError:
             # This failure is expected before implementation
             self.fail("save_wallet_stats() does not accept 'alias' argument yet.")
        
        # Verify
        row = conn.execute("SELECT alias FROM wallets_stats WHERE wallet_address='0x123'").fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "WhaleUser")

    def test_save_wallet_stats_preserves_existing_alias_if_new_is_none(self):
        conn = self.mock_get_db()
        
        # Insert initial record with alias
        conn.execute("INSERT INTO wallets_stats (wallet_address, total_pnl, last_updated, alias) VALUES (?, ?, ?, ?)", 
                     ("0x123", 50.0, "2024-01-01", "ExistingAlias"))
        conn.commit()
        
        # Update PnL but provide no alias (None)
        try:
            save_wallet_stats(conn, "0x123", 200.0, alias=None)
        except TypeError:
             self.fail("save_wallet_stats() does not accept 'alias' argument yet.")

        # Verify alias is still "ExistingAlias"
        row = conn.execute("SELECT alias, total_pnl FROM wallets_stats WHERE wallet_address='0x123'").fetchone()
        conn.close()
        
        self.assertEqual(row[0], "ExistingAlias")
        self.assertEqual(row[1], 200.0)

if __name__ == '__main__':
    unittest.main()
