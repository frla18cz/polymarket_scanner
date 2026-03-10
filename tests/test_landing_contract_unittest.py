import unittest
from pathlib import Path

from runtime_paths import repo_root


REPO_ROOT = repo_root()
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "landing" / "index.html"
STATIC_INDEX = REPO_ROOT / "static" / "landing" / "index.html"


class TestLandingContract(unittest.TestCase):
    def test_static_and_frontend_deploy_landing_are_identical(self):
        self.assertTrue(FRONTEND_DEPLOY.exists(), f"Missing {FRONTEND_DEPLOY}")
        self.assertTrue(STATIC_INDEX.exists(), f"Missing {STATIC_INDEX}")
        self.assertEqual(
            FRONTEND_DEPLOY.read_bytes(),
            STATIC_INDEX.read_bytes(),
            "frontend_deploy/landing/index.html and static/landing/index.html must stay identical",
        )

    def test_required_sections_and_ctas_exist(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        required_tokens = [
            "Find better Polymarket trades in seconds",
            "Scan live markets by price, spread, APR, liquidity, and smart-money behavior",
            "Open APP",
            "See Live Demo",
            "PolyLab is currently free during early access.",
            "Currently free",
            "No wallet required",
            "Hourly snapshots",
            "Independent tool",
            "Yield + Filters",
            "16,000+ active markets tracked",
            "Independent analyzer for Polymarket",
            "Scan faster",
            "See smart money",
            "Focus on tradable setups",
            "How it works",
            "Currently free during early access.",
            "There is no paid subscription yet.",
            "Paid plans may be introduced later",
            "Need a private feed instead of the public app?",
            "Custom Data",
            "Stop browsing markets manually",
        ]

        for token in required_tokens:
            self.assertIn(token, html, f"Missing landing page token: {token}")

        self.assertNotIn("Open Scanner", html, "Landing page should use 'Open APP' instead of 'Open Scanner'")
        self.assertNotIn("Free vs Pro", html)
        self.assertNotIn("unlock Pro features later", html)

    def test_landing_uses_dedicated_assets(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        required_asset_refs = [
            "/assets/landing-loop.webm",
            "/assets/landing-loop.mp4",
            "/assets/landing-poster.png",
            "/assets/landing-scanner-view.png",
            "/assets/landing-smart-money-view.png",
            "/assets/landing-yield-view.png",
            "/assets/landing-og.png",
            "/assets/polylab-info-content.js",
            "/assets/polylab-marketing.js",
        ]

        for asset_ref in required_asset_refs:
            self.assertIn(asset_ref, html, f"Missing landing asset reference: {asset_ref}")

        self.assertIn('data-hero-gallery', html, "Hero gallery should be present")
        self.assertIn('data-hero-target="smart-money"', html, "Hero smart-money tab should be present")

    def test_landing_uses_shared_info_surface(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        self.assertIn('data-faq-list', html, "Landing page should render FAQ from shared info content")
        self.assertIn('data-info-trigger="terms"', html, "Landing page should expose shared Terms link")
        self.assertIn('data-info-trigger="privacy"', html, "Landing page should expose shared Privacy link")
        self.assertIn('data-contact-link', html, "Landing page should expose shared Contact link")
        self.assertIn('href="/docs"', html, "Landing page should link to the docs page")
        self.assertIn('href="/custom-data"', html, "Landing page should link to the custom-data page")
        self.assertIn('"@type":"Organization"', html)
        self.assertIn('"@type":"SoftwareApplication"', html)
        self.assertIn('"@type":"FAQPage"', html)


if __name__ == "__main__":
    unittest.main()
