import unittest

from runtime_paths import repo_root


REPO_ROOT = repo_root()
MIGRATION = REPO_ROOT / "supabase" / "migrations" / "20260310_auth_recovery.sql"
TRACKING_FRONTEND = REPO_ROOT / "frontend_deploy" / "assets" / "polylab-tracking.js"
TRACKING_STATIC = REPO_ROOT / "static" / "assets" / "polylab-tracking.js"


class TestSupabaseRecoveryContract(unittest.TestCase):
    def test_checked_in_recovery_migration_exists(self):
        self.assertTrue(MIGRATION.exists(), f"Missing {MIGRATION}")

        sql = MIGRATION.read_text("utf-8")
        required_tokens = [
            "create table if not exists public.profiles",
            "create table if not exists public.marketing_events",
            "alter table public.profiles enable row level security",
            "alter table public.marketing_events enable row level security",
            "create or replace function public.handle_new_user()",
            "create trigger on_auth_user_created",
            "insert into public.profiles",
            "to authenticated",
            "to anon, authenticated",
            "utm_source",
            "session_id",
        ]

        normalized_sql = " ".join(sql.lower().split())
        for token in required_tokens:
            self.assertIn(token, normalized_sql, f"Missing migration token: {token}")

    def test_tracking_asset_exists_and_is_mirrored(self):
        self.assertTrue(TRACKING_FRONTEND.exists(), f"Missing {TRACKING_FRONTEND}")
        self.assertTrue(TRACKING_STATIC.exists(), f"Missing {TRACKING_STATIC}")
        self.assertEqual(
            TRACKING_FRONTEND.read_text("utf-8"),
            TRACKING_STATIC.read_text("utf-8"),
            "Tracking helper must stay mirrored between frontend_deploy and static",
        )

        asset = TRACKING_FRONTEND.read_text("utf-8")
        required_tokens = [
            "window.POLYLAB_TRACKING_CONFIG",
            "marketing_events",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "page_view",
            "cta_click",
            "data-track-event",
            "session_id",
            "firstTouchStorageKey",
            "entry_page_path",
            "entry_landing_variant",
        ]

        for token in required_tokens:
            self.assertIn(token, asset, f"Missing tracking token: {token}")

    def test_public_pages_and_app_load_tracking_helper(self):
        html_files = [
            REPO_ROOT / "frontend_deploy" / "index.html",
            REPO_ROOT / "frontend_deploy" / "landing" / "index.html",
            REPO_ROOT / "frontend_deploy" / "custom-data" / "index.html",
            REPO_ROOT / "frontend_deploy" / "app" / "index.html",
        ]

        for path in html_files:
            html = path.read_text("utf-8", errors="replace")
            self.assertIn("/assets/polylab-tracking.js", html, f"{path} should load the tracking helper")
            self.assertIn("data-page-key=", html, f"{path} should declare a page key for tracking")


if __name__ == "__main__":
    unittest.main()
