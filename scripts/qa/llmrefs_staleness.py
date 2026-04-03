#!/usr/bin/env python3
"""Audit llmrefs Read-next links and optionally auto-heal path renames."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

START = "<!-- llmrefs:start -->"
END = "<!-- llmrefs:end -->"
PATH_RE = re.compile(r"`([^`]+\.md)`")


def extract_block(text: str) -> str | None:
    if START not in text or END not in text:
        return None
    _, rest = text.split(START, 1)
    block, _ = rest.split(END, 1)
    return block


def extract_read_next_paths(block: str) -> list[str]:
    paths: list[str] = []
    for line in block.splitlines():
        if "Read next" in line or line.strip().startswith("- `"):
            for match in PATH_RE.findall(line):
                paths.append(match)
    return paths


def apply_renames_in_block(text: str, renames: dict[str, str]) -> str:
    block = extract_block(text)
    if block is None:
        return text
    new_block = block
    for old, new in renames.items():
        new_block = new_block.replace(f"`{old}`", f"`{new}`")
    return text.replace(block, new_block, 1)


def parse_rename_flags(items: Iterable[str]) -> dict[str, str]:
    renames: dict[str, str] = {}
    for item in items:
        if ":" not in item:
            raise ValueError(f"Invalid --rename value: {item}. Expected OLD:NEW")
        old, new = item.split(":", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ValueError(f"Invalid --rename value: {item}. Expected OLD:NEW")
        renames[old] = new
    return renames


def audit_docs(root: Path) -> list[tuple[Path, str]]:
    issues: list[tuple[Path, str]] = []
    for doc in sorted(root.glob("docs/*.md")):
        text = doc.read_text(encoding="utf-8")
        block = extract_block(text)
        if block is None:
            continue
        for ref in extract_read_next_paths(block):
            target = root / ref
            if not target.exists():
                issues.append((doc, ref))
    return issues


def write_report(output: Path, issues: list[tuple[Path, str]]) -> None:
    lines = ["# LLMRefs Staleness Audit", ""]
    if not issues:
        lines += ["LLMREFS_OK: no broken `Read next` links found.", ""]
    else:
        lines += [f"LLMREFS_STALE: {len(issues)} broken link(s).", ""]
        for doc, ref in issues:
            lines.append(f"- `{doc.as_posix()}` -> missing `{ref}`")
        lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit llmrefs link staleness.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--output", default="/tmp/qa-llmrefs.md", help="Report path")
    parser.add_argument(
        "--rename",
        action="append",
        default=[],
        help="Auto-heal rename mapping OLD:NEW within llmrefs blocks",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output)

    renames = parse_rename_flags(args.rename)
    if renames:
        for doc in sorted(root.glob("docs/*.md")):
            text = doc.read_text(encoding="utf-8")
            updated = apply_renames_in_block(text, renames)
            if updated != text:
                doc.write_text(updated, encoding="utf-8")

    issues = audit_docs(root)
    write_report(output, issues)
    if issues:
        print(f"LLMREFS_STALE: {len(issues)}")
        return 1
    print("LLMREFS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
