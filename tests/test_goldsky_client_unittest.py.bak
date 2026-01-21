import unittest
import os
import sys
import requests
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holders_client import GoldskyClient

class TestGoldskyClient(unittest.TestCase):

    def setUp(self):
        self.client = GoldskyClient()

    @patch('holders_client.requests.post')
    def test_fetch_holders_subgraph_success(self, mock_post):
        """Test successful fetching of holders from the subgraph."""
        # Mock successful API response for two calls (outcome 0 and 1)
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "data": {
                "userBalances": [
                    {"user": "0x123", "balance": "1000"},
                    {"user": "0x456", "balance": "2000"}
                ]
            }
        }
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "data": {
                "userBalances": [
                    {"user": "0x789", "balance": "3000"},
                    {"user": "0xabc", "balance": "4000"}
                ]
            }
        }
        mock_post.side_effect = [mock_response_1, mock_response_2]

        condition_id = "0x123abc"
        holders = self.client.fetch_holders_subgraph(condition_id, limit=20)

        self.assertIsNotNone(holders)
        self.assertEqual(len(holders), 4)
        # The list is sorted, so 0xabc should be first
        self.assertEqual(holders[0]["address"], "0xabc")
        self.assertEqual(holders[0]["positionSize"], 0.004)

        # Check that post was called twice
        self.assertEqual(mock_post.call_count, 2)

    @patch('holders_client.requests.post')
    def test_fetch_holders_subgraph_empty(self, mock_post):
        """Test handling of an empty response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"userBalances": []}}
        mock_post.return_value = mock_response

        condition_id = "0x456def"
        holders = self.client.fetch_holders_subgraph(condition_id, limit=20)

        self.assertEqual(holders, [])

    @patch('holders_client.requests.post')
    def test_fetch_holders_subgraph_caps_limit(self, mock_post):
        """Test that the client caps and returns at most 20 holders."""
        balances_0 = [{"user": f"0x0_{i}", "balance": str(1000 + i)} for i in range(15)]
        balances_1 = [{"user": f"0x1_{i}", "balance": str(2000 + i)} for i in range(15)]

        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {"data": {"userBalances": balances_0}}

        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {"data": {"userBalances": balances_1}}

        mock_post.side_effect = [mock_response_1, mock_response_2]

        holders = self.client.fetch_holders_subgraph("0xLimitCID", limit=50)

        self.assertEqual(len(holders), 20)
        args, kwargs = mock_post.call_args_list[0]
        self.assertEqual(kwargs["json"]["variables"]["first"], 20)

    @patch('holders_client.requests.post')
    def test_fetch_holders_subgraph_retry(self, mock_post):
        """Test that the client retries on transient errors."""
        # Setup mock responses: 
        # 1. First call fails (Timeout)
        # 2. Second call succeeds for outcome 0
        # 3. Third call succeeds for outcome 1
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": {"userBalances": [{"user": "0xRetry", "balance": "500"}]}}
        
        mock_post.side_effect = [
            requests.exceptions.Timeout("Slow connection"),
            mock_response_success,
            mock_response_success
        ]

        with patch('holders_client.time.sleep'): # Avoid waiting during tests
            holders = self.client.fetch_holders_subgraph("0xRetryCID", limit=10)

        self.assertIsNotNone(holders)
        self.assertEqual(len(holders), 2) # Outcome 0 and 1
        self.assertEqual(mock_post.call_count, 3)

    @patch('holders_client.requests.post')
    def test_fetch_holders_subgraph_api_error(self, mock_post):
        """Test handling of an API error (e.g., 500)."""
        mock_post.side_effect = requests.exceptions.RequestException("API is down")

        condition_id = "0x789ghi"
        holders = self.client.fetch_holders_subgraph(condition_id, limit=20)

        self.assertIsNone(holders)

if __name__ == '__main__':
    unittest.main()
