import unittest

from runtime_paths import repo_root


class TestSiteIndexingContract(unittest.TestCase):
    def test_robots_and_sitemap_exist_and_are_mirrored(self):
        repo = repo_root()
        frontend_robots = repo / "frontend_deploy" / "robots.txt"
        static_robots = repo / "static" / "robots.txt"
        frontend_sitemap = repo / "frontend_deploy" / "sitemap.xml"
        static_sitemap = repo / "static" / "sitemap.xml"

        for path in [frontend_robots, static_robots, frontend_sitemap, static_sitemap]:
            self.assertTrue(path.exists(), f"Missing indexing asset: {path}")

        self.assertEqual(frontend_robots.read_text("utf-8"), static_robots.read_text("utf-8"))
        self.assertEqual(frontend_sitemap.read_text("utf-8"), static_sitemap.read_text("utf-8"))

    def test_robots_and_sitemap_contents_match_indexing_policy(self):
        repo = repo_root()
        robots = (repo / "frontend_deploy" / "robots.txt").read_text("utf-8")
        sitemap = (repo / "frontend_deploy" / "sitemap.xml").read_text("utf-8")

        for token in [
            "User-agent: *",
            "Disallow: /app",
            "Disallow: /landing",
            "Sitemap: https://www.polylab.app/sitemap.xml",
        ]:
            self.assertIn(token, robots, f"Missing robots token: {token}")

        self.assertIn("<loc>https://www.polylab.app/</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/docs</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/docs/getting-started</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/docs/how-polylab-works</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/docs/methodology/apr</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/docs/sources/markets-and-events</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/docs/reference/public-api-contract</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/docs/faq</loc>", sitemap)
        self.assertIn("<loc>https://www.polylab.app/custom-data</loc>", sitemap)
        self.assertNotIn("/landing", sitemap)
        self.assertNotIn("<loc>https://www.polylab.app/app</loc>", sitemap)


if __name__ == "__main__":
    unittest.main()
