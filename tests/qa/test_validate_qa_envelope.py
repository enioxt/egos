import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from unittest import TestCase

MODULE_PATH = '/workspace/egos/scripts/qa/validate_qa_envelope.py'
spec = importlib.util.spec_from_file_location('validate_qa_envelope', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ValidateQaEnvelopeTests(TestCase):
    def test_validate_payload_ok(self):
        payload = {
            'generated_at_utc': '2026-04-02T00:00:00+00:00',
            'sources': {},
            'gate_signals': {
                'guardrail_status': 'GUARDRAIL_OK',
                'guardrail_monthly_usd': '0.20',
                'guardrail_slow_events': '1',
                'ssot_classification_hint': 'env_drift',
                'telemetry_gate_pass': True,
            },
            'artifacts': {},
        }
        self.assertEqual(module.validate_payload(payload), [])

    def test_validate_payload_missing_fields(self):
        payload = {'generated_at_utc': 'bad', 'gate_signals': {}}
        errors = module.validate_payload(payload)
        self.assertTrue(any('missing top-level keys' in e for e in errors))
        self.assertTrue(any('generated_at_utc is not a valid ISO datetime' in e for e in errors))

    def test_validate_payload_stale_timestamp(self):
        stale = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
        payload = {
            'generated_at_utc': stale,
            'sources': {},
            'gate_signals': {
                'guardrail_status': 'GUARDRAIL_OK',
                'guardrail_monthly_usd': '0.20',
                'guardrail_slow_events': '1',
                'ssot_classification_hint': 'env_drift',
                'telemetry_gate_pass': True,
            },
            'artifacts': {},
        }
        errors = module.validate_payload(payload, max_age_minutes=30)
        self.assertTrue(any('stale' in e for e in errors))
