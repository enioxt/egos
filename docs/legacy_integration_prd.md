@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/legacy_integration_prd.md

# Product Requirements Document: EGOS Legacy Integration & Project Evolution

**Version:** 1.0
**Date:** 2025-04-18
**Author:** Cascade (AI) & [USER NAME] (Please update with your name)
**Status:** Draft

## 1. Introduction

This document outlines the requirements for the **EGOS Legacy Integration & Project Evolution** initiative. The primary goal is to systematically identify, process, standardize, integrate, and document historical artifacts ("legacy") generated throughout the EGOS project's lifecycle. This includes code, documentation, design notes, conversation logs, and strategic plans that currently exist outside the main, standardized project structure. This initiative aims to preserve valuable historical context, make past knowledge accessible, and create a traceable narrative of the project's evolution, reinforcing core EGOS principles.

## 2. Goals

*   **Preserve Historical Context:** Ensure valuable knowledge, decisions, and rationale from the project's past are not lost.
*   **Improve Discoverability:** Make legacy information accessible and searchable within the current EGOS framework.
*   **Enhance Onboarding:** Provide future contributors (human and AI) with a richer understanding of the project's history and evolution.
*   **Standardize Artifacts:** Apply KOIOS standards (formatting, metadata, language) to legacy materials for consistency.
*   **Document Evolution:** Create a clear narrative tracing the project's development phases and key architectural/philosophical shifts.
*   **Reinforce EGOS Principles:** Directly implement and showcase **CRONOS (Evolutionary Preservation)** and **KOIOS (Standardization, Documentation)**.

## 3. Scope

**In Scope:**

*   Identification of legacy artifacts (code, docs, .txt notes, chat logs, etc.) within defined locations (e.g., `c:\EGOS`, potentially specified archives).
*   Creation of an inventory document for tracked legacy artifacts.
*   Development of scripts for batch processing (renaming, metadata injection, language detection, basic formatting).
*   Definition and application of standardization patterns for legacy files (target format: Markdown, metadata headers).
*   Process for translating non-English artifacts (prioritizing key documents).
*   Strategy for integrating processed artifacts into the live EGOS structure (e.g., `/docs/legacy`).
*   Creation of a central document detailing the project's evolution narrative and the legacy integration strategy.

**Out of Scope:**

*   Deep refactoring of legacy *code* to meet current functional requirements (focus is on preservation and standardization, not modernization of function unless trivial).
*   Migration of large binary assets (unless specifically prioritized).
*   Real-time, continuous capture of *new* conversations (this is handled by existing logging/interaction mechanisms).
*   Building a dedicated search engine for legacy content (discoverability will rely on structure and existing search tools initially).

## 4. Target Audience

*   **Current & Future Developers:** To understand project history, past decisions, and find relevant prior art/context.
*   **AI Assistants (like Cascade):** To have access to a richer, structured dataset for providing more informed assistance.
*   **Project Maintainers:** To ensure long-term knowledge preservation and consistency.
*   **External Contributors (Future):** To understand the project's journey and design philosophy.

## 5. Guiding Principles

*   **CRONOS (Evolutionary Preservation):** The core driver – ensuring the past informs the present and future.
*   **KOIOS (Standardization & Documentation):** Applying structure, metadata, and clear documentation to the process and the artifacts.
*   **HARMONY (Compatibility):** Ensuring scripts and processes work within the Windows environment.
*   **Universal Accessibility:** Making the integrated information accessible and understandable.
*   **Conscious Modularity:** Breaking down the complex task into manageable phases and scripts.

## 6. Functional Requirements (Features / Process Steps)

*   **FR1: Legacy Artifact Identification:** The system/process must allow for identifying potential legacy artifacts based on location, file type, and potentially keywords.
*   **FR2: Legacy Inventory Management:** A central inventory (`docs/legacy/legacy_inventory.md`) must be created and maintained, tracking artifact path, type, estimated date, language, status (raw, processed, translated, integrated), priority, and relevant tags.
*   **FR3: Standardization Scripting:** Reusable scripts must be developed to:
    *   FR3.1: Rename files to target format (e.g., .txt -> .md).
    *   FR3.2: Inject a standard metadata header (YAML frontmatter).
    *   FR3.3: Perform automated language detection (e.g., 'en', 'pt', 'mixed').
    *   FR3.4: Apply basic Markdown formatting where feasible (e.g., identify potential headers, code blocks).
    *   FR3.5: Log processing actions and errors.
