@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/core_materials/standards/snake_case_naming_convention.md

# EGOS `snake_case` Naming Convention Standard

## Overview

This document defines the standard for `snake_case` naming convention within the EGOS project, in alignment with the Master Quantum Prompt (MQP v9.0 "Full Moon Blueprint") principles, particularly Systemic Cartography (SC) and Conscious Modularity (CM).

## Definition

`snake_case` is a naming convention where:
- All letters are lowercase
- Words are separated by underscores (`_`)
- No spaces or hyphens are allowed
- No special characters except underscores

Examples:
- `file_name.py`
- `directory_name`
- `function_name`
- `variable_name`

## Scope of Application

This naming convention applies to:
1. All file names (with exceptions noted below)
2. All directory names (with exceptions noted below)
3. All Python variables, functions, and modules
4. Configuration keys and database field names

## Exceptions

The following items are exempt from the `snake_case` requirement:
1. Files with standard names that follow other conventions (e.g., `README.md`, `LICENSE`)
2. System directories (e.g., `.git`, `.vscode`)
3. Third-party dependencies (e.g., `node_modules`)
4. Work log files following the date-based naming pattern (`WORK_YYYY-MM-DD_Title.md`)
5. Core EGOS documents with established names (e.g., `MQP.md`, `ROADMAP.md`, `ADRS_Log.md`)

## Conversion Process

The conversion of existing files and directories to `snake_case` is managed through a phased approach:

1. **Audit**: Using `C:\EGOS\scripts\utils\audit_snake_case.py` to identify non-compliant items
2. **Analysis**: Reviewing audit results and prioritizing items for conversion
3. **Conversion**: Using `C:\EGOS\scripts\utils\convert_to_snake_case.py` to rename items, following the prioritization strategy:
   - Tier 1: Core Scripts & Configuration
   - Tier 2: Core EGOS Framework & Key Documentation
   - Tier 3: Ancillary Components & High-Volume Areas
   - Tier 4: Archived/Less Critical Areas

## Configuration

The conversion process is configured through `C:\EGOS\config\snake_case_convert_config.json`, which specifies:
- Directories to exclude
- Files to exclude
- File extensions where stem case should be preserved
- Path patterns to ignore (using regex)

## Maintenance

To maintain `snake_case` compliance:
1. All new files and directories must follow the `snake_case` convention
2. Run the audit script periodically to identify any new non-compliant items
3. Update the configuration file as needed to reflect new exceptions

## References

- [MQP.md](C:\EGOS\MQP.md) - Master Quantum Prompt defining EGOS principles
- [ADRS_Log.md](C:\EGOS\ADRS_Log.md) - Anomaly & Deviation Reporting System log
- [snake_case_conversion_plan.md](C:\EGOS\docs\planning\snake_case_conversion_plan.md) - Detailed conversion plan