---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: readme
tags: [documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - scripts/system_health/cross_reference/README.md

---
title: Cross-Reference Analyzer
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

# Cross-Reference Analyzer

## Overview

The Cross-Reference Analyzer is a modular system for analyzing, validating, and improving cross-references across the EGOS codebase. It helps maintain the "mycelium network" of connections between files that is fundamental to EGOS's interconnected architecture.

## Architecture

The system follows a modular pipeline architecture with clear separation of concerns:

1. **FileScanner** (`scanner.py`): Discovers and filters files for analysis
2. **GraphBuilder** (`graph_builder.py`): Constructs a reference graph from files
3. **AnalysisEngine** (`engine.py`): Analyzes the graph to identify issues and generate suggestions
4. **AnalysisPipeline** (`pipeline.py`): Orchestrates the analysis process
5. **Reporters**: Generate reports in various formats (console, markdown)

```
                ┌─────────────┐
                │    Files    │
                └──────┬──────┘
                       │
                       ▼
┌──────────────────────────────────────┐
│            FileScanner               │
│  (Discovers and filters files)       │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│            GraphBuilder              │
│  (Builds reference graph)            │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│           AnalysisEngine             │
│  (Analyzes graph, generates report)  │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│             Reporters                │
│  (Generate output in various formats)│
└──────────────────────────────────────┘
```

## Usage

### Command Line

```powershell
# Basic usage (generates report)
python scripts/maintenance/run_cross_reference_analysis.py

# Verbose mode (shows detailed analysis)
python scripts/maintenance/run_cross_reference_analysis.py --verbose

# Fix issues automatically 
python scripts/maintenance/run_cross_reference_analysis.py --fix

# Specify custom root directory
python scripts/maintenance/run_cross_reference_analysis.py --root-dir /path/to/analyze
```

### Programmatic Usage

```python
from scripts.maintenance.cross_reference.pipeline import AnalysisPipeline

# Create a pipeline with custom configuration
pipeline = AnalysisPipeline(
    root_dir="/path/to/analyze",
    config={
        'verbose': True,
        'fix': False,
        'enable_rich': True,
        'markdown_report': True,
        'console_report': True,
        'report_dir': './reports',
    }
)

# Run the analysis
report = pipeline.run()

# Access analysis results
print(f"Health score: {report.health_score}")
print(f"Files with issues: {len(report.issues)}")
```

## Testing

The system includes comprehensive unit tests for each component:

```powershell
# Run all tests
python -m unittest discover -s scripts/maintenance/cross_reference/tests

# Run tests for a specific component
python -m unittest scripts/maintenance/cross_reference/tests/test_scanner.py
```

## Components

### FileScanner (`scanner.py`)

Responsible for discovering and filtering files for analysis.

```python
scanner = FileScanner(
    include_dirs=[root_dir],
    exclude_dirs=["venv", ".git"],
    include_exts=[".md", ".py"],
    exclude_exts=[".pyc"]
)
files = scanner.scan()
```

### GraphBuilder (`graph_builder.py`)

Builds a directed graph of references between files.

```python
graph_builder = GraphBuilder(root_dir)
graph = graph_builder.build_graph(files)
```

### AnalysisEngine (`engine.py`)

Analyzes the reference graph to identify issues and generate suggestions.

```python
engine = AnalysisEngine(graph, root_dir)
report = engine.analyze()
```

### AnalysisPipeline (`pipeline.py`)

Orchestrates the entire analysis process.

```python
pipeline = AnalysisPipeline(root_dir, config)
report = pipeline.run()
```

## Extending the System

### Adding New Parsers

To add support for a new file type:

1. Create a new parser in `parsers/` (implement the parse method)
2. Add the parser to `parser_mapping` in `graph_builder.py`

### Adding New Analysis Types

To add new analysis capabilities:

1. Add methods to `AnalysisEngine` for the new analysis
2. Update the `analyze` method to include the new analysis

### Adding New Report Formats

To add a new report format:

1. Create a new reporter class in `reporters/`
2. Update `AnalysisPipeline._create_reporters` to include the new reporter

## References

- <!-- TO_BE_REPLACED --> - Detailed documentation of the refactoring process
- <!-- TO_BE_REPLACED -->:KOIOS-DOC-009 - Cross-Reference Analyzer Refactoring task
- <!-- TO_BE_REPLACED --> - Best practices for cross-references