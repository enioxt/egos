###############################################
# EGOS Project Structure Analysis Script
# Version: 1.0
# Date: 2025-05-20
# Purpose: Analyze the EGOS project structure to support reorganization
###############################################

# Configuration
$rootPath = "C:\EGOS"
$outputPath = "C:\EGOS\recovery_analysis"
$excludeDirs = @('.git', '.venv', 'node_modules', '__pycache__', '.obsidian', '.streamlit', '.cursor', '.vs')
$excludeExtensions = @('.pyc', '.git', '.tmp', '.log')
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = Join-Path -Path $outputPath -ChildPath "project_structure_analysis_$timestamp.md"

# Create output directory if it doesn't exist
if (-not (Test-Path -Path $outputPath)) {
    New-Item -Path $outputPath -ItemType Directory -Force
}

# Initialize results file with metadata and headers
$fileContent = @"
# EGOS Project Structure Analysis Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Root Directory:** $rootPath

## 1. Top-Level Structure

"@

# Get top-level directories and files
$topLevel = Get-ChildItem -Path $rootPath | Sort-Object -Property Name | ForEach-Object {
    $isDir = $_.PSIsContainer
    $pathType = if ($isDir) { "Directory" } else { "File" }
    $size = if (-not $isDir) { [math]::Round($_.Length / 1KB, 2) } else { "N/A" }
    
    "- **$($_.Name)** ($pathType" + $(if(-not $isDir) { ", Size: $size KB" } else { "" }) + ")"
}

$fileContent += "`n`n" + ($topLevel -join "`n") + "`n`n## 2. Empty Directories`n`n"

# Find empty directories
$emptyDirs = Get-ChildItem -Path $rootPath -Directory -Recurse | Where-Object {
    $dirPath = $_.FullName
    $exclude = $false
    foreach ($excludeDir in $excludeDirs) {
        if ($dirPath -like "*\$excludeDir*") {
            $exclude = $true
            break
        }
    }
    
    -not $exclude -and (Get-ChildItem -Path $dirPath -Recurse -File | Where-Object {
        $fileExt = [System.IO.Path]::GetExtension($_.Name)
        $exclude = $false
        foreach ($excludeExt in $excludeExtensions) {
            if ($fileExt -eq $excludeExt) {
                $exclude = $true
                break
            }
        }
        -not $exclude
    } | Measure-Object).Count -eq 0
} | Select-Object -ExpandProperty FullName

if ($emptyDirs.Count -gt 0) {
    $fileContent += ($emptyDirs | ForEach-Object { "- $($_ -replace [regex]::Escape($rootPath), 'C:\EGOS')" }) -join "`n"
} else {
    $fileContent += "No empty directories found (excluding system directories)."
}

# Count files by directory
$fileContent += "`n`n## 3. Directory File Distribution`n`n"

$fileContent += "| Directory | File Count | Subdirectory Count | Total Size (KB) |`n"
$fileContent += "|-----------|------------|-------------------|-----------------|`n"

$dirStats = Get-ChildItem -Path $rootPath -Directory | Where-Object {
    $excluded = $false
    foreach ($excludeDir in $excludeDirs) {
        if ($_.FullName -like "*\$excludeDir*") {
            $excluded = $true
            break
        }
    }
    -not $excluded
} | ForEach-Object {
    $dirPath = $_.FullName
    $dirName = $_.Name
    
    $files = Get-ChildItem -Path $dirPath -File -Recurse | Where-Object {
        $filePath = $_.FullName
        $excluded = $false
        foreach ($excludeDir in $excludeDirs) {
            if ($filePath -like "*\$excludeDir*") {
                $excluded = $true
                break
            }
        }
        -not $excluded
    }
    
    $fileCount = $files | Measure-Object | Select-Object -ExpandProperty Count
    $totalSize = $files | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum
    if ($null -eq $totalSize) { $totalSize = 0 }
    $totalSizeKB = [math]::Round($totalSize / 1KB, 2)
    
    $subdirCount = (Get-ChildItem -Path $dirPath -Directory -Recurse | Where-Object {
        $subDirPath = $_.FullName
        $excluded = $false
        foreach ($excludeDir in $excludeDirs) {
            if ($subDirPath -like "*\$excludeDir*") {
                $excluded = $true
                break
            }
        }
        -not $excluded
    } | Measure-Object).Count
    
    "| $dirName | $fileCount | $subdirCount | $totalSizeKB |"
}

