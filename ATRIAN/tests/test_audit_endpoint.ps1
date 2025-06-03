# Test script for ATRiAN EaaS API Audit Endpoint
# This script tests the /ethics/audit endpoint with various filtering and pagination parameters
# It follows the EGOS testing standards and provides detailed output for validation

$baseUrl = "http://localhost:8000"
$apiEndpoint = "/ethics/audit"
$fullUrl = $baseUrl + $apiEndpoint

Write-Host "===== ATRiAN EaaS API - Audit Endpoint Test =====" -ForegroundColor Cyan
Write-Host "Testing endpoint: $fullUrl" -ForegroundColor Cyan
Write-Host "Started at: $(Get-Date)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Function to make API calls and display results
function Invoke-AuditTest {
    param (
        [string]$TestName,
        [string]$Url,
        [hashtable]$QueryParams = @{}
    )
    
    Write-Host "`n>> Test: $TestName" -ForegroundColor Green
    
    # Build the query string
    $queryString = ""
    if ($QueryParams.Count -gt 0) {
        $queryParts = @()
        foreach ($key in $QueryParams.Keys) {
            if ($null -ne $QueryParams[$key]) {
                $queryParts += "$key=$([System.Web.HttpUtility]::UrlEncode($QueryParams[$key]))"
            }
        }
        $queryString = "?" + ($queryParts -join "&")
    }
    
    $fullTestUrl = $Url + $queryString
    Write-Host "Request URL: $fullTestUrl" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri $fullTestUrl -Method Get -ContentType "application/json"
        
        # Display response summary
        Write-Host "Response Status: Success" -ForegroundColor Green
        Write-Host "Total Logs: $($response.total_count)" -ForegroundColor Cyan
        Write-Host "Page: $($response.page)" -ForegroundColor Cyan
        Write-Host "Page Size: $($response.page_size)" -ForegroundColor Cyan
        Write-Host "Has More: $($response.has_more)" -ForegroundColor Cyan
        
        # Display log entries (limited to first 3 for readability)
        $logCount = [Math]::Min($response.logs.Count, 3)
        if ($logCount -gt 0) {
            Write-Host "`nSample Log Entries (showing $logCount of $($response.logs.Count)):" -ForegroundColor Magenta
            for ($i = 0; $i -lt $logCount; $i++) {
                $log = $response.logs[$i]
                Write-Host "  Log #$($i+1):" -ForegroundColor Yellow
                Write-Host "    ID: $($log.log_id)" -ForegroundColor White
                Write-Host "    Timestamp: $($log.timestamp)" -ForegroundColor White
                Write-Host "    Action: $($log.action_type)" -ForegroundColor White
                Write-Host "    Endpoint: $($log.endpoint_called)" -ForegroundColor White
                Write-Host "    User: $($log.user_id)" -ForegroundColor White
            }
            
            if ($response.logs.Count -gt 3) {
                Write-Host "  ... and $($response.logs.Count - 3) more logs" -ForegroundColor Gray
            }
        } else {
            Write-Host "`nNo logs found matching the criteria." -ForegroundColor Yellow
        }
        
        return $response
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host "StatusCode: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response Body: $responseBody" -ForegroundColor Red
        }
        
        return $null
    }
}

# Test 1: Basic retrieval (default parameters)
Invoke-AuditTest -TestName "Basic Retrieval (Default Parameters)" -Url $fullUrl

# Test 2: Limit results to 5
Invoke-AuditTest -TestName "Limited Results (5 logs)" -Url $fullUrl -QueryParams @{
    limit = 5
}

# Test 3: Pagination (second page of 5 results)
Invoke-AuditTest -TestName "Pagination (Second Page)" -Url $fullUrl -QueryParams @{
    limit = 5
    offset = 5
}

# Test 4: Filter by action type
Invoke-AuditTest -TestName "Filter by Action Type (evaluate_ethics)" -Url $fullUrl -QueryParams @{
    action_type = "evaluate_ethics"
    limit = 10
}

# Test 5: Filter by user
Invoke-AuditTest -TestName "Filter by User (anonymous)" -Url $fullUrl -QueryParams @{
    user_id = "anonymous"
    limit = 10
}

# Test 6: Date range filter (last 24 hours)
$yesterday = (Get-Date).AddDays(-1).ToString("o")
$now = (Get-Date).ToString("o")

Invoke-AuditTest -TestName "Date Range Filter (Last 24 Hours)" -Url $fullUrl -QueryParams @{
    start_date = $yesterday
    end_date = $now
    limit = 10
}

# Test 7: Combined filters
Invoke-AuditTest -TestName "Combined Filters" -Url $fullUrl -QueryParams @{
    action_type = "retrieve_audit_logs"
    user_id = "anonymous"
    limit = 10
}

# Test 8: Edge case - very large limit
Invoke-AuditTest -TestName "Edge Case - Large Limit" -Url $fullUrl -QueryParams @{
    limit = 1000
}

# Test 9: Edge case - zero limit (should default to API default)
Invoke-AuditTest -TestName "Edge Case - Zero Limit" -Url $fullUrl -QueryParams @{
    limit = 0
}

Write-Host "`n===== Audit Endpoint Test Complete =====" -ForegroundColor Cyan
Write-Host "Completed at: $(Get-Date)" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan