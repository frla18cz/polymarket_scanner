import unittest
from pathlib import Path

from runtime_paths import repo_root


REPO_ROOT = repo_root()
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "docs" / "index.html"
STATIC_INDEX = REPO_ROOT / "static" / "docs" / "index.html"


class TestDocsContract(unittest.TestCase):
    def test_static_and_frontend_deploy_docs_are_identical(self):
        self.assertTrue(FRONTEND_DEPLOY.exists(), f"Missing {FRONTEND_DEPLOY}")
        self.assertTrue(STATIC_INDEX.exists(), f"Missing {STATIC_INDEX}")
        self.assertEqual(
            FRONTEND_DEPLOY.read_bytes(),
            STATIC_INDEX.read_bytes(),
            "frontend_deploy/docs/index.html and static/docs/index.html must stay identical",
        )

    def test_docs_home_uses_classic_docs_navigation_and_status(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        required_tokens = [
            "PolyLab Docs | Documentation",
            "Documentation",
            "Implementation-first docs.",
            "Current implementation docs.",
            "Start Here",
            "Using the Scanner",
            "Understanding the Data",
            "Data Sources",
            "Pipeline",
            "Reference",
            "Appendix",
            'href="/docs/getting-started"',
            'href="/docs/how-polylab-works"',
            'href="/docs/workflows"',
            'href="/docs/scanner/filters-and-sorting"',
            'href="/docs/scanner/market-details-and-holders"',
            'href="/docs/metrics/core-metrics"',
            'href="/docs/methodology/apr"',
            'href="/docs/methodology/smart-money"',
            'href="/docs/data/freshness-and-limitations"',
            'href="/docs/sources/markets-and-events"',
            'href="/docs/sources/holders-and-wallet-pnl"',
            'href="/docs/pipeline/refresh-storage-and-snapshots"',
            'href="/docs/reference/upstream-field-map"',
            'href="/docs/reference/scanner-query-contract"',
            'href="/docs/reference/public-api-contract"',
            'href="/docs/faq"',
            'href="/docs/appendix/access-model"',
            'href="/docs/appendix/storage-and-runtime"',
            'href="/app"',
            'href="/custom-data"',
        ]

        for token in required_tokens:
            self.assertIn(token, html, f"Missing docs token: {token}")

        self.assertIn('content="https://www.polylab.app/docs"', html)
        self.assertIn('<link rel="canonical" href="https://www.polylab.app/docs">', html)
        self.assertIn('"@type":"TechArticle"', html)
        self.assertIn('"@type":"BreadcrumbList"', html)
        self.assertIn(".info-modal[hidden]", html)
        self.assertIn(".info-modal-item", html)
        self.assertIn("docs-sidebar", html)
        self.assertIn("docs-toc", html)
        self.assertIn('<section class="docs-home-banner"', html)
        self.assertIn('<p class="docs-sidebar-note">Current implementation docs.', html)
        self.assertNotIn('noindex,follow', html)
        self.assertNotIn("docs_hero_primary", html)
        self.assertNotIn("docs-sidebar-link-status", html)
        self.assertNotIn("docs-status-badge", html)

    def test_docs_article_pages_use_compact_shared_notice_without_home_banner(self):
        article_page = REPO_ROOT / "frontend_deploy" / "docs" / "methodology" / "apr" / "index.html"
        self.assertTrue(article_page.exists(), f"Missing {article_page}")

        html = article_page.read_text("utf-8", errors="replace")

        self.assertIn("Current implementation docs.", html)
        self.assertNotIn("Implementation-first docs.", html)
        self.assertNotIn("Documentation is in progress.", html)
        self.assertNotIn('<section class="docs-home-banner"', html)
        self.assertNotIn("docs-sidebar-link-status", html)
        self.assertNotIn("docs-status-badge", html)

    def test_docs_home_and_expected_generated_pages_exist(self):
        expected_pages = [
            FRONTEND_DEPLOY,
            REPO_ROOT / "frontend_deploy" / "docs" / "getting-started" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "how-polylab-works" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "workflows" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "scanner" / "filters-and-sorting" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "scanner" / "market-details-and-holders" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "metrics" / "core-metrics" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "methodology" / "apr" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "methodology" / "smart-money" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "data" / "freshness-and-limitations" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "sources" / "markets-and-events" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "sources" / "holders-and-wallet-pnl" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "pipeline" / "refresh-storage-and-snapshots" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "reference" / "upstream-field-map" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "reference" / "scanner-query-contract" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "reference" / "public-api-contract" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "faq" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "appendix" / "access-model" / "index.html",
            REPO_ROOT / "frontend_deploy" / "docs" / "appendix" / "storage-and-runtime" / "index.html",
        ]

        for page in expected_pages:
            static_page = Path(str(page).replace("/frontend_deploy/", "/static/"))
            self.assertTrue(page.exists(), f"Missing generated docs page: {page}")
            self.assertTrue(static_page.exists(), f"Missing mirrored docs page: {static_page}")
            self.assertEqual(page.read_bytes(), static_page.read_bytes(), f"Mirrored docs page differs: {page}")


if __name__ == "__main__":
    unittest.main()
