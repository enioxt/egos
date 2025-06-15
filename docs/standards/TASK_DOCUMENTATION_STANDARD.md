---
title: TASK_DOCUMENTATION_STANDARD
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: task_documentation_standard
tags: [documentation]
---
---
title: TASK_DOCUMENTATION_STANDARD
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
title: TASK_DOCUMENTATION_STANDARD
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

# EGOS Task and Documentation Standard

**Document ID:** DOCS-STANDARD-001  
**Version:** 1.0.0  
**Last Updated:** 2025-04-19  
**Status:** ⚡ Active

## Overview

This document defines the standardized approach to task management and documentation within the EGOS ecosystem. It establishes consistent patterns for tracking development progress, maintaining comprehensive documentation, and ensuring the interconnectedness of all system components—aligning with the EGOS principles of Conscious Modularity, Systemic Cartography, and Reciprocal Trust.

## Task Lifecycle Management

### Task Status Definitions

All tasks in the EGOS ecosystem must use the following standardized status indicators:

| Symbol | Status | Description |
|--------|--------|-------------|
| ✅ | Completed | Task has been fully implemented, tested, and documented |
| ⏳ | In Progress | Work has started but is not yet complete |
| ❌ | Paused | Work has been temporarily stopped (requires explanation) |
| ⚡ | Active | Currently being actively worked on (high priority) |
| ❓ | Pending Review | Implementation complete but awaiting review |

### Task Recording Requirements

All tasks must be properly recorded in the `ROADMAP.md` file using the following format:

```markdown
#### [Task ID]: [Task Name]

**Status:** [Status Symbol and Label]  
**Responsible:** [Human Developer/AI Agent Name]  
**Subsystems:** [Related Subsystems]  
**Priority:** [High/Medium/Low]  
**Est. Completion:** [Date or Sprint]

**Description:**  
Brief description of the task and its goals.

**Acceptance Criteria:**
- Criterion 1
- Criterion 2

**Dependencies:**
- [Dependency Task ID]

**References:**
- [Reference Link 1]
- [Reference Link 2]
```

### Task Skeleton for Incomplete Work

When work on a task cannot be completed in a single session, a task skeleton must be created:

```markdown
## Task Skeleton: [Task Name]

**Current Status:** [Status Symbol and Label]  
**Progress:** [Estimated percentage]

**Completed Items:**
- [Item 1]
- [Item 2]

**Remaining Work:**
- [Item 1] - [Notes/Instructions]
- [Item 2] - [Notes/Instructions]

**Known Issues:**
- [Issue 1]
- [Issue 2]

**Context/Notes for Continuation:**
[Important context that would help someone continue this work]
```

Task skeletons should be stored in `docs/tasks/skeletons/` with the naming convention `TASKID_taskname_skeleton.md`.

## Documentation Structure

### Required Documentation Elements

Every subsystem, component, and tool within EGOS must include the following documentation:

1. **README.md** - Overview document answering:
   - What is this component?
   - Why does it exist (purpose)?
   - How is it used?
   - Where are its dependencies?
   - Who maintains it?

2. **API_REFERENCE.md** (if applicable) - Detailed API documentation

3. **ARCHITECTURE.md** (for subsystems) - Architectural details and components

4. **QUICK_REFERENCE.md** - Essential information for rapid onboarding

### Standard Document Header

All documentation files must begin with the standard header:

```markdown
# [Document Title]

**Document ID:** [Category-Type-Number]  
**Version:** [X.Y.Z]  
**Last Updated:** [YYYY-MM-DD]  
**Status:** [Status Symbol and Label]

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - [ROADMAP](../../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
  - [MQP](../../core/MQP.md) - Master Quantum Prompt defining EGOS principles
- Other:
  - [MQP](../../core/MQP.md)
  - docs/standards/TASK_DOCUMENTATION_STANDARD.md




### Document Status Indicators

Documentation uses the same status indicators as tasks:

| Symbol | Status | Description |
|--------|--------|-------------|
| ✅ | Completed | Document is complete and up-to-date |
| ⏳ | In Development | Document is being actively written |
| ❌ | Outdated | Document needs updating due to system changes |
| ⚡ | Active | Document is current and actively maintained |
| ❓ | Needs Review | Document requires technical review |

## Cross-Referencing System (Mycelium Architecture)

### Principle of Interconnectedness

Every file in the EGOS system should reference at least two other relevant files, embodying the principle that "Life happens together, not alone. No one exists in isolation."

### Reference Format

References should be included at the bottom of each file using the following format:

```markdown
## References

