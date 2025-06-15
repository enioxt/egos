# ATRiAN Data Ingestion and ROI Simulation Workflow

**Version:** 1.0
**Date:** {{ CURRENT_DATE_ISO }}

## 1. Overview

This document describes the automated workflow for ingesting raw ATRiAN MongoDB backup data (BSON format), processing it into an analysis-ready format (Parquet), and running a Return on Investment (ROI) simulation based on this data. The primary goal is to provide a quantitative measure of ATRiAN's value by analyzing historical incident data.

This pipeline operates without requiring a live MongoDB server instance for ingestion.

## 2. Data Flow Diagram (Conceptual)

```mermaid
graph TD
    A[Raw MongoDB Backups<br>(data/raw/mongo_backups/<backup_slug>/*.bson)] --> B(ingest_mongo_backups_bson.py);
    B --> C{Processed Data<br>(data/processed/<backup_slug>/<collection>.parquet)};
    B --> D[Archived Raw Backups<br>(data/raw/mongo_backups/archived/)];
    C --> E(roi_prepare_data.py);
    E --> F[Master Incidents Data<br>(data/roi/master_incidents.parquet)];
    G[ROI Financial Model<br>(data/roi/default_roi_model.yaml)] --> H(roi_simulate.py);
    F --> H;
    H --> I[ROI Simulation Results<br>(data/roi/latest_roi.json)];
```

## 3. Key Scripts and Execution

### 3.0 Quick-Start: Integrating AI Incident Database (AIID)  
For analysts who only need to bring the public AI Incident Database (AIID) into the pipeline and visual dashboard, follow **these four steps**:

| # | Action | Example Command |
|---|--------|-----------------|
| 1 | **Download** latest AIID backup to `C:\EGOS\data\raw\ai_incident_db\` | `Invoke-WebRequest -Uri https://pub-a5fe.../backup-20250609100613.tar.bz2 -OutFile backup.tar.bz2` |
| 2 | **Extract** archive (tar.bz2) into a versioned sub-folder | `tar -xjf backup.tar.bz2 -C C:\EGOS\data\raw\ai_incident_db\20250609` |
| 3 | **Ingest** JSON → Parquet  | `python scripts\ingest_ai_incident_db.py --input-dir C:\EGOS\data\raw\ai_incident_db\20250609` |
| 4 | **Refresh ROI pipeline** (prepare + simulate) | ```powershell
python scripts\roi_prepare_data.py
python scripts\roi_simulate.py
``` |

At this point the **Streamlit dashboard** will automatically surface AIID incidents (labelled *AI Incident Database*) next time you run:

```powershell
cd C:\EGOS\apps\dashboard\core
streamlit run streamlit_app.py
```

Full rationale, data mappings, and test strategy are described in  
`docs/implementation_plans/ai_incident_db_ingestion_plan.md` (cross-referenced so it will surface in global search).


All scripts are located in `C:\EGOS\scripts\`.

### 3.1. `ingest_mongo_backups_bson.py`

*   **Purpose:** Ingests raw BSON files from individual MongoDB backup folders, converts specified collections to Parquet format, generates a manifest, and archives the raw backup.
*   **Input:** Raw BSON dump folders in `C:\EGOS\data\raw\mongo_backups\`.
*   **Output:** Parquet files (e.g., `incidents.parquet`) and `manifest.json` in `C:\EGOS\data\processed\<backup_slug>\`.
*   **Archiving:** Moves processed raw backup folders to `C:\EGOS\data\raw\mongo_backups\archived\`.
*   **Key Collections Processed:** `incidents` (others like `cost_reports`, `users` can be added if present and needed).
*   **Execution (from `C:\EGOS\`):
    ```bash
    python scripts/ingest_mongo_backups_bson.py
    ```

### 3.2. `roi_prepare_data.py`

*   **Purpose:** Consolidates all `incidents.parquet` files from the `data/processed/` subdirectories into a single master incidents Parquet file. It also generates an `estimated_cost_usd` for each incident if not already present (currently uses random generation for consistency with previous versions).
*   **Input:** `incidents.parquet` files located in `C:\EGOS\data\processed\*\`.
*   **Output:** `C:\EGOS\data\roi\master_incidents.parquet`.
*   **Execution (from `C:\EGOS\`):
    ```bash
    python scripts/roi_prepare_data.py
    ```

### 3.3. `roi_simulate.py`

*   **Purpose:** Performs a Monte Carlo simulation to estimate ROI based on the master incident data and a financial model.
*   **Input:** 
    *   Master incidents data: `C:\EGOS\data\roi\master_incidents.parquet` (can be overridden with `--incidents_data` argument).
    *   ROI financial model: A YAML file (e.g., `C:\EGOS\data\roi\default_roi_model.yaml`) specified via the `--model` argument.
*   **Output:** ROI simulation results in JSON format, specified via the `--out` argument (e.g., `C:\EGOS\data\roi\latest_roi.json`).
*   **Execution (from `C:\EGOS\`):
    ```bash
    python scripts/roi_simulate.py --model C:\EGOS\data\roi\default_roi_model.yaml --out C:\EGOS\data\roi\latest_roi.json
    ```

### 3.4. Phase-2 External Data Ingestion

| # | Script | Purpose |
|---|--------|---------|
| 1 | `scripts/ingest_vendor_costs_csv.py` | Converts raw vendor-subscription CSVs to Parquet for ROI modelling. |
| 2 | `scripts/ingest_saas_incidents.py`  | Normalises SaaS provider outage feeds (CSV/JSON) into Parquet. |
| 3 | `scripts/run_roi_pipeline_phase2.ps1` | One-shot orchestration that runs both ingestions, refreshes master incidents, runs `roi_simulate.py`, and prints a summary. |

**Sample usage**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_roi_pipeline_phase2.ps1
```

