import importlib.util
import sys
from pathlib import Path
from unittest import TestCase

MODULE_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'qa' / 'telemetry_dashboard.py'
spec = importlib.util.spec_from_file_location('telemetry_dashboard', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TelemetryDashboardTests(TestCase):
    def test_parse_line_accepts_prefixed_json(self):
        line = '[agents-cli-telemetry] {"ev":"tool_call","ms":123}'
        event = module.parse_line(line)
        self.assertEqual(event['ev'], 'tool_call')

    def test_build_dashboard_contains_sections(self):
        events = [
            {'ev': 'tool_call', 'ms': 6400, 'cost': 0.01, 't': '2026-04-01T00:00:00Z', 'meta': {'agentId': 'mcp-router', 'toolName': 'web.search'}},
            {'ev': 'agent_session', 'ms': 1200, 'cost': 0.00, 't': '2026-04-01T01:00:00Z', 'meta': {'agentId': 'context-tracker'}},
        ]
        md = module.build_dashboard(events)
        self.assertIn('# Telemetry Dashboard (Log-derived)', md)
        self.assertIn('## Event volume', md)
        self.assertIn('## Cost by agent (USD)', md)
        self.assertIn('## Slow events (>5s)', md)
        self.assertIn('## Cost forecast (run-rate)', md)
