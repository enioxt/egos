#!/usr/bin/env python3
"""Build a lightweight telemetry dashboard from structured log lines.

Expected line format:
  [agents-cli-telemetry] {"ev":"tool_call", ...}
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def parse_line(line: str):
    if '] ' not in line:
        return None
    _, payload = line.split('] ', 1)
    payload = payload.strip()
    if not payload.startswith('{'):
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


def build_dashboard(events: list[dict]):
    total = len(events)
    by_event = Counter(e.get('ev', 'unknown') for e in events)
    by_agent = Counter((e.get('meta') or {}).get('agentId', 'unknown') for e in events)
    by_tool = Counter((e.get('meta') or {}).get('toolName', 'unknown') for e in events if e.get('ev') == 'tool_call')

    cost_by_agent = defaultdict(float)
    slow_over_5s = Counter()
    for event in events:
        meta = event.get('meta') or {}
        agent_id = meta.get('agentId', 'unknown')
        cost = event.get('cost') or 0
        ms = event.get('ms') or 0
        cost_by_agent[agent_id] += float(cost)
        if isinstance(ms, (int, float)) and ms > 5000:
            slow_over_5s[event.get('ev', 'unknown')] += 1

    lines = [
        '# Telemetry Dashboard (Log-derived)',
        '',
        f'- Total events: **{total}**',
        '',
        '## Event volume',
    ]
    for key, amount in by_event.most_common():
        lines.append(f'- `{key}`: {amount}')

    lines.append('')
    lines.append('## Agent volume')
    for key, amount in by_agent.most_common():
        lines.append(f'- `{key}`: {amount}')

    lines.append('')
    lines.append('## Tool volume')
    for key, amount in by_tool.most_common():
        lines.append(f'- `{key}`: {amount}')

    lines.append('')
    lines.append('## Cost by agent (USD)')
    for key, amount in sorted(cost_by_agent.items(), key=lambda x: x[1], reverse=True):
        lines.append(f'- `{key}`: ${amount:.6f}')

    lines.append('')
    lines.append('## Slow events (>5s)')
    if slow_over_5s:
        for key, amount in slow_over_5s.most_common():
            lines.append(f'- `{key}`: {amount}')
    else:
        lines.append('- none')

    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build EGOS telemetry dashboard from logs')
    parser.add_argument('--input', required=True, help='Path to telemetry log file')
    parser.add_argument('--output', default='', help='Optional output markdown path')
    args = parser.parse_args()

    raw = Path(args.input).read_text().splitlines()
    events = [e for e in (parse_line(line) for line in raw) if e is not None]
    md = build_dashboard(events)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md)
    else:
        print(md)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