The default ROI model (`data/roi/default_roi_model.yaml`) now includes:
* `vendor_cost_reduction_perc` – expected % savings on SaaS spend
* `third_party_monitoring` – baseline cost to potentially replace

`roi_simulate.py` automatically:
1. Loads total annual vendor spend from `processed/vendor_costs/vendor_costs.parquet`.
2. Computes avoided SaaS spend = vendor_costs × vendor_cost_reduction_perc.
3. Adds this to incident-cost savings to determine overall benefit.

---

## 4. Directory Structure (Key Paths)

*   `C:\EGOS\data\raw\mongo_backups\`: Location for new, unprocessed MongoDB backup dumps (each in its own subfolder).
*   `C:\EGOS\data\raw\mongo_backups\archived\`: Processed raw backup dumps are moved here.
*   `C:\EGOS\data\processed\`: Contains subfolders for each processed backup, holding Parquet files and manifests.
    *   `C:\EGOS\data\processed\<backup_slug>\incidents.parquet`
*   `C:\EGOS\data\roi\`: Contains data and results specific to ROI analysis.
    *   `C:\EGOS\data\roi\master_incidents.parquet`: Consolidated incident data.
    *   `C:\EGOS\data\roi\default_roi_model.yaml`: Example financial model for ROI.
    *   `C:\EGOS\data\roi\latest_roi.json`: Output of the ROI simulation.

## 5. Dependencies

*   Python 3.x
*   `pandas`
*   `pyarrow`
*   `pymongo` (specifically for the `bson` library)
*   `PyYAML`

These can typically be installed via pip: `pip install pandas pyarrow pymongo PyYAML`.

## 6. Configuration

*   **ROI Financial Model:** The `roi_simulate.py` script requires a YAML file defining cost components and value drivers. An example is `default_roi_model.yaml`. This model needs to be adjusted with realistic financial data for meaningful ROI calculations.
*   **Target Collections:** The `ingest_mongo_backups_bson.py` script has a hardcoded list of target collections (currently focused on `incidents`). This can be modified in the script if other collections need to be processed.

## 7. Notes and Troubleshooting

*   **BSON ObjectId Conversion:** The ingestion script converts BSON `ObjectId` fields to strings to prevent type errors when writing to Parquet with PyArrow.
*   **Missing Collections:** The ingestion script will log warnings if expected collections (e.g., `cost_reports`, `users`) are not found in a backup. This is normal if those collections are not present in all dumps.
*   **Data Integrity:** It's advisable to spot-check the generated Parquet files (e.g., using pandas in a Python script or Jupyter notebook) after ingestion, especially when setting up the pipeline or after changes.

## 8. Future Enhancements

(Refer to the main project plan for details on planned enhancements, such as incorporating additional data sources like ATRiAN audit logs, public AI incident databases, and synthetic incident generation.)

## 9. Related Documentation

- [ATRiAN Incident Analysis Methods](../../ATRIAN/docs/methods/incident_analysis_methods.md) - Detailed methodology for incident analysis, severity scoring, and cross-sectoral pattern recognition
- [Top Incidents Case Studies](../../ATRIAN/docs/case_studies/top_incidents.md) - Five high-severity incidents with diagnostics and ATRiAN preventive patterns

---
*This document is part of the EGOS project and is subject to its overall governance and standards.*

@references(level=1):
  - ATRIAN/docs/case_studies/top_incidents.md
  - ATRIAN/docs/methods/incident_analysis_methods.md