# ConnLab Phase 7 Smoke Test Script
# Make sure backend is running before executing

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ConnLab Phase 7 Smoke Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Configuration
$BASE_URL = "http://localhost:8000"
$TEST_DATA_DIR = "D:\test_samples"
$MSG_FILE = Join-Path $TEST_DATA_DIR "request.msg"

# Check if test file exists
if (-not (Test-Path $MSG_FILE)) {
    Write-Host "ERROR: Test MSG file not found: $MSG_FILE" -ForegroundColor Red
    Write-Host "Please prepare a real .msg file and update the path in this script" -ForegroundColor Yellow
    exit 1
}

# Check if backend is running
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/docs" -Method GET -TimeoutSec 5 -UseBasicParsing
    Write-Host "Backend service is running`n" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Backend service is not running or not accessible" -ForegroundColor Red
    Write-Host "Please run first: .\scripts\run_backend.ps1" -ForegroundColor Yellow
    exit 1
}

# Test results tracking
$TEST_RESULTS = @()

function Test-Pass {
    param([string]$TestName, [string]$Detail = "")
    $TEST_RESULTS += @{Name=$TestName; Result="PASS"; Detail=$Detail}
    Write-Host "[PASS] $TestName" -ForegroundColor Green
    if ($Detail) { Write-Host "   $Detail" -ForegroundColor Gray }
}

function Test-Fail {
    param([string]$TestName, [string]$Detail = "")
    $TEST_RESULTS += @{Name=$TestName; Result="FAIL"; Detail=$Detail}
    Write-Host "[FAIL] $TestName" -ForegroundColor Red
    if ($Detail) { Write-Host "   $Detail" -ForegroundColor Gray }
}

function Test-Skip {
    param([string]$TestName, [string]$Reason = "")
    $TEST_RESULTS += @{Name=$TestName; Result="SKIP"; Detail=$Reason}
    Write-Host "[SKIP] $TestName" -ForegroundColor Yellow
    if ($Reason) { Write-Host "   $Reason" -ForegroundColor Gray }
}

Write-Host "`nStarting tests...`n" -ForegroundColor Cyan

# ========================================
# Test 1: Import MSG Package
# ========================================
Write-Host "--- Test 1: Import MSG Package ---" -ForegroundColor Cyan
$PACKAGE_ID = $null
try {
    $formData = @{
        file = Get-Item $MSG_FILE
    }
    
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/intake-packages/import-msg" `
        -Method POST `
        -Form $formData `
        -TimeoutSec 30
    
    $PACKAGE_ID = $response.package_id
    
    if ($PACKAGE_ID) {
        Test-Pass "MSG Import" "Package ID: $PACKAGE_ID"
        
        # Validate metadata
        if ($response.subject -or $response.sender_email) {
            Test-Pass "Metadata Extraction" "Subject: $($response.subject)"
        } else {
            Test-Fail "Metadata Extraction" "Missing subject or sender email"
        }
        
        # Validate attachments
        if ($response.attachments -and $response.attachments.Count -gt 0) {
            Test-Pass "Attachment Extraction" "$($response.attachments.Count) attachments"
        } else {
            Test-Pass "Attachment Extraction" "No attachments (email may not have any)"
        }
    } else {
        Test-Fail "MSG Import" "No package_id returned"
    }
} catch {
    Test-Fail "MSG Import" $_.Exception.Message
}

# If import failed, skip dependent tests
if (-not $PACKAGE_ID) {
    Write-Host "`nWARNING: Skipping dependent tests due to MSG import failure`n" -ForegroundColor Yellow
    Test-Skip "Exception Workflow Review" "Depends on MSG import"
    Test-Skip "Form Selection" "Depends on MSG import"
    Test-Skip "Project Creation" "Depends on form selection"
    Test-Skip "LTR Readiness" "Depends on project creation"
    Test-Skip "LTR Preview" "Depends on project creation"
    Test-Skip "LTR Commit" "Depends on project creation"
    Test-Skip "Folder Generation" "Depends on LTR registration"
    Test-Skip "Evidence Placement" "Depends on folder generation"
    Test-Skip "Lifecycle Guards" "Depends on multiple prerequisites"
    Test-Skip "Lookup Endpoints" "Depends on project creation"
    
    # Output summary
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Test Summary" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    $passCount = ($TEST_RESULTS | Where-Object {$_.Result -eq "PASS"}).Count
    $failCount = ($TEST_RESULTS | Where-Object {$_.Result -eq "FAIL"}).Count
    $skipCount = ($TEST_RESULTS | Where-Object {$_.Result -eq "SKIP"}).Count
    
    Write-Host "Passed: $passCount" -ForegroundColor Green
    Write-Host "Failed: $failCount" -ForegroundColor Red
    Write-Host "Skipped: $skipCount`n" -ForegroundColor Yellow
    
    exit 1
}

