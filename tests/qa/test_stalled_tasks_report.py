import datetime as dt
import importlib.util
import sys
from pathlib import Path
from unittest import TestCase

MODULE_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'qa' / 'stalled_tasks_report.py'
spec = importlib.util.spec_from_file_location('stalled_tasks_report', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class StalledTasksReportTests(TestCase):
    def test_parse_sections_and_pending_extracts_ids_and_dates(self):
        text = '\n'.join([
            '### Area A (2026-04-01)',
            '- [ ] A-001: pending',
            '### Area B',
            '- [ ] B-002 pending no colon',
        ])

        items = module.parse_sections_and_pending(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['task_id'], 'A-001')
        self.assertEqual(items[0]['section_date'], dt.date(2026, 4, 1))
        self.assertEqual(items[1]['task_id'], 'B-002')
        self.assertIsNone(items[1]['section_date'])

    def test_build_report_contains_stalled_sections_and_top_table(self):
        items = [
            {
                'section': 'Area A (2026-04-01)',
                'section_date': dt.date(2026, 4, 1),
                'line': 10,
                'task_id': 'A-001',
                'task': 'A-001: pending',
            },
            {
                'section': 'Area A (2026-04-01)',
                'section_date': dt.date(2026, 4, 1),
                'line': 11,
                'task_id': 'A-002',
                'task': 'A-002: P0-URGENT pending',
            },
        ]

        report = module.build_report(items, today=dt.date(2026, 4, 2), min_age_days=1)
        self.assertIn('Frentes mais paradas', report)
        self.assertIn('Area A (2026-04-01)', report)
        self.assertIn('Top tasks para atenção imediata', report)
        self.assertIn('| 1 | A-002 | A-002: P0-URGENT pending |', report)
