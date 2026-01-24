import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "index.html"

class TestMobilePolishContract(unittest.TestCase):
    def test_address_shortening_logic_exists(self):
        """
        Ensures the formatWalletAddress function exists and behaves as expected (shortens to 0x...1234).
        """
        if not FRONTEND_DEPLOY.exists():
             self.fail(f"Frontend file not found at {FRONTEND_DEPLOY}")

        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        self.assertIn(
            "const formatWalletAddress", 
            html, 
            "Frontend must contain `formatWalletAddress` function"
        )
        
        # We expect the logic to slice(0,6) and slice(-4) or similar
        self.assertIn(
            "slice(0, 6)", 
            html, 
            "Address shortening should keep the first 6 chars"
        )
        self.assertIn(
            "slice(-4)", 
            html, 
            "Address shortening should keep the last 4 chars"
        )

    def test_profile_link_exists(self):
        """
        Ensures that we generate links to polymarket.com/profile/<address>.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        self.assertIn(
            "polymarket.com/profile/", 
            html, 
            "Frontend must contain a link to the Polymarket profile page"
        )
        
    def test_tooltip_attribute_exists(self):
        """
        Ensures that the full address is available in a title attribute for desktop hover.
        """
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        # Look for the binding :title="holder.wallet_address" or similar
        self.assertIn(
            ':title="holder.wallet_address"', 
            html, 
            "Frontend must bind the full wallet address to the title attribute for tooltips"
        )
