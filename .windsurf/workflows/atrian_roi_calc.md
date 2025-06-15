---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~7 k)
# Version 2.0 – “Ethics ROI” – 2025-06-13

description: Methodical approach to calculating and analyzing the return on investment for implementing ATRiAN's Ethics as a Service (EaaS) capabilities.
categories: [finance, analytics, ethics]
requires: [ATRiAN]
---

# ATRIAN ROI CALCULATION & ANALYSIS WORKFLOW (EGOS × WINDSURF)

> “Measure the value of doing the right thing.”

Invoke with `/atrian_roi_calc`.

---
## TABLE OF CONTENTS
1. Prerequisites & Data Sources  
2. Phase 1 – Define ROI Model  
3. Phase 2 – Collect Baseline Metrics  
4. Phase 3 – Monte Carlo Simulation  
5. Phase 4 – Sensitivity Analysis  
6. Phase 5 – Report & Dashboard  
7. Annex A – Financial Template  

---
## 1. PREREQUISITES & DATA SOURCES // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | Master incidents Parquet | `dir data/roi/master_incidents.parquet` |
|   | Market salary rates sheet | `dir data/roi/salaries.xlsx` |
|   | `pandas` + `numpy` installed | `pip show pandas` |

Abort if any check fails.

---
## 2. PHASE 1 – DEFINE ROI MODEL
### 1.1 Value Drivers
* Risk mitigation (regulatory fines avoided)
* Brand trust uplift (NPS delta → rev growth)
* Dev efficiency (bugs prevented via early ethics check)

### 1.2 Cost Components
* ATRiAN subscription  
* Engineering integration hours  
* Ongoing evaluation compute

Store model assumptions in `roi_model.yaml`.

---
## 3. PHASE 2 – COLLECT BASELINE METRICS
Load incident cost, frequency, compliance fines from sector reports.
`python scripts/roi_prepare_data.py` aggregates processed Parquet files and produces `master_incidents.parquet` (see detailed pipeline doc).

---
## 4. PHASE 3 – MONTE CARLO SIMULATION // turbo
```bash
python scripts/roi_simulate.py --model roi_model.yaml --runs 10000 --out mc_results.parquet
```
Outputs distribution of ROI %, NPV, payback period.

---
## 5. PHASE 4 – SENSITIVITY ANALYSIS
`python scripts/roi_sensitivity.py mc_results.parquet --plot` generates tornado chart.

Identify top 5 parameters influencing ROI; update mitigation plan.

---
## 6. PHASE 5 – REPORT & DASHBOARD
### 5.1 Markdown Report
Generate with Jinja template `templates/roi_report.md.j2`.

### 5.2 Grafana Dashboard Export
Upload CSV to Influx; import dashboard JSON `dashboards/atri_roi.json`.

### 5.3 Share & Log
Commit report to `docs/roi/`. Log summary to ADRS if ROI < expected.

---
## ANNEX A – FINANCIAL TEMPLATE (CSV)
```
parameter,low,mid,high
fine_per_incident,200000,500000,1500000
engineering_hour_cost,60,80,100
```

---
### WORKFLOW META
* `// turbo` denotes safe auto-runs; obey RULE-OPS-CHECKLIST-001.  
* Keep file < 12 000 chars; bump version on edits.

---
## Cross-References & Related Workflows

- /atrian_ethics_evaluation – Supplies evaluation coverage metrics used as inputs for ROI.
- /ai_assisted_research_and_synthesis – Gather baseline financial data and incident cost research.
- /dynamic_documentation_update_from_code_changes – Auto-sync ROI report templates after updates.
- Documentation: `docs/workflows/atrian_data_pipeline_roi_workflow.md` – End-to-end data ingestion & preparation details.
- /initiate_msak_analysis – Feed ROI findings into strategic scenario planning.
- /project_handover_procedure – Transfer ROI dashboards to finance or leadership teams.

*EOF*