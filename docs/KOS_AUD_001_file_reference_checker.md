---
title: "File Reference Checker Plan (KOS-AUD-001)"
version: 0.1.0
status: Planned
date_created: 2025-05-19
date_modified: 2025-05-19
authors: [EGOS Team]
description: "Specification and plan for the KOS-AUD-001 File Reference Checker tool, designed to identify undocumented files and verify cross-references within the EGOS project."
file_type: specification
scope: project-wide
primary_entity_type: tool_specification
primary_entity_name: KOS-AUD-001
tags: [audits, koios, file-references, undocumented-files, tool-specification, KOS-AUD-001, SACA]
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/index.md






  - "[Audits Dashboard](./index.md)"
  - "[KOIOS Subsystem](../../subsystems/KOIOS/README.md)"
---
  - docs/KOS_AUD_001_file_reference_checker.md
# File Reference Checker (KOS-AUD-001)

**Status:** Planned

## 1. Objective

Build a File Reference Checker that:

- Finds files modified in the last N hours/days (configurable, default 48 hours) anywhere in the EGOS repository (excluding black-listed directories like `node_modules`, `.git`, `venv`).
- Searches for cross-references to these modified files across all other important files (e.g., `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.md`, etc.).
- Identifies undocumented files (i.e., files with no mentions or references outside of themselves or their own directory, configurable).
- Generates a structured report (JSON and/or Markdown) indicating which files are documented/referenced and which are not, including context for found references.
- Can be run both as a stand-alone CLI tool and as a callable Python module by an AI agent (e.g., in Windsurf via an `--agent-mode` flag).

## 2. Scope

- **Monitored File Types for Modification**: Configurable list of extensions (default includes common source code and documentation files like `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.md`).
- **Reference Target Files**: All files with important extensions where references might be found.
- **Reference Search Patterns**:
    - Exact filename matches (e.g., `example.py`).
    - Partial path matches (e.g., `scripts/cleaner` from root).
    - Base-name matches without extensions (e.g., `data_cleaner` from `data_cleaner.py`).
    - (Optional V2) Fuzzy or semantic matches if performance allows.
- **Excluded Directories**: Customizable list (hard-coded defaults: `node_modules`, `.git`, `venv`, `build`, `dist`, `__pycache__`).

## 3. How It Works (Planned)

1.  **Configuration Loading**: Load settings from a `.file_ref_checker.yml` or use CLI arguments.
2.  **Discover Modified Files**: Use `git log` to identify files changed within the specified time window, respecting monitored extensions and excluded directories.
3.  **Gather Reference Files**: Collect a list of all files where references might be found, respecting excluded directories.
4.  **Search for References**: For each modified file, iterate through all reference files and search for occurrences of its name/path using the defined patterns.
5.  **Report Generation**: Compile results into JSON and Markdown formats.
    -   **JSON Report**: Structured data suitable for machine processing.
        ```json
        {
          "report_id": "timestamp_uuid",
          "scan_parameters": {
            "time_window_hours": 48,
            "monitored_extensions": [".py", ".md"],
            "excluded_dirs": ["node_modules"]
          },
          "files_analyzed": [
            {
              "file_path": "src/module_a.py",
              "last_modified": "iso_timestamp",
              "is_documented": true,
              "referenced_by": [
                {"source_file": "tests/test_module_a.py", "line_number": 10, "context": "import src.module_a"},
                {"source_file": "docs/api/module_a.md", "line_number": 5, "context": "Details about module_a.py"}
              ]
            },
            {
              "file_path": "scripts/new_script.py",
              "last_modified": "iso_timestamp",
              "is_documented": false,
              "referenced_by": []
            }
          ],
          "summary": {
            "total_files_scanned": 1500,
            "modified_files_found": 5,
            "documented_files": 3,
            "undocumented_files": 2
          }
        }
        ```
    -   **Markdown Report**: Human-readable summary.
        ```markdown
        # File Reference Audit Report - YYYY-MM-DD HH:MM

        ## Summary
        - **Total Files Scanned:** 1500
        - **Modified Files (last 48h):** 5
        - **Documented:** 3
        - **Undocumented:** 2

        ## Undocumented Files
        - `scripts/new_script.py` (Last Modified: YYYY-MM-DD)
        - ...

        ## Documented Files & References
        ### `src/module_a.py`
        - Found in `tests/test_module_a.py:10` (Context: `import src.module_a`)
        - Found in `docs/api/module_a.md:5` (Context: `Details about module_a.py`)
        ---
        ```

