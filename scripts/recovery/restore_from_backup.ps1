# Script to restore files from backups
# Created as part of the recovery effort on 2025-05-20

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupDir = "C:\EGOS\backups",
    
    [Parameter(Mandatory=$false)]
    [switch]$Preview
)

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

# Main script logic
if (-not (Test-Path $FilePath)) {
    Write-Error "File not found: $FilePath"
    exit 1
}

Write-Host "Searching for backups of: $FilePath"
$backup = Find-MostRecentBackup -OriginalPath $FilePath -BackupRoot $BackupDir

if ($null -eq $backup) {
    Write-Host "No backup found for this file." -ForegroundColor Yellow
    exit 0
}

Write-Host "Found backup: $($backup.FullName)" -ForegroundColor Green
Write-Host "Backup date: $($backup.LastWriteTime)" -ForegroundColor Cyan

# Create a backup of the current file before restoring
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$currentBackupPath = "$FilePath.pre_restore_$timestamp"
Copy-Item -Path $FilePath -Destination $currentBackupPath
Write-Host "Created backup of current file: $currentBackupPath" -ForegroundColor Cyan

# Show a preview of differences
Write-Host "`nDifferences between current file and backup:" -ForegroundColor Yellow
$diff = Compare-Object -ReferenceObject (Get-Content $FilePath) -DifferenceObject (Get-Content $backup.FullName)
$diff | ForEach-Object {
    if ($_.SideIndicator -eq "<=") {
        Write-Host "- $($_.InputObject)" -ForegroundColor Red
    } else {
        Write-Host "+ $($_.InputObject)" -ForegroundColor Green
    }
}

if ($Preview) {
    Write-Host "`nPreview mode - no changes made." -ForegroundColor Yellow
    exit 0
}

# Restore the file
$confirmRestore = Read-Host "Do you want to restore this file from backup? (Y/N)"
if ($confirmRestore -eq "Y" -or $confirmRestore -eq "y") {
    Copy-Item -Path $backup.FullName -Destination $FilePath -Force
    Write-Host "File restored successfully from backup." -ForegroundColor Green
} else {
    Write-Host "Restore cancelled." -ForegroundColor Yellow
}