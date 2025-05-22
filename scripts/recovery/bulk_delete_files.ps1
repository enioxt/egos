#Requires -Version 5.1
<#
.SYNOPSIS
    Bulk deletes files based on a provided list.
.DESCRIPTION
    This script reads a list of full file paths from an input text file
    and attempts to delete each file. It logs all actions.
.PARAMETER InputFilePath
    The full path to the text file containing the list of files to delete (one file per line).
.PARAMETER LogDirectory
    The directory where the log file will be created. Defaults to 'C:\EGOS\recovery_analysis'.
.EXAMPLE
    .\bulk_delete_files.ps1 -InputFilePath "C:\EGOS\recovery_analysis\deletion_candidates.txt"
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$InputFilePath,

    [Parameter(Mandatory=$false)]
    [string]$LogDirectory = "C:\EGOS\recovery_analysis"
)

# --- Script Configuration ---
$ErrorActionPreference = "SilentlyContinue" # Handle errors manually

# --- Initialization ---
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$scriptName = $MyInvocation.MyCommand.Name
$logFileName = "bulk_delete_log_${timestamp}.txt"
$logFilePath = Join-Path -Path $LogDirectory -ChildPath $logFileName

# --- Functions ---
function Write-Log {
    param(
        [string]$Message,
        [switch]$NoTimestamp
    )
    $logEntry = if ($NoTimestamp) { $Message } else { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message" }
    Add-Content -Path $logFilePath -Value $logEntry
    Write-Host $Message # Also output to console
}

# --- Main Script ---
# Ensure Log Directory exists
if (-not (Test-Path -Path $LogDirectory -PathType Container)) {
    try {
        New-Item -Path $LogDirectory -ItemType Directory -Force -ErrorAction Stop | Out-Null
        Write-Log "Log directory created: $LogDirectory" -NoTimestamp
    }
    catch {
        Write-Error "FATAL: Could not create log directory '$LogDirectory'. Error: $($_.Exception.Message)"
        exit 1 # Cannot proceed without logging
    }
}

Write-Log "Bulk Delete Script Started." -NoTimestamp
Write-Log "--------------------------------------------------" -NoTimestamp
Write-Log "Input File: $InputFilePath"
Write-Log "Log File:   $logFilePath"
Write-Log "--------------------------------------------------" -NoTimestamp

if (-not (Test-Path -Path $InputFilePath -PathType Leaf)) {
    Write-Log "ERROR: Input file '$InputFilePath' not found or is not a file."
    Write-Log "Bulk Delete Script Aborted." -NoTimestamp
    exit 1
}

$filesToDelete = Get-Content -Path $InputFilePath -ErrorAction SilentlyContinue
if ($null -eq $filesToDelete -or $filesToDelete.Count -eq 0) {
    Write-Log "INFO: Input file '$InputFilePath' is empty or could not be read. No files to delete."
    Write-Log "Bulk Delete Script Finished." -NoTimestamp
    exit 0
}

Write-Log "Found $($filesToDelete.Count) file path(s) in '$InputFilePath'."
Write-Log "Starting deletion process..."
Write-Log "--------------------------------------------------" -NoTimestamp

$deletedCount = 0
$notFoundCount = 0
$errorCount = 0

foreach ($filePath in $filesToDelete) {
    $trimmedPath = $filePath.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmedPath)) {
        Write-Log "SKIPPED: Empty line in input file."
        continue
    }

    Write-Log "Attempting to delete: $trimmedPath"
    if (Test-Path -Path $trimmedPath -PathType Leaf) {
        try {
            Remove-Item -Path $trimmedPath -Force -ErrorAction Stop
            Write-Log "  SUCCESS: Deleted '$trimmedPath'."
            $deletedCount++
        }
        catch {
            Write-Log "  ERROR: Could not delete '$trimmedPath'. Reason: $($_.Exception.Message)"
            $errorCount++
        }
    }
    elseif (Test-Path -Path $trimmedPath -PathType Container) {
        Write-Log "  SKIPPED: Path '$trimmedPath' is a directory, not a file. This script only deletes files."
        $errorCount++ # Counting as an error because it was expected to be a file
    }
    else {
        Write-Log "  NOT FOUND: File '$trimmedPath' does not exist or was already deleted."
        $notFoundCount++
    }
}

Write-Log "--------------------------------------------------" -NoTimestamp
Write-Log "Deletion Process Summary:"
Write-Log "  Successfully deleted: $deletedCount file(s)."
Write-Log "  Files not found:    $notFoundCount file(s)."
Write-Log "  Errors encountered: $errorCount file(s)."
Write-Log "--------------------------------------------------" -NoTimestamp
Write-Log "Bulk Delete Script Finished." -NoTimestamp
