# Direct component migration script
# Implements EGOS Conscious Modularity principles by consolidating all components
# into the standard Next.js src/components structure

Write-Output "=== EGOS Component Direct Migration Tool ==="
Write-Output "Implementing Conscious Modularity: Moving all components to src/components..."

# Ensure target directory exists
if (-not (Test-Path "src\components")) {
    New-Item -Path "src\components" -ItemType Directory -Force
}

# Copy all files from components to src/components
if (Test-Path "components") {
    # First, copy all top-level component files
    Get-ChildItem -Path "components" -File -Filter "*.tsx" | ForEach-Object {
        $targetPath = "src\components\$($_.Name)"
        Write-Output "Copying $($_.Name) to src\components\"
        Copy-Item -Path $_.FullName -Destination $targetPath -Force
    }
    
    # Then handle subdirectories
    Get-ChildItem -Path "components" -Directory | ForEach-Object {
        $dirName = $_.Name
        $targetDir = "src\components\$dirName"
        
        # Create directory if it doesn't exist
        if (-not (Test-Path $targetDir)) {
            New-Item -Path $targetDir -ItemType Directory -Force
        }
        
        # Copy all files in the subdirectory
        Get-ChildItem -Path $_.FullName -File -Recurse | ForEach-Object {
            $relativePath = $_.FullName.Substring($_.FullName.IndexOf("\$dirName\") + $dirName.Length + 2)
            $targetPath = Join-Path $targetDir $relativePath
            
            # Ensure target directory exists
            $targetDirPath = Split-Path -Path $targetPath -Parent
            if (-not (Test-Path $targetDirPath)) {
                New-Item -Path $targetDirPath -ItemType Directory -Force
            }
            
            Write-Output "Copying $($_.Name) to $targetDirPath"
            Copy-Item -Path $_.FullName -Destination $targetPath -Force
        }
    }
    
    # Rename original components directory to prevent further build issues
    Write-Output "Renaming original 'components' directory to 'components.old'"
    if (Test-Path "components.old") {
        Remove-Item -Path "components.old" -Recurse -Force
    }
    Rename-Item -Path "components" -NewName "components.old" -Force
}

Write-Output "=== Migration Complete ==="
Write-Output "Run 'npm run build' to verify the fix"
