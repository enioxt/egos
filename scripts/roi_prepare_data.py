"""Prepares master incident data for ROI analysis.

Reads all 'incidents.parquet' files from subdirectories in 'data/processed/',
concatenates them, assigns a randomly generated 'estimated_cost_usd', **passes through rich
contextual fields such as `title`, `description`, `date`, `sector` (if present),** and derives a
simple ordinal `severity_score` (3 =fatalities, 2 = bodily/serious harm or systemic discrimination,
1 = reputational/financial only).  The enriched dataset is written to
`data/roi/master_incidents.parquet` and becomes an input to downstream ROI and case-study analyses.
"""
from __future__ import annotations

import random
from pathlib import Path
import pandas as pd

PROCESSED_DATA_DIR = Path(r"C:\EGOS\data\processed")
ROI_DATA_DIR = Path(r"C:\EGOS\data\roi")
OUTPUT_PARQUET = ROI_DATA_DIR / "master_incidents.parquet"

def main():
    ROI_DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42) # For reproducible random cost generation

    all_incidents_dfs = []
    processed_folders = [f for f in PROCESSED_DATA_DIR.iterdir() if f.is_dir()]

    if not processed_folders:
        print(f"No processed data folders found in {PROCESSED_DATA_DIR}.")
        return
        
    # Check for AI Incident Database data
    aiid_path = PROCESSED_DATA_DIR / "ai_incident_db" / "ai_incidents_latest.parquet"
    if aiid_path.exists():
        print(f"Reading AI Incident Database data from {aiid_path}")
        try:
            aiid_df = pd.read_parquet(aiid_path)
            if not aiid_df.empty:
                # Ensure required columns are present
                required_columns = ["incident_id", "sector", "severity_score"]
                if all(col in aiid_df.columns for col in required_columns):
                    all_incidents_dfs.append(aiid_df)
                    print(f"Added {len(aiid_df)} incidents from AI Incident Database")
                else:
                    print(f"Warning: AI Incident Database data missing required columns: {required_columns}")
            else:
                print(f"Warning: {aiid_path} is empty.")
        except Exception as e:
            print(f"Error reading {aiid_path}: {e}")

    # ------------------------------------------------------------------
    # Additional source: SaaS provider incidents (processed separately)
    # ------------------------------------------------------------------
    saas_incidents_path = Path(r"C:\EGOS\data\processed\saas_incidents\saas_incidents.parquet")
    if saas_incidents_path.exists():
        try:
            saas_df = pd.read_parquet(saas_incidents_path)
            if not saas_df.empty:
                all_incidents_dfs.append(saas_df)
                print(f"Added {len(saas_df)} SaaS provider incidents")
        except Exception as e:
            print(f"Error reading {saas_incidents_path}: {e}")

    # Process other incident data sources
    for folder in processed_folders:
        incident_parquet_path = folder / "incidents.parquet"
        if incident_parquet_path.exists():
            print(f"Reading {incident_parquet_path}")
            try:
                df = pd.read_parquet(incident_parquet_path)
                if not df.empty:
                    all_incidents_dfs.append(df)
                else:
                    print(f"Warning: {incident_parquet_path} is empty.")
            except Exception as e:
                print(f"Error reading {incident_parquet_path}: {e}")
        else:
            print(f"Warning: {incident_parquet_path} not found in {folder}.")


    if not all_incidents_dfs:
        print("No incident data found to process.")
        return

    master_incidents_df = pd.concat(all_incidents_dfs, ignore_index=True)

    # Generate estimated_cost_usd if it doesn't exist or to ensure consistency
    # This replicates the logic from the previous script version.
    # Ensure 'incident_id' exists, if not, try to use '_id' or generate one.
    if 'incident_id' not in master_incidents_df.columns:
        if '_id' in master_incidents_df.columns:
            master_incidents_df['incident_id'] = master_incidents_df['_id'].astype(str)
        else:
            # If no suitable ID column, we might need to generate one or raise an error
            # For now, let's assume one of them will be present from BSON conversion.
            print("Error: Neither 'incident_id' nor '_id' found in the concatenated data.")
            # Fallback: generate a temporary ID if absolutely necessary, though not ideal
            # master_incidents_df['incident_id'] = [f"gen_id_{i}" for i in range(len(master_incidents_df))]
            # return # Or handle error more gracefully

    master_incidents_df["estimated_cost_usd"] = [
        rng.randint(100_000, 2_000_000) for _ in range(len(master_incidents_df))
    ]
    
    # Select and reorder columns for the final output, ensuring incident_id is present
    final_columns = ['incident_id', 'estimated_cost_usd']
    # Add other relevant columns from the source, if they exist, avoiding duplicates
    for col in master_incidents_df.columns:
        if col not in final_columns:
            final_columns.append(col)
    
    # ------------------------------------------------------------------
    # Derive a coarse severity score from free-text fields
    # ------------------------------------------------------------------
    def _score(row: pd.Series) -> int:
        text = f"{row.get('title','')} {row.get('description','')}".lower()
        fatal_kw = ("kill", "death", "fatal", "crush", "pedestrian", "dead")
        harm_kw = ("injur", "harm", "bias", "discrimin", "child", "kid", "exploit")
        if any(k in text for k in fatal_kw):
            return 3
        if any(k in text for k in harm_kw):
            return 2
        return 1
    master_incidents_df["severity_score"] = master_incidents_df.apply(_score, axis=1)

    # ------------------------------------------------------------------
    # Preserve important context columns when available
    # ------------------------------------------------------------------
    context_cols = [c for c in [
        "title",
        "description",
        "date",
        "sector",  # may be absent – kept if future ingestion populates it
    ] if c in master_incidents_df.columns]

    final_columns = ['incident_id', 'severity_score', 'estimated_cost_usd'] + context_cols
    # Append any other original columns (excluding duplicates)
    for col in master_incidents_df.columns:
        if col not in final_columns:
            final_columns.append(col)

    master_incidents_df = master_incidents_df[final_columns]

    try:
        master_incidents_df.to_parquet(OUTPUT_PARQUET, index=False)
        print(f"Wrote master incident data ({len(master_incidents_df)} rows) to {OUTPUT_PARQUET}")
    except Exception as e:
        print(f"Error writing Parquet file to {OUTPUT_PARQUET}: {e}")

if __name__ == "__main__":
    main()