@references:
  - subsystems/AutoCrossRef/docs/ROADMAP.md

# AutoCrossRef Subsystem - Roadmap

**Version:** 0.1.5 (Reflects completion of core modules)
**Last Updated:** {{ CURRENT_DATE_ISO }}

## Overview

This document outlines the development roadmap for the AutoCrossRef subsystem. It has been updated to reflect the completion of core functional modules and to detail the next steps towards a fully operational tool.

## Phases

### Phase 1: Core Module Implementation (Completed)

- **[X] Task 1.1: Detailed Design Document (`DESIGN.md`)**
  - Core algorithms, data flows, and module responsibilities defined.
- **[X] Task 1.2: Configuration Loader (`src/config_loader.py`)**
  - Loads and validates `autocrossref_config.yaml`.
- **[X] Task 1.3: File Scanner (`src/scanner.py`)**
  - Traverses configured `scan_paths` and filters files by `include_file_extensions`.
- **[X] Task 1.4: Candidate Detector (`src/candidate_detector.py`)**
  - Identifies potential cross-reference candidates using regex and keyword patterns from config.
- **[X] Task 1.5: Path Resolver (`src/path_resolver.py`)**
  - Maps candidate strings to canonical file paths using a file index and known terms.
- **[X] Task 1.6: Existing Reference Checker (`src/existing_ref_checker.py`)**
  - Parses `@references:` blocks to check if a target path is already referenced, handling various path formats.
- **[X] Task 1.7: Reference Injector (`src/ref_injector.py`)**
  - Safely inserts new references into the `@references:` block, with backup and dry-run support.

### Phase 2: Orchestration, CLI, and Initial End-to-End Workflow (Est. 1-2 weeks)

- **[ ] Task 2.1: Orchestrator Development (`src/orchestrator.py`)**
  - Integrate all Phase 1 modules into a cohesive workflow: Scan -> Detect -> Resolve -> Check Existing -> [Suggest/Inject].
  - Implement logic for handling lists of candidates and batch processing.
- **[ ] Task 2.2: Command-Line Interface (CLI)**
  - Develop CLI arguments (using `argparse` or similar) for:
    - Specifying target files/directories for scanning.
    - Dry-run mode (report suggestions without modifying files).
    - Interactive mode (prompt user for each suggestion).
    - Automatic injection mode (with appropriate warnings).
    - Configuration file path.
- **[ ] Task 2.3: Suggestion Engine (Initial Version)**
  - Develop logic to format and present suggestions to the user (CLI output).
  - Filter out candidates that fail resolution or are already present.
- **[ ] Task 2.4: Initial End-to-End Testing**
  - Test the complete workflow on a diverse set of EGOS Markdown documents.
  - Refine error handling and user feedback.

### Phase 3: Testing, Refinement, and Advanced Features (Est. 2-3 weeks)

- **[ ] Task 3.1: Formal Unit & Integration Testing**
  - Create dedicated test files in `/tests` (using `unittest` or `pytest`) for all modules and the orchestrator.
  - Aim for comprehensive test coverage.
- **[ ] Task 3.2: Advanced Path Equivalency & Normalization**
  - Enhance `path_resolver.py` and `existing_ref_checker.py` to handle more complex path equivalency scenarios (e.g., case-insensitivity on Windows, symlinks, more robust relative path calculations from different contexts).
- **[ ] Task 3.3: Enhanced Configuration Options**
  - Allow more granular control over detection patterns, ignore rules, and output formatting via `autocrossref_config.yaml`.
- **[ ] Task 3.4: Support for Code Files (Python Docstrings - Basic)**
  - Extend `scanner.py` and `candidate_detector.py` to find candidates within Python docstrings.
  - Adapt `ref_injector.py` if docstring modification requires different logic than Markdown.
- **[ ] Task 3.5: Comprehensive Documentation Update**
  - Finalize `USAGE.md` with detailed CLI examples and configuration guide.
  - Update `DESIGN.md` with any architectural changes from Phase 2 & 3.
  - Create `INTEGRATION_PLAN.md` if specific integration points with other EGOS tools are identified.

### Phase 4: Beta Release & Future Enhancements (Ongoing)

- **[ ] Task 4.1: Beta Testing within EGOS Project**
  - Encourage wider use on EGOS documents and gather feedback.
- **[ ] Task 4.2: Performance Optimization**
  - Profile and optimize for large document sets if needed.
- **[ ] Task 4.3: Advanced Candidate Detection**
  - Explore NLP techniques or more sophisticated heuristics for identifying linkable terms.
- **[ ] Task 4.4: Reporting & Visualization**
  - Consider generating reports on cross-reference health or integrating with visualization tools.

## Future Considerations (Long-Term)

- Real-time suggestions (e.g., IDE integration or file watcher).
- Broader language/file type support beyond Markdown and Python docstrings.
- Integration with a potential central EGOS Reference Registry or Knowledge Graph.
- GUI for user interaction if CLI proves insufficient for complex scenarios.