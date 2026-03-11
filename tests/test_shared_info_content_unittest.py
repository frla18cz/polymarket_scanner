import unittest

from runtime_paths import repo_root


class TestSharedInfoContent(unittest.TestCase):
    def test_shared_info_asset_exists_and_is_mirrored(self):
        repo = repo_root()
        frontend_asset = repo / "frontend_deploy" / "assets" / "polylab-info-content.js"
        static_asset = repo / "static" / "assets" / "polylab-info-content.js"
        frontend_helper = repo / "frontend_deploy" / "assets" / "polylab-marketing.js"
        static_helper = repo / "static" / "assets" / "polylab-marketing.js"

        self.assertTrue(frontend_asset.exists(), f"Missing {frontend_asset}")
        self.assertTrue(static_asset.exists(), f"Missing {static_asset}")
        self.assertTrue(frontend_helper.exists(), f"Missing {frontend_helper}")
        self.assertTrue(static_helper.exists(), f"Missing {static_helper}")
        self.assertEqual(frontend_asset.read_text("utf-8"), static_asset.read_text("utf-8"))
        self.assertEqual(frontend_helper.read_text("utf-8"), static_helper.read_text("utf-8"))

    def test_shared_info_asset_contains_canonical_sections(self):
        content = (repo_root() / "frontend_deploy" / "assets" / "polylab-info-content.js").read_text("utf-8")

        required_tokens = [
            "hello@polylab.app",
            "What is PolyLab?",
            "Do I need a wallet to use it?",
            "currently free for all users during early access",
            "There is no paid subscription yet",
            "What does Smart Money mean?",
            "Need custom Polymarket data for a team?",
            "Custom Polymarket data for research teams",
            "mailto:hello@polylab.app?subject=Custom%20Data%20Inquiry",
            "PolyLab is provided for informational and analytical purposes only.",
            "Data Collection: We do not collect personal information",
        ]

        for token in required_tokens:
            self.assertIn(token, content, f"Missing shared info token: {token}")


if __name__ == "__main__":
    unittest.main()
