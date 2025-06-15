# ATRiAN EaaS API Testing Script - Evaluate Endpoint
# This script tests the /ethics/evaluate endpoint with different scenarios
# to verify persistence and proper error handling

Write-Host "ATRiAN EaaS API Testing - Evaluate Endpoint" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Base URL for the API
$baseUrl = "http://127.0.0.1:8000"

# Test Case 1: Standard evaluation request
Write-Host "`n[TEST CASE 1] Standard evaluation request" -ForegroundColor Green
$testCase1 = @{
    action = "Implementing a facial recognition system for public surveillance"
    context = @{
        domain = "Public Security"
        purpose = "Developing security measures for a public transportation system"
        stakeholders = @(
            "Transportation users",
            "Security personnel", 
            "Public officials",
            "Privacy advocates"
        )
        data_sources = @(
            "Security camera feeds",
            "Facial recognition database"
        )
    }
    options = @{
        detail_level = "comprehensive"
        include_alternatives = $true
    }
}

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/ethics/evaluate" -Method Post -ContentType "application/json" -Body ($testCase1 | ConvertTo-Json -Depth 5)
    Write-Host "SUCCESS: Received valid response" -ForegroundColor Green
    Write-Host "Ethical Score: $($response1.ethical_score)" -ForegroundColor Yellow
    Write-Host "Compliant: $($response1.compliant)" -ForegroundColor Yellow
    Write-Host "Concerns: $($response1.concerns.Count)" -ForegroundColor Yellow
    Write-Host "Recommendations: $($response1.recommendations.Count)" -ForegroundColor Yellow
    
    # Save the evaluation ID for persistence testing
    $evaluationId = $response1.evaluation_id
    $explanationToken = $response1.explanation_token
    Write-Host "Evaluation ID: $evaluationId" -ForegroundColor Magenta
    Write-Host "Explanation Token: $explanationToken" -ForegroundColor Magenta
}
catch {
    Write-Host "ERROR: Test Case 1 failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test Case 2: Evaluation with sensitive data
Write-Host "`n[TEST CASE 2] Evaluation with sensitive data" -ForegroundColor Green
$testCase2 = @{
    action = "Collecting and analyzing health records for research"
    context = @{
        domain = "Healthcare"
        purpose = "Medical research to improve treatment outcomes"
        stakeholders = @(
            "Patients",
            "Researchers",
            "Healthcare providers"
        )
        data_sources = @(
            "sensitive_data_patient_records",
            "anonymized_treatment_outcomes"
        )
    }
    options = @{
        detail_level = "comprehensive"
        include_alternatives = $true
    }
}

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/ethics/evaluate" -Method Post -ContentType "application/json" -Body ($testCase2 | ConvertTo-Json -Depth 5)
    Write-Host "SUCCESS: Received valid response" -ForegroundColor Green
    Write-Host "Ethical Score: $($response2.ethical_score)" -ForegroundColor Yellow
    Write-Host "Compliant: $($response2.compliant)" -ForegroundColor Yellow
    Write-Host "Concerns: $($response2.concerns.Count)" -ForegroundColor Yellow
    Write-Host "Recommendations: $($response2.recommendations.Count)" -ForegroundColor Yellow
}
catch {
    Write-Host "ERROR: Test Case 2 failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test Case 3: Evaluation with surveillance domain
Write-Host "`n[TEST CASE 3] Evaluation with surveillance domain" -ForegroundColor Green
$testCase3 = @{
    action = "Implementing automated monitoring of employee productivity"
    context = @{
        domain = "surveillance"
        purpose = "Workplace efficiency monitoring"
        stakeholders = @(
            "Employees",
            "Management",
            "HR department"
        )
        data_sources = @(
            "computer_activity_logs",
            "application_usage_metrics",
            "productivity_data"
        )
    }
    options = @{
        detail_level = "comprehensive"
        include_alternatives = $true
    }
}

try {
    $response3 = Invoke-RestMethod -Uri "$baseUrl/ethics/evaluate" -Method Post -ContentType "application/json" -Body ($testCase3 | ConvertTo-Json -Depth 5)
    Write-Host "SUCCESS: Received valid response" -ForegroundColor Green
    Write-Host "Ethical Score: $($response3.ethical_score)" -ForegroundColor Yellow
    Write-Host "Compliant: $($response3.compliant)" -ForegroundColor Yellow
    Write-Host "Concerns: $($response3.concerns.Count)" -ForegroundColor Yellow
    Write-Host "Recommendations: $($response3.recommendations.Count)" -ForegroundColor Yellow
}
catch {
    Write-Host "ERROR: Test Case 3 failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test Case 4: Malformed request (missing required fields)
Write-Host "`n[TEST CASE 4] Malformed request (missing required fields)" -ForegroundColor Green
$testCase4 = @{
    # Missing 'action' field
    context = @{
        domain = "General"
    }
}

try {
    $response4 = Invoke-RestMethod -Uri "$baseUrl/ethics/evaluate" -Method Post -ContentType "application/json" -Body ($testCase4 | ConvertTo-Json -Depth 5)
    Write-Host "ERROR: Test should have failed but succeeded" -ForegroundColor Red
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 422) {
        Write-Host "SUCCESS: Properly rejected malformed request with 422 status code" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Unexpected error status code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host "`nTesting complete!" -ForegroundColor Cyan
