import os
import unittest

from fastapi import HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from starlette.requests import Request


class TestLandingRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SERVE_FRONTEND"] = "1"
        import main as app_main

        cls.app_main = app_main

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("SERVE_FRONTEND", None)

    def test_landing_route_is_registered(self):
        route_paths = {route.path for route in self.app_main.app.routes}
        self.assertIn("/landing", route_paths)
        self.assertIn("/app", route_paths)
        self.assertIn("/custom-data", route_paths)
        self.assertIn("/docs", route_paths)
        self.assertIn("/docs/{path:path}", route_paths)

    def test_frontend_landing_serves_dedicated_file(self):
        self.assertTrue(hasattr(self.app_main, "LANDING_INDEX_PATH"))
        self.assertTrue(hasattr(self.app_main, "frontend_landing"))

        response = self.app_main.frontend_landing()

        self.assertIsInstance(response, FileResponse)
        self.assertTrue(str(response.path).endswith("frontend_deploy/landing/index.html"))
        self.assertEqual(response.headers.get("cache-control"), "no-cache, no-store, must-revalidate")

    def test_frontend_root_serves_homepage_index(self):
        request = Request({"type": "http", "method": "GET", "path": "/", "query_string": b""})
        response = self.app_main.frontend_root(request)

        self.assertIsInstance(response, FileResponse)
        self.assertTrue(str(response.path).endswith("frontend_deploy/index.html"))

    def test_frontend_app_serves_scanner_index(self):
        response = self.app_main.frontend_app()

        self.assertIsInstance(response, FileResponse)
        self.assertTrue(str(response.path).endswith("frontend_deploy/app/index.html"))

    def test_frontend_custom_data_serves_dedicated_file(self):
        self.assertTrue(hasattr(self.app_main, "CUSTOM_DATA_INDEX_PATH"))
        self.assertTrue(hasattr(self.app_main, "frontend_custom_data"))

        response = self.app_main.frontend_custom_data()

        self.assertIsInstance(response, FileResponse)
        self.assertTrue(str(response.path).endswith("frontend_deploy/custom-data/index.html"))

    def test_frontend_docs_serves_dedicated_file(self):
        self.assertTrue(hasattr(self.app_main, "DOCS_INDEX_PATH"))
        self.assertTrue(hasattr(self.app_main, "frontend_docs"))

        response = self.app_main.frontend_docs()

        self.assertIsInstance(response, FileResponse)
        self.assertTrue(str(response.path).endswith("frontend_deploy/docs/index.html"))

    def test_frontend_docs_nested_page_serves_generated_file(self):
        self.assertTrue(hasattr(self.app_main, "frontend_docs_page"))

        response = self.app_main.frontend_docs_page("getting-started")

        self.assertIsInstance(response, FileResponse)
        self.assertTrue(str(response.path).endswith("frontend_deploy/docs/getting-started/index.html"))

    def test_frontend_robots_and_sitemap_serve_checked_in_files(self):
        self.assertTrue(hasattr(self.app_main, "ROBOTS_TXT_PATH"))
        self.assertTrue(hasattr(self.app_main, "SITEMAP_XML_PATH"))

        robots = self.app_main.frontend_robots()
        sitemap = self.app_main.frontend_sitemap()

        self.assertIsInstance(robots, FileResponse)
        self.assertIsInstance(sitemap, FileResponse)
        self.assertTrue(str(robots.path).endswith("frontend_deploy/robots.txt"))
        self.assertTrue(str(sitemap.path).endswith("frontend_deploy/sitemap.xml"))

    def test_frontend_root_market_id_redirects_to_app(self):
        request = Request({"type": "http", "method": "GET", "path": "/", "query_string": b"market_id=test123"})
        response = self.app_main.frontend_root(request)

        self.assertIsInstance(response, RedirectResponse)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers.get("location"), "/app?market_id=test123")

    def test_frontend_landing_is_hidden_when_frontend_disabled(self):
        os.environ.pop("SERVE_FRONTEND", None)
        try:
            with self.assertRaises(HTTPException) as ctx:
                self.app_main.frontend_landing()
            self.assertEqual(ctx.exception.status_code, 404)
        finally:
            os.environ["SERVE_FRONTEND"] = "1"

    def test_frontend_custom_data_is_hidden_when_frontend_disabled(self):
        os.environ.pop("SERVE_FRONTEND", None)
        try:
            with self.assertRaises(HTTPException) as ctx:
                self.app_main.frontend_custom_data()
            self.assertEqual(ctx.exception.status_code, 404)
        finally:
            os.environ["SERVE_FRONTEND"] = "1"

    def test_frontend_docs_is_hidden_when_frontend_disabled(self):
        os.environ.pop("SERVE_FRONTEND", None)
        try:
            with self.assertRaises(HTTPException) as ctx:
                self.app_main.frontend_docs()
            self.assertEqual(ctx.exception.status_code, 404)
        finally:
            os.environ["SERVE_FRONTEND"] = "1"

    def test_frontend_docs_nested_page_is_hidden_when_frontend_disabled(self):
        os.environ.pop("SERVE_FRONTEND", None)
        try:
            with self.assertRaises(HTTPException) as ctx:
                self.app_main.frontend_docs_page("getting-started")
            self.assertEqual(ctx.exception.status_code, 404)
        finally:
            os.environ["SERVE_FRONTEND"] = "1"


if __name__ == "__main__":
    unittest.main()
