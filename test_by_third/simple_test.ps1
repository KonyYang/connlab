# Simple Smoke Test - No complex setup needed

Write-Host "`n=== ConnLab Phase 7 Quick Test ===" -ForegroundColor Cyan
Write-Host ""

$BASE = "http://localhost:8000"

# Test 1: Project Lookup
Write-Host "[Test 1] Project Lookup..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$BASE/api/projects/lookup?query=test" -Method GET
    Write-Host "  PASS - Found $($result.Count) projects" -ForegroundColor Green
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Get a project ID and test sample summary
Write-Host "`n[Test 2] Sample Summary..." -ForegroundColor Yellow
try {
    $projects = Invoke-RestMethod -Uri "$BASE/api/projects/lookup?query=test" -Method GET
    if ($projects.Count -gt 0) {
        $projectId = $projects[0].project_id
        $result = Invoke-RestMethod -Uri "$BASE/api/projects/$projectId/sample-summary" -Method GET
        Write-Host "  PASS - Project: $($result.product_name)" -ForegroundColor Green
    } else {
        Write-Host "  SKIP - No projects found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Testing Summary
Write-Host "`n[Test 3] Testing Summary..." -ForegroundColor Yellow
try {
    $projects = Invoke-RestMethod -Uri "$BASE/api/projects/lookup?query=test" -Method GET
    if ($projects.Count -gt 0) {
        $projectId = $projects[0].project_id
        $result = Invoke-RestMethod -Uri "$BASE/api/projects/$projectId/testing-summary" -Method GET
        Write-Host "  PASS - Got testing summary" -ForegroundColor Green
    }
} catch {
    Write-Host "  FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Lifecycle Guard (should fail with 404)
Write-Host "`n[Test 4] Lifecycle Guard..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "$BASE/api/projects/nonexistent/ltr/readiness" -Method GET -ErrorAction Stop
    Write-Host "  FAIL - Should have returned 404" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "  PASS - Correctly rejected invalid project" -ForegroundColor Green
    } else {
        Write-Host "  FAIL - Wrong error: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "`n=== Tests Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more tests, open: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
