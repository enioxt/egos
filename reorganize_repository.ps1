# EGOS Repository Reorganization Script
# Created: 2025-06-03
# Purpose: Safely reorganize the EGOS repository structure before GitHub commit
# This script implements structural improvements while preserving all important content

# Script Configuration
$backupRoot = "C:\EGOS_BACKUPS_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$repoRoot = "C:\EGOS"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "EGOS REPOSITORY REORGANIZATION SCRIPT" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will reorganize the EGOS repository structure" -ForegroundColor Yellow
Write-Host "A backup will be created at: $backupRoot" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Enter to continue or Ctrl+C to cancel..." -ForegroundColor Red
$null = Read-Host

# STEP 1: Create a backup of the entire repository
Write-Host "[STEP 1] Creating full backup of the repository..." -ForegroundColor Green

# Create backup directory
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
Write-Host "  - Created backup directory at: $backupRoot" -ForegroundColor Gray

# Copy all files (excluding very large directories like node_modules)
Write-Host "  - Copying repository files to backup location..." -ForegroundColor Gray
robocopy $repoRoot $backupRoot /E /XD "$repoRoot\node_modules" "$repoRoot\.venv" "$repoRoot\website\node_modules" "$repoRoot\website\.next" /NP /NFL /NDL

Write-Host "  - Backup completed successfully!" -ForegroundColor Green
Write-Host ""

# STEP 2: Clean up temporary and backup files
Write-Host "[STEP 2] Moving backup and temporary files to a separate location..." -ForegroundColor Green

# Create a directory for backups inside the backup root
$localBackupDir = Join-Path -Path $backupRoot -ChildPath "local_backups"
New-Item -ItemType Directory -Path $localBackupDir -Force | Out-Null

# Find and move backup files
$backupFiles = Get-ChildItem -Path $repoRoot -Recurse -File -Include "*_backup_*", "*.bak", "*_old.*", "*.tmp", "*.temp", "*_archive_*"

if ($backupFiles.Count -gt 0) {
    foreach ($file in $backupFiles) {
        $relativePath = $file.FullName.Substring($repoRoot.Length)
        $targetPath = Join-Path -Path $localBackupDir -ChildPath $relativePath
        $targetDir = Split-Path -Parent $targetPath
        
        # Create the directory structure if it doesn't exist
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        # Move the file
        Move-Item -Path $file.FullName -Destination $targetPath
        Write-Host "  - Moved backup file: $relativePath" -ForegroundColor Gray
    }
    
    Write-Host "  - Total backup files moved: $($backupFiles.Count)" -ForegroundColor Yellow
} else {
    Write-Host "  - No backup files found to move" -ForegroundColor Yellow
}

Write-Host "  - Backup file cleanup completed!" -ForegroundColor Green
Write-Host ""

# STEP 3: Standardize documentation structure
Write-Host "[STEP 3] Improving documentation structure..." -ForegroundColor Green

# Create the new documentation structure
$docDirs = @(
    "docs/core",
    "docs/systems",
    "docs/guides",
    "docs/processes",
    "docs/standards",
    "docs/research"
)

foreach ($dir in $docDirs) {
    $fullPath = Join-Path -Path $repoRoot -ChildPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  - Created directory: $dir" -ForegroundColor Gray
    }
}

# Create index.md files in each major documentation directory
$indexContent = @"
# EGOS Documentation Index

This directory contains the following sections:

- [Core Documentation](./core/): Core concepts and architectural documentation
- [Systems Documentation](./systems/): All subsystems documentation
- [Guides](./guides/): Usage and development guides
- [Processes](./processes/): Process documentation
- [Standards](./standards/): Project standards and conventions
- [Research](./research/): Research materials and findings

Last updated: $(Get-Date -Format 'yyyy-MM-dd')
"@

$indexPath = Join-Path -Path $repoRoot -ChildPath "docs/index.md"
Set-Content -Path $indexPath -Value $indexContent
Write-Host "  - Created main documentation index file" -ForegroundColor Gray

# Move some key documentation files to appropriate directories
$docMappings = @{
    "docs/ARCHITECTURE.MD" = "docs/core/ARCHITECTURE.md";
    "docs/system_health_check_framework.md" = "docs/systems/health_check_framework.md";
    "docs/caching_best_practices.md" = "docs/standards/caching_best_practices.md";
}

foreach ($source in $docMappings.Keys) {
    $sourcePath = Join-Path -Path $repoRoot -ChildPath $source
    $targetPath = Join-Path -Path $repoRoot -ChildPath $docMappings[$source]
    $targetDir = Split-Path -Parent $targetPath
    
    if (Test-Path $sourcePath) {
        # Ensure target directory exists
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        # Copy the file (not move to be safer)
        Copy-Item -Path $sourcePath -Destination $targetPath
        Write-Host "  - Copied: $source -> $($docMappings[$source])" -ForegroundColor Gray
    }
}

Write-Host "  - Documentation structure improvements completed!" -ForegroundColor Green
Write-Host ""

# STEP 4: Website structure improvements
Write-Host "[STEP 4] Improving website structure..." -ForegroundColor Green

