[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Write-Host "===================================="
Write-Host " Starting ConnLab MVP Dev Servers"
Write-Host "===================================="
Write-Host "Opening backend and frontend in separate PowerShell windows."

Start-Process powershell.exe -WindowStyle Normal -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    (Join-Path $repoRoot "scripts\run_backend.ps1")
)

Start-Process powershell.exe -WindowStyle Normal -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    (Join-Path $repoRoot "scripts\run_frontend.ps1")
)
