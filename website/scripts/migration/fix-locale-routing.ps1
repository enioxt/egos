# EGOS Locale Routing Fix Script
# Implements RULE-OPS-AUTONOMY-01 & Conscious Modularity principles

Write-Output "=== EGOS Locale Routing Fix ==="
Write-Output "Migrating from [locale] routing to root structure..."

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
    Write-Output "Renaming [locale] directory to locale-old..."
    if (Test-Path "src\app\locale-old") {
        Remove-Item -Path "src\app\locale-old" -Recurse -Force
    }
    Rename-Item -Path "src\app\[locale]" -NewName "locale-old" -Force
}

Write-Output "=== Locale Routing Fix Complete ==="
Write-Output "Run 'npm run build' to verify all issues are resolved"
