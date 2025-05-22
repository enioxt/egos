# EGOS Special Directory Removal Script
# Implements RULE-FILE-ACCESS-01 by using terminal commands for special directory handling

Write-Output "=== EGOS Special Directory Removal ==="
Write-Output "Removing directories with special characters..."

# Use cmd.exe to handle special characters in directory names
Write-Output "Removing [locale] directory using cmd.exe..."
cmd /c "if exist ""src\app\[locale]"" rmdir /s /q ""src\app\[locale]"""

# Verify the directory is gone
$dirs = Get-ChildItem -Path "src\app" -Force
if ($dirs | Where-Object { $_.Name -eq "[locale]" }) {
    Write-Output "WARNING: [locale] directory still exists. Trying alternative method..."
    
    # Create a temporary script to handle this
    $tempScript = "temp-remove.bat"
    @"
@echo off
cd src\app
if exist "[locale]" (
  echo Removing [locale] directory...
  rmdir /s /q "[locale]"
) else (
  echo [locale] directory not found
)
"@ | Out-File -FilePath $tempScript -Encoding ascii
    
    # Run the batch script
    Write-Output "Running batch script to remove directory..."
    cmd /c $tempScript
    
    # Clean up
    Remove-Item -Path $tempScript -Force
}

# Check if the directory is finally gone
$dirsAfter = Get-ChildItem -Path "src\app" -Force
if ($dirsAfter | Where-Object { $_.Name -eq "[locale]" }) {
    Write-Output "ERROR: Unable to remove [locale] directory. Please remove it manually."
} else {
    Write-Output "Successfully removed [locale] directory."
}

# Update next.config.js to explicitly disable i18n
if (Test-Path "next.config.js") {
    $configContent = Get-Content -Path "next.config.js" -Raw
    
    # Only modify if it doesn't already have i18n configuration
    if (-not ($configContent -match "i18n:")) {
        Write-Output "Updating next.config.js to explicitly disable i18n routing..."
        $configContent = $configContent -replace "const nextConfig = \{", "const nextConfig = {`n  // Explicitly disable i18n routing`n  i18n: null,"
        Set-Content -Path "next.config.js" -Value $configContent -Force
    }
}

Write-Output "=== Special Directory Removal Complete ==="
Write-Output "Run 'npm run build' to verify all issues are resolved"
