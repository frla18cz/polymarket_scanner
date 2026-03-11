import unittest

from runtime_paths import repo_root


class TestLandingAssets(unittest.TestCase):
    def test_landing_media_assets_exist(self):
        repo = repo_root()
        asset_roots = [
            repo / "static" / "assets",
            repo / "frontend_deploy" / "assets",
        ]

        for asset_root in asset_roots:
            expected = [
                asset_root / "landing-loop.webm",
                asset_root / "landing-loop.mp4",
                asset_root / "landing-poster.png",
                asset_root / "landing-scanner-view.png",
                asset_root / "landing-smart-money-view.png",
                asset_root / "landing-yield-view.png",
                asset_root / "landing-og.png",
                asset_root / "polylab-info-content.js",
                asset_root / "polylab-marketing.js",
            ]

            for asset_path in expected:
                self.assertTrue(asset_path.exists(), f"Missing landing asset: {asset_path}")

    def test_landing_markup_uses_lazy_loaded_proof_media_and_motion_guard(self):
        landing_path = repo_root() / "frontend_deploy" / "landing" / "index.html"
        content = landing_path.read_text("utf-8", errors="replace")

        self.assertIn('loading="lazy"', content)
        self.assertIn('decoding="async"', content)
        self.assertIn('prefers-reduced-motion: reduce', content)
        self.assertIn('max-width: 767px', content)


if __name__ == "__main__":
    unittest.main()
