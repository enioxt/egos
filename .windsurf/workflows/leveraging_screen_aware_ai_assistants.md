---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~8 k)
# Version 2.0 – “Contextual Eyes” – 2025-06-13

description: Workflow for evaluating and integrating screen-aware AI assistants (like Highlight AI) into EGOS development processes
categories: [ai_tools, privacy, productivity, ethics]
requires: [ATRiAN]
---

# LEVERAGING SCREEN-AWARE AI ASSISTANTS WORKFLOW (EGOS × WINDSURF)

> “Let the AI see what you see—securely.”

Invoke with `/leveraging_screen_aware_ai_assistants`.

---
## TABLE OF CONTENTS
1. Prerequisites & Privacy Impact  
2. Phase 1 – Assistant Selection  
3. Phase 2 – Trial Deployment  
4. Phase 3 – KPI Measurement  
5. Phase 4 – Full Integration  
6. Annex – Privacy Impact Assessment  

---
## 1. PREREQUISITES & PRIVACY IMPACT // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | DPIA template ready | `dir docs/privacy/dpia_template.md` |
|   | Highlight AI installer | `ls installers/highlight_ai.exe` |
|   | ATRiAN privacy constitution active | `echo %ETHICAL_CONSTITUTION_ID%` |

Abort if any check fails.

---
## 2. PHASE 1 – ASSISTANT SELECTION
Compare vendors on: on-device processing, encryption, cost, plugin ecosystem.

---
## 3. PHASE 2 – TRIAL DEPLOYMENT
### 2.1 Isolated Sandbox // turbo
```bash
start-highlight-ai --mode sandbox --recording off
```

### 2.2 Task Scenario Set
Run typical coding session, capture metrics.

### 2.3 Privacy Impact Assessment
Fill DPIA; run `/atrian_ethics_evaluation` on screenshot logs.

---
## 4. PHASE 3 – KPI MEASUREMENT
Metrics: task completion time, error rate, user satisfaction survey.

### 3.2 Data Sync KPI Dashboard
Push metrics to Grafana board `highlight_ai.json`.

---
## 5. PHASE 4 – FULL INTEGRATION
* Enable live screen context in Cascade via Highlight API.
* Document opt-in procedure; default off.
* Quarterly privacy audits.

---
## ANNEX – PRIVACY IMPACT ASSESSMENT CHECKLIST
1. Purpose limitation documented  
2. Data minimisation measures  
3. Encryption in transit & at rest  
4. Retention period defined  
5. User consent captured  

---
### WORKFLOW META
* `// turbo` designates safe auto-runs.  
* Keep file <12 k chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /ai_assisted_research_and_synthesis – Incorporate findings from screen-aware assistants into research.
- /atrian_ethics_evaluation – Evaluate assistant outputs for privacy leakage.
- /dynamic_documentation_update_from_code_changes – Document configuration changes for assistants.
- /project_handover_procedure – Transfer assistant settings.

*EOF*