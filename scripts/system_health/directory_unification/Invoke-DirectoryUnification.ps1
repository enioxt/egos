<#
.SYNOPSIS
    PowerShell wrapper for the Directory Unification Tool.

.DESCRIPTION
    This script provides a user-friendly PowerShell interface for the Directory Unification Tool,
    making it easier to invoke with tab completion and parameter validation.

.PARAMETER Keyword
    The keyword to search for related content.

.PARAMETER EgosRoot
    The root directory of the EGOS system. Defaults to the EGOS_ROOT environment variable.

.PARAMETER OutputDir
    The directory where reports will be saved. Defaults to the standard reports directory.

.PARAMETER MaxDepth
    The maximum depth to search for files. Defaults to 10.

.PARAMETER ExcludeDirs
    Directories to exclude from the search. Defaults to common directories to exclude.

.PARAMETER ExcludeFiles
    File patterns to exclude from the search. Defaults to common file patterns to exclude.

.PARAMETER DryRun
    If specified, no actual file operations will be performed.

.PARAMETER TestMode
    If specified, runs in test mode with limited file processing for faster execution.

.PARAMETER Verbose
    If specified, provides detailed output during execution.

.EXAMPLE
    .\Invoke-DirectoryUnification.ps1 -Keyword "test" -DryRun

.EXAMPLE
    .\Invoke-DirectoryUnification.ps1 -Keyword "documentation" -MaxDepth 5 -Verbose

.NOTES
    Author: Cascade
    Date: 2025-05-23
    Version: 1.0.0
    References:
        - C:\EGOS\scripts\maintenance\directory_unification\directory_unification_tool.py
        - C:\EGOS\docs\work_logs\WORK_2025_05_23_Directory_Unification_Implementation.md
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0, HelpMessage = "Keyword to search for related content")]
    [string]$Keyword,

    [Parameter(Mandatory = $false, HelpMessage = "Root directory of the EGOS system")]
    [string]$EgosRoot = $env:EGOS_ROOT,

    [Parameter(Mandatory = $false, HelpMessage = "Directory where reports will be saved")]
    [string]$OutputDir = "",

    [Parameter(Mandatory = $false, HelpMessage = "Maximum depth to search for files")]
    [int]$MaxDepth = 10,

    [Parameter(Mandatory = $false, HelpMessage = "Directories to exclude from the search")]
    [string[]]$ExcludeDirs = @("venv", ".git", "__pycache__", "node_modules", ".next", "dist", "build"),

    [Parameter(Mandatory = $false, HelpMessage = "File patterns to exclude from the search")]
    [string[]]$ExcludeFiles = @("*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.jar", "*.pack", "*.idx"),

    [Parameter(Mandatory = $false, HelpMessage = "If specified, no actual file operations will be performed")]
    [switch]$DryRun,

    [Parameter(Mandatory = $false, HelpMessage = "If specified, runs in test mode with limited file processing")]
    [switch]$TestMode,

    [Parameter(Mandatory = $false, HelpMessage = "If specified, provides detailed output during execution")]
    [switch]$Verbose
)

# Print banner
function Print-Banner {
    Write-Host ""
    Write-Host "    ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "    ║           Directory Unification Tool                     ║" -ForegroundColor Cyan
    Write-Host "    ║ EGOS Directory Unification Tool                          ║" -ForegroundColor Cyan
    Write-Host "    ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# Validate EGOS_ROOT
if (-not $EgosRoot) {
    Write-Host "Error: EGOS_ROOT environment variable is not set and no -EgosRoot parameter was provided." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $EgosRoot)) {
    Write-Host "Error: EGOS_ROOT directory does not exist: $EgosRoot" -ForegroundColor Red
    exit 1
}

# Construct command arguments
$PythonArgs = @(
    "$EgosRoot\scripts\maintenance\directory_unification\directory_unification_tool.py",
    "--keyword", "`"$Keyword`"",
    "--egos-root", "`"$EgosRoot`"",
    "--max-depth", $MaxDepth
)

# Add output directory if specified
if ($OutputDir) {
    $PythonArgs += "--output-dir"
    $PythonArgs += "`"$OutputDir`""
}

# Add exclude directories
if ($ExcludeDirs.Count -gt 0) {
    foreach ($dir in $ExcludeDirs) {
        $PythonArgs += "--exclude-dir"
        $PythonArgs += "`"$dir`""
    }
}

# Add exclude files
if ($ExcludeFiles.Count -gt 0) {
    foreach ($file in $ExcludeFiles) {
        $PythonArgs += "--exclude-file"
        $PythonArgs += "`"$file`""
    }
}

# Add dry run flag if specified
if ($DryRun) {
    $PythonArgs += "--dry-run"
}

# Add test mode flag if specified
if ($TestMode) {
    $PythonArgs += "--test-mode"
}

# Add verbose flag if specified
if ($Verbose) {
    $PythonArgs += "--verbose"
}

# Print banner
Print-Banner

# Print command information
Write-Host "Running Directory Unification Tool with the following parameters:" -ForegroundColor Yellow
Write-Host "  Keyword: $Keyword" -ForegroundColor Cyan
Write-Host "  EGOS Root: $EgosRoot" -ForegroundColor Cyan
Write-Host "  Max Depth: $MaxDepth" -ForegroundColor Cyan
if ($OutputDir) { Write-Host "  Output Directory: $OutputDir" -ForegroundColor Cyan }
Write-Host "  Exclude Directories: $($ExcludeDirs -join ', ')" -ForegroundColor Cyan
Write-Host "  Exclude Files: $($ExcludeFiles -join ', ')" -ForegroundColor Cyan
if ($DryRun) { Write-Host "  Dry Run: Enabled" -ForegroundColor Green }
if ($TestMode) { Write-Host "  Test Mode: Enabled" -ForegroundColor Green }
if ($Verbose) { Write-Host "  Verbose Output: Enabled" -ForegroundColor Green }
Write-Host ""

# Construct and display the command
$CommandString = "python $($PythonArgs -join ' ')"
Write-Host "Executing command:" -ForegroundColor Yellow
Write-Host $CommandString -ForegroundColor Gray
Write-Host ""

# Execute the command
try {
    # Change to EGOS root directory
    Push-Location $EgosRoot
    
    # Execute the Python script
    & python $PythonArgs
    
    # Check if the command was successful
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nDirectory Unification Tool completed successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "`nDirectory Unification Tool completed with errors. Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
}
catch {
    Write-Host "Error executing Directory Unification Tool: $_" -ForegroundColor Red
}
finally {
    # Return to original directory
    Pop-Location
}

# Print EGOS signature
Write-Host "`n✧༺❀༻∞ EGOS ∞༺❀༻✧" -ForegroundColor Cyan
