# EGOS Documentation - Phase 2: Execution Plan

**Date:** 2025-05-20

**Objective:** To detail the actionable steps for executing the consolidation and cleanup of the EGOS documentation system, based on the findings and recommendations in `Work_2025-05-20_Documentation_Diagnosis.md`.

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Guiding Principles for Execution](#2-guiding-principles-for-execution)
3.  [Detailed Action Plan (Based on Diagnostic Recommendations)](#3-detailed-action-plan)
    *   [3.1 Rec. 7.1: Unified Hierarchy & SSoT](#31-rec-71-unified-hierarchy--ssot)
        *   [3.1.1 Define Target Directory Structure](#311-define-target-directory-structure)
        *   [3.1.2 Map Document Types to SSoT Locations](#312-map-document-types-to-ssot-locations)
        *   [3.1.3 De-duplication and Migration Process](#313-de-duplication-and-migration-process)
        *   [3.1.4 Identify and Process Sparse/Empty Directories](#314-identify-and-process-sparseempty-directories)
    *   [3.2 Rec. 7.2: Formalize "Docs-as-Code"](#32-rec-72-formalize-docs-as-code)
        *   [3.2.1 Standard Subsystem Docs Structure](#321-standard-subsystem-docs-structure)
        *   [3.2.2 Aggregation/Linking Mechanism](#322-aggregationlinking-mechanism)
    *   [3.3 Rec. 7.3: Address Critical Content Gaps](#33-rec-73-address-critical-content-gaps)
        *   [3.3.1 Plan for Missing Subsystem READMEs (CHRONICLER, KARDIA, etc.)](#331-plan-for-missing-subsystem-readmes)
        *   [3.3.2 Plan for KOS_process_index.md](#332-plan-for-kos_process_indexmd)
    *   [3.4 Rec. 7.4: Develop KOIOS Documentation Standards Guide](#34-rec-74-develop-koios-documentation-standards-guide)
    *   [3.5 Rec. 7.5: Implement Robust Linking Strategy](#35-rec-75-implement-robust-linking-strategy)
    *   [3.6 Rec. 7.6: Clarify Documentation Versioning Strategy](#36-rec-76-clarify-documentation-versioning-strategy)
    *   [3.7 Rec. 7.7: Enhance Discoverability (Index & Search)](#37-rec-77-enhance-discoverability-index--search)
    *   [3.8 Rec. 7.8: Integrate Working Documents](#38-rec-78-integrate-working-documents)
4.  [Tooling & Support Requirements](#4-tooling--support-requirements)
5.  [Timeline & Milestones (Preliminary)](#5-timeline--milestones-preliminary)
6.  [Risk Assessment & Mitigation](#6-risk-assessment--mitigation)

---

## 1. Introduction

This document outlines the detailed execution plan for Phase 2 of the EGOS Documentation Optimization initiative: "Execute Consolidation & Cleanup." It builds directly upon the findings and recommendations presented in the `Work_2025-05-20_Documentation_Diagnosis.md` report.

The primary goal of this phase is to transform the current state of EGOS documentation into a more organized, coherent, discoverable, and maintainable system. This involves establishing a unified information architecture, eliminating redundancy, addressing critical content gaps, and reinforcing documentation standards under the stewardship of KOIOS.

This plan details specific actions, assigns priorities, and will serve as a roadmap for the practical work of reorganizing the documentation assets.

## 2. Guiding Principles for Execution

The execution of Phase 2 will adhere to the following principles, aligned with EGOS core values and KOIOS standards:

*   **Minimize Disruption:** Changes will be implemented methodically to minimize disruption to ongoing development activities. Where possible, redirection or clear communication will be provided for moved content.
*   **Clarity and Simplicity:** The target information architecture will prioritize clarity and ease of navigation for all users (human and AI).
*   **Single Source of Truth (SSoT):** A core objective is to establish an SSoT for all key documentation artifacts, eliminating ambiguity and reducing maintenance.
*   **KOIOS Standards Alignment:** All reorganization and content creation/modification efforts will strive to align with established and emerging KOIOS documentation standards (including MDC, naming conventions, and metadata).
*   **Iterative Progress & Validation:** While the plan is comprehensive, execution may involve iterative steps, especially for complex tasks. Validation checks will be performed at key milestones.
*   **Preserve Value:** Existing valuable content will be preserved and migrated to the new structure. Deletion will only occur after careful consideration and confirmation of redundancy or obsolescence.
*   **Systematic Cartography:** The reorganization will aim to reflect the relationships between components and concepts more clearly, embodying the Systemic Cartography principle.
*   **Conscious Modularity:** Documentation will be organized to reflect the modular nature of EGOS subsystems, ensuring that information is appropriately scoped and self-contained where logical.
*   **Prioritize Impact:** Efforts will be prioritized based on their potential to deliver the most significant improvements to discoverability, usability, and completeness.
*   **Collaboration & Communication:** This phase will require clear communication. Changes and rationale will be documented (e.g., in Git commit messages, updates to this plan or related working documents).

## 3. Detailed Action Plan (Based on Diagnostic Recommendations)

This section breaks down each recommendation from `Work_2025-05-20_Documentation_Diagnosis.md` (Section 7) into specific, actionable sub-tasks. Priorities are inherited from the diagnostic report.

### 3.1 Rec. 7.1: Establish a Unified Documentation Hierarchy & Single Source of Truth (SSoT)

**Priority:** High

**Objective:** To create a clear, logical, and centralized structure for all EGOS documentation, establishing definitive locations for all content types and eliminating redundancy.

#### 3.1.1 Define Target Directory Structure

*   **Action 3.1.1.1:** Propose a new root documentation directory. Suggestion: `C:\EGOS\docs_egos\` (or `C:\EGOS\documentation\`) to clearly distinguish from the old `docs\` during transition and to house all unified documentation.
*   **Action 3.1.1.2:** Define primary top-level categories within the new root. Initial proposal:
    *   `docs_egos/00_project_overview/`: For `MQP.md`, `ARCHITECTURE.MD`, `ROADMAP.md`, `STRATEGY.MD` (single, authoritative versions).
    *   `docs_egos/01_subsystems/`: To house aggregated views or links to subsystem documentation (see Rec. 7.2).
    *   `docs_egos/02_koios_standards/`: For all KOIOS standards, guides, MDCs, `ai_handover_standard.mdc`, etc.
    *   `docs_egos/03_processes/`: For operational procedures, workflows (e.g., `human_ai_collaboration_guidelines.md`).
    *   `docs_egos/04_products_services/`: For documentation related to specific EGOS products or services (e.g., the EGOS Website).
    *   `docs_egos/05_technical_references/`: For glossaries, technical deep-dives not specific to one subsystem, testing strategies.
    *   `docs_egos/06_community_contribution/`: For contributor guides, code of conduct, licensing information (beyond `LICENSE` file in root).
    *   `docs_egos/zz_archive/`: For explicitly archived, non-current materials, if any need to be retained outside of Git history for specific reasons.
*   **Action 3.1.1.3:** Review and refine proposed top-level categories and their intended scope.
*   **Action 3.1.1.4:** Define clear naming conventions for files and directories within this new structure (e.g., `lowercase-with-hyphens`, subsystem prefixes like `KOS_` for KOIOS-specific documents).

#### 3.1.2 Map Document Types to SSoT Locations

*   **Action 3.1.2.1:** Create a comprehensive inventory of all existing `.md`, `.mdc`, and other key documentation files across the current dispersed locations.
*   **Action 3.1.2.2:** For each identified document (or type of document), assign it to a definitive SSoT path within the newly defined target directory structure.
*   **Action 3.1.2.3:** Document this mapping in a temporary manifest file (e.g., `C:\EGOS\recovery_analysis\documentation_migration_map.csv` or a Markdown table) to guide the migration process. This map should identify the original path and the new target SSoT path.

#### 3.1.3 De-duplication and Migration Process

*   **Action 3.1.3.1:** For identified duplicate documents (e.g., multiple `STRATEGY.MD` files), perform a content comparison (diff) to identify the most comprehensive and up-to-date version. If necessary, merge content from duplicates into the chosen SSoT version.
*   **Action 3.1.3.2:** Systematically move each document from its current location to its designated SSoT path based on the `documentation_migration_map.csv`.
*   **Action 3.1.3.3:** For files that are truly superseded or redundant after content merging, list them in `C:\EGOS\recovery_analysis\deletion_candidates.txt` with a clear rationale. Actual deletion will occur after review.
*   **Action 3.1.3.4:** Where appropriate (e.g., for high-traffic old locations), consider placing temporary "redirect" stubs or updating prominent links to point to the new SSoT location.

#### 3.1.4 Identify and Process Sparse/Empty Directories

*   **Action 3.1.4.1:** During the inventory (Action 3.1.2.1) and migration process, identify all directories that are empty or contain very few files (e.g., 1-4 files), as per user guidance.
*   **Action 3.1.4.2:** For each sparse/empty directory, assess if its content can be merged into a more appropriate, consolidated location within the new SSoT structure. Add this to the `documentation_migration_map.csv`.
*   **Action 3.1.4.3:** If a sparse directory's distinct identity is not valuable, mark the directory itself for deletion in `deletion_candidates.txt` after its contents have been migrated.
*   **Action 3.1.4.4:** This process will primarily apply to the *old* directory structure. The *new* `docs_egos/` structure should be designed to avoid unnecessary sparseness from the outset.

### 3.2 Rec. 7.2: Formalize and Promote the "Docs-as-Code" Approach

**Priority:** High

**Objective:** To officially adopt and standardize the practice of maintaining technical subsystem documentation alongside its source code, ensuring it is current, developer-centric, and integrated into the overall EGOS knowledge base.

#### 3.2.1 Standard Subsystem Docs Structure

*   **Action 3.2.1.1:** Define a standard subdirectory name within each `C:\EGOS\subsystems\<SUBSYSTEM_NAME>\` directory for its documentation. Proposal: `C:\EGOS\subsystems\<SUBSYSTEM_NAME>\docs\`.
*   **Action 3.2.1.2:** Specify a standard set of essential documents within each subsystem's `docs\` directory. Minimum requirements:
    *   `README.md`: (Already existing in many) Detailed overview, purpose, core functionalities, key components, setup/build instructions, and quick start guide for the subsystem.
    *   `API_REFERENCE.md`: (If applicable) Detailed documentation of public APIs, data Pydantic schemas, Mycelium message formats, etc.
    *   `TECHNICAL_DESIGN.md`: Deeper architectural decisions, internal workings, data flow specific to the subsystem.
    *   `USAGE_EXAMPLES.md`: Practical examples of how to use or interact with the subsystem.
    *   `CONTRIBUTING.md`: Guidelines specific to contributing to this subsystem (if different from global contributing guides).
*   **Action 3.2.1.3:** Define a structure for images or other assets used in subsystem documentation, e.g., `C:\EGOS\subsystems\<SUBSYSTEM_NAME>\docs\assets\images\`.
*   **Action 3.2.1.4:** Ensure all subsystem `README.md` files (and other docs) adhere to KOIOS formatting and metadata standards (to be fully defined in Rec. 7.4).
*   **Action 3.2.1.5:** Review existing subsystem documentation (currently mostly `README.md` files in the root of subsystem folders) and plan their migration/restructuring into this new standard `docs/` subdirectory within each subsystem.

#### 3.2.2 Aggregation/Linking Mechanism

*   **Action 3.2.2.1:** In the central `docs_egos/01_subsystems/` directory, create a main `README.md` that serves as an index or portal to all subsystem documentation.
*   **Action 3.2.2.2:** For each subsystem, create a corresponding file or entry in `docs_egos/01_subsystems/` (e.g., `docs_egos/01_subsystems/MYCELIUM.md`) that provides:
    *   A brief, high-level summary of the subsystem (potentially an excerpt from its main `README.md`).
    *   Direct links to the key documents within `C:\EGOS\subsystems\<SUBSYSTEM_NAME>\docs\` (e.g., link to its `README.md`, `API_REFERENCE.md`).
*   **Action 3.2.2.3:** Evaluate tools or scripting solutions (potentially a KOIOS utility) that could automate the generation or updating of these aggregator files in `docs_egos/01_subsystems/` by introspecting the `C:\EGOS\subsystems\` directories. This would ensure the central portal remains synchronized with the subsystem-level documentation.
*   **Action 3.2.2.4:** Ensure clear navigation from the central documentation system to the specific subsystem docs-as-code and vice-versa.

### 3.3 Rec. 7.3: Address Critical Content Gaps

**Priority:** High

**Objective:** To ensure all identified EGOS subsystems have at least foundational documentation and that critical missing KOIOS process documents are recovered or reconstituted.

#### 3.3.1 Plan for Missing Subsystem READMEs (CHRONICLER, KARDIA, ORION, SYNAPSE, ZEPHYR)

*   **Action 3.3.1.1:** For each subsystem (CHRONICLER, KARDIA, ORION, SYNAPSE, ZEPHYR) currently lacking a discoverable `README.md`:
    *   Perform a final, intensive search within the entire `C:\EGOS\` workspace for any orphaned files, notes, or partial drafts related to these subsystems using broad keyword searches (e.g., `grep_search` for subsystem names, related terms from `ARCHITECTURE.MD`). This includes checking `recovery_analysis/` for any previously cataloged but unlinked files.
    *   Consult `ARCHITECTURE.MD` and any related design documents again for descriptions of their intended purpose and functionality.
*   **Action 3.3.1.2:** If no existing materials are found, create a basic stub `README.md` file for each within its respective `C:\EGOS\subsystems\<SUBSYSTEM_NAME>\docs\` directory (following the structure from Action 3.2.1.1).
*   **Action 3.3.1.3:** The stub `README.md` should include:
    *   The subsystem's name and its primary purpose as defined in `ARCHITECTURE.MD`.
    *   A clear statement that this is initial documentation and requires expansion.
    *   Any known relationships or dependencies with other subsystems.
    *   A placeholder for "Key Features" and "Technical Design Notes."
*   **Action 3.3.1.4:** Log these newly created stubs as high-priority items for future content population by relevant subject matter experts or through dedicated research tasks.
*   **Action 3.3.1.5:** Update the central aggregator in `docs_egos/01_subsystems/` to link to these new stub READMEs.

#### 3.3.2 Plan for `KOS_process_index.md`

*   **Action 3.3.2.1:** Conduct a final, exhaustive search for `KOS_process_index.md` across all directories, including backups and archives. Use `find_by_name` with varying patterns.
*   **Action 3.3.2.2:** If the file is definitively lost, initiate a reconstruction effort:
    *   Review existing KOIOS documents (`KOS_standards.md`, `ai_handover_standard.mdc`, `human_ai_collaboration_guidelines.md`, any `README.md` files related to KOIOS) for mentions of specific processes.
    *   Analyze observed operational patterns and best practices that seem to function as implicit KOIOS processes.
    *   Draft a new `KOS_process_index.md` in `docs_egos/02_koios_standards/`.
*   **Action 3.3.2.3:** The new `KOS_process_index.md` should aim to:
    *   List key operational and documentation processes managed or defined by KOIOS.
    *   Provide a brief description for each process.
    *   Link to the detailed document describing each process (if it exists elsewhere, e.g., `ai_handover_standard.mdc`).
    *   Identify any processes that need to be formally documented.
*   **Action 3.3.2.4:** This reconstruction will likely be an iterative task, starting with known processes and expanding as more are identified or formalized.

### 3.4 Rec. 7.4: Develop and Enforce Comprehensive KOIOS Documentation Standards Guide

**Priority:** Medium-High

**Objective:** To create a single, authoritative guide detailing all KOIOS-mandated documentation standards, making them easily accessible and understandable for all contributors (human and AI).

*   **Action 3.4.1:** Designate the SSoT location for this guide. Proposal: `docs_egos/02_koios_standards/KOS_documentation_standards_guide.md`.
*   **Action 3.4.2:** Consolidate all existing explicit and implicit KOIOS standards into this guide. Sources include:
    *   Principles from `MQP.md` (e.g., Conscious Modularity, Systemic Cartography).
    *   Content from `ai_handover_standard.mdc` regarding structure and metadata.
    *   Rules from `human_ai_collaboration_guidelines.md`.
    *   Any style or formatting conventions observed in well-structured existing documents.
    *   User-defined rules (MEMORY[user_global]).
*   **Action 3.4.3:** Define and document standards for the following areas (at a minimum):
    *   **File Naming Conventions:** (e.g., `lowercase-with-hyphens.md`, `SUBSYSTEM_document_type.md`).
    *   **Directory Naming Conventions:** (e.g., `lowercase-with-hyphens`).
    *   **Markdown Frontmatter:** Define a standard schema for metadata (e.g., `title`, `date_created`, `date_modified`, `version`, `authors`, `status`, `tags`, `subsystem_relevance`).
    *   **MDC (Markdown Component) Usage:** Guidelines on when and how to use structured MDC for content elements (if a formal MDC system is to be adopted beyond rule files like `.mdc`).
    *   **Cross-Referencing:** Standard syntax for internal links (relative paths preferred), links to code, links to external resources.
    *   **Diagramming Standards:** Reference <!-- TO_BE_REPLACED --> - preferred tools (Mermaid), types, consistency, and integration into documents.
    *   **Code Block Formatting:** Language specification, syntax highlighting.
    *   **Terminology and Glossary Usage:** Guidelines for using and linking to a central glossary (to be developed).
    *   **Accessibility Considerations:** Basic guidelines for ensuring document accessibility (e.g., alt text for images).
    *   **Review and Update Cadence:** Guidelines for how often documents should be reviewed and updated.
*   **Action 3.4.4:** Include practical examples and templates within the guide to illustrate correct application of the standards.
*   **Action 3.4.5:** Once drafted, this guide should be reviewed and ratified as the official KOIOS standard.
*   **Action 3.4.6:** Plan for the socialization of this guide among all contributors.
*   **Action 3.4.7:** Investigate the feasibility of automated linters or validation scripts (e.g., using `ruff` for Markdown if plugins exist, or custom scripts) to check adherence to these standards, particularly frontmatter and linking.

### 3.5 Rec. 7.5: Implement a Robust Cross-Referencing and Linking Strategy

**Priority:** Medium

**Objective:** To ensure all internal and external links within the documentation are accurate, consistently formatted, and maintainable.

*   **Action 3.5.1:** Once the new SSoT directory structure (Rec. 7.1) is largely in place and key documents have been migrated, conduct a comprehensive audit of all internal Markdown links across the `docs_egos/` structure.
    *   Identify broken links (pointing to non-existent files or anchors).
    *   Identify links that might be valid but use inconsistent formatting (e.g., absolute vs. relative paths unnecessarily).
*   **Action 3.5.2:** Mandate the use of relative paths for all internal links between documents within the `docs_egos/` structure. This enhances portability and reduces breakage if the entire `docs_egos/` root is moved.
*   **Action 3.5.3:** Define a standard for linking to specific sections/headers within documents (e.g., using GitHub-style anchors: `#section-title-lowercase-with-hyphens`). Include this in the `KOS_documentation_standards_guide.md`.
*   **Action 3.5.4:** For links to source code elements (e.g., specific functions or classes in `C:\EGOS\subsystems\`), establish a recommended best practice. This might involve linking to a specific line number on GitHub (if the repository is hosted there) or using a permalink if the hosting service supports it. Consider the volatility of line numbers.
*   **Action 3.5.5:** Systematically correct all identified broken or inconsistently formatted links based on the new SSoT and established standards.
*   **Action 3.5.6:** Investigate and recommend tools for link checking that can be run regularly (e.g., command-line Markdown link checkers, or features within potential static site generator frameworks if one is adopted for documentation presentation).
*   **Action 3.5.7:** Document the linking strategy and recommended tools in the `KOS_documentation_standards_guide.md`.

### 3.6 Rec. 7.6: Clarify and Implement a Documentation Versioning Strategy

**Priority:** Medium

**Objective:** To establish clear guidelines for how documentation artifacts (especially non-code text documents like Markdown files) are versioned within the Git repository, ensuring change history is transparent and manageable.

*   **Action 3.6.1:** Confirm that all consolidated documentation under `docs_egos/` will be version-controlled using Git, similar to source code. This includes committing all changes and not relying on out-of-band backup systems for version history.
*   **Action 3.6.2:** Define commit message conventions specifically for documentation changes. This should align with the overall project's Conventional Commits specification (MEMORY[user_global] - `type(scope): message`) but with specific `type` or `scope` recommendations for docs. Examples:
    *   `docs(koios): update KOS_standards_guide.md with new linking policy`
    *   `fix(docs): correct broken links in MYCELIUM.md aggregator`
    *   `feat(docs): add initial README for CHRONICLER subsystem`
*   **Action 3.6.3:** For significant revisions of major documents (e.g., `ARCHITECTURE.MD`, `MQP.md`, `KOS_documentation_standards_guide.md`), consider a strategy for tagging or versioning these documents more formally within their content (e.g., a `version:` field in the frontmatter) in addition to Git history. This helps readers understand the document's evolution at a glance.
*   **Action 3.6.4:** If the documentation is ever to be published or released in distinct versions (e.g., aligned with software releases), plan how Git tags or branches might be used to capture snapshots of the documentation state at those points.
*   **Action 3.6.5:** Discourage the practice of creating versioned filenames (e.g., `MY_DOCUMENT_v1.md`, `MY_DOCUMENT_v2.md`). Git history is the primary mechanism for accessing previous versions. The `zz_archive/` directory is for long-term archival of *entirely superseded concepts* if deemed necessary, not for iterative versions of active documents.
*   **Action 3.6.6:** Document these versioning conventions in the `KOS_documentation_standards_guide.md`.

### 3.7 Rec. 7.7: Enhance Discoverability (Central Indexing and Search)

**Priority:** Medium

**Objective:** To significantly improve the ease with which users can find relevant documentation through better organization, clear entry points, and effective search capabilities.

*   **Action 3.7.1:** Ensure the root `README.md` of the new `docs_egos/` directory serves as a primary, well-structured entry point to the entire documentation system. This `README.md` should clearly explain the top-level categories and link to their respective index pages (e.g., `docs_egos/01_subsystems/README.md`, `docs_egos/02_koios_standards/README.md`).
*   **Action 3.7.2:** Create or refine `README.md` files within each major subdirectory of `docs_egos/` to act as local indexes or tables of contents for that section.
*   **Action 3.7.3:** Consider creating a dedicated, top-level `docs_egos/DOCUMENTATION_INDEX.md` or `docs_egos/SEARCH_PORTAL.md` that offers:
    *   A brief guide on how the documentation is structured.
    *   Links to key overarching documents (`MQP.md`, `ARCHITECTURE.MD`, `ROADMAP.md`, `KOS_documentation_standards_guide.md`).
    *   Links to each major section's index.
    *   Potentially, a manually curated list of common search terms or FAQs with links to relevant documents.
*   **Action 3.7.4:** Evaluate options for implementing a full-text search capability across the `docs_egos/` structure:
    *   **Option A (Basic):** Rely on IDE/editor search tools (e.g., VS Code's search) and Git repository search (e.g., GitHub's search if hosted there). Document best practices for using these tools effectively.
    *   **Option B (Enhanced):** Investigate deploying a lightweight static site generator (e.g., MkDocs, Jekyll, Hugo, Docusaurus) for the `docs_egos/` content. Many of these come with built-in search functionality (often client-side search like Lunr.js). This would also improve readability and navigation.
        *   If pursuing this, sub-actions would include selecting a tool, configuring it, defining a theme, and setting up a build/deployment process (even if just for local viewing initially).
    *   **Option C (Advanced):** Explore dedicated search engine solutions if the documentation grows extremely large, though this is likely overkill for the current scale.
*   **Action 3.7.5:** If a static site generator (Option B) is chosen, ensure generated HTML documentation is also discoverable by search engines if deployed publicly.
*   **Action 3.7.6:** Promote the use of consistent tagging (`tags:` field in frontmatter) across documents to aid in faceted search or filtering, especially if a more advanced search solution is adopted.

### 3.8 Rec. 7.8: Integrate Working Docs into Permanent Knowledge Base / Maintainability

**Priority:** Medium-Low (Adjusted from original diagnostic; core structural changes take precedence)

**Objective:** To establish clear processes for managing temporary or evolving working documents and ensuring the long-term maintainability of the entire documentation system.

*   **Action 3.8.1:** Define a clear policy for "working documents" (like the `Work_*.md` files we are currently using, or analysis files in `C:\EGOS\recovery_analysis\`).
    *   These should have a clear lifecycle: creation, active use, and then either archival (if purely for historical record of a process) or integration/distillation into the permanent `docs_egos/` structure.
    *   Example: `Work_2025-05-20_Documentation_Diagnosis.md` might be moved to `docs_egos/zz_archive/planning_records/` after this Phase 2 is complete, or key sections might be summarized into a lessons-learned document within `docs_egos/02_koios_standards/`.
*   **Action 3.8.2:** Establish a dedicated location for transient, non-critical notes or drafts that are not yet ready for formal documentation. This could be a user-specific `scratch/` directory (outside of `docs_egos/`) or a clearly marked section within `docs_egos/` if strictly managed (e.g., `docs_egos/00_project_overview/working_drafts/` with clear naming conventions and review cadences).
*   **Action 3.8.3:** Implement a regular review cycle for the documentation system's health:
    *   **Link Checking:** (See Action 3.5.6) Run automated link checks periodically.
    *   **Stale Content Review:** Identify documents not updated for an extended period (e.g., >1 year) and assess their continued relevance or need for updates. This could be facilitated by `date_modified` in frontmatter.
    *   **Gap Analysis:** Periodically review against the `ARCHITECTURE.MD` and `ROADMAP.md` to identify new components or features that require documentation.
*   **Action 3.8.4:** Promote a culture of documentation ownership. Where possible, subsystem documentation should be maintained by those actively working on or most familiar with the subsystem.
*   **Action 3.8.5:** Include "Documentation Update" as a standard part of the definition-of-done for any new feature development or significant system change.
*   **Action 3.8.6:** Document these maintainability processes and policies within the `KOS_documentation_standards_guide.md`.

## 4. Timeline and Milestones

**Objective:** To provide a high-level overview of the expected sequencing and duration for the execution of this plan. Detailed timelines will be developed iteratively.

*   **Phase 2.A: Foundational Restructuring (Estimated: [e.g., 2-4 weeks])**
    *   **Milestone 2.A.1:** New `docs_egos/` SSoT directory structure established (Actions 3.1.1.1 - 3.1.1.4).
    *   **Milestone 2.A.2:** Initial mapping of all documents to SSoT locations (`documentation_migration_map.csv`) completed (Action 3.1.2.1 - 3.1.2.3).
    *   **Milestone 2.A.3:** Core project documents (`MQP.md`, `ARCHITECTURE.MD`, `ROADMAP.md`, `STRATEGY.MD`) migrated and de-duplicated to `docs_egos/00_project_overview/` (Part of Action 3.1.3).
    *   **Milestone 2.A.4:** Standard subsystem `docs/` structure defined and initial `README.md` stubs created for all known subsystems (Actions 3.2.1.1 - 3.2.1.5, 3.3.1.1 - 3.3.1.5).
    *   **Milestone 2.A.5:** `KOS_process_index.md` reconstituted or recovered (Action 3.3.2).

*   **Phase 2.B: Standards Implementation & Content Migration (Estimated: [e.g., 4-8 weeks])**
    *   **Milestone 2.B.1:** `KOS_documentation_standards_guide.md` drafted and ratified (Actions 3.4.1 - 3.4.5).
    *   **Milestone 2.B.2:** Full migration of prioritized existing documentation to `docs_egos/` according to the migration map and new standards (Action 3.1.3.2, ongoing application of Rec. 7.4).
    *   **Milestone 2.B.3:** Linking strategy implemented; initial link audit and correction pass completed (Actions 3.5.1 - 3.5.7).
    *   **Milestone 2.B.4:** Versioning strategy documented and applied to new commits (Actions 3.6.1 - 3.6.6).

*   **Phase 2.C: Enhancement and Sustainability (Estimated: [e.g., Ongoing, initial focus 2-3 weeks])**
    *   **Milestone 2.C.1:** Discoverability mechanisms (central indexes, READMEs) implemented (Actions 3.7.1 - 3.7.3).
    *   **Milestone 2.C.2:** Initial decision and potential PoC for search solution (Action 3.7.4).
    *   **Milestone 2.C.3:** Policies for working documents and maintainability processes documented and communicated (Actions 3.8.1 - 3.8.6).

*(Note: Timelines are indicative and subject to available resources and emerging priorities.)*

## 5. Resource Allocation

*(Content to be detailed. This section will outline the human and tool resources required for successful execution. E.g., Lead technical writer/coordinator, subsystem expert contributions, AI assistant time, specific software tools if any.)*

## 6. Risks and Mitigation

*(Content to be detailed. This section will identify potential risks to the plan's success and propose mitigation strategies. E.g., Risk: Competing priorities delaying contributions. Mitigation: Secure dedicated time from key personnel.)*

## 7. Next Steps & Review

*(Content to be detailed. This section will outline immediate next steps after this plan's approval and how progress will be tracked and reviewed.)*
