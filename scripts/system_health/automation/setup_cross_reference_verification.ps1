# EGOS Cross-Reference Weekly Verification Setup
# This script sets up automated weekly verification of cross-references in EGOS documentation
# Author: EGOS Development Team
# Date: 2025-05-18

# Configuration
$EGOS_ROOT = "C:\EGOS"
$SCRIPTS_DIR = "$EGOS_ROOT\scripts"
$REPORTS_DIR = "$EGOS_ROOT\reports\documentation\weekly_verification"
$TASK_NAME = "EGOS_Weekly_Cross_Reference_Check"
$LOG_FILE = "$EGOS_ROOT\logs\cross_reference_verification.log"

# Ensure directories exist
function EnsureDirectoryExists {
    param (
        [string]$Directory
    )
    
    if (-not (Test-Path -Path $Directory)) {
        Write-Host "Creating directory: $Directory"
        New-Item -Path $Directory -ItemType Directory -Force | Out-Null
    }
}

EnsureDirectoryExists -Directory $REPORTS_DIR
EnsureDirectoryExists -Directory "$EGOS_ROOT\logs"

# Create the verification script
$verificationScriptPath = "$SCRIPTS_DIR\maintenance\automation\run_weekly_verification.ps1"

$verificationScriptContent = @"
# EGOS Cross-Reference Weekly Verification
# This script runs weekly verification of cross-references in EGOS documentation
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Configuration
`$EGOS_ROOT = "$EGOS_ROOT"
`$SCRIPTS_DIR = "`$EGOS_ROOT\scripts"
`$REPORTS_DIR = "`$EGOS_ROOT\reports\documentation\weekly_verification"
`$LOG_FILE = "`$EGOS_ROOT\logs\cross_reference_verification.log"

# Start logging
Start-Transcript -Path "`$LOG_FILE" -Append

Write-Host "========================================================"
Write-Host "EGOS Weekly Cross-Reference Verification"
Write-Host "Started: `$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "========================================================"

try {
    # Change to scripts directory
    Set-Location -Path "`$SCRIPTS_DIR"
    
    # Create timestamp for report files
    `$timestamp = Get-Date -Format "yyyyMMddHHmmss"
    
    # Run verification for all documentation files
    Write-Host "Running verification for all documentation files..."
    python .\cross_reference\recent_files_verifier.py --base-path ..\ --hours 168 --extensions .md --report-dir "`$REPORTS_DIR\`$timestamp\all_docs"
    
    # Run verification for Python scripts
    Write-Host "Running verification for Python scripts..."
    python .\cross_reference\recent_files_verifier.py --base-path ..\ --hours 168 --extensions .py --report-dir "`$REPORTS_DIR\`$timestamp\scripts"
    
    # Generate summary report
    Write-Host "Generating summary report..."
    `$summaryPath = "`$REPORTS_DIR\`$timestamp\summary.md"
    
    @"
# EGOS Weekly Cross-Reference Verification Summary

**Date:** `$(Get-Date -Format 'yyyy-MM-dd')
**Time:** `$(Get-Date -Format 'HH:mm:ss')

## Reports Generated

- [Documentation Files Report](`$timestamp/all_docs/recent_files_report_`$timestamp.md)
- [Python Scripts Report](`$timestamp/scripts/recent_files_report_`$timestamp.md)

## Next Steps

1. Review the reports to identify files needing cross-references
2. Update critical files first (see <!-- TO_BE_REPLACED -->)
3. Run specific verification for files you've updated

## Automation Information

This report was generated automatically by the weekly cross-reference verification task.
"@ | Out-File -FilePath "`$summaryPath" -Encoding utf8
    
    # Create notification file
    `$notificationPath = "`$EGOS_ROOT\CROSS_REFERENCE_VERIFICATION_COMPLETE.md"
    
    @"
# Cross-Reference Verification Complete

The weekly cross-reference verification has been completed.

**Date:** `$(Get-Date -Format 'yyyy-MM-dd')
**Time:** `$(Get-Date -Format 'HH:mm:ss')

## Results

View the detailed reports at:
`$REPORTS_DIR\`$timestamp\summary.md

## Next Steps

1. Review the reports to identify files needing cross-references
2. Update critical files first (see [Cross-Reference Priority List](docs/governance/cross_reference_priority_list.md))
3. Run specific verification for files you've updated

*This notification will be automatically removed the next time verification runs.*
"@ | Out-File -FilePath "`$notificationPath" -Encoding utf8
    
    Write-Host "Verification complete. Reports saved to: `$REPORTS_DIR\`$timestamp"
    Write-Host "Notification file created at: `$notificationPath"
    
} catch {
    Write-Host "Error during verification: `$_" -ForegroundColor Red
    
    # Create error notification
    `$errorNotificationPath = "`$EGOS_ROOT\CROSS_REFERENCE_VERIFICATION_ERROR.md"
    
    @"
# Cross-Reference Verification Error

An error occurred during the weekly cross-reference verification.

**Date:** `$(Get-Date -Format 'yyyy-MM-dd')
**Time:** `$(Get-Date -Format 'HH:mm:ss')

## Error Details

```
`$_
```

Please check the log file for more details:
`$LOG_FILE

*This notification will be automatically removed the next time verification runs successfully.*
"@ | Out-File -FilePath "`$errorNotificationPath" -Encoding utf8
    
    Write-Host "Error notification created at: `$errorNotificationPath"
} finally {
    # End logging
    Stop-Transcript
}
"@

