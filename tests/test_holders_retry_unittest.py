import unittest
from unittest.mock import patch, MagicMock
import requests
from holders_client import HoldersClient

class TestHoldersRetry(unittest.TestCase):
    @patch('requests.get')
    @patch('time.sleep', return_value=None)  # Don't wait during tests
    def test_fetch_holders_retries_on_failure(self, mock_sleep, mock_get):
        client = HoldersClient()
        
        # Mock failure, then success with enough data
        mock_error = requests.exceptions.RequestException("Network error")
        mock_success = MagicMock()
        mock_success.status_code = 200
        
        holders_0 = [{"proxyWallet": f"0x0_{i}", "amount": 10, "outcomeIndex": 0} for i in range(20)]
        holders_1 = [{"proxyWallet": f"0x1_{i}", "amount": 10, "outcomeIndex": 1} for i in range(20)]
        mock_success.json.return_value = [{"holders": holders_0 + holders_1}]
        
        # First two calls fail, third succeeds
        mock_get.side_effect = [mock_error, mock_error, mock_success]
        
        holders = client.fetch_holders("market_123")
        
        self.assertIsNotNone(holders)
        self.assertEqual(len(holders), 40)
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    def test_fetch_holders_fails_after_max_retries(self, mock_sleep, mock_get):
        client = HoldersClient()
        
        # All three calls fail
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        holders = client.fetch_holders("market_123")
        
        self.assertIsNone(holders)
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('requests.get')
    def test_fetch_holders_unexpected_format(self, mock_get):
        client = HoldersClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"not": "a list"}
        mock_get.return_value = mock_response
        
        holders = client.fetch_holders("market_123")
        self.assertIsNone(holders)

class TestPnLClientRetry(unittest.TestCase):
    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    def test_fetch_pnl_rate_limit(self, mock_sleep, mock_get):
        from holders_client import PnLClient
        client = PnLClient()
        
        # Mock 429, then success
        mock_429 = MagicMock()
        mock_429.status_code = 429
        
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = [{"p": 100.0}]
        
        mock_get.side_effect = [mock_429, mock_success]
        
        pnl = client.fetch_user_pnl("0x1")
        self.assertEqual(pnl, 100.0)
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    def test_fetch_pnl_timeout_retry(self, mock_sleep, mock_get):
        from holders_client import PnLClient
        client = PnLClient()
        
        # Mock timeout, then success
        mock_get.side_effect = [requests.exceptions.Timeout("Timeout"), MagicMock(status_code=200, json=lambda: [{"p": 50.0}])]
        
        pnl = client.fetch_user_pnl("0x1")
        self.assertEqual(pnl, 50.0)
        self.assertEqual(mock_get.call_count, 2)

    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    def test_fetch_pnl_unexpected_exception(self, mock_sleep, mock_get):
        from holders_client import PnLClient
        client = PnLClient()
        
        mock_get.side_effect = ValueError("Something very wrong")
        
        pnl = client.fetch_user_pnl("0x1")
        self.assertIsNone(pnl)

if __name__ == '__main__':
    unittest.main()
