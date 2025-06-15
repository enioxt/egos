# ------------------------------------------------------------------------------
# work_log_manager.ps1
# ------------------------------------------------------------------------------
# Description: PowerShell script to manage WORK log files according to EGOS standards
# Author: Cascade (AI Assistant)
# Date: 2025-05-23
# Version: 1.0
# References:
#   - C:\EGOS\WORK_2025-05-23_Work_Log_Standardization.md
#   - C:\EGOS\docs\templates\WORK_template.md
# ------------------------------------------------------------------------------

<#
.SYNOPSIS
    Manages WORK log files according to EGOS standards.

.DESCRIPTION
    This script provides utilities for creating, updating, and archiving WORK log files
    according to the standardized format defined in WORK_2025-05-23_Work_Log_Standardization.md.
    It supports creating new WORK files, checking for files that should be archived,
    and validating existing files against the standard.

.PARAMETER Action
    The action to perform: Create, Archive, Validate, or Status

.PARAMETER Title
    The title of the work (for Create action)

.PARAMETER RoadmapIds
    Comma-separated list of roadmap IDs (for Create action)

.PARAMETER Priority
    Priority level: Critical, High, Medium, or Low (for Create action)

.EXAMPLE
    .\work_log_manager.ps1 -Action Create -Title "Feature Implementation" -RoadmapIds "EGOS-EPIC-001" -Priority "High"
    Creates a new WORK log file with the specified parameters.

.EXAMPLE
    .\work_log_manager.ps1 -Action Archive
    Identifies completed WORK files older than 7 days and moves them to the archive.

.EXAMPLE
    .\work_log_manager.ps1 -Action Validate
    Validates all WORK files against the standard and reports non-compliant files.

.EXAMPLE
    .\work_log_manager.ps1 -Action Status
    Shows a summary of all WORK files by status.
#>

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("Create", "Archive", "Validate", "Status")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Title,
    
    [Parameter(Mandatory=$false)]
    [string]$RoadmapIds,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("Critical", "High", "Medium", "Low")]
    [string]$Priority = "Medium"
)

# Constants
$EGOS_ROOT = "C:\EGOS"
$ARCHIVE_DIR = "$EGOS_ROOT\archive\work_tracking_archive"
$TEMPLATE_PATH = "$EGOS_ROOT\docs\templates\WORK_template.md"
$STANDARD_DOC = "$EGOS_ROOT\WORK_2025-05-23_Work_Log_Standardization.md"

# Banner function for visual consistency
function Show-Banner {
    param (
        [string]$Title
    )
    
    $border = "=" * 80
    Write-Host $border -ForegroundColor Cyan
    Write-Host "EGOS WORK Log Manager - $Title" -ForegroundColor Cyan
    Write-Host $border -ForegroundColor Cyan
    Write-Host ""
}

# Function to create a new WORK log file
function New-WorkLog {
    param (
        [string]$Title,
        [string]$RoadmapIds,
        [string]$Priority
    )
    
    Show-Banner "Creating New WORK Log"
    
    # Validate parameters
    if ([string]::IsNullOrEmpty($Title)) {
        Write-Host "Error: Title is required for creating a new WORK log." -ForegroundColor Red
        return
    }
    
    # Format the date
    $date = Get-Date -Format "yyyy-MM-dd"
    
    # Format the title for the filename (PascalCase)
    $fileTitle = $Title -replace '\s+', '_'
    
    # Create the filename
    $fileName = "WORK_${date}_${fileTitle}.md"
    $filePath = "$EGOS_ROOT\$fileName"
    
    # Check if file already exists
    if (Test-Path $filePath) {
        Write-Host "Error: A WORK log with this name already exists: $fileName" -ForegroundColor Red
        return
    }
    
    # Read the template
    if (Test-Path $TEMPLATE_PATH) {
        $template = Get-Content $TEMPLATE_PATH -Raw
    } else {
        Write-Host "Error: Template file not found at $TEMPLATE_PATH" -ForegroundColor Red
        return
    }
    
    # Replace placeholders in the template
    $content = $template -replace "Title of the Work", $Title
    $content = $content -replace "YYYY-MM-DD", $date
    $content = $content -replace "Author Name \(Human or AI\)", $env:USERNAME
    $content = $content -replace "Current status", "In Progress"
    $content = $content -replace "Priority level", $Priority
    
    if (-not [string]::IsNullOrEmpty($RoadmapIds)) {
        $roadmapIdsArray = $RoadmapIds -split ',' | ForEach-Object { $_.Trim() }
        $roadmapIdsString = $roadmapIdsArray -join ', '
        $roadmapIdsYaml = '[' + ($roadmapIdsArray | ForEach-Object { '"' + $_ + '"' }) -join ', ' + ']'
        
        $content = $content -replace 'roadmap_ids: \["EGOS-EPIC-XXX", "EGOS-EPIC-XXX-YY"\]', "roadmap_ids: $roadmapIdsYaml"
        $content = $content -replace '\*\*Roadmap IDs:\*\* EGOS-EPIC-XXX, EGOS-EPIC-XXX-YY', "**Roadmap IDs:** $roadmapIdsString"
    }
    
    # Write the content to the file
    $content | Out-File -FilePath $filePath -Encoding utf8
    
    Write-Host "Successfully created new WORK log: $fileName" -ForegroundColor Green
    Write-Host "Location: $filePath" -ForegroundColor Green
}

