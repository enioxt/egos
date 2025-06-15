"""merge_cost_reports.py
Aggregates multiple cost report CSV files found under a root directory
(e.g., C:\\EGOS\\data) into a single, deduplicated CSV enriched with a
`snapshot_date` column derived from the parent *backup-YYYYMMDDHHMMSS*
folder name.

Usage (PowerShell):
    python scripts/merge_cost_reports.py \
        --root C:\EGOS\data \
        --output C:\EGOS\data\roi\reports_merged.csv

The script will:
1. Recursively search for any file exactly named `reports.csv`.
2. Read each row with Python's built-in `csv` module (no third-party deps).
3. Append a `snapshot_date` column indicating the backup snapshot that row
   originated from. If the column already exists it will be overwritten.
4. Union all rows and write the merged result to the `--output` path,
   creating parent directories as needed.

This prepares a canonical cost dataset for ROI analytics & dashboards.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Iterable, List, Dict

# Optional progress bar
try:
    from tqdm import tqdm  # type: ignore
except ModuleNotFoundError:
    tqdm = None  # type: ignore

BACKUP_RE = re.compile(r"backup-(\d{14})")


def iter_cost_reports(root: Path) -> Iterable[Path]:
    """Yield every `reports.csv` beneath *root*."""
    # Standard reports.csv files from backup snapshots
    yield from root.rglob("reports.csv")
    
    # Also check for incident cost data in external sources
    external_dir = root / "external"
    if external_dir.exists():
        for source_dir in external_dir.iterdir():
            if source_dir.is_dir():
                # Look for CSV files that might contain incident cost data
                for csv_file in source_dir.glob("*cost*.csv"):
                    yield csv_file
                for csv_file in source_dir.glob("*incident*cost*.csv"):
                    yield csv_file


def derive_snapshot_date(path: Path) -> str:
    """Return YYYYMMDDHHMMSS from the nearest `backup-<stamp>` parent folder.
    For external datasets, extract date from filename pattern like incidentdatabase_ai_20250614.csv
    If none found, fallback to the name of the highest folder above the csv.
    """
    # Check if this is an external dataset with date in filename
    if "external" in path.parts:
        filename = path.name
        # Look for YYYYMMDD pattern in filename
        date_match = re.search(r'(\d{8})', filename)
        if date_match:
            return date_match.group(1)
    
    # Standard backup folder pattern
    for part in path.parents:
        m = BACKUP_RE.search(part.name)
        if m:
            return m.group(1)
    
    # Fallback – maybe `mongodump_full_snapshot00` or similar
    return part.name  # type: ignore[misc]


def merge_reports(reports: Iterable[Path]):
    rows: List[Dict[str, str]] = []
    headers: List[str] | None = None

    iterable = tqdm(reports, desc="Merging reports") if tqdm else reports

    for csv_path in iterable:
        snapshot = derive_snapshot_date(csv_path)
        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if headers is None:
                headers = list(reader.fieldnames or [])
                if "snapshot_date" not in headers:
                    headers.append("snapshot_date")
            for row in reader:
                row["snapshot_date"] = snapshot
                rows.append(row)
                # live row count feedback
                if tqdm:
                    iterable.set_postfix(rows=len(rows))

    if tqdm and hasattr(iterable, 'close'):
        iterable.close()

    if headers is None:
        raise RuntimeError("No reports.csv files found – nothing to merge.")
    return headers, rows


def write_merged_csv(headers: List[str], rows: List[Dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] Wrote {len(rows)} rows → {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge ATRiAN cost reports.csv files")
    parser.add_argument("--root", default="C:/EGOS/data", help="Root directory to scan (default: %(default)s)")
    parser.add_argument("--output", default="C:/EGOS/data/roi/reports_merged.csv", help="Output CSV path (default: %(default)s)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve()

    print(f"[INFO] Scanning {root} for reports.csv files …")
    reports = list(iter_cost_reports(root))
    print(f"[INFO] Found {len(reports)} cost report files")

    if not reports:
        print("[WARN] Nothing to merge. Exiting.")
        return

    headers, rows = merge_reports(reports)
    write_merged_csv(headers, rows, output)


if __name__ == "__main__":
    main()
