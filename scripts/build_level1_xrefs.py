#!/usr/bin/env python3
"""Build or update Level-1 cross-reference blocks automatically.

Level-0 (canonical 6-item list) is assumed to exist already.  Level-1 collects
context-specific references (markdown links, imports, etc.) so documentation
stays inter-connected without manual effort.

Current implementation scope (MVP)
----------------------------------
• Scans *.md files and extracts relative markdown links `](path)` that resolve
  to other files inside the repository.
• Produces a block:

    @references(level=1):
      - path/to/OtherFile.md
      - another.md

• Inserts the block immediately after the Level-0 bullet that ends with
  `CROSSREF_STANDARD.md`.  If a previous Level-1 block exists it is replaced.
• Supports `--dry` preview mode and makes *.bak backups when modifying files.
• Shares exclusion rules and style with existing cleaner scripts.

Future expansion: parse Python/JS imports, smarter heuristics, ML detection,
pre-commit integration.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Iterable, Set
import time
import posixpath

# Optional progress bar for user feedback
try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    tqdm = None

EGOS_ROOT = Path(__file__).resolve().parents[1]

# This flag is set in main() based on --verbose
VERBOSE = False

# ---------- Repo traversal rules ------------------------------------------------
EXTS_TO_SCAN = {".md"}  # MVP: only markdown
EXCLUDE_DIR_NAMES = {
    "node_modules",
    "env",
    "venv",
    "lib",
    "Lib",
    "__pycache__",
    "dist-info",
    "egg-info",
    "website",  # generated site
    "backups",
    "backup",
    "archive",
    "archives",
    "_bak",
    "zz_archive",
}

LEVEL0_BASENAMES = {
    ".windsurfrules",
    "CODE_OF_CONDUCT.md",
    "MQP.md",
    "README.md",
    "ROADMAP.md",
    "CROSSREF_STANDARD.md",
}

# Regex for markdown links: [text](path)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#?]+)\)")

# Cap link processing to avoid runaway cost on huge files
MAX_LINKS = 500

# ---------- Helpers -------------------------------------------------------------

def iter_repo_files(root: Path = EGOS_ROOT) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTS_TO_SCAN and not any(
            part in EXCLUDE_DIR_NAMES for part in p.parts
        ):
            yield p


def extract_md_links(md_text: str, base_dir: Path) -> Set[str]:
    """Return repo-relative paths referenced by markdown links.

    Ultra-light parser – **no real filesystem calls**.  This function only
    performs string manipulations, making it thousands of times faster on
    Windows than repeatedly calling `Path.resolve()`.
    """
    refs: set[str] = set()
    for match in MD_LINK_RE.finditer(md_text):
        if len(refs) >= MAX_LINKS:
            break
        raw_href = match.group(1).strip()
        # Skip absolute URLs, mailto, anchors, etc.
        if (
            any(c in raw_href for c in "<>|")
            or raw_href.startswith("http")
            or raw_href.startswith("mailto:")
            or raw_href.startswith("#")
            or "//" in raw_href
            or raw_href.startswith("file:")
            or ":" in raw_href  # any scheme like ftp:
        ):
            continue
        # Build candidate repo-relative path purely with string ops (fast & normalised)
        candidate = posixpath.normpath((base_dir / raw_href).as_posix())
        egos_prefix = EGOS_ROOT.as_posix() + "/"
        if not candidate.startswith(egos_prefix):
            continue  # link points outside repo
        rel = candidate[len(egos_prefix):]
        if not rel:
            continue  # Self or root path
        refs.add(rel)
    return refs


def build_level1_refs(path: Path, text: str) -> Set[str]:
    if path.suffix.lower() == ".md":
        refs = extract_md_links(text, path.parent)
    else:
        refs = set()
    # Remove Level-0 names & self
    refs = {r for r in refs if Path(r).name not in LEVEL0_BASENAMES and r != str(path.relative_to(EGOS_ROOT)).replace("\\", "/")}
    return refs


# ---------- Core ----------------------------------------------------------------

def update_file(path: Path, dry: bool) -> bool:
    """Return True if file changed (or would change in dry mode)."""
    try:
        original = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return False

    start_time = time.perf_counter()
    refs = build_level1_refs(path, original)
    t_refs = time.perf_counter() - start_time
    if not refs:
        return False  # nothing to write

    # Prepare new block
    block_lines = ["@references(level=1):"] + [f"  - {r}" for r in sorted(refs)]

    lines = original.splitlines()
    # Quick exit: if an existing Level-1 block already matches, skip heavy rewrite
    existing_block_match = re.search(r"@references\(level=1\):[\s\S]*?$", original, re.MULTILINE)
    if existing_block_match:
        existing_block = existing_block_match.group(0).strip()
        new_block_text = "\n".join(["@references(level=1):"] + [f"  - {r}" for r in sorted(refs)]).strip()
        if existing_block == new_block_text:
            if VERBOSE:
                print(f"[SKIP] {path.name} already up to date")
            return False
    new_lines: list[str] = []
    i = 0
    replaced_existing = False
    inserted_after_level0 = False

    while i < len(lines):
        line = lines[i]
        # Detect existing Level-1 block to skip/replace
        token = line.lstrip(' #')
        if token.startswith("@references(level=1):"):
            # Optimized: Skip existing Level-1 block much faster
            block_end = i + 1
            while block_end < len(lines) and lines[block_end].lstrip().startswith("-"):
                block_end += 1
            i = block_end        # jump past entire block at once
            replaced_existing = True
            continue  # do not increment here; loop will increase
        new_lines.append(line)
        # Insert new block immediately after Level-0 terminal bullet
        if not inserted_after_level0 and "CROSSREF_STANDARD.md" in line:
            new_lines.append("")
            new_lines.extend(block_lines)
            inserted_after_level0 = True
        i += 1

    if not inserted_after_level0:
        # Fallback: append at file end
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.extend(block_lines)

    updated = "\n".join(new_lines)
    t_rewrite = time.perf_counter() - (start_time + t_refs)

    if VERBOSE:
        writer = tqdm.write if tqdm else print
        writer(f"[TIME] {path.relative_to(EGOS_ROOT)} refs={t_refs:.3f}s rewrite={t_rewrite:.3f}s lines={len(lines)}")

    if updated == original:
        return False

    if dry:
        return True

    # Write with backup
    backup_path = path.with_suffix(path.suffix + ".bak")
    if not backup_path.exists():
        try:
            shutil.copy2(path, backup_path)
        except OSError as exc:
            print(f"[WARN] Cannot create backup for {path}: {exc}")
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Level-1 cross-reference blocks.")
    parser.add_argument("--dry", action="store_true", help="Preview changes without writing files.")
    parser.add_argument("--root", type=str, default=str(EGOS_ROOT), help="Root directory to scan (defaults to project root).")
    parser.add_argument("--verbose", action="store_true", help="Print each file being processed (debug).")
    parser.add_argument("--limit", type=int, default=0, help="Process only N files (debug).")
    parser.add_argument("--exclude", action="append", default=[], help="Basename(s) to skip (may repeat).")
    args = parser.parse_args()

    # expose verbosity globally for update_file()
    global VERBOSE
    VERBOSE = args.verbose

    root_path = Path(args.root).resolve()

    file_iter = list(iter_repo_files(root_path))
    if args.exclude:
        excl_set = set(args.exclude)
        file_iter = [p for p in file_iter if p.name not in excl_set]
    if args.limit:
        file_iter = file_iter[: args.limit]
    iterable = tqdm(file_iter, desc="Building Level-1 refs") if tqdm else file_iter

    modified = 0
    for fp in iterable:
        if VERBOSE:
            writer = tqdm.write if tqdm else print
            writer(f"[CHECK] {fp.relative_to(root_path)}") 
        try:
            changed = update_file(fp, dry=args.dry)
            if changed:
                modified += 1
                writer = tqdm.write if tqdm else print
                if args.dry:
                    writer(f"[DRY] {fp.relative_to(EGOS_ROOT)}")
                else:
                    writer(f"[UPDATE] {fp.relative_to(EGOS_ROOT)}")
        except Exception as exc:
            print(f"[ERROR] {fp.relative_to(root_path)} -> {exc}")
            continue

    # Print final summary
    suffix = "would be" if args.dry else "were"
    print(f"\nDone. {modified} files {suffix} updated.")


if __name__ == "__main__":
    main()
