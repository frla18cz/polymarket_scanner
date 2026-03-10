import unittest

from runtime_paths import repo_root


class TestCustomDataMeta(unittest.TestCase):
    def test_custom_data_meta_tags_present(self):
        custom_data_path = repo_root() / "static" / "custom-data" / "index.html"
        self.assertTrue(custom_data_path.exists())

        content = custom_data_path.read_text("utf-8", errors="replace")

        self.assertIn("<title>PolyLab | Custom Polymarket Data for Research Teams</title>", content)
        self.assertIn('content="https://www.polylab.app/custom-data"', content)
        self.assertIn('<meta name="description"', content)
        self.assertIn('<meta property="og:title"', content)
        self.assertIn('<meta property="og:description"', content)
        self.assertIn('<meta name="twitter:card"', content)
        self.assertIn('<link rel="canonical" href="https://www.polylab.app/custom-data">', content)
        self.assertNotIn('noindex,follow', content)


if __name__ == "__main__":
    unittest.main()
