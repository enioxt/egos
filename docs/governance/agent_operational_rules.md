---
title: agent_operational_rules
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: agent_operational_rules
tags: [documentation]
---
---
title: agent_operational_rules
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: agent_operational_rules
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

<!-- 
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - governance/cross_reference_best_practices.md





  - [MQP](..\reference\MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Process Documentation:
  - [cross_reference_best_practices](../../governance/cross_reference_best_practices.md)
  - docs/governance/agent_operational_rules.md




**Protocol ID:** `PROTO-OPS-RULES-01`

**Purpose:** To define fundamental operational guidelines for AI agents (like Cascade) working within the EGOS framework, ensuring consistency, efficiency, and alignment with project principles.

**Owning Subsystem:** CORUJA (Coordination & Communication) / KOIOS (Knowledge & Learning)

**Applicability:** These rules apply to all AI agent interactions within the EGOS development environment unless overridden by specific, immediate user instructions for a given task.

**Core Operational Rules:**

1.  **Rule ID:** `RULE-OPS-LANG-01`
    *   **Rule (Language):** All communication, generated code, documentation, and file content MUST be in **English**, unless explicitly instructed otherwise by the user for a specific context.

2.  **Rule ID:** `RULE-OPS-AUTONOMY-01`
    *   **Rule (Task Execution & Autonomy):** Proceed autonomously on sequential tasks within an agreed-upon plan. Execute routine actions (file operations, standard code generation, running safe commands) without seeking confirmation. Reserve questions for genuine points of uncertainty, critical decisions, potential risks, or when deviating significantly from the current plan. Aim for efficiency and workflow fluidity.

3.  **Rule ID:** `RULE-OPS-CONTEXT-01`
    *   **Rule (Context Management):** Actively track the current task and workflow context. If multiple complex topics arise concurrently, proactively structure the conversation to address them sequentially or request prioritization from the user. Explicitly tie responses to specific tasks or subtasks.

4.  **Rule ID:** `RULE-FILE-ACCESS-01` (Defined previously)
    *   **Rule (File Access Fallback):** If a direct file access tool (`view_file`, `edit_file`, etc.) fails to access a requested file path, the agent MUST automatically attempt to locate the file using a recursive terminal search (e.g., `Get-ChildItem -Recurse -Filter 'filename.ext'`) within the EGOS project root (`C:\Eva Guarani EGOS`). If found, retry the original action with the correct path. If not found after search, inform the user.

5.  **Rule ID:** `RULE-OPS-HANDOVER-01` (Semi-Automated)
    *   **Rule (Session Handover):** Upon user signal that work is concluding for the session, synthesize the current development state, including completed tasks, pending items from the active plan, key notes, and (eventually) time estimates. Propose this summary to the user. Upon approval, create or update the `EGOS_Handover_Log.md` file in the project root with the approved summary.

**Governance:**

*   These rules are fundamental but can be refined or added to via user feedback and system evolution.
*   They complement, but do not replace, specific guidelines in other `.mdc` files (e.g., `sparc_orchestration.mdc`, `security_practices.mdc`, `ai_collaboration_guidelines.mdc`).