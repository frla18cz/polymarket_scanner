import json
import unittest

from runtime_paths import repo_root


class TestVercelRouting(unittest.TestCase):
    def test_vercel_rewrites_cover_app_landing_and_custom_data(self):
        config_path = repo_root() / "vercel.json"
        self.assertTrue(config_path.exists())

        config = json.loads(config_path.read_text("utf-8"))
        rewrites = config.get("rewrites", [])

        pairs = {(item.get("source"), item.get("destination")) for item in rewrites}

        expected_pairs = {
            ("/assets/:path*", "/frontend_deploy/assets/:path*"),
            ("/robots.txt", "/frontend_deploy/robots.txt"),
            ("/sitemap.xml", "/frontend_deploy/sitemap.xml"),
            ("/api/:path*", "https://api.polylab.app/api/:path*"),
            ("/app", "/frontend_deploy/app/index.html"),
            ("/app/:path*", "/frontend_deploy/app/index.html"),
            ("/docs", "/frontend_deploy/docs/index.html"),
            ("/docs/:path*", "/frontend_deploy/docs/:path*/index.html"),
            ("/landing", "/frontend_deploy/landing/index.html"),
            ("/landing/:path*", "/frontend_deploy/landing/index.html"),
            ("/custom-data", "/frontend_deploy/custom-data/index.html"),
            ("/custom-data/:path*", "/frontend_deploy/custom-data/index.html"),
            ("/", "/frontend_deploy/index.html"),
        }

        for pair in expected_pairs:
            self.assertIn(pair, pairs, f"Missing Vercel rewrite: {pair}")


if __name__ == "__main__":
    unittest.main()
