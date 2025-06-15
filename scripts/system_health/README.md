@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - WORK_2025_05_22_file_duplication_management.md
  - docs/process/script_management_guidelines.md
  - docs/technical/cross_reference_system.md





  - scripts/system_health/README.md

# EGOS Maintenance Scripts

This directory contains maintenance and optimization tools for the EGOS ecosystem.

## Overview

These scripts help maintain the integrity, efficiency, and organization of the EGOS system by automating routine maintenance tasks, detecting issues, and providing tools for system optimization.

## Available Tools

### File Duplication Auditor

**Script**: `file_duplication_auditor.py`

A comprehensive tool for detecting and managing file duplication across the EGOS ecosystem. The tool implements context-aware duplicate detection with robust caching and parallel processing capabilities.

#### Key Features

- **Multiple Detection Methods**:
  - Name-based identification (same filename in different locations)
  - Content-based identification (identical content hash)
  - Similarity-based identification (similar content above threshold)
  - Context-aware grouping (considers file purpose and location)

- **Performance Optimizations**:
  - File system and content hash caching
  - Parallel processing for hash computation and similarity analysis
  - Configurable workers, batch size, and timeouts
  - Optimized scanning with early filtering

- **Comprehensive Reporting**:
  - Multiple output formats (HTML, JSON, CSV, Markdown)
  - Detailed statistics and metrics
  - Interactive HTML reports with file details
  - Configurable report retention

- **System-Wide Scanning**:
  - Support for multiple root directories
  - Intelligent exclusion of standard directories
  - Cross-reference system integration

#### Usage

Basic usage:
```bash
python file_duplication_auditor.py --scan-dir <directory> --by-content --html
```

Advanced usage with context-aware scanning and caching:
```bash
python file_duplication_auditor.py --scan-system --scan-root C:\EGOS --by-content --context-aware --use-cache --num-workers 8 --html --json
```

For complete options:
```bash
python file_duplication_auditor.py --help
```

#### References

- Work Log: [WORK_2025_05_22_file_duplication_management.md](../../WORK_2025_05_22_file_duplication_management.md)
- Standards: [script_management_guidelines.md](../../docs/process/script_management_guidelines.md)
- Integration: [cross_reference_system.md](../../docs/technical/cross_reference_system.md)

## Future Tools

Additional maintenance tools planned or in development:

1. **Storage Optimization Tool** - Identify large files and suggest compression options
2. **Documentation Health Scanner** - Ensure all modules have proper documentation
3. **Dependency Tracker** - Monitor and report on module dependencies and imports

---

✧༺❀༻∞ EGOS ∞༺❀༻✧