# Remove shortcut files
$shortcuts = Get-ChildItem -Path "$repoRoot\website" -Filter "*.lnk" -File -Recurse
foreach ($shortcut in $shortcuts) {
    Remove-Item -Path $shortcut.FullName
    Write-Host "  - Removed shortcut file: $($shortcut.FullName.Substring($repoRoot.Length + 1))" -ForegroundColor Gray
}

# Create a design directory for design documentation
$websiteDesignDir = Join-Path -Path $repoRoot -ChildPath "website/docs/design"
if (-not (Test-Path $websiteDesignDir)) {
    New-Item -ItemType Directory -Path $websiteDesignDir -Force | Out-Null
    Write-Host "  - Created website design documentation directory" -ForegroundColor Gray
}

# Move design documents to the design directory
$designDocs = Get-ChildItem -Path "$repoRoot\website" -Filter "*DESIGN*.md" -File
foreach ($doc in $designDocs) {
    $targetPath = Join-Path -Path $websiteDesignDir -ChildPath $doc.Name
    Copy-Item -Path $doc.FullName -Destination $targetPath
    Write-Host "  - Copied design doc to organized location: $($doc.Name)" -ForegroundColor Gray
}

Write-Host "  - Website structure improvements completed!" -ForegroundColor Green
Write-Host ""

# STEP 5: Enhance .gitignore file
Write-Host "[STEP 5] Enhancing .gitignore file..." -ForegroundColor Green

$gitignorePath = Join-Path -Path $repoRoot -ChildPath ".gitignore"
$additionalGitignorePatterns = @"

# Additional ignore patterns (added by reorganization script)
# Development environments
.cursor/local/
.history/

# Local test data
**/test_data/local/

# Temporary files generated during builds
.temp/
.tmp/
**/tmp/

# IDE specific settings that shouldn't be shared
**/.vscode/settings.json

# Website build artifacts
website/.next/
website/node_modules/

# Backup files
**/*_backup_*.*
**/*.bak
**/*_old.*

# End of additional patterns
"@

Add-Content -Path $gitignorePath -Value $additionalGitignorePatterns
Write-Host "  - Enhanced .gitignore file with additional patterns" -ForegroundColor Green
Write-Host ""

# STEP 6: Create organization guide
Write-Host "[STEP 6] Creating repository organization guide..." -ForegroundColor Green

$orgGuideContent = @"
# EGOS Repository Organization Guide

## Repository Structure

This repository follows a consistent organization structure to maintain the EGOS project effectively.

### Key Directories

- **/.windsurf/**: Windsurf workflows and configuration
- **/ATRIAN/**: The ATRiAN module - Ethics as a Service
- **/EGOS_Framework/**: Core EGOS framework and MCP files
- **/apps/**: EGOS applications and services
- **/config/**: Configuration files (excluding secrets)
- **/docs/**: Documentation organized by topic
  - **/core/**: Core concepts and architecture
  - **/systems/**: All subsystems documentation
  - **/guides/**: Usage and development guides
  - **/processes/**: Process documentation
  - **/standards/**: Project standards
  - **/research/**: Research materials
- **/scripts/**: Utility scripts and tools
- **/website/**: EGOS website source code

### File Types and Locations

- **Markdown Documentation**: Use `.md` files for all documentation
- **Python Code**: Follow PEP 8 style guidelines
- **Configuration**: Use YAML for configuration files when possible
- **Scripts**: Include usage comments at the top of each script

### Excluded Items

The following should never be committed to the repository:

- Secrets, API keys, or credentials
- Node modules and other large dependency directories
- Temporary or backup files
- Large binary assets (use external storage instead)

## Organization Guidelines

1. **Keep Related Items Together**: Group related files in the same directory
2. **Use Clear Naming**: File names should indicate content and purpose
3. **Minimize Duplication**: Avoid duplicating content across multiple locations
4. **Reference Don't Copy**: Link to existing content rather than duplicating it
5. **Document Structure**: Keep documentation structure parallel to code structure

Last updated: $(Get-Date -Format 'yyyy-MM-dd')
"@

$orgGuidePath = Join-Path -Path $repoRoot -ChildPath "REPOSITORY_ORGANIZATION.md"
Set-Content -Path $orgGuidePath -Value $orgGuideContent
Write-Host "  - Created repository organization guide" -ForegroundColor Green
Write-Host ""

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "REPOSITORY REORGANIZATION COMPLETED!" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "A complete backup has been saved at:" -ForegroundColor Yellow
Write-Host "  $backupRoot" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Magenta
Write-Host "1. Review the changes made by this script" -ForegroundColor White
Write-Host "2. Further organize specific content areas as needed" -ForegroundColor White
Write-Host "3. Initialize Git repository and make initial commit" -ForegroundColor White
Write-Host "4. Push to GitHub" -ForegroundColor White
Write-Host ""
Write-Host "For a summary of the repository organization," -ForegroundColor White
Write-Host "see the newly created file: REPOSITORY_ORGANIZATION.md" -ForegroundColor White
Write-Host ""
