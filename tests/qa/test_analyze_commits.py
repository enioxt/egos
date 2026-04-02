import importlib.util
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "qa" / "analyze_commits.py"
spec = importlib.util.spec_from_file_location("analyze_commits", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class AnalyzeCommitsTests(TestCase):
    def test_commit_type_fallback(self):
        self.assertEqual(module._commit_type("feat(core): add x"), "feat")
        self.assertEqual(module._commit_type("random subject"), "other")

    def test_collect_stats_parses_types_dates_areas_files(self):
        header = "2026-04-01|feat(core): add x\n2026-04-01|docs: update y\n2026-03-31|misc change"
        files_blob = (
            "@@@2026-04-01|feat(core): add x\n"
            "packages/shared/src/index.ts\n"
            "docs/README.md\n"
            "@@@2026-04-01|docs: update y\n"
            "TASKS.md\n"
            "@@@2026-03-31|misc change\n"
            "scripts/qa/analyze_commits.py\n"
        )

        with patch.object(module, "_run_git", side_effect=[header, files_blob]):
            stats = module.collect_stats(100)

        self.assertEqual(stats.count, 100)
        self.assertEqual(stats.types["feat"], 1)
        self.assertEqual(stats.types["docs"], 1)
        self.assertEqual(stats.types["other"], 1)
        self.assertEqual(stats.dates["2026-04-01"], 2)
        self.assertEqual(stats.areas["packages"], 1)
        self.assertEqual(stats.areas["docs"], 1)
        self.assertEqual(stats.areas["TASKS.md"], 1)
        self.assertEqual(stats.files["scripts/qa/analyze_commits.py"], 1)
        self.assertEqual(sum(stats.frozen_zone_touches.values()), 0)

    def test_collect_stats_handles_commit_without_files(self):
        header = "2026-04-01|chore: housekeeping"
        files_blob = "@@@2026-04-01|chore: housekeeping\n"

        with patch.object(module, "_run_git", side_effect=[header, files_blob]):
            stats = module.collect_stats(10)

        self.assertEqual(stats.types["chore"], 1)
        self.assertEqual(sum(stats.files.values()), 0)
        self.assertEqual(sum(stats.areas.values()), 0)

    def test_collect_stats_detects_frozen_zone_touches(self):
        header = "2026-04-01|chore: update hook"
        files_blob = (
            "@@@2026-04-01|chore: update hook\n"
            ".husky/pre-commit\n"
            "docs/README.md\n"
        )

        with patch.object(module, "_run_git", side_effect=[header, files_blob]):
            stats = module.collect_stats(5)

        self.assertEqual(stats.frozen_zone_touches[".husky/pre-commit"], 1)

    def test_format_markdown_contains_sections(self):
        stats = module.QaStats(
            count=3,
            types=module.collections.Counter({"feat": 2, "docs": 1}),
            dates=module.collections.Counter({"2026-04-01": 3}),
            areas=module.collections.Counter({"docs": 2}),
            frozen_zone_touches=module.collections.Counter(),
            files=module.collections.Counter({"TASKS.md": 2}),
        )

        output = module.format_markdown(stats, top=1)

        self.assertIn("# QA Commit Audit (últimos 3 commits)", output)
        self.assertIn("## Tipos de commit", output)
        self.assertIn("## Concentração por data", output)
        self.assertIn("## Top 1 áreas por churn", output)
        self.assertIn("## Frozen zones (touch count)", output)
        self.assertIn("## Top 1 arquivos por churn", output)
