# Test script for the ATRiAN EaaS API /ethics/audit endpoint
# This script tests the audit log retrieval functionality

Write-Host "Testing ATRiAN EaaS API /ethics/audit endpoint..." -ForegroundColor Cyan

# Base URL for the API
$baseUrl = "http://localhost:8000"

# Test the audit endpoint with default parameters
Write-Host "`nTest 1: Get audit logs with default parameters" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$baseUrl/ethics/audit" -Method Get
Write-Host "Response received with $($response.count) audit logs"
Write-Host "Timestamp: $($response.timestamp)"

# Test with filtering by action_type
Write-Host "`nTest 2: Get audit logs filtered by action_type=evaluate" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$baseUrl/ethics/audit?action_type=evaluate" -Method Get
Write-Host "Response received with $($response.count) evaluation audit logs"

# Test with limit parameter
Write-Host "`nTest 3: Get audit logs with limit=5" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$baseUrl/ethics/audit?limit=5" -Method Get
Write-Host "Response received with $($response.count) audit logs (limited to 5)"

# Test with pagination
Write-Host "`nTest 4: Get audit logs with pagination (offset=5, limit=5)" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$baseUrl/ethics/audit?offset=5&limit=5" -Method Get
Write-Host "Response received with $($response.count) audit logs (offset 5, limit 5)"

Write-Host "`nAudit endpoint testing completed successfully!" -ForegroundColor Cyan
