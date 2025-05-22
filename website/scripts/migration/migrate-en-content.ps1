# EGOS en-locale Migration Script
# <!-- TO_BE_REPLACED -->KOIOS-CODE-001, CORUJA-MIGRATION-001

<#
@metadata
@title EGOS Locale Migration Script
@description Migrates content from locale-specific paths to the root structure
@author EgosArchitect
@version 1.0.0
@date 2025-04-24
@status ⚡ Active
@references
- `mdc:website/src/app/page.tsx`
- `mdc:website/middleware.ts`
- `mdc:website/next.config.js`
#>

Write-Output "=== EGOS Locale Migration Tool ==="
Write-Output "Moving content from /en locale path to root structure..."

# Step 1: Handle HomeContent component
# Note: This was already moved in the component consolidation but may need final cleanup
if (Test-Path "src\app\en\HomeContent.tsx") {
    Write-Output "Processing HomeContent.tsx..."
    # Check if the target exists first
    if (-not (Test-Path "src\components\HomeContent.tsx")) {
        Write-Output "  • Moving HomeContent.tsx to src\components\"
        Copy-Item -Path "src\app\en\HomeContent.tsx" -Destination "src\components\HomeContent.tsx" -Force
    } else {
        Write-Output "  • HomeContent.tsx already exists in src\components\"
    }
}

# Step 2: Migrate RoadmapSection component
if (Test-Path "src\app\en\RoadmapSection.tsx") {
    Write-Output "Processing RoadmapSection.tsx..."
    # Ensure target directory exists
    if (-not (Test-Path "src\components\content")) {
        New-Item -Path "src\components\content" -ItemType Directory -Force | Out-Null
    }
    
    if (-not (Test-Path "src\components\content\RoadmapSection.tsx")) {
        Write-Output "  • Moving RoadmapSection.tsx to src\components\content\"
        Copy-Item -Path "src\app\en\RoadmapSection.tsx" -Destination "src\components\content\RoadmapSection.tsx" -Force
    } else {
        Write-Output "  • RoadmapSection.tsx already exists in src\components\content\"
    }
}

# Step 3: Ensure global CSS is properly consolidated
if (Test-Path "src\app\en\globals.css") {
    Write-Output "Processing globals.css..."
    # If the root globals.css doesn't exist, copy it there
    if (-not (Test-Path "src\app\globals.css")) {
        Write-Output "  • Moving globals.css to src\app\"
        Copy-Item -Path "src\app\en\globals.css" -Destination "src\app\globals.css" -Force
    } else {
        # Check if there's unique content to merge
        $sourceContent = Get-Content -Path "src\app\en\globals.css" -Raw
        $targetContent = Get-Content -Path "src\app\globals.css" -Raw
        
        if ($sourceContent -ne $targetContent) {
            Write-Output "  • Content differs between en/globals.css and globals.css"
            Write-Output "  • Creating backup as src\app\globals.css.bak"
            Copy-Item -Path "src\app\globals.css" -Destination "src\app\globals.css.bak" -Force
            Write-Output "  • Merging content (taking most recent)"
            Copy-Item -Path "src\app\en\globals.css" -Destination "src\app\globals.css" -Force
        } else {
            Write-Output "  • Content is identical, no action needed"
        }
    }
}

# Step 4: Rename the /en directory to prevent it from being used
if (Test-Path "src\app\en") {
    Write-Output "Renaming src\app\en to src\app\en.old to prevent routing conflicts"
    if (Test-Path "src\app\en.old") {
        Remove-Item -Path "src\app\en.old" -Recurse -Force
    }
    Rename-Item -Path "src\app\en" -NewName "en.old" -Force
}

Write-Output "=== Locale Migration Complete ==="
Write-Output "Run 'npm run build' to verify all issues are resolved"
