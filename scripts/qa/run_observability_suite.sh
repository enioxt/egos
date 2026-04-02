#!/usr/bin/env bash
set -euo pipefail

python -m unittest discover -s tests/qa -p 'test_*.py'
python scripts/qa/analyze_commits.py --count 25 --format markdown --output /tmp/qa-commit-audit.md
python scripts/qa/telemetry_dashboard.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-telemetry-dashboard.md
python scripts/qa/telemetry_forecast.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-telemetry-forecast.md
python scripts/qa/telemetry_guardrail.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-guardrail.txt
python scripts/qa/observability_evidence.py --telemetry-input tests/qa/fixtures/sample_telemetry.txt --guardrail-input /tmp/qa-guardrail.txt --output /tmp/qa-evidence.md
python scripts/qa/list_pending_tasks.py --input TASKS.md --output /tmp/qa-pending-tasks.md
python scripts/qa/stalled_tasks_report.py --input TASKS.md --output /tmp/qa-stalled-tasks.md
bun test packages/shared/src/__tests__/telemetry.test.ts
