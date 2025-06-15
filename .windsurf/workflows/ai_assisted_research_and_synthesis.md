---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12000 chars (current ~8 k)
# Version 2.0 – “Deep-Research” expansion – 2025-06-13

description: End-to-end workflow for AI-assisted research & synthesis—combining systematic inquiry, Windsurf automations, EGOS ethical governance, and reproducible knowledge capture.
categories: [research, synthesis, governance]
requires: [ATRiAN, Mycelium]
---

# AI-ASSISTED RESEARCH & SYNTHESIS WORKFLOW (EGOS × WINDSURF)

> “Curiosity disciplined by method; insight amplified by AI.”

Invoke with `/ai_assisted_research_and_synthesis`.

---
## TABLE OF CONTENTS
1. Prerequisites & Environment  
2. Phase 1 – Define & Plan  
3. Phase 2 – Gather (AI-Assisted)  
4. Phase 3 – Process & Analyse  
5. Phase 4 – Synthesize & Draft  
6. Phase 5 – Validate & Publish  
7. Phase 6 – Feedback & Continuous Improvement  
8. Annex A – Tool Cheat-Sheet  
9. Annex B – Citation & Metadata Schema

---
## 1. PREREQUISITES & ENVIRONMENT // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | search_web API key set (`WSF_SEARCH_KEY`) | `echo %WSF_SEARCH_KEY%` |
|   | Citation manager (`citeproc`) installed | `pip install citeproc-py` |
|   | Mycelium endpoint reachable | `curl http://localhost:8700/health` |
|   | Backup script ready | `scripts/backup_modified_files.ps1` |

**Abort if any check fails.**

---
## 2. PHASE 1 – DEFINE & PLAN
### 1.1 Clarify Research Objective
Write a one-sentence **Problem Statement** and success criteria.

### 1.2 Map Knowledge Domains
Use *Systemic Cartography* to list sub-topics, stakeholders, and ethical angles.

### 1.3 Draft Query Matrix
Prepare search permutations:
```
|#|Keyword set|Reason|
|1|"EU AI Act" + compliance + healthcare|Reg driver|
|2|LLM hallucination mitigation|Tech risk|
```
Store as `docs/research/<topic>/query_matrix.md`.

---
## 3. PHASE 2 – GATHER INFORMATION (AI-ASSISTED)
### 2.1 Execute Searches // turbo-all
```python
results = search_web(query, max_results=20)
```
For internal artefacts use `codebase_search` or `mcp6_search_nodes`.

### 2.2 Relevance Scoring
Let EVA rank results by semantic similarity to Problem Statement.

### 2.3 Harvest & Snapshot
`read_url_content` or `open_browser_url` to capture HTML → store raw content under `data/raw/<hash>.md` with YAML header (source, timestamp).

### 2.4 Deduplicate & Tag
Compute SHA-256; skip if hash exists. Tag metadata (`ai`, `regulation`, etc.) for Mycelium ingestion.

---
## 4. PHASE 3 – PROCESS & ANALYSE
### 3.1 Cleaning
Strip boilerplate, adverts, and consolidate PDFs via `pdfminer`.

### 3.2 Information Extraction
Run NLP pipeline (spaCy + transformer): entities, relations, sentiment.
```bash
python scripts/extract_entities.py data/clean/<file>.md  // turbo
```

### 3.3 Thematic Mapping
Cluster documents using `BERTopic`; output interactive HTML map → attach to issue tracker.

### 3.4 Gap Analysis
EVA suggests areas with sparse coverage; log to `docs/research/<topic>/gap_log.md`.

---
## 5. PHASE 4 – SYNTHESIZE & DRAFT
### 4.1 AI Draft Generation
Prompt Cascade with:
```
Summarize cluster X; include pros/cons, cite sources by [n].
```
### 4.2 Human Enhancement
Editors refine language, add critical analysis, cross-reference MQP principles.

### 4.3 Backup Before Overwrite // turbo
```
powershell scripts/backup_modified_files.ps1 docs/research/<topic>
```

### 4.4 Document Assembly
• Executive Summary (≤1 page)  
• Detailed Findings  
• Recommendations & Ethical implications  
Compile via `mkdocs build` if part of site.

---
## 6. PHASE 5 – VALIDATE & PUBLISH
### 5.1 Fact Check
Run `scripts/fact_check.py` – flags unsupported statements.

### 5.2 Source Verification
Ensure each citation resolves; 404 triggers blocking.

### 5.3 Technical Validation
If code samples exist, execute in isolated venv; attach logs.

### 5.4 Peer Review & ADRS
Open MR; reviewers use checklist. Significant insights logged to `ADRS_Log.md`.

### 5.5 Publish & Distribute
Merge to `main`, trigger `/dynamic_documentation_update_from_code_changes`; Mycelium ingests metadata; Slack notification.

---
## 7. PHASE 6 – FEEDBACK & CONTINUOUS IMPROVEMENT
• Monitor dashboard for engagement metrics (views, citations).  
• Schedule quarterly re-validation of sources.  
• Update research when regulatory landscape shifts (>major version).

---
## ANNEX A – TOOL CHEAT-SHEET
| Purpose | Tool / Command |
|---------|----------------|
| Web search | `search_web` |
| Internal grep | `grep_search` |
| Backup | `scripts/backup_modified_files.ps1` |
| NLP extract | `scripts/extract_entities.py` |
| Fact check | `scripts/fact_check.py` |

---
## ANNEX B – CITATION & METADATA SCHEMA
```yaml
source: "https://example.com/article"
collected: 2025-06-13T22:40:00Z
retrieved_by: ai_assisted_research_workflow
license: CC-BY-4.0
hash: <sha256>
tags: [ai, governance]
```

---
### WORKFLOW META
* `// turbo` annotations denote safe auto-runs; obey RULE-OPS-CHECKLIST-001.  
* Keep this file <12 000 chars; update version header when modified.

---
## Cross-References & Related Workflows

- /ai_assisted_research_and_synthesis – Comprehensive AI-driven research loop (this file).
- /initiate_msak_analysis – Strategic scenario kernel; typically follows consolidated research.
- /atrian_ethics_evaluation – Inject at validation steps to ensure ethical compliance of gathered insights and outputs.
- /atrian_roi_calc – Quantify financial impact of adopting ethics findings; can be triggered after evaluation metrics are recorded.
- /dynamic_documentation_update_from_code_changes – Run automatically after any of these workflows to keep docs aligned.
- /iterative_code_refinement_cycle – Apply when research uncovers code-level improvements.
- /project_handover_procedure – Use to transfer ownership of completed research packages.

*EOF*