$fileContent += $dirStats -join "`n"

# Count files by extension
$fileContent += "`n`n## 4. File Extensions Distribution`n`n"

$fileContent += "| Extension | Count | Total Size (KB) | Primary Locations |`n"
$fileContent += "|-----------|-------|-----------------|-------------------|`n"

$extensionStats = Get-ChildItem -Path $rootPath -File -Recurse | Where-Object {
    $filePath = $_.FullName
    $excluded = $false
    foreach ($excludeDir in $excludeDirs) {
        if ($filePath -like "*\$excludeDir*") {
            $excluded = $true
            break
        }
    }
    -not $excluded
} | Group-Object -Property {[System.IO.Path]::GetExtension($_)} | Sort-Object -Property Count -Descending | ForEach-Object {
    $extension = if ($_.Name -eq "") { "(no extension)" } else { $_.Name }
    $count = $_.Count
    $totalSize = ($_.Group | Measure-Object -Property Length -Sum).Sum
    $totalSizeKB = [math]::Round($totalSize / 1KB, 2)
    
    # Find primary locations (directories) for this extension
    $locations = $_.Group | ForEach-Object { Split-Path -Parent $_.FullName } | Group-Object | Sort-Object -Property Count -Descending | Select-Object -First 3 | ForEach-Object {
        $locationPath = $_.Name -replace [regex]::Escape($rootPath), 'C:\EGOS'
        $locationCount = $_.Count
        "$locationPath ($locationCount)"
    }
    
    $locationString = $locations -join ", "
    
    "| $extension | $count | $totalSizeKB | $locationString |"
}

$fileContent += $extensionStats -join "`n"

# Deep Scan of docs directory to understand structure
$fileContent += "`n`n## 5. Documentation Directory Structure`n`n"

$docsPath = Join-Path -Path $rootPath -ChildPath "docs"
$docsStructure = Get-ChildItem -Path $docsPath -Directory | Sort-Object -Property Name | ForEach-Object {
    $subdir = $_
    $subdirName = $subdir.Name
    $subdirPath = $subdir.FullName
    
    $fileCount = (Get-ChildItem -Path $subdirPath -File -Recurse | Measure-Object).Count
    $subdirCount = (Get-ChildItem -Path $subdirPath -Directory -Recurse | Measure-Object).Count
    
    "### $subdirName/`n`n"
    "- **Files:** $fileCount"
    "- **Subdirectories:** $subdirCount"
    
    # List first level of subdirectories
    $firstLevelDirs = Get-ChildItem -Path $subdirPath -Directory | Sort-Object -Property Name
    if ($firstLevelDirs.Count -gt 0) {
        "`n**Subdirectories:**`n"
        $firstLevelDirs | ForEach-Object {
            $nestedFileCount = (Get-ChildItem -Path $_.FullName -File -Recurse | Measure-Object).Count
            "- $($_.Name)/ ($nestedFileCount files)"
        }
    }
    
    # List top files (up to 10)
    $topFiles = Get-ChildItem -Path $subdirPath -File | Sort-Object -Property Length -Descending | Select-Object -First 10
    if ($topFiles.Count -gt 0) {
        "`n**Notable Files:**`n"
        $topFiles | ForEach-Object {
            $fileSize = [math]::Round($_.Length / 1KB, 2)
            "- $($_.Name) ($fileSize KB)"
        }
    }
    
    "`n"
}

$fileContent += $docsStructure -join "`n"

# Examine docs_egos staging area
$fileContent += "`n## 6. New Documentation Structure (docs_egos)`n`n"