## 4. Configuration (`.file_ref_checker.yml` - Example)

```yaml
# Configuration for File Reference Checker (KOS-AUD-001)
# Default time window in hours to check for modified files
time_window_hours: 48

# File extensions to monitor for modifications
monitored_extensions_for_modification:
  - ".py"
  - ".js"
  - ".ts"
  - ".md"
  - ".java"
  - ".cs"
  - ".go"
  - ".rb"
  - ".php"
  - ".rs"
  - ".swift"
  - ".kt"

# File extensions where references will be searched
reference_target_extensions:
  - ".py"
  - ".js"
  - ".ts"
  - ".md"
  - ".java"
  - ".cs"
  - ".go"
  - ".rb"
  - ".php"
  - ".rs"
  - ".swift"
  - ".kt"
  - ".json"
  - ".yaml"
  - ".yml"
  - ".xml"
  - ".html"
  - ".css"
  - ".txt"
  - ".rst"
  - ".tex"

# Directories to exclude from all scanning (both modification discovery and reference searching)
excluded_directories:
  - "node_modules"
  - ".git"
  - "venv"
  - ".venv"
  - "env"
  - ".env"
  - "build"
  - "dist"
  - "__pycache__"
  - ".pytest_cache"
  - ".mypy_cache"
  - ".ruff_cache"
  - "target" # For Rust/Java
  - "bin" # For Go/compiled outputs
  - "obj" # For .NET
  - "temp"
  - "tmp"
  - "docs/_build" # Sphinx builds
  - "site" # MkDocs, Jekyll sites

# Define what constitutes an "undocumented" file
# A file is considered undocumented if it has no references found:
# - anywhere_else: outside of its own content (e.g. self-imports or self-mentions)
# - outside_its_directory: outside of its own directory and parent directories up to project root (helps find orphan modules)
# - strictly_no_references: absolutely no references anywhere, including itself (rarely useful)
undocumented_file_criteria: "outside_its_directory"

# Agent mode settings
agent_mode:
  # If true, output will be minimal and machine-readable, suitable for AI agent consumption
  enabled: false
  # Format for agent mode output, if 'enabled' is true
  output_format: "json_summary" # "json_full", "json_summary", "text_brief"

# Reporting settings
reporting:
  # Directory where reports will be saved
  output_directory: "reports/file_reference_audits"
  # Filename template for reports. Placeholders: {timestamp}, {date}, {time}
  filename_template: "ref_audit_{timestamp}" # e.g., ref_audit_20250518_153000
  # Generate Markdown report
  markdown_report: true
  # Generate JSON report
  json_report: true
```

## 5. Future Considerations & Enhancements (V2+)

- **Integration with CI/CD**: Automate checks on pull requests or merges.
- **IDE Plugin**: Provide real-time feedback in IDEs.
- **Semantic Search**: Use embeddings or NLP to find conceptual references, not just string matches.
- **Ignoring Specific References**: Allow patterns or comments to mark certain references as "to be ignored" (e.g., `#noref`).
- **Automated Stub Creation**: For undocumented files, offer to create basic documentation stubs (e.g., a `README.md` in the directory or an entry in a module index).
- **Dependency Graph Visualization**: Generate a graph of file inter-references.
- **Performance Optimization**: For very large repositories, optimize file scanning and searching (e.g., using optimized grep-like tools or indexing).
- **Historical Analysis**: Track documentation coverage over time.

## 6. Dependencies

- **Git**: For identifying modified files.
- **Python**: Core language for the script.
- **PyYAML**: For parsing configuration files.
- (Potentially) `ripgrep` or similar for fast text searching, accessed via `subprocess`.

## 7. CLI Usage (Planned Example)

```bash
# Run with default configuration (from .file_ref_checker.yml if present)
python scripts/file_reference_checker.py

# Override time window to check files modified in the last 7 days
python scripts/file_reference_checker.py --time-window-days 7

# Specify particular extensions to monitor for modification
python scripts/file_reference_checker.py --monitor-ext .py .md

# Run in agent mode with JSON summary output
python scripts/file_reference_checker.py --agent-mode --agent-output-format json_summary

# Generate report in a custom directory
python scripts/file_reference_checker.py --report-dir custom_reports/
```

This plan outlines a robust tool for maintaining documentation hygiene and ensuring discoverability of new or modified code within the EGOS project.