import unittest
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "index.html"


class TestSmartMoneyUiLabels(unittest.TestCase):
    def test_smart_money_labels_and_counts(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        self.assertNotIn("Smart (P)", html, "Legacy 'Smart (P)' label should be removed")
        self.assertNotIn("Dumb (L)", html, "Legacy 'Dumb (L)' label should be removed")

        self.assertRegex(html, r"Yes\s+side", "Missing 'Yes side' label")
        self.assertRegex(html, r"No\s+side", "Missing 'No side' label")

        self.assertRegex(html, r"yes_profitable_count", "Missing YES profitable count in template")
        self.assertRegex(html, r"no_profitable_count", "Missing NO profitable count in template")


if __name__ == "__main__":
    unittest.main()
