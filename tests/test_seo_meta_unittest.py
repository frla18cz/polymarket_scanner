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
        self.assertIn('<meta property="og:title"', content)
        self.assertIn('<meta property="og:description"', content)
        self.assertIn('<meta property="og:image"', content)
        self.assertIn('<meta name="description"', content)
        self.assertIn('<meta name="twitter:card"', content)

if __name__ == "__main__":
    unittest.main()
