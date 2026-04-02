import importlib.util
import json
import sys
from pathlib import Path
from unittest import TestCase

MODULE_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'qa' / 'compose_qa_envelope.py'
spec = importlib.util.spec_from_file_location('compose_qa_envelope', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ComposeQaEnvelopeTests(TestCase):
    def test_build_envelope_extracts_gate_signals(self):
        base = Path('/tmp/compose-qa-test')
        base.mkdir(parents=True, exist_ok=True)
        guardrail = base / 'guardrail.txt'
        ssot = base / 'ssot.md'
        evidence = base / 'evidence.md'

        guardrail.write_text('status=GUARDRAIL_OK\nmonthly_usd=0.20\nslow_events=1\n')
        ssot.write_text('classification: env_drift\n')
        evidence.write_text('telemetry minimum gate: ✅ PASS\n')

        payload = module.build_envelope(
            {'guardrail': str(guardrail), 'ssot': str(ssot), 'evidence': str(evidence)}
        )

        self.assertEqual(payload['gate_signals']['guardrail_status'], 'GUARDRAIL_OK')
        self.assertEqual(payload['gate_signals']['ssot_classification_hint'], 'env_drift')
        self.assertTrue(payload['gate_signals']['telemetry_gate_pass'])

    def test_parse_key_value_handles_empty(self):
        self.assertEqual(module.parse_key_value(''), {})
        self.assertEqual(module.parse_key_value('a=1\nb=2')['b'], '2')
