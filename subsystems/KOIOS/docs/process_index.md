---
title: Process Index
version: 1.0.0
status: Active
date: 2025-04-22
subsystem: KOIOS
tags: [documentation, egos, koios]
@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning



# KOIOS Process Index

This index provides a central registry for all documented operational processes within the KOIOS subsystem and the wider EGOS project. Ensure all new process documents are added here for discoverability.

## Core Processes

*   **<!-- TO_BE_REPLACED -->:** Defines how code and standards are updated, reviewed, and merged.
*   **<!-- TO_BE_REPLACED -->:** Procedures for addressing linting errors identified by automated tools.
*   **<!-- TO_BE_REPLACED -->:** Defines the structure and rules for Markdown Documentation Contracts (`.mdc` files).
*   **<!-- TO_BE_REPLACED -->:** The procedure for conducting comprehensive project health checks.
*   **<!-- TO_BE_REPLACED -->:** The master document outlining core project standards, conventions, and meta-rules (including this index requirement).
*   **<!-- TO_BE_REPLACED -->:** Defines the process for conducting in-depth strategic analysis using the standardized meta-prompt.
*   **<!-- TO_BE_REPLACED -->:** Defines the standard directory structure and core components for EGOS subsystems.
*   **<!-- TO_BE_REPLACED -->:** Specific rules for code syntax and style consistency.
*   **<!-- TO_BE_REPLACED -->:** Standard procedures for diagnosing and resolving issues.

## Mycelium Integration & Process Propagation

- **Requirement:** All processes and associated automation scripts MUST integrate with the Mycelium Network for:
    - **Discoverability:** Announcing capabilities and status.
    - **Coordination:** Sending/receiving requests or events relevant to the process.
    - **Health Reporting:** Providing status updates for monitoring.
    - **Propagation:** Broadcasting new insights or standards derived from the process (see `propagate_best_practices.py` tool).
- Each process document should detail its specific Mycelium topics, message contracts, and integration points.

## Continuous Improvement Propagation

- **Process:** Whenever a significant improvement or automation is developed, it must be generalized and propagated across EGOS using the `subsystems/KOIOS/tools/propagate_best_practices.py` script (or equivalent Mycelium broadcast).
- This ensures rapid, system-wide adoption of best practices.

## Validation Tools

*   **<!-- TO_BE_REPLACED -->:** Automates checks based on `project_diagnostic_standard.md`.
*   **<!-- TO_BE_REPLACED -->:** (Planned) Script to enforce `MDC_RULES_STANDARD.md`.
*   **<!-- TO_BE_REPLACED -->:** (Planned) Script to enforce `subsystem_structure.md`.
*   **(Future:** Add `validate_syntax.py`, `check_references.py`, etc.)

*This index should be kept up-to-date as new processes are defined or existing ones are modified.*
