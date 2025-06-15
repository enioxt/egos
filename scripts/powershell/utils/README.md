@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - scripts/powershell/utils/README.md

# EGOS PowerShell Utilities

This directory contains PowerShell utility scripts for the EGOS project.

## Available Utilities

### Invoke-EGOSMigration.ps1

A utility script for automating file and directory migrations based on a CSV task definition. This script is particularly useful for reorganizing documentation, code, and other project assets according to EGOS standards.

#### Features

- CSV-driven migration tasks
- Support for both Move and Copy operations
- Handles files and directories
- Automatic parent directory creation
- Configurable overwrite behavior
- Dry run mode for testing migrations

#### Usage

```powershell
.\Invoke-EGOSMigration.ps1 -CsvPath <path_to_csv> [-DryRun]
```

#### CSV Format

The CSV file must contain the following headers:
- `SourcePath`: Path to the source file or directory
- `DestinationPath`: Path to the destination
- `ItemType`: 'File' or 'Directory'
- `Operation`: 'Move' or 'Copy'
- `CreateParents`: 'true' or 'false' (create parent directories if needed)
- `Overwrite`: 'true' or 'false' (overwrite existing files/directories)

#### Example CSV

```csv
SourcePath,DestinationPath,ItemType,Operation,CreateParents,Overwrite
C:\EGOS\docs\ai_collaboration,C:\EGOS\docs_egos\05_processes_and_workflows\ai_collaboration_legacy,Directory,Move,true,false
C:\EGOS\docs\prompts,C:\EGOS\docs_egos\04_modules_and_components\CORUJA\prompts,Directory,Copy,true,false
```

#### Documentation

For complete documentation, see <!-- TO_BE_REPLACED -->.

## Best Practices

1. Always run scripts with `-DryRun` first to verify operations
2. Back up important data before running migration scripts
3. Keep CSV files for documentation and potential rollback reference
4. Verify results after migration

## Cross-References

- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->

✧༺❀༻∞ EGOS ∞༺❀༻✧