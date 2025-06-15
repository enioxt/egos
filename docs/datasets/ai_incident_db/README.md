# AI Incident Database (AIID) Dataset

## Overview
The AI Incident Database (AIID) is a collection of real-world AI incidents, failures, and near-misses that have been reported in the public domain. This dataset provides valuable insights into the types of incidents that occur with AI systems across various sectors, their impacts, and the responses to them.

## Source Information
- **Provider**: Partnership on AI (PAI)
- **Website**: [https://incidentdatabase.ai/](https://incidentdatabase.ai/)
- **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Latest Backup URL**: [https://pub-a5fe3e44369c4cabb576fa0d2c09fdf6.r2.dev/backup-YYYYMMDDHHMMSS.tar.bz2](https://pub-a5fe3e44369c4cabb576fa0d2c09fdf6.r2.dev/backup-YYYYMMDDHHMMSS.tar.bz2) (Replace YYYYMMDDHHMMSS with the latest date)

## Data Structure
The AIID export contains several JSON files, with the primary ones being:
- `incidents.json`: Core incident information including ID, title, description, date, and domain
- `reports.json`: Reports associated with incidents, containing detailed information and analysis

## Integration with ATRiAN Analytics Pipeline
This dataset is integrated into the ATRiAN analytics pipeline through the following process:
1. Download and extract the latest AIID backup to `C:\EGOS\data\raw\ai_incident_db\`
2. Process using `scripts\ingest_ai_incident_db.py` to convert to Parquet format
3. Output stored in `C:\EGOS\data\processed\ai_incident_db\ai_incidents_latest.parquet`
4. Integrated into the ROI pipeline via `scripts\roi_prepare_data.py`
5. Visualized in the ATRiAN dashboard with source attribution

## Schema Mapping
The AIID data is mapped to the ATRiAN incidents schema as follows:

| AIID Field | ATRiAN Field | Notes |
|------------|--------------|-------|
| incident_id | incident_id | Prefixed with "aiid_" |
| date | incident_date | Converted to datetime |
| domain | sector | Mapped to ATRiAN sectors (mobility, manufacturing, etc.) |
| title | description | Used as incident description |
| N/A | severity_score | Derived from text analysis (1-3 scale) |
| N/A | estimated_cost_usd | Currently null, future enhancement |
| N/A | source | Set to "AI Incident Database" |

## Sector Mapping
The following mappings are used to convert AIID domains to ATRiAN sectors:
- transportation, automotive, aviation → mobility
- manufacturing, industrial → manufacturing
- media, social media, entertainment → media
- law enforcement, criminal justice → public_safety
- healthcare, medical → healthcare
- education → education
- finance, banking → financial

## Usage Notes
- The AIID data provides real-world incidents that complement ATRiAN's internal incident data
- Sector-based analysis is enhanced by the broader coverage of the AIID
- The severity scoring is derived using a simple keyword-based heuristic and may be refined in future versions

## References
- [ATRiAN Data Pipeline & ROI Workflow](C:/EGOS/docs/workflows/atrian_data_pipeline_roi_workflow.md)
- [AI Incident Database Implementation Plan](C:/EGOS/docs/implementation_plans/ai_incident_db_ingestion_plan.md)
- [AIID Research Paper](https://arxiv.org/abs/2011.08512) - "The AI Incident Database: Using collective incident reporting to improve safety outcomes in AI"

## Changelog
- 2025-06-15: Initial documentation created
- 2025-06-15: Integration with ROI pipeline implemented
- 2025-06-15: Dashboard visualization updated to show data source