[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===================================="
Write-Host " Running ConnLab Frontend Build"
Write-Host "===================================="

if (!(Test-Path "frontend\package.json")) {
    Write-Host "[ERROR] frontend\package.json not found. Run this script from the repository root."
    exit 1
}

Push-Location "frontend"
try {
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Frontend build failed"
        exit $LASTEXITCODE
    }

    Write-Host "[OK] Frontend build passed"
    exit 0
}
finally {
    Pop-Location
}
