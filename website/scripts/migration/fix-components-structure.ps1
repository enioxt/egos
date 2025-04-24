# Enhanced Script to consolidate the components directory structure
# Following EGOS Conscious Modularity principles (Ref: MEMORY[user_global])
# Implements RULE-OPS-AUTONOMY-01 by batching related file structure operations

Write-Output "=== EGOS Component Directory Structure Fix ===" 
Write-Output "Applying Conscious Modularity principles to resolve directory inconsistencies..."

# Create any missing target directories
$directories = @(
    'src\components\ui',
    'src\components\svg',
    'src\components\layout',
    'src\components\content',
    'src\components\features'
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        Write-Output "Creating $dir directory"
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
}

# Function to copy component files with proper handling
function Copy-ComponentFiles {
    param (
        [string]$sourcePath,
        [string]$targetPath,
        [string]$componentType
    )
    
    if (-not (Test-Path $sourcePath)) {
        Write-Output "Source path not found: $sourcePath"
        return
    }
    
    Write-Output "Moving $componentType components from $sourcePath to $targetPath"
    Get-ChildItem -Path $sourcePath -Filter '*.tsx' | ForEach-Object {
        $destPath = Join-Path $targetPath $_.Name
        
        if (Test-Path $destPath) {
            # Handle existing files with smart merging
            try {
                $sourceHash = (Get-FileHash $_.FullName).Hash
                $destHash = (Get-FileHash $destPath).Hash
                
                if ($sourceHash -eq $destHash) {
                    Write-Output "  • $($_.Name): Files are identical, skipping"
                } else {
                    Write-Output "  • $($_.Name): Files differ, applying smart merge"
                    # Create backup
                    Copy-Item -Path $destPath -Destination "$destPath.bak" -Force
                    # Use the newer/complete version
                    if ($_.LastWriteTime -gt (Get-Item $destPath).LastWriteTime) {
                        Copy-Item -Path $_.FullName -Destination $destPath -Force
                        Write-Output "    - Source is newer, using source version"
                    } else {
                        Write-Output "    - Destination is newer, keeping destination version"
                    }
                }
            } catch {
                Write-Output "  • Error comparing files: $($_.Exception.Message)"
                Copy-Item -Path $_.FullName -Destination "$destPath.new" -Force
            }
        } else {
            Write-Output "  • $($_.Name): Copying to $targetPath"
            Copy-Item -Path $_.FullName -Destination $destPath -Force
        }
    }
}

# Move all component subdirectories
$componentMappings = @(
    @{ Source = 'components\ui'; Target = 'src\components\ui'; Type = 'UI' },
    @{ Source = 'components\svg'; Target = 'src\components\svg'; Type = 'SVG' },
    @{ Source = 'components\layout'; Target = 'src\components\layout'; Type = 'Layout' },
    @{ Source = 'components\content'; Target = 'src\components\content'; Type = 'Content' },
    @{ Source = 'components\features'; Target = 'src\components\features'; Type = 'Feature' }
)

foreach ($mapping in $componentMappings) {
    Copy-ComponentFiles -sourcePath $mapping.Source -targetPath $mapping.Target -componentType $mapping.Type
}

# Handle root component files
if (Test-Path 'components' -PathType Container) {
    $rootComponentFiles = Get-ChildItem -Path 'components' -Filter '*.tsx' 
    if ($rootComponentFiles.Count -gt 0) {
        Write-Output "Moving root component files to src\components"
        foreach ($file in $rootComponentFiles) {
            $destPath = "src\components\$($file.Name)"
            if (Test-Path $destPath) {
                Write-Output "  • $($file.Name): File already exists in target location"
                if ((Get-FileHash $file.FullName).Hash -eq (Get-FileHash $destPath).Hash) {
                    Write-Output "    - Files are identical, skipping"
                } else {
                    Write-Output "    - Files differ, copying with .new extension"
                    Copy-Item -Path $file.FullName -Destination "$destPath.new" -Force
                }
            } else {
                Write-Output "  • $($file.Name): Copying to src\components"
                Copy-Item -Path $file.FullName -Destination $destPath -Force
            }
        }
    }
}

# Verify critical files that Next.js might be looking for
$criticalFiles = @(
    @{ Path = 'src\components\ui\alert-dialog.tsx'; Source = 'components\ui\alert-dialog.tsx' }
)

foreach ($file in $criticalFiles) {
    if (-not (Test-Path $file.Path)) {
        if (Test-Path $file.Source) {
            Write-Output "Critical file $($file.Path) missing - copying from $($file.Source)"
            Copy-Item -Path $file.Source -Destination $file.Path -Force
        } else {
            Write-Output "WARNING: Critical file $($file.Path) missing and source not found!"
        }
    }
}

# Create a symbolic link for compatibility (temporary solution)
if ((Test-Path 'components') -and (-not (Test-Path 'components_old'))) {
    Write-Output "Creating temporary symbolic link for backward compatibility"
    try {
        # Rename original components dir to components_old
        Rename-Item -Path 'components' -NewName 'components_old' -Force
        # Create junction point for backward compatibility
        New-Item -ItemType Junction -Path 'components' -Target 'src\components'
        Write-Output "Created directory junction: components -> src\components"
    } catch {
        Write-Output "ERROR creating compatibility link: $($_.Exception.Message)"
        # Try to restore if failed
        if (Test-Path 'components_old') {
            Rename-Item -Path 'components_old' -NewName 'components' -Force
        }
    }
}

Write-Output "=== Component Migration Complete ===" 
Write-Output "1. Run 'npm run build' to verify the changes"
Write-Output "2. After verifying the build works, remove the 'components_old' directory"
Write-Output "3. Check any .new or .bak files to resolve remaining differences"
