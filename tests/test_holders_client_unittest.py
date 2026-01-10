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
        
        # Mock token-based response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "token": "tok1",
                "holders": [
                    {"proxyWallet": "0x1", "amount": 100},
                    {"proxyWallet": "0x2", "amount": 50}
                ]
            },
            {
                "token": "tok2",
                "holders": [
                    {"proxyWallet": "0x3", "amount": 10}
                ]
            }
        ]
        mock_get.return_value = mock_response
        
        holders = client.fetch_holders("market_123", limit=3)
        
        self.assertEqual(len(holders), 3)
        self.assertEqual(holders[0]['address'], "0x1")
        self.assertEqual(holders[0]['positionSize'], 100)
        
    @patch('requests.get')
    def test_fetch_holders_unsorted_warning(self, mock_get):
        from holders_client import HoldersClient
        client = HoldersClient()
        
        # Mock UNsorted response (after flattening)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "token": "t1",
                "holders": [
                    {"proxyWallet": "0x1", "amount": 10},
                    {"proxyWallet": "0x2", "amount": 100}
                ]
            }
        ]
        mock_get.return_value = mock_response
        
        # Note: HoldersClient now explicitly sorts the flattened list, 
        # so the "unsorted warning" check might not be needed or should check input.
        # But we check that it RETURNS them correctly sorted.
        holders = client.fetch_holders("market_unsorted")
        self.assertEqual(len(holders), 2)
        # Should be sorted DESC by client
        self.assertEqual(holders[0]['positionSize'], 100)
        self.assertEqual(holders[1]['positionSize'], 10)

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
