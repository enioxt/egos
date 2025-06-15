#!/usr/bin/env python3
"""Utility helpers for the AutoCrossRef subsystem.

Currently contains YAML-header parsing helpers used by multiple scripts.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

import yaml

EGOS_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_CROSSREF_STANDARD_PATH = EGOS_PROJECT_ROOT / "subsystems" / "AutoCrossRef" / "CROSSREF_STANDARD.md"


def load_core_refs() -> List[str]:
    """Return the list of Level-0 core references defined in ``CROSSREF_STANDARD.md``.

    The function only parses the YAML front-matter (between the first pair of
    `---` delimiters). If the file or key is missing it falls back to a minimal
    default (``[".windsurfrules"]``) so that downstream tooling never crashes.
    """
    if not _CROSSREF_STANDARD_PATH.exists():
        print(
            f"AutoCrossRef.utils: {_CROSSREF_STANDARD_PATH} not found – returning fallback core list.",
            flush=True,
        )
        return [".windsurfrules"]

    # Read only until the closing '---' of the front-matter.
    yaml_lines: list[str] = []
    with _CROSSREF_STANDARD_PATH.open("r", encoding="utf-8") as fh:
        first_sep_found = False
        for line in fh:
            if line.strip() == "---":
                if not first_sep_found:
                    first_sep_found = True
                    continue  # do not include first '---'
                else:
                    # reached closing separator – stop reading
                    break
            if first_sep_found:
                yaml_lines.append(line)

    try:
        header_data = yaml.safe_load("".join(yaml_lines)) or {}
        core_refs: list[str] = header_data.get("core_references", [])
        if not core_refs:
            raise ValueError("core_references key missing / empty in YAML header")
        # Normalise path separators to forward-slashes for consistency
        return [os.path.normpath(ref).replace("\\", "/") for ref in core_refs]
    except Exception as exc:  # noqa: BLE001 – we need broad catch to avoid crash in CI
        print(
            f"AutoCrossRef.utils: error parsing YAML header – {exc}. Using fallback core list.",
            flush=True,
        )
        return [".windsurfrules"]