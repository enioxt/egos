import subprocess
from pathlib import Path
from unittest import TestCase


class TelemetryGuardrailTests(TestCase):
    def test_guardrail_passes_with_relaxed_threshold(self):
        fixture = Path('tests/qa/fixtures/sample_telemetry.txt')
        result = subprocess.run(
            [
                'python',
                'scripts/qa/telemetry_guardrail.py',
                '--input',
                str(fixture),
                '--max-monthly-usd',
                '10',
                '--max-over5s',
                '10',
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('GUARDRAIL_OK', result.stdout)

    def test_guardrail_fails_with_strict_monthly_threshold(self):
        fixture = Path('tests/qa/fixtures/sample_telemetry.txt')
        result = subprocess.run(
            [
                'python',
                'scripts/qa/telemetry_guardrail.py',
                '--input',
                str(fixture),
                '--max-monthly-usd',
                '0.01',
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('GUARDRAIL_FAIL', result.stdout)
