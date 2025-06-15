"""Ingest SaaS provider incident feeds (CSV/JSON) into Parquet for ROI pipeline.

Supported input formats (auto-detected by file extension):
  - .csv  (comma-separated)
  - .json (newline-delimited JSON or array)

Expected minimal schema after normalization:
  incident_id, provider, description, date, estimated_cost_usd?, severity_score?
Any missing numeric fields will be filled with defaults:
  estimated_cost_usd -> 0 (will be enriched later)
  severity_score -> 1

Usage:
  python scripts/ingest_saas_incidents.py --raw-dir C:\EGOS\data\raw\saas_incidents
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

RAW_DIR_DEFAULT = Path(r"C:\EGOS\data\raw\saas_incidents")
PROCESSED_DIR = Path(r"C:\EGOS\data\processed\saas_incidents")
OUTPUT_PARQUET = PROCESSED_DIR / "saas_incidents.parquet"


REQUIRED_COLUMNS = {"incident_id", "provider", "description", "date"}

def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def _load_json(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try line-delimited JSON
        data = [json.loads(line) for line in text.splitlines() if line.strip()]
    return pd.DataFrame(data)

def load_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return _load_csv(path)
    if path.suffix.lower() == ".json":
        return _load_json(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    # Fill defaults
    if "estimated_cost_usd" not in df.columns:
        df["estimated_cost_usd"] = 0
    if "severity_score" not in df.columns:
        df["severity_score"] = 1
    return df

def main():
    parser = argparse.ArgumentParser(description="Ingest SaaS incident feeds into Parquet")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR_DEFAULT)
    parser.add_argument("--out", type=Path, default=OUTPUT_PARQUET)
    args = parser.parse_args()

    if not args.raw_dir.exists():
        parser.error(f"Raw directory {args.raw_dir} does not exist")

    files = [p for p in args.raw_dir.glob("*.*") if p.suffix.lower() in (".csv", ".json")]
    if not files:
        parser.error(f"No incident feed files found in {args.raw_dir}")

    dfs = []
    for f in files:
        try:
            df = normalize(load_file(f))
            df["source_file"] = f.name
            dfs.append(df)
            print(f"Loaded {len(df)} rows from {f}")
        except Exception as e:
            print(f"Error processing {f}: {e}")

    if not dfs:
        parser.error("No valid incident feed files processed.")

    combined = pd.concat(dfs, ignore_index=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(args.out, index=False)
    print(f"SaaS incidents Parquet written to {args.out} ({len(combined)} rows)")

if __name__ == "__main__":
    main()
