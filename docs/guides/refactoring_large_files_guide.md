---
title: refactoring_large_files_guide
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: refactoring_large_files_guide
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/guides/refactoring_large_files_guide.md

---
title: refactoring_large_files_guide
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
ID: KOIOS-GUIDE-001
Title: Refactoring Large Files Guide
Author: Cascade AI (Initial Draft)
Date: 2024-08-01
Version: 0.1
Status: Draft
Scope: EGOS Codebase Development
Related: KOIOS-STD-002 (File Size and Modularity Standard)
---

# Refactoring Large Files Guide (KOIOS-GUIDE-001)

## 1. Introduction

This guide provides strategies and best practices for refactoring large files within the EGOS codebase to comply with the [File Size and Modularity Standard (KOIOS-STD-002)](</docs/standards/file_size_modularity_standard.md>). Refactoring aims to improve code structure, maintainability, and adherence to EGOS principles like Conscious Modularity without altering external behavior.

## 2. Identifying Candidates for Refactoring

Files exceeding the recommended size limit (e.g., 500 LOC) are primary candidates. Other indicators include:

- **Low Cohesion:** The file handles multiple unrelated responsibilities.
- **High Complexity:** Functions within the file have high cyclomatic complexity.
- **Difficult Testing:** Unit testing parts of the file in isolation is challenging.
- **Frequent Merge Conflicts:** Multiple developers often modify the same large file.
- **NEXUS Analysis:** Reports from NEXUS highlighting size, complexity, or coupling issues.

## 3. Refactoring Strategies

Choose strategies based on the specific structure and responsibilities within the large file:

### 3.1 Extract Class

- **When:** A subset of data and methods within a large class seem to form a cohesive unit or represent a distinct concept.
- **How:** Create a new class, move the relevant fields and methods to it. Establish a relationship (composition or association) between the original and new class.

### 3.2 Extract Module/Sub-package

- **When:** A large file contains multiple related classes or functions that could logically be grouped elsewhere.
- **How:** Create a new Python file (module) or a directory with an `__init__.py` (sub-package). Move the related code into the new module(s). Update imports accordingly.

### 3.3 Extract Function/Method

- **When:** A function or method is too long or performs multiple distinct steps.
- **How:** Identify logical sub-steps within the long function. Extract each sub-step into a new, well-named private or public function/method. Call the new functions from the original one.

### 3.4 Introduce Facade/Interface

- **When:** A module exposes too many internal details, leading to high coupling.
- **How:** Create a simpler interface (e.g., a Facade class or a set of public functions) that delegates calls to the internal components. Clients interact only with the facade.

### 3.5 Separate Concerns (e.g., Data Access, Business Logic, Presentation)

- **When:** A single file mixes different architectural concerns.
- **How:** Create separate modules for each concern (e.g., `_database.py`, `_processing.py`, `_utils.py`). Move relevant code into these modules.

## 4. Refactoring Process Steps

1.  **Backup:** Ensure the code is under version control (CRONOS backup recommended before major refactoring).
2.  **Analyze:** Understand the code, identify responsibilities, and choose a refactoring strategy.
3.  **Test:** Ensure existing tests cover the code to be refactored. Write tests if coverage is insufficient.
4.  **Refactor Incrementally:** Apply small, testable changes. Run tests frequently.
5.  **Review:** Have the changes reviewed by peers.
6.  **Document:** Update any relevant documentation, including docstrings and KOIOS references.

## 5. Tooling Support

- **IDE Refactoring Tools:** Leverage built-in IDE capabilities (e.g., Rename Symbol, Extract Method).
- **NEXUS:** Use NEXUS analysis to guide refactoring decisions.
- **Linters/Formatters (Ruff):** Ensure code quality throughout the process.

## 6. Revision History

- v0.1 (2024-08-01): Initial draft created by Cascade AI.