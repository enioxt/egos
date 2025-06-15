#!/usr/bin/env python3
"""validate_kernel_docs.py

EGOS Validation Script — Kernel Documentation Compliance Checker

Checks each Markdown file in docs/prompt_kernels/ for:
• Presence of YAML front-matter block;
• Required metadata fields: title, version, status, author, created, updated, pdd;
• Ensures the referenced PDD YAML file exists and passes KOIOS validation (optional — via validate_pdd.py if available);
• Outputs a summary and sets a non-zero exit code if any kernel doc fails.

Usage:
    python scripts/validation/validate_kernel_docs.py [--base-path C:\EGOS] [--strict]

Exit Codes:
    0  – all good
    1  – validation errors detected
    2  – script error

Cross-References:
    - .windsurfrules → `KERNEL_STANDARDS` block (validation rule linkage)
    - docs/standards/KOIOS_PDD_Standard.md (for PDD structure)
    - scripts/validation/validate_promptvault.py (complementary validator)
    - .windsurf/workflows/iterative_code_refinement_cycle.md (CI integration pattern)
"""
# 
# @references:
#   - scripts/validation/validate_kernel_docs.py
# 
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import yaml  # type: ignore
except ImportError:
    print("Missing PyYAML. Install with `pip install pyyaml`.", file=sys.stderr)
    sys.exit(2)

REQUIRED_FIELDS = [
    "title",
    "version",
    "status",
    "author",
    "created",
    "updated",
    "pdd",
]

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate EGOS kernel documentation files.")
    parser.add_argument("--base-path", default="C:/EGOS", help="Project root directory (defaults to C:/EGOS)")
    parser.add_argument("--strict", action="store_true", help="Fail if the referenced PDD file does not validate via validate_pdd.py")
    return parser.parse_args()


def validate_front_matter(content: str) -> Dict[str, Any]:
    match = FRONT_MATTER_RE.match(content)
    if not match:
        raise ValueError("Missing YAML front-matter block")
    front_matter = yaml.safe_load(match.group(1)) or {}
    for field in REQUIRED_FIELDS:
        if field not in front_matter:
            raise ValueError(f"Missing required field: {field}")
    return front_matter  # type: ignore


def validate_pdd(pdd_path: Path) -> bool:
    if not pdd_path.exists():
        return False
    # Call KOIOS validate_pdd.py if available
    validator = Path("subsystems/KOIOS/schemas/validate_pdd.py")
    if validator.exists():
        result = subprocess.run([sys.executable, str(validator), str(pdd_path)], capture_output=True)
        return result.returncode == 0
    return True  # assume valid if validator not present


def main() -> None:
    args = parse_args()
    base_path = Path(args.base_path)
    kernels_path = base_path / "docs" / "prompt_kernels"

    failures: List[str] = []

    for md_file in kernels_path.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            fm = validate_front_matter(content)
            pdd_rel = fm.get("pdd")
            if not pdd_rel:
                raise ValueError("Field 'pdd' must reference a PDD YAML file")
            pdd_path = base_path / pdd_rel.replace("/", os.sep)
            if args.strict and not validate_pdd(pdd_path):
                raise ValueError(f"Associated PDD failed validation: {pdd_path}")
        except Exception as exc:
            failures.append(f"{md_file}: {exc}")

    if failures:
        print("Kernel documentation validation failed:")
        for failure in failures:
            print("  •", failure)
        sys.exit(1)
    print("All kernel documentation files passed validation.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(2)