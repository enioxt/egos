---
title: 'Script Ecosystem Analyzer'
date: '2025-05-27'
updated: '2025-05-27'
author: 'EGOS System'
description: 'Analyzes the distribution and health of scripts and documentation across the EGOS system, creating heat map visualizations and identifying orphaned scripts.'
categories: ['tools', 'system-health', 'analysis']
tags: ['scripts', 'analysis', 'health-check', 'documentation', 'heat-map', 'visualization', 'orphaned-scripts', 'coruja-integration']
---

# Script Ecosystem Analyzer

## Overview

The Script Ecosystem Analyzer is a tool that analyzes the distribution and health of scripts and documentation across the EGOS system. It creates a "heat map" visualization that identifies:

- **Isolated scripts**: Scripts in directories with few other scripts
- **Potentially orphaned scripts**: Scripts with low cross-references or no recent modifications
- **Underdeveloped areas**: Directories with few scripts
- **Documentation health**: Documentation without clear purpose or references

This tool is part of the unified health check framework and integrates with the CORUJA subsystem and EGOS website.

## Integration with EGOS

The Script Ecosystem Analyzer is integrated with the following EGOS components:

- **Health Check Framework**: Part of the unified health check system
- **CORUJA Subsystem**: Analyzes connections with the human-AI interaction subsystem
- **Website**: Generates reports that are integrated with the EGOS website

## Features

### Heat Map Visualization

The analyzer generates a heat map visualization of the directory structure, using temperature indicators to show script density:

```
└── ❄️ docs (3 scripts, 45 docs)
    ├── 🔵 core_materials (1 scripts, 20 docs)
    ├── 🟢 planning (5 scripts, 10 docs)
    └── 🔴 tools (15 scripts, 5 docs)
        └── 🔥 script_ecosystem_analyzer (8 scripts, 2 docs)
```

The heat scale ranges from cold (❄️) to hot (🔥), indicating areas with low to high script density.

### Script Density Analysis

The analyzer provides a detailed breakdown of script and documentation density by directory, helping identify hot and cold areas of development.

### Orphaned Script Detection

The analyzer identifies potentially orphaned scripts by analyzing cross-references and modification dates.

### Documentation Health Check

The analyzer evaluates documentation health by checking for purpose statements and cross-references.

### CORUJA Integration

The analyzer includes special analysis of the CORUJA subsystem, highlighting connections between scripts and the human-AI interaction components. This integration helps identify how scripts interact with human-AI interfaces and ensures proper cross-referencing between components.

### Large File Handling

The analyzer includes special handling for large documentation files, using chunked reading to prevent memory issues when analyzing extensive documentation.

### Website Integration

The analyzer automatically generates website integration files, making it easy to publish analysis results to the EGOS website. This integration is handled by the `ecosystem_analyzer_integrator.py` script.

## Usage

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
- `--coruja-analysis`: Perform special analysis of CORUJA subsystem
- `--update-references`: Update cross-references in documentation

### Integration Script

For full integration with the EGOS ecosystem, use the integration script:

```bash
python C:\EGOS\scripts\system_health\integrations\ecosystem_analyzer_integrator.py
```

This script handles:
- Updating cross-references in documentation
- Integrating with the CORUJA subsystem
- Generating website content
- Creating visualization files

## Latest Reports

- [Latest Script Ecosystem Analysis](/reports/script_ecosystem_report/)
- [Documentation Health Analysis](/reports/documentation_health_report/)
- [CORUJA Integration Analysis](/reports/coruja_integration_report/)

## Documentation

Comprehensive documentation for the Script Ecosystem Analyzer is available in the following locations:

- [Script Ecosystem Analyzer README](C:\EGOS\docs\tools\script_ecosystem_analyzer\README.md)
- [Implementation Work Log](C:\EGOS\WORK_2025-05-27_Script_Ecosystem_Analyzer_Implementation.md)
- [Documentation Index](C:\EGOS\docs\index\documentation_index.md)

## References

- [Health Check Unification Plan](/docs/planning/health_check_unification_plan/)
- [CORUJA Subsystem](/subsystems/coruja/)
- [EGOS Roadmap](/roadmap/)
- [Master Quantum Prompt (MQP)](/MQP/) - Systemic Cartography (SC) and Evolutionary Preservation (EP) principles