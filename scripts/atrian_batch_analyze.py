"""Batch analysis of AI Incident backups for ATRiAN ethics evaluation + ROI.

Usage:
    python atrian_batch_analyze.py --backup C:\path\to\backup_dir \
        --out C:\EGOS\ATRIAN\reports

Outputs per-backup sub-folders with:
    ethics.json  – per-incident risk scores
    roi.json     – per-incident ROI estimates
    summary.md   – human-readable markdown summary
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# --- Ethics evaluation (import from atrian_evaluate) -------------------------

try:
    from scripts.atrian_evaluate import offline_evaluate  # type: ignore
except ImportError:
    # Fallback if relative import fails
    from atrian_evaluate import offline_evaluate  # type: ignore

# ---------------------------------------------------------------------------
RISK_MITIGATION_PERC = 0.15  # 15 % avoided cost per incident


def load_incidents(csv_path: Path) -> List[Dict[str, Any]]:
    return pd.read_csv(csv_path).to_dict(orient="records")


def estimate_costs(incidents: List[Dict[str, Any]]) -> Dict[int, int]:
    rng = random.Random(42)
    costs: Dict[int, int] = {}
    for row in incidents:
        iid = int(row["incident_id"])
        costs[iid] = rng.randint(100_000, 2_000_000)
    return costs


def compute_roi(costs: Dict[int, int]) -> Dict[int, float]:
    roi: Dict[int, float] = {}
    for iid, cost in costs.items():
        avoided = cost * RISK_MITIGATION_PERC
        total_costs = 64_600  # placeholder static annual cost
        roi[iid] = (avoided - total_costs) / total_costs * 100
    return roi


def write_markdown(
    out_dir: Path, ethics: List[Dict[str, Any]], roi: Dict[int, float]
):
    md = ["# ATRiAN Batch Analysis", "", f"Generated: {datetime.utcnow().isoformat()}", ""]
    md.append("| Incident | Bias | Safety | PrivacyLeak | ROI % |\n|---|---|---|---|---|")
    for rec in ethics:
        iid = rec["incident_id"]
        md.append(
            f"| {iid} | {rec['BiasScore']:.3f} | {rec['SafetyScore']:.3f} | {rec['PrivacyLeakProb']:.3f} | {roi[iid]:.1f} |"
        )
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backup", required=True, help="Path to backup directory")
    ap.add_argument("--out", required=True, help="Base output directory")
    args = ap.parse_args()

    backup_dir = Path(args.backup)
    out_base = Path(args.out)
    label = backup_dir.name
    out_dir = out_base / label
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    incidents_csv = backup_dir / "mongodump_full_snapshot" / "incidents.csv"
    if not incidents_csv.exists():
        raise FileNotFoundError(incidents_csv)

    incidents = load_incidents(incidents_csv)
    ethics = offline_evaluate(incidents)
    (out_dir / "ethics.json").write_text(json.dumps(ethics, indent=2), encoding="utf-8")

    costs = estimate_costs(incidents)
    roi = compute_roi(costs)
    (out_dir / "roi.json").write_text(json.dumps(roi, indent=2), encoding="utf-8")

    write_markdown(out_dir, ethics, roi)
    print(f"Analysis written to {out_dir}")


if __name__ == "__main__":
    main()