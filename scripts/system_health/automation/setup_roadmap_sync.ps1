# EGOS Roadmap Synchronization Automation Setup
# Author: EGOS Development Team
# Date: 2025-05-18
# Description: Sets up automated roadmap synchronization and standardization tasks

<#
.SYNOPSIS
    Sets up automated roadmap synchronization and standardization tasks for EGOS.

.DESCRIPTION
    This script configures Windows Task Scheduler to run roadmap synchronization
    and standardization tasks on a regular schedule. It ensures that main and local
    roadmaps remain aligned according to the hierarchy guidelines.

.PARAMETER BaseDir
    The base directory of the EGOS project.

.PARAMETER ScheduleTime
    The time to schedule the task (default: 3:00 AM).

.PARAMETER DayOfWeek
    The day of the week to run the task (default: Monday).

.PARAMETER ReportDir
    The directory to store reports (default: reports/roadmap).

.EXAMPLE
    .\setup_roadmap_sync.ps1 -BaseDir "C:\EGOS" -ScheduleTime "03:00" -DayOfWeek "Monday"
#>

param (
    [string]$BaseDir = (Get-Location).Path,
    [string]$ScheduleTime = "03:00",
    [string]$DayOfWeek = "Monday",
    [string]$ReportDir = "reports/roadmap"
)

# Ensure we're running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Error "This script must be run as Administrator. Please restart PowerShell as Administrator and try again."
    exit 1
}

# Validate base directory
if (-not (Test-Path $BaseDir)) {
    Write-Error "Base directory '$BaseDir' does not exist."
    exit 1
}

# Create report directory if it doesn't exist
$reportPath = Join-Path -Path $BaseDir -ChildPath $ReportDir
if (-not (Test-Path $reportPath)) {
    New-Item -ItemType Directory -Path $reportPath -Force | Out-Null
    Write-Host "Created report directory: $reportPath"
}

# Create the wrapper script that will be executed by the scheduler
$wrapperScriptPath = Join-Path -Path $BaseDir -ChildPath "scripts\maintenance\automation\run_roadmap_sync.ps1"

$wrapperScriptContent = @"
# EGOS Roadmap Synchronization Runner
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# This script is automatically generated - do not edit manually

# Set working directory to EGOS root
Set-Location "$BaseDir"

# Import common functions
. "$BaseDir\scripts\maintenance\automation\common_functions.ps1"

