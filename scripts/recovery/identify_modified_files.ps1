# Script to identify files modified during the website recovery process
# Created as part of the recovery effort on 2025-05-20

# Define the timestamp when the website recovery occurred
$recoveryTime = Get-Date "2025-05-20 00:48:00"
$timeWindow = 30 # minutes

# Define directories to exclude from the search
$excludeDirs = @(
    "website", 
    "_website_backup_*", 
    "_temp_*", 
    ".git", 
    "node_modules", 
    ".next"
)

# Create the output directory if it doesn't exist
$outputDir = "C:\EGOS\recovery_analysis"
if (-not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory | Out-Null
}

# Function to check if a path should be excluded
function ShouldExclude($path) {
    foreach ($excludeDir in $excludeDirs) {
        if ($path -like "*\$excludeDir*") {
            return $true
        }
    }
    return $false
}

# Find files modified around the recovery time
Write-Host "Identifying files modified during website recovery..."
$modifiedFiles = Get-ChildItem -Path "C:\EGOS" -Recurse -File | 
    Where-Object { 
        -not (ShouldExclude($_.FullName)) -and 
        $_.LastWriteTime -ge $recoveryTime.AddMinutes(-$timeWindow) -and 
        $_.LastWriteTime -le $recoveryTime.AddMinutes($timeWindow)
    }

# Export the list of modified files
$modifiedFiles | 
    Select-Object FullName, LastWriteTime, Length | 
    Export-Csv -Path "$outputDir\modified_files.csv" -NoTypeInformation

# Group files by directory for easier analysis
$filesByDirectory = $modifiedFiles | 
    Group-Object -Property { Split-Path $_.FullName -Parent } | 
    Select-Object Name, @{Name="FileCount"; Expression={$_.Count}}, @{Name="Files"; Expression={$_.Group.Name -join ", "}}

$filesByDirectory | 
    Export-Csv -Path "$outputDir\modified_files_by_directory.csv" -NoTypeInformation

# Create a summary report
$totalFiles = $modifiedFiles.Count
$totalDirectories = $filesByDirectory.Count

$summaryContent = @"
# Website Recovery Analysis Report
Generated: $(Get-Date)

## Summary
- Recovery timestamp: $recoveryTime
- Time window analyzed: ±$timeWindow minutes
- Total files potentially affected: $totalFiles
- Number of directories with modified files: $totalDirectories

## Next Steps
1. Review the CSV files in this directory to identify which files need to be restored
2. For critical files, check backups or previous Git commits
3. Use the recovery script to restore files as needed

## Files
The following files were identified as potentially modified during the website recovery:

"@

foreach ($file in $modifiedFiles) {
    $summaryContent += "- $($file.FullName) (Modified: $($file.LastWriteTime))`n"
}

$summaryContent | Out-File -FilePath "$outputDir\recovery_analysis_report.md" -Encoding utf8

Write-Host "Analysis complete. Results saved to $outputDir"
Write-Host "Modified files: $totalFiles"
Write-Host "Affected directories: $totalDirectories"