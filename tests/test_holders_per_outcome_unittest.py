import unittest
from unittest.mock import patch, MagicMock
from holders_client import GoldskyClient, HoldersClient

class TestHoldersPerOutcome(unittest.TestCase):
    def setUp(self):
        self.goldsky = GoldskyClient()
        self.legacy = HoldersClient()

    @patch("requests.post")
    def test_goldsky_fetches_per_outcome(self, mock_post):
        """
        Verify that GoldskyClient returns up to limit * outcomes holders.
        If limit is 20, and we have 2 outcomes with 20 holders each, we expect 40 total.
        """
        limit = 20
        
        # Mock response generator
        def side_effect(*args, **kwargs):
            json_body = kwargs.get("json", {})
            variables = json_body.get("variables", {})
            outcome_index = variables.get("outcomeIndex")
            
            # Generate 20 holders for requested outcome
            holders = []
            for i in range(limit):
                holders.append({
                    "user": f"0xUser{outcome_index}_{i}",
                    "balance": "1000000" # 1.0 size
                })
                
            return MagicMock(
                status_code=200,
                json=lambda: {"data": {"userBalances": holders}}
            )

        mock_post.side_effect = side_effect

        results = self.goldsky.fetch_holders_subgraph("condition123", limit=limit)
        
        # Expect 40 results (20 for outcome 0, 20 for outcome 1)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 40)
        
        # Verify outcomes
        outcomes = [r["outcomeIndex"] for r in results]
        self.assertEqual(outcomes.count(0), 20)
        self.assertEqual(outcomes.count(1), 20)

    @patch("requests.get")
    def test_legacy_fetches_per_outcome(self, mock_get):
        """
        Verify that HoldersClient returns holders for both outcomes without capping global total at limit.
        Legacy API returns a list of tokens (outcomes).
        """
        limit = 20
        
        # Mock response: 2 tokens, each with 20 holders
        mock_data = []
        for i in range(2): # 2 outcomes
            holders = []
            for j in range(limit):
                holders.append({
                    "proxyWallet": f"0xUser{i}_{j}",
                    "amount": "1.0"
                })
            mock_data.append({"holders": holders})

        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_data
        )

        results = self.legacy.fetch_holders("market123", limit=limit)
        
        self.assertIsNotNone(results)
        # Expect 40 results (legacy client currently flattens them, but we want 40)
        self.assertEqual(len(results), 40)

if __name__ == "__main__":
    unittest.main()
