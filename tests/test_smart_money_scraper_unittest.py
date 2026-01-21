import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust path if needed, but since we run from root, it should be fine
# import smart_money_scraper 

class TestSmartMoneyScraper(unittest.TestCase):
    @patch('smart_money_scraper.get_db_connection')
    @patch('smart_money_scraper.HoldersClient')
    @patch('smart_money_scraper.PnLClient')
    def test_run_flow(self, MockPnL, MockHolders, mock_db_conn):
        import smart_money_scraper
        
        # Mock DB
        mock_conn = MagicMock()
        mock_db_conn.return_value = mock_conn
        
        # Mock active markets
        mock_cursor = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"condition_id": "m1"}]
        
        # Mock Holders Client
        mock_h_instance = MockHolders.return_value
        mock_h_instance.fetch_holders.return_value = [
            {"address": "0x1", "positionSize": 100, "outcomeIndex": 0}
        ]
        
        # Mock PnL Client
        mock_p_instance = MockPnL.return_value
        mock_p_instance.fetch_user_pnl.return_value = 50.0
        
        # Run
        smart_money_scraper.run([])
        
        # Verify
        # It should call with limit 1000
        mock_h_instance.fetch_holders.assert_called_with("m1", limit=1000)
        
        # Verify PnL fetched 
        # Since it runs in threads, timing is tricky but run() waits for threads.
        mock_p_instance.fetch_user_pnl.assert_called_with("0x1")
        
        # Verify DB calls
        # We expect INSERT into holders and wallets_stats
        # save_holders_batch calls executemany
        self.assertTrue(mock_conn.executemany.called)
        # save_wallet_stats calls execute
        self.assertTrue(mock_conn.execute.called)

if __name__ == '__main__':
    unittest.main()
