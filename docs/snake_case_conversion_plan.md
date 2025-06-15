@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/snake_case_conversion_plan.md

# EGOS Project: snake_case Conversion Plan

**Document Version:** 2.0
**Date:** 2025-05-26
**Author:** Cascade (AI Assistant)
**Status:** Implementation in Progress

## 1. Objective

To define the requirements, scope, and phased approach for developing a Python script that audits the `C:\EGOS` workspace for files and directories not adhering to the `snake_case` naming convention. This plan supports the eventual goal of standardizing all project artifact names.

## 2. Background

*   **EGOS Standard:** `RULE-FS-SNAKE-CASE-01` (defined in global and workspace `.windsurfrules`) mandates the use of `snake_case` for all files and directories within the EGOS project.
*   **ADRS Log Entry:** An item in `ADRS_Log.md` (Timestamp: `2025-05-26T19:15:00Z`, Artifact: `C:\EGOS\ (Project-wide)`) tracks this inconsistency.
*   **MQP Alignment:** This initiative directly supports `EGOS_PRINCIPLE:Systemic_Organization` by ensuring a consistent and predictable naming scheme, and `EGOS_PRINCIPLE:Progressive_Standardization` by systematically addressing a known deviation.

## 3. Audit Script Requirements

The Python script (`audit_snake_case.py` or similar) should:

