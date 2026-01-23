import unittest
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "index.html"

class TestFrontendMetricRemoval(unittest.TestCase):
    def test_smart_money_win_rate_ui_removed(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        
        # Check for UI labels
        self.assertNotRegex(html, r"Smart Money Win Rate", "UI Label 'Smart Money Win Rate' should be removed")
        self.assertNotRegex(html, r"Smart Win", "UI Label 'Smart Win' should be removed")
        
        # Check for filter key
        match = re.search(r"const\s+filters\s*=\s*ref\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;", html)
        if match:
            filters_obj = match.group(1)
            self.assertNotRegex(filters_obj, r"min_smart_money_win_rate\s*:", "Filter key 'min_smart_money_win_rate' should be removed")
            
        # Check for sort call
        self.assertNotIn("setSort('smart_money_win_rate')", html, "Sort handler for smart_money_win_rate should be removed")
        
        # Check for API param mapping
        self.assertNotIn('params.append("min_smart_money_win_rate"', html, "API param mapping for min_smart_money_win_rate should be removed")
