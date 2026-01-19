import unittest
from unittest.mock import patch, MagicMock
import requests
from holders_client import HoldersClient

class TestHoldersValidation(unittest.TestCase):
    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    def test_fetch_holders_limit_is_1000(self, mock_sleep, mock_get):
        client = HoldersClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        client.fetch_holders("market_123")
        
        # Verify limit=1000 is passed to the API
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['limit'], 1000)

    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    def test_fetch_holders_validation_success(self, mock_sleep, mock_get):
        client = HoldersClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create 20 holders for outcome 0 and 20 for outcome 1
        holders_data = []
        for i in range(20):
            holders_data.append({"proxyWallet": f"0x0_{i}", "amount": 10, "outcomeIndex": 0})
            holders_data.append({"proxyWallet": f"0x1_{i}", "amount": 10, "outcomeIndex": 1})
            
        mock_response.json.return_value = [{"holders": holders_data}]
        mock_get.return_value = mock_response
        
        result = client.fetch_holders("market_123")
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 40)

    @patch('requests.get')
    @patch('time.sleep', return_value=None)
    def test_fetch_holders_allows_low_counts(self, mock_sleep, mock_get):
        client = HoldersClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Insufficient data (only 1 holder)
        mock_response.json.return_value = [{"holders": [{"proxyWallet": "0x1", "amount": 10, "outcomeIndex": 0}]}]
        mock_get.return_value = mock_response
        
        result = client.fetch_holders("market_123")
        
        self.assertEqual(mock_get.call_count, 1)
        self.assertFalse(mock_sleep.called)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)

if __name__ == '__main__':
    unittest.main()
