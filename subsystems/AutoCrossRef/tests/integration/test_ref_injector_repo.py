# @references:
#   - subsystems/AutoCrossRef/tests/integration/test_ref_injector_repo.py
# 
import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Import the function under test from the same package level
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / 'src'))
from ref_injector import inject_reference


@pytest.fixture()
def sample_repo(tmp_path):
    """Create a tiny repo with a couple of files to exercise RefInjector end-to-end."""
    samples = [
        (
            "readme.md",
            """# Sample README\n\nSome intro.\n""",
            "docs/intro.md",
        ),
        (
            "module.py",
            """#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\nprint('hi')\n""",
            "utils/helper.py",
        ),
    ]

    for fname, content, _ in samples:
        (tmp_path / fname).write_text(content, encoding="utf-8")
    return tmp_path, samples


def _default_config(backup_dir):
    """Return a minimal config dict with backups enabled."""
    return {
        "backup_options": {"enabled": True, "directory": str(backup_dir)},
        "resolve_options": {"enabled": False},
        "file_index_cache_ttl": 0,
        "parser_options": {"python": {}, "markdown": {}},
    }


def test_integration_inserts_and_backups(sample_repo):
    repo_path, samples = sample_repo
    backup_dir = repo_path / "_bak"
    config = _default_config(backup_dir)

    for fname, _content, ref in samples:
        file_path = repo_path / fname
        # absolute path to satisfy parameter requirement
        resolved_abs_ref = str(repo_path / ref)
        # Ensure directory of resolved path exists to avoid false negative exists-check
        os.makedirs(os.path.dirname(resolved_abs_ref), exist_ok=True)
        Path(resolved_abs_ref).touch()

        # keep original for later comparison
        original_bytes = file_path.read_bytes()

        success = inject_reference(
            str(file_path), ref, resolved_abs_ref, config, dry_run=False
        )
        assert success, f"inject_reference failed for {fname}"

        # backup file should exist and match original
        # Backups are timestamped: <stem>_<YYYYMMDD_HHMMSS><suffix>
        backups = list(backup_dir.glob(f"{file_path.stem}_*{file_path.suffix}"))
        assert backups, f"Backup not created for {fname}"
        bak_path = backups[0]
        assert bak_path.read_bytes() == original_bytes, "Backup differs from original"

        # modified file should now contain the reference block and the ref path
        modified_text = file_path.read_text(encoding="utf-8")
        assert "@references:" in modified_text.lower(), "Reference block missing"
        assert ref in modified_text, "Injected reference not present"