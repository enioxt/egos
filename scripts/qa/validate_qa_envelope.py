#!/usr/bin/env python3
"""Validate QA envelope schema and essential gate fields."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_TOP = {'generated_at_utc', 'sources', 'gate_signals', 'artifacts'}
REQUIRED_GATES = {'guardrail_status', 'guardrail_monthly_usd', 'guardrail_slow_events', 'ssot_classification_hint', 'telemetry_gate_pass'}
MANIFEST_PATH = Path('scripts/qa/artifact_manifest.json')


def load_allowed_artifacts() -> set[str]:
    if not MANIFEST_PATH.exists():
        return set()
    data = json.loads(MANIFEST_PATH.read_text())
    items = data.get('versioned_artifacts') or []
    return {str(item) for item in items}


def validate_payload(
    payload: dict,
    max_age_minutes: int | None = None,
    coherence_mode: str = 'off',
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_top = sorted(REQUIRED_TOP - set(payload.keys()))
    if missing_top:
        errors.append(f'missing top-level keys: {", ".join(missing_top)}')

    gates = payload.get('gate_signals')
    sources = payload.get('sources')
    allowed = load_allowed_artifacts()
    if isinstance(sources, dict) and allowed:
        unknown = sorted({str(v) for v in sources.values()} - allowed)
        if unknown:
            errors.append(f'sources include non-versioned artifacts: {", ".join(unknown)}')
    if not isinstance(gates, dict):
        errors.append('gate_signals must be an object')
    else:
        missing_gates = sorted(REQUIRED_GATES - set(gates.keys()))
        if missing_gates:
            errors.append(f'missing gate_signals keys: {", ".join(missing_gates)}')

    ts = payload.get('generated_at_utc')
    parsed_ts: datetime | None = None
    if isinstance(ts, str):
        try:
            parsed_ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            errors.append('generated_at_utc is not a valid ISO datetime')
    else:
        errors.append('generated_at_utc must be a string')

    if parsed_ts and max_age_minutes is not None:
        now = datetime.now(timezone.utc)
        ts_utc = parsed_ts.astimezone(timezone.utc)
        age_minutes = (now - ts_utc).total_seconds() / 60
        if age_minutes > max_age_minutes:
            errors.append(f'generated_at_utc is stale: {age_minutes:.1f}m > {max_age_minutes}m')

    if coherence_mode in {'warn', 'fail'} and isinstance(gates, dict):
        status = str(gates.get('guardrail_status', 'unknown'))
        telemetry_gate_pass = gates.get('telemetry_gate_pass')
        coherence_issues: list[str] = []
        if telemetry_gate_pass is True and status != 'GUARDRAIL_OK':
            coherence_issues.append('coherence error: telemetry_gate_pass=true but guardrail_status is not GUARDRAIL_OK')
        if telemetry_gate_pass is False and status == 'GUARDRAIL_OK':
            coherence_issues.append('coherence error: telemetry_gate_pass=false but guardrail_status is GUARDRAIL_OK')
        if coherence_mode == 'fail':
            errors.extend(coherence_issues)
        else:
            warnings.extend(coherence_issues)

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate /tmp/qa-envelope.json structure')
    parser.add_argument('--input', default='/tmp/qa-envelope.json')
    parser.add_argument('--max-age-minutes', type=int, default=120, help='Maximum allowed age for generated_at_utc')
    parser.add_argument('--coherence-mode', choices=['off', 'warn', 'fail'], default='off', help='Coherence check mode for guardrail_status vs telemetry_gate_pass')
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text())
    errors, warnings = validate_payload(
        data,
        max_age_minutes=args.max_age_minutes,
        coherence_mode=args.coherence_mode,
    )
    for warning in warnings:
        print(f'QA_ENVELOPE_WARN: {warning}')
    if errors:
        print('QA_ENVELOPE_FAIL')
        for err in errors:
            print(f'- {err}')
        return 8

    print('QA_ENVELOPE_VALID')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
