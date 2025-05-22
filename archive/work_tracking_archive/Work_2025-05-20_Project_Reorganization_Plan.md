# EGOS Project Reorganization Plan

**Last Updated:** 2025-05-20

## 1. Introduction and Objectives

This document outlines the comprehensive plan for reorganizing the EGOS project structure. The primary goal is to establish a clean, scalable, and AI-friendly directory structure that enhances navigability, maintainability, and collaboration for both human developers and AI agents.

**Key Objectives:**

*   Consolidate all project documentation, scripts, and core code into a logically organized framework.
*   Eliminate redundant and empty directories.
*   Unify similarly named folders and establish consistent naming conventions.
*   Define clear guidelines for future documentation, development processes, and AI interaction.
*   Improve overall project clarity and accessibility.

## 2. Current State Analysis Summary

The EGOS project currently faces several challenges related to its structure:

*   **Fragmented Documentation:** Information is dispersed across various locations, making it difficult to find and maintain a single source of truth.
*   **Inconsistent Structures:** Different parts of the project may follow varied organizational patterns.
*   **Redundancy:** Duplicate files and information exist, leading to potential inconsistencies.
*   **Lack of Clear AI Guidance:** The current structure is not optimally designed for AI agent interaction and understanding.
*   **Initial Artifacts Created:**
    *   `C:\EGOS\recovery_analysis\documentation_migration_map.csv`: Created to track all documentation files. Current status: All listed items are "Pending" investigation and migration.
    *   `C:\EGOS\recovery_analysis\docs_reorganization_log.txt`: Contains logs from an initial script that migrated files from an old `C:\EGOS\docs` directory to the new staging `C:\EGOS\docs_egos` directory.
*   **Outstanding Issues:** A note from a previous session indicated four files were missing. Their status needs to be formally resolved during the verification phase.

## 3. Adopted Reorganization Strategy

The reorganization will be guided by the following strategic principles:

