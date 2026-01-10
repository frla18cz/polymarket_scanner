import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import main
import sqlite3

class TestApiHoldersIntegration(unittest.TestCase):
    def setUp(self):
        # We need to override get_db_connection to return a mock or use a test DB.
        # Since we want to test the SQL logic, using an in-memory DB is best.
        self.client = TestClient(main.app)
        
        # Setup in-memory DB with check_same_thread=False to allow access from FastAPI threads
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
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
                last_updated TEXT
            );
            INSERT INTO holders (market_id, outcome_index, wallet_address, position_size) VALUES 
            ('m1', 0, '0x1', 100.0),
            ('m1', 1, '0x2', 50.0);
            
            INSERT INTO wallets_stats (wallet_address, total_pnl) VALUES 
            ('0x1', 1000.0),
            ('0x2', -500.0);
        """)

    def tearDown(self):
        self.conn.close()

    @patch('main.get_db_connection')
    def test_get_holders_endpoint(self, mock_get_db):
        mock_get_db.return_value = self.conn
        
        response = self.client.get("/api/markets/m1/holders")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data), 2)
        # Sort order check (should be outcome ASC, size DESC)
        self.assertEqual(data[0]["wallet_address"], "0x1")
        self.assertEqual(data[0]["total_pnl"], 1000.0)
        self.assertEqual(data[1]["wallet_address"], "0x2")
        self.assertEqual(data[1]["total_pnl"], -500.0)

if __name__ == '__main__':
    unittest.main()
