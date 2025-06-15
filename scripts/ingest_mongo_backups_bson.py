"""MongoDB-free ingestion of backup folders → Parquet

This script is an alternative to ``ingest_mongo_backups.py`` that **does not**
require a local MongoDB installation.  Instead it reads the raw ``*.bson`` files
inside a mongodump folder directly using the ``bson`` package.

Workflow per backup folder (under data/raw/mongo_backups/):
1. Derive a slug from the folder name (e.g. ``backup-20250331100541`` →
   ``20250331``).
2. Locate all ``*.bson`` files.  Group them by collection name.
3. For each target collection (see ``TARGET_COLLECTIONS``):
   • Parse every BSON document into Python dicts.
   • Load the dicts into a pandas DataFrame.
   • Write DataFrame to Parquet at
     ``data/processed/<slug>/<collection>.parquet``.
4. Write a ``manifest.json`` summarising row counts & columns.
5. Move the processed backup directory to ``data/raw/mongo_backups/archived``.

Run:
    python ingest_mongo_backups_bson.py            # process all un-archived
    python ingest_mongo_backups_bson.py backup-123 # process specific folder

Dependencies: bson, pandas, pyarrow
"""
from __future__ import annotations

import argparse
import glob
import json
import shutil
from pathlib import Path
from typing import Dict, List

import bson  # type: ignore
import pandas as pd  # type: ignore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw" / "mongo_backups"
PROCESSED_DIR = DATA_DIR / "processed"
ARCHIVE_DIR = RAW_DIR / "archived"

# Limit to the collections we actually care about for ROI analytics
TARGET_COLLECTIONS = [
    "incidents",
    "cost_reports",
    "users",
]

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def dump_slug(folder: Path) -> str:
    """Create a short slug for processed output based on folder name."""
    return folder.name.replace("backup-", "").replace("mongodump_", "")


def find_bson_files(folder: Path) -> Dict[str, List[Path]]:
    """Return mapping {collection_name: [bson_path, …]} for the dump folder."""
    mapping: Dict[str, List[Path]] = {}
    for bson_path in glob.glob(str(folder / "**" / "*.bson"), recursive=True):
        p = Path(bson_path)
        coll = p.stem  # filename without extension => collection name
        mapping.setdefault(coll, []).append(p)
    return mapping


def bson_files_to_df(paths: List[Path]) -> pd.DataFrame:
    """Read a set of BSON files into a single DataFrame."""
    records: List[dict] = []
    for path in paths:
        # A .bson file is a sequence of BSON documents
        with path.open("rb") as fh:
            while True:
                size_bytes = fh.read(4)
                if len(size_bytes) < 4:
                    break  # EOF
                size = int.from_bytes(size_bytes, "little")
                fh.seek(-4, 1)  # rewind to include size in slice
                doc = fh.read(size)
                try:
                    records.extend(bson.decode_all(doc))
                except Exception as exc:  # pragma: no cover
                    print(f"[WARN] failed to decode doc in {path}: {exc}")
    df = pd.DataFrame(records)
    # Arrow cannot handle bson.ObjectId; convert any such columns to strings
    if not df.empty:
        from bson import ObjectId as _OID  # local import to avoid global dependency when unused
        for col in df.columns:
            if df[col].dtype == "object" and df[col].apply(lambda v: isinstance(v, _OID)).any():
                df[col] = df[col].astype(str)
    return df

# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process_folder(folder: Path):
    slug = dump_slug(folder)
    out_dir = PROCESSED_DIR / slug

    if out_dir.exists():
        print(f"[SKIP] {folder.name} already processed → {out_dir}")
        return

    print(f"[INFO] Processing backup {folder.name} …")
    out_dir.mkdir(parents=True, exist_ok=True)

    bson_map = find_bson_files(folder)
    if not bson_map:
        print(f"[WARN] No BSON files found in {folder}")
        return

    manifest = {}
    for coll in TARGET_COLLECTIONS:
        if coll not in bson_map:
            print(f"[WARN] Collection '{coll}' missing in {folder.name}")
            continue

        df = bson_files_to_df(bson_map[coll])
        if df.empty:
            print(f"[WARN] Collection '{coll}' is empty in {folder.name}")
            continue

        pq_path = out_dir / f"{coll}.parquet"
        df.to_parquet(pq_path, index=False)
        manifest[coll] = {
            "rows": len(df),
            "parquet": str(pq_path.relative_to(DATA_DIR)),
            "columns": list(df.columns),
            "size_mb": round(pq_path.stat().st_size / (1024 * 1024), 2),
        }
        print(f"  • {coll}: {len(df)} rows → {pq_path}")

    # Write manifest
    if manifest:
        with (out_dir / "manifest.json").open("w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)
        print(f"[OK] Manifest written → {out_dir / 'manifest.json'}")

        # Archive raw folder
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(folder), ARCHIVE_DIR / folder.name)
        print(f"[INFO] Archived raw dump to {ARCHIVE_DIR / folder.name}\n")
    else:
        print(f"[WARN] Nothing was processed for {folder.name}\n")

# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main(folder_args: List[str]):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    targets = (
        [RAW_DIR / p for p in folder_args]
        if folder_args
        else [p for p in RAW_DIR.iterdir() if p.is_dir() and p.name != "archived"]
    )

    if not targets:
        print("[INFO] No backup folders to process.")
        return

    for t in targets:
        if not t.exists():
            print(f"[WARN] Folder {t} not found, skipping…")
            continue
        process_folder(t)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MongoDB dump folders (BSON) → Parquet without MongoDB installation")
    parser.add_argument("folders", nargs="*", help="Specific folder names to process; default=all un-archived")
    args = parser.parse_args()
    main(args.folders)