*   **FR4: Translation Workflow:** A process must be defined for translating high-priority non-English artifacts, including:
    *   FR4.1: Identification of files needing translation based on inventory metadata.
    *   FR4.2: (Optional) Integration with AI translation tools.
    *   FR4.3: A mandatory human review step for accuracy and context.
    *   FR4.4: Storing translated versions alongside originals.
*   **FR5: Artifact Integration:** A strategy and process must exist for placing processed artifacts into the live EGOS structure (e.g., `/docs/legacy/`, `/docs/archive/`, potentially linked from relevant current docs). Integration must consider discoverability.
*   **FR6: Evolution Narrative:** A dedicated document (`docs/process/legacy_integration_strategy.md` or similar) must be created summarizing the project's history, the legacy integration process itself, and linking to key findings or integrated artifacts.
*   **FR7: Issue Flagging:** The process (human or assisted) should flag potentially valuable but underdeveloped ideas found in legacy artifacts (e.g., ETHIK CHAIN details, RPG concepts) for review.

## 7. Non-Functional Requirements

*   **NFR1: Usability (Scripts):** Scripts should be easy to run, configurable, and provide clear output/logging.
*   **NFR2: Maintainability (Scripts):** Script code should be clean, well-commented, and follow EGOS coding standards.
*   **NFR3: Performance (Scripts):** Scripts should handle a reasonable volume of files efficiently, although batch processing is acceptable.
*   **NFR4: Discoverability (Artifacts):** Integrated legacy artifacts should be reasonably findable through directory structure and potentially linked from relevant areas.
*   **NFR5: Idempotency (Scripts):** Where possible, scripts should be safe to re-run on already processed files without causing unintended changes.

## 8. Success Metrics

*   Percentage of identified potential legacy locations scanned.
*   Completeness of the `legacy_inventory.md` (covering prioritized artifacts).
*   Successful execution of standardization scripts on >95% of targeted files.
*   Translation and review completed for defined high-priority non-English documents.
*   Creation and approval of the `legacy_integration_strategy.md` / Project Evolution document.
*   Subjective assessment by the team that historical context is more accessible.

## 9. Release Criteria / Phasing

This initiative will be executed in phases, aligned with the Roadmap tasks:

*   **Phase 1 (Scan & Script Foundation):** Complete `LEGACY-SCAN-01` (Inventory) and `LEGACY-SCRIPT-01` (Initial Standardization Scripts). *Pause/Review Point.*
*   **Phase 2 (Processing & Translation):** Run scripts on batches of artifacts. Begin `LEGACY-TRANSLATE-01` workflow for priority items. *Pause/Review Point.*
*   **Phase 3 (Integration & Narrative):** Begin `LEGACY-INTEGRATE-01` based on strategy. Draft and complete `LEGACY-NARRATIVE-01`. *Ongoing Review.*
*   **Phase 4 (Refinement & Maintenance):** Refine scripts, process remaining artifacts, update inventory and narrative as needed.

## 10. Detailed Task Breakdown (Roadmap Alignment)

*(This section references the detailed task breakdown added to the EGOS Roadmap under the 'Legacy Integration & Project Evolution' section. Each task (LEGACY-SCAN-01, LEGACY-SCRIPT-01, LEGACY-TRANSLATE-01, LEGACY-INTEGRATE-01, LEGACY-NARRATIVE-01) includes Objectives, Inputs, Outputs, Sub-tasks, ETA, Effort Estimates, Resources, and Pause/Correction Points.)*

*Refer to ROADMAP.md for the full breakdown.* 

*(Example Summary for LEGACY-SCAN-01)*
*   **Task ID: LEGACY-SCAN-01: Define Scope & Inventory Legacy Artifacts**
    *   **Objective:** Create a comprehensive, prioritized inventory; define legacy scope.
    *   **ETA:** 1-2 Weeks
    *   **Effort:** Human: 5-10 hrs, AI: 2-4 hrs
    *   **Key Output:** `docs/legacy/legacy_inventory.md`
    *   **Pause Point:** Review scope/inventory before scripting.

*(Similar summaries can be added here for other tasks if desired, or rely solely on the Roadmap)*

## 11. Open Issues / Future Considerations

*   Final decision on specific AI translation service/API key management (if used).
*   Strategy for handling very large legacy files or binary assets.
*   Need for more sophisticated parsing/formatting within scripts (beyond basic Markdown).
*   Potential integration with a dedicated knowledge base or search tool later.
*   Process for periodically re-scanning for new "legacy" material.