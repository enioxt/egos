#!/usr/bin/env python3
"""Historical telemetry cost analysis + forecast from structured logs."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_event(line: str):
    if '] ' not in line:
        return None
    _, payload = line.split('] ', 1)
    payload = payload.strip()
    if not payload.startswith('{'):
        return None
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if 't' not in event:
        return None
    return event


def compute_metrics(events: list[dict]) -> dict:
    cost_by_day = defaultdict(float)

    for event in events:
        t = event.get('t')
        cost = float(event.get('cost') or 0)
        if not isinstance(t, str):
            continue
        try:
            dt = datetime.fromisoformat(t.replace('Z', '+00:00'))
        except ValueError:
            continue
        cost_by_day[dt.date().isoformat()] += cost

    ordered_days = sorted(cost_by_day.items(), key=lambda x: x[0])
    totals = [v for _, v in ordered_days]

    def avg(window: int) -> float:
        if not totals:
            return 0.0
        slice_values = totals[-window:] if len(totals) >= window else totals
        return sum(slice_values) / len(slice_values)

    avg7 = avg(7)
    avg30 = avg(30)
    total_observed = sum(totals)

    return {
        'days_observed': len(ordered_days),
        'total_observed_cost': total_observed,
        'daily_cost_series': ordered_days,
        'avg_daily_7d': avg7,
        'avg_daily_30d': avg30,
        'monthly_forecast_7d': avg7 * 30,
        'monthly_forecast_30d': avg30 * 30,
    }


def build_forecast(events: list[dict]) -> str:
    metrics = compute_metrics(events)
    ordered_days = metrics['daily_cost_series']

    lines = [
        '# Telemetry Historical Forecast',
        '',
        f'- Days observed: **{metrics["days_observed"]}**',
        f'- Total observed cost: **${metrics["total_observed_cost"]:.6f}**',
        '',
        '## Daily cost series',
    ]

    for day, value in ordered_days:
        lines.append(f'- {day}: ${value:.6f}')

    lines.extend([
        '',
        '## Forecast',
        f'- Avg daily (last 7d): `${metrics["avg_daily_7d"]:.6f}`',
        f'- Avg daily (last 30d): `${metrics["avg_daily_30d"]:.6f}`',
        f'- Monthly forecast from 7d avg: `${metrics["monthly_forecast_7d"]:.2f}`',
        f'- Monthly forecast from 30d avg: `${metrics["monthly_forecast_30d"]:.2f}`',
        '',
    ])

    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Forecast telemetry costs from historical logs')
    parser.add_argument('--input', required=True, help='Path to telemetry log file')
    parser.add_argument('--output', default='', help='Optional output markdown path')
    args = parser.parse_args()

    raw = Path(args.input).read_text().splitlines()
    events = [e for e in (parse_event(line) for line in raw) if e is not None]
    report = build_forecast(events)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)
    else:
        print(report)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