*   **Centralized Documentation Root:** A new, unified documentation root will be established at `C:\EGOS\docs\`. During the transition, this will be staged in `C:\EGOS\docs_egos\`.
*   **Standardized Directory Structure:** The `docs` directory will feature a clear, hierarchical structure:
    *   `00_project_overview/`: Core project documents (README, Roadmap, Architecture, Principles, Strategy).
    *   `01_subsystems/`: Information and links related to major EGOS subsystems (KOIOS, ETHIK, HARMONY, CORUJA, NEXUS, etc.).
    *   `02_koios_standards/`: All KOIOS-defined standards, guides (including AI collaboration), protocols, and templates.
    *   `03_processes/`: Documented operational procedures, workflows (e.g., development, CI/CD, issue management).
    *   `04_products_services/`: Documentation related to specific products or services offered by EGOS (e.g., website).
    *   `05_technical_references/`: Glossaries, deep-dive technical explanations, API references.
    *   `06_community_contribution/`: Contribution guidelines, code of conduct, licensing.
    *   `zz_archive/`: Archived materials, planning records no longer active but retained for historical purposes.
*   **Master Documentation Index:** A `SUMMARY.md` file within the `docs` root will serve as the primary, human-readable, and AI-parsable index for all documentation.
*   **AI Guidance File:** A `.windsurfrules` file will be placed in the project root (or `docs` root) to provide specific instructions and context for AI agents interacting with the EGOS codebase and documentation.
*   **Subsystem Documentation Integration:** Documentation for key subsystems like ETHIK, HARMONY, KOIOS, and CORUJA will be consolidated and integrated into the `01_subsystems/` directory.
*   **Component Centralization:** All reorganization efforts will adhere to the EGOS Component Centralization System, leveraging `index.json` and associated verification protocols to prevent duplication.

### 3.1. Fallback Procedures and Alternative Tooling

In situations where standard tools (e.g., the `filesystem` MCP server) encounter limitations or failures, particularly for operations like listing extensive directory structures, creating very large files, or experiencing persistent errors, the Windsurf integrated terminal provides a robust fallback mechanism. Utilizing terminal commands directly can offer greater control and overcome such challenges, ensuring project continuity.

## 4. Phased Action Plan

The reorganization will be executed in the following phases:

### Phase 0: Final Planning & Preparation (Current)

*   **Task 0.1: Finalize Reorganization Plan Document.**
    *   **Status:** In Progress (This document).
    *   **Action:** Ensure this plan is comprehensive and agreed upon.
*   **Task 0.2: Perform Full Project Backup.**
    *   **Status:** Pending.
    *   **Responsibility:** USER.
    *   **Note:** Critical before proceeding with any file move/delete operations.

### Phase 1: Inventory, Verification & Initial Cleanup

*   **Task 1.1: Resolve Status of Previously Identified Missing Files.**
    *   **Status:** Pending.
    *   **Action:** If a specific list of the four files is unavailable, systematically verify the existence of each file listed in `documentation_migration_map.csv` at both its `Original_Path` and `New_SSoT_Path`. Update map accordingly.
*   **Task 1.2: Conduct Comprehensive Scan of `C:\EGOS\`.**
    *   **Status:** Pending.
    *   **Action:** Use `list_dir` and/or terminal commands (`Get-ChildItem -Recurse`) to generate a complete inventory of all files and directories within `C:\EGOS\`.
    *   **Action:** Identify and list all empty directories.
    *   **Action:** Identify potential duplicates or uncatalogued files not present in `documentation_migration_map.csv`.
*   **Task 1.3: Update `documentation_migration_map.csv` and Plan Initial Cleanup.**
    *   **Status:** Pending.
    *   **Action:** Add any newly discovered documentation files to the map.
    *   **Action:** Mark empty directories and confirmed redundant files for deletion in the map or a separate cleanup list.

### Phase 2: Documentation Migration & SSoT Establishment

*   **Task 2.1: Systematically Process `documentation_migration_map.csv`.**
    *   **Status:** Pending.
    *   **Action:** For each file marked "Pending" or requiring action:
        *   Verify existence at `Original_Path` (if not already done).
        *   Copy or move the file to its designated `New_SSoT_Path` within `C:\EGOS\docs_egos\`.
        *   Handle files requiring merge or review as per notes in the map.
        *   Update the `Migration_Status` in `documentation_migration_map.csv` (e.g., "Migrated to docs_egos", "Reviewed", "Error").
*   **Task 2.2: Create and Populate `C:\EGOS\docs_egos\SUMMARY.md`.**
    *   **Status:** Pending.
    *   **Action:** Generate content reflecting the new `docs_egos` structure, linking to key READMEs and documents in each main section.
*   **Task 2.3: Create and Populate Project `.windsurfrules`.**
    *   **Status:** Pending.
    *   **Action:** Define rules for AI interaction, referencing key documentation paths and project standards. (Location: `C:\EGOS\.windsurfrules` or `C:\EGOS\docs_egos\.windsurfrules`).
*   **Task 2.4: Integrate Subsystem Documentation.**
    *   **Status:** Pending.
    *   **Action:** Consolidate and move/link essential documentation for ETHIK, HARMONY, KOIOS, CORUJA, NEXUS, etc., into their respective subdirectories under `C:\EGOS\docs_egos\01_subsystems\`.
*   **Task 2.5: Consolidate Core Project `ROADMAP.md` and `README.md`.**
    *   **Status:** Pending.
    *   **Action:** Review all existing `ROADMAP.md` and `README.md` variants. Synthesize their content into the primary `C:\EGOS\docs_egos\00_project_overview\ROADMAP.md` and `C:\EGOS\docs_egos\README.md`.

### Phase 3: Structure Finalization & Validation

*   **Task 3.1: Review and Validate `C:\EGOS\docs_egos\` Structure and Content.**
    *   **Status:** Pending.
    *   **Action:** Thoroughly review the reorganized content for completeness, correctness, and adherence to standards.
*   **Task 3.2: Rename `C:\EGOS\docs_egos\` to `C:\EGOS\docs\`.**
    *   **Status:** Pending.
    *   **Action:** Once validation is complete, perform the rename operation.
*   **Task 3.3: Update Project-Level `ROADMAP.md` and `README.md` (if separate from docs).**
    *   **Status:** Pending.
    *   **Action:** Ensure any root-level `ROADMAP.md` or `README.md` correctly points to or summarizes the new `docs` structure.
*   **Task 3.4: Perform Final Link Integrity Check.**
    *   **Status:** Pending.
    *   **Action:** Use tools or manual checks to ensure all internal links within the new `docs` structure are valid.

### Phase 4: Post-Implementation & Iteration

*   **Task 4.1: Gather Feedback.**
    *   **Status:** Pending.
    *   **Action:** Solicit feedback from team members and stakeholders on the new structure.
*   **Task 4.2: Iterate on Documentation and Structure.**
    *   **Status:** Pending.
    *   **Action:** Make adjustments based on feedback and evolving project needs.
*   **Task 4.3: Update `ONBOARDING.md`.**
    *   **Status:** Pending.
    *   **Action:** Ensure the project onboarding documentation reflects the new structure and guides contributors effectively.

## 5. Key Files & Artifacts (Tracking)

*   `C:\EGOS\Work_2025-05-20_Project_Reorganization_Plan.md` (This document)
*   `C:\EGOS\recovery_analysis\documentation_migration_map.csv`
*   `C:\EGOS\recovery_analysis\docs_reorganization_log.txt`
*   `C:\EGOS\docs_egos\` (Staging directory for `C:\EGOS\docs\`)
*   `C:\EGOS\docs_egos\SUMMARY.md` (To be created)
*   `C:\EGOS\.windsurfrules` or `C:\EGOS\docs_egos\.windsurfrules` (To be created)
*   `C:\EGOS\index.json` (Component Centralization Manifest)

## 6. Notes & Considerations

*   All activities must adhere to KOIOS standards for documentation, naming, and structure.
*   The EGOS Component Centralization Protocol must be followed for any new components or significant restructuring to avoid duplication.
*   Regular communication and updates will be provided throughout the reorganization process.
