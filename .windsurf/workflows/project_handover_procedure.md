---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~9 k)
# Version 2.1 – “Ultra-Clean Handover” – 2025-06-13

description: Standardized procedure for project, task, or role handovers within the EGOS ecosystem to ensure continuity and knowledge transfer.
categories: [process, documentation, governance]
requires: [ATRiAN]
---

# PROJECT HANDOVER PROCEDURE WORKFLOW (EGOS × WINDSURF)

> “No knowledge left behind.”

Invoke with `/project_handover_procedure`.

---
## TABLE OF CONTENTS
1. Prerequisites & Checklist  
2. Phase 1 – Preparation  
3. Phase 2 – Documentation Consolidation  
4. Phase 3 – Access Transfer  
5. Phase 4 – Live Handover Session  
6. Phase 5 – Post-Handover Support  
7. Annex – Ultra-Clean Handover Checklist v2  

---
## 1. PREREQUISITES & CHECKLIST // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | Handover template present | `dir docs/standards/handover_checklist_template.md` |
|   | Backup script ready | `scripts/backup_modified_files.ps1` |
|   | Access audit tool | `pip show access-audit` |

Abort if any check fails.

---
## 2. PHASE 1 – PREPARATION
### 1.1 Define Scope
Specify project, repos, environments to transfer.

### 1.2 Stakeholder Mapping
Identify outgoing lead, incoming owner, reviewers.

### 1.3 Schedule Timeline
Set freeze date, session date, support window.

---
## 3. PHASE 2 – DOCUMENTATION CONSOLIDATION
### 2.1 Run Auto-Harvest // turbo
```bash
python scripts/harvest_docs.py --project <slug> --out handover_pack
```
Collect READMEs, ADRS, plan.md, workflows.

### 2.2 Validate Completeness
Checklist auto-populates; missing items flagged in red.

### 2.3 Backup Artifacts
`powershell scripts/backup_modified_files.ps1 handover_pack`.

---
## 4. PHASE 3 – ACCESS TRANSFER
### 3.1 Audit Current Access // turbo
```bash
access-audit list --project <slug> --out access_before.csv
```
### 3.2 Update Permissions
Add incoming owner to repos, CI/CD, cloud, secrets.

### 3.3 Verify Least Privilege
Re-run audit; diff must show only intended changes.

---
## 5. PHASE 4 – LIVE HANDOVER SESSION
### 4.1 Agenda
* Project overview & roadmap  
* Key workflows & tech stack  
* Open risks & technical debt  
* Q&A

### 4.2 Recording & Minutes
Record via Teams; minutes saved to `docs/handover/<date>.md`.

### 4.3 Sign-Off
Both parties tick boxes in checklist; store signed PDF.

---
## 6. PHASE 5 – POST-HANDOVER SUPPORT
* Outgoing lead available N days (default 10) for queries.  
* Weekly checkpoint call until KPI “Stabilised” state.  
* After support window, revoke old access.

---
## ANNEX – ULTRA-CLEAN HANDOVER CHECKLIST v2 (excerpt)
| Section | Item | Done |
|---------|------|------|
| Docs | Up-to-date README | [ ] |
| Docs | ADRS entries linked | [ ] |
| Code | All tests pass | [ ] |
| Access | Secrets rotated | [ ] |
| Support | Schedule set | [ ] |

*(Full template located in docs/standards/handover_checklist_template.md)*

---
### WORKFLOW META
* `// turbo` designates safe auto-runs; obey RULE-OPS-CHECKLIST-001.  
* Keep file < 12 000 chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /dynamic_documentation_update_from_code_changes – Ensure docs are current before handover.
- /ai_assisted_research_and_synthesis – Attach links to research packages being handed over.
- /atrian_ethics_evaluation – Include latest evaluation reports in the handover bundle.
- /atrian_roi_calc – Provide ROI dashboard snapshots to stakeholders.

*EOF*