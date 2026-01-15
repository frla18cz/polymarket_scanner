import unittest
import sqlite3
import os
import shutil
from pathlib import Path
from unittest.mock import patch
import main

class TestHoldersSchema(unittest.TestCase):
    def setUp(self):
        # Create a temp DB path
        self.test_db_path = "test_holders_schema.db"
        # Ensure it doesn't exist
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        # We need to simulate the environment where the DB is at self.test_db_path
        # We can patch main.DB_PATH or main.get_db_connection
        self.patcher = patch('main.DB_PATH', self.test_db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        # Also remove WAL files
        if os.path.exists(self.test_db_path + "-wal"):
            os.remove(self.test_db_path + "-wal")
        if os.path.exists(self.test_db_path + "-shm"):
            os.remove(self.test_db_path + "-shm")

    def test_wallets_stats_has_alias_column(self):
        # Initialize DB (this should create tables)
        main.ensure_indices()
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check columns of wallets_stats
        cursor.execute("PRAGMA table_info(wallets_stats)")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        self.assertIn("alias", columns, "Column 'alias' is missing in wallets_stats table")

if __name__ == '__main__':
    unittest.main()