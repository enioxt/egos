@references:
  - subsystems/AutoCrossRef/docs/USAGE.md

# AutoCrossRef Subsystem - Usage Guide

**Version:** 0.1
**Last Updated:** {{ CURRENT_DATE_ISO }}

## 1. Introduction

This guide explains how to use the AutoCrossRef subsystem CLI tool.

## 2. Prerequisites

- Python 3.x
- Access to the EGOS project file system.
- Required dependencies (to be listed in `requirements.txt` or `pyproject.toml` for AutoCrossRef).

## 3. Installation

(To be detailed - likely involves ensuring the `C:\EGOS\subsystems\AutoCrossRef\src` is in PYTHONPATH or the tool is installed via a setup.py/pyproject.toml).

## 4. Command-Line Interface (CLI)

(This is a preliminary design and will evolve)

```bash
python -m autocrossref.orchestrator <command> [options] [paths...]
```

### 4.1. Commands

- **`scan`**: 
  - Description: Scans specified paths or configured default paths for potential new cross-references and reports them (dry-run by default).
  - Usage: `python -m autocrossref.orchestrator scan [paths...] [--apply] [--interactive]`
  - `[paths...]`: Optional list of specific files or directories to scan. If omitted, uses paths from `autocrossref_config.yaml`.
  - Options:
    - `--apply`: If present, approved suggestions will be written to files (requires confirmation).
    - `--interactive`: Prompts the user to approve/reject each suggestion individually before applying (if `--apply` is also used).
    - `--config <path_to_config>`: Specify a custom `autocrossref_config.yaml`.
    - `--output <report_file.json>`: Save suggestions to a JSON report file.

- **`validate`**: (Future command)
  - Description: Validates existing cross-references in specified paths using the underlying `file_reference_checker_ultra.py` logic.
  - Usage: `python -m autocrossref.orchestrator validate [paths...]`

### 4.2. Examples

- **Scan default directories and show suggestions:**
  ```bash
  python -m autocrossref.orchestrator scan
  ```

- **Scan a specific directory and its subdirectories:**
  ```bash
  python -m autocrossref.orchestrator scan C:\EGOS\docs\subsystems
  ```

- **Scan and interactively apply suggestions:**
  ```bash
  python -m autocrossref.orchestrator scan --apply --interactive C:\EGOS\docs\guides
  ```

## 5. Configuration

- The primary configuration file is `C:\EGOS\subsystems\AutoCrossRef\config\autocrossref_config.yaml`.
- It also respects settings in `C:\EGOS\scripts\cross_reference\config_ultra.yaml` for file discovery rules.

## 6. Output & Reports

- By default, suggestions are printed to the console.
- The `--output` option can be used to save suggestions to a structured format (e.g., JSON) for review or programmatic use.

## 7. Troubleshooting

- (To be added as common issues are identified)