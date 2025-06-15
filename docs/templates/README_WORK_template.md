@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/templates/README_WORK_template.md

# WORK Log Template

This template provides the standardized structure for WORK log files in the EGOS system, following the guidelines established in [WORK_2025-05-23_Work_Log_Standardization.md](C:\EGOS\WORK_2025-05-23_Work_Log_Standardization.md).

## Usage

### Manual Creation

1. Copy the [WORK_template.md](C:\EGOS\docs\templates\WORK_template.md) file
2. Rename it following the pattern: `WORK_YYYY-MM-DD_Descriptive_Name.md`
3. Place it in the root directory (`C:\EGOS\`)
4. Fill in all the required sections

### Automated Creation

Use the WORK Log Manager tool:

```powershell
# From PowerShell
C:\EGOS\scripts\maintenance\work_log_manager.ps1 -Action Create -Title "Feature Implementation" -RoadmapIds "EGOS-EPIC-001" -Priority "High"
```

Or via the run_tools.py system:

```bash
# Using run_tools.py
python run_tools.py work_log_manager -Action Create -Title "Feature Implementation" -RoadmapIds "EGOS-EPIC-001" -Priority "High"
```

## Template Structure

The template includes:

1. YAML frontmatter with metadata
2. Title and key information section
3. Structured sections for:
   - Objective
   - Context
   - Completed Tasks
   - Next Steps
   - Modified Files
   - References

## Lifecycle Management

The WORK Log Manager tool provides commands to:

- Create new WORK logs
- Archive completed logs older than 7 days
- Validate logs against the standard
- Show status of all WORK logs

For more information, see [WORK_2025-05-23_Work_Log_Standardization.md](C:\EGOS\WORK_2025-05-23_Work_Log_Standardization.md).

✧༺❀༻∞ EGOS ∞༺❀༻✧