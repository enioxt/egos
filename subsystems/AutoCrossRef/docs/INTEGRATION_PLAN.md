@references:
  - subsystems/AutoCrossRef/docs/INTEGRATION_PLAN.md

# AutoCrossRef Subsystem - Integration Plan

**Version:** 0.1
**Last Updated:** {{ CURRENT_DATE_ISO }}

## 1. Introduction

This document outlines how the AutoCrossRef subsystem integrates with existing EGOS tools, scripts, and workflows, particularly the cross-reference toolkit found in `C:\EGOS\scripts\cross_reference\`.

## 2. Integration with `file_reference_checker_ultra.py`

- **Purpose:** To determine if a potential cross-reference (source file to target file) already exists and to validate link targets.
- **Method:** 
  - The AutoCrossRef orchestrator will not call `file_reference_checker_ultra.py` as a separate process directly for each check due to performance considerations.
  - Instead, AutoCrossRef will **import and utilize core functions or classes** from `file_reference_checker_ultra.py` (or its refactored components if necessary) to perform these checks programmatically.
  - This requires `file_reference_checker_ultra.py` to be structured in a way that its core logic (e.g., parsing a file's existing references, checking if a specific target is referenced) is accessible.
  - Configuration (`config_ultra.yaml`) used by `file_reference_checker_ultra.py` for defining valid paths and exclusions will be respected.
- **Data Exchange:** AutoCrossRef will pass file paths and target paths to the imported functions and receive boolean (exists/doesn't exist) or structured data about existing references.

## 3. Integration with `inject_standardized_references.py`

- **Purpose:** To safely modify files by adding new, approved cross-references to the `@references:` block.
- **Method:**
  - Similar to the above, AutoCrossRef will aim to **import and use core functions/classes** from `inject_standardized_references.py` for file modification tasks.
  - This includes leveraging its backup mechanisms, dry-run capabilities (if exposed programmatically), and logic for correctly formatting and inserting into the `@references:` block.
  - If direct import is not feasible without significant refactoring of `inject_standardized_references.py`, an alternative is for AutoCrossRef to prepare a list of changes and then invoke `inject_standardized_references.py` as a command-line tool with specific instructions (less ideal but a fallback).
- **Data Exchange:** AutoCrossRef will provide the source file path and the details of the reference to be added (target path, link text).

## 4. Integration with `config_ultra.yaml`

- AutoCrossRef will read `config_ultra.yaml` to understand project-wide inclusion/exclusion rules for file scanning, valid path definitions, and other relevant settings that the underlying tools use.
- `autocrossref_config.yaml` will provide settings specific to AutoCrossRef's higher-level logic (e.g., candidate detection patterns, directories to prioritize for automated runs).

## 5. Workflow Integration

- **Manual Trigger:** Initially, AutoCrossRef will be a CLI tool run manually by developers.
- **CI/CD (Future):**
  - Could be run in a dry-run/suggestion mode in a CI pipeline to flag missing references in pull requests.
  - Automated injection in CI is a more advanced step requiring high confidence and careful consideration.

## 6. Potential Refactoring of Existing Scripts

- To facilitate cleaner programmatic integration, minor refactoring of `file_reference_checker_ultra.py` and `inject_standardized_references.py` might be necessary to expose their core logic as reusable functions/classes. This should be done carefully to maintain their existing CLI functionality.
  - Example: Separating file I/O and parsing logic from the main execution flow.

## 7. Error Handling and Fallbacks

- If programmatic integration proves too complex initially, AutoCrossRef can fall back to calling the existing scripts as subprocesses, parsing their output. This is less efficient but provides a phased approach.