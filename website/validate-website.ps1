# Validation Script for EGOS @website Subsystem
# Ref: KOIOS-CODE-001, CORUJA-TEST-001

<#
@metadata
@title EGOS Website Validation Script
@description Validates the EGOS website build, lint, and provides a manual testing checklist
@author EgosArchitect
@version 1.0.0
@date 2025-04-24
@status ⏳ In Progress
@references
- `mdc:website/package.json`
- `mdc:website/next.config.js`
- `mdc:docs/testing/validation_strategy.mdc`
#>

Write-Output "=== EGOS Website Validation ==="

# Step 1: Run Build
Write-Output "Running npm run build..."
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed! Aborting validation."
    exit 1
} else {
    Write-Output "Build successful."
}

# Step 2: Run Lint (Adjust command if using Ruff directly)
Write-Output "Running npm run lint..."
npm run lint
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Linting issues found. Please review."
    # Continue validation, but flag the issue
} else {
    Write-Output "Linting passed."
}

# Step 3: Manual Smoke Test Reminder
Write-Output "---------------------------------------"
Write-Output "Automated checks complete."
Write-Output "Reminder: Perform manual smoke tests:"
Write-Output " - Load Homepage (/)"
Write-Output " - Check System Explorer (if applicable)"
Write-Output " - Check Roadmap page (if applicable)"
Write-Output " - Verify no console errors in browser."
Write-Output "---------------------------------------"

Write-Output "Validation process finished."
exit 0 # Exit with 0 even if lint fails, as build passed. Handle lint separately.
