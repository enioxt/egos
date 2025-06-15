@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/governance/migrations/universal_migration_framework.md

# EGOS Universal Migration Framework

**Status:** Active  
**Version:** 1.0.0  
**Last Updated:** 2025-05-20  
**Subsystem:** KOIOS

## Overview

The EGOS Universal Migration Framework provides a standardized approach to migrating files, directories, and content within the EGOS ecosystem. This framework was developed based on the successful documentation migration process and has been generalized for use in any future migration scenarios.

## Framework Components

The Universal Migration Framework consists of the following components:

### 1. Migration Scripts

| Script | Purpose | Description |
|--------|---------|-------------|
| `docs_structure_migrator.py` | File Migration | Moves files to new locations while preserving metadata and updating cross-references |
| `docs_migration_verification.py` | Migration Verification | Verifies the success of migration by checking for broken links and missing files |
| `docs_duplicate_finder.py` | Duplicate Detection | Identifies duplicate files between old and new directories |
| `unique_files_analyzer.py` | Unique File Analysis | Analyzes files in old directories that were not migrated |
| `process_unique_files.py` | Unique File Processing | Processes unique files based on recommendations (migrate, archive, delete) |
| `cleanup_empty_directories.py` | Directory Cleanup | Removes empty directories after migration |

### 2. Migration Process

The migration process follows a systematic approach:

1. **Pre-Migration Analysis**
   - Analyze existing file structure
   - Identify target structure
   - Create migration plan
   - Back up critical files

2. **Migration Execution**
   - Move files to new locations
   - Update cross-references
   - Preserve metadata
   - Maintain file integrity

3. **Post-Migration Verification**
   - Verify all files were migrated correctly
   - Check for broken links
   - Identify any missing files
   - Ensure cross-references are updated

4. **Cleanup and Finalization**
   - Identify and process unique files
   - Remove duplicate files
   - Clean up empty directories
   - Document the migration process

## Usage Guidelines

### Preparing for Migration

Before starting a migration, follow these steps:

1. **Define Clear Objectives**
   - What is being migrated?
   - Where is it being migrated to?
   - What are the success criteria?

2. **Create a Migration Plan**
   - Map source and destination paths
   - Identify dependencies
   - Establish timeline
   - Define rollback procedures

3. **Prepare the Environment**
   - Back up critical files
   - Ensure sufficient disk space
   - Set up logging
   - Prepare verification tools

### Executing the Migration

To execute a migration using the framework:

1. **Run the Migration Script**

   ```bash
   python scripts/migrations/docs_structure_migrator.py --source-dir <source> --target-dir <target> --update-references
   ```

2. **Verify the Migration**

   ```bash
   python scripts/migrations/docs_migration_verification.py --target-dir <target>
   ```

3. **Find Duplicates**

   ```bash
   python scripts/migrations/docs_duplicate_finder.py --old-dir <old> --new-dir <new>
   ```

4. **Analyze Unique Files**

   ```bash
   python scripts/migrations/unique_files_analyzer.py --old-dir <old> --new-dir <new>
   ```

5. **Process Unique Files**

   ```bash
   python scripts/migrations/process_unique_files.py --action all
   ```

6. **Clean Up Empty Directories**

   ```bash
   python scripts/migrations/cleanup_empty_directories.py --target-dir <old>
   ```

### Post-Migration Tasks

After completing the migration:

1. **Update Documentation**
   - Update READMEs
   - Update roadmaps
   - Document the migration process

2. **Notify Stakeholders**
   - Inform team members of the changes
   - Provide guidance on new structure
   - Address any questions or concerns

3. **Monitor for Issues**
   - Watch for broken links
   - Address any reported problems
   - Make adjustments as needed

## Best Practices

### Batch Operations

For efficient file migration in the EGOS system, follow these proven practices:

1. **Preparation Phase**:
   - Create targeted backups of only the directories being modified
   - Use `Get-ChildItem` with specific exclusions (`-Exclude *venv*,*node_modules*,*.git*,*__pycache__*`)
   - Verify source file counts before migration

