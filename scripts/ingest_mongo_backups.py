"""ETL utility to ingest MongoDB dump folders under data/raw/mongo_backups/.

1. For each backup directory it will:
   • Derive a slug from the folder name (e.g. backup-20250331100541 → 20250331).
   • Spin-up (or reuse) a local temporary `mongod` instance bound to a random free port.
   • Use `mongorestore` to load the dump into the temporary server.
   • Export selected collections to JSON via `mongoexport`.
   • Convert JSON → Parquet using pandas (+ pyarrow) and write to
     data/processed/<slug>/<collection>.parquet.
   • Generate a `manifest.json` with row counts and basic stats for each collection.
   • Tear-down the temporary Mongo server.

2. After successful processing, the script can optionally move the original dump
   folder to an `archived/` sub-directory (or prompt the user).

The script avoids heavy dependencies: only `pandas`, `pyarrow`, and `psutil` for
port detection. MongoDB tools (`mongod`, `mongorestore`, `mongoexport`) must be
available on PATH.

Run:
    python ingest_mongo_backups.py --all   # process every un-processed folder
    python ingest_mongo_backups.py backup-20250331100541  # process one

"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

import pandas as pd  # type: ignore

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw" / "mongo_backups"
PROCESSED_DIR = DATA_DIR / "processed"
ARCHIVE_DIR = RAW_DIR / "archived"

# Collections to export; edit as needed.
TARGET_COLLECTIONS = [
    "incidents",
    "cost_reports",
    "users",
]

def find_free_port() -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]

def start_temp_mongod(data_dir: Path) -> subprocess.Popen[bytes]:
    port = find_free_port()
    cmd = [
        "mongod",
        "--dbpath",
        str(data_dir),
        "--port",
        str(port),
        "--quiet",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc, port

def stop_mongod(proc: subprocess.Popen[bytes]):
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def restore_dump(dump_path: Path, port: int):
    cmd = [
        "mongorestore",
        "--port",
        str(port),
        "--drop",
        str(dump_path),
    ]
    subprocess.check_call(cmd)


def export_collection(coll: str, out_json: Path, port: int):
    cmd = [
        "mongoexport",
        "--port",
        str(port),
        "--db",
        "admin",  # update if needed
        "--collection",
        coll,
        "--out",
        str(out_json),
        "--quiet",
    ]
    subprocess.check_call(cmd)


def json_to_parquet(json_path: Path, parquet_path: Path):
    df = pd.read_json(json_path, lines=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)


def process_backup_folder(folder: Path):
    slug = folder.name.replace("backup-", "").replace("mongodump_", "")
    out_dir = PROCESSED_DIR / slug
    if out_dir.exists():
        print(f"[SKIP] {folder.name} already processed → {out_dir}")
        return

    temp_dbpath = Path(tempfile.mkdtemp())
    mongod_proc, port = start_temp_mongod(temp_dbpath)
    try:
        print(f"[INFO] Restoring {folder.name} on port {port} …")
        restore_dump(folder, port)

        stats = {}
        for coll in TARGET_COLLECTIONS:
            json_fp = temp_dbpath / f"{coll}.json"
            export_collection(coll, json_fp, port)
            pq_fp = out_dir / f"{coll}.parquet"
            json_to_parquet(json_fp, pq_fp)
            rows = pd.read_parquet(pq_fp).shape[0]
            stats[coll] = {"rows": rows, "parquet": str(pq_fp.relative_to(DATA_DIR))}
            json_fp.unlink(missing_ok=True)

        manifest_path = out_dir / "manifest.json"
        out_dir.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("w", encoding="utf-8") as fh:
            json.dump(stats, fh, indent=2)

        print(f"[OK] Processed {folder.name} → {out_dir}")
    finally:
        stop_mongod(mongod_proc)
        shutil.rmtree(temp_dbpath, ignore_errors=True)

    # Optionally archive raw folder
    ARCHIVE_DIR.mkdir(exist_ok=True, parents=True)
    shutil.move(str(folder), ARCHIVE_DIR / folder.name)


def main(args: List[str]):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True, parents=True)

    if args:
        targets = [RAW_DIR / p for p in args]
    else:
        targets = [p for p in RAW_DIR.iterdir() if p.is_dir() and p.name != "archived"]

    for folder in targets:
        if not folder.exists():
            print(f"[WARN] {folder} does not exist, skipping.")
            continue
        process_backup_folder(folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest MongoDB backup folders → Parquet")
    parser.add_argument("folders", nargs="*", help="Specific folders to process; default = all unprocessed")
    cli_args = parser.parse_args()
    main(cli_args.folders)
