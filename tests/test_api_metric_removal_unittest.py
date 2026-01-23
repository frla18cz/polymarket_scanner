import os
import sqlite3
import unittest
from fastapi import Response
from tests._db_snapshot import snapshot_main_db

class TestMetricRemoval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._snapshot = snapshot_main_db()
        os.environ["MARKETS_DB_PATH"] = str(cls._snapshot.path)

        import main as app_main
        app_main.DB_PATH = str(cls._snapshot.path)
        cls.app_main = app_main
        cls.app_main.ensure_indices()

        cls._conn = sqlite3.connect(str(cls._snapshot.path))
        cls._conn.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        os.environ.pop("MARKETS_DB_PATH", None)
        cls._conn.close()
        cls._snapshot.cleanup()

    def test_win_rate_param_removed(self):
        """Test that passing min_smart_money_win_rate raises TypeError (parameter removed)."""
        response = Response()
        try:
            self.app_main.get_markets(response=response, min_smart_money_win_rate=0.5)
            self.fail("Should have raised TypeError because min_smart_money_win_rate param is removed")
        except TypeError:
            pass # Expected
        except Exception as e:
            self.fail(f"Expected TypeError, got {type(e).__name__}: {e}")

    def test_win_rate_field_removed_from_response(self):
        """Test that smart_money_win_rate is not in the response."""
        response = Response()
        # Call without the removed parameter
        markets = self.app_main.get_markets(response=response, limit=1)
        if markets:
            self.assertNotIn("smart_money_win_rate", markets[0], "smart_money_win_rate should be removed from response")
