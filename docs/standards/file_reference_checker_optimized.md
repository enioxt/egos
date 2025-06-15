@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/standards/file_reference_checker_optimized.md

# File Reference Checker (Optimized) - `file_reference_checker_optimized.py`

**Version:** 1.1.0
**Author:** EGOS Development Team (with Cascade AI)
**Date:** 2025-05-19

**Cross-References:**
-   **Configuration:** `scripts/cross_reference/config.yaml`
-   **Script Location:** `scripts/cross_reference/file_reference_checker_optimized.py`
-   **System Context:** `../EGOS_SYSTEM_STRUCTURE.md`
-   **Example Reports:** Generated in `scripts/cross_reference/` (e.g., `file_reference_report_YYYYMMDD_HHMMSS.md`)

---

## 1. Overview

The Optimized File Reference Checker is a Python script designed to enhance development workflows by automatically identifying recently modified files within a project and verifying if they are appropriately referenced across the codebase and documentation. This helps ensure that all new or updated components are integrated and documented, preventing orphaned files and improving maintainability.

The script scans configured directories for files whose last modification timestamp (as per the file system) falls within a specified time window. For each such "target file," it then searches for mentions (references) in other configured parts of the project. The findings are compiled into timestamped Markdown and JSON reports. Additionally, the script manages its own report archive by automatically deleting older reports based on a configurable retention policy.

## 2. Key Features

-   **Recent File Detection:** Scans for files modified within a user-defined time window (e.g., last 48 hours).
-   **Configurable Reference Searching:** Allows detailed configuration of:
    -   Target directories/files for reference searching.
    -   File extensions to be scanned for references.
    -   Custom text patterns (with placeholders like `{filename}`, `{filepath}`, `{module_name}`) for identifying references in code, comments, or text.
    -   Automatic resolution of Python module names for targeted searching.
-   **Comprehensive Reporting:** Generates detailed reports in both Markdown and JSON formats. Reports list:
    -   Recently modified files.
    -   Specific locations (file, line number, content snippet) where each modified file is referenced.
    -   A prominent **warning** (highlighting project guidelines such as MEMORY[3bae44d3-4f57-48b4-acd0-c2eedf79171c] regarding unreferenced files) if a modified file has no detected references. This is crucial for maintaining system integrity.
-   **Timestamped Archival:** Saves reports with timestamps in their filenames (e.g., `file_reference_report_YYYYMMDD_HHMMSS.ext`) to prevent overwriting and maintain a history.
-   **Automated Report Retention:** Implements a policy to automatically delete old reports after a configured number of days, helping manage storage space.
-   **High Configurability:** All operational aspects are controlled via an external `config.yaml` file.
-   **Logging:** Provides informative console output and detailed debug logging to `checker_debug_output.log`.

## 3. Prerequisites

-   **Python:** Version 3.7+
-   **Libraries:**
    -   `PyYAML`: For parsing the `config.yaml` file. Install via `pip install PyYAML`.
-   **Optional:**
    -   `ripgrep`: If using the `"ripgrep"` search method for potentially faster searches on large codebases. Ensure `rg` is in your system's PATH.

## 4. Configuration (`config.yaml`)

The script's behavior is entirely controlled by `config.yaml`, located in the same directory as the script (`scripts/cross_reference/`).

