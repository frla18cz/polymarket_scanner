import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOME_FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "index.html"


class TestHomeSignalDeepLink(unittest.TestCase):
    def test_signal_modal_open_in_scanner_targets_selected_market_in_smart_view(self):
        html = HOME_FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        self.assertRegex(
            html,
            r"buildSignalScannerHref\s*\(",
            "Homepage should build the Smart Money signal CTA from the selected market.",
        )
        self.assertIn("market_id", html)
        self.assertRegex(
            html,
            r"searchParams\.set\(['\"]view['\"],\s*['\"]smart['\"]\)",
            "Homepage Smart Money signal CTA must force the Smart view.",
        )


if __name__ == "__main__":
    unittest.main()
