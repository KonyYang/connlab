[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===================================="
Write-Host " Running ConnLab Tests"
Write-Host "===================================="

if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

py -m pytest -p no:cacheprovider 2>&1 | Tee-Object -FilePath "logs/pytest_last.log"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed"
    exit 0
} else {
    Write-Host "❌ Tests failed"
    Write-Host "Failure log saved to logs/pytest_last.log"
    exit 1
}
