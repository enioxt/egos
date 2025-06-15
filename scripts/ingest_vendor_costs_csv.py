"""Ingest vendor cost CSVs and convert to Parquet for ROI analysis.

Expected input directory structure:
  C:\EGOS\data\raw\vendor_costs\*.csv
Each CSV must contain at minimum:
  - vendor (str): vendor name
  - annual_cost_usd (float/int): yearly subscription or license cost
  - start_date (YYYY-MM-DD)
  - end_date (optional) or term_months (int)

Output:
  Consolidated Parquet file written to
  C:\EGOS\data\processed\vendor_costs\vendor_costs.parquet

This script is intentionally simple – it trusts column names and types.
If CSV columns differ, provide a --columns-map JSON argument to rename.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

RAW_DIR_DEFAULT = Path(r"C:\EGOS\data\raw\vendor_costs")
PROCESSED_DIR = Path(r"C:\EGOS\data\processed\vendor_costs")
OUTPUT_PARQUET = PROCESSED_DIR / "vendor_costs.parquet"

REQUIRED_COLUMNS = {"vendor", "annual_cost_usd", "start_date"}


def load_and_normalize_csv(path: Path, columns_map: dict[str, str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    if columns_map:
        df = df.rename(columns=columns_map)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV {path} missing required columns: {missing}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Ingest vendor cost CSVs to Parquet")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR_DEFAULT, help="Directory containing vendor cost CSV files")
    parser.add_argument("--columns-map", type=str, help="Optional JSON mapping of column names in CSV to required names")
    parser.add_argument("--out", type=Path, default=OUTPUT_PARQUET, help="Path to output Parquet file")
    args = parser.parse_args()

    if args.columns_map:
        try:
            columns_map = json.loads(args.columns_map)
        except json.JSONDecodeError as e:
            parser.error(f"Invalid JSON for --columns-map: {e}")
    else:
        columns_map = None

    raw_dir: Path = args.raw_dir
    if not raw_dir.exists():
        parser.error(f"Raw directory {raw_dir} does not exist")

    csv_files = list(raw_dir.glob("*.csv"))
    if not csv_files:
        parser.error(f"No CSV files found in {raw_dir}")

    dataframes = []
    for csv_path in csv_files:
        try:
            df = load_and_normalize_csv(csv_path, columns_map)
            df["source_file"] = csv_path.name
            dataframes.append(df)
            print(f"Loaded {len(df)} rows from {csv_path}")
        except Exception as e:
            print(f"Error loading {csv_path}: {e}")

    if not dataframes:
        parser.error("No valid CSV files processed – aborting")

    combined = pd.concat(dataframes, ignore_index=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(args.out, index=False)
    print(f"Vendor costs Parquet written to {args.out} ({len(combined)} rows)")


if __name__ == "__main__":
    main()