# Log file setup
`$logDir = "$BaseDir\logs\roadmap"
if (-not (Test-Path `$logDir)) {
    New-Item -ItemType Directory -Path `$logDir -Force | Out-Null
}
`$logFile = Join-Path -Path `$logDir -ChildPath "roadmap_sync_`$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Start-Transcript -Path `$logFile

try {
    # Create timestamp for report files
    `$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    `$reportBasePath = Join-Path -Path "$reportPath" -ChildPath "sync_report_`$timestamp"
    
    # Activate Python environment
    Write-Host "Activating Python environment..."
    `$envPath = "$BaseDir\venv\Scripts\Activate.ps1"
    if (Test-Path `$envPath) {
        . `$envPath
    } else {
        Write-Warning "Python environment not found at `$envPath. Using system Python."
    }
    
    # Run roadmap synchronization
    Write-Host "Running roadmap synchronization..."
    python "$BaseDir\scripts\maintenance\roadmap_sync.py" --base-path "$BaseDir" --report-file `$reportBasePath
    
    # Check for inconsistencies
    `$jsonReport = Get-Content "`$reportBasePath.json" | ConvertFrom-Json
    `$inconsistencyCount = `$jsonReport.inconsistencies.Count
    
    if (`$inconsistencyCount -gt 0) {
        Write-Host "Found `$inconsistencyCount inconsistencies between main and local roadmaps."
        
        # Create notification for inconsistencies
        `$notificationFile = Join-Path -Path "$BaseDir" -ChildPath "ROADMAP_SYNC_NEEDED.md"
        @"
# Roadmap Synchronization Needed

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

The automated roadmap synchronization process has detected **`$inconsistencyCount** inconsistencies between the main roadmap and local roadmaps.

## Details

Please review the full report at:
- [`$reportBasePath.md](`$reportBasePath.md)

## Quick Actions

1. **Review Inconsistencies:**
   - Check the status of epics in the main roadmap against their child tasks
   - Update statuses to reflect the current state of work

2. **Run Manual Sync:**
   \`\`\`powershell
   cd $BaseDir
   python scripts\maintenance\roadmap_sync.py --base-path "$BaseDir" --update --report-file reports/roadmap/manual_sync_report
   \`\`\`

3. **Verify Hierarchy:**
   - Ensure all local roadmap tasks link to their parent epics
   - Check that parent-child relationships are correctly defined

## Next Steps

After addressing these inconsistencies, delete this file to acknowledge completion.
"@ | Out-File -FilePath `$notificationFile -Encoding utf8
        
        Write-Host "Created notification file: `$notificationFile"
    } else {
        Write-Host "No inconsistencies found. Roadmaps are properly synchronized."
        
        # Remove notification file if it exists
        `$notificationFile = Join-Path -Path "$BaseDir" -ChildPath "ROADMAP_SYNC_NEEDED.md"
        if (Test-Path `$notificationFile) {
            Remove-Item -Path `$notificationFile
            Write-Host "Removed previous notification file."
        }
    }
    
    # Generate standardization report
    Write-Host "Checking roadmap standardization..."
    `$standardizationReport = Join-Path -Path "$reportPath" -ChildPath "standardization_report_`$timestamp"
    
    # Find all roadmap files
    `$roadmapFiles = Get-ChildItem -Path "$BaseDir" -Recurse -Filter "roadmap.md" -File
    
    # Check each roadmap file for compliance with standards
    `$compliantFiles = 0
    `$nonCompliantFiles = @()
    `$missingRoadmaps = @()
    
    foreach (`$file in `$roadmapFiles) {
        `$content = Get-Content -Path `$file.FullName -Raw
        
        # Check for required sections
        `$hasMetadata = `$content -match "---\s*\n.*\n.*\n.*\n.*\n---"
        `$hasStatusLegend = `$content -match "## Status Legend"
        `$hasTasks = `$content -match "## Tasks"
        
        if (`$hasMetadata -and `$hasStatusLegend -and `$hasTasks) {
            `$compliantFiles++
        } else {
            `$nonCompliantFiles += @{
                Path = `$file.FullName.Replace("$BaseDir\", "")
                MissingMetadata = -not `$hasMetadata
                MissingStatusLegend = -not `$hasStatusLegend
                MissingTasks = -not `$hasTasks
            }
        }
    }
    
    # Check for missing roadmaps in key directories
    `$keyDirectories = @(
        "$BaseDir\docs",
        "$BaseDir\scripts",
        "$BaseDir\subsystems"
    )
    
    foreach (`$dir in `$keyDirectories) {
        if (Test-Path `$dir) {
            `$roadmapPath = Join-Path -Path `$dir -ChildPath "roadmap.md"
            if (-not (Test-Path `$roadmapPath)) {
                `$missingRoadmaps += `$dir.Replace("$BaseDir\", "")
            }
        }
    }
    
    # Generate standardization report
    `$reportContent = @"
# EGOS Roadmap Standardization Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Summary

- Total Roadmap Files: $(`$roadmapFiles.Count)
- Compliant Files: `$compliantFiles
- Non-Compliant Files: $(`$nonCompliantFiles.Count)
- Missing Roadmaps in Key Directories: $(`$missingRoadmaps.Count)

## Non-Compliant Files

| File | Missing Metadata | Missing Status Legend | Missing Tasks |
|------|------------------|------------------------|--------------|
"@

    foreach (`$item in `$nonCompliantFiles) {
        `$reportContent += "`n| " + `$item.Path + " | " + `$item.MissingMetadata + " | " + `$item.MissingStatusLegend + " | " + `$item.MissingTasks + " |"
    }

    `$reportContent += @"

## Missing Roadmaps

The following key directories should have a roadmap.md file:

"@

    foreach (`$dir in `$missingRoadmaps) {
        `$reportContent += "`n- " + `$dir
    }

    `$reportContent += @"

## Recommendations

1. **Fix Non-Compliant Files:**
   - Add missing metadata headers
   - Include a Status Legend section
   - Organize tasks properly

2. **Create Missing Roadmaps:**
   - Use the template at `docs/templates/roadmap_template.md`
   - Ensure proper linking to the main roadmap

3. **Run Standardization Check:**
   \`\`\`powershell
   cd $BaseDir
   .\scripts\maintenance\automation\run_roadmap_sync.ps1
   \`\`\`

## Related Documents

- [Roadmap Standardization Guidelines](docs/governance/roadmap_standardization.md)
- [Roadmap Hierarchy Guidelines](docs/governance/roadmap_hierarchy.md)
- [Roadmap Template](docs/templates/roadmap_template.md)
"@

    `$reportContent | Out-File -FilePath "`$standardizationReport.md" -Encoding utf8
    
    Write-Host "Generated standardization report: `$standardizationReport.md"
    
    # Create notification if there are non-compliant files or missing roadmaps
    if ((`$nonCompliantFiles.Count -gt 0) -or (`$missingRoadmaps.Count -gt 0)) {
        `$notificationFile = Join-Path -Path "$BaseDir" -ChildPath "ROADMAP_STANDARDIZATION_NEEDED.md"
        @"
# Roadmap Standardization Needed

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

The automated roadmap standardization check has detected issues with roadmap files:

- Non-Compliant Files: $(`$nonCompliantFiles.Count)
- Missing Roadmaps in Key Directories: $(`$missingRoadmaps.Count)

## Details

Please review the full report at:
- [`$standardizationReport.md](`$standardizationReport.md)

## Quick Actions

1. **Fix Non-Compliant Files:**
   - Add missing metadata headers
   - Include a Status Legend section
   - Organize tasks properly

2. **Create Missing Roadmaps:**
   - Use the template at `docs/templates/roadmap_template.md`
   - Ensure proper linking to the main roadmap

## Next Steps

After addressing these issues, delete this file to acknowledge completion.
"@ | Out-File -FilePath `$notificationFile -Encoding utf8
        
        Write-Host "Created standardization notification file: `$notificationFile"
    }
    
    Write-Host "Roadmap synchronization and standardization check completed successfully."
    
} catch {
    Write-Error "An error occurred: `$_"
    exit 1
} finally {
    Stop-Transcript
}
"@