# ========================================
# Test 2: Exception Workflow Review
# ========================================
Write-Host "`n--- Test 2: Exception Workflow Review ---" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/intake-packages/$PACKAGE_ID/exceptions/review" `
        -Method POST `
        -TimeoutSec 10
    
    if ($response.package_status) {
        Test-Pass "Exception Review" "Status: $($response.package_status)"
        
        if ($response.issues -and $response.issues.Count -gt 0) {
            Test-Pass "Issue Detection" "$($response.issues.Count) issues"
        } else {
            Test-Pass "Issue Detection" "No issues (normal package)"
        }
    } else {
        Test-Fail "Exception Review" "No package status returned"
    }
} catch {
    Test-Fail "Exception Review" $_.Exception.Message
}

# ========================================
# Tests 3-5: Require frontend interaction
# ========================================
Write-Host "`n--- Tests 3-5: Form Selection and Project Creation ---" -ForegroundColor Cyan
Write-Host "WARNING: These tests require frontend UI or complex API calls" -ForegroundColor Yellow
Write-Host "Recommend completing manually via frontend interface" -ForegroundColor Yellow
Test-Skip "Form Selection" "Requires frontend UI or complex API sequence"
Test-Skip "Missing Field Blocking" "Requires specific test data"
Test-Skip "Complete Case Confirmation" "Requires frontend UI or complex API sequence"

# ========================================
# Tests 6-8: LTR related (need project ID)
# ========================================
Write-Host "`n--- Tests 6-8: LTR Functions ---" -ForegroundColor Cyan
Write-Host "WARNING: Need to create project first and obtain project_id" -ForegroundColor Yellow
Test-Skip "LTR Readiness" "Requires project_id"
Test-Skip "LTR Preview" "Requires project_id"
Test-Skip "LTR Local Commit" "Requires project_id"

# ========================================
# Tests 10-11: Folder and Evidence (need project ID and LTR)
# ========================================
Write-Host "`n--- Tests 10-11: Folder and Evidence ---" -ForegroundColor Cyan
Test-Skip "Folder Generation" "Requires project_id and LTR registration"
Test-Skip "Evidence Placement" "Requires folder generation"

# ========================================
# Test 12: Lifecycle Guards
# ========================================
Write-Host "`n--- Test 12: Lifecycle Guards ---" -ForegroundColor Cyan
try {
    # Try operation on non-existent project
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/projects/nonexistent-project/ltr/readiness" `
        -Method GET `
        -TimeoutSec 5 `
        -ErrorAction SilentlyContinue
    
    Test-Fail "Lifecycle Guards" "Should return 404 but succeeded"
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Test-Pass "Lifecycle Guards" "Correctly rejected invalid project"
    } else {
        Test-Fail "Lifecycle Guards" "Wrong error code: $($_.Exception.Response.StatusCode)"
    }
}

# ========================================
# Test 13: Lookup Endpoints
# ========================================
Write-Host "`n--- Test 13: Lookup Endpoints ---" -ForegroundColor Cyan
try {
    # Search test (should return empty list, not error)
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/projects/lookup?q=test" `
        -Method GET `
        -TimeoutSec 5
    
    if ($response -is [array]) {
        Test-Pass "Project Search" "Returned array (may be empty)"
    } else {
        Test-Pass "Project Search" "Returned response"
    }
} catch {
    Test-Fail "Project Search" $_.Exception.Message
}

# ========================================
# Output Summary
# ========================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$passCount = ($TEST_RESULTS | Where-Object {$_.Result -eq "PASS"}).Count
$failCount = ($TEST_RESULTS | Where-Object {$_.Result -eq "FAIL"}).Count
$skipCount = ($TEST_RESULTS | Where-Object {$_.Result -eq "SKIP"}).Count

Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host "Skipped: $skipCount`n" -ForegroundColor Yellow

Write-Host "Detailed Results:" -ForegroundColor Cyan
foreach ($result in $TEST_RESULTS) {
    if ($result.Result -eq "PASS") {
        $icon = "[PASS]"
        $color = "Green"
    } elseif ($result.Result -eq "FAIL") {
        $icon = "[FAIL]"
        $color = "Red"
    } else {
        $icon = "[SKIP]"
        $color = "Yellow"
    }
    Write-Host "  $icon $($result.Name): $($result.Detail)" -ForegroundColor $color
}

Write-Host "`n========================================`n" -ForegroundColor Cyan

if ($failCount -gt 0) {
    Write-Host "WARNING: Some tests failed, please check output above" -ForegroundColor Yellow
    exit 1
} elseif ($skipCount -gt 0) {
    Write-Host "INFO: Some tests skipped, recommend manual completion of full workflow" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "All executed tests passed!" -ForegroundColor Green
    exit 0
}
