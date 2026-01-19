import unittest
from unittest.mock import patch, MagicMock
import requests
# Will import HoldersClient after creation
# from holders_client import HoldersClient 

class TestHoldersClient(unittest.TestCase):
    def setUp(self):
        # We'll need to import this inside tests or use a conditional import 
        # because the file doesn't exist yet for the first run
        pass

    @patch('requests.get')
    def test_fetch_holders_success(self, mock_get):
        from holders_client import HoldersClient
        client = HoldersClient()
        
        # Mock token-based response with enough holders for validation
        holders_0 = [{"proxyWallet": f"0x0_{i}", "amount": 100, "outcomeIndex": 0} for i in range(20)]
        holders_1 = [{"proxyWallet": f"0x1_{i}", "amount": 50, "outcomeIndex": 1} for i in range(20)]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"token": "tok1", "holders": holders_0},
            {"token": "tok2", "holders": holders_1}
        ]
        mock_get.return_value = mock_response
        
        holders = client.fetch_holders("market_123")
        
        self.assertIsNotNone(holders)
        self.assertEqual(len(holders), 20)
        
    @patch('requests.get')
    def test_fetch_holders_unsorted_warning(self, mock_get):
        from holders_client import HoldersClient
        client = HoldersClient()
        
        # Mock enough holders but unsorted
        holders_0 = [{"proxyWallet": f"0x0_{i}", "amount": i, "outcomeIndex": 0} for i in range(20)]
        holders_1 = [{"proxyWallet": f"0x1_{i}", "amount": i, "outcomeIndex": 1} for i in range(20)]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"token": "t1", "holders": holders_0 + holders_1}
        ]
        mock_get.return_value = mock_response
        
        holders = client.fetch_holders("market_unsorted")
        self.assertIsNotNone(holders)
        self.assertEqual(len(holders), 20)
        # Should be sorted DESC by amount (which we mapped to positionSize)
        self.assertEqual(holders[0]['positionSize'], 19)

    @patch('requests.get')
    def test_fetch_pnl_success(self, mock_get):
        from holders_client import PnLClient
        client = PnLClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        # PnL API structure assumption based on spec: "Use the last data point p"
        # Example: [{"t": ..., "p": 123.45}, ...]
        mock_response.json.return_value = [
            {"t": 100, "p": 10.0},
            {"t": 101, "p": 15.5}
        ]
        mock_get.return_value = mock_response
        
        pnl = client.fetch_user_pnl("0xABC")
        self.assertEqual(pnl, 15.5)

if __name__ == '__main__':
    unittest.main()
