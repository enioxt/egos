#!/usr/bin/env bash
set -euo pipefail

python -m unittest discover -s tests/qa -p 'test_*.py'
python scripts/qa/analyze_commits.py --count 25 --format markdown --output /tmp/qa-commit-audit.md
python scripts/qa/ssot_check_diagnostic.py --command 'sh scripts/governance-sync.sh --check' --output /tmp/qa-ssot-check.md
python scripts/qa/telemetry_dashboard.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-telemetry-dashboard.md
python scripts/qa/telemetry_forecast.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-telemetry-forecast.md
python scripts/qa/telemetry_guardrail.py --input tests/qa/fixtures/sample_telemetry.txt --output /tmp/qa-guardrail.txt
python scripts/qa/observability_evidence.py --telemetry-input tests/qa/fixtures/sample_telemetry.txt --guardrail-input /tmp/qa-guardrail.txt --output /tmp/qa-evidence.md --enforce
python scripts/qa/compose_qa_envelope.py --guardrail /tmp/qa-guardrail.txt --ssot /tmp/qa-ssot-check.md --evidence /tmp/qa-evidence.md --output /tmp/qa-envelope.json
python scripts/qa/validate_qa_envelope.py --input /tmp/qa-envelope.json --max-age-minutes 180
python scripts/qa/list_pending_tasks.py --input TASKS.md --output /tmp/qa-pending-tasks.md
python scripts/qa/stalled_tasks_report.py --input TASKS.md --output /tmp/qa-stalled-tasks.md
bun test packages/shared/src/__tests__/telemetry.test.ts
