import unittest
from unittest.mock import patch, MagicMock
from smart_money_scraper import process_market_holders_worker

class TestSmartMoneySkip(unittest.TestCase):
    @patch('smart_money_scraper.HoldersClient')
    @patch('smart_money_scraper.get_db_connection')
    @patch('smart_money_scraper.time.sleep', return_value=None)
    def test_process_market_holders_skips_on_none(self, mock_sleep, mock_db, mock_client_class):
        # Mock HoldersClient.fetch_holders to return None
        mock_client = mock_client_class.return_value
        mock_client.fetch_holders.return_value = None
        
        result = process_market_holders_worker("market_fail")
        
        # Result should be empty list of wallets
        self.assertEqual(result, [])
        # DB connection should NOT be called (no save)
        self.assertFalse(mock_db.called)

    @patch('smart_money_scraper.HoldersClient')
    @patch('smart_money_scraper.get_db_connection')
    @patch('smart_money_scraper.save_holders_batch')
    @patch('smart_money_scraper.time.sleep', return_value=None)
    def test_process_market_holders_saves_on_success(self, mock_sleep, mock_save, mock_db, mock_client_class):
        # Mock HoldersClient.fetch_holders to return valid data
        mock_client = mock_client_class.return_value
        mock_client.fetch_holders.return_value = [{"address": "0x1", "outcomeIndex": 0}]
        
        result = process_market_holders_worker("market_success")
        
        self.assertEqual(result, ["0x1"])
        self.assertTrue(mock_save.called)

if __name__ == '__main__':
    unittest.main()
