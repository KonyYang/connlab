[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Write-Host "===================================="
Write-Host " Starting ConnLab Desktop Shell"
Write-Host "===================================="
Write-Host "Desktop shell loads: http://localhost:5173"
Write-Host "Start backend and frontend first, or run .\scripts\run_mvp_dev.ps1 -WithDesktopShell"

py -m backend.desktop.shell
