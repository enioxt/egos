# Migrate Locale Content Script
# This script completes the migration from locale-based routing to root-based routing
# Implements EGOS Conscious Modularity principles and follows RULE-OPS-AUTONOMY-01

Write-Output "=== EGOS Locale Content Migration Tool ==="
Write-Output "Moving content from locale-specific routes to the root path..."

# Check if there's anything to migrate
if (-not (Test-Path "src\app\en")) {
    Write-Output "No /en locale directory found. Migration may already be complete."
    exit 0
}

# Handle specific migration cases with smart handling
$filesToMigrate = @(
    # Format: @{ Source = "source path"; Destination = "destination path"; Action = "copy|move|skip" }
    @{ Source = "src\app\en\HomeContent.tsx"; Destination = "src\components\HomeContent.tsx"; Action = "skip" }
    @{ Source = "src\app\en\RoadmapSection.tsx"; Destination = "src\components\content\RoadmapSection.tsx"; Action = "copy" }
    @{ Source = "src\app\en\globals.css"; Destination = "src\app\globals.css"; Action = "skip" }
    @{ Source = "src\app\en\page.tsx"; Destination = "src\app\page.tsx"; Action = "skip" }
)

# Process each file with appropriate action
foreach ($file in $filesToMigrate) {
    if (Test-Path $file.Source) {
        $destDir = Split-Path -Path $file.Destination -Parent
        if (-not (Test-Path $destDir)) {
            Write-Output "Creating directory: $destDir"
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }
        
        # If destination already exists, compare content
        if (Test-Path $file.Destination) {
            if ((Get-FileHash -Path $file.Source -Algorithm SHA256).Hash -eq 
                (Get-FileHash -Path $file.Destination -Algorithm SHA256).Hash) {
                Write-Output "✓ $($file.Source) and $($file.Destination) are identical."
                if ($file.Action -eq "skip") {
                    Write-Output "  Skipping as instructed..."
                    continue
                }
            } else {
                Write-Output "⚠ $($file.Source) and $($file.Destination) have different content."
                # Create backup of destination
                Copy-Item -Path $file.Destination -Destination "$($file.Destination).bak" -Force
                Write-Output "  Created backup: $($file.Destination).bak"
            }
        } else {
            Write-Output "🔍 Destination doesn't exist: $($file.Destination)"
        }
        
        # Perform requested action
        if ($file.Action -eq "copy" -or $file.Action -eq "move") {
            Write-Output "📋 Copying $($file.Source) to $($file.Destination)"
            Copy-Item -Path $file.Source -Destination $file.Destination -Force
            
            if ($file.Action -eq "move") {
                Write-Output "🗑️ Removing source file after successful copy"
                Remove-Item -Path $file.Source -Force
            }
        } else {
            Write-Output "⏭️ Skipping $($file.Source) as per configuration"
        }
    } else {
        Write-Output "❌ Source file not found: $($file.Source)"
    }
}

# Disable the locale-based routing completely by removing or renaming the /en directory
if (Test-Path "src\app\en") {
    Write-Output "📂 Renaming locale directory to prevent further routing conflicts"
    if (Test-Path "src\app\en.old") {
        Remove-Item -Path "src\app\en.old" -Recurse -Force
    }
    Rename-Item -Path "src\app\en" -NewName "en.old" -Force
}

Write-Output "=== Locale Content Migration Complete ==="
Write-Output "Run 'npm run build' to verify the fix"
