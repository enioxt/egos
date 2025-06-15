---
description: "Methods for incident analysis, severity scoring, and cross-sectoral pattern recognition in ATRiAN"
---

# ATRiAN Incident Analysis Methods & Practical Workflows

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
- docs/case_studies/top_incidents.md
- docs/workflows/atrian_data_pipeline_roi_workflow.md
- scripts/roi_prepare_data.py
- .windsurf/workflows/distill_and_vault_prompt.md
- .windsurf/workflows/atrian_roi_calc.md

## 1. Context-Rich Analysis Approach

The ATRiAN system emphasizes contextual, qualitative incident analysis over purely numeric metrics, enabling deeper insights into failure patterns and more effective preventative measures.

### 1.1. Text Mining & Incident Identification

High-severity incidents are identified through a multi-step process:

1. **Data Loading & Analysis**:
   - Load all `incidents.parquet` files using pandas (accessible via both MCP filesystem tools or terminal commands)
   - Perform text mining on `title` & `description` fields using keyword search patterns for high-harm indicators:
     ```python
     # Example terminal one-liner for rapid exploration
     python -c "import pandas as pd; df = pd.read_parquet('data/processed/backup-20250407100605/incidents.parquet'); print(df[df['title'].str.contains('|'.join(['kill', 'bias', 'crash', 'harm', 'death']), case=False, na=False)][['incident_id', 'title', 'description']].head())"
     ```

2. **Severity Scoring Heuristics**:
   - Incidents are scored on a 1-3 ordinal scale using keyword-based heuristics:
     - **3 (Fatal/Critical)**: Contains keywords related to death, fatality, or permanent harm
     - **2 (Serious)**: Contains keywords related to injury, discrimination, child exposure to inappropriate content
     - **1 (Moderate)**: Contains keywords related to financial damage, reputational harm, or other non-physical impacts

3. **Public Domain Research**:
   - High-severity incidents are manually matched to public domain post-mortems
   - Failure chains are reconstructed using published investigations and technical reports

### 1.2. ATRiAN Signal Mapping

Each incident's failure chain is systematically mapped to ATRiAN signal categories:

| Signal Category | Description | Example Metric |
|-----------------|-------------|----------------|
| Data-Bias KPIs | Metrics identifying biases in training or production data | Demographic parity scores, feature distribution shifts |
| Simulation Gaps | Missing scenarios in test/simulation environments | Coverage of edge cases like "pedestrian at night" |
| Config-Drift | Changes to safety-critical configuration parameters | Unauthorized override of safety protocols |
| Live Toxicity | Real-time content moderation metrics | Spikes in toxicity scores in user-generated content |
| Evasion KPIs | Metrics related to system's ability to handle unexpected scenarios | Availability of evasive maneuvers in autonomous systems |

## 2. Tool Selection & Methodology Rationale

### 2.1. Balancing Interactive vs. Programmatic Approaches

The ATRiAN analysis pipeline employs both interactive terminal commands and MCP filesystem tools:

- **Quick Terminal One-liners**: Used for ad-hoc exploration with feedback cycles under 2 seconds
- **MCP Filesystem Tools**: Used for:
  - Programmatic, reusable data ingestion (generating parquet files, docs, tests)
  - Fine-grained writes within the EGOS ecosystem (edit_file operations)

Both approaches access the same underlying data, allowing analysts to switch between methods based on whether latency or repeatability is the priority.

## 3. Reverse-Prompt Engineering for Automated Insights

The ATRiAN system implements a reverse-prompt engineering workflow to automate incident pattern recognition:

1. **Query Script Creation**:
   - Develop a script that prints a markdown table of top-N incidents with summaries
   - Example: `python scripts/query_high_severity_incidents.py --top 5 --format markdown`

2. **Prompt Distillation**:
   - Invoke `/distill_and_vault_prompt` workflow on the chat containing query results
   - Cascade distills the question (e.g., "give me 5 grave incidents with diagnostics") into a reusable prompt template

3. **PromptVault Storage**:
   - The distilled prompt is stored in PromptVault for reuse
   - Any analyst can regenerate the table with one prompt invocation

This approach minimizes human effort while ensuring consistent output across analyses.

## 4. Information Journey & Processing Timeline

The ATRiAN system provides rapid analysis through a streamlined information pipeline:

| Stage | Processing Time | Description |
|-------|----------------|-------------|
| Streaming Ingestion | < 500 ms | ATRiAN pre-processors create embeddings and KPI snapshots |
| Rule Application | < 250 ms | Sector-specific rules are applied to incoming data |
| Alert Generation | Real-time (seconds) | If thresholds are exceeded, ATRiAN pushes webhooks to CI/CD or moderation queues |

**Current Implementation Status**: Approximately 70% complete
- **Implemented**: Ingestion pipelines and basic KPI hooks
- **Missing Components**: Sector-specific rule-sets, live connectors, and dashboards

## 5. Sector-Specific Roadmap & Cross-Sector Knowledge Sharing

### 5.1. Mobility Sector

- **Scenario Library Expansion**:
  - Add unprotected left turn scenarios
  - Add jaywalking at night scenarios
- **CI Integration**:
  - Connect ATRiAN to simulator run results
  - Automatically fail merge requests if safety KPI falls below 99%

### 5.2. Media & User-Generated Content

- **Content Moderation**:
  - Deploy toxicity + visual-cues ensemble classifier
  - Implement live sampling of 1% of uploads
- **Escalation Protocol**:
  - Add rapid human-escalation workflow for flagged content

### 5.3. Manufacturing

- **Safety Controls**:
  - Implement config-drift monitoring on robot safety settings
  - Require two-person override for safety-critical changes

### 5.4. Public Safety & Policing

- **Fairness Monitoring**:
  - Deploy fairness regression tests
  - Implement counter-factual disparity scoring for each model retraining

### 5.5. Cross-Sector Knowledge Sharing

ATRiAN facilitates cross-sector learning through a modular rule system:

- **Rule Storage**: Each sector's rules are stored as YAML files in `EGOS/rules/<sector>.yaml`
- **Rule Loading**: The ATRiAN engines load all YAML files during initialization
- **Knowledge Transfer**: This approach allows bias checks developed for policing to be applied to loan-approval models
- **Rule Discovery**: The system automatically suggests potentially applicable rules from other sectors based on semantic similarity

## 6. Implementation Status & Next Steps

### 6.1. Completed Enhancements

✓ `roi_prepare_data.py` now passes through rich context fields (`title`, `description`, `date`, `sector`)  
✓ `roi_prepare_data.py` computes heuristic `severity_score` for incidents  
✓ `docs/case_studies/top_incidents.md` created with diagnostics for five high-severity incidents  
✓ Created cross-references between case studies and relevant EGOS documentation  
✓ Added test file `tests/test_roi_prepare_data_columns.py` to enforce data quality  
✓ Updated README to surface the case-study library  

### 6.2. Pending Enhancements

- Scale `roi_simulate.py` risk mitigation factors by `severity_score`
- Create sector-specific rule YAML files with example ATRiAN detectors
- Implement live connectors for real-time monitoring
- Develop dashboard components for visualization of incident patterns
- Complete the prompt distillation and automation workflow

---

*This document is maintained as part of the EGOS methodological documentation library and follows the EGOS standards for cross-referencing and knowledge integration.*
