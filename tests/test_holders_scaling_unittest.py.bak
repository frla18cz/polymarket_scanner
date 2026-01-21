import unittest
from unittest.mock import patch, MagicMock
from holders_client import GoldskyClient

class TestHoldersScaling(unittest.TestCase):
    def setUp(self):
        self.client = GoldskyClient()

    @patch('requests.post')
    def test_fetch_holders_subgraph_scaling(self, mock_post):
        # Mock Goldsky response with a raw balance of 1,000,000 (representing 1 share if scaled by 1e6)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "userBalances": [
                    {
                        "user": "0x123",
                        "balance": "1000000"  # Raw value from subgraph
                    }
                ]
            }
        }
        mock_post.return_value = mock_response

        # Call the method
        holders = self.client.fetch_holders_subgraph("condition_123")

        # Assertions
        self.assertIsNotNone(holders)
        # We expect 2 because the client queries for outcome 0 and 1, and our mock returns data for both.
        self.assertEqual(len(holders), 2)
        
        holder = holders[0]
        # We expect the positionSize to be scaled down by 1e6.
        # So 1,000,000 raw units should be 1.0 share.
        # The current implementation (buggy) returns 1,000,000.
        # This assertion should FAIL until we fix the code.
        self.assertEqual(holder['positionSize'], 1.0, f"Expected 1.0 but got {holder['positionSize']}")

if __name__ == '__main__':
    unittest.main()