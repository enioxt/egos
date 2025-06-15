#!/usr/bin/env python3
"""validate_promptvault.py

EGOS Validation Script — PromptVault JSON Compliance Checker

Scans `PromptVault/*.json` for:
• Valid JSON syntax;
• Required metadata fields: title, description, created, updated, author, llm_context_length;
• (Optional) Future schema check when `promptvault_schema.json` is finalized.

Usage:
    python scripts/validation/validate_promptvault.py [--base-path C:\EGOS] [--schema promptvault_schema.json]

Exit Codes:
    0 – all good
    1 – validation errors detected
    2 – script error

Cross-References:
    - .windsurfrules → `PROMPT_VAULT_STANDARDS` block (validation rule linkage)
    - .windsurf/workflows/distill_and_vault_prompt.md (creation workflow)
    - scripts/validation/validate_kernel_docs.py (companion validator)
    - docs/planning/PromptVault_System_Design.md (design reference)
"""
# 
# @references:
#   - scripts/validation/validate_promptvault.py
# 
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

REQUIRED_FIELDS = [
    "title",
    "description",
    "created",
    "updated",
    "author",
    "llm_context_length",
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PromptVault JSON files.")
    parser.add_argument("--base-path", default="C:/EGOS", help="Project root directory")
    parser.add_argument("--schema", help="(Future) path to JSON schema file")
    return parser.parse_args()


def validate_prompt_file(file_path: Path) -> List[str]:
    errors: List[str] = []
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{file_path}: JSON parse error – {exc}"]

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{file_path}: missing required field '{field}'")

    # Placeholder for future schema validation logic
    return errors


def main() -> None:
    args = parse_args()
    base = Path(args.base_path)
    vault_dir = base / "PromptVault"

    all_errors: List[str] = []
    for json_file in vault_dir.glob("*.json"):
        all_errors.extend(validate_prompt_file(json_file))

    if all_errors:
        print("PromptVault validation failed:")
        for err in all_errors:
            print("  •", err)
        sys.exit(1)
    print("All PromptVault JSON files passed validation.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(2)