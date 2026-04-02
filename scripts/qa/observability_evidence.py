#!/usr/bin/env python3
"""Generate a compact QA evidence summary with telemetry gate signals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_telemetry_events(path: str) -> list[dict]:
    events: list[dict] = []
    for line in Path(path).read_text().splitlines():
        payload = line.strip()
        if '] ' in payload:
            _, payload = payload.split('] ', 1)
            payload = payload.strip()
        if not payload.startswith('{'):
            continue
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


def parse_guardrail(path: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        values[k.strip()] = v.strip()
    return values


def evaluate_gate(events: list[dict], guardrail: dict[str, str]) -> dict[str, object]:
    event_types = {str(e.get('ev', '')) for e in events}
    has_agent_session = 'agent_session' in event_types
    has_tool_call = 'tool_call' in event_types
    guardrail_status = guardrail.get('status', 'unknown')
    guardrail_ok = guardrail_status == 'GUARDRAIL_OK'

    gate_ok = has_agent_session and has_tool_call and guardrail_ok
    return {
        'has_agent_session': has_agent_session,
        'has_tool_call': has_tool_call,
        'guardrail_status': guardrail_status,
        'guardrail_ok': guardrail_ok,
        'gate_ok': gate_ok,
    }


def build_report(events: list[dict], guardrail: dict[str, str]) -> str:
    gate = evaluate_gate(events, guardrail)
    monthly = guardrail.get('monthly_usd', 'n/a')
    slow_events = guardrail.get('slow_events', 'n/a')

    lines = [
        '# QA Observability Evidence',
        '',
        f"- telemetry minimum gate: {'✅ PASS' if gate['gate_ok'] else '❌ FAIL'}",
        '',
        '## Telemetry minimum gate',
        f"- agent session telemetry: {'✅' if gate['has_agent_session'] else '❌'}",
        f"- tool-call attribution telemetry: {'✅' if gate['has_tool_call'] else '❌'}",
        f"- cost/latency guardrail result: {'✅' if gate['guardrail_ok'] else '❌'} ({gate['guardrail_status']})",
        '',
        '## Guardrail snapshot',
        f'- monthly_usd: `{monthly}`',
        f'- slow_events: `{slow_events}`',
        '',
        '## Evidence notes',
        f'- parsed telemetry events: **{len(events)}**',
    ]
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build QA evidence summary')
    parser.add_argument('--telemetry-input', required=True, help='Telemetry log input')
    parser.add_argument('--guardrail-input', required=True, help='Guardrail summary input')
    parser.add_argument('--output', default='', help='Optional output markdown path')
    parser.add_argument('--enforce', action='store_true', help='Fail when telemetry minimum gate is not satisfied')
    args = parser.parse_args()

    events = parse_telemetry_events(args.telemetry_input)
    guardrail = parse_guardrail(args.guardrail_input)
    report = build_report(events, guardrail)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)
    else:
        print(report)

    if args.enforce:
        gate = evaluate_gate(events, guardrail)
        if not gate['gate_ok']:
            print('TELEMETRY_GATE_FAIL: telemetry minimum gate not satisfied')
            return 5

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
