#!/usr/bin/env python3
"""Generate a lightweight QA summary from recent git commits.

Usage:
  python scripts/qa/analyze_commits.py --count 100
  python scripts/qa/analyze_commits.py --count 100 --format markdown > docs/qa/_generated/last100.md
"""

from __future__ import annotations

import argparse
import collections
from pathlib import Path
import re
import subprocess
from dataclasses import dataclass

FROZEN_ZONES = (
    "agents/runtime/runner.ts",
    "agents/runtime/event-bus.ts",
    ".husky/pre-commit",
    ".guarani/orchestration/PIPELINE.md",
)


@dataclass
class QaStats:
    count: int
    types: collections.Counter
    dates: collections.Counter
    areas: collections.Counter
    files: collections.Counter
    frozen_zone_touches: collections.Counter


def _run_git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _commit_type(subject: str) -> str:
    match = re.match(r"(\w+)(\(.+\))?:", subject)
    return match.group(1) if match else "other"


def collect_stats(count: int) -> QaStats:
    header = _run_git("log", f"-n{count}", "--pretty=format:%ad|%s", "--date=short")
    files_blob = _run_git(
        "log",
        f"-n{count}",
        "--name-only",
        "--pretty=format:@@@%ad|%s",
        "--date=short",
    )

    types: collections.Counter[str] = collections.Counter()
    dates: collections.Counter[str] = collections.Counter()
    areas: collections.Counter[str] = collections.Counter()
    files: collections.Counter[str] = collections.Counter()
    frozen_zone_touches: collections.Counter[str] = collections.Counter()

    for line in header.splitlines():
        if not line.strip():
            continue
        if "|" not in line:
            continue
        date, subject = line.split("|", 1)
        dates[date] += 1
        types[_commit_type(subject)] += 1

    for entry in files_blob.split("@@@")[1:]:
        lines = [ln for ln in entry.splitlines() if ln.strip()]
        if not lines:
            continue
        for path in lines[1:]:
            files[path] += 1
            areas[path.split("/", 1)[0] if "/" in path else path] += 1
            if path in FROZEN_ZONES:
                frozen_zone_touches[path] += 1

    return QaStats(
        count=count,
        types=types,
        dates=dates,
        areas=areas,
        files=files,
        frozen_zone_touches=frozen_zone_touches,
    )


def format_markdown(stats: QaStats, top: int) -> str:
    lines: list[str] = []
    lines.append(f"# QA Commit Audit (últimos {stats.count} commits)")
    lines.append("")

    lines.append("## Tipos de commit")
    total = sum(stats.types.values()) or 1
    for commit_type, amount in stats.types.most_common():
        pct = (amount / total) * 100
        lines.append(f"- `{commit_type}`: {amount} ({pct:.1f}%)")

    lines.append("")
    lines.append("## Concentração por data")
    for date, amount in sorted(stats.dates.items()):
        lines.append(f"- {date}: {amount}")

    lines.append("")
    lines.append(f"## Top {top} áreas por churn")
    for area, amount in stats.areas.most_common(top):
        lines.append(f"- `{area}`: {amount}")

    lines.append("")
    lines.append("## Frozen zones (touch count)")
    if stats.frozen_zone_touches:
        for path, amount in stats.frozen_zone_touches.most_common():
            lines.append(f"- ⚠️ `{path}`: {amount}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append(f"## Top {top} arquivos por churn")
    for path, amount in stats.files.most_common(top):
        lines.append(f"- `{path}`: {amount}")

    lines.append("")
    return "\n".join(lines)


def format_text(stats: QaStats, top: int) -> str:
    blocks = [
        f"count={stats.count}",
        f"types={dict(stats.types)}",
        f"dates={dict(stats.dates)}",
        f"areas_top={stats.areas.most_common(top)}",
        f"frozen_zone_touches={dict(stats.frozen_zone_touches)}",
        f"files_top={stats.files.most_common(top)}",
    ]
    return "\n".join(blocks) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="EGOS QA commit auditor")
    parser.add_argument("--count", type=int, default=100, help="How many recent commits")
    parser.add_argument("--top", type=int, default=10, help="Top N entries for hotspots")
    parser.add_argument(
        "--format",
        choices=["markdown", "text"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output file path. Prints to stdout when omitted.",
    )
    args = parser.parse_args()

    stats = collect_stats(args.count)
    rendered = ""
    if args.format == "markdown":
        rendered = format_markdown(stats, args.top)
    else:
        rendered = format_text(stats, args.top)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered)
    else:
        print(rendered, end="" if rendered.endswith("\n") else "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
