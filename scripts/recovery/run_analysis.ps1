# Script to run the file identification analysis
# This is a wrapper script that can be executed directly from PowerShell

# Set execution policy for this process only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Execute the identification script
Write-Host "Starting file identification analysis..." -ForegroundColor Cyan
Write-Host "This will identify files modified during the website recovery process." -ForegroundColor Cyan
Write-Host "Results will be saved to C:\EGOS\recovery_analysis\" -ForegroundColor Cyan
Write-Host ""

# Path to the identification script
$scriptPath = Join-Path $PSScriptRoot "identify_modified_files.ps1"

# Execute the script
& $scriptPath

Write-Host ""
Write-Host "Analysis complete. Please review the results in C:\EGOS\recovery_analysis\" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review the recovery_analysis_report.md file" -ForegroundColor Yellow
Write-Host "2. Identify critical files that need restoration" -ForegroundColor Yellow
Write-Host "3. Use restore_from_backup.ps1 to restore files as needed" -ForegroundColor Yellow

# Keep the window open
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")