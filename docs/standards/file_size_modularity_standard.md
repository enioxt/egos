---
title: file_size_modularity_standard
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: file_size_modularity_standard
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/standards/file_size_modularity_standard.md

---
title: file_size_modularity_standard
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
ID: KOIOS-STD-002
Title: File Size and Modularity Standard
Author: Cascade AI (Initial Draft)
Date: 2024-08-01
Version: 0.1.1
Status: Draft
Scope: EGOS Codebase
Related: KOIOS-CODE-001, EGOS-PRINCIPLE-CONSCIOUS-MODULARITY, EGOS-PRINCIPLE-SRP, docs/guides/refactoring_large_files_guide.md
---

# File Size and Modularity Standard (KOIOS-STD-002)

## 1. Introduction

This standard defines guidelines for managing file size and promoting modularity within the EGOS codebase. Adherence to this standard supports the core EGOS principles of Conscious Modularity and Integrated Ethics by enhancing code readability, maintainability, testability, and reducing cognitive load.

## 2. Standard Definition

### 2.1 File Size Limit

- **Guideline:** Python files (`.py`) should generally not exceed **500 lines of code (LOC)**, excluding blank lines and comments.
- **Rationale:** Smaller files are easier to understand, review, test, and maintain. This aligns with the Single Responsibility Principle (SRP) and Conscious Modularity.
- **Exceptions:** Exceptions may be granted on a case-by-case basis with clear justification (e.g., unavoidable boilerplate, large data structures). Justification must be documented within the file's docstring or a related design document.

### 2.2 Modularity and Cohesion

- **Guideline:** Each file (module) should encapsulate a single, well-defined responsibility or cohesive set of functionalities.
- **Rationale:** High cohesion within modules and low coupling between modules improve system design and resilience to change.

## 3. Justification

- **Maintainability:** Smaller, focused modules are easier to modify without unintended side effects.
- **Readability:** Reduced file size improves comprehension and speeds up code navigation.
- **Testability:** Isolating responsibilities simplifies unit testing.
- **Collaboration:** Smaller units of work reduce merge conflicts and facilitate parallel development.
- **Alignment with EGOS:** Directly supports Conscious Modularity by encouraging thoughtful decomposition of the system.

## 4. Implementation and Enforcement

- **Code Reviews:** File size and modularity will be checked during code reviews.
- **Linting/Static Analysis:** Future integration with static analysis tools (potentially NEXUS) may automate checking for violations.
- **Refactoring:** Developers are encouraged to proactively refactor large or unfocused modules. See the [Refactoring Large Files Guide](</docs/guides/refactoring_large_files_guide.md>) for strategies.

## 5. Integration with NEXUS

NEXUS, the code analysis subsystem, plays a crucial role in monitoring and encouraging adherence to this standard. Integration involves:

- **Metric Tracking:** NEXUS should be configured to track relevant metrics for each file, including:
    - Lines of Code (LOC), excluding comments and blank lines.
    - Cyclomatic Complexity.
    - Cohesion metrics (e.g., LCOM - Lack of Cohesion in Methods, if applicable).
    - Coupling metrics (e.g., afferent and efferent coupling).
- **Reporting:** NEXUS analysis reports should:
    - Flag files exceeding the defined LOC threshold (KOIOS-STD-002 Section 2.1).
    - Highlight files with potentially low cohesion or high complexity, suggesting them as refactoring candidates even if below the strict LOC limit.
    - Provide dependency graphs or coupling information to aid in identifying appropriate boundaries for module extraction.
- **Automated Checks:** Where feasible, integrate checks into pre-commit hooks or CI/CD pipelines, leveraging NEXUS results to provide early feedback to developers.
- **Refactoring Guidance:** The analysis results from NEXUS should directly inform refactoring efforts, helping prioritize which files offer the most benefit from being modularized, as detailed in the [Refactoring Large Files Guide](</docs/guides/refactoring_large_files_guide.md>).

## 6. Revision History

- v0.1.1 (2024-08-01): Elaborated on NEXUS integration details.
- v0.1 (2024-08-01): Initial draft created by Cascade AI.