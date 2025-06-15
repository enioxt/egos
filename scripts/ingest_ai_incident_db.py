#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ingest_ai_incident_db.py

Ingests AI Incident Database exports into the ATRiAN analytics pipeline.
Converts the AIID JSON format to Parquet files compatible with our schema.

Usage:
    python ingest_ai_incident_db.py --input-dir C:/EGOS/data/raw/ai_incident_db/[version] --output-dir C:/EGOS/data/processed/ai_incident_db

References:
    - ATRiAN Data Pipeline & ROI Workflow: C:/EGOS/docs/workflows/atrian_data_pipeline_roi_workflow.md
    - AIID Dataset Documentation: C:/EGOS/docs/datasets/ai_incident_db/README.md
"""
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("EGOS.ingest_ai_incident_db")

# Mapping of AIID sectors to ATRiAN sectors
SECTOR_MAPPING = {
    "transportation": "mobility",
    "automotive": "mobility",
    "aviation": "mobility",
    "manufacturing": "manufacturing",
    "industrial": "manufacturing",
    "media": "media",
    "social media": "media",
    "entertainment": "media",
    "law enforcement": "public_safety",
    "criminal justice": "public_safety",
    "healthcare": "healthcare",
    "medical": "healthcare",
    "education": "education",
    "finance": "financial",
    "banking": "financial",
    # Add more mappings as needed
    # Default will be "other"
}

def read_aiid_export(input_dir: Path) -> Dict:
    """
    Read the AIID export files from the specified directory.
    
    Args:
        input_dir: Path to the directory containing AIID export files
        
    Returns:
        Dictionary containing the loaded data from incidents.json and reports.json
    """
    incidents_path = input_dir / "incidents.json"
    reports_path = input_dir / "reports.json"
    
    if not incidents_path.exists():
        raise FileNotFoundError(f"Incidents file not found: {incidents_path}")
    if not reports_path.exists():
        raise FileNotFoundError(f"Reports file not found: {reports_path}")
    
    logger.info(f"Reading incidents from {incidents_path}")
    with open(incidents_path, "r", encoding="utf-8") as f:
        incidents = json.load(f)
    
    logger.info(f"Reading reports from {reports_path}")
    with open(reports_path, "r", encoding="utf-8") as f:
        reports = json.load(f)
    
    return {"incidents": incidents, "reports": reports}

def map_to_atrian_schema(aiid_data: Dict) -> pd.DataFrame:
    """
    Map AIID data to ATRiAN incidents schema.
    
    Args:
        aiid_data: Dictionary containing AIID incidents and reports
        
    Returns:
        DataFrame with mapped data conforming to ATRiAN schema
    """
    incidents = aiid_data["incidents"]
    reports = aiid_data["reports"]
    
    # Create a lookup for reports by incident ID
    reports_by_incident = {}
    for report in reports:
        incident_id = report.get("incident_id")
        if incident_id:
            if incident_id not in reports_by_incident:
                reports_by_incident[incident_id] = []
            reports_by_incident[incident_id].append(report)
    
    mapped_incidents = []
    
    for incident in incidents:
        incident_id = incident.get("incident_id")
        if not incident_id:
            continue
            
        # Extract incident date
        date_str = incident.get("date")
        try:
            incident_date = pd.to_datetime(date_str) if date_str else None
        except:
            incident_date = None
        
        # Determine sector from incident data and reports
        sector = determine_sector(incident, reports_by_incident.get(incident_id, []))
        
        # Estimate severity (1-3 scale)
        severity = estimate_severity(incident, reports_by_incident.get(incident_id, []))
        
        # Estimate cost (if possible)
        estimated_cost = estimate_cost(incident, reports_by_incident.get(incident_id, []))
        
        mapped_incident = {
            "incident_id": f"aiid_{incident_id}",
            "incident_date": incident_date,
            "sector": sector,
            "severity_score": severity,
            "estimated_cost_usd": estimated_cost,
            "description": incident.get("title", ""),
            "source": "AI Incident Database",
            "details": {
                "aiid_id": incident_id,
                "url": f"https://incidentdatabase.ai/cite/{incident_id}",
                "alleged_deployer": incident.get("alleged_deployer_of_ai_system", ""),
                "alleged_developer": incident.get("alleged_developer_of_ai_system", ""),
            }
        }
        
        mapped_incidents.append(mapped_incident)
    
    return pd.DataFrame(mapped_incidents)

def determine_sector(incident: Dict, reports: List[Dict]) -> str:
    """
    Determine the ATRiAN sector based on AIID incident and reports.
    
    Args:
        incident: AIID incident data
        reports: List of reports for this incident
        
    Returns:
        Mapped sector name
    """
    # Extract potential sector information from various fields
    potential_sectors = []
    
    # From incident
    if "domain" in incident and incident["domain"]:
        potential_sectors.extend(incident["domain"].lower().split(","))
    
    # From reports
    for report in reports:
        if "domain" in report and report["domain"]:
            potential_sectors.extend(report["domain"].lower().split(","))
    
    # Clean up and normalize
    potential_sectors = [s.strip() for s in potential_sectors]
    
    # Try to map to our sectors
    for sector in potential_sectors:
        if sector in SECTOR_MAPPING:
            return SECTOR_MAPPING[sector]
    
    # If no match found, try partial matching
    for sector in potential_sectors:
        for aiid_sector, atrian_sector in SECTOR_MAPPING.items():
            if sector in aiid_sector or aiid_sector in sector:
                return atrian_sector
    
    return "other"  # Default sector

def estimate_severity(incident: Dict, reports: List[Dict]) -> int:
    """
    Estimate incident severity on a 1-3 scale.
    
    Args:
        incident: AIID incident data
        reports: List of reports for this incident
        
    Returns:
        Severity score (1-3)
    """
    # This is a simplified heuristic - can be enhanced with NLP in the future
    severity_indicators = {
        "death": 3,
        "fatal": 3,
        "fatality": 3,
        "injury": 2,
        "harm": 2,
        "damage": 2,
        "discrimination": 2,
        "bias": 1,
        "error": 1,
        "mistake": 1,
    }
    
    max_severity = 1  # Default to lowest severity
    
    # Check incident title and description
    text_to_check = incident.get("title", "") + " " + incident.get("description", "")
    text_to_check = text_to_check.lower()
    
    for indicator, score in severity_indicators.items():
        if indicator in text_to_check:
            max_severity = max(max_severity, score)
    
    # Check reports too
    for report in reports:
        report_text = report.get("title", "") + " " + report.get("text", "")
        report_text = report_text.lower()
        
        for indicator, score in severity_indicators.items():
            if indicator in report_text:
                max_severity = max(max_severity, score)
    
    return max_severity

def estimate_cost(incident: Dict, reports: List[Dict]) -> Optional[float]:
    """
    Estimate incident cost in USD.
    
    Args:
        incident: AIID incident data
        reports: List of reports for this incident
        
    Returns:
        Estimated cost in USD or None if cannot be determined
    """
    # This is a placeholder - in a real implementation, we would use
    # NLP to extract cost information from text or use a more sophisticated model
    # For now, we'll return None to indicate unknown cost
    return None

def write_parquet(df: pd.DataFrame, output_dir: Path) -> Path:
    """
    Write the mapped data to a Parquet file.
    
    Args:
        df: DataFrame to write
        output_dir: Directory to write the Parquet file to
        
    Returns:
        Path to the written Parquet file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"ai_incidents_{timestamp}.parquet"
    
    logger.info(f"Writing {len(df)} incidents to {output_path}")
    df.to_parquet(output_path, index=False)
    
    # Also write a latest symlink/copy
    latest_path = output_dir / "ai_incidents_latest.parquet"
    df.to_parquet(latest_path, index=False)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Ingest AI Incident Database exports")
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory containing AIID export files"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="C:/EGOS/data/processed/ai_incident_db",
        help="Directory to write Parquet files to"
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    try:
        # Read AIID export
        aiid_data = read_aiid_export(input_dir)
        
        # Map to ATRiAN schema
        df = map_to_atrian_schema(aiid_data)
        
        # Write to Parquet
        output_path = write_parquet(df, output_dir)
        
        logger.info(f"Successfully ingested {len(df)} incidents from AIID")
        logger.info(f"Output written to {output_path}")
        
        # Print summary statistics
        logger.info("Summary statistics:")
        logger.info(f"  Total incidents: {len(df)}")
        logger.info(f"  Date range: {df['incident_date'].min()} to {df['incident_date'].max()}")
        logger.info(f"  Sectors: {df['sector'].value_counts().to_dict()}")
        logger.info(f"  Severity distribution: {df['severity_score'].value_counts().to_dict()}")
        
    except Exception as e:
        logger.error(f"Error ingesting AIID data: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
