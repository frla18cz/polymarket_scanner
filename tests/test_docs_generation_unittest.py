import subprocess
import unittest
from pathlib import Path

from runtime_paths import repo_root


REPO_ROOT = repo_root()
SOURCE_ROOT = REPO_ROOT / "docs" / "access" / "site"


class TestDocsGeneration(unittest.TestCase):
    def test_docs_markdown_source_tree_exists_with_frontmatter(self):
        expected_sources = [
            SOURCE_ROOT / "index.md",
            SOURCE_ROOT / "getting-started.md",
            SOURCE_ROOT / "how-polylab-works.md",
            SOURCE_ROOT / "workflows.md",
            SOURCE_ROOT / "scanner" / "filters-and-sorting.md",
            SOURCE_ROOT / "scanner" / "market-details-and-holders.md",
            SOURCE_ROOT / "metrics" / "core-metrics.md",
            SOURCE_ROOT / "methodology" / "apr.md",
            SOURCE_ROOT / "methodology" / "smart-money.md",
            SOURCE_ROOT / "data" / "freshness-and-limitations.md",
            SOURCE_ROOT / "sources" / "markets-and-events.md",
            SOURCE_ROOT / "sources" / "holders-and-wallet-pnl.md",
            SOURCE_ROOT / "pipeline" / "refresh-storage-and-snapshots.md",
            SOURCE_ROOT / "reference" / "upstream-field-map.md",
            SOURCE_ROOT / "reference" / "scanner-query-contract.md",
            SOURCE_ROOT / "reference" / "public-api-contract.md",
            SOURCE_ROOT / "faq.md",
            SOURCE_ROOT / "appendix" / "access-model.md",
            SOURCE_ROOT / "appendix" / "storage-and-runtime.md",
        ]

        required_frontmatter_keys = [
            "title:",
            "slug:",
            "section:",
            "order:",
            "summary:",
            "status:",
            "description:",
        ]

        for source_path in expected_sources:
            self.assertTrue(source_path.exists(), f"Missing docs source: {source_path}")
            content = source_path.read_text("utf-8", errors="replace")
            self.assertTrue(content.startswith("---\n"), f"Missing frontmatter start: {source_path}")
            for key in required_frontmatter_keys:
                self.assertIn(key, content, f"Missing frontmatter key {key} in {source_path}")
            self.assertIn("status: in-progress", content, f"All public docs pages should be marked in progress: {source_path}")

    def test_docs_generator_check_passes(self):
        script_path = REPO_ROOT / "scripts" / "build_public_docs.py"
        self.assertTrue(script_path.exists(), f"Missing docs generator: {script_path}")

        result = subprocess.run(
            ["python", str(script_path), "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"Docs generator --check failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_generator_source_uses_single_homepage_intro_pattern(self):
        script_path = REPO_ROOT / "scripts" / "build_public_docs.py"
        content = script_path.read_text("utf-8", errors="replace")

        self.assertIn("docs-home-banner", content)
        self.assertIn("docs-sidebar-note", content)
        self.assertNotIn("Documentation is in progress.", content)


if __name__ == "__main__":
    unittest.main()
