import unittest
from unittest.mock import patch, MagicMock
import smart_money_scraper

class TestGoldskyIntegration(unittest.TestCase):
    @patch('smart_money_scraper.get_db_connection')
    @patch('smart_money_scraper.GoldskyClient')
    @patch('smart_money_scraper.HoldersClient')
    def test_worker_uses_goldsky_first(self, MockHolders, MockGoldsky, mock_db_conn):
        # Setup mocks
        mock_goldsky_instance = MockGoldsky.return_value
        mock_holders_instance = MockHolders.return_value
        
        # Scenario: Goldsky returns data
        mock_goldsky_instance.fetch_holders_subgraph.return_value = [
            {"address": "0xGold", "positionSize": 500, "outcomeIndex": 1}
        ]
        
        # Mock DB
        mock_conn = MagicMock()
        mock_db_conn.return_value = mock_conn
        
        condition_id = "test_condition"
        
        # Call worker
        wallets = smart_money_scraper.process_market_holders_worker(condition_id)
        
        # Assertions
        mock_goldsky_instance.fetch_holders_subgraph.assert_called_once_with(condition_id)
        # HoldersClient should NOT be called if Goldsky succeeded (or at least Goldsky was tried first)
        self.assertFalse(mock_holders_instance.fetch_holders.called)
        self.assertEqual(wallets, ["0xGold"])

    @patch('smart_money_scraper.get_db_connection')
    @patch('smart_money_scraper.GoldskyClient')
    @patch('smart_money_scraper.HoldersClient')
    def test_worker_fallback_to_legacy(self, MockHolders, MockGoldsky, mock_db_conn):
        # Setup mocks
        mock_goldsky_instance = MockGoldsky.return_value
        mock_holders_instance = MockHolders.return_value
        
        # Scenario: Goldsky fails (returns None)
        mock_goldsky_instance.fetch_holders_subgraph.return_value = None
        
        # Legacy returns data
        mock_holders_instance.fetch_holders.return_value = [
            {"address": "0xLegacy", "positionSize": 100, "outcomeIndex": 0}
        ]
        
        # Mock DB
        mock_conn = MagicMock()
        mock_db_conn.return_value = mock_conn
        
        condition_id = "test_condition"
        
        # Call worker
        wallets = smart_money_scraper.process_market_holders_worker(condition_id)
        
        # Assertions
        mock_goldsky_instance.fetch_holders_subgraph.assert_called_once_with(condition_id)
        mock_holders_instance.fetch_holders.assert_called_once_with(condition_id, limit=1000)
        self.assertEqual(wallets, ["0xLegacy"])

if __name__ == '__main__':
    unittest.main()
