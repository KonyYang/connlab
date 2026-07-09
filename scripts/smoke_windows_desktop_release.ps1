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
    $latest = Get-ChildItem -LiteralPath $releaseRoot -Directory |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latest) {
        throw "No release folder found under dist_release."
    }
    $ReleaseFolder = $latest.FullName
}

$resolvedRelease = (Resolve-Path $ReleaseFolder).Path
$stableExe = Join-Path $resolvedRelease "ConnLab.exe"
$versionedExe = Get-ChildItem -LiteralPath $resolvedRelease -File -Filter "ConnLab_*_v*.exe" |
    Select-Object -First 1
$operatorReadme = Join-Path $resolvedRelease "README_FOR_OPERATOR.md"
$releaseNotes = Join-Path $resolvedRelease "RELEASE_NOTES.md"
$internalDir = Join-Path $resolvedRelease "_internal"

Write-Host "===================================="
Write-Host " ConnLab Release Smoke Check"
Write-Host "===================================="
Write-Host "Release folder: $resolvedRelease"

if (-not (Test-Path $stableExe)) {
    throw "Missing stable ConnLab.exe"
}
if (-not $versionedExe) {
    throw "Missing versioned ConnLab_<date>_v<version>.exe"
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

Write-Host "[OK] Release folder shape is valid."
Write-Host "Versioned EXE: $($versionedExe.Name)"
Write-Host "Stable EXE: ConnLab.exe"

if ($Launch) {
    Write-Host "Launching ConnLab for manual smoke..."
    Start-Process -FilePath $stableExe -WorkingDirectory $resolvedRelease
}
