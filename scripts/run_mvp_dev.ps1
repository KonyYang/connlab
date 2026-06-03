param(
    [switch]$WithDesktopShell
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

Write-Host "===================================="
Write-Host " Starting ConnLab MVP Dev Servers"
Write-Host "===================================="
Write-Host "Opening backend and frontend in separate PowerShell windows."
if ($WithDesktopShell) {
    Write-Host "Desktop shell will open in a third PowerShell window."
}

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

if ($WithDesktopShell) {
    Start-Process powershell.exe -WindowStyle Normal -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (Join-Path $repoRoot "scripts\run_desktop_shell.ps1")
    )
}
