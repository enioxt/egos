"""Very lightweight Monte Carlo ROI simulation.

This is a minimal placeholder to support the ATRIAN ROI workflow until the full
financial model is implemented.  It randomly samples incident costs and applies
assumed mitigation percentages to estimate benefits, then subtracts costs.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import List
import pandas as pd
import yaml
from datetime import datetime


def load_incident_costs_from_parquet(path: Path) -> pd.DataFrame:
    """Loads incident data including 'estimated_cost_usd' and 'severity_score' from a Parquet file."""
    try:
        df = pd.read_parquet(path)
        if "estimated_cost_usd" not in df.columns:
            raise ValueError("'estimated_cost_usd' column not found in Parquet file.")
        
        # Ensure minimum required columns exist
        if not df.shape[0]:
            raise ValueError("No data found in Parquet file.")
            
        # Ensure severity_score exists or default to 1
        if "severity_score" not in df.columns:
            df["severity_score"] = 1
            print("Warning: 'severity_score' column not found. Using default value 1.")
        
        # Ensure sector column exists or add default
        if "sector" not in df.columns:
            df["sector"] = "unknown"
            print("Warning: 'sector' column not found. Using 'unknown' as default sector.")
            
        return df[['estimated_cost_usd', 'severity_score', 'sector']]
    except Exception as e:
        print(f"Error loading incident costs from {path}: {e}")
        # Return an empty list or re-raise, depending on desired error handling
        return []


def run_simulation(df_incidents: pd.DataFrame, model: dict, vendor_costs_total: float = 0.0, runs: int = 1000):
    """Run Monte Carlo ROI simulation with severity-aware risk mitigation.
    
    Args:
        df_incidents: DataFrame with incidents data including costs, severity scores, and sectors
        model: ROI model parameters including cost components and value drivers
        runs: Number of simulation runs
        
    Returns:
        Dictionary with simulation results including ROI and sector-specific metrics
    """
    if df_incidents.empty:
        print("Warning: No incident data provided to simulation. ROI will be inaccurate.")
        # Return error structure with basic cost calculation
        return {
            "average_avoided_cost": 0,
            "total_costs": model["cost_components"].get("atrian_subscription_annual", 0) + 
                           model["cost_components"].get("integration_hours", 0) * model["cost_components"].get("engineer_hour_cost", 0) + 
                           model["cost_components"].get("evaluation_compute_per_year", 0),
            "roi_pct": -100, # Indicates total loss if costs are present and benefits are zero
            "error": "No incident cost data available for simulation"
        }
    
    # Extract needed columns as lists for faster sampling
    costs = df_incidents['estimated_cost_usd'].astype(int).tolist()
    severity_scores = df_incidents['severity_score'].astype(float).tolist()
    sectors = df_incidents['sector'].tolist()
    incident_indices = list(range(len(costs)))
    
    # Base risk mitigation percentage from model
    base_mitigation_perc = model["value_drivers"]["risk_mitigation_perc"]
    
    # Get sector-specific risk mitigation multipliers if available, otherwise use default of 1.0
    sector_multipliers = model.get("sector_risk_mitigation_multipliers", {})
    
    rng = random.Random(42)  # Fixed seed for reproducibility
    
    # Store results for overall and per-sector analysis
    avoided_costs = []
    sector_costs = {}
    
    for _ in range(runs):
        # Randomly select an incident
        idx = rng.choice(incident_indices)
        incident_cost = costs[idx]
        severity = severity_scores[idx]
        sector = sectors[idx]
        
        # Apply severity scaling to risk mitigation percentage
        # Severity 1 = base mitigation, severity 2 = 1.5x, severity 3 = 2x
        severity_multiplier = 0.5 * (severity + 1)  # Maps 1→1.0, 2→1.5, 3→2.0
        
        # Apply sector-specific multiplier if available
        sector_multiplier = sector_multipliers.get(sector, 1.0)
        
        # Calculate final mitigation percentage with both severity and sector factors
        effective_mitigation = base_mitigation_perc * severity_multiplier * sector_multiplier
        
        # Cap at 0.95 (95%) to avoid unrealistic perfect mitigation
        effective_mitigation = min(effective_mitigation, 0.95)
        
        # Calculate avoided cost
        avoided = incident_cost * effective_mitigation
        avoided_costs.append(avoided)
        
        # Track per-sector costs
        if sector not in sector_costs:
            sector_costs[sector] = []
        sector_costs[sector].append(avoided)
    
    # Calculate overall average
    avg_avoided_incidents = sum(avoided_costs) / len(avoided_costs)

    # ------------------------------------------------------------------
    # Vendor-cost savings (static, not Monte Carlo)
    # ------------------------------------------------------------------
    vendor_savings_perc = model["value_drivers"].get("vendor_cost_reduction_perc", 0)
    avoided_vendor_costs = vendor_costs_total * vendor_savings_perc

    # Combine benefits
    total_avoided = avg_avoided_incidents + avoided_vendor_costs

    annual_subscription = model["cost_components"]["atrian_subscription_annual"]
    integration_hours = model["cost_components"]["integration_hours"]
    engineer_rate = model["cost_components"]["engineer_hour_cost"]
    integration_cost = integration_hours * engineer_rate
    compute = model["cost_components"]["evaluation_compute_per_year"]

    total_costs = annual_subscription + integration_cost + compute
    
    # Avoid division by zero if total_costs is 0
    roi_pct = ((total_avoided - total_costs) / total_costs * 100) if total_costs else float('-inf') 
    
    # Prepare sector-specific results
    sector_results = {}
    for sector, avoided_list in sector_costs.items():
        if avoided_list:
            sector_avg = sum(avoided_list) / len(avoided_list)
            sector_roi = ((sector_avg - (total_costs / len(sector_costs))) / (total_costs / len(sector_costs)) * 100) if total_costs else float('-inf')
            sector_results[sector] = {
                "average_avoided_cost": sector_avg,
                "roi_pct": sector_roi,
                "incident_count": len(avoided_list),
                "sector_mitigation_multiplier": model.get("sector_risk_mitigation_multipliers", {}).get(sector, 1.0)
            }
    
    return {
        "average_avoided_incident_cost": avg_avoided_incidents,
        "avoided_vendor_costs": avoided_vendor_costs,
        "total_avoided_benefit": total_avoided,
        "total_costs": total_costs,
        "roi_pct": roi_pct,
        "sectors": sector_results,
        "simulation_metadata": {
            "runs": runs,
            "severity_scaling_enabled": True,
            "sector_scaling_enabled": bool(model.get("sector_risk_mitigation_multipliers"))
        }
    }


def load_vendor_costs(path: Path) -> float:
    """Return total annual vendor costs based on CSV ingestion output.
    For simplicity, sum annual_cost_usd for all rows whose start_date is in past.
    """
    if not path.exists():
        return 0.0
    try:
        df = pd.read_parquet(path)
        if "annual_cost_usd" not in df.columns:
            return 0.0
        # basic filter: contracts already started (ignore future)
        today = datetime.utcnow().date()
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce").dt.date
        df_valid = df[df["start_date"] <= today]
        return float(df_valid["annual_cost_usd"].sum())
    except Exception as e:
        print(f"Error loading vendor costs from {path}: {e}")
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="Run Monte Carlo ROI simulation using Parquet incident data.")
    parser.add_argument("--model", required=True, help="Path to the YAML model file for ROI calculation.")
    parser.add_argument("--runs", type=int, default=1000, help="Number of simulation runs.")
    parser.add_argument("--out", required=True, help="Path to save the JSON output report.")
    parser.add_argument("--vendor-costs", type=Path, default=Path(r"C:\EGOS\data\processed\vendor_costs\vendor_costs.parquet"), help="Path to vendor costs Parquet file.")
    parser.add_argument("--incidents_data", type=Path, default=Path(r"C:\EGOS\data\roi\master_incidents.parquet"), help="Path to the master incidents Parquet file.")
    parser.add_argument("--by-sector", action="store_true", help="Enable detailed per-sector ROI analysis in output")
    args = parser.parse_args()

    df_incidents = load_incident_costs_from_parquet(args.incidents_data)
    vendor_costs_total = load_vendor_costs(args.vendor_costs)
    
    if isinstance(df_incidents, list) or df_incidents.empty:
        print(f"Could not load incident data from {args.incidents_data}. Aborting simulation.")
        # Write an error report to args.out
        error_report = {"error": f"Failed to load incident data from {args.incidents_data}"}
        Path(args.out).write_text(json.dumps(error_report, indent=2), encoding="utf-8")
        return

    try:
        model = yaml.safe_load(Path(args.model).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading ROI model from {args.model}: {e}")
        error_report = {"error": f"Failed to load ROI model from {args.model}: {e}"}
        Path(args.out).write_text(json.dumps(error_report, indent=2), encoding="utf-8")
        return
    
    # Check if we have sector-specific risk multipliers; if not and we're using by-sector,
    # add a default multiplier of 1.0 for each sector in the data
    if args.by_sector and "sector_risk_mitigation_multipliers" not in model:
        unique_sectors = df_incidents["sector"].unique().tolist()
        model["sector_risk_mitigation_multipliers"] = {sector: 1.0 for sector in unique_sectors}
        print(f"Added default sector multipliers (1.0) for {len(unique_sectors)} sectors")

    result = run_simulation(df_incidents, model, vendor_costs_total=vendor_costs_total, runs=args.runs)
    try:
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"ROI simulation written to {args.out}")
    except Exception as e:
        print(f"Error writing simulation output to {args.out}: {e}")


if __name__ == "__main__":
    main()