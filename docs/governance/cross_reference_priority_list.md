@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/cross_reference_standard.md
  - docs/governance/development_standards.md
  - docs/governance/file_lifecycle_management.md
  - docs/templates/file_creation_checklist.md
  - scripts/cross_reference/documentation_reference_manager
  - scripts/cross_reference/recent_files_verifier.py






  - docs/governance/cross_reference_priority_list.md

# Cross-Reference Priority List

## Overview

This document identifies key files that require cross-references and documentation based on the recent files verification performed on May 18, 2025. It serves as an actionable list for improving the documentation interconnection structure within the EGOS ecosystem.

## Priority Categories

Files are categorized by priority based on their importance to the system and recent modification status:

1. **Critical Priority**: Core system files, roadmaps, and key documentation
2. **High Priority**: Subsystem documentation and important reference materials
3. **Medium Priority**: Supporting documentation and guides
4. **Low Priority**: Archived or backup files

## Critical Priority Files

These files are essential to the system and should be addressed immediately:

| File | Current Status | Action Required |
|------|----------------|-----------------|
| `README.md` | No references | Add outgoing references to key documentation |
| `ROADMAP.md` | No references | Add references to subsystem roadmaps |
| `docs/governance/development_standards.md` | New file | Add references to related standards |
| `docs/governance/file_lifecycle_management.md` | New file | Add references to development standards |
| `docs/templates/file_creation_checklist.md` | New file | Add references to governance documents |
| `docs/governance/cross_reference_standard.md` | No references | Add references to related documentation |
| `docs/governance/cross_reference_system_enhancements.md` | No references | Add references to implementation details |
| `docs/subsystems/KOIOS/KOS_roadmap.md` | No references | Add references to related KOIOS documents |

## High Priority Files

These files are important for system understanding and should be addressed soon:

| File | Current Status | Action Required |
|------|----------------|-----------------|
| `docs/reference/applying_cross_references.md` | No references | Add references to cross-reference tools |
| `scripts/cross_reference/recent_files_verifier.py` | New file | Add code documentation and references |
| `scripts/cross_reference/documentation_reference_manager` | New package | Ensure all modules have proper references |
| `docs/governance/roadmap_modularization_summary.md` | No references | Add references to related roadmaps |
| `docs/governance/roadmap_standardization.md` | No references | Add references to standardization efforts |

## Medium Priority Files

These supporting files should be addressed after higher priorities:

| File | Current Status | Action Required |
|------|----------------|-----------------|
| `docs/guides/ci_cd_cross_reference_integration.md` | No references | Add references to CI/CD documentation |
| `docs/reference/windows_powershell_commands.md` | No references | Add references to automation scripts |
| `scripts/SCRIPTS_INVENTORY.md` | No references | Add references to script categories |
| `scripts/README.md` | No references | Add references to key scripts |

## Implementation Plan

1. **Immediate Action**: Address Critical Priority files within the next week
2. **Short-term Action**: Address High Priority files within the next two weeks
3. **Medium-term Action**: Address Medium Priority files within the next month
4. **Automation**: Configure the Recent Files Verifier to run weekly and generate updated reports

## Monitoring Progress

Progress will be tracked by:

1. Running the Recent Files Verifier weekly with:
   ```
   python .\cross_reference\recent_files_verifier.py --base-path ..\ --hours 168 --report-dir reports\documentation\recent_files
   ```

2. Reviewing the generated reports to identify:
   - Files that have been properly cross-referenced
   - New files that need attention
   - Overall improvement in documentation interconnection

## Related Documents

- [MQP.md](../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](../ROADMAP.md) - Project roadmap and planning
- [Development Standards](./development_standards.md) - Core development standards including Golden Rule
- [File Lifecycle Management](./file_lifecycle_management.md) - Detailed guidelines for file management
- [File Creation Checklist](../templates/file_creation_checklist.md) - Template for new file creation
- [Cross-Reference Standard](./cross_reference_standard.md) - Standards for cross-references

## Implementation Tools

- [Recent Files Verifier](../../scripts/cross_reference/recent_files_verifier.py) - Tool to identify recently modified files needing cross-references
- [Documentation Reference Manager](../../scripts/cross_reference/documentation_reference_manager) - Package for managing cross-references