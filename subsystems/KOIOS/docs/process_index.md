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

*   **[Code Evolution Process](./code_evolution_process.md):** Defines how code and standards are updated, reviewed, and merged.
*   **[Lint Error Resolution](./lint_error_resolution_processes.md):** Procedures for addressing linting errors identified by automated tools.
*   **[MDC Rules Standard](./MDC_RULES_STANDARD.md):** Defines the structure and rules for Markdown Documentation Contracts (`.mdc` files).
*   **[Project Diagnostic Standard](./project_diagnostic_standard.md):** The procedure for conducting comprehensive project health checks.
*   **[Standards](./STANDARDS.md):** The master document outlining core project standards, conventions, and meta-rules (including this index requirement).
*   **[Strategic Analysis Process](./processes/koios_strategic_analysis_process.md):** Defines the process for conducting in-depth strategic analysis using the standardized meta-prompt.
*   **[Subsystem Structure](./subsystem_structure.md):** Defines the standard directory structure and core components for EGOS subsystems.
*   **[Syntax Standardization](./syntax_standardization.md):** Specific rules for code syntax and style consistency.
*   **[Troubleshooting Guide](./troubleshooting_guide.md):** Standard procedures for diagnosing and resolving issues.

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

*   **[Project Diagnostic Script](../tools/run_full_diagnostic.py):** Automates checks based on `project_diagnostic_standard.md`.
*   **[MDC Rules Validator](../tools/validate_mdc_rules.py):** (Planned) Script to enforce `MDC_RULES_STANDARD.md`.
*   **[Subsystem Structure Validator](../tools/validate_subsystem_structure.py):** (Planned) Script to enforce `subsystem_structure.md`.
*   **(Future:** Add `validate_syntax.py`, `check_references.py`, etc.)

*This index should be kept up-to-date as new processes are defined or existing ones are modified.*
