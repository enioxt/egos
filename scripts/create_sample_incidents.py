import pandas as pd
import numpy as np
from pathlib import Path

"""Synthetic Incident Generator

Generates a synthetic incidents dataset compatible with the ATRiAN pipeline.

Features:
• CLI parameters for record count & output root
• Writes Parquet file as <root>/synthetic_<YYYYMMDDHHMMSS>/incidents.parquet
• Adds `source` column = "synthetic"
• Reuses sector list from ATRiAN taxonomy
"""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

SECTORS: List[str] = [
    "mobility",
    "manufacturing",
    "media",
    "public_safety",
    "healthcare",
    "financial",
    "education",
]

INCIDENT_TYPES = ["safety", "bias", "privacy", "technical", "ethical"]


def _random_date(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between `start` and `end`."""
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_synthetic_incidents(count: int = 500) -> pd.DataFrame:
    """Generate a DataFrame with synthetic incident records."""
    rng = np.random.default_rng(seed=42)

    today = datetime.utcnow()
    start_date = today - timedelta(days=730)  # last two years

    records = []
    for i in range(1, count + 1):
        incident_date = _random_date(start_date, today)
        records.append(
            {
                "incident_id": f"SYN-{i:06d}",
                "estimated_cost_usd": int(rng.choice([10_000, 25_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000])),
                "severity_score": int(rng.choice([1, 2, 3], p=[0.6, 0.3, 0.1])),
                "sector": rng.choice(SECTORS).item(),
                "incident_date": pd.Timestamp(incident_date),
                "incident_type": rng.choice(INCIDENT_TYPES).item(),
                "resolution_time_days": int(rng.integers(1, 90)),
                "affected_users": int(rng.integers(0, 100_000)),
                "source": "synthetic",
            }
        )

    return pd.DataFrame.from_records(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic incidents for ATRiAN.")
    parser.add_argument("--count", type=int, default=500, help="Number of incidents to generate (default: 500).")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(r"C:/EGOS/data/processed"),
        help="Root directory where synthetic dataset folder will be created.",
    )

    args = parser.parse_args()

    df = generate_synthetic_incidents(args.count)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    out_dir = args.output_root / f"synthetic_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "incidents.parquet"
    df.to_parquet(out_path, index=False)

    latest_path = args.output_root / "synthetic_latest.parquet"
    df.to_parquet(latest_path, index=False)

    print(f"[Synthetic Generator] Wrote {len(df)} incidents to {out_path}")
    print(f"Latest copy: {latest_path}")


if __name__ == "__main__":
    main()

def create_sample_incidents(output_path):
    # Define sectors from our YAML files
    sectors = ["mobility", "manufacturing", "media", "public_safety", "healthcare", "financial", "education"]
    
    # Create synthetic data
    np.random.seed(42)  # For reproducibility
    
    # Generate 100 incident records
    data = {
        'incident_id': [f'INC-{i:05d}' for i in range(1, 101)],
        'estimated_cost_usd': np.random.choice([10000, 25000, 50000, 100000, 500000, 1000000, 5000000, 10000000], 100),
        'severity_score': np.random.choice([1, 2, 3], 100, p=[0.6, 0.3, 0.1]),  # 1=low, 2=medium, 3=high
        'sector': np.random.choice(sectors, 100),
        'incident_date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'incident_type': np.random.choice(['safety', 'bias', 'privacy', 'technical', 'ethical'], 100),
        'resolution_time_days': np.random.randint(1, 90, 100),
        'affected_users': np.random.randint(0, 100000, 100)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Parquet
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    
    print(f"Created sample incidents dataset with {len(df)} records at {output_path}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nSample data:\n{df.head(3).to_string()}")
    
    return df

if __name__ == "__main__":
    # Create in data/roi directory
    output_path = "data/roi/sample_incidents.parquet"
    create_sample_incidents(output_path)
