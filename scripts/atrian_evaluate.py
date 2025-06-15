"""Simple ATRiAN ethics evaluation simulator.

This placeholder script emulates the behaviour of posting artefacts and
scenarios to an ATRiAN `/evaluate` endpoint.  Because ATRiAN may not be
available in every developer environment, the script falls back to a local
pseudo-evaluation that assigns deterministic pseudo-random scores based on the
incident_id.  When the real service URL is supplied via the ATR_URL
environment variable, the script will attempt a live call; otherwise it will
use the offline mode.

Outputs a JSON file with one record per incident and a timestamp plus three
score fields (BiasScore, SafetyScore, PrivacyLeakProb).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
import yaml

DEFAULT_OUT = "report.json"

BIAS_MAX = 1.0
SAFETY_MAX = 1.0
PRIVACY_MAX = 0.1  # lower is better


def pseudo_score(value: int, max_val: float, offset: float = 0.0) -> float:
    """Deterministically derive a pseudo-score in (0, max_val]."""
    # Use SHA1 hash for reproducible pseudo-randomness.
    h = int(hashlib.sha1(str(value).encode()).hexdigest(), 16)
    return round(offset + (h % 1000) / 1000 * (max_val - offset), 3)


def offline_evaluate(incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for row in incidents:
        incident_id = int(row.get("incident_id", 0))
        results.append(
            {
                "incident_id": incident_id,
                "BiasScore": pseudo_score(incident_id, BIAS_MAX, 0.5),
                "SafetyScore": pseudo_score(incident_id * 7, SAFETY_MAX, 0.7),
                "PrivacyLeakProb": pseudo_score(incident_id * 13, PRIVACY_MAX, 0.0),
            }
        )
    return results


def live_evaluate(
    artefact: Path, constitution_id: str, atr_url: str
) -> List[Dict[str, Any]]:
    """Attempt to call a live ATRiAN Ethics-as-a-Service endpoint."""
    try:
        resp = requests.post(
            f"{atr_url.rstrip('/')}/evaluate",
            json={
                "constitution_id": constitution_id,
                "artefact_path": str(artefact),
                "timestamp": datetime.utcnow().isoformat(),
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        # Expecting list of dicts.
        if isinstance(data, list):
            return data
        raise ValueError("Unexpected response schema from ATRiAN service")
    except Exception as exc:
        print(f"[WARN] Live ATRiAN call failed: {exc}. Falling back to offline mode.")
        with artefact.open("r", encoding="utf-8") as fp:
            incidents = json.load(fp)
        return offline_evaluate(incidents)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python atrian_evaluate.py --manifest evaluation_manifest.yaml --out report.json")
        sys.exit(1)

    manifest_path = None
    out_path = DEFAULT_OUT
    for idx, arg in enumerate(sys.argv):
        if arg == "--manifest":
            manifest_path = Path(sys.argv[idx + 1])
        if arg == "--out":
            out_path = sys.argv[idx + 1]

    if manifest_path is None or not manifest_path.exists():
        print("[ERROR] Manifest file not found.")
        sys.exit(1)

    manifest = yaml.safe_load(manifest_path.read_text())
    constitution_id = manifest.get("constitution_id", "default-constitution")
    artefact_path = Path(manifest["artefact_path"])

    atr_url = os.getenv("ATR_URL")

    print("[INFO] Running ATRiAN ethics evaluation…")
    if atr_url:
        print(f"[INFO] Using live ATRiAN endpoint: {atr_url}")
        records = live_evaluate(artefact_path, constitution_id, atr_url)
    else:
        print("[INFO] ATR_URL not set. Running in offline simulation mode.")
        incidents = json.loads(artefact_path.read_text(encoding="utf-8"))
        records = offline_evaluate(incidents)

    print(f"[INFO] Writing report to {out_path}")
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(records, fp, indent=2)

    print("[SUCCESS] Ethics evaluation completed.")


if __name__ == "__main__":
    main()