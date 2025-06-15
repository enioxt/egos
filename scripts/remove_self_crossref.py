#!/usr/bin/env python3
"""Remove self-references that sometimes appear immediately after the standard
cross-reference block.

Example patterns removed (for ROADMAP.md):

    @references:
    - .windsurfrules
    - CODE_OF_CONDUCT.md
    - MQP.md
    - README.md
    - ROADMAP.md
    - CROSSREF_STANDARD.md

      - ROADMAP.md   # <- self-reference to remove

It also handles commented variants such as:

    # @references:
    #   - .windsurfrules
    #   - CODE_OF_CONDUCT.md
    #   - MQP.md
    #   - README.md
    #   - ROADMAP.md
    #   - CROSSREF_STANDARD.md

    @references:
      - ATRIA.MD      # <- self-reference to remove

Usage (from EGOS project root):
    python scripts/remove_self_crossref.py [--dry]

Options:
    --dry   Preview changes without modifying any file.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

# Optional progress bar
try:
    from tqdm import tqdm  # type: ignore
except ImportError:  # pragma: no cover
    tqdm = None

EGOS_ROOT = Path(__file__).resolve().parents[1]

# File extensions we care about (text & code). Adjust if needed.
EXTS = {
    ".md",
    ".txt",
    ".py",
    ".json",
    ".yaml",
    ".yml",
}

# Directories to skip (mirrors quick_crossref_cleaner exclusions)
EXCLUDE_DIR_NAMES = {
    "node_modules",
    "site-packages",
    "dist-info",
    "egg-info",
    "__pycache__",
    "Lib",  # venv on Windows
    "lib",
    "env",
    "venv",
    "pochete_env",
    ".venv",
    ".next",
    "backup",
    "backups",
    "archive",
    "archives",
    "zz_archive",
    "_bak",
    "_ref_bak",
    "ref_bak",
    "bak",
}

# Marker regexes (same as quick_crossref_cleaner)
MARKER_PATTERNS = (
    r"^@references:\s*$",
    r"^#\s*@references:\s*$",
    r"^<!--\s*@references:\s*-->\s*$",
)
MARKER_REGEXES = [re.compile(p) for p in MARKER_PATTERNS]


def iter_repo_files(root: Path = EGOS_ROOT) -> list[Path]:
    """Return repository files we want to inspect."""
    return [
        p
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in EXTS
        and not any(part in EXCLUDE_DIR_NAMES for part in p.parts)
    ]


def is_self_reference(line: str, basename: str) -> bool:
    """Return True if the line is a bullet item that references the current file."""
    # Strip leading comment markers, whitespace, HTML comment wrappers, etc.
    stripped = line.strip()

    # Remove potential comment prefixes
    if stripped.startswith("#"):
        stripped = stripped.lstrip("#").strip()
    if stripped.startswith("<!--") and stripped.endswith("-->"):
        stripped = stripped[4:-3].strip()

    # Normal bullet list begins with '- '
    if not stripped.startswith("-"):
        return False

    # Remove leading '-' and whitespace
    item = stripped.lstrip("- ").strip()
    # Case-insensitive match on basename
    return item.lower() == basename.lower()


def clean_file(path: Path) -> bool:
    """Remove self-reference lines from a file. Return True if modified."""
    try:
        original_text = path.read_text(encoding="utf-8", errors="ignore")
    except (UnicodeDecodeError, OSError):
        return False  # skip binary / unreadable

    basename = path.name  # includes extension
    lines = original_text.splitlines()
    cleaned_lines: list[str] = []
    modified = False

    for line in lines:
        if is_self_reference(line, basename):
            # Skip (remove) this line
            modified = True
            continue
        cleaned_lines.append(line)

    if not modified:
        return False

    updated_text = "\n".join(cleaned_lines)
    backup_path = path.with_suffix(path.suffix + ".bak")
    try:
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
    except OSError as exc:
        print(f"[WARN] Could not create backup for {path}: {exc}")
    path.write_text(updated_text, encoding="utf-8")
    return True


def preview_file(path: Path) -> bool:
    """Return True if self-reference would be removed from this file."""
    try:
        original_text = path.read_text(encoding="utf-8", errors="ignore")
    except (UnicodeDecodeError, OSError):
        return False
    basename = path.name
    return any(is_self_reference(line, basename) for line in original_text.splitlines())


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove self-reference lines from cross-reference blocks.")
    parser.add_argument("--dry", action="store_true", help="Preview changes without modifying files.")
    parser.add_argument("--root", type=str, default=str(EGOS_ROOT), help="Root directory to scan (defaults to project root).")
    args = parser.parse_args()

    root_path = Path(args.root).resolve()

    file_list = iter_repo_files(root_path)
    iterable = tqdm(file_list, desc="Scanning files") if tqdm else file_list

    modified_count = 0
    for fp in iterable:
        if args.dry:
            if preview_file(fp):
                print(f"[DRY] Would modify {fp.relative_to(root_path)}")
                modified_count += 1
        else:
            if clean_file(fp):
                print(f"[FIX] {fp.relative_to(root_path)}")
                modified_count += 1

    print(f"Done. {modified_count} files {'would be ' if args.dry else ''}modified.")


if __name__ == "__main__":
    main()
