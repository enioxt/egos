# EGOS Locale Migration Finalization Script
# Implements RULE-OPS-AUTONOMY-01 & Conscious Modularity principles

<#
@metadata
@title EGOS Locale Migration Finalization Script
@description Complete the migration from locale-based routing to root routing
@author EgosArchitect
@version 1.0.0
@date 2025-04-24
@status ⚡ Active
@references
- `mdc:website/middleware.ts`
- `mdc:website/src/app/page.tsx`
- `mdc:website/src/components/HomeContent.tsx`
#>

Write-Output "=== EGOS Locale Migration Finalization ==="
Write-Output "Completing migration from [locale] routing to root structure..."

# Step 1: Create backup of [locale] directory
if (Test-Path "src\app\[locale]") {
    Write-Output "Creating backup of [locale] directory..."
    if (Test-Path "src\app\locale-backup") {
        Remove-Item -Path "src\app\locale-backup" -Recurse -Force
    }
    Copy-Item -Path "src\app\[locale]" -Destination "src\app\locale-backup" -Recurse -Force
}

# Step 2: Copy essential files from [locale] to appropriate destinations
# Check if ClientProviders.tsx needs to be migrated
if (Test-Path "src\app\[locale]\ClientProviders.tsx") {
    Write-Output "Migrating ClientProviders.tsx to lib directory..."
    if (-not (Test-Path "src\lib")) {
        New-Item -Path "src\lib" -ItemType Directory -Force | Out-Null
    }
    Copy-Item -Path "src\app\[locale]\ClientProviders.tsx" -Destination "src\lib\ClientProviders.tsx" -Force
}

# Check if i18n.ts needs to be migrated
if (Test-Path "src\app\[locale]\i18n.ts") {
    Write-Output "Migrating i18n.ts to lib directory..."
    if (-not (Test-Path "src\lib")) {
        New-Item -Path "src\lib" -ItemType Directory -Force | Out-Null
    }
    Copy-Item -Path "src\app\[locale]\i18n.ts" -Destination "src\lib\i18n.ts" -Force
}

# Step 3: Rename [locale] directory to prevent it from being used in routing
if (Test-Path "src\app\[locale]") {
    Write-Output "Renaming [locale] directory to [locale].old..."
    if (Test-Path "src\app\[locale].old") {
        Remove-Item -Path "src\app\[locale].old" -Recurse -Force
    }
    Rename-Item -Path "src\app\[locale]" -NewName "[locale].old" -Force
}

# Step 4: Update references in layout.tsx if needed
if (Test-Path "src\app\layout.tsx") {
    Write-Output "Checking for references to [locale] components in layout.tsx..."
    $content = Get-Content -Path "src\app\layout.tsx" -Raw
    $newContent = $content -replace "import .* from ['\"]\./\[locale\]/ClientProviders", "import ClientProviders from '@/lib/ClientProviders"
    $newContent = $newContent -replace "import .* from ['\"]\./\[locale\]/i18n", "import { i18n } from '@/lib/i18n"
    
    if ($content -ne $newContent) {
        Write-Output "Updating imports in layout.tsx..."
        Set-Content -Path "src\app\layout.tsx" -Value $newContent -Force
    }
}

Write-Output "=== Locale Migration Finalization Complete ==="
Write-Output "Run 'npm run build' to verify all issues are resolved"
