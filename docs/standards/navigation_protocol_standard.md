---
title: SEGURO Navigation Protocol Standard
version: 1.0.1
status: Active
date_created: 2025-05-10
date_modified: 2025-05-17
authors: [EGOS Team, Cascade AI]
description: "Defines the SEGURO (Structured Ecosystem for Guided Unified Relocation Operations) protocol, establishing standard practices for safe directory navigation, context tracking, and traceable operations during development within the EGOS project."
file_type: standard
scope: project-wide
primary_entity_type: protocol_standard
primary_entity_name: SEGURO Navigation Protocol
tags: [seguro, navigation, protocol, standard, trust_weaver, koios, development_guideline, context_management]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/standards/navigation_protocol_standard.md

# Directory Navigation Protocol (SEGURO)

**@module**: CORE-PRACTICES
**@author**: EGOS Team
**@version**: 1.0.0
**@date**: 2025-05-04
**@status**: development

- Core References:
  - [MQP](../../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [MEMORY: Directory Navigation Protocol](../../../memory:\\f8bc36de-3c61-45bb-a995-59b85efb95db)
- Related Standards:
  - [redundancy_diagnostics_standard.md](../../../.\redundancy_diagnostics_standard.md) - EGOS Redundancy Diagnostic System
  - [file_size_modularity_standard.md](../../../.\file_size_modularity_standard.md) - File size guidelines

## Summary

This document establishes the SEGURO Protocol (Structured Ecosystem for Guided Unified Relocation Operations) as a standard practice to ensure that navigation between directories during development is safe, traceable, and reversible, reducing the risks of operations in incorrect contexts.

## Objectives

1. Ensure complete traceability of operations between directories
2. Prevent accidental file modifications due to context confusion
3. Establish standardized practices for operations involving multiple directories
4. Facilitate auditing of context changes
5. Preserve the structural integrity of the EGOS file system

## SEGURO Protocol Principles

### 1. Complete Traceability

- Explicitly record each directory change
- Document the source and destination directory in each operation
- Maintain a "breadcrumb trail" for safe return

### 2. Clear Operation Context

- Before any file operation, confirm current context
- Prefix commands with directory indicator
- Use absolute paths for operations between directories

### 3. Guaranteed Return

- Implement a mechanism for "return to original context"
- After tasks in different directories, explicitly return
- Verify that the return was successful

### 4. Scope Markers

- Start operation block with `[START_DIRECTORY: /absolute/path]`
- End operation block with `[END_DIRECTORY: /absolute/path, RETURN: /original/path]`
- Validate consistency of markers

## Implementation Process

### 1. Starting Operation in a New Directory

```
[START_DIRECTORY: /new/absolute/path]
ORIGIN: /current/absolute/path
REASON: Clear justification for directory change
ESTIMATED DURATION: X operations or Y minutes
[START_DIRECTORY: /new/absolute/path]
ORIGIN: /current/absolute/path
REASON: Clear justification for directory change
ESTIMATED DURATION: X operations or Y minutes
```

### 2. During Operations

- **MANDATORY**: Prefix each command with directory indicator:

```
[@DIR=/path]: <command or operation>
```

- **MANDATORY**: Document all changes made before changing directories:
  - Update the subsystem-specific ROADMAP
  - Document in relevant README.md files
  - Update the main ROADMAP when appropriate

### 3. Completion of Operations

```
[END_DIRECTORY: /new/absolute/path]
OPERATIONS PERFORMED: List of changes made
AFFECTED FILES: List of modified files
RETURN: /original/absolute/path
```

### 4. Post-Return Verification

```
[CONTEXT_VERIFICATION]
CURRENT DIRECTORY: /verified/absolute/path
STATUS: Success/Failure
```

## Mandatory Documentation During Directory Transitions

A fundamental rule of the SEGURO protocol is that every directory change must be preceded by complete documentation of the work done in the current directory:

1. **Mandatory Completion Documentation**:
   - NEVER change directories without documenting the work done in the current directory
   - Update the ROADMAP.md and README.md files of the current subsystem
   - Record progress in any other relevant documentation files

2. **Pending Items Verification**:
   - Before leaving a directory, verify that all modified items have been documented
   - Confirm that all completed tasks have been marked in the relevant roadmaps
   - Ensure that cross-references have been appropriately updated

3. **Transition Report**:
   - When concluding work in a directory, explicitly document:
     - What was done (summary of changes)
     - What still needs to be done (pending items)
     - Recommended next steps

4. **Centralized Documentation**:
   - Any significant change must be reflected in the central ROADMAP
   - Changes that affect multiple subsystems must be documented in each subsystem

This mandatory continuous documentation ensures that knowledge is not lost during context transitions and that the current state of the project is always reflected in the documentation.

## Model for Global Rules

When implementing global rules:

1. Identify the appropriate directory for global rules (`/global/rules` or equivalent)
2. Follow the SEGURO protocol for navigation
3. Explicitly document the global scope of the rule
4. Return to the original context after implementation

## Technical Implementation

The SEGURO Protocol will be implemented through the following components:

### 1. Support Tools

- **DirStack**: Implement directory stack for tracking
- **ContextVerifier**: Verify context before critical operations
- **PathResolver**: Resolve relative paths to absolute paths
- **ReturnGuarantee**: Ensure return even in case of failures

### 2. IDE Integration

Extensions for IDEs such as VS Code that:

- Display the current context visibly
- Alert about operations in different contexts
- Provide commands to manage the navigation stack

### 3. CLI Tools

- `egos-dir-stack push <path>` - Adds a directory to the stack
- `egos-dir-stack pop` - Returns to the previous directory
- `egos-dir-context check` - Checks and reports the current context

## Application Scenarios

### Scenario 1: Implementing a Global Rule

```
[START_DIRECTORY: c:\EGOS\docs\standards]
ORIGIN: c:\EGOS\apps\dashboard\component.py
REASON: Implementation of global rule for EGOS
ESTIMATED DURATION: 3 operations

[@DIR=c:\EGOS\docs\standards]: <operation 1>
[@DIR=c:\EGOS\docs\standards]: <operation 2>
[@DIR=c:\EGOS\docs\standards]: <operation 3>

[END_DIRECTORY: c:\EGOS\docs\standards]
OPERATIONS PERFORMED: Creation of standard document, update of references
AFFECTED FILES: new_standard.md, references.md
RETURN: c:\EGOS\apps\dashboard\component.py

[CONTEXT_VERIFICATION]
CURRENT DIRECTORY: c:\EGOS\apps\dashboard\component.py
STATUS: Success
```

### Scenario 2: Operations in Multiple Subsystems

```
[START_DIRECTORY: c:\EGOS\mycelium]
ORIGIN: c:\EGOS\apps\dashboard\component.py
REASON: Integration of messaging between subsystems
ESTIMATED DURATION: 2 operations

[@DIR=c:\EGOS\mycelium]: <operation 1>
[@DIR=c:\EGOS\mycelium]: <operation 2>

[START_DIRECTORY: c:\EGOS\trust_weaver]
ORIGIN: c:\EGOS\mycelium
REASON: Verification of security policies
ESTIMATED DURATION: 1 operation

[@DIR=c:\EGOS\trust_weaver]: <operation 1>

[END_DIRECTORY: c:\EGOS\trust_weaver]
OPERATIONS PERFORMED: Policy verification
AFFECTED FILES: security_policy.py
RETURN: c:\EGOS\mycelium

[END_DIRECTORY: c:\EGOS\mycelium]
OPERATIONS PERFORMED: Implementation of events
AFFECTED FILES: event_broker.py, event_schemas.py
RETURN: c:\EGOS\apps\dashboard\component.py

[CONTEXT_VERIFICATION]
CURRENT DIRECTORY: c:\EGOS\apps\dashboard\component.py
STATUS: Success
```

## Validation and Compliance

Compliance with this protocol will be monitored through:

1. Code reviews that verify the presence of appropriate markers
2. Automated tools to validate context integrity
3. Alerts for operations performed in inappropriate contexts
4. Log analysis to identify problematic navigation patterns

## Gradual Adoption

The implementation of this protocol will follow these phases:

1. **Phase 1**: Documentation and awareness
2. **Phase 2**: Manual adoption by developers
3. **Phase 3**: Implementation of support tools
4. **Phase 4**: Integration with CI/CD for automatic validation
5. **Phase 5**: Adoption as a mandatory requirement for all operations