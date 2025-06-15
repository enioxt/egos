@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/audits/index.md
  - docs/governance/cross_reference/documentation_reference_manager
  - docs/governance/cross_reference_priority_list.md
  - docs/governance/development_standards.md
  - docs/governance/documentation_health_analysis.md
  - docs/governance/roadmap_standardization.md
  - docs/reference/roadmap_hierarchy_implementation.md






  - docs/governance/roadmap_hierarchy.md

﻿---
title: EGOS Roadmap Hierarchy and Alignment Guidelines
version: 1.0.0
status: Active
date_created: 2025-05-18
date_modified: 2025-05-18
authors: [EGOS Development Team]
description: Guidelines for aligning main and local roadmaps across the EGOS ecosystem
file_type: documentation
scope: project-wide
primary_entity_type: governance
primary_entity_name: roadmap_hierarchy
tags: [documentation, roadmap, standardization, governance, planning, hierarchy]
---
## Cross References

- [EGOS ROADMAP](../../ROADMAP.md)
- [Development Standards](./development_standards.md)
- [Roadmap Standardization](./roadmap_standardization.md)
- [Cross-Reference Priority List](./cross_reference_priority_list.md)
- [Documentation Health Analysis](./documentation_health_analysis.md)
- [Roadmap Hierarchy Implementation](../reference/roadmap_hierarchy_implementation.md)

# EGOS Roadmap Hierarchy and Alignment Guidelines

## Overview

This document defines the hierarchical relationship between the main EGOS roadmap and local (folder- or subsystem-level) roadmaps. It establishes clear guidelines for maintaining alignment, preventing duplication, and ensuring consistent status tracking across all roadmap levels.

## Roadmap Hierarchy

### Main Roadmap (`ROADMAP.md`)

- **Purpose**: Defines high-level goals, milestones, and epics for the entire EGOS project
- **Location**: Project root directory
- **Content**: Strategic initiatives, major features, cross-cutting concerns
- **Audience**: All stakeholders, including management and new contributors
- **Task Level**: Epics and major initiatives

### Local Roadmaps (`roadmap.md`)

- **Purpose**: Define detailed tasks specific to a particular area or subsystem
- **Location**: Each major subfolder (e.g., `scripts/`, `docs/`, `subsystems/KOIOS/`)
- **Content**: Implementation details, specific features, bug fixes
- **Audience**: Developers and contributors working on that specific area
- **Task Level**: Stories, tasks, and subtasks

## Alignment Principles

### 1. Clear Parent-Child Relationships

- Every local roadmap task must link back to its corresponding main roadmap epic
- Parent tasks (epics) live in the main roadmap; child tasks (stories) live in local roadmaps
- No task should be duplicated across roadmaps at the same level of detail

### 2. Consistent Identification System

- **Epic IDs**: Each epic in the main roadmap has a unique identifier (e.g., `EGOS-EPIC-002`)
- **Story IDs**: Tasks in local roadmaps use prefixed IDs (e.g., `EGOS-EPIC-002-01`, `EGOS-EPIC-002-02`)
- **Cross-References**: All tasks include references to parent/child tasks

### 3. Status Propagation

- Child tasks progress through statuses in their local roadmap
- Epic status in the main roadmap reflects the aggregate status of its child tasks
- An epic is only marked "Done" when all its child tasks are complete

## Implementation Guidelines

### Task ID Structure

```
[Project]-[Type]-[Number]-[Subtask]
```

- **Project**: `EGOS` for all tasks
- **Type**: `EPIC` for main roadmap, subsystem code for local roadmaps (e.g., `KOS`, `ATL`)
- **Number**: Sequential number (e.g., `001`, `002`)
- **Subtask**: Sequential subtask number (e.g., `01`, `02`) for local roadmap tasks

### Status Definitions

| Status | Description | Main Roadmap Meaning | Local Roadmap Meaning |
|--------|-------------|----------------------|----------------------|
| Backlog | Planned but not started | No child tasks in progress | Not yet started |
| In Progress | Work has begun | Some child tasks in progress | Active development |
| Review | Ready for review | All child tasks complete, awaiting verification | Code review or testing |
| Done | Complete | All child tasks done and verified | Task complete |
| Deferred | Postponed | Initiative postponed | Task postponed |
| Blocked | Cannot proceed | Critical child tasks blocked | Cannot proceed due to dependency |

### Example Alignment

**Main Roadmap (`ROADMAP.md`):**
```markdown
## Documentation System Enhancement

### [EGOS-EPIC-003] Cross-Reference System Enhancement

**Status:** In Progress
**Priority:** High
**Owner:** Documentation Team

**Description:**
Enhance the documentation cross-reference system to ensure all files maintain proper interconnections.

**Child Tasks:**
- [EGOS-EPIC-003-01] Refactor cross-reference management system (`scripts/roadmap.md`)
- [EGOS-EPIC-003-02] Implement configuration system (`scripts/roadmap.md`)
- [EGOS-EPIC-003-03] Create verification automation (`scripts/roadmap.md`)
- [EGOS-EPIC-003-04] Update documentation standards (`docs/roadmap.md`)

**Acceptance Criteria:**
1. All documentation files have proper cross-references
2. Automated verification system is in place
3. Documentation standards are updated and enforced
```

**Local Roadmap (`scripts/roadmap.md`):**
```markdown
## Cross-Reference Tools

### [EGOS-EPIC-003-01] Refactor Cross-Reference Management System

**Parent Epic:** [EGOS-EPIC-003](../../ROADMAP.md#egos-epic-003-cross-reference-system-enhancement)
**Status:** Done
**Priority:** High
**Owner:** Developer Team

**Description:**
Refactor the cross-reference management system into a modular package.

**Tasks:**
- [x] Create modular package structure
- [x] Implement progress tracking utilities
- [x] Implement checkpoint management
- [x] Create command-line interface

**References:**
- [Cross-Reference Manager](./cross_reference/documentation_reference_manager/)
```

## Handling Edge Cases

### Shared Tasks Between Subsystems

When a task spans multiple subsystems:

1. Create the task in the local roadmap of the primary owner
2. Add cross-references to the task in other relevant local roadmaps
3. Clearly indicate shared ownership in the task description

### Emergent Tasks

For tasks that emerge during development and weren't in the original plan:

1. Add the task to the appropriate local roadmap
2. Link it to the most relevant parent epic in the main roadmap
3. If no suitable parent exists, consider creating a new epic

### Changing Priorities

When priorities change:

1. Update the status in both main and local roadmaps
2. Document the reason for the change
3. Update any affected dependencies

## Automation and Tooling

### Status Synchronization

A script will be developed to:

1. Scan all roadmap files
2. Identify parent-child relationships
3. Verify status consistency
4. Generate reports of misalignments
5. Optionally update statuses based on child task completion

### Visualization

A dashboard will be created to visualize:

1. Overall roadmap completion status
2. Epic-to-story relationships
3. Progress metrics across subsystems
4. Blocked or at-risk tasks

## Related Documents

- [Roadmap Standardization Guidelines](./roadmap_standardization.md)
- [Development Standards](./development_standards.md)
- [Cross-Reference Priority List](./cross_reference_priority_list.md)
- [Audit Dashboard](../audits/index.md)