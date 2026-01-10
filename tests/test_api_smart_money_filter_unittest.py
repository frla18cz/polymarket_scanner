import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import main
import sqlite3

class TestApiSmartMoneyFilter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Setup schema (simplified)
        self.conn.executescript("""
            CREATE TABLE active_market_outcomes (
                market_id TEXT,
                question TEXT,
                outcome_name TEXT,
                volume_usd REAL,
                liquidity_usd REAL,
                price REAL,
                spread REAL,
                end_date TEXT,
                snapshot_at TEXT,
                apr REAL,
                smart_money_win_rate REAL
            );
            CREATE TABLE market_tags (
                market_id TEXT,
                tag_label TEXT
            );
            
            INSERT INTO active_market_outcomes (market_id, smart_money_win_rate, volume_usd, price) VALUES 
            ('m1', 0.8, 1000, 0.5),
            ('m2', 0.2, 1000, 0.5),
            ('m3', 0.5, 1000, 0.5),
            ('m4', NULL, 1000, 0.5);
        """)

    def tearDown(self):
        self.conn.close()

    @patch('main.get_db_connection')
    def test_filter_by_smart_money(self, mock_get_db):
        mock_get_db.return_value = self.conn
        
        # Test: Min Win Rate 0.5
        response = self.client.get("/api/markets?min_smart_money_win_rate=0.5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data), 2) # m1 (0.8), m3 (0.5)
        ids = sorted([d['market_id'] for d in data])
        self.assertEqual(ids, ['m1', 'm3'])

    @patch('main.get_db_connection')
    def test_sort_by_smart_money(self, mock_get_db):
        mock_get_db.return_value = self.conn
        
        response = self.client.get("/api/markets?sort_by=smart_money_win_rate&sort_dir=desc")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Order should be m1 (0.8), m3 (0.5), m2 (0.2), m4 (NULL - usually last or first depending on DB)
        # SQLite NULLs are considered smallest, so in DESC they come last? No, first?
        # Default SQLite: NULLs are smaller than any value. DESC puts NULLs last.
        
        self.assertEqual(data[0]['market_id'], 'm1')
        self.assertEqual(data[1]['market_id'], 'm3')
        self.assertEqual(data[2]['market_id'], 'm2')

if __name__ == '__main__':
    unittest.main()
