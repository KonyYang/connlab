param(
    [string]$ReleaseFolder = "",
    [switch]$Launch
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if (-not $ReleaseFolder) {
    $releaseRoot = Join-Path $repoRoot "dist_release"
    if (-not (Test-Path $releaseRoot)) {
        throw "dist_release folder not found. Build a release first."
    }
    $latest = Get-ChildItem -LiteralPath $releaseRoot -Directory -Filter "ConnLab_Web_*" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latest) {
        throw "No ConnLab_Web release folder found under dist_release."
    }
    $ReleaseFolder = $latest.FullName
}

$resolvedRelease = (Resolve-Path $ReleaseFolder).Path
$serverExe = Join-Path $resolvedRelease "ConnLab_Server.exe"
$startScript = Join-Path $resolvedRelease "Start_ConnLab.bat"
$operatorReadme = Join-Path $resolvedRelease "README_FOR_OPERATOR.md"
$releaseNotes = Join-Path $resolvedRelease "RELEASE_NOTES.md"
$internalDir = Join-Path $resolvedRelease "_internal"

Write-Host "===================================="
Write-Host " ConnLab Browser Release Smoke Check"
Write-Host "===================================="
Write-Host "Release folder: $resolvedRelease"
Write-Host "URL: http://127.0.0.1:8765/"

if (-not (Test-Path $serverExe)) {
    throw "Missing ConnLab_Server.exe"
}
if (-not (Test-Path $startScript)) {
    throw "Missing Start_ConnLab.bat"
}
if (-not (Test-Path $operatorReadme)) {
    throw "Missing README_FOR_OPERATOR.md"
}
if (-not (Test-Path $releaseNotes)) {
    throw "Missing RELEASE_NOTES.md"
}
if (-not (Test-Path $internalDir)) {
    throw "Missing _internal folder"
}

Write-Host "[OK] Browser release folder shape is valid."
Write-Host "Start script: Start_ConnLab.bat"
Write-Host "Server EXE: ConnLab_Server.exe"

if ($Launch) {
    Write-Host "Launching ConnLab local browser server..."
    Start-Process -FilePath $startScript -WorkingDirectory $resolvedRelease
}