Write-Host "Creating verification script: $verificationScriptPath"
$verificationScriptContent | Out-File -FilePath $verificationScriptPath -Encoding utf8

# Register the scheduled task
Write-Host "Setting up scheduled task: $TASK_NAME"

# Remove existing task if it exists
if (Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue) {
    Write-Host "Removing existing task: $TASK_NAME"
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
}

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$verificationScriptPath`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 9am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

try {
    Register-ScheduledTask -TaskName $TASK_NAME -Action $action -Trigger $trigger -Settings $settings -Description "Runs weekly verification of cross-references in EGOS documentation"
    Write-Host "Scheduled task created successfully: $TASK_NAME"
    
    # Create documentation for the automation
    $automationDocPath = "$EGOS_ROOT\docs\reference\cross_reference_automation.md"
    
    $automationDocContent = @"
# Cross-Reference Verification Automation

This document describes the automated cross-reference verification system for EGOS documentation.

## Overview

The system automatically runs weekly verification of cross-references in EGOS documentation, generating reports and notifications to help maintain documentation integrity.

## Scheduled Task

A Windows Task Scheduler task has been created with the following properties:

- **Task Name:** $TASK_NAME
- **Schedule:** Weekly on Sunday at 9:00 AM
- **Script:** \`$verificationScriptPath\`
- **Action:** Runs cross-reference verification for all documentation and script files

## Reports

Reports are generated in the following location:
\`\`\`
$REPORTS_DIR\<timestamp>\
\`\`\`

Each verification run creates a new timestamped directory containing:

- **all_docs/** - Reports for all documentation files
- **scripts/** - Reports for Python script files
- **summary.md** - Summary report with links to detailed reports

## Notifications

After each verification run, a notification file is created in the EGOS root directory:

- **CROSS_REFERENCE_VERIFICATION_COMPLETE.md** - Created when verification completes successfully
- **CROSS_REFERENCE_VERIFICATION_ERROR.md** - Created if an error occurs during verification

These files contain information about the verification results and next steps.

## Logs

Detailed logs of each verification run are saved to:
\`\`\`
$LOG_FILE
\`\`\`

## Manual Execution

To run the verification manually:

1. Open PowerShell
2. Navigate to the EGOS scripts directory
3. Run the following command:

\`\`\`powershell
.\maintenance\automation\run_weekly_verification.ps1
\`\`\`

## Troubleshooting

If the scheduled task fails to run:

1. Check the log file for error messages
2. Verify that PowerShell execution policy allows script execution
3. Ensure the EGOS directory structure has not changed
4. Verify that the Python environment is properly configured

## Alternative Automation Options

### Git Hooks

For development workflow integration, you can set up Git hooks to run verification after pulling changes:

1. Create a post-merge hook in \`.git/hooks/\`
2. Add the following content:

\`\`\`bash
#!/bin/sh
echo "Running cross-reference verification..."
cd \$(git rev-parse --show-toplevel)/scripts
python ./cross_reference/recent_files_verifier.py --base-path ../ --hours 168 --report-dir ../reports/documentation/git_hooks
echo "Verification complete. See reports for details."
\`\`\`

### CI/CD Integration

For GitHub Actions integration, create a workflow file at \`.github/workflows/cross-reference-check.yml\`:

\`\`\`yaml
name: Weekly Cross-Reference Check

on:
  schedule:
    - cron: '0 9 * * 0'  # Run every Sunday at 9 AM
  workflow_dispatch:     # Allow manual triggering

jobs:
  verify-cross-references:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run verification
        run: |
          cd scripts
          python ./cross_reference/recent_files_verifier.py --base-path ../ --hours 168 --report-dir ../reports/documentation/github_actions
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: cross-reference-reports
          path: reports/documentation/github_actions
\`\`\`
"@

    EnsureDirectoryExists -Directory (Split-Path -Path $automationDocPath -Parent)
    $automationDocContent | Out-File -FilePath $automationDocPath -Encoding utf8
    Write-Host "Automation documentation created: $automationDocPath"
    
} catch {
    Write-Host "Error creating scheduled task: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Cross-reference verification automation setup complete!"
Write-Host "The verification will run weekly on Sunday at 9:00 AM."
Write-Host "Documentation has been created at: $automationDocPath"