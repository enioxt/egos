import importlib.util
import json
import sys
from pathlib import Path
from unittest import TestCase

MODULE_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'qa' / 'list_pending_tasks.py'
spec = importlib.util.spec_from_file_location('list_pending_tasks', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class _BrokenPipeWriter:
    def write(self, _):
        raise BrokenPipeError()

    def flush(self):
        return None


class ListPendingTasksTests(TestCase):
    def test_parse_pending_tasks_extracts_only_unchecked(self):
        text = '\n'.join([
            '### Section A',
            '- [x] A-001 done',
            '- [ ] A-002 pending',
            '### Section B',
            '  - [ ] B-001 nested pending: detail',
        ])

        items = module.parse_pending_tasks(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['section'], 'Section A')
        self.assertEqual(items[0]['task_id'], 'A-002')
        self.assertEqual(items[1]['section'], 'Section B')

    def test_build_markdown_report_contains_summary_and_table(self):
        items = [
            {'section': 'Section A', 'line': 3, 'task_id': 'A-002', 'task': 'A-002: pending',},
            {'section': 'Section B', 'line': 6, 'task_id': 'B-001', 'task': 'B-001: pending',},
        ]

        report = module.build_markdown_report(items, 'TASKS.md')
        self.assertIn('Total pending tasks: **2**', report)
        self.assertIn('| # | Section | Task ID | Task | Line |', report)
        self.assertIn('| 1 | Section A | A-002 | A-002: pending | 3 |', report)

    def test_build_json_report_contains_totals_and_items(self):
        items = [
            {'section': 'Section A', 'line': 3, 'task_id': 'A-002', 'task': 'A-002: pending'},
        ]
        raw = module.build_json_report(items, 'TASKS.md')
        payload = json.loads(raw)
        self.assertEqual(payload['source'], 'TASKS.md')
        self.assertEqual(payload['pending_total'], 1)
        self.assertEqual(payload['pending_by_section']['Section A'], 1)
        self.assertEqual(payload['items'][0]['task_id'], 'A-002')

    def test_write_report_handles_broken_pipe(self):
        writer = _BrokenPipeWriter()
        ok = module.write_report('payload', writer)
        self.assertFalse(ok)