2. **Migration Phase**:
   - Create destination directories with `New-Item -Path $path -ItemType Directory -Force`
   - Move files in batches by directory type rather than individual files
   - Use `Copy-Item` with `-Recurse` and specific exclusions for directories
   - Verify destination file counts after copying

3. **Cleanup Phase**:
   - Remove source directories only after verifying successful migration
   - Update cross-references in batches using regex replacements
   - Remove empty parent directories

### Cross-Reference Handling

When updating cross-references during migration:

1. **Standardize Format**
   - Use consistent relative paths
   - Follow the established cross-reference format
   - Avoid duplicate metadata

2. **Batch Updates**
   - Update cross-references in batches
   - Use regex for pattern matching
   - Verify updates with sample checks

3. **Validation**
   - Test links after updating
   - Check for broken references
   - Ensure bidirectional links work

### File Exclusions

Always exclude the following directories from migration operations:

- `venv/` and `.venv/` (Python virtual environments)
- `node_modules/` (Node.js dependencies)
- `__pycache__/` (Python cache files)
- `.git/` (Git repository data)
- `.vs/` (Visual Studio files)
- `backup/` and `backups/` (Backup directories)

## Case Study: Documentation Migration

The Universal Migration Framework was developed based on the successful migration of the EGOS documentation structure. This case study provides insights into the process and lessons learned.

### Background

The EGOS documentation was originally scattered across multiple directories with inconsistent naming and organization. The goal was to consolidate and standardize the documentation structure to improve discoverability and maintainability.

### Migration Process

1. **Analysis**
   - Analyzed existing documentation structure
   - Identified inconsistencies and gaps
   - Developed standardized structure
   - Created migration plan

2. **Execution**
   - Developed migration scripts
   - Moved files to new structure
   - Updated cross-references
   - Verified migration success

3. **Cleanup**
   - Identified unique files
   - Processed files based on recommendations
   - Removed empty directories
   - Documented the process

### Results

- **Files Migrated**: 588 files moved to the new structure
- **Cross-References Updated**: 1273 cross-references successfully updated
- **Unique Files Analyzed**: 475 unique files identified in old directories
- **Duplicates Found**: 0 duplicates found, indicating a clean migration

### Lessons Learned

1. **Batch Operations**
   - Processing files in batches significantly improved efficiency
   - Grouping similar operations reduced tool calls and processing time

2. **Verification**
   - Thorough verification was critical to ensure migration success
   - Automated verification tools saved time and improved accuracy

3. **Documentation**
   - Documenting the process helped identify gaps and improvements
   - Creating a standardized framework enabled future migrations

## Extending the Framework

The Universal Migration Framework can be extended for various migration scenarios:

1. **Code Migration**
   - Moving code between subsystems
   - Refactoring code structure
   - Updating import statements

2. **Data Migration**
   - Moving data between storage systems
   - Updating data formats
   - Preserving data integrity

3. **Configuration Migration**
   - Moving configuration files
   - Updating configuration formats
   - Ensuring compatibility

## References

- [Documentation Structure Standard](mdc:project_documentation/standards/documentation_structure_standard.md)
- [KOIOS Roadmap](mdc:project_documentation/subsystems/KOIOS/KOS_roadmap.md)
- [Documentation Migration Case Study](mdc:project_documentation/governance/reorganization/DOCS_MIGRATION_CASE_STUDY.md)
- [Efficient File Migration Process](mdc:project_documentation/governance/migrations/efficient_file_migration.md)

---

**@references:**
- mdc:project_documentation/standards/documentation_structure_standard.md
- mdc:project_documentation/subsystems/KOIOS/KOS_roadmap.md
- mdc:project_documentation/governance/reorganization/DOCS_MIGRATION_CASE_STUDY.md
- mdc:project_documentation/governance/migrations/efficient_file_migration.md