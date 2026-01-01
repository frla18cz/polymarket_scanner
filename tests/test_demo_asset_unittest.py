import unittest
import os
from runtime_paths import repo_root

class TestDemoAsset(unittest.TestCase):
    def test_demo_gif_exists_and_valid(self):
        """Verify that the demo GIF asset exists and is a valid GIF."""
        demo_gif_path = repo_root() / 'static' / 'assets' / 'demo.gif'
        self.assertTrue(demo_gif_path.exists(), f"Demo GIF not found at {demo_gif_path}")
        
        # Check if it's a valid GIF by reading magic bytes
        with open(demo_gif_path, 'rb') as f:
            header = f.read(6)
        
        self.assertIn(header, [b'GIF87a', b'GIF89a'], f"File at {demo_gif_path} does not have a valid GIF header")
