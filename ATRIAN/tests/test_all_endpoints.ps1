# ATRiAN Ethics as a Service (EaaS) API Comprehensive Test Script
# This script tests all the ATRiAN EaaS API endpoints to ensure proper functionality
# Version: 1.0
# Date: 2025-06-01

# Base URL for the API
$baseUrl = "http://localhost:8000"

# Function to display test results
function Display-TestResult {
    param (
        [string]$testName,
        [bool]$success,
        [object]$response,
        [string]$errorMessage = ""
    )
    
    if ($success) {
        Write-Host "✅ $testName - Success" -ForegroundColor Green
        Write-Host "   Response: $($response | ConvertTo-Json -Depth 3 -Compress)" -ForegroundColor Gray
    } else {
        Write-Host "❌ $testName - Failed" -ForegroundColor Red
        Write-Host "   Error: $errorMessage" -ForegroundColor Red
        if ($response) {
            Write-Host "   Response: $($response | ConvertTo-Json -Depth 3 -Compress)" -ForegroundColor Gray
        }
    }
    Write-Host ""
}

# Function to run a test and handle errors
function Run-Test {
    param (
        [string]$testName,
        [scriptblock]$testScript
    )
    
    Write-Host "Running test: $testName" -ForegroundColor Cyan
    try {
        & $testScript
    } catch {
        Display-TestResult -testName $testName -success $false -errorMessage $_.Exception.Message
    }
}

Write-Host "=== ATRiAN EaaS API Comprehensive Test Script ===" -ForegroundColor Magenta
Write-Host "Testing all endpoints for proper functionality and persistence" -ForegroundColor Magenta
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Magenta
Write-Host "=======================================================" -ForegroundColor Magenta
Write-Host ""

# Test 1: List Ethical Frameworks
Run-Test -testName "List Ethical Frameworks" -testScript {
    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/framework" -Method Get
    Display-TestResult -testName "List Ethical Frameworks" -success $true -response $response
}

# Test 2: Get Specific Framework
Run-Test -testName "Get Specific Framework (MQP)" -testScript {
    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/framework/mqp_v9_full_moon" -Method Get
    Display-TestResult -testName "Get Specific Framework (MQP)" -success $true -response $response
}

# Test 3: Ethical Evaluation
Run-Test -testName "Ethical Evaluation" -testScript {
    $evalPayload = @{
        action_description = "Implementing a facial recognition system for public surveillance"
        context = @{
            domain = "Public Security"
            data_sources = @("Security camera feeds", "Facial recognition database")
            purpose = "Developing security measures for a public transportation system"
            stakeholders = @("Transportation users", "Security personnel", "Public officials", "Privacy advocates")
        }
        options = @{
            detail_level = "comprehensive"
            include_alternatives = $true
        }
    } | ConvertTo-Json -Depth 5

    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/evaluate" -Method Post -Body $evalPayload -ContentType "application/json"
    $global:evaluationId = $response.evaluation_id
    Display-TestResult -testName "Ethical Evaluation" -success $true -response $response
    
    Write-Host "   Saved evaluation_id: $global:evaluationId for subsequent tests" -ForegroundColor Yellow
}

# Test 4: Get Explanation
Run-Test -testName "Get Explanation" -testScript {
    $explainPayload = @{
        evaluation_id = $global:evaluationId
        explanation_token = "ATRIAN-EXPLAIN-TOKEN-2025"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/explain" -Method Post -Body $explainPayload -ContentType "application/json"
    Display-TestResult -testName "Get Explanation" -success $true -response $response
}

# Test 5: Get Suggestions
Run-Test -testName "Get Suggestions" -testScript {
    $suggestPayload = @{
        evaluation_id = $global:evaluationId
        action_description = "Implementing a facial recognition system for public surveillance"
        ethical_concerns = @("Privacy invasion", "Potential for misuse", "Lack of consent")
        suggestion_count = 3
    } | ConvertTo-Json -Depth 3

    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/suggest" -Method Post -Body $suggestPayload -ContentType "application/json"
    Display-TestResult -testName "Get Suggestions" -success $true -response $response
}

# Test 6: Get Audit Logs
Run-Test -testName "Get Audit Logs" -testScript {
    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/audit" -Method Get
    Display-TestResult -testName "Get Audit Logs" -success $true -response $response
}

# Test 7: Get Audit Logs with Filtering
Run-Test -testName "Get Audit Logs with Filtering" -testScript {
    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/audit?action_type=evaluate&limit=5" -Method Get
    Display-TestResult -testName "Get Audit Logs with Filtering" -success $true -response $response
}

# Test 8: Create New Framework
Run-Test -testName "Create New Framework" -testScript {
    $frameworkId = "test_framework_$(Get-Random)"
    $frameworkPayload = @{
        name = "Test Ethical Framework"
        version = "1.0"
        description = "A test framework created by the test script"
        principles = @("Transparency", "Accountability", "Fairness")
        active = $true
        metadata = @{
            created_by = "test_script"
            purpose = "testing"
        }
    } | ConvertTo-Json -Depth 3

    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/framework" -Method Post -Body $frameworkPayload -ContentType "application/json"
    $global:testFrameworkId = $response.id
    Display-TestResult -testName "Create New Framework" -success $true -response $response
    
    Write-Host "   Created framework with ID: $global:testFrameworkId" -ForegroundColor Yellow
}

# Test 9: Update Framework
Run-Test -testName "Update Framework" -testScript {
    $updatePayload = @{
        description = "Updated test framework description"
        principles = @("Transparency", "Accountability", "Fairness", "Inclusivity")
        metadata = @{
            updated_by = "test_script"
            update_time = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        }
    } | ConvertTo-Json -Depth 3

    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/framework/$global:testFrameworkId" -Method Put -Body $updatePayload -ContentType "application/json"
    Display-TestResult -testName "Update Framework" -success $true -response $response
}

# Test 10: Delete Framework
Run-Test -testName "Delete Framework" -testScript {
    $response = Invoke-RestMethod -Uri "$baseUrl/ethics/framework/$global:testFrameworkId" -Method Delete
    Display-TestResult -testName "Delete Framework" -success $true -response $response
}

Write-Host "=== Test Summary ===" -ForegroundColor Magenta
Write-Host "All tests completed. Check the results above for any failures." -ForegroundColor Magenta
Write-Host "Remember to verify data persistence by restarting the API server and checking if data is still available." -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Magenta
