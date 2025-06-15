@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - scripts/system_health/work_log_manager_README.md

# WORK Log Manager

## Overview

The WORK Log Manager is a PowerShell utility for managing WORK log files according to the EGOS standardized format. It provides functionality for creating, archiving, validating, and reporting on WORK files to ensure consistency across the EGOS ecosystem.

## Standard Reference

This tool implements the standards defined in [WORK_2025-05-23_Work_Log_Standardization.md](C:\EGOS\WORK_2025-05-23_Work_Log_Standardization.md), which establishes:

- Naming conventions (`WORK_YYYY-MM-DD_Descriptive_Name.md`)
- File structure with YAML frontmatter
- Location requirements (active files in root directory)
- Archiving process (7-day retention after completion)
- Roadmap integration requirements

## Usage

### Creating a New WORK Log

```powershell
.\work_log_manager.ps1 -Action Create -Title "Feature Implementation" -RoadmapIds "EGOS-EPIC-001" -Priority "High"
```

### Archiving Completed WORK Logs

```powershell
.\work_log_manager.ps1 -Action Archive
```

### Validating WORK Logs Against Standards

```powershell
.\work_log_manager.ps1 -Action Validate
```

### Viewing WORK Log Status

```powershell
.\work_log_manager.ps1 -Action Status
```

## Integration with EGOS

- **Tool Registry**: Registered in the central tool registry (`C:\EGOS\config\tool_registry.json`)
- **Template**: Uses the template at `C:\EGOS\docs\templates\WORK_template.md`
- **Cross-References**: Maintains references to the roadmap and related documents
- **Archiving**: Follows CRONOS principles for versioning and preservation

## References

- [WORK_2025-05-23_Work_Log_Standardization.md](C:\EGOS\WORK_2025-05-23_Work_Log_Standardization.md)
- [WORK_template.md](C:\EGOS\docs\templates\WORK_template.md)
- [README_WORK_template.md](C:\EGOS\docs\templates\README_WORK_template.md)
- [DiagEnio.md](C:\EGOS\DiagEnio.md)

✧༺❀༻∞ EGOS ∞༺❀༻✧