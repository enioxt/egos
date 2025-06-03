# ATRiAN EaaS API Testing Script - Explain and Suggest Endpoints
# This script tests the /ethics/explain and /ethics/suggest endpoints
# to verify persistence and proper error handling

Write-Host "ATRiAN EaaS API Testing - Explain and Suggest Endpoints" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Base URL for the API
$baseUrl = "http://127.0.0.1:8000"

# First, create an evaluation to get an evaluation_id and explanation_token
Write-Host "`n[SETUP] Creating initial evaluation to get tokens" -ForegroundColor Green
$evaluationRequest = @{
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
    $evalResponse = Invoke-RestMethod -Uri "$baseUrl/ethics/evaluate" -Method Post -ContentType "application/json" -Body ($evaluationRequest | ConvertTo-Json -Depth 5)
    Write-Host "SUCCESS: Created evaluation" -ForegroundColor Green
    $evaluationId = $evalResponse.evaluation_id
    $explanationToken = $evalResponse.explanation_token
    Write-Host "Evaluation ID: $evaluationId" -ForegroundColor Magenta
    Write-Host "Explanation Token: $explanationToken" -ForegroundColor Magenta
}
catch {
    Write-Host "ERROR: Failed to create initial evaluation" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit
}

# Test Case 1: Request explanation with valid token
Write-Host "`n[TEST CASE 1] Request explanation with valid token" -ForegroundColor Green
$explainRequest = @{
    evaluation_id = $evaluationId
    explanation_token = $explanationToken
    detail_level = "comprehensive"
}

try {
    $explainResponse = Invoke-RestMethod -Uri "$baseUrl/ethics/explain" -Method Post -ContentType "application/json" -Body ($explainRequest | ConvertTo-Json)
    Write-Host "SUCCESS: Received explanation" -ForegroundColor Green
    Write-Host "Explanation ID: $($explainResponse.evaluation_id)" -ForegroundColor Yellow
    Write-Host "Principles Applied: $($explainResponse.principles_applied -join ', ')" -ForegroundColor Yellow
    Write-Host "Timestamp: $($explainResponse.timestamp)" -ForegroundColor Yellow
}
catch {
    Write-Host "ERROR: Explanation request failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test Case 2: Request explanation with invalid token
Write-Host "`n[TEST CASE 2] Request explanation with invalid token" -ForegroundColor Green
$invalidExplainRequest = @{
    evaluation_id = $evaluationId
    explanation_token = "invalid_token_123"
    detail_level = "comprehensive"
}

try {
    $invalidExplainResponse = Invoke-RestMethod -Uri "$baseUrl/ethics/explain" -Method Post -ContentType "application/json" -Body ($invalidExplainRequest | ConvertTo-Json)
    Write-Host "ERROR: Request with invalid token should have failed" -ForegroundColor Red
}
catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401 -or $_.Exception.Response.StatusCode.value__ -eq 403) {
        Write-Host "SUCCESS: Properly rejected invalid token with $($_.Exception.Response.StatusCode.value__) status code" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Unexpected error status code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

# Test Case 3: Request suggestions based on evaluation ID
Write-Host "`n[TEST CASE 3] Request suggestions based on evaluation ID" -ForegroundColor Green
$suggestRequest = @{
    evaluation_id = $evaluationId
    suggestion_count = 3
}

try {
    $suggestResponse = Invoke-RestMethod -Uri "$baseUrl/ethics/suggest" -Method Post -ContentType "application/json" -Body ($suggestRequest | ConvertTo-Json)
    Write-Host "SUCCESS: Received suggestions" -ForegroundColor Green
    Write-Host "Request ID: $($suggestResponse.request_id)" -ForegroundColor Yellow
    Write-Host "Number of alternatives: $($suggestResponse.alternatives.Count)" -ForegroundColor Yellow
    Write-Host "Original evaluation ID: $($suggestResponse.original_evaluation_id)" -ForegroundColor Yellow
}
catch {
    Write-Host "ERROR: Suggestion request failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test Case 4: Request suggestions without evaluation ID
Write-Host "`n[TEST CASE 4] Request suggestions without evaluation ID" -ForegroundColor Green
$directSuggestRequest = @{
    action_description = "Implementing a facial recognition system for public surveillance"
    context = @{
        domain = "Public Security"
        purpose = "Developing security measures for a public transportation system"
    }
    ethical_concerns = @(
        "Privacy invasion",
        "Potential discrimination"
    )
    suggestion_count = 2
}

try {
    $directSuggestResponse = Invoke-RestMethod -Uri "$baseUrl/ethics/suggest" -Method Post -ContentType "application/json" -Body ($directSuggestRequest | ConvertTo-Json -Depth 5)
    Write-Host "SUCCESS: Received direct suggestions" -ForegroundColor Green
    Write-Host "Request ID: $($directSuggestResponse.request_id)" -ForegroundColor Yellow
    Write-Host "Number of alternatives: $($directSuggestResponse.alternatives.Count)" -ForegroundColor Yellow
}
catch {
    Write-Host "ERROR: Direct suggestion request failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test Case 5: Verify persistence by restarting server and retrieving explanation
Write-Host "`n[TEST CASE 5] Persistence verification instructions" -ForegroundColor Green
Write-Host "To verify persistence:" -ForegroundColor Yellow
Write-Host "1. Restart the API server" -ForegroundColor Yellow
Write-Host "2. Run the following command to retrieve the explanation:" -ForegroundColor Yellow
Write-Host "   Invoke-RestMethod -Uri '$baseUrl/ethics/explain' -Method Post -ContentType 'application/json' -Body '{\"evaluation_id\":\"$evaluationId\",\"explanation_token\":\"$explanationToken\",\"detail_level\":\"comprehensive\"}'" -ForegroundColor Cyan

Write-Host "`nTesting complete!" -ForegroundColor Cyan
