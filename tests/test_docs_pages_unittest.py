import unittest

from runtime_paths import repo_root


REPO_ROOT = repo_root()


class TestDocsPages(unittest.TestCase):
    def test_apr_methodology_page_is_detailed_and_formula_driven(self):
        apr_page = REPO_ROOT / "frontend_deploy" / "docs" / "methodology" / "apr" / "index.html"
        self.assertTrue(apr_page.exists())

        html = apr_page.read_text("utf-8", errors="replace")

        required_tokens = [
            "APR Methodology",
            "In Progress",
            "Documentation is in progress.",
            "((1.0 / price) - 1.0) * (365.0 / days)",
            "APR is only computed when price is greater than 0 and less than 1",
            "When APR is null",
            "Short-duration annualization can overstate weak setups",
        ]

        for token in required_tokens:
            self.assertIn(token, html, f"Missing APR methodology token: {token}")

    def test_smart_money_methodology_page_matches_current_count_logic(self):
        smart_money_page = REPO_ROOT / "frontend_deploy" / "docs" / "methodology" / "smart-money" / "index.html"
        self.assertTrue(smart_money_page.exists())

        html = smart_money_page.read_text("utf-8", errors="replace")

        required_tokens = [
            "Smart Money Methodology",
            "In Progress",
            "top 20 holders per outcome",
            "ws.total_pnl &gt; 0",
            "ws.total_pnl &lt; 0",
            "yes_profitable_count",
            "no_losing_count",
            "Known data anomalies",
            "system wallet",
            "Do not treat Smart Money counts as proof",
            "smart_money_win_rate</code> is not a current public filter",
        ]

        for token in required_tokens:
            self.assertIn(token, html, f"Missing Smart Money token: {token}")

    def test_freshness_page_describes_real_refresh_cadence(self):
        freshness_page = REPO_ROOT / "frontend_deploy" / "docs" / "data" / "freshness-and-limitations" / "index.html"
        self.assertTrue(freshness_page.exists())

        html = freshness_page.read_text("utf-8", errors="replace")

        required_tokens = [
            "Freshness and Limitations",
            "Documentation is in progress.",
            "Market snapshots refresh every hour",
            "Smart Money analysis refreshes every 6 hours",
            "Why numbers can differ from Polymarket",
            "hourly snapshots rather than tick-level live execution",
        ]

        for token in required_tokens:
            self.assertIn(token, html, f"Missing freshness token: {token}")

    def test_market_source_page_names_real_gamma_endpoints(self):
        source_page = REPO_ROOT / "frontend_deploy" / "docs" / "sources" / "markets-and-events" / "index.html"
        self.assertTrue(source_page.exists())

        html = source_page.read_text("utf-8", errors="replace")
        required_tokens = [
            "Markets and Events Source",
            "https://gamma-api.polymarket.com/markets",
            "https://gamma-api.polymarket.com/events",
            "enableOrderBook=false",
            '<table class="docs-table">',
        ]
        for token in required_tokens:
            self.assertIn(token, html, f"Missing market source token: {token}")

    def test_holders_source_page_documents_sampling_cap(self):
        source_page = REPO_ROOT / "frontend_deploy" / "docs" / "sources" / "holders-and-wallet-pnl" / "index.html"
        self.assertTrue(source_page.exists())

        html = source_page.read_text("utf-8", errors="replace")
        required_tokens = [
            "Holders and Wallet PnL Source",
            "https://data-api.polymarket.com/holders",
            "https://user-pnl-api.polymarket.com/user-pnl",
            "top 20 holders per outcome",
            "per_outcome_limit = min(limit, 20)",
        ]
        for token in required_tokens:
            self.assertIn(token, html, f"Missing holders source token: {token}")

    def test_field_map_reference_renders_table_and_exact_mappings(self):
        reference_page = REPO_ROOT / "frontend_deploy" / "docs" / "reference" / "upstream-field-map" / "index.html"
        self.assertTrue(reference_page.exists())

        html = reference_page.read_text("utf-8", errors="replace")
        required_tokens = [
            "Upstream to PolyLab Field Map",
            '<table class="docs-table">',
            "Gamma market",
            "market_id",
            "condition_id",
            "tag_label",
        ]
        for token in required_tokens:
            self.assertIn(token, html, f"Missing field map token: {token}")


if __name__ == "__main__":
    unittest.main()
