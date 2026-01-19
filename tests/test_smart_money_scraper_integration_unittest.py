import unittest
import sqlite3
import os
from unittest.mock import MagicMock, patch
import smart_money_scraper

class TestSmartMoneyScraperIntegration(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_scraper_integration.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        # Patch DB
        self.patcher_db = patch('smart_money_scraper.get_db_connection')
        self.mock_get_db = self.patcher_db.start()
        
        # Initialize DB
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("CREATE TABLE wallets_stats (wallet_address TEXT PRIMARY KEY, total_pnl REAL, last_updated TEXT, alias TEXT)")
        conn.execute("CREATE TABLE holders (market_id TEXT, outcome_index INTEGER, wallet_address TEXT, position_size REAL, snapshot_at TEXT)")
        conn.execute("CREATE TABLE active_market_outcomes (condition_id TEXT, smart_money_win_rate REAL)")
        # Insert a fake market
        conn.execute("INSERT INTO active_market_outcomes (condition_id) VALUES ('fake_cid')")
        conn.commit()
        conn.close()
        
        self.mock_get_db.side_effect = lambda: self._get_conn()

        # Patch Clients
        self.patcher_goldsky = patch('smart_money_scraper.GoldskyClient')
        self.MockGoldsky = self.patcher_goldsky.start()
        
        self.patcher_holders = patch('smart_money_scraper.HoldersClient')
        self.MockHolders = self.patcher_holders.start()

        self.patcher_pnl = patch('smart_money_scraper.PnLClient')
        self.MockPnL = self.patcher_pnl.start()

    def _get_conn(self):
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def tearDown(self):
        self.patcher_db.stop()
        self.patcher_goldsky.stop()
        self.patcher_holders.stop()
        self.patcher_pnl.stop()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_run_saves_alias_from_holders_client(self):
        # Setup: Goldsky fails (so we use Legacy), Legacy returns alias
        mock_goldsky_instance = self.MockGoldsky.return_value
        mock_goldsky_instance.fetch_holders_subgraph.return_value = None # Force fallback

        mock_holders_instance = self.MockHolders.return_value
        mock_holders_instance.fetch_holders.return_value = [
            {"address": "0xWhale", "positionSize": 1000, "name": "BigWhale"}
        ]
        
        mock_pnl_instance = self.MockPnL.return_value
        mock_pnl_instance.fetch_user_pnl.return_value = 500.0

        # Execute
        smart_money_scraper.run(args_list=[])

        # Verify
        conn = sqlite3.connect(self.test_db_path)
        row = conn.execute("SELECT alias, total_pnl FROM wallets_stats WHERE wallet_address='0xWhale'").fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "BigWhale")
        self.assertEqual(row[1], 500.0)

    def test_run_handles_missing_alias(self):
        # Setup: Goldsky fails, Legacy returns alias as empty string
        mock_goldsky_instance = self.MockGoldsky.return_value
        mock_goldsky_instance.fetch_holders_subgraph.return_value = None

        mock_holders_instance = self.MockHolders.return_value
        mock_holders_instance.fetch_holders.return_value = [
            {"address": "0xAnon", "positionSize": 1000, "name": ""}
        ]
        
        mock_pnl_instance = self.MockPnL.return_value
        mock_pnl_instance.fetch_user_pnl.return_value = 100.0

        # Execute
        smart_money_scraper.run(args_list=[])

        # Verify
        conn = sqlite3.connect(self.test_db_path)
        row = conn.execute("SELECT alias FROM wallets_stats WHERE wallet_address='0xAnon'").fetchone()
        conn.close()
        
        self.assertIsNone(row[0])

    def test_run_enrich_aliases_when_goldsky_succeeds(self):
        # Setup: Goldsky succeeds (returns data without aliases)
        mock_goldsky_instance = self.MockGoldsky.return_value
        mock_goldsky_instance.fetch_holders_subgraph.return_value = [
            {"address": "0xGoldUser", "positionSize": 500, "outcomeIndex": 1}
        ]

        # Legacy also succeeds and returns alias
        mock_holders_instance = self.MockHolders.return_value
        mock_holders_instance.fetch_holders.return_value = [
            {"address": "0xGoldUser", "positionSize": 500, "name": "GoldWhale"}
        ]
        
        mock_pnl_instance = self.MockPnL.return_value
        mock_pnl_instance.fetch_user_pnl.return_value = 1000.0

        # Execute
        smart_money_scraper.run(args_list=[])

        # Verify
        conn = sqlite3.connect(self.test_db_path)
        row = conn.execute("SELECT alias, total_pnl FROM wallets_stats WHERE wallet_address='0xGoldUser'").fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "GoldWhale")
        self.assertEqual(row[1], 1000.0)

if __name__ == '__main__':
    unittest.main()
