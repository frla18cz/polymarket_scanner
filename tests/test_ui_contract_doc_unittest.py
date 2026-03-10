import unittest

from runtime_paths import repo_root


class TestUiContractDoc(unittest.TestCase):
    def test_ui_contract_matches_current_public_app_contract(self):
        content = (repo_root() / "docs" / "UI_CONTRACT.md").read_text("utf-8", errors="replace")

        self.assertIn("frontend_deploy/app/index.html", content)
        self.assertIn("static/app/index.html", content)
        self.assertIn("filters.min_profitable", content)
        self.assertIn("`smart_money_win_rate` is not part of the current public app contract", content)
        self.assertNotIn("filters.min_smart_money_win_rate", content)
        self.assertNotIn("min_smart_money_win_rate", content)


if __name__ == "__main__":
    unittest.main()
