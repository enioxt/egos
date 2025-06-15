# Batch Restore Script for EGOS Recovery
# This script helps restore multiple files from backups in a batch process
# Created: 2025-05-20

param(
    [Parameter(Mandatory=$false)]
    [string]$InputCsvPath,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupDir = "C:\EGOS\backups",
    
    [Parameter(Mandatory=$false)]
    [switch]$Preview
)

# Create a timestamp for the operation
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "C:\EGOS\recovery_analysis\restore_log_$timestamp.txt"

# Start logging
"Batch Restore Operation - $timestamp" | Out-File -FilePath $logFile
"Preview Mode: $Preview" | Out-File -FilePath $logFile -Append

# Function to find the most recent backup of a file
function Find-MostRecentBackup {
    param (
        [string]$OriginalPath,
        [string]$BackupRoot
    )
    
    # Get the relative path from EGOS root
    $relativePath = $OriginalPath -replace "C:\\EGOS\\", ""
    $fileDir = Split-Path -Parent $relativePath
    $fileName = Split-Path -Leaf $relativePath
    
    # Search for backups
    $potentialBackups = @()
    
    # Check in backup directories
    Get-ChildItem -Path $BackupRoot -Recurse -File | Where-Object {
        $_.Name -eq $fileName
    } | ForEach-Object {
        $potentialBackups += $_
    }
    
    # If we found potential backups, return the most recent one
    if ($potentialBackups.Count -gt 0) {
        return $potentialBackups | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    }
    
    return $null
}

# Function to restore a single file
function Restore-SingleFile {
    param (
        [string]$FilePath,
        [switch]$PreviewOnly
    )
    
    "Processing file: $FilePath" | Out-File -FilePath $logFile -Append
    
    if (-not (Test-Path $FilePath)) {
        "  Error: File not found: $FilePath" | Out-File -FilePath $logFile -Append
        return $false
    }
    
    $backup = Find-MostRecentBackup -OriginalPath $FilePath -BackupRoot $BackupDir
    
    if ($null -eq $backup) {
        "  No backup found for this file." | Out-File -FilePath $logFile -Append
        return $false
    }
    
    "  Found backup: $($backup.FullName)" | Out-File -FilePath $logFile -Append
    "  Backup date: $($backup.LastWriteTime)" | Out-File -FilePath $logFile -Append
    
    # Create a backup of the current file before restoring
    $currentBackupPath = "$FilePath.pre_restore_$timestamp"
    Copy-Item -Path $FilePath -Destination $currentBackupPath
    "  Created backup of current file: $currentBackupPath" | Out-File -FilePath $logFile -Append
    
    # If preview only, don't restore
    if ($PreviewOnly) {
        "  Preview mode - no changes made." | Out-File -FilePath $logFile -Append
        return $true
    }
    
    # Restore the file
    Copy-Item -Path $backup.FullName -Destination $FilePath -Force
    "  File restored successfully from backup." | Out-File -FilePath $logFile -Append
    return $true
}

# Main script logic
if ($InputCsvPath -and (Test-Path $InputCsvPath)) {
    $filesToRestore = Import-Csv -Path $InputCsvPath
    
    "Found $($filesToRestore.Count) files to process in CSV" | Out-File -FilePath $logFile -Append
    
    $successCount = 0
    $failCount = 0
    
    foreach ($fileEntry in $filesToRestore) {
        $filePath = $fileEntry.FilePath
        $result = Restore-SingleFile -FilePath $filePath -PreviewOnly:$Preview
        
        if ($result) {
            $successCount++
        } else {
            $failCount++
        }
    }
    
    "Batch processing complete." | Out-File -FilePath $logFile -Append
    "Success: $successCount" | Out-File -FilePath $logFile -Append
    "Failed: $failCount" | Out-File -FilePath $logFile -Append
} else {
    # Interactive mode - let the user select files
    "Interactive mode - no CSV provided" | Out-File -FilePath $logFile -Append
    
    # Define critical files to check
    $criticalFiles = @(
        "C:\EGOS\README.md",
        "C:\EGOS\ARCHITECTURE.MD",
        "C:\EGOS\CONTRIBUTING.md",
        "C:\EGOS\CODE_OF_CONDUCT.md",
        "C:\EGOS\.editorconfig",
        "C:\EGOS\.gitignore"
    )
    
    "Processing $($criticalFiles.Count) critical files" | Out-File -FilePath $logFile -Append
    
    $successCount = 0
    $failCount = 0
    
    foreach ($filePath in $criticalFiles) {
        Write-Host "Processing file: $filePath" -ForegroundColor Cyan
        $result = Restore-SingleFile -FilePath $filePath -PreviewOnly:$Preview
        
        if ($result) {
            Write-Host "  Backup found and processed." -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  No suitable backup found." -ForegroundColor Yellow
            $failCount++
        }
        
        # If not in preview mode, ask for confirmation
        if (-not $Preview -and $result) {
            $confirm = Read-Host "  Do you want to restore this file? (Y/N)"
            if ($confirm -eq "Y" -or $confirm -eq "y") {
                Copy-Item -Path (Find-MostRecentBackup -OriginalPath $filePath -BackupRoot $BackupDir).FullName -Destination $filePath -Force
                Write-Host "  File restored." -ForegroundColor Green
            } else {
                Write-Host "  Skipped restoration." -ForegroundColor Yellow
            }
        }
    }
    
    "Interactive processing complete." | Out-File -FilePath $logFile -Append
    "Success: $successCount" | Out-File -FilePath $logFile -Append
    "Failed: $failCount" | Out-File -FilePath $logFile -Append
}

Write-Host "Processing complete. See log file for details: $logFile" -ForegroundColor Green