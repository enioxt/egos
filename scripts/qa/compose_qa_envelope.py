#!/usr/bin/env python3
"""Compose QA artifacts into a single JSON envelope for integrations."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def read_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ''
    return p.read_text()


def parse_key_value(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        result[k.strip()] = v.strip()
    return result


def build_envelope(inputs: dict[str, str]) -> dict:
    guardrail_raw = read_text(inputs['guardrail'])
    ssot_raw = read_text(inputs['ssot'])
    evidence_raw = read_text(inputs['evidence'])

    guardrail = parse_key_value(guardrail_raw)

    return {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'sources': inputs,
        'gate_signals': {
            'guardrail_status': guardrail.get('status', 'unknown'),
            'guardrail_monthly_usd': guardrail.get('monthly_usd', 'n/a'),
            'guardrail_slow_events': guardrail.get('slow_events', 'n/a'),
            'ssot_classification_hint': 'env_drift' if 'env_drift' in ssot_raw else ('repo_drift' if 'repo_drift' in ssot_raw else 'unknown'),
            'telemetry_gate_pass': '✅ PASS' in evidence_raw,
        },
        'artifacts': {
            'guardrail': guardrail_raw,
            'ssot_diagnostic': ssot_raw,
            'evidence': evidence_raw,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Compose QA JSON envelope from existing artifacts')
    parser.add_argument('--guardrail', default='/tmp/qa-guardrail.txt')
    parser.add_argument('--ssot', default='/tmp/qa-ssot-check.md')
    parser.add_argument('--evidence', default='/tmp/qa-evidence.md')
    parser.add_argument('--output', default='/tmp/qa-envelope.json')
    args = parser.parse_args()

    payload = build_envelope({
        'guardrail': args.guardrail,
        'ssot': args.ssot,
        'evidence': args.evidence,
    })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    print(f'QA_ENVELOPE_OK: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
