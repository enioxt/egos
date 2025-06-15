#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

<#
.SYNOPSIS
    Download and run NATS server for EGOS Dashboard real-time data integration.
.DESCRIPTION
    This script downloads the latest NATS server release for Windows and runs it with default configuration.
    Part of the EGOS Dashboard Real-Time Data Integration strategy (DBP-P1.1.1).
.NOTES
    Author: EGOS System
    Version: 1.0
    Date: 2025-06-03
    Aligned with: Master Quantum Prompt (MQP v9.0 "Full Moon Blueprint")
    EGOS_PRINCIPLE: Conscious Modularity, Systemic Cartography
#>

# Configuration
$natsVersion = "v2.10.11"  # Update this to the latest version as needed
$natsDownloadUrl = "https://github.com/nats-io/nats-server/releases/download/$natsVersion/nats-server-$natsVersion-windows-amd64.zip"
$natsDirectory = "$PSScriptRoot"
$natsZipPath = "$natsDirectory\nats-server.zip"
$natsExecutablePath = "$natsDirectory\nats-server-$natsVersion-windows-amd64\nats-server.exe"

# Create log directory if it doesn't exist
$logDirectory = "$natsDirectory\logs"
if (-not (Test-Path $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory | Out-Null
    Write-Host "Created log directory: $logDirectory"
}

$logFile = "$logDirectory\nats-server-$(Get-Date -Format 'yyyy-MM-dd').log"

# Function to download NATS server if not already present
function Download-NatsServer {
    if (-not (Test-Path $natsExecutablePath)) {
        Write-Host "NATS server executable not found. Downloading from $natsDownloadUrl..."
        
        # Download the zip file
        Invoke-WebRequest -Uri $natsDownloadUrl -OutFile $natsZipPath
        
        # Extract the zip file
        Expand-Archive -Path $natsZipPath -DestinationPath $natsDirectory -Force
        
        # Verify the executable exists
        if (Test-Path $natsExecutablePath) {
            Write-Host "NATS server downloaded and extracted successfully."
        } else {
            Write-Error "Failed to extract NATS server executable. Please check the download URL and try again."
            exit 1
        }
    } else {
        Write-Host "NATS server executable already exists at $natsExecutablePath"
    }
}

# Function to run NATS server
function Run-NatsServer {
    Write-Host "Starting NATS server on default port 4222..."
    Write-Host "Log file: $logFile"
    Write-Host "Press Ctrl+C to stop the server."
    
    # Run NATS server with basic configuration
    & $natsExecutablePath --addr 0.0.0.0 --port 4222 --http_port 8222 --debug | Tee-Object -FilePath $logFile
}

# Main execution
try {
    Write-Host "=== EGOS NATS Server Launcher ==="
    Write-Host "This script is part of the EGOS Dashboard Real-Time Data Integration strategy."
    Write-Host "It will download (if needed) and run the NATS server required for real-time messaging."
    
    Download-NatsServer
    Run-NatsServer
} catch {
    Write-Error "An error occurred: $_"
    exit 1
}