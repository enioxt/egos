#!/usr/bin/env python3
"""Validate QA envelope schema and essential gate fields."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

REQUIRED_TOP = {'generated_at_utc', 'sources', 'gate_signals', 'artifacts'}
REQUIRED_GATES = {'guardrail_status', 'guardrail_monthly_usd', 'guardrail_slow_events', 'ssot_classification_hint', 'telemetry_gate_pass'}


def validate_payload(payload: dict) -> list[str]:
    errors: list[str] = []

    missing_top = sorted(REQUIRED_TOP - set(payload.keys()))
    if missing_top:
        errors.append(f'missing top-level keys: {", ".join(missing_top)}')

    gates = payload.get('gate_signals')
    if not isinstance(gates, dict):
        errors.append('gate_signals must be an object')
    else:
        missing_gates = sorted(REQUIRED_GATES - set(gates.keys()))
        if missing_gates:
            errors.append(f'missing gate_signals keys: {", ".join(missing_gates)}')

    ts = payload.get('generated_at_utc')
    if isinstance(ts, str):
        try:
            datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            errors.append('generated_at_utc is not a valid ISO datetime')
    else:
        errors.append('generated_at_utc must be a string')

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate /tmp/qa-envelope.json structure')
    parser.add_argument('--input', default='/tmp/qa-envelope.json')
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text())
    errors = validate_payload(data)
    if errors:
        print('QA_ENVELOPE_FAIL')
        for err in errors:
            print(f'- {err}')
        return 8

    print('QA_ENVELOPE_VALID')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
