#!/usr/bin/env python3
"""Fail-fast guardrail for telemetry cost/latency risk."""

from __future__ import annotations

import argparse
import importlib.util
import os
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
    parser.add_argument('--max-monthly-usd', type=float, default=float(os.getenv('QA_MAX_MONTHLY_USD', '100')))
    parser.add_argument('--max-over5s', type=int, default=int(os.getenv('QA_MAX_OVER5S', '20')))
    parser.add_argument('--output', default='', help='Optional output summary file')
    args = parser.parse_args()

    dashboard = load_module('scripts/qa/telemetry_dashboard.py', 'telemetry_dashboard_mod')
    forecast = load_module('scripts/qa/telemetry_forecast.py', 'telemetry_forecast_mod')

    raw = Path(args.input).read_text().splitlines()
    events = [e for e in (dashboard.parse_line(line) for line in raw) if e is not None]
    if not events:
        print('GUARDRAIL_FAIL: no telemetry events parsed')
        return 2

    forecast_events = [e for e in (forecast.parse_event(line) for line in raw) if e is not None]
    if not forecast_events:
        print('GUARDRAIL_FAIL: no forecastable telemetry events parsed (missing timestamps)')
        return 2

    forecast_metrics = forecast.compute_metrics(forecast_events)

    over5s = sum(
        1
        for event in events
        if isinstance(event.get('ms'), (int, float)) and float(event.get('ms')) > 5000
    )
    monthly = float(forecast_metrics.get('monthly_forecast_7d') or 0.0)

    status = 'GUARDRAIL_OK'
    code = 0
    message = f'monthly=${monthly:.2f}, slow_events={over5s}'

    if monthly > args.max_monthly_usd:
        status = 'GUARDRAIL_FAIL'
        code = 3
        message = f'monthly forecast ${monthly:.2f} > ${args.max_monthly_usd:.2f}'
    elif over5s > args.max_over5s:
        status = 'GUARDRAIL_FAIL'
        code = 4
        message = f'slow events {over5s} > max {args.max_over5s}'

    line = f'{status}: {message}'
    print(line)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            '\n'.join([
                f'status={status}',
                f'monthly_usd={monthly:.2f}',
                f'slow_events={over5s}',
                f'max_monthly_usd={args.max_monthly_usd:.2f}',
                f'max_over5s={args.max_over5s}',
            ]) + '\n'
        )

    return code


if __name__ == '__main__':
    raise SystemExit(main())
