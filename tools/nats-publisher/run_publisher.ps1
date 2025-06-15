# EGOS Activity Publisher Runner
# This script starts the NATS server and the EGOS activity publisher
# Following EGOS principles of Operational Elegance and Conscious Modularity

# Check if Python and required packages are installed
Write-Host "Checking Python environment..." -ForegroundColor Cyan

# Verify watchdog package is installed
$watchdogInstalled = python -c "import watchdog" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing watchdog package..." -ForegroundColor Yellow
    pip install watchdog
}

# Verify nats-py package is installed
$natsInstalled = python -c "import nats" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing nats-py package..." -ForegroundColor Yellow
    pip install nats-py
}

# Define paths
$egosDirPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$natsServerPath = Join-Path $egosDirPath "tools\nats-server"
$natsServerScript = Join-Path $natsServerPath "download-and-run-nats.ps1"
$publisherScript = Join-Path $PSScriptRoot "egos_activity_publisher.py"

# Create a function to check if a port is in use
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$Port.*LISTENING"
    return $connections.Count -gt 0
}

# Check if NATS server is already running
$natsRunning = Test-PortInUse -Port 4222
if ($natsRunning) {
    Write-Host "NATS server is already running on port 4222" -ForegroundColor Green
} else {
    # Start NATS server in a new PowerShell window
    Write-Host "Starting NATS server..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit -File `"$natsServerScript`"" -WindowStyle Normal
    
    # Wait for NATS server to start
    $attempts = 0
    $maxAttempts = 10
    while (-not (Test-PortInUse -Port 4222) -and $attempts -lt $maxAttempts) {
        Write-Host "Waiting for NATS server to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 1
        $attempts++
    }
    
    if (Test-PortInUse -Port 4222) {
        Write-Host "NATS server started successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to start NATS server. Please start it manually using $natsServerScript" -ForegroundColor Red
        exit 1
    }
}

# Start the EGOS activity publisher
Write-Host "Starting EGOS activity publisher..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the publisher" -ForegroundColor Yellow
Write-Host "Publisher will monitor file changes and publish events to NATS topics:" -ForegroundColor Cyan
Write-Host "  - egos.sparc.tasks" -ForegroundColor White
Write-Host "  - egos.llm.logs" -ForegroundColor White
Write-Host "  - egos.propagation.log" -ForegroundColor White
Write-Host ""
Write-Host "To see the events in the dashboard:" -ForegroundColor Cyan
Write-Host "1. Start the dashboard: python -m streamlit run C:\EGOS\apps\dashboard\core\streamlit_app.py" -ForegroundColor White
Write-Host "2. Enable 'Use Live Data' toggle in the dashboard" -ForegroundColor White
Write-Host ""

# Run the publisher
python $publisherScript

# Note: The script will continue running until manually terminated with Ctrl+C