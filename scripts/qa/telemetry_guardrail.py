#!/usr/bin/env python3
"""Fail-fast guardrail for telemetry cost/latency risk."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description='Telemetry guardrail checks')
    parser.add_argument('--input', required=True, help='Path to telemetry log file')
    parser.add_argument('--max-monthly-usd', type=float, default=100.0)
    parser.add_argument('--max-over5s', type=int, default=20)
    args = parser.parse_args()

    dashboard = load_module('scripts/qa/telemetry_dashboard.py', 'telemetry_dashboard_mod')
    forecast = load_module('scripts/qa/telemetry_forecast.py', 'telemetry_forecast_mod')

    raw = Path(args.input).read_text().splitlines()
    events = [e for e in (dashboard.parse_line(line) for line in raw) if e is not None]
    if not events:
        print('GUARDRAIL_FAIL: no telemetry events parsed')
        return 2

    forecast_events = [e for e in (forecast.parse_event(line) for line in raw) if e is not None]
    forecast_md = forecast.build_forecast(forecast_events)

    over5s = sum(
        1
        for event in events
        if isinstance(event.get('ms'), (int, float)) and float(event.get('ms')) > 5000
    )
    monthly = 0.0

    for line in forecast_md.splitlines():
        if line.startswith('- Monthly forecast from 7d avg:'):
            monthly = float(line.split('`$')[1].split('`')[0])
            break

    if monthly > args.max_monthly_usd:
        print(f'GUARDRAIL_FAIL: monthly forecast ${monthly:.2f} > ${args.max_monthly_usd:.2f}')
        return 3

    if over5s > args.max_over5s:
        print(f'GUARDRAIL_FAIL: slow events {over5s} > max {args.max_over5s}')
        return 4

    print(f'GUARDRAIL_OK: monthly=${monthly:.2f}, slow_events={over5s}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
