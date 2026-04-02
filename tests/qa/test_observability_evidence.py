import importlib.util
import sys
from pathlib import Path
from unittest import TestCase

MODULE_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'qa' / 'observability_evidence.py'
spec = importlib.util.spec_from_file_location('observability_evidence', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ObservabilityEvidenceTests(TestCase):
    def test_build_report_marks_gate_signals(self):
        events = [
            {'ev': 'agent_session'},
            {'ev': 'tool_call'},
        ]
        guardrail = {'status': 'GUARDRAIL_OK', 'monthly_usd': '0.20', 'slow_events': '1'}

        report = module.build_report(events, guardrail)
        self.assertIn('agent session telemetry: ✅', report)
        self.assertIn('tool-call attribution telemetry: ✅', report)
        self.assertIn('cost/latency guardrail result: ✅', report)

    def test_build_report_marks_missing_signals(self):
        events = [{'ev': 'other'}]
        guardrail = {'status': 'GUARDRAIL_FAIL'}

        report = module.build_report(events, guardrail)
        self.assertIn('agent session telemetry: ❌', report)
        self.assertIn('tool-call attribution telemetry: ❌', report)
        self.assertIn('cost/latency guardrail result: ❌', report)
