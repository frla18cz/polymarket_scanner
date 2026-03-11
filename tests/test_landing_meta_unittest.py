import unittest

from runtime_paths import repo_root


class TestLandingMeta(unittest.TestCase):
    def test_landing_meta_tags_present(self):
        landing_path = repo_root() / "static" / "landing" / "index.html"
        self.assertTrue(landing_path.exists())

        content = landing_path.read_text("utf-8", errors="replace")

        self.assertIn("<title>PolyLab | Find Better Polymarket Trades Faster</title>", content)
        self.assertIn('<meta name="description"', content)
        self.assertIn('<meta property="og:title"', content)
        self.assertIn('<meta property="og:description"', content)
        self.assertIn('content="https://www.polylab.app/assets/landing-og.png"', content)
        self.assertIn('<meta name="twitter:card"', content)
        self.assertIn('<link rel="canonical" href="https://www.polylab.app/landing">', content)
        self.assertIn('<meta name="robots" content="noindex,follow">', content)


if __name__ == "__main__":
    unittest.main()
