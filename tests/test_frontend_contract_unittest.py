import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "app" / "index.html"
STATIC_INDEX = REPO_ROOT / "static" / "app" / "index.html"


class TestFrontendContract(unittest.TestCase):
    def test_static_and_frontend_deploy_are_identical(self):
        self.assertTrue(FRONTEND_DEPLOY.exists(), f"Missing {FRONTEND_DEPLOY}")
        self.assertTrue(STATIC_INDEX.exists(), f"Missing {STATIC_INDEX}")
        self.assertEqual(
            FRONTEND_DEPLOY.read_bytes(),
            STATIC_INDEX.read_bytes(),
            "frontend_deploy/app/index.html and static/app/index.html must stay identical",
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
            "min_hours_to_expire",
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
            'params.append("min_hours_to_expire"',
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
            "Not Sooner Than",
            "Price Range",
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
            "applyExpiryPreset('end_this')",
            "applyExpiryPreset('end')",
            "applyExpiryPreset('any')",
        ]:
            self.assertIn(token, html, f"Missing expected expiry preset handler: {token}")

    def test_presets_exist(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        for preset_id in ["smart_money_edge", "safe_haven", "yolo", "buffett", "sniper"]:
            self.assertIn(f"id: '{preset_id}'", html, f"Missing preset id: {preset_id}")

    def test_safe_haven_and_smart_money_edge_preset_contract(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        self.assertIn("label: 'Smart Money Edge'", html)
        self.assertIn("filters.value.min_profitable = 15;", html)
        self.assertIn("filters.value.min_losing_opposite = 15;", html)
        self.assertIn("filters.value.max_spread = 0.05;", html)
        self.assertIn("filters.value.min_liquidity = 1000;", html)
        self.assertIn("filters.value.sort_by = 'volume_usd';", html)
        self.assertIn("filters.value.sort_dir = 'desc';", html)

        self.assertIn("label: 'Safe Haven (>90%)'", html)
        self.assertIn("filters.value.min_price = 0.90;", html)
        self.assertIn("filters.value.max_price = 1.00;", html)
        self.assertIn("filters.value.max_spread = 0.02;", html)

    def test_table_headers_and_sorts_exist(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        required = [
            "text-center\">Icon</div>",
            "setSort('question')\">Market",
            "setSort('price')\">Price",
            "setSort('spread')",
            "Spread <i class=",
            "setSort('apr')",
            "setSort('volume_usd')\">Volume",
            "setSort('liquidity_usd')\">Liq",
            "setSort('end_date')\">Expires",
        ]
        for token in required:
            self.assertIn(token, html, f"Missing expected table header/sort token: {token}")

    def test_app_uses_shared_info_content_and_app_redirect(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        self.assertIn('/assets/polylab-info-content.js', html)
        self.assertIn("const infoContent = window.POLYLAB_INFO_CONTENT || {}", html)
        self.assertIn("redirectTo: window.location.origin + '/app'", html)

    def test_app_auth_copy_is_free_tier_consistent(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        self.assertIn("PolyLab Account", html)
        self.assertIn("Sign in to use advanced presets. PolyLab is currently free during early access.", html)
        self.assertIn(">Signed in<", html)
        self.assertNotIn("PolyLab Pro", html)
        self.assertNotIn("premium filters & presets", html)
        self.assertNotIn(">PRO<", html)

    def test_app_has_activation_tracking_contract_tokens(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")
        for token in [
            "app_first_markets_loaded",
            "app_first_filter_interaction",
            "app_market_outbound_click",
            "app_smart_money_view_opened",
            "auth_password_started",
            "auth_password_failed",
            '<link rel="canonical" href="https://www.polylab.app/app">',
            '<meta name="robots" content="noindex,follow">',
        ]:
            self.assertIn(token, html, f"Missing app readiness token: {token}")
