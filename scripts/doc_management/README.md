@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - scripts/cross_reference/script_template_generator.py





  - scripts/doc_management/README.md

# Document Organizer (`doc_organizer.py`)

**Version:** 0.2.0 (Enhanced Error Handling & Consolidation Planning)  
**Author:** EGOS System (Maintained by Cascade AI)  
**Date:** 2025-05-24  
**Status:** In Development

## 1. Overview

`doc_organizer.py` is a Python utility script designed to help manage and organize document directories within the EGOS project. Its primary functions include identifying and removing empty directories, and it is being enhanced to support advanced features like duplicate folder detection, intelligent file consolidation, and contextual analysis for archival or unification suggestions.

This script adheres to EGOS project standards, including robust error handling, configurable logging, and operational modes (dry-run vs. actual execution).

## 2. Features

### 2.1 Current Features (as of v0.2.0)

*   **Empty Directory Removal:** Scans a specified base path for empty directories and removes them.
    *   Supports dry-run mode to preview actions.
    *   Logs all actions and errors.
*   **Enhanced Error Handling:**
    *   Gracefully handles common filesystem errors (e.g., `PermissionError`, `FileNotFoundError`, `OSError`).
    *   Provides detailed error messages and context.
    *   Includes a retry mechanism for transient errors during directory deletion.
*   **Basic File Consolidation Logic (Foundation):**
    *   Initial framework for moving files based on criteria (to be fully developed).
*   **Configurable Logging:** Adjustable log levels via command-line arguments.
*   **Progress Tracking:** Uses `tqdm` for visual progress bars during lengthy operations.

### 2.2 Planned Features (See [Project Roadmap](../../../ROADMAP.md#document-organization-and-cleanup-doc_organizerpy))

*   **DOC-ORG-01: Duplicate Folder Detection:**
    *   Identify folders with similar or identical content.
    *   Use criteria like importance, creation date, and file count for assessment.
*   **DOC-ORG-02: File Consolidation from Duplicates:**
    *   Move files from less important/older duplicate folders to a primary folder.
    *   Implement robust filename conflict resolution.
    *   Clean up source folders after successful consolidation.
*   **DOC-ORG-03: Contextual File Analysis:**
    *   Analyze files post-consolidation to determine development stage/version.
    *   Use heuristics based on content summaries, metadata, and origin.
*   **DOC-ORG-04: Actionable Suggestions:**
    *   Suggest file unification/merging for similar content.
    *   Suggest archival of older/redundant versions.
    *   Suggest deletion of obsolete files.
*   **DOC-ORG-00 Enhancements:**
    *   Comprehensive error scenario testing.
    *   Performance improvements based on standards scan.
    *   Configurable ignore patterns for scanning.
    *   Age-based deletion criteria for empty directories.

## 3. Usage

```bash
python doc_organizer.py <path_to_scan> [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--dry-run] [--consolidate] [--target-dir <target_consolidation_directory>]
```

**Arguments:**

*   `path_to_scan`: (Required) The base directory to scan for organization.
*   `--log-level`: (Optional) Set the logging level. Default: `INFO`.
*   `--dry-run`: (Optional) Simulate actions without making changes.
*   `--consolidate`: (Optional) Enable file consolidation mode (under development).
*   `--target-dir`: (Optional) Specify the target directory for consolidated files. Required if `--consolidate` is used.

**Examples:**

*   Scan `C:\EGOS\docs` and remove empty directories (actual run):
    ```bash
    python doc_organizer.py C:\EGOS\docs
    ```
*   Dry-run scan of `C:\EGOS\sandbox` with debug logging:
    ```bash
    python doc_organizer.py C:\EGOS\sandbox --dry-run --log-level DEBUG
    ```

## 4. Dependencies

*   Python 3.8+
*   `tqdm` (for progress bars)

Install dependencies using:
```bash
pip install -r requirements.txt 
```
*(Note: A `requirements.txt` specific to this script or its parent module should be created if not already present.)*

## 5. Script Standards & Compliance

This script aims to comply with EGOS project scripting standards.
*   **Standard Script Template:** Applied.
*   **Logging:** Implemented.
*   **Error Handling:** Significantly improved.
*   **Cross-Reference Integration:** To be reviewed and ensured for file modification actions.
*   **MQP Principles:** Considered in design (e.g., Conscious Modularity, Integrated Ethics for file handling).

Refer to `script_standards_scanner.py` output for detailed compliance status.

## 6. Contribution & Development

Further development will focus on implementing the planned features outlined above. Contributions should adhere to EGOS coding standards and MQP principles.

## 7. References

*   [Project Roadmap (`ROADMAP.md`)](../../../ROADMAP.md)
*   [Work Log (`WORK_2025-05-24_DocOrganizerEnhancements.md`)](../../../WORK_2025-05-24_DocOrganizerEnhancements.md)
*   [MQP Document (`MQP.md`)](../../../MQP.md)
*   [Script Template Generator (`script_template_generator.py`)](../cross_reference/script_template_generator.py)

✧༺❀༻∞ EGOS ∞༺❀༻✧