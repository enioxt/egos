# EGOS Scheduled Cleanup Task Creator
# This script creates a scheduled task to run the EGOS cleanup script periodically
# Following EGOS principles of Compassionate Temporality and Evolutionary Preservation

# Configuration
$taskName = "EGOS_Scheduled_Cleanup"
$taskDescription = "Performs automated cleanup of temporary files in the EGOS system"
$scriptPath = Join-Path $PSScriptRoot "scheduled_cleanup.py"
$configPath = Join-Path $PSScriptRoot "cleanup_config.json"
$logDir = Join-Path $PSScriptRoot "..\..\logs\maintenance"
$pythonExe = "python"

# Ensure log directory exists
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    Write-Host "Created log directory: $logDir"
}

# Generate log file path with timestamp
$timestamp = Get-Date -Format "yyyyMMdd"
$logFile = Join-Path $logDir "cleanup_${timestamp}.log"

# Build the command to execute
$workingDir = Join-Path $PSScriptRoot "..\..\"
$command = "$pythonExe $scriptPath --root `"$workingDir`" --config `"$configPath`" --log-file `"$logFile`""

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"$command`"" -WorkingDirectory $workingDir

# Create the scheduled task trigger (weekly on Sunday at 3:00 AM)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am

# Create the scheduled task settings (wake to run, run with highest privileges)
$settings = New-ScheduledTaskSettingsSet -WakeToRun -RunOnlyIfNetworkAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Create the scheduled task principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the scheduled task
try {
    # Check if the task already exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($existingTask) {
        # Update existing task
        Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription
        Write-Host "Updated scheduled task: $taskName"
    } else {
        # Create new task
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription
        Write-Host "Created scheduled task: $taskName"
    }
    
    # Output success message
    Write-Host "Scheduled task '$taskName' has been configured to run weekly on Sunday at 3:00 AM."
    Write-Host "The task will execute the EGOS cleanup script with the following command:"
    Write-Host $command
    
} catch {
    Write-Error "Failed to register scheduled task: $_"
    exit 1
}

# Create a manual run script for on-demand execution
$manualRunScript = @"
# EGOS Cleanup Manual Run Script
# Run this script to execute the cleanup process immediately

Write-Host "Running EGOS cleanup script..."
$command
Write-Host "Cleanup completed. Check the log file for details: $logFile"
"@

$manualRunPath = Join-Path $PSScriptRoot "run_cleanup_now.ps1"
$manualRunScript | Out-File -FilePath $manualRunPath -Encoding utf8

Write-Host "Created manual run script: $manualRunPath"
Write-Host "You can run this script at any time to execute the cleanup process manually."

# Done
Write-Host "Setup completed successfully."