$docsEgosPath = Join-Path -Path $rootPath -ChildPath "docs_egos"
$docsEgosStructure = Get-ChildItem -Path $docsEgosPath -Directory | Sort-Object -Property Name | ForEach-Object {
    $subdir = $_
    $subdirName = $subdir.Name
    $subdirPath = $subdir.FullName
    
    $fileCount = (Get-ChildItem -Path $subdirPath -File -Recurse | Measure-Object).Count
    $subdirCount = (Get-ChildItem -Path $subdirPath -Directory -Recurse | Measure-Object).Count
    
    "### $subdirName/`n`n"
    "- **Files:** $fileCount"
    "- **Subdirectories:** $subdirCount"
    
    # List first level of subdirectories
    $firstLevelDirs = Get-ChildItem -Path $subdirPath -Directory | Sort-Object -Property Name
    if ($firstLevelDirs.Count -gt 0) {
        "`n**Subdirectories:**`n"
        $firstLevelDirs | ForEach-Object {
            $nestedFileCount = (Get-ChildItem -Path $_.FullName -File -Recurse | Measure-Object).Count
            "- $($_.Name)/ ($nestedFileCount files)"
        }
    }
    
    "`n"
}

$fileContent += $docsEgosStructure -join "`n"

# Potential Redundancies Analysis
$fileContent += "`n## 7. Potential Redundancies`n`n"

# Look for similar file names across directories
$fileContent += "### Similar File Names`n`n"

$allFiles = Get-ChildItem -Path $rootPath -File -Recurse | Where-Object {
    $filePath = $_.FullName
    $excluded = $false
    foreach ($excludeDir in $excludeDirs) {
        if ($filePath -like "*\$excludeDir*") {
            $excluded = $true
            break
        }
    }
    -not $excluded
} | Select-Object Name, FullName, Length

# Group by similar names (removing prefixes like EGO_, XXX_, etc.)
$similarNames = $allFiles | Group-Object -Property { 
    $name = $_.Name
    $name -replace '^(EGO_|[A-Z]{3}_|README_)', '' -replace '\.(md|txt|py|js)$', ''
} | Where-Object { $_.Count -gt 1 } | Sort-Object -Property Count -Descending

if ($similarNames.Count -gt 0) {
    foreach ($group in $similarNames) {
        $baseName = $group.Name
        $count = $group.Count
        
        $fileContent += "**Base name: $baseName** ($count occurrences)`n`n"
        
        foreach ($file in $group.Group | Sort-Object -Property FullName) {
            $relativePath = $file.FullName -replace [regex]::Escape($rootPath), 'C:\EGOS'
            $sizeKB = [math]::Round($file.Length / 1KB, 2)
            $fileContent += "- $relativePath ($sizeKB KB)`n"
        }
        
        $fileContent += "`n"
    }
} else {
    $fileContent += "No similar file names found (excluding system directories).`n`n"
}

# Look for multiple roadmaps
$fileContent += "### Multiple Roadmap Files`n`n"

$roadmaps = Get-ChildItem -Path $rootPath -Recurse -File | Where-Object {
    $_.Name -like "*ROADMAP*" -and $_.FullName -notlike "*\$excludeDirs\*"
} | Select-Object FullName, Length

if ($roadmaps.Count -gt 0) {
    foreach ($roadmap in $roadmaps | Sort-Object -Property FullName) {
        $relativePath = $roadmap.FullName -replace [regex]::Escape($rootPath), 'C:\EGOS'
        $sizeKB = [math]::Round($roadmap.Length / 1KB, 2)
        $fileContent += "- $relativePath ($sizeKB KB)`n"
    }
} else {
    $fileContent += "No roadmap files found (excluding system directories).`n`n"
}

# Look for multiple README files
$fileContent += "`n### Multiple README Files`n`n"

$readmes = Get-ChildItem -Path $rootPath -Recurse -File | Where-Object {
    $_.Name -like "README*" -and $_.FullName -notlike "*\$excludeDirs\*"
} | Select-Object FullName, Length

if ($readmes.Count -gt 0) {
    foreach ($readme in $readmes | Sort-Object -Property FullName) {
        $relativePath = $readme.FullName -replace [regex]::Escape($rootPath), 'C:\EGOS'
        $sizeKB = [math]::Round($readme.Length / 1KB, 2)
        $fileContent += "- $relativePath ($sizeKB KB)`n"
    }
} else {
    $fileContent += "No README files found (excluding system directories).`n`n"
}

# Write the results to the output file
$fileContent | Out-File -FilePath $outputFile -Encoding utf8

Write-Host "Analysis complete. Results written to $outputFile"
