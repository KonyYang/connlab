[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Write-Host "===================================="
Write-Host " Starting ConnLab Backend"
Write-Host "===================================="
Write-Host "API: http://127.0.0.1:8000"
Write-Host "Health: http://127.0.0.1:8000/health"

py -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