# Function to archive completed WORK logs older than 7 days
function Archive-WorkLogs {
    Show-Banner "Archiving Completed WORK Logs"
    
    # Ensure archive directory exists
    if (-not (Test-Path $ARCHIVE_DIR)) {
        New-Item -Path $ARCHIVE_DIR -ItemType Directory -Force | Out-Null
        Write-Host "Created archive directory: $ARCHIVE_DIR" -ForegroundColor Yellow
    }
    
    $currentDate = Get-Date
    $archivedCount = 0
    
    # Get all WORK files in the root directory
    Get-ChildItem -Path "$EGOS_ROOT\WORK_*.md" -File | ForEach-Object {
        $filePath = $_.FullName
        $content = Get-Content $filePath -Raw
        
        # Check if the file is marked as completed
        if ($content -match 'status: "Completed"' -or $content -match '\*\*Status:\*\* Completed') {
            $fileDate = $_.LastWriteTime
            $daysSinceCompletion = ($currentDate - $fileDate).Days
            
            # If the file is older than 7 days, archive it
            if ($daysSinceCompletion -ge 7) {
                $destPath = "$ARCHIVE_DIR\$($_.Name)"
                Move-Item -Path $filePath -Destination $destPath -Force
                Write-Host "Archived: $($_.Name) (Completed $daysSinceCompletion days ago)" -ForegroundColor Green
                $archivedCount++
            } else {
                Write-Host "Skipped: $($_.Name) (Completed $daysSinceCompletion days ago, will be archived in $((7 - $daysSinceCompletion)) days)" -ForegroundColor Yellow
            }
        }
    }
    
    if ($archivedCount -eq 0) {
        Write-Host "No completed WORK logs found that are older than 7 days." -ForegroundColor Cyan
    } else {
        Write-Host "Successfully archived $archivedCount WORK logs." -ForegroundColor Green
    }
}

# Function to validate WORK logs against the standard
function Validate-WorkLogs {
    Show-Banner "Validating WORK Logs"
    
    $allFiles = @()
    $allFiles += Get-ChildItem -Path "$EGOS_ROOT\WORK_*.md" -File
    $allFiles += Get-ChildItem -Path "$ARCHIVE_DIR\WORK_*.md" -File -ErrorAction SilentlyContinue
    
    $validCount = 0
    $invalidCount = 0
    
    foreach ($file in $allFiles) {
        $issues = @()
        $content = Get-Content $file.FullName -Raw
        
        # Check filename format
        if (-not ($file.Name -match 'WORK_\d{4}-\d{2}-\d{2}_.*\.md')) {
            $issues += "Filename does not follow the standard format (WORK_YYYY-MM-DD_Description.md)"
        }
        
        # Check for YAML frontmatter
        if (-not ($content -match '---\s*\n.*\n---')) {
            $issues += "Missing YAML frontmatter"
        }
        
        # Check for required sections
        $requiredSections = @(
            "# .+", # Title
            "## 1\. Objective",
            "## 2\. Context",
            "## .+Tasks",
            "## .+Next Steps",
            "## .+References"
        )
        
        foreach ($section in $requiredSections) {
            if (-not ($content -match $section)) {
                $issues += "Missing required section: $section"
            }
        }
        
        # Check for EGOS signature
        if (-not ($content -match '✧༺❀༻∞ EGOS ∞༺❀༻✧')) {
            $issues += "Missing EGOS signature"
        }
        
        # Report results
        if ($issues.Count -eq 0) {
            Write-Host "✅ Valid: $($file.Name)" -ForegroundColor Green
            $validCount++
        } else {
            Write-Host "❌ Invalid: $($file.Name)" -ForegroundColor Red
            foreach ($issue in $issues) {
                Write-Host "   - $issue" -ForegroundColor Red
            }
            $invalidCount++
        }
    }
    
    Write-Host ""
    Write-Host "Validation Summary:" -ForegroundColor Cyan
    Write-Host "- Total WORK logs: $($allFiles.Count)" -ForegroundColor Cyan
    Write-Host "- Valid: $validCount" -ForegroundColor Green
    Write-Host "- Invalid: $invalidCount" -ForegroundColor ($invalidCount -gt 0 ? "Red" : "Green")
}

# Function to show status of all WORK logs
function Show-WorkLogStatus {
    Show-Banner "WORK Log Status"
    
    $allFiles = @()
    $allFiles += Get-ChildItem -Path "$EGOS_ROOT\WORK_*.md" -File
    $allFiles += Get-ChildItem -Path "$ARCHIVE_DIR\WORK_*.md" -File -ErrorAction SilentlyContinue
    
    $statusCounts = @{
        "In Progress" = 0
        "Completed" = 0
        "Blocked" = 0
        "Planning" = 0
        "Unknown" = 0
    }
    
    $priorityCounts = @{
        "Critical" = 0
        "High" = 0
        "Medium" = 0
        "Low" = 0
        "Unknown" = 0
    }
    
    $recentFiles = @()
    $currentDate = Get-Date
    
    foreach ($file in $allFiles) {
        $content = Get-Content $file.FullName -Raw
        $status = "Unknown"
        $priority = "Unknown"
        
        # Extract status
        if ($content -match 'status: "([^"]+)"') {
            $status = $matches[1]
        } elseif ($content -match '\*\*Status:\*\* ([^\r\n]+)') {
            $status = $matches[1]
        }
        
        # Extract priority
        if ($content -match 'priority: "([^"]+)"') {
            $priority = $matches[1]
        } elseif ($content -match '\*\*Priority:\*\* ([^\r\n]+)') {
            $priority = $matches[1]
        }
        
        # Update counts
        if ($statusCounts.ContainsKey($status)) {
            $statusCounts[$status]++
        } else {
            $statusCounts["Unknown"]++
        }
        
        if ($priorityCounts.ContainsKey($priority)) {
            $priorityCounts[$priority]++
        } else {
            $priorityCounts["Unknown"]++
        }
        
        # Check if file was modified in the last 7 days
        $daysSinceModification = ($currentDate - $file.LastWriteTime).Days
        if ($daysSinceModification -le 7) {
            $recentFiles += @{
                Name = $file.Name
                Status = $status
                Priority = $priority
                DaysAgo = $daysSinceModification
            }
        }
    }
    
    # Display status summary
    Write-Host "Status Summary:" -ForegroundColor Cyan
    Write-Host "- In Progress: $($statusCounts["In Progress"])" -ForegroundColor Yellow
    Write-Host "- Completed: $($statusCounts["Completed"])" -ForegroundColor Green
    Write-Host "- Blocked: $($statusCounts["Blocked"])" -ForegroundColor Red
    Write-Host "- Planning: $($statusCounts["Planning"])" -ForegroundColor Blue
    Write-Host "- Unknown: $($statusCounts["Unknown"])" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Priority Summary:" -ForegroundColor Cyan
    Write-Host "- Critical: $($priorityCounts["Critical"])" -ForegroundColor Red
    Write-Host "- High: $($priorityCounts["High"])" -ForegroundColor Yellow
    Write-Host "- Medium: $($priorityCounts["Medium"])" -ForegroundColor Green
    Write-Host "- Low: $($priorityCounts["Low"])" -ForegroundColor Blue
    Write-Host "- Unknown: $($priorityCounts["Unknown"])" -ForegroundColor Gray
    Write-Host ""
    
    # Display recent files
    Write-Host "Recently Modified WORK Logs (Last 7 Days):" -ForegroundColor Cyan
    if ($recentFiles.Count -eq 0) {
        Write-Host "No WORK logs have been modified in the last 7 days." -ForegroundColor Yellow
    } else {
        $recentFiles | Sort-Object -Property DaysAgo | ForEach-Object {
            $statusColor = switch ($_.Status) {
                "In Progress" { "Yellow" }
                "Completed" { "Green" }
                "Blocked" { "Red" }
                "Planning" { "Blue" }
                default { "Gray" }
            }
            
            Write-Host "$($_.Name) - $($_.Status) ($($_.Priority)) - Modified $($_.DaysAgo) days ago" -ForegroundColor $statusColor
        }
    }
}

# Main execution
try {
    switch ($Action) {
        "Create" {
            New-WorkLog -Title $Title -RoadmapIds $RoadmapIds -Priority $Priority
        }
        "Archive" {
            Archive-WorkLogs
        }
        "Validate" {
            Validate-WorkLogs
        }
        "Status" {
            Show-WorkLogStatus
        }
    }
    
    # Display EGOS signature
    Write-Host ""
    Write-Host "✧༺❀༻∞ EGOS ∞༺❀༻✧" -ForegroundColor Magenta
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
}
