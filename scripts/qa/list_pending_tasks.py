#!/usr/bin/env python3
"""Extract unchecked tasks from TASKS.md and emit a markdown report."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

SECTION_RE = re.compile(r"^###\s+(.*)")
PENDING_RE = re.compile(r"^\s*-\s\[\s\]\s+(.*)")
TASK_ID_RE = re.compile(r"^([A-Z]+(?:-[A-Z]+)*-\d+[A-Z]?)\b")


def parse_pending_tasks(text: str):
    section = "Uncategorized"
    results: list[dict] = []

    for line_number, raw in enumerate(text.splitlines(), start=1):
        section_match = SECTION_RE.match(raw)
        if section_match:
            section = section_match.group(1).strip()
            continue

        pending_match = PENDING_RE.match(raw)
        if pending_match:
            task = pending_match.group(1).strip()
            task_id_match = TASK_ID_RE.match(task)
            task_id = task_id_match.group(1) if task_id_match else ""
            results.append(
                {
                    'section': section,
                    'line': line_number,
                    'task_id': task_id,
                    'task': task,
                }
            )

    return results


def build_markdown_report(items: list[dict], source_file: str) -> str:
    by_section = defaultdict(int)
    for item in items:
        by_section[item['section']] += 1

    lines = [
        '# Pending Tasks Snapshot',
        '',
        f'- Source: `{source_file}`',
        f'- Total pending tasks: **{len(items)}**',
        '',
        '## Pending by section',
    ]

    for section, amount in sorted(by_section.items(), key=lambda pair: (-pair[1], pair[0])):
        lines.append(f'- `{section}`: {amount}')

    lines.extend(['', '## Full pending list', '', '| # | Section | Task ID | Task | Line |', '|---|---|---|---|---|'])

    for idx, item in enumerate(items, start=1):
        task_id = item['task_id'] or '—'
        task = item['task'].replace('|', '\\|')
        lines.append(f"| {idx} | {item['section']} | {task_id} | {task} | {item['line']} |")

    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='List all pending tasks from TASKS.md')
    parser.add_argument('--input', default='TASKS.md', help='Input TASKS markdown file')
    parser.add_argument('--output', default='', help='Optional output markdown file path')
    args = parser.parse_args()

    source = Path(args.input)
    text = source.read_text()
    pending_items = parse_pending_tasks(text)
    report = build_markdown_report(pending_items, str(source))

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)
    else:
        print(report)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
