#!/usr/bin/env python3
"""Identify stalled pending fronts from TASKS.md for async prioritization."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from collections import defaultdict
from pathlib import Path

SECTION_RE = re.compile(r"^###\s+(.*)")
PENDING_RE = re.compile(r"^\s*-\s\[\s\]\s+(.*)")
DATE_RE = re.compile(r"\((\d{4}-\d{2}-\d{2})\)")
TASK_ID_RE = re.compile(r"^([A-Z]+(?:-[A-Z]+)*-\d+[A-Z]?)\b")


def parse_sections_and_pending(text: str) -> list[dict]:
    section = "Uncategorized"
    section_date: dt.date | None = None
    items: list[dict] = []

    for line_no, line in enumerate(text.splitlines(), start=1):
        m_section = SECTION_RE.match(line)
        if m_section:
            section = m_section.group(1).strip()
            m_date = DATE_RE.search(section)
            section_date = dt.date.fromisoformat(m_date.group(1)) if m_date else None
            continue

        m_pending = PENDING_RE.match(line)
        if not m_pending:
            continue

        task = m_pending.group(1).strip()
        m_id = TASK_ID_RE.match(task)
        task_id = m_id.group(1) if m_id else ""
        items.append({
            "section": section,
            "section_date": section_date,
            "line": line_no,
            "task_id": task_id,
            "task": task,
        })

    return items


def build_report(items: list[dict], today: dt.date, min_age_days: int = 1) -> str:
    by_section: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        by_section[item["section"]].append(item)

    stalled_sections: list[tuple[str, int, int]] = []
    for section, section_items in by_section.items():
        section_date = section_items[0]["section_date"]
        age = (today - section_date).days if section_date else 0
        if age >= min_age_days:
            stalled_sections.append((section, len(section_items), age))

    stalled_sections.sort(key=lambda row: (-row[2], -row[1], row[0]))

    lines = [
        "# Stalled Tasks Report",
        "",
        f"- Generated at: `{today.isoformat()}`",
        f"- Pending tasks total: **{len(items)}**",
        f"- Stalled threshold: **{min_age_days}+ days**",
        "",
        "## Frentes mais paradas (seção)",
    ]

    if not stalled_sections:
        lines.append("- none")
    else:
        for section, count, age in stalled_sections:
            lines.append(f"- `{section}`: {count} pending, age ~{age}d")

    lines.extend(["", "## Top tasks para atenção imediata", "", "| # | Task ID | Task | Section | Age(d) | Line |", "|---|---|---|---|---:|---:|"])

    ranked: list[dict] = []
    for item in items:
        section_date = item["section_date"]
        age = (today - section_date).days if section_date else 0
        urgency_boost = 5 if "P0" in item["task"] or "URGENT" in item["task"] else 0
        ranked.append({**item, "age": age, "score": age + urgency_boost})

    ranked.sort(key=lambda item: (-item["score"], -item["age"], item["section"], item["line"]))

    for idx, item in enumerate(ranked[:15], start=1):
        tid = item["task_id"] or "—"
        task = item["task"].replace("|", "\\|")
        lines.append(
            f"| {idx} | {tid} | {task} | {item['section']} | {item['age']} | {item['line']} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate stalled tasks report from TASKS.md")
    parser.add_argument("--input", default="TASKS.md")
    parser.add_argument("--output", default="")
    parser.add_argument("--today", default="", help="Override YYYY-MM-DD")
    parser.add_argument("--min-age-days", type=int, default=1)
    args = parser.parse_args()

    text = Path(args.input).read_text()
    items = parse_sections_and_pending(text)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    report = build_report(items, today=today, min_age_days=args.min_age_days)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
