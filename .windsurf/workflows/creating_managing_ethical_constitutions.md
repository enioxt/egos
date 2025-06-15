---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~8 k)
# Version 2.0 – “Living Constitution” – 2025-06-13

description: A structured process for creating, customizing, and managing ethical constitutions for use with ATRiAN's Ethics as a Service (EaaS)
categories: [ethics, governance, documentation]
requires: [ATRiAN]
---

# CREATING & MANAGING ETHICAL CONSTITUTIONS WORKFLOW (EGOS × WINDSURF)

> “Codify values; iterate responsibly.”

Invoke with `/creating_managing_ethical_constitutions`.

---
## TABLE OF CONTENTS
1. Prerequisites & Governance  
2. Phase 1 – Draft Constitution  
3. Phase 2 – Review & Approval  
4. Phase 3 – Versioning & Publication  
5. Phase 4 – Monitoring & Amendments  
6. Annex – Constitution Template  

---
## 1. PREREQUISITES & GOVERNANCE // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | Template generator present | `scripts/gen_constitution.py --help` |
|   | Review Board defined | `grep "ReviewBoard:" org_chart.md` |
|   | Validator CLI ready | `atrian-validator --help` |

Abort if any check fails.

---
## 2. PHASE 1 – DRAFT CONSTITUTION
### 1.1 Use Generator // turbo
```bash
python scripts/gen_constitution.py --output constitutions/new_draft.yaml
```
Choose base template (privacy, bias, safety modules).

### 1.2 Populate Metadata
Fill `title`, `version`, `jurisdiction`, `author`.

### 1.3 Internal Alignment
Cross-check against MQP principles and sector regulations.

---
## 3. PHASE 2 – REVIEW & APPROVAL
### 2.1 Validator Pass
Run `/atrian_validator_testing`.

### 2.2 Review Board Session
Stakeholders vote (record in `reviews/constitution_<date>.md`).

### 2.3 Ethical Impact Assessment
Use `/atrian_ethics_evaluation` on sample outputs.

---
## 4. PHASE 3 – VERSIONING & PUBLICATION
### 3.1 Semantic Versioning
Increment MAJOR for principle change, MINOR for rule addition.

### 3.2 Publish to ATRiAN // turbo
```bash
atrian-cli upload constitution.yaml --activate
```
### 3.3 Git Tag & Release Notes
Tag `constitution-vX.Y.Z`.

---
## 5. PHASE 4 – MONITORING & AMENDMENTS
* Monitor evaluation metrics; if degradation >5%, open amendment issue.
* Quarterly review cycle.

---
## ANNEX – CONSTITUTION TEMPLATE (YAML)
```yaml
id: <uuid>
title: "EGOS Privacy & Safety Constitution"
version: 1.0.0
jurisdiction: global
author: egos_review_board
principles:
  - id: p1
    name: Respect Privacy
    rules:
      - id: p1r1
        description: "No PII leakage."
        level: critical
```

---
### WORKFLOW META
* `// turbo` denotes safe auto-runs.  
* Keep file <12 k chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /atrian_ethics_evaluation – Consumes constitution IDs defined here.
- /atrian_sdk_dev – Uses constitution schemas when building SDK helpers.
- /ai_assisted_research_and_synthesis – Research scholarly sources to refine constitutions.
- /dynamic_documentation_update_from_code_changes – Sync constitution docs with code.
- /project_handover_procedure – Transfer stewardship of constitutions.

*EOF*