---
title: EGOS Script Versioning Standards
version: 1.0.0
status: Active
date_created: 2025-05-16
date_modified: 2025-05-16
authors: [EGOS Team]
description: Comprehensive documentation of EGOS script versioning standards and practices
file_type: documentation
scope: development
primary_entity_type: standard
primary_entity_name: script_versioning
tags: [development, versioning, scripts, standards, documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/guides/development/script_versioning_standards.md

# EGOS Script Versioning Standards

## Overview

This document defines the standardized versioning system for all scripts within the EGOS ecosystem. These standards ensure consistency, traceability, and maintainability across the codebase, facilitating collaboration and knowledge transfer among team members.

## Core Principles

The EGOS script versioning system is built on the following core principles, aligned with the EGOS foundational values:

1. **Conscious Modularity**: Each script is a discrete module with clear versioning that reflects its evolution.
2. **Evolutionary Preservation**: Version history preserves the evolutionary path of each script.
3. **Systemic Cartography**: Versioning provides a map of the script ecosystem and its interconnections.
4. **Integrated Ethics**: Proper versioning supports accountability and transparency.

## Version Numbering

### Semantic Versioning

All EGOS scripts follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incremented for incompatible API changes or significant functionality changes that may break existing dependencies.
- **MINOR**: Incremented for backwards-compatible functionality additions or improvements.
- **PATCH**: Incremented for backwards-compatible bug fixes or minor improvements.

### Initial Versioning

- All new scripts start at version `1.0.0`.
- Existing scripts without version information should be assigned an appropriate version based on their maturity and stability.

### Version Incrementation Guidelines

| Change Type | Example | Version Increment |
|-------------|---------|-------------------|
| Bug fix | Fix typo in output message | PATCH (1.0.0 → 1.0.1) |
| Minor enhancement | Add optional parameter | MINOR (1.0.0 → 1.1.0) |
| Performance improvement | Optimize algorithm | MINOR (1.0.0 → 1.1.0) |
| Breaking change | Change required parameters | MAJOR (1.0.0 → 2.0.0) |
| Complete rewrite | Reimplement using different approach | MAJOR (1.0.0 → 2.0.0) |

## Script Header Standards

### Required Header Fields

All scripts must include a standardized header with the following information:

| Field | Description | Required? |
|-------|-------------|-----------|
| Script Name | Name of the script file | Yes |
| Description | Brief description of script purpose | Yes |
| Version | Semantic version number | Yes |
| Author | Original author or team | Yes |
| Creation Date | Initial creation date (YYYY-MM-DD) | Yes |
| Last Updated | Date of most recent update (YYYY-MM-DD) | Yes |
| Change History | Log of version changes with dates | Yes |
| References | Links to related documentation | Recommended |

### Header Templates

#### Python Scripts

```python
# Script Name: script_name.py
# 
# Description of what the script does
# 
# Version:        1.0.0
# Author:         Author Name
# Creation Date:  YYYY-MM-DD
# Last Updated:   YYYY-MM-DD
# 
# Change History:
# 1.0.0 (YYYY-MM-DD) - Initial version
# 
# References:
# - Link to relevant documentation
```

#### PowerShell Scripts

```powershell
# Script Name: script_name.ps1
# 
# Description of what the script does
# 
# Version:        1.0.0
# Author:         Author Name
# Creation Date:  YYYY-MM-DD
# Last Updated:   YYYY-MM-DD
# 
# Change History:
# 1.0.0 (YYYY-MM-DD) - Initial version
# 
# References:
# - Link to relevant documentation
```

#### Batch Files

```batch
@echo off
REM Script Name: script_name.bat
REM 
REM Description of what the script does
REM 
REM Version:        1.0.0
REM Author:         Author Name
REM Creation Date:  YYYY-MM-DD
REM Last Updated:   YYYY-MM-DD
REM 
REM Change History:
REM 1.0.0 (YYYY-MM-DD) - Initial version
REM 
REM References:
REM - Link to relevant documentation
```

### Change History Format

The change history should follow this format:
- Version number (date) - Description of changes

Example:
```
# Change History:
# 1.0.0 (2025-05-01) - Initial version
# 1.0.1 (2025-05-05) - Fixed output formatting bug
# 1.1.0 (2025-05-10) - Added support for JSON output
```

## Versioning Tools

### Script Version Tracking Tool

The `track_script_versions.py` tool scans directories for scripts and reports on their versioning status:

```bash
python scripts/tools/version_control/track_script_versions.py --directory scripts/tools
```

#### Features

- Identifies scripts with and without version information
- Generates reports on versioning compliance
- Supports multiple script types (Python, PowerShell, Batch)
- Optional JSON output for integration with other tools

#### Options

- `--directory`: Directory to scan for scripts
- `--json`: Output results in JSON format
- `--fix`: Automatically add template headers to scripts missing version information
- `--report`: Generate a detailed markdown report

### Version Check Hook

The `version_check_hook.py` tool verifies that scripts follow versioning standards:

```bash
python scripts/tools/version_control/version_check_hook.py --directory scripts/tools
```

#### Options

- `--directory`: Directory to check for script versioning
- `--strict`: Fail if any script lacks proper versioning
- `--fix`: Automatically add template headers to scripts missing version information

## Integration with Git Workflow

### Pre-commit Hook

A pre-commit hook is provided to ensure all scripts adhere to versioning standards before being committed:

1. The hook checks all scripts in the commit for proper version headers
2. If any script lacks a version header, the commit is rejected
3. The developer can fix the issues manually or use the `--fix` option of the version check tool

### Installation

To install the pre-commit hook:

```bash
scripts/tools/version_control/install_git_hooks.bat
```

This script:
1. Copies the pre-commit hook to your local `.git/hooks` directory
2. Makes the hook executable
3. Configures Git to use the hooks

## Regular Audits

Bi-weekly audits are conducted to ensure ongoing compliance with versioning standards:

1. The `run_versioning_audit.py` script scans all script directories
2. Reports are generated in `reports/script_versioning/`
3. Email notifications are sent to the development team
4. Non-compliant scripts are flagged for updates

### Scheduling Audits

To schedule regular audits:

```bash
scripts/tools/version_control/schedule_versioning_audits.bat
```

This sets up a Windows Task Scheduler task to run the audit every two weeks.

## Best Practices

### When Updating Scripts

1. **Always increment the version number** according to semantic versioning rules
2. **Update the "Last Updated" date** to the current date
3. **Add an entry to the change history** describing your changes
4. **Update references** if new documentation is relevant

### Common Pitfalls to Avoid

1. Forgetting to update the "Last Updated" date
2. Inconsistent version numbering
3. Vague change history entries
4. Missing references to documentation
5. Incorrect version increments (e.g., using MAJOR when MINOR is appropriate)

## Compliance Requirements

### New Scripts

All new scripts must include proper version headers before being committed to the repository.

### Existing Scripts

All existing scripts should be updated to include version headers according to the following timeline:

1. Core utility scripts: Immediate
2. Subsystem-specific scripts: Within 2 weeks
3. Test and development scripts: Within 1 month

## Training and Support

### Documentation

- This document: `docs/development/script_versioning_standards.md`
- Training materials: `docs/training/script_versioning_workshop.md`

### Workshops

Regular training workshops are conducted to ensure all team members understand and can apply the versioning standards.

### Support Channels

For questions or assistance with script versioning:
- Contact the EGOS Development Team
- Refer to the training materials
- Review examples in the codebase

## Appendix

### Example: Well-Versioned Script

```python
# Script Name: example_script.py
# 
# Demonstrates proper versioning standards for EGOS scripts
# 
# Version:        1.2.0
# Author:         EGOS Team
# Creation Date:  2025-05-01
# Last Updated:   2025-05-16
# 
# Change History:
# 1.0.0 (2025-05-01) - Initial version
# 1.0.1 (2025-05-05) - Fixed output formatting bug
# 1.1.0 (2025-05-10) - Added support for JSON output
# 1.2.0 (2025-05-16) - Added command-line arguments
# 
# References:
# - docs/development/script_versioning_standards.md
# - docs/api/json_output_format.md

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Example script demonstrating versioning")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()
    
    data = {"message": "Hello, EGOS!", "status": "success"}
    
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"Message: {data['message']}")
        print(f"Status: {data['status']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Version Tracking Report Example

```markdown
# Script Versioning Report

## Summary
- Total Scripts: 41
- Scripts with Version Information: 41 (100%)
- Scripts without Version Information: 0 (0%)

## Compliance by Directory
| Directory | Total | Versioned | Unversioned | Compliance % |
|-----------|-------|-----------|-------------|--------------|
| scripts/tools | 25 | 25 | 0 | 100% |
| subsystems/AETHER/scripts | 5 | 5 | 0 | 100% |
| subsystems/ATLAS/scripts | 3 | 3 | 0 | 100% |
| subsystems/KOIOS/scripts | 8 | 8 | 0 | 100% |

## Conclusion
All scripts comply with EGOS versioning standards.
```

---

✧༺❀༻∞ EGOS ∞༺❀༻✧