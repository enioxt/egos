import tempfile
import unittest
from pathlib import Path

from scripts.qa import llmrefs_staleness


class LlmrefsStalenessTests(unittest.TestCase):
    def test_audit_docs_detects_missing_link(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs = root / "docs"
            docs.mkdir()
            (docs / "A.md").write_text(
                "# A\n\n<!-- llmrefs:start -->\n- **Read next:**\n  - `docs/MISSING.md`\n<!-- llmrefs:end -->\n",
                encoding="utf-8",
            )
            issues = llmrefs_staleness.audit_docs(root)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0][1], "docs/MISSING.md")

    def test_apply_renames_in_block_only_changes_llmrefs(self):
        text = (
            "# T\n\n"
            "<!-- llmrefs:start -->\n"
            "- **Read next:**\n"
            "  - `docs/OLD.md`\n"
            "<!-- llmrefs:end -->\n"
            "\nReference docs/OLD.md outside block.\n"
        )
        updated = llmrefs_staleness.apply_renames_in_block(
            text, {"docs/OLD.md": "docs/NEW.md"}
        )
        self.assertIn("`docs/NEW.md`", updated)
        self.assertIn("Reference docs/OLD.md outside block.", updated)

    def test_parse_rename_flags_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            llmrefs_staleness.parse_rename_flags(["invalid"])


if __name__ == "__main__":
    unittest.main()
