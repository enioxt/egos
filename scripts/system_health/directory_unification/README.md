@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - scripts/docs/work_logs/WORK_2025_05_23_Directory_Unification_Analysis.md
  - scripts/docs/work_logs/WORK_2025_05_23_Directory_Unification_Implementation.md





  - scripts/system_health/directory_unification/README.md

# Directory Unification Tool

## Overview

The Directory Unification Tool is a comprehensive system for identifying, analyzing, and consolidating related content across the EGOS system. It follows EGOS Core Principles including Conscious Modularity, Systemic Cartography, and Evolutionary Preservation.

## Features

- **Keyword-based Content Discovery**: Find files and directories related to specific keywords
- **Cross-Reference Analysis**: Analyze relationships and dependencies between files
- **Intelligent Consolidation Planning**: Determine optimal target locations for consolidation
- **Safe Migration Execution**: Execute migrations with automatic backups and reference updates
- **Comprehensive Reporting**: Generate detailed HTML and Markdown reports with visualizations

## Architecture

The tool follows a modular architecture with clear separation of concerns:

```
directory_unification/
├── __init__.py               # Package exports
├── directory_unification_tool.py  # Main orchestration script
├── content_discovery.py      # Content discovery module
├── cross_reference_analyzer.py  # Cross-reference analysis module
├── consolidation_planner.py  # Consolidation planning module
├── migration_executor.py     # Migration execution module
├── report_generator.py       # Report generation module
└── utils.py                  # Shared utility functions
```

## Usage

### Basic Usage

```powershell
# Using the PowerShell wrapper (recommended)
.\Invoke-DirectoryUnification.ps1 -Keyword dashboard

# Direct Python execution
python scripts\maintenance\directory_unification\directory_unification_tool.py --keyword dashboard
```

### Dry Run Mode

```powershell
# Perform a dry run without making changes
python -m scripts.maintenance.directory_unification.directory_unification_tool --keyword dashboard --dry-run
```

### Advanced Usage

```powershell
# Run with specific target directory and exclusions
python -m scripts.maintenance.directory_unification.directory_unification_tool \
  --keyword dashboard \
  --target-dir apps/dashboards \
  --exclude-dirs venv node_modules .git \
  --exclude-files *.pyc *.log \
  --dry-run
```

## Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--keyword` | Keyword for content discovery and unification (required) |
| `--target-dir` | Target directory for consolidation (optional) |
| `--exclude-dirs` | Directories to exclude from search |
| `--exclude-files` | File patterns to exclude from search |
| `--max-depth` | Maximum depth for directory traversal |
| `--dry-run` | Perform a dry run without making changes |
| `--no-backup` | Skip creating backups |
| `--force` | Force execution even if backup fails |
| `--output-dir` | Output directory for results |
| `--egos-root` | Path to EGOS root directory |

## Testing

Run the test script to verify functionality:

```powershell
python -m scripts.maintenance.directory_unification.test_directory_unification
```

## Dependencies

- Python 3.8+
- colorama
- matplotlib (optional, for visualizations)
- networkx (optional, for visualizations)
- jinja2 (optional, for HTML reports)

## Integration with EGOS

This tool is registered in the EGOS tool registry (`config/tool_registry.json`) and follows all EGOS Core Principles and script standardization rules.

## Recommended Workflow

Based on our experience with the dashboard consolidation project, we recommend the following workflow for using the Directory Unification Tool:

1. **Analysis Phase**:
   - Run the tool with the target keyword to identify all related files
   - Review the generated report to understand the current distribution
   - Identify primary implementation and secondary/duplicate implementations

2. **Planning Phase**:
   - Create a detailed consolidation plan document (WORK_YYYY-MM-DD_Keyword_Consolidation.md)
   - Define the target directory structure
   - Create a mapping of source files to target locations
   - Document any special handling requirements

3. **Implementation Phase**:
   - Create backup of original files
   - Create target directory structure
   - Migrate files in logical batches (core files, modules, utilities)
   - Update imports and references
   - Create proper documentation (README.md)

4. **Verification Phase**:
   - Test functionality of consolidated implementation
   - Verify all references are updated
   - Update system documentation (DiagEnio.md)

## Case Study: Dashboard Consolidation

The Dashboard Consolidation project (May 2025) successfully applied this workflow to consolidate multiple dashboard implementations scattered across the EGOS system. Key steps included:

1. Initial analysis identified 23 primary dashboard files in `C:\EGOS\dashboard\app\` and several partial implementations in `apps\` subdirectories
2. Created a structured target directory at `C:\EGOS\apps\dashboard\` with specialized subdirectories (core, ui, integrations, analytics, utils)
3. Implemented a staged migration with full backup
4. Created comprehensive documentation including README and requirements.txt

This consolidation improved maintainability, reduced duplication, and aligned the dashboard implementation with EGOS principles of Conscious Modularity and Systemic Cartography.

## References

- [Directory Unification Implementation](../../docs/work_logs/WORK_2025_05_23_Directory_Unification_Implementation.md)
- [Directory Unification Analysis](../../docs/work_logs/WORK_2025_05_23_Directory_Unification_Analysis.md)
- [Cross-Reference System](../../scripts/cross_reference/README.md)
- [Directory Unification Tool PRD](C:\EGOS\docs\tools\directory_unification_tool_prd.md)
- [EGOS Cross-Reference System](C:\EGOS\docs\subsystems\cross_reference_system.md)
- [EGOS File Management Standards](C:\EGOS\docs\standards\file_management_standards.md)
- [Dashboard Consolidation Plan](C:\EGOS\WORK_2025-05-23_Dashboard_Consolidation.md)

✧༺❀༻∞ EGOS ∞༺❀༻✧