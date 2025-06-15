---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~8 k)
# Version 2.0 – “Task Orchestrator” – 2025-06-13

description: A structured workflow for managing tasks using TaskMaster AI within the EGOS ecosystem, via the egos-tasks.ps1 script.
categories: [project_management, automation, productivity]
requires: [TaskMaster, Mycelium]
---

# TASKMASTER TASK MANAGEMENT WORKFLOW (EGOS × WINDSURF)

> “From chaos to cohesive execution.”

Invoke with `/taskmaster_task_management`.

---
## TABLE OF CONTENTS
1. Prerequisites & Setup  
2. Phase 1 – Initialise Board  
3. Phase 2 – Create & Prioritise Tasks  
4. Phase 3 – Execution Tracking  
5. Phase 4 – Reporting & Insights  
6. Annex – YAML Task Spec v1  

---
## 1. PREREQUISITES & SETUP // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | egos-tasks.ps1 present | `dir scripts/egos-tasks.ps1` |
|   | Mycelium endpoint reachable | `curl http://localhost:8700/health` |
|   | Plan.md exists | `dir %USERPROFILE%\.codeium\windsurf\brain\*\plan.md` |

Abort if any check fails.

---
## 2. PHASE 1 – INITIALISE BOARD
### 1.1 One-Time Setup // turbo
```powershell
powershell scripts/egos-tasks.ps1 init --plan path\to\plan.md
```
Creates default Kanban columns: Backlog, In-Progress, Review, Done.

### 1.2 Sync Existing Issues
Import open GitHub issues via REST API; tag with `taskmaster-sync`.

---
## 3. PHASE 2 – CREATE & PRIORITISE TASKS
### 2.1 YAML Task Spec
Write task in `tasks/*.yaml` (see Annex).

### 2.2 Auto-Prioritise // turbo
```powershell
powershell scripts/egos-tasks.ps1 auto-prioritise --source tasks/
```
Uses EVA to rank by impact vs effort.

### 2.3 Review Board Approval
Stakeholders approve top N tasks for sprint.

---
## 4. PHASE 3 – EXECUTION TRACKING
### 3.1 Update Status // turbo-all
```powershell
powershell scripts/egos-tasks.ps1 move --id 42 --to In-Progress
```
Updates Plan.md and pushes Mycelium event.

### 3.2 Time Logging
Each move records timestamp; weekly burndown chart auto-generated.

### 3.3 Dependency Alerts
If blocked, script notifies Slack channel.

---
## 5. PHASE 4 – REPORTING & INSIGHTS
* Generate sprint report PDF via `scripts/gen_sprint_report.py`.  
* Metrics: throughput, cycle time, blocked ratio.  
* Publish to `docs/reports/` and post link to channel.

---
## ANNEX – YAML TASK SPEC v1
```yaml
id: 42
title: "Implement cancellation in video processor"
description: "User can terminate FFmpeg mid-run."
status: backlog
labels: [video, UX]
priority: medium
estimate: 4h
owner: @enioxt
created: 2025-06-13
```

---
### WORKFLOW META
* `// turbo` designates safe auto-runs; obey RULE-OPS-CHECKLIST-001.  
* Keep file < 12 000 chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /project_handover_procedure – Interface with TaskMaster tasks when handing over projects.
- /ai_assisted_research_and_synthesis – Track research tasks within TaskMaster.
- /dynamic_documentation_update_from_code_changes – Trigger doc updates when tasks completed.

*EOF*