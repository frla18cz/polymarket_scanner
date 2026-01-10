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
        
        # Mock sorted response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"address": "0x1", "positionSize": 100},
            {"address": "0x2", "positionSize": 50},
            {"address": "0x3", "positionSize": 10}
        ]
        mock_get.return_value = mock_response
        
        holders = client.fetch_holders("market_123", limit=3)
        
        self.assertEqual(len(holders), 3)
        self.assertEqual(holders[0]['address'], "0x1")
        
    @patch('requests.get')
    def test_fetch_holders_unsorted_warning(self, mock_get):
        from holders_client import HoldersClient
        client = HoldersClient()
        
        # Mock UNsorted response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"address": "0x1", "positionSize": 10},
            {"address": "0x2", "positionSize": 100}
        ]
        mock_get.return_value = mock_response
        
        # Use logs capture or just verify it returns the data anyway
        with self.assertLogs('polylab.holders', level='WARNING') as cm:
            holders = client.fetch_holders("market_unsorted")
            self.assertEqual(len(holders), 2)
            self.assertTrue(any("unsorted" in m for m in cm.output))

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
