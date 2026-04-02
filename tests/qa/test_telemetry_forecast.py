import importlib.util
import sys
from pathlib import Path
from unittest import TestCase

MODULE_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'qa' / 'telemetry_forecast.py'
spec = importlib.util.spec_from_file_location('telemetry_forecast', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TelemetryForecastTests(TestCase):
    def test_parse_event_accepts_valid_line(self):
        line = '[agents-cli-telemetry] {"t":"2026-04-01T00:00:00Z","cost":0.1}'
        event = module.parse_event(line)
        self.assertIsNotNone(event)

    def test_build_forecast_has_core_sections(self):
        events = [
            {'t': '2026-04-01T00:00:00Z', 'cost': 0.1},
            {'t': '2026-04-02T00:00:00Z', 'cost': 0.2},
        ]
        out = module.build_forecast(events)
        self.assertIn('# Telemetry Historical Forecast', out)
        self.assertIn('## Daily cost series', out)
        self.assertIn('## Forecast', out)
        self.assertIn('Monthly forecast from 7d avg', out)
