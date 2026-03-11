import unittest
from runtime_paths import repo_root

class TestSEOMeta(unittest.TestCase):
    def test_meta_tags_present(self):
        """Verify that essential SEO and Social meta tags are present in index.html."""
        index_path = repo_root() / 'static' / 'index.html'
        self.assertTrue(index_path.exists())
        
        with open(index_path, 'r') as f:
            content = f.read()
        
        # Check for essential tags
        self.assertIn('<title>PolyLab | Independent analyzer for Polymarket</title>', content)
        self.assertIn('<meta property="og:title"', content)
        self.assertIn('<meta property="og:description"', content)
        self.assertIn('<meta property="og:image"', content)
        self.assertIn('<meta name="description"', content)
        self.assertIn('<meta name="twitter:card"', content)
        self.assertIn('<title>PolyLab | Independent analyzer for Polymarket</title>', content)
        self.assertIn('content="https://www.polylab.app"', content)
        self.assertIn('content="https://www.polylab.app"', content)
        self.assertIn('<link rel="canonical" href="https://www.polylab.app">', content)
        self.assertNotIn('noindex,follow', content)

if __name__ == "__main__":
    unittest.main()