@references:
- [Relative path to related file 1] - [Brief description of relationship]
- [Relative path to related file 2] - [Brief description of relationship]
```

### Cross-Reference Types

Different types of cross-references serve different purposes:

1. **Dependency References** - Components that this file depends on
2. **Extension References** - Components that extend or build upon this file
3. **Conceptual References** - Files that share conceptual relationships
4. **Process References** - Files involved in the same process

### Reference Discovery Tools

EGOS provides tools for maintaining and discovering references:

```bash
# Find all files referencing a specific component
python scripts/maintenance/docs/find_references.py --target subsystems/ETHIK/core/validator.py

# Suggest potential references for a file
python scripts/maintenance/docs/suggest_references.py --file subsystems/NEXUS/core/analyzer.py

# Validate references in a file
python scripts/maintenance/docs/validate_references.py --file docs/subsystems/KOIOS/ARCHITECTURE.md
```

## Roadmap Maintenance

### Roadmap Structure

The EGOS ROADMAP.md must be structured as follows:

```markdown
# EGOS Development Roadmap

## Current Focus Areas
[Summary of current priorities]

## Subsystem Status

### [Subsystem Name]
[Brief description and overall status]

#### Components:
| Component | Status | Next Action | Responsible | Target Date |
|-----------|--------|-------------|-------------|------------|
| [Name] | [Status] | [Action] | [Person] | [Date] |

#### Tasks:
[List of tasks following the standard task format]

### [Next Subsystem]
[...repeat structure...]

## Recently Completed
[List of recently completed high-level tasks]

## Future Initiatives
[List of planned future work]
```

### Roadmap Maintenance Schedule

The roadmap must be updated:

1. After completion of any task
2. Weekly (minimum) for status updates
3. At the beginning of each new development cycle
4. When priorities change significantly

## Memory Caching & LLM Guidance

### Session Context Requirements

Each development session with AI assistance should begin with a context summary:

```markdown
## Session Context Summary

**Date:** [Current Date]
**Focus:** [Primary Focus Area]
**Subsystems:** [Relevant Subsystems]

**Current Status:**
[Brief summary of current development status]

**Session Goals:**
- [Goal 1]
- [Goal 2]

**Open Issues:**
- [Issue 1]
- [Issue 2]
```

### Memory Caching

Important context should be cached in `.windsurfmemories/` using:

1. **System Memory** - Core principles, subsystem architecture
2. **Project Memory** - Current project context and goals
3. **Session Memory** - Session-specific information

### LLM Guidance

All LLM interactions should include:

1. **Clear role definitions** for the AI assistant
2. **Well-defined objectives** for the session
3. **Relevant constraints** and requirements
4. **Performance metrics** for evaluating success

## Community Empowerment for Vibe Coding

### Resources for New Users

The following resources must be maintained for vibe coders:

1. **VIBE_CODING_GUIDE.md** - Comprehensive guide for AI-assisted coding
2. **MODEL_SELECTION_GUIDE.md** - Guidance on choosing appropriate AI models
3. **TOKEN_OPTIMIZATION.md** - Strategies for efficient token usage
4. **RULES_CUSTOMIZATION.md** - Instructions for creating custom rules

### Community Documentation Standards

Community members contributing to EGOS should be guided to follow these documentation standards through:

1. Templates in `docs/templates/`
2. Automated validation tools
3. Clear contribution guidelines
4. Documentation examples

## Implementation and Adoption

### Documentation Audit

A documentation audit should be conducted monthly to:

1. Identify gaps in documentation
2. Verify adherence to standards
3. Update outdated information
4. Validate cross-references

### Training and Awareness

All team members should be trained on these standards through:

1. Documentation workshops
2. Regular reviews
3. Feedback mechanisms
4. Recognition for high-quality documentation

## References

@references:
- ../process/DOCUMENTATION_METRICS_DASHBOARD.md - Provides metrics for evaluating documentation quality
- ../guides/VIBE_CODING_GUIDE.md - Complements task management with AI-assisted coding practices
- ../../README.md - Root document that follows these standards
- ../../ROADMAP.md - Implementation of the roadmap standards defined here

✧༺❀༻∞ EGOS ∞༺❀༻✧