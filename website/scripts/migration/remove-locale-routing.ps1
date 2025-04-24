# EGOS Locale Routing Removal Script
# Implements RULE-OPS-AUTONOMY-01 by batching related file structure operations

Write-Output "=== EGOS Locale Routing Removal ==="
Write-Output "Completely removing [locale] routing structure..."

# Step 1: Check if we need to backup any important files first
$backupDir = "src\app\locale-backup-final"
if (-not (Test-Path $backupDir)) {
    New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
}

# Backup important files if they exist
$filesToBackup = @(
    "src\app\[locale]\ClientProviders.tsx",
    "src\app\[locale]\i18n.ts"
)

foreach ($file in $filesToBackup) {
    if (Test-Path $file) {
        $fileName = Split-Path -Leaf $file
        Write-Output "Backing up $fileName..."
        Copy-Item -Path $file -Destination "$backupDir\$fileName" -Force
    }
}

# Step 2: Completely remove the [locale] directory
if (Test-Path "src\app\[locale]") {
    Write-Output "Removing [locale] directory..."
    Remove-Item -Path "src\app\[locale]" -Recurse -Force
}

# Step 3: Check for any other locale-related directories and remove them
$localeRelatedDirs = @(
    "src\app\locale-old",
    "src\app\en.old"
)

foreach ($dir in $localeRelatedDirs) {
    if (Test-Path $dir) {
        Write-Output "Removing $dir..."
        Remove-Item -Path $dir -Recurse -Force
    }
}

# Step 4: Create a next.config.js that explicitly disables i18n routing if it doesn't already have this
if (Test-Path "next.config.js") {
    $configContent = Get-Content -Path "next.config.js" -Raw
    
    # Only modify if it doesn't already have i18n configuration
    if (-not ($configContent -match "i18n:")) {
        Write-Output "Updating next.config.js to explicitly disable i18n routing..."
        $configContent = $configContent -replace "const nextConfig = \{", "const nextConfig = {`n  // Explicitly disable i18n routing`n  i18n: null,"
        Set-Content -Path "next.config.js" -Value $configContent -Force
    }
}

Write-Output "=== Locale Routing Removal Complete ==="
Write-Output "Run 'npm run build' to verify all issues are resolved"
