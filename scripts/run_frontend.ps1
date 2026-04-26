[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$frontendRoot = Join-Path $repoRoot "frontend"
Set-Location $frontendRoot

if (!(Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..."
    npm install
}

Write-Host "===================================="
Write-Host " Starting ConnLab Frontend"
Write-Host "===================================="
Write-Host "Frontend dev server will print the local URL."
Write-Host "API proxy target: http://127.0.0.1:8000"

npm run dev
