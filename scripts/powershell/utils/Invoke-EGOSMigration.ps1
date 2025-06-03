<#
.SYNOPSIS
    Simple utility to migrate files and directories based on a CSV definition.

.DESCRIPTION
    Processes a CSV file with migration tasks and performs move or copy operations.

.PARAMETER CsvPath
    Path to the CSV file with migration tasks.

.PARAMETER DryRun
    If specified, only simulates the operations without making changes.

.PARAMETER CsvLogPath
    Optional. Path to the CSV log file for structured logging of operations.
    If not specified, only console logging is performed. The log includes:
    Timestamp, SourcePath, DestinationPath, ItemType, Operation, Status, Details.

.EXAMPLE
    # Example 1: Dry run to see what would happen
    .\Invoke-EGOSMigration.ps1 -CsvPath .\migration_tasks.csv -DryRun

    # Example 2: Execute migration and log to a CSV file
    .\Invoke-EGOSMigration.ps1 -CsvPath .\migration_tasks.csv -CsvLogPath .\migration_log.csv

    # Example 3: Execute migration without CSV logging (console output only)
    .\Invoke-EGOSMigration.ps1 -CsvPath .\migration_tasks.csv
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$CsvPath,
    
    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [string]$CsvLogPath
)

# CSV Log Header
$csvLogHeader = "Timestamp,SourcePath,DestinationPath,ItemType,Operation,Status,Details"

# Function to write to CSV Log
function Write-CsvLogEntry {
    param (
        [string]$SourcePath,
        [string]$DestinationPath,
        [string]$ItemType,
        [string]$Operation,
        [string]$Status,
        [string]$Details
    )
    if (-not $CsvLogPath) { return }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logRecord = [PSCustomObject]@{        
        Timestamp = $timestamp
        SourcePath = $SourcePath
        DestinationPath = $DestinationPath
        ItemType = $ItemType
        Operation = $Operation
        Status = $Status
        Details = $Details
    }
    # Ensure directory for CSV log exists
    $csvLogDir = Split-Path $CsvLogPath -Parent
    if ($csvLogDir -and (-not (Test-Path $csvLogDir))) {
        try {
            New-Item -Path $csvLogDir -ItemType Directory -Force -ErrorAction SilentlyContinue | Out-Null
        } catch {
            Write-Host "WARNING: Could not create directory for CSV Log at $csvLogDir. CSV logging might fail." -ForegroundColor Yellow
        }
    }
    # Initialize CSV log file with header if it doesn't exist or is empty
    if (-not (Test-Path $CsvLogPath) -or (Get-Item $CsvLogPath).Length -eq 0) {
        try {
            Set-Content -Path $CsvLogPath -Value $csvLogHeader -ErrorAction SilentlyContinue
        } catch {
             Write-Host "WARNING: Could not write header to CSV Log at $CsvLogPath. CSV logging might fail." -ForegroundColor Yellow
        }
    }
    try {
        $logRecord | Export-Csv -Path $CsvLogPath -Append -NoTypeInformation -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "WARNING: Failed to write to CSV Log at $CsvLogPath. Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Start message
Write-Host "Starting EGOS Migration Tool"
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'EXECUTE' })"
Write-Host "Using CSV: $CsvPath"
if ($CsvLogPath) { Write-Host "CSV Log File: $CsvLogPath" }
Write-Host "----------------------------------------"

# Check if CSV exists
if (-not (Test-Path $CsvPath)) {
    Write-Host "ERROR: CSV file not found at $CsvPath" -ForegroundColor Red
    exit 1
}

# Import CSV
try {
    $tasks = Import-Csv -Path $CsvPath
    Write-Host "Loaded $($tasks.Count) tasks from CSV" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to import CSV: $_" -ForegroundColor Red
    exit 1
}

# Process each task
$taskNum = 0
$success = 0
$failed = 0
$skipped = 0

foreach ($task in $tasks) {
    $taskNum++
    
    # Get task details
    $source = $task.SourcePath
    $dest = $task.DestinationPath
    $type = $task.ItemType
    $op = $task.Operation
    $createParents = $task.CreateParents -eq "true"
    $overwrite = $task.Overwrite -eq "true"
    
    Write-Host "`nTask $taskNum/$($tasks.Count): $op $type"
    Write-Host "  From: $source"
    Write-Host "  To:   $dest"
    
    # Check source exists
    if (-not (Test-Path $source)) {
        $errMsg = "Source does not exist"
        Write-Host "  ERROR: $errMsg" -ForegroundColor Red
        Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "FAILED" -Details $errMsg
        $failed++
        continue
    }
    
    # Check if destination exists
    $destExists = Test-Path $dest
    if ($destExists -and -not $overwrite) {
        $skipMsg = "Destination exists and overwrite=false"
        Write-Host "  SKIP: $skipMsg" -ForegroundColor Yellow
        Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "SKIPPED" -Details $skipMsg
        $skipped++
        continue
    }
    
    # Create parent directory if needed
    if ($createParents) {
        $parent = Split-Path $dest -Parent
        if (-not (Test-Path $parent)) {
            Write-Host "  Creating parent directory: $parent"
            if (-not $DryRun) {
                try {
                    New-Item -Path $parent -ItemType Directory -Force | Out-Null
                }
                catch {
                    $errMsg = "Failed to create parent directory: $($_.Exception.Message)"
                    Write-Host "  ERROR: $errMsg" -ForegroundColor Red
                    Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "FAILED" -Details $errMsg
                    $failed++
                    continue
                }
            }
        }
    }
    
    # Execute the operation
    if ($DryRun) {
        $dryRunMsg = "DRY RUN: Would $op $type from '$source' to '$dest'"
        Write-Host "  $dryRunMsg" -ForegroundColor Cyan
        Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "DRYRUN_SUCCESS" -Details "Operation simulated"
        $success++
    }
    else {
        try {
            if ($op -eq "Move") {
                Move-Item -Path $source -Destination $dest -Force:$overwrite
                Write-Host "  SUCCESS: Moved $type to $dest" -ForegroundColor Green
                Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "SUCCESS" -Details "Move completed"
            }
            elseif ($op -eq "Copy") {
                if ($type -eq "Directory") {
                    Copy-Item -Path $source -Destination $dest -Recurse -Force:$overwrite
                }
                else {
                    Copy-Item -Path $source -Destination $dest -Force:$overwrite
                }
                Write-Host "  SUCCESS: Copied $type to $dest" -ForegroundColor Green
                Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "SUCCESS" -Details "Copy completed"
            }
            else {
                $errMsg = "Unknown operation '$op'"
                Write-Host "  ERROR: $errMsg" -ForegroundColor Red
                Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "FAILED" -Details $errMsg
                $failed++
                continue
            }
            $success++
        }
        catch {
            $errMsg = "Operation failed: $($_.Exception.Message)"
            Write-Host "  ERROR: $errMsg" -ForegroundColor Red
            Write-CsvLogEntry -SourcePath $source -DestinationPath $dest -ItemType $type -Operation $op -Status "FAILED" -Details $errMsg
            $failed++
        }
    }
}

# Summary
Write-Host "`n----------------------------------------"
Write-Host "Migration Summary:"
Write-Host "  Total tasks:  $taskNum"
Write-Host "  Successful:   $success"
Write-Host "  Failed:       $failed"
Write-Host "  Skipped:      $skipped"
Write-Host "----------------------------------------"