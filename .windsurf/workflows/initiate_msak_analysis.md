---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~8 k)
# Version 2.0 – “ULTRA v4.2 Kernel” – 2025-06-13

description: Initiates a comprehensive strategic analysis using the EGOS ULTRA v4.2 Multiverse Strategic Analysis Kernel (MSAK).
categories: [strategy, analytics, decision_support, ethics]
requires: [Mycelium, ATRiAN]
---

# INITIATE MSAK ANALYSIS WORKFLOW (EGOS × WINDSURF)

> “Navigate the multiverse of strategy.”

Invoke with `/initiate_msak_analysis`.

---
## TABLE OF CONTENTS
1. Prerequisites & Data Check  
2. Phase 1 – Define Strategic Question  
3. Phase 2 – Data Ingestion  
4. Phase 3 – Kernel Execution  
5. Phase 4 – Insight Synthesis  
6. Phase 5 – Validation & Sign-Off  
7. Annex – Analysis Template  

---
## 1. PREREQUISITES & DATA CHECK // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | MSAK Docker image pulled | `docker images | findstr msak` |
|   | Input dataset present | `dir data/strategic/` |
|   | Mycelium endpoint reachable | `curl http://localhost:8700/health` |

Abort if any check fails.

---
## 2. PHASE 1 – DEFINE STRATEGIC QUESTION
Write single-line question, success criteria, horizon (e.g., 3-5 yrs).
Store in `analyses/<slug>/question.md`.

---
## 3. PHASE 2 – DATA INGESTION
### 2.1 Collect Relevant Docs
Link market reports, internal metrics.

### 2.2 Pre-Process // turbo
```bash
python scripts/msak_prepare.py --input data/strategic/ --out data/processed/
```

### 2.3 Ethical Screening
Run `/atrian_ethics_evaluation` on data samples.

---
## 4. PHASE 3 – KERNEL EXECUTION // turbo-all
```bash
docker run --rm -v $(pwd):/work msak:4.2 run --config configs/msak.yaml --out outputs/<slug>
```
Generates JSON & Markdown insight files.

---
## 5. PHASE 4 – INSIGHT SYNTHESIS
Use Cascade to craft executive summary (<1 page) and deck.

### 4.2 Scenario Mapping
Translate kernel outputs into optimistic, neutral, pessimistic tracks.

---
## 6. PHASE 5 – VALIDATION & SIGN-OFF
* Peer review by ULTRA committee.
* Metrics check: Coverage ≥ 90 %, Confidence ≥ 0.8.
* Upon approval, commit analysis under `docs/strategic/`.

---
## ANNEX – ANALYSIS TEMPLATE (YAML)
```yaml
slug: <string>
question: "How to maximise EaaS adoption?"
horizon: "2025-2030"
inputs:
  - market_reports
  - internal_metrics
outputs:
  - summary.md
  - scenarios.xlsx
```

---
### WORKFLOW META
* `// turbo` designates safe auto-runs.  
* Keep file <12 k chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /ai_assisted_research_and_synthesis – Provide research corpus feeding scenario kernel.
- /atrian_ethics_evaluation – Screen scenario datasets for ethical compliance.
- /atrian_roi_calc – Incorporate ROI outputs into strategic scenarios.
- /project_handover_procedure – Transfer analysis deliverables to stakeholders.

*EOF*