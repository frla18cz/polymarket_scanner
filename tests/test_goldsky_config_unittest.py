import unittest
import os
import sys
from unittest.mock import patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We anticipate the client will be in holders_client.py
from holders_client import GoldskyClient

class TestGoldskyConfig(unittest.TestCase):
    def test_default_url(self):
        """Test that the default URL is used when env var is not set."""
        # Ensure env var is not set
        with patch.dict(os.environ, {}, clear=True):
            client = GoldskyClient()
            expected_default = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn"
            self.assertEqual(client.url, expected_default)

    def test_env_var_override(self):
        """Test that the URL can be overridden by environment variable."""
        test_url = "https://api.goldsky.com/test-endpoint"
        with patch.dict(os.environ, {"GOLDSKY_SUBGRAPH_URL": test_url}):
            client = GoldskyClient()
            self.assertEqual(client.url, test_url)

if __name__ == '__main__':
    unittest.main()
