@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/script_ecosystem_analyzer/README.md

# Script Ecosystem Analyzer

## Overview

The Script Ecosystem Analyzer is a tool that analyzes the distribution and health of scripts and documentation across the EGOS system. It creates a "heat map" visualization that identifies:

- **Isolated scripts**: Scripts in directories with few other scripts
- **Potentially orphaned scripts**: Scripts with low cross-references or no recent modifications
- **Underdeveloped areas**: Directories with few scripts
- **Documentation health**: Documentation without clear purpose or references

This tool is part of the unified health check framework and integrates with the CORUJA subsystem and EGOS website.

## Purpose

The primary purpose of this tool is to provide a comprehensive view of the EGOS script ecosystem, helping identify areas that need attention or consolidation. By visualizing the distribution of scripts and documentation, it helps maintain a well-organized and interconnected system.

## Integration with EGOS

The Script Ecosystem Analyzer is integrated with the following EGOS components:

- **Health Check Framework**: Part of the unified health check system (`C:\EGOS\scripts\system_health\`)
- **CORUJA Subsystem**: Analyzes connections with the human-AI interaction subsystem (`C:\EGOS\subsystems\coruja\`)
- **Website**: Generates reports that are integrated with the EGOS website (`C:\EGOS\website\content\reports\`)

## Features

### Heat Map Visualization

The analyzer generates a heat map visualization of the directory structure, using temperature indicators to show script density:

```
└── ❄️ docs (3 scripts, 45 docs)
    ├── 🔵 core_materials (1 scripts, 20 docs)
    ├── 🟢 planning (5 scripts, 10 docs)
    └── 🔴 tools (15 scripts, 5 docs)
```

### Script Density Analysis

The analyzer provides a detailed breakdown of script and documentation density by directory, helping identify hot and cold areas of development.

### Orphaned Script Detection

The analyzer identifies potentially orphaned scripts by analyzing cross-references and modification dates.

### Documentation Health Check

The analyzer evaluates documentation health by checking for purpose statements and cross-references.

### CORUJA Integration

The analyzer includes special analysis of the CORUJA subsystem, highlighting connections between scripts and the human-AI interaction components.

### Website Integration

The analyzer generates reports that are automatically integrated with the EGOS website, ensuring visibility of the analysis results.

## Usage

### Command Line

```bash
python C:\EGOS\scripts\system_health\analyzers\script_ecosystem_analyzer.py [target_path] --output [output_path] --website-integration
```

### Parameters

- `target_path`: Path to analyze (default: EGOS root directory)
- `--output`: Path to save the report (default: auto-generated)
- `--config`: Path to configuration file
- `--verbose`: Enable verbose logging
- `--max-file-size`: Maximum file size in MB to analyze (default: 10)
- `--website-integration`: Generate website integration files

### Configuration

The analyzer can be configured using a JSON configuration file:

```json
{
  "exclusions": [
    ".git", "venv", ".venv", "env", "node_modules", "__pycache__", 
    ".vscode", ".idea", "build", "dist", ".pytest_cache"
  ],
  "script_extensions": [".py", ".sh", ".bat", ".ps1", ".js", ".ts", ".rb"],
  "doc_extensions": [".md", ".txt", ".rst", ".html", ".pdf", ".docx"],
  "max_age_days": 180,
  "min_references": 1,
  "min_scripts_per_dir": 3,
  "visualization": {
    "enabled": true,
    "max_depth": 4,
    "heat_scale": ["❄️", "🔵", "🟢", "🟡", "🔴", "🔥"]
  }
}
```

## Integration Script

The Script Ecosystem Analyzer includes an integration script that ensures proper connections with other EGOS components:

```bash
python C:\EGOS\scripts\system_health\integrations\ecosystem_analyzer_integrator.py --all
```

This script:

1. Runs the analyzer
2. Creates website integration
3. Creates CORUJA integration
4. Updates cross-references

## Output Format

All reports are generated in Markdown format, following EGOS standard RULE-REPORT-STD-01. Reports include:

1. Summary of findings
2. Heat map visualization
3. Script density analysis
4. Lists of potentially orphaned scripts
5. Lists of isolated scripts
6. Lists of underdeveloped areas
7. Documentation health analysis
8. CORUJA integration analysis
9. Website integration analysis

## References

- [Health Check Unification Plan](C:\EGOS\docs\planning\health_check_unification_plan.md)
- [CORUJA Subsystem](C:\EGOS\subsystems\coruja\README.md)
- [EGOS Website](C:\EGOS\website\README.md)
- [Script Ecosystem Analyzer](C:\EGOS\scripts\system_health\analyzers\script_ecosystem_analyzer.py)
- [Ecosystem Analyzer Integrator](C:\EGOS\scripts\system_health\integrations\ecosystem_analyzer_integrator.py)
- [Master Quantum Prompt](C:\EGOS\MQP.md) (Systemic Cartography, Evolutionary Preservation)