*   **Traversal:** Recursively traverse all directories starting from `C:\EGOS\`.
*   **Identification:** Identify any file or directory name that:
    *   Contains uppercase letters.
    *   Contains spaces.
    *   Uses hyphens (`-`) instead of underscores (`_`) for separation (unless part of an explicitly allowed pattern, TBD).
    *   Does not follow the general `snake_case` pattern (e.g., `camelCase`, `PascalCase`).
*   **Exclusions:** Allow configuration of exclusion rules for specific directories, files, or patterns.
*   **Reporting:**
    *   Output a list of all non-compliant file and directory paths.
    *   Provide a summary count of non-compliant items.
    *   Optionally, generate a report file (e.g., Markdown or CSV) detailing the findings.
*   **Configuration:** Exclusion rules and other parameters should be configurable, potentially via a simple configuration file or command-line arguments.
*   **Platform Agnostic:** While developed on Windows, the script logic should be as platform-agnostic as possible for future flexibility.

## 4. Scope

*   **In-Scope:** The entire `C:\EGOS\` workspace.
*   **Initial Exclusions (to be configurable):**
    *   `.git/`
    *   `venv/` (and similar virtual environment directories like `.venv/`, `env/`)
    *   `node_modules/`
    *   `__pycache__/`
    *   `.vscode/`
    *   `.idea/`
    *   Specific files known to require a different case (e.g., `README.md`, `LICENSE`, `Makefile` - though `makefile` is also common). This needs careful consideration.
    *   Files with extensions that are typically uppercase (e.g., `.SQL` if that's a project convention, though `.sql` is more common).

## 5. Desired Output

*   **Console Output:** Clear list of non-compliant paths.
*   **Report File (Optional, Markdown):**
    ```markdown
    # snake_case Compliance Audit Report
    **Date:** YYYY-MM-DD HH:MM:SS
    **Total Items Scanned:** X
    **Non-Compliant Items Found:** Y

    ## Non-Compliant Directories:
    - path/to/DirectoryA
    - path/to/Another_Bad-Dir

    ## Non-Compliant Files:
    - path/to/someFile.py
    - path/to/Other-File.txt
    ```

## 6. Potential Risks

*   **Misidentification:** The script might incorrectly flag items if the `snake_case` detection logic is not robust.
*   **Performance:** Traversing a very large number of files could be slow if not optimized.
*   **Scope Creep (for Audit Script):** The audit script should *not* perform any renaming actions in its initial versions. Renaming is a separate, more complex phase.

## 7. Phased Approach and Current Status

1.  **Phase 1: Audit Script Development (COMPLETED)**
    * ✅ Developed `C:\EGOS\scripts\utils\audit_snake_case.py` to perform read-only auditing.
    * ✅ Implemented configuration loading from `C:\EGOS\config\snake_case_audit_config.json`.
    * ✅ Added robust exclusion handling for directories, files, and patterns.
    * ✅ Created reporting functionality with summary statistics.

2.  **Phase 2: Workspace Audit & Analysis (COMPLETED)**
    * ✅ Ran the audit script on the entire `C:\EGOS` workspace.
    * ✅ Generated comprehensive report at `C:\EGOS\reports\snake_case_audit_report.md`.
    * ✅ Identified 3,081 non-compliant items out of 13,797 total items scanned.
    * ✅ Analyzed patterns of non-compliance (PascalCase directories, mixed casing in filenames).
    * ✅ Updated `ADRS_Log.md` to reflect the completion of the initial audit.
    * ✅ Developed prioritization strategy for conversion:
        * Tier 1: Core Scripts & Configuration
        * Tier 2: Core EGOS Framework & Key Documentation
        * Tier 3: Ancillary Components & High-Volume Areas
        * Tier 4: Archived/Less Critical Areas

3.  **Phase 3: Interactive Conversion Tool (IN PROGRESS)**
    * ✅ Developed `C:\EGOS\scripts\utils\convert_to_snake_case.py` with the following features:
        * Robust string conversion logic for various naming conventions
        * Configuration loading from JSON
        * Directory traversal with proper ordering (children before parents)
        * Interactive prompting (confirm, skip, custom name, auto-confirm)
        * Dry-run mode to simulate changes
        * Comprehensive exclusion mechanisms
        * Logging and reporting
    * ✅ Created test environment at `C:\EGOS\test_conversion_area` with various naming patterns.
    * ✅ Created test configuration at `C:\EGOS\config\snake_case_convert_test_config.json`.
    * ✅ Created production configuration at `C:\EGOS\config\snake_case_convert_config.json`.
    * ✅ Documented the `snake_case` naming convention standard at `C:\EGOS\docs\core_materials\standards\snake_case_naming_convention.md`.
    * 🔄 Testing in progress with the test environment.

4.  **Phase 4: Execution of Conversion (PLANNED)**
    * 📅 Execute conversion following the prioritization strategy:
        1. Tier 1: Core Scripts & Configuration
        2. Tier 2: Core EGOS Framework & Key Documentation
        3. Tier 3: Ancillary Components & High-Volume Areas
        4. Tier 4: Archived/Less Critical Areas
    * 📅 For each tier:
        * Run dry-run first to validate changes
        * Execute actual conversion with appropriate safeguards
        * Verify functionality after conversion
    * 📅 Update cross-references as needed

5.  **Phase 5: Post-Conversion Verification (PLANNED)**
    * 📅 Run the audit script again to verify reduction in non-compliant items
    * 📅 Check for broken references or functionality issues
    * 📅 Update the `ADRS_Log.md` with conversion results
    * 📅 Document any remaining non-compliant items and reasons for exceptions

## 8. Next Steps

1. Complete testing of the conversion script using the test environment.
2. Begin execution of the conversion plan, starting with Tier 1 (Core Scripts & Configuration):
   ```powershell
   # First, always do a dry run
   python C:\EGOS\scripts\utils\convert_to_snake_case.py C:\EGOS\scripts --config-file C:\EGOS\config\snake_case_convert_config.json --dry-run
   python C:\EGOS\scripts\utils\convert_to_snake_case.py C:\EGOS\config --config-file C:\EGOS\config\snake_case_convert_config.json --dry-run
   
   # Then, if results look good, proceed with actual conversion
   python C:\EGOS\scripts\utils\convert_to_snake_case.py C:\EGOS\scripts --config-file C:\EGOS\config\snake_case_convert_config.json
   python C:\EGOS\scripts\utils\convert_to_snake_case.py C:\EGOS\config --config-file C:\EGOS\config\snake_case_convert_config.json
   ```
3. Monitor and address any issues that arise during the conversion process.
4. Proceed with subsequent tiers after successful completion of each tier.

## 9. Risk Mitigation

* **Backup:** Create backups of directories before conversion.
* **Incremental Approach:** Convert one tier at a time, verifying functionality between tiers.
* **Cross-Reference Updates:** Update any cross-references that might be affected by renamed files.
* **Documentation:** Keep detailed logs of all conversions for potential rollback if needed.