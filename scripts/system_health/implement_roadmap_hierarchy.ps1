# EGOS Roadmap Hierarchy Implementation
# Author: EGOS Development Team
# Date: 2025-05-18
# Description: Implements the complete roadmap hierarchy system by updating existing files
#              and creating standardized local roadmaps for all key directories

# Configuration
$baseDir = "C:\EGOS"
$currentDate = Get-Date -Format "yyyy-MM-dd"
$reportsDir = Join-Path -Path $baseDir -ChildPath "reports\roadmap"

# Ensure reports directory exists
if (-not (Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null
    Write-Host "Created reports directory: $reportsDir"
}

# Start transcript for logging
$logDir = Join-Path -Path $baseDir -ChildPath "logs\roadmap"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
$logFile = Join-Path -Path $logDir -ChildPath "roadmap_hierarchy_implementation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Start-Transcript -Path $logFile

Write-Host "=== EGOS Roadmap Hierarchy Implementation ==="
Write-Host "Starting implementation at $(Get-Date)"

#region Update Existing Files with Cross-References

Write-Host "`n=== Updating Existing Files with Cross-References ==="

$existingFiles = @{
    "docs\governance\roadmap_hierarchy.md" = @{
        CrossRefs = @"
## Cross References

- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->

"@
    }
    "docs\governance\roadmap_standardization.md" = @{
        CrossRefs = @"
## Cross References

- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->

"@
    }
    "docs\templates\roadmap_template.md" = @{
        CrossRefs = @"
## Cross References

- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->

"@
    }
    "docs\templates\main_roadmap_template.md" = @{
        CrossRefs = @"
## Cross References

- [Development Standards](docs/governance/development_standards.md)
- [Roadmap Hierarchy](docs/governance/roadmap_hierarchy.md)
- [Roadmap Standardization](docs/governance/roadmap_standardization.md)
- [Roadmap Template](docs/templates/roadmap_template.md)

"@
    }
    "docs\reference\roadmap_hierarchy_implementation.md" = @{
        CrossRefs = @"
## Cross References

- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->

"@
    }
    "docs\audits\index.md" = @{
        CrossRefs = @"
## Cross References

- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->
- <!-- TO_BE_REPLACED -->

"@
    }
}

foreach ($filePath in $existingFiles.Keys) {
    $fullPath = Join-Path -Path $baseDir -ChildPath $filePath
    if (Test-Path $fullPath) {
        Write-Host "Processing $filePath..."
        
        # Read file content
        $content = Get-Content -Path $fullPath -Raw
        
        # Check if file already has cross-references
        if ($content -match "## Cross References") {
            Write-Host "  File already has cross-references. Skipping."
            continue
        }
        
        # Extract metadata section
        $metadataMatch = [regex]::Match($content, "(?s)^---\n(.*?)\n---\n")
        if (-not $metadataMatch.Success) {
            Write-Host "  No metadata section found. Skipping."
            continue
        }
        
        $metadata = $metadataMatch.Value
        $bodyContent = $content.Substring($metadataMatch.Length)
        
        # Insert cross-references after metadata
        $newContent = $metadata + $existingFiles[$filePath].CrossRefs + $bodyContent
        
        # Write updated content back to file
        Set-Content -Path $fullPath -Value $newContent -Encoding UTF8
        
        Write-Host "  Added cross-references to $filePath"
    }
    else {
        Write-Host "  File not found: $filePath"
    }
}

#endregion

#region Create Local Roadmaps

Write-Host "`n=== Creating Local Roadmaps ==="

# Define directories that need roadmaps
$directories = @(
    "docs",
    "scripts",
    "subsystems",
    "subsystems\KOIOS",
    "subsystems\ATLAS",
    "subsystems\MYCELIUM",
    "subsystems\NEXUS",
    "subsystems\CORUJA"
)

foreach ($dir in $directories) {
    $dirPath = Join-Path -Path $baseDir -ChildPath $dir
    $roadmapPath = Join-Path -Path $dirPath -ChildPath "roadmap.md"
    
    Write-Host "Processing $dir..."
    
    # Skip if directory doesn't exist
    if (-not (Test-Path $dirPath)) {
        Write-Host "  Directory doesn't exist: $dirPath. Skipping."
        continue
    }
    
    # Skip if roadmap already exists
    if (Test-Path $roadmapPath) {
        Write-Host "  Roadmap already exists at $roadmapPath. Skipping."
        continue
    }
    
    # Extract directory name for title
    $dirName = Split-Path -Path $dirPath -Leaf
    
    Write-Host "  Creating roadmap for $dirName..."
    
    # Calculate relative path to root
    $depth = ($dir.Split('\').Count)
    $rootPath = "../" * $depth
    
    # Create roadmap file with proper metadata and cross-references
    $roadmapContent = @"
---
title: $dirName Roadmap
version: 1.0.0
status: Active
date_created: $currentDate
date_modified: $currentDate
authors: [EGOS Development Team]
description: Development roadmap for $dirName
file_type: documentation
scope: directory-specific
primary_entity_type: roadmap
primary_entity_name: $($dirName.ToLower())_roadmap
tags: [documentation, roadmap, planning, $($dirName.ToLower())]
---

## Cross References

- [EGOS ROADMAP]($($rootPath)ROADMAP.md)
- [Roadmap Hierarchy]($($rootPath)docs/governance/roadmap_hierarchy.md)
- [Roadmap Standardization]($($rootPath)docs/governance/roadmap_standardization.md)
- [Development Standards]($($rootPath)docs/governance/development_standards.md)

# $dirName Roadmap

## Overview

[Brief description of this directory/subsystem and its purpose within EGOS]

## Status Legend

| Status | Description |
|--------|-------------|
| 🔄 Backlog | Planned but not started |
| ⏳ In Progress | Work has begun |
| 🔍 Review | Ready for review |
| ✅ Done | Complete |
| 🔜 Deferred | Postponed |
| ⛔ Blocked | Cannot proceed due to dependency |

## Current Priorities

[Brief summary of current focus areas and priorities]

## Tasks

### [EGOS-EPIC-XXX-YY] Task Title

**Parent Epic:** [EGOS-EPIC-XXX]($($rootPath)ROADMAP.md#egos-epic-xxx-epic-title)  
**Status:** 🔄 Backlog  
**Priority:** [High/Medium/Low]  
**Owner:** [Team/Individual]  
**Estimated Effort:** [Hours or Story Points]  

**Description:**  
[Detailed description of the task]

**Tasks:**
- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

**References:**
- [Related Document 1](path/to/document1.md)
- [Related Document 2](path/to/document2.md)

**Acceptance Criteria:**
1. Criterion 1
2. Criterion 2
3. Criterion 3

## Completed Tasks

### [EGOS-EPIC-XXX-YY] Completed Task Title

**Parent Epic:** [EGOS-EPIC-XXX]($($rootPath)ROADMAP.md#egos-epic-xxx-epic-title)  
**Status:** ✅ Done  
**Completion Date:** YYYY-MM-DD  

**Description:**  
[Brief description of the completed task]

**Key Achievements:**
- Achievement 1
- Achievement 2
- Achievement 3

## Dependencies

| Task ID | Depends On | Status |
|---------|------------|--------|
| EGOS-EPIC-XXX-YY | EGOS-EPIC-ZZZ-WW | [Status] |
| EGOS-EPIC-XXX-YY | External Dependency | [Status] |
"@

    # Write the roadmap file
    Set-Content -Path $roadmapPath -Value $roadmapContent -Encoding UTF8
    
    Write-Host "  Created roadmap at $roadmapPath"
}

#endregion

#region Update Main Roadmap with Hierarchy References

Write-Host "`n=== Updating Main ROADMAP.md with Hierarchy References ==="

$mainRoadmapPath = Join-Path -Path $baseDir -ChildPath "ROADMAP.md"
if (Test-Path $mainRoadmapPath) {
    Write-Host "Processing main ROADMAP.md..."
    
    # Read file content
    $content = Get-Content -Path $mainRoadmapPath -Raw
    
    # Check if roadmap already has hierarchy section
    if ($content -match "## Roadmap Hierarchy") {
        Write-Host "  Main roadmap already has hierarchy section. Skipping."
    }
    else {
        # Find a good place to insert the hierarchy section
        $insertPosition = $content.LastIndexOf("<!-- KOIOS-AUTO-GEN:MAIN_CONTENT:END -->")
        if ($insertPosition -eq -1) {
            $insertPosition = $content.Length
        }
        
        $hierarchySection = @"

## Roadmap Hierarchy

This main roadmap contains high-level epics that are broken down into specific tasks in local roadmaps. For detailed implementation tasks, refer to the corresponding local roadmap files:

- [Scripts Roadmap](scripts/roadmap.md)
- [Documentation Roadmap](docs/roadmap.md)
- [Subsystems Roadmap](subsystems/roadmap.md)
  - [KOIOS Roadmap](subsystems/KOIOS/roadmap.md)
  - [ATLAS Roadmap](subsystems/ATLAS/roadmap.md)
  - [MYCELIUM Roadmap](subsystems/MYCELIUM/roadmap.md)
  - [NEXUS Roadmap](subsystems/NEXUS/roadmap.md)
  - [CORUJA Roadmap](subsystems/CORUJA/roadmap.md)

### Status Synchronization

Epic statuses in this main roadmap are synchronized with their child tasks in local roadmaps according to the following rules:

1. An epic is marked "Done" only when all its child tasks are complete
2. An epic is "Blocked" if any critical child task is blocked
3. An epic is "In Progress" when at least one child task is in progress

For more details on roadmap hierarchy and status synchronization, see [Roadmap Hierarchy Guidelines](docs/governance/roadmap_hierarchy.md).

"@
        
        # Insert hierarchy section
        $newContent = $content.Insert($insertPosition, $hierarchySection)
        
        # Write updated content back to file
        Set-Content -Path $mainRoadmapPath -Value $newContent -Encoding UTF8
        
        Write-Host "  Added hierarchy section to main ROADMAP.md"
    }
}
else {
    Write-Host "  Main ROADMAP.md not found. Skipping."
}

#endregion

#region Generate Implementation Report

Write-Host "`n=== Generating Implementation Report ==="

$reportPath = Join-Path -Path $reportsDir -ChildPath "roadmap_hierarchy_implementation_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"

$reportContent = @"
# EGOS Roadmap Hierarchy Implementation Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Summary

The roadmap hierarchy system has been implemented across the EGOS ecosystem, establishing clear parent-child relationships between the main roadmap and local roadmaps.

## Implementation Details

### Updated Files

The following existing files have been updated with proper cross-references:

$(foreach ($filePath in $existingFiles.Keys) {
    $fullPath = Join-Path -Path $baseDir -ChildPath $filePath
    if (Test-Path $fullPath) {
        "- [$filePath]($filePath)"
    }
})

### Created Roadmaps

The following local roadmaps have been created:

$(foreach ($dir in $directories) {
    $roadmapPath = Join-Path -Path $dir -ChildPath "roadmap.md"
    $fullPath = Join-Path -Path $baseDir -ChildPath $roadmapPath
    if (Test-Path $fullPath) {
        "- [$roadmapPath]($roadmapPath)"
    }
})

### Main Roadmap

The main ROADMAP.md has been updated with a hierarchy section that links to all local roadmaps and explains the status synchronization rules.

## Next Steps

1. **Customize Local Roadmaps**:
   - Update each local roadmap with actual tasks and priorities
   - Ensure proper parent-child relationships with the main roadmap

2. **Run Synchronization Tool**:
   ```powershell
   cd $baseDir
   python scripts\maintenance\roadmap_sync.py --base-path "$baseDir" --report-file reports/roadmap/initial_sync_report
   ```

3. **Schedule Weekly Verification**:
   ```powershell
   cd $baseDir\scripts\maintenance\automation
   .\setup_roadmap_sync.ps1
   ```

## Related Documents

- [Roadmap Hierarchy Guidelines](docs/governance/roadmap_hierarchy.md)
- [Roadmap Standardization Guidelines](docs/governance/roadmap_standardization.md)
- [Roadmap Hierarchy Implementation Guide](docs/reference/roadmap_hierarchy_implementation.md)
- [Audit Dashboard](docs/audits/index.md)
"@

# Write the report file
Set-Content -Path $reportPath -Value $reportContent -Encoding UTF8

Write-Host "  Generated implementation report at $reportPath"

#endregion

Write-Host "`n=== Implementation Completed ==="
Write-Host "Roadmap hierarchy system has been successfully implemented."
Write-Host "Implementation report saved to: $reportPath"
Write-Host "Log file saved to: $logFile"

Stop-Transcript

Write-Host "`nNext steps:"
Write-Host "1. Review and customize each local roadmap for its specific directory"
Write-Host "2. Run the roadmap synchronization tool to verify proper hierarchy:"
Write-Host "   python scripts\maintenance\roadmap_sync.py --base-path `"$baseDir`" --report-file reports/roadmap/initial_sync_report"
Write-Host "3. Set up weekly verification:"
Write-Host "   .\scripts\maintenance\automation\setup_roadmap_sync.ps1"