| Setting                     | Type          | Description                                                                                                                                                              | Example                                              |
| --------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| `project_base_path`         | String        | Absolute path to the root of the project to be scanned.                                                                                                                  | `"c:\\EGOS"` or `"/mnt/c/EGOS"`                      |
| `scan_directories`          | List          | List of directories (relative to `project_base_path`) to scan for recently modified files. Use `"."` for the entire project base.                                         | `[".", "src/core"]`                                  |
| `target_file_extensions`    | List          | File extensions that identify a file as a "target file" if recently modified.                                                                                            | `[".py", ".md", ".yaml"]`                            |
| `reference_search_directories` | List          | List of directories or specific files (relative to `project_base_path`) to search within for references to target files.                                                 | `["docs/", "scripts/", "README.md"]`                  |
| `reference_file_extensions` | List          | File extensions to consider when searching for references within `reference_search_directories`.                                                                           | `[".py", ".md", ".txt"]`                             |
| `excluded_directories`      | List          | Directories (relative to `project_base_path`) to exclude from both scanning for modified files and searching for references. Supports glob patterns for filenames.          | `[".git", "venv", "__pycache__", "*.log"]`           |
| `time_window_hours`         | Integer       | Defines "recent." Files modified within this many hours from the current time are considered.                                                                            | `48` (for 2 days)                                    |
| `output_formats`            | List          | Desired output report formats. Options: `"markdown"`, `"json"`.                                                                                                          | `["markdown", "json"]`                               |
| `output_filename`           | String        | Base name for the output report files. Timestamps and extensions will be appended.                                                                                         | `"file_reference_report"`                            |
| `report_retention_days`     | Integer       | Number of days to retain generated reports. Reports older than this are deleted. Set to `0` or negative to disable.                                                      | `30`                                                 |
| `search_method`             | String        | Method for searching references. Options: `"in_memory"` (loads files, good for smaller projects), `"ripgrep"` (uses `rg` command, faster for large projects).             | `"in_memory"`                                        |
| `parallel_processes`        | String/Int    | Number of parallel processes for searching. `0` or `1` for no parallelism. `"cpu_count"` uses available cores.                                                           | `"cpu_count"` or `4`                                 |
| `log_level`                 | String        | Logging verbosity. Options: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`.                                                                                    | `"INFO"`                                             |
| `reference_patterns`        | List          | Patterns to identify as references. `{filename}` and `{filepath}` are placeholders for the target file's name and relative path. `{module_name}` for Python files. These patterns are treated as plain text and searched for literally (after placeholder replacement) within the content of reference files. This means matches can occur in code, comments, or plain text.      | `["{filename}", "import {module_name}"]`            |
| `resolve_python_modules`    | Boolean       | If `true`, for Python files (e.g., `utils/helpers.py`), also searches for its module form (e.g., `utils.helpers`) using the `{module_name}` pattern.                       | `true`                                               |

## 5. Usage

To run the script, navigate to its directory and execute it with Python:

```bash
cd path/to/EGOS/scripts/cross_reference
python file_reference_checker_optimized.py
```

Ensure `config.yaml` is present in the same directory and properly configured.

The script can also be run with an optional `--config` argument to specify a different configuration file path:
```bash
python file_reference_checker_optimized.py --config /path/to/alternative_config.yaml
```

## 6. Output

The script generates reports in the formats specified in `config.yaml` (Markdown and/or JSON). These files are saved in the script's directory.

-   **Markdown Report (`<output_filename>_YYYYMMDD_HHMMSS.md`):**
    -   Human-readable summary.
    -   Lists each recently modified file.
    -   Under each file, lists all found references, including the referencing file, line number, and a snippet of the line content.
    -   Displays a prominent warning (potentially citing project guidelines like MEMORY[3bae44d3...]) if no references are found for a modified file.
    -   Includes metadata about the run (timestamp, configuration highlights).

-   **JSON Report (`<output_filename>_YYYYMMDD_HHMMSS.json`):**
    -   Machine-readable format.
    -   Contains structured data including:
        -   Run metadata (timestamp, configuration used).
        -   A list of processed files, each with:
            -   Its path.
            -   A list of found references (each with `referencing_file`, `line_number`, `line_content`).
            -   A flag indicating if it's unreferenced.

## 7. Troubleshooting and Logging

-   **Console Output:** Provides real-time status updates based on the `log_level` in `config.yaml`.
-   **Log File (`checker_debug_output.log`):** A detailed log file is created in the script's directory. For `DEBUG` level, this includes all configuration details, files scanned, references checked, and errors encountered. This is the primary resource for troubleshooting.

## 8. Version History

-   **1.1.0 (2025-05-19):**
    -   Implemented reference searching for modified files.
    -   Added detailed Markdown and JSON reporting with reference locations.
    -   Implemented report archival with timestamps.
    -   Added automatic report retention policy.
    -   Enhanced configurability and logging.
-   **1.0.0 (2025-05-18):**
    -   Initial optimized version focusing on finding recently modified files.

---
*This document is maintained under KOIOS documentation standards.*