# Create the wrapper script
Set-Content -Path $wrapperScriptPath -Value $wrapperScriptContent
Write-Host "Created wrapper script: $wrapperScriptPath"

# Create common functions script if it doesn't exist
$commonFunctionsPath = Join-Path -Path $BaseDir -ChildPath "scripts\maintenance\automation\common_functions.ps1"
if (-not (Test-Path $commonFunctionsPath)) {
    $commonFunctionsContent = @"
# EGOS Common Functions for Automation Scripts
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

function Send-EmailNotification {
    param (
        [string]`$Subject,
        [string]`$Body,
        [string[]]`$Attachments = @()
    )
    
    # This is a placeholder function for email notifications
    # Implement actual email sending logic based on your environment
    Write-Host "Would send email with subject: `$Subject"
    Write-Host "Attachments: `$Attachments"
}

function Get-ProjectVersion {
    param (
        [string]`$ProjectRoot = "."
    )
    
    # Try to get version from version.txt if it exists
    `$versionFile = Join-Path -Path `$ProjectRoot -ChildPath "version.txt"
    if (Test-Path `$versionFile) {
        return Get-Content -Path `$versionFile -Raw
    }
    
    # Default version if not found
    return "1.0.0"
}

function Format-MarkdownTable {
    param (
        [Parameter(Mandatory=`$true, ValueFromPipeline=`$true)]
        [PSObject[]]`$InputObject,
        
        [Parameter(Mandatory=`$true)]
        [string[]]`$Columns
    )
    
    begin {
        `$output = @()
        
        # Add header row
        `$headerRow = "| " + (`$Columns -join " | ") + " |"
        `$output += `$headerRow
        
        # Add separator row
        `$separatorRow = "|" + (`$Columns | ForEach-Object { " --- |" } -join "")
        `$output += `$separatorRow
    }
    
    process {
        foreach (`$item in `$InputObject) {
            `$row = "| "
            foreach (`$column in `$Columns) {
                `$value = `$item.`$column
                if (`$null -eq `$value) { `$value = "" }
                `$row += `$value + " | "
            }
            `$output += `$row
        }
    }
    
    end {
        return `$output -join "`n"
    }
}
"@
    Set-Content -Path $commonFunctionsPath -Value $commonFunctionsContent
    Write-Host "Created common functions script: $commonFunctionsPath"
}

# Create the task in Windows Task Scheduler
$taskName = "EGOS_Roadmap_Sync"
$taskDescription = "Synchronizes EGOS roadmap files and checks standardization"

# Delete the task if it already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing task: $taskName"
}

# Create the task action
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$wrapperScriptPath`"" -WorkingDirectory $BaseDir

# Create the task trigger
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $DayOfWeek -At $ScheduleTime

# Create the task settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Create the task principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the task
Register-ScheduledTask -TaskName $taskName -Description $taskDescription -Action $action -Trigger $trigger -Settings $settings -Principal $principal
Write-Host "Registered scheduled task: $taskName"

# Create logs directory
$logsDir = Join-Path -Path $BaseDir -ChildPath "logs\roadmap"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Write-Host "Created logs directory: $logsDir"
}

# Run the script once to generate initial reports
Write-Host "Running initial roadmap synchronization and standardization check..."
& $wrapperScriptPath

Write-Host "`nSetup completed successfully!"
Write-Host "The roadmap synchronization task will run every $DayOfWeek at $ScheduleTime."
Write-Host "Reports will be saved to: $reportPath"
Write-Host "Logs will be saved to: $logsDir"
Write-Host "`nYou can manually run the synchronization at any time with:"
Write-Host "  & `"$wrapperScriptPath`""