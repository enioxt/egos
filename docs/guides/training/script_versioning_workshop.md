---
title: EGOS Script Versioning Standards Workshop
version: 1.0.0
status: Active
date_created: 2025-05-16
date_modified: 2025-05-16
authors: [EGOS Team]
description: Training materials for EGOS script versioning standards and practices
file_type: documentation
scope: development
primary_entity_type: training
primary_entity_name: script_versioning_workshop
tags: [training, versioning, scripts, standards, documentation]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/docs/development/script_versioning_standards.md
  - docs/docs/governance/documentation_standards.md





  - docs/guides/training/script_versioning_workshop.md

# EGOS Script Versioning Standards Workshop

## Overview

This document serves as the training material for the EGOS Script Versioning Standards workshop. It provides a comprehensive guide to understanding and implementing the versioning standards across all EGOS scripts.

## Learning Objectives

By the end of this workshop, participants will be able to:

1. Understand the importance of script versioning in the EGOS ecosystem
2. Apply the EGOS versioning standards to new and existing scripts
3. Use the versioning tools to track and enforce compliance
4. Integrate versioning checks into their development workflow

## Prerequisites

- Basic understanding of EGOS project structure
- Familiarity with Python, PowerShell, and/or Batch scripting
- Git knowledge (basic commands and workflow)

## Workshop Agenda

1. Introduction to Script Versioning (30 minutes)
2. EGOS Versioning Standards (45 minutes)
3. Hands-on Practice: Adding Version Headers (60 minutes)
4. Using the Version Tracking Tools (45 minutes)
5. Git Integration and Workflow (30 minutes)
6. Q&A and Best Practices (30 minutes)

## 1. Introduction to Script Versioning

### Why Version Scripts?

Script versioning provides several critical benefits:

- **Traceability**: Track changes and understand the evolution of scripts over time
- **Accountability**: Identify authors and contributors for each script
- **Maintenance**: Simplify maintenance by documenting changes and their rationale
- **Compliance**: Ensure adherence to organizational standards
- **Collaboration**: Facilitate collaboration among team members

### The Cost of Unversioned Scripts

Without proper versioning:

- Scripts may become outdated without clear indicators
- Changes may be made without documentation
- Troubleshooting becomes more difficult
- Knowledge transfer is hindered
- Compliance with standards cannot be verified

## 2. EGOS Versioning Standards

### Semantic Versioning

EGOS scripts follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### Standard Header Templates

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

### Required Header Fields

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

## 3. Hands-on Practice: Adding Version Headers

### Exercise 1: Analyze an Existing Script

1. Select an existing script from your subsystem
2. Identify its purpose, author, and approximate creation date
3. Determine appropriate version number based on its maturity

### Exercise 2: Add Version Header

1. Add the appropriate version header to your selected script
2. Document any known changes in the change history
3. Add references to relevant documentation

### Exercise 3: Update an Existing Header

1. Select a script with an outdated header
2. Update the version number according to semantic versioning rules
3. Add your changes to the change history

## 4. Using the Version Tracking Tools

### Track Script Versions Tool

The `track_script_versions.py` tool scans directories for scripts and reports on their versioning status:

```bash
python scripts/tools/version_control/track_script_versions.py --directory scripts/tools
```

Features:
- Identifies scripts with and without version information
- Generates reports on versioning compliance
- Supports multiple script types (Python, PowerShell, Batch)

### Version Check Hook

The `version_check_hook.py` tool verifies that scripts follow versioning standards:

```bash
python scripts/tools/version_control/version_check_hook.py --directory scripts/tools
```

Options:
- `--strict`: Fail if any script lacks proper versioning
- `--fix`: Automatically add template headers to scripts missing version information

## 5. Git Integration and Workflow

### Pre-commit Hook Installation

To install the pre-commit hook:

```bash
scripts/tools/version_control/install_git_hooks.bat
```

This will:
1. Copy the pre-commit hook to your local `.git/hooks` directory
2. Make the hook executable
3. Configure Git to use the hooks

### Development Workflow

1. Create or modify a script
2. Ensure proper version header is included
3. Update version number and change history if modifying an existing script
4. Commit changes (pre-commit hook will verify versioning)
5. If the hook fails, fix the issues and try again

### Automated Audits

Bi-weekly audits will be conducted to ensure ongoing compliance:

1. The tracking tool will scan all script directories
2. Reports will be generated in `reports/script_versioning/`
3. Non-compliant scripts will be flagged for updates

## 6. Q&A and Best Practices

### Best Practices

1. **Always increment version numbers** when making changes
2. **Be descriptive in change history** entries
3. **Include references** to related documentation or tickets
4. **Run the tracking tool** before committing to catch issues early
5. **Follow semantic versioning rules** consistently

### Common Pitfalls

1. Forgetting to update the "Last Updated" date
2. Inconsistent version numbering
3. Vague change history entries
4. Missing references to documentation
5. Incorrect version increments (e.g., using MAJOR when MINOR is appropriate)

## Resources

- [Script Versioning Standards](../../docs/development/script_versioning_standards.md)
- [EGOS Documentation Standards](../../docs/governance/documentation_standards.md)
- [Semantic Versioning](https://semver.org/)

## Conclusion

Consistent script versioning is essential for maintaining the EGOS codebase. By following these standards and using the provided tools, we can ensure that our scripts remain well-documented, traceable, and maintainable.

---

**Workshop Date:** 2025-05-20
**Location:** Virtual Meeting
**Facilitator:** EGOS Development Team

For questions or assistance, contact the EGOS Development Team.

✧༺❀༻∞ EGOS ∞༺❀༻✧