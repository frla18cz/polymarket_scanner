import unittest

from runtime_paths import repo_root


REPO_ROOT = repo_root()
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "custom-data" / "index.html"
STATIC_INDEX = REPO_ROOT / "static" / "custom-data" / "index.html"


class TestCustomDataContract(unittest.TestCase):
    def test_static_and_frontend_deploy_custom_data_are_identical(self):
        self.assertTrue(FRONTEND_DEPLOY.exists(), f"Missing {FRONTEND_DEPLOY}")
        self.assertTrue(STATIC_INDEX.exists(), f"Missing {STATIC_INDEX}")
        self.assertEqual(
            FRONTEND_DEPLOY.read_bytes(),
            STATIC_INDEX.read_bytes(),
            "frontend_deploy/custom-data/index.html and static/custom-data/index.html must stay identical",
        )

    def test_custom_data_page_contains_expected_content(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        required_tokens = [
            "PolyLab | Custom Polymarket Data for Research Teams",
            "Custom Polymarket data for research teams",
            "Request Custom Data",
            "Open APP",
            "What teams can get",
            "Delivery models",
            "Who it is for",
            "Custom Data FAQ",
            'data-faq-source="customData.page.faq"',
            "mailto:hello@polylab.app?subject=Custom%20Data%20Inquiry",
            "/assets/polylab-info-content.js",
            "/assets/polylab-marketing.js",
        ]

        for token in required_tokens:
            self.assertIn(token, html, f"Missing custom-data token: {token}")

        self.assertIn('href="/docs"', html)
        self.assertIn('"@type":"Organization"', html)
        self.assertIn('"@type":"Service"', html)
        self.assertIn('"@type":"FAQPage"', html)


if __name__ == "__main__":
    unittest.main()
