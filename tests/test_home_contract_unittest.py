import unittest

from runtime_paths import repo_root


REPO_ROOT = repo_root()
FRONTEND_DEPLOY = REPO_ROOT / "frontend_deploy" / "index.html"
STATIC_INDEX = REPO_ROOT / "static" / "index.html"


class TestHomeContract(unittest.TestCase):
    def test_static_and_frontend_deploy_home_are_identical(self):
        self.assertTrue(FRONTEND_DEPLOY.exists(), f"Missing {FRONTEND_DEPLOY}")
        self.assertTrue(STATIC_INDEX.exists(), f"Missing {STATIC_INDEX}")
        self.assertEqual(
            FRONTEND_DEPLOY.read_bytes(),
            STATIC_INDEX.read_bytes(),
            "frontend_deploy/index.html and static/index.html must stay identical",
        )

    def test_homepage_contains_expected_root_marketing_content(self):
        html = FRONTEND_DEPLOY.read_text("utf-8", errors="replace")

        required_tokens = [
            "PolyLab",
            "Follow the smart money on Polymarket",
            "Open APP",
            "See live signals",
            "8 trading playbooks",
            "Currently free during early access.",
            "Currently free",
            "No wallet required",
            "Hourly snapshots",
            "Independent tool",
            "Currently free during early access.",
            "Paid plans may be introduced later",
            "Need custom Polymarket data for a team?",
            "Explore Custom Data",
            "Independent analysis layer for Polymarket",
            "data-faq-list",
            'data-info-trigger="terms"',
            'data-info-trigger="privacy"',
            'data-contact-link',
        ]

        for token in required_tokens:
            self.assertIn(token, html, f"Missing homepage token: {token}")

        self.assertIn('content="https://www.polylab.app"', html)
        self.assertIn('href="/docs"', html)
        self.assertIn('href="/custom-data"', html)
        self.assertIn('"@type":"Organization"', html)
        self.assertIn('"@type":"SoftwareApplication"', html)
        self.assertIn('"@type":"FAQPage"', html)
        self.assertIn("Smart Money Edge", html)
        self.assertNotIn("Free vs Pro", html)
        self.assertNotIn("unlock Pro features later", html)


if __name__ == "__main__":
    unittest.main()
