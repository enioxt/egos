#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Runs all EGOS validation scripts to ensure codebase integrity.

.DESCRIPTION
    This script discovers and executes all validation scripts in the EGOS codebase.
    It follows the naming convention of `validate_*.py` to identify validators.
    Each validator is run sequentially, and the script reports overall success/failure.

.NOTES
    File Name      : run_validators.ps1
    Author         : EGOS System
    Prerequisite   : PowerShell 5.1 or later
    Version        : 1.0.0
    Date           : 2025-06-11

.EXAMPLE
    ./scripts/ci/run_validators.ps1
    
.EXAMPLE
    ./scripts/ci/run_validators.ps1 -BasePath "C:/EGOS"

Cross-References:
    - .windsurfrules → RULE-CI-VALIDATION
    - scripts/validation/* (all validation scripts)
    - docs/standards/KOIOS_PDD_Standard.md (PDD validation reference)
    - docs/planning/PromptVault_System_Design.md (PromptVault validation reference)
#>

param (
    [string]$BasePath = "C:/EGOS"
)

# ANSI color codes for output formatting
$GREEN = "`e[32m"
$RED = "`e[31m"
$YELLOW = "`e[33m"
$RESET = "`e[0m"
$BOLD = "`e[1m"

Write-Host "$BOLD=== EGOS Validation Suite ===$RESET"
Write-Host "Base path: $BasePath"
Write-Host "Starting validation at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "-----------------------------------"

# Track overall success/failure
$allPassed = $true
$validatorCount = 0
$passedCount = 0
$failedCount = 0

# Find all validation scripts
$validationScripts = Get-ChildItem -Path "$BasePath/scripts/validation" -Filter "validate_*.py" -Recurse

if ($validationScripts.Count -eq 0) {
    Write-Host "${YELLOW}Warning: No validation scripts found!$RESET"
    exit 0
}

# Run each validator
foreach ($script in $validationScripts) {
    $validatorCount++
    $scriptName = $script.Name
    Write-Host "Running $scriptName... " -NoNewline
    
    # Execute the validator
    $output = & python $script.FullName --base-path $BasePath 2>&1
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        $passedCount++
        Write-Host "${GREEN}PASSED$RESET"
    }
    else {
        $failedCount++
        $allPassed = $false
        Write-Host "${RED}FAILED$RESET"
        Write-Host $output
        Write-Host ""
    }
}

# Summary
Write-Host "-----------------------------------"
Write-Host "Validation Summary:"
Write-Host "  Total validators: $validatorCount"
Write-Host "  ${GREEN}Passed: $passedCount$RESET"
if ($failedCount -gt 0) {
    Write-Host "  ${RED}Failed: $failedCount$RESET"
}

if ($allPassed) {
    Write-Host "${GREEN}${BOLD}All validators passed successfully!$RESET"
    exit 0
}
else {
    Write-Host "${RED}${BOLD}Some validators failed. See details above.$RESET"
    exit 1
}
