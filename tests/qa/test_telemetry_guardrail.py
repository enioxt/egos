import subprocess
from pathlib import Path
from unittest import TestCase
import os


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

    def test_guardrail_supports_env_thresholds_and_output_file(self):
        fixture = Path('tests/qa/fixtures/sample_telemetry.txt')
        out = Path('/tmp/qa-guardrail-test.txt')
        if out.exists():
            out.unlink()

        env = os.environ.copy()
        env['QA_MAX_MONTHLY_USD'] = '10'
        env['QA_MAX_OVER5S'] = '10'
        result = subprocess.run(
            [
                'python',
                'scripts/qa/telemetry_guardrail.py',
                '--input',
                str(fixture),
                '--output',
                str(out),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(out.exists())
        content = out.read_text()
        self.assertIn('status=GUARDRAIL_OK', content)

    def test_guardrail_fails_when_events_have_no_timestamps_for_forecast(self):
        fixture = Path('/tmp/qa-telemetry-no-timestamps.txt')
        fixture.write_text('[agents-cli-telemetry] {"ev":"tool_call","ms":120,"cost":0.01}\n')

        result = subprocess.run(
            [
                'python',
                'scripts/qa/telemetry_guardrail.py',
                '--input',
                str(fixture),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('GUARDRAIL_FAIL', result.stdout)
