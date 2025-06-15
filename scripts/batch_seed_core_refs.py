#!/usr/bin/env python3
"""Batch purge & seed Level-0 references across the entire EGOS repository.

Usage:
    python batch_seed_core_refs.py            # Dry-run (diagnose) only
    python batch_seed_core_refs.py --apply    # Apply changes (full mode)

The script will:
1. Discover every file containing an ``@references:`` header (via `git grep`).
2. For each file, call ``inject_reference`` in **full** mode with the Level-0
   core list loaded from ``CROSSREF_STANDARD.md``. This automatically removes
   self-references, purges legacy refs, and injects any missing core refs.
3. Produce a JSON summary (always) and an optional HTML report (TODO) that can
   be reviewed before committing.

Safety: without ``--apply`` it performs a *diagnose* dry-run and never writes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List

# Local imports – ensure src is on path
EGOS_ROOT = Path(__file__).resolve().parents[1]
if str(EGOS_ROOT) not in sys.path:
    sys.path.insert(0, str(EGOS_ROOT))

from subsystems.AutoCrossRef.src.ref_injector import inject_reference  # type: ignore
from subsystems.AutoCrossRef.src.utils import load_core_refs  # type: ignore


def find_reference_files() -> List[Path]:
    """Return all repo files that currently contain an @references: header."""
    try:
        output = subprocess.check_output(
            ["git", "grep", "-l", "@references:"], cwd=EGOS_ROOT
        ).decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError as err:
        # If grep returns non-zero because no match, we get CalledProcessError with returncode 1
        output = err.output.decode("utf-8", errors="ignore") if err.output else ""
    return [EGOS_ROOT / line.strip() for line in output.splitlines() if line.strip()]


def main() -> None:
    # Force unbuffered output
    import os
    os.environ['PYTHONUNBUFFERED'] = '1'
    parser = argparse.ArgumentParser(description="Purge legacy refs and seed Level-0 core refs across the repo.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to disk (runs in full mode). Without this flag we only diagnose.",
    )
    parser.add_argument(
        "--summary-json",
        default="autocrossref-global-summary.json",
        help="Path to write JSON summary (default: autocrossref-global-summary.json)",
    )
    args = parser.parse_args()

    core_refs = load_core_refs()
    mode = "full" if args.apply else "diagnose"

    all_results = []
    target_files = find_reference_files()
    print(f"AutoCrossRef Batch: scanning {len(target_files)} files…", flush=True)
    print(f"Core references to ensure: {core_refs}", flush=True)

    for fp in target_files:
        res = inject_reference(
            file_path=str(fp),
            reference_to_inject="",  # legacy param unused
            absolute_reference_path="",
            config={},
            references_to_ensure=core_refs,
            all_valid_core_refs=core_refs,
            mode=mode,
            create_backup=True,
        )
        all_results.append(res)
        if res.get("status") not in {"skipped_idempotent", "diagnose_only"}:
            print(f" → {fp.relative_to(EGOS_ROOT)}: {res['status']}", flush=True)

    with open(args.summary_json, "w", encoding="utf-8") as fh:
        json.dump(all_results, fh, indent=2)
    print(f"Summary written to {args.summary_json}")

    # Count files that need changes (missing refs, self refs, or legacy refs)
    needs_changes = [r for r in all_results 
                    if not r.get("is_compliant") 
                    or r.get("references_purged") 
                    or r.get("missing_references")]
    
    if needs_changes:
        missing_count = sum(1 for r in all_results if r.get("missing_references"))
        
        files_with_purged_self_refs = 0
        files_with_purged_legacy_refs = 0

        for r_item in all_results:
            if r_item.get("references_purged"):
                file_path_obj = Path(r_item["file_path"])
                # EGOS_ROOT is already a resolved Path object
                current_file_relative_path = str(file_path_obj.relative_to(EGOS_ROOT)).replace('\\', '/')
                current_file_basename = file_path_obj.name
                
                found_self_ref_in_file = False
                found_legacy_ref_in_file = False

                for purged_ref_str in r_item.get("references_purged", []):
                    # Normalize purged_ref_str for consistent comparison
                    normalized_purged_ref = str(Path(purged_ref_str)).replace('\\', '/')
                    is_self_ref = (normalized_purged_ref == current_file_relative_path or
                                   normalized_purged_ref == current_file_basename)
                    
                    if is_self_ref:
                        found_self_ref_in_file = True
                    else:
                        found_legacy_ref_in_file = True
                
                if found_self_ref_in_file:
                    files_with_purged_self_refs += 1
                if found_legacy_ref_in_file: # Count if any non-self-ref was purged
                    files_with_purged_legacy_refs += 1
        
        summary_prefix = "APPLY MODE SUMMARY" if args.apply else "DRY-RUN SUMMARY"
        print(f"\n{summary_prefix}: {len(needs_changes)} files need changes:")
        print(f" - {missing_count} files missing core references")
        print(f" - {files_with_purged_self_refs} files with self-references to purge")
        print(f" - {files_with_purged_legacy_refs} files with legacy references to purge")
        
        if not args.apply:
            print("\nRerun with --apply to make these changes.")
        else:
            print("\nAll changes applied. Review git diff and commit when satisfied.")
    else:
        print("\nNo changes needed – repository is already Level-0 compliant.")


if __name__ == "__main__":
    main()