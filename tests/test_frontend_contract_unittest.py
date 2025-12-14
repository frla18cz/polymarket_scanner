import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "index.html"
STATIC_INDEX = REPO_ROOT / "static" / "index.html"


class TestFrontendContract(unittest.TestCase):
    def test_static_and_frontend_deploy_are_identical(self):
        self.assertTrue(FRONTEND_DEPLOY.exists(), f"Missing {FRONTEND_DEPLOY}")
        self.assertTrue(STATIC_INDEX.exists(), f"Missing {STATIC_INDEX}")
        self.assertEqual(
            FRONTEND_DEPLOY.read_bytes(),
            STATIC_INDEX.read_bytes(),
            "frontend_deploy/index.html and static/index.html must stay identical",
        )

    def test_required_filters_exist(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        match = re.search(r"const\s+filters\s*=\s*ref\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;", html)
        self.assertIsNotNone(match, "Could not find `const filters = ref({ ... });` in frontend HTML")

        filters_obj = match.group(1)
        required_keys = [
            "includedTags",
            "excludedTags",
            "min_volume",
            "min_liquidity",
            "min_price",
            "max_price",
            "max_spread",
            "min_apr_percent",
            "max_hours_to_expire",
            "expiry_index",
            "include_expired",
            "search",
            "sort_by",
            "sort_dir",
        ]
        for key in required_keys:
            self.assertRegex(filters_obj, rf"\b{re.escape(key)}\s*:", f"Missing filter key: {key}")

    def test_markets_request_contains_required_query_params(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        required_snippets = [
            'params.append("min_volume"',
            'params.append("min_liquidity"',
            'params.append("min_price"',
            'params.append("max_price"',
            'params.append("max_spread"',
            'params.append("include_expired"',
            'params.append("sort_by"',
            'params.append("sort_dir"',
            'params.append("included_tags"',
            'params.append("excluded_tags"',
            'params.append("max_hours_to_expire"',
            'params.append("limit"',
            'params.append("offset"',
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, html, f"Missing required request param mapping: {snippet}")

    def test_market_details_labels_present_on_page(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        for label in ["Market Details", "Implied odds", "APR (Win)", "Liquidity", "Volume", "Dates", "Market ID"]:
            pattern = re.escape(label).replace(r"\ ", r"\s+")
            self.assertRegex(html, pattern, f"Missing expected details label: {label}")

    def test_sidebar_sections_present(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        for label in [
            "Search Markets",
            "Include Categories",
            "Exclude Categories",
            "Expires Within",
            "Outcome Price Range (Probability)",
            "Max Spread",
            "Min APR (Win)",
            "Min Volume",
            "Min Liquidity",
            "Compact Rows",
        ]:
            pattern = re.escape(label).replace(r"\ ", r"\s+")
            self.assertRegex(html, pattern, f"Missing expected sidebar label: {label}")

    def test_expiry_preset_buttons_exist(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        for token in [
            "applyExpiryPreset('24h')",
            "applyExpiryPreset('7d')",
            "applyExpiryPreset('30d')",
            "applyExpiryPreset('end')",
            "applyExpiryPreset('any')",
        ]:
            self.assertIn(token, html, f"Missing expected expiry preset handler: {token}")

    def test_presets_exist(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        for preset_id in ["safe_haven", "yolo", "buffett", "sniper"]:
            self.assertIn(f"id: '{preset_id}'", html, f"Missing preset id: {preset_id}")

    def test_table_headers_and_sorts_exist(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        required = [
            "text-center\">Icon</div>",
            "setSort('question')\">Market",
            "setSort('price')\">Price",
            "setSort('spread')\">Spread",
            "setSort('apr')",
            "setSort('volume_usd')\">Volume",
            "setSort('liquidity_usd')\">Liq",
            "setSort('end_date')\">Expires",
        ]
        for token in required:
            self.assertIn(token, html, f"Missing expected table header/sort token: {token}")
