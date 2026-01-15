import unittest
import sqlite3
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
import main

class TestAPIHoldersAlias(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_api_holders.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        # Patch DB
        self.patcher = patch('main.DB_PATH', self.test_db_path)
        self.patcher.start()
        
        # Setup DB schema and data
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("CREATE TABLE holders (market_id TEXT, outcome_index INTEGER, wallet_address TEXT, position_size REAL, snapshot_at TEXT)")
        conn.execute("CREATE TABLE wallets_stats (wallet_address TEXT PRIMARY KEY, total_pnl REAL, last_updated TEXT, alias TEXT)")
        
        # Data
        conn.execute("INSERT INTO holders VALUES ('m1', 0, '0x1', 100.0, '2024-01-01')")
        conn.execute("INSERT INTO wallets_stats VALUES ('0x1', 500.0, '2024-01-01', 'Whale1')")
        conn.commit()
        conn.close()
        
        # We need to re-initialize main's DB related things if any, but main.get_db_connection uses main.DB_PATH
        self.client = TestClient(main.app)

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_get_holders_returns_alias(self):
        response = self.client.get("/api/markets/m1/holders")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["wallet_address"], "0x1")
        # This is expected to fail before implementation
        self.assertEqual(data[0]["alias"], "Whale1")

if __name__ == '__main__':
    unittest.main()
