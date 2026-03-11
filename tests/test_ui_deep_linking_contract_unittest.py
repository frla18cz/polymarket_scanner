import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "app" / "index.html"

class TestDeepLinkingContract(unittest.TestCase):
    def test_url_update_logic_exists(self):
        """
        Ensures that the frontend has logic to update the URL when a market is selected/deselected.
        We look for specific function calls or patterns that indicate this behavior.
        """
        if not FRONTEND_DEPLOY.exists():
             self.fail(f"Frontend file not found at {FRONTEND_DEPLOY}")

        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        # We expect a watch on 'selectedMarket' or a function that handles opening/closing
        # that calls history.pushState or history.replaceState, or modifies window.location.
        
        # Check for logic that adds the query param
        self.assertRegex(
            html, 
            r"['\"]market_id['\"]", 
            "Frontend must contain logic to set 'market_id' query parameter"
        )
        
        # Check for history API usage to update URL without reload
        self.assertTrue(
            "history.pushState" in html or "history.replaceState" in html,
            "Frontend must use history API (pushState/replaceState) to update URL"
        )

        # Check for URLSearchParams usage which is cleaner
        self.assertIn(
            "URLSearchParams", 
            html, 
            "Frontend should use URLSearchParams for query manipulation"
        )
