@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/cross_reference_priority_list.md
  - docs/governance/development_standards.md
  - docs/governance/file_lifecycle_management.md
  - docs/project_documentation/subsystems/KOIOS/KOS_standards.md





  - scripts/cross_reference/README.md

# EGOS Documentation Cross-Reference Tools

## Overview

This directory contains tools for managing cross-references within the EGOS documentation ecosystem. These tools implement the principle that "no file exists in isolation" by creating and maintaining a mycelium-like interconnection structure across all documentation files and code.

## Available Tools

### 1. File Reference Checker Ultra

**Location:** `file_reference_checker_ultra.py`

A high-performance tool for identifying references between files across the entire EGOS ecosystem. This optimized tool uses advanced techniques to efficiently process large codebases:

- **Parallel Processing**: Uses asyncio for concurrent file processing
- **Content Caching**: Avoids redundant file reads with an intelligent caching system
- **Aho-Corasick Algorithm**: Employs efficient multi-pattern matching
- **Hierarchical Processing**: Prioritizes files based on importance (configurable)
- **Detailed Progress Tracking**: Provides real-time updates with accurate ETA
- **Performance Monitoring**: Logs detailed metrics for optimization

**Key Features:**
- Process thousands of files efficiently with minimal memory footprint
- Beautiful progress display with accurate time estimates
- Partial run options for quick testing (25%, 50%, 75%)
- Detailed performance logging for analysis
- Configurable search patterns and exclusions

**Usage Example:**
```bash
# Run with default configuration
python scripts/cross_reference/file_reference_checker_ultra.py

# Run with custom configuration
python scripts/cross_reference/file_reference_checker_ultra.py --config scripts/cross_reference/config_performance_test.yaml

# Run with partial dataset (25%)
# Edit config.yaml and set performance.partial_run_percentage: 25
python scripts/cross_reference/file_reference_checker_ultra.py --config scripts/cross_reference/config_performance_test.yaml
```

**Performance Metrics:**
- Processing Speed: ~10-15 files per second (with caching)
- Memory Usage: Efficient even with large codebases
- Typical Runtime: Minutes instead of hours for full codebase analysis

### 2. Documentation Reference Manager

**Location:** `documentation_reference_manager/`

A modular package for scanning, analyzing, and enhancing cross-references across the EGOS documentation. This package implements the following functionality:

- **Scanning documentation files** to build a comprehensive map
- **Extracting existing references** from various formats (Markdown links, `@references` blocks)
- **Analyzing potential connections** between related documents
- **Adding suggested cross-references** to files that need them
- **Generating reports** on the cross-reference structure

**Usage Example:**
```bash
# Run with default settings (dry run mode)
python -m cross_reference.documentation_reference_manager.cli --base-path C:\EGOS

# Add references to files in a specific directory
python -m cross_reference.documentation_reference_manager.cli --base-path C:\EGOS --add-references --filter-dir docs/governance

# Generate a cross-reference report
python -m cross_reference.documentation_reference_manager.cli --base-path C:\EGOS --report reports/documentation/cross_reference_report.json
```

### 2. Recent Files Verifier

**Location:** `recent_files_verifier.py`

A tool for identifying recently modified files and verifying their cross-reference status. This tool helps maintain documentation integrity by ensuring that newly created or modified files are properly integrated into the documentation ecosystem.

**Usage Example:**
```bash
# Check files modified in the last 48 hours
python cross_reference/recent_files_verifier.py --base-path C:\EGOS --hours 48

# Check only Python files modified in the last 96 hours
python cross_reference/recent_files_verifier.py --base-path C:\EGOS --hours 96 --extensions .py

# Check only Markdown files in a specific directory
python cross_reference/recent_files_verifier.py --base-path C:\EGOS --hours 72 --extensions .md --filter-dir docs/governance
```

## Analysis Capabilities

These tools provide detailed insights into the EGOS documentation structure:

1. **Cross-Reference Density Analysis**
   - Identifies files with insufficient references (both incoming and outgoing)
   - Calculates reference density metrics across the documentation

2. **Documentation Health Metrics**
   - Percentage of files with proper cross-references
   - Orphaned documents (no references in or out)
   - Reference distribution patterns

3. **Temporal Analysis**
   - Recently modified files needing attention
   - Historical trends in cross-reference quality

4. **Directory-Specific Analysis**
   - Cross-reference patterns by directory
   - Subsystem interconnection metrics

## Implementation Details

The tools in this directory implement the following EGOS principles:

- **Conscious Modularity:** Each tool is designed with clear separation of concerns
- **Systemic Cartography:** Tools provide clear mapping of documentation relationships
- **Evolutionary Preservation:** Ensures documentation remains interconnected as it evolves

## Related Documentation

- [Development Standards](../../docs/governance/development_standards.md) - Core development standards including Golden Rule
- [File Lifecycle Management](../../docs/governance/file_lifecycle_management.md) - Detailed guidelines for file management
- [Cross-Reference Priority List](../../docs/governance/cross_reference_priority_list.md) - Files needing cross-reference attention
- [KOIOS Documentation Standards](../../docs/project_documentation/subsystems/KOIOS/KOS_standards.md) - Documentation standards