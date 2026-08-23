param(
    [string]$ReleaseFolder = "",
    [switch]$Launch,
    [ValidateRange(1, 120)][int]$StartupTimeoutSeconds = 20,
    [ValidateRange(1, 65535)][int]$Port = 8765
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

function Wait-ForConnLabResponse {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$ServerProcess,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $lastError = "no response"
    while ((Get-Date) -lt $deadline) {
        $ServerProcess.Refresh()
        if ($ServerProcess.HasExited) {
            throw "ConnLab_Server.exe exited before $Uri became available."
        }
        try {
            return Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 2
        }
        catch {
            $lastError = $_.Exception.Message
            Start-Sleep -Milliseconds 250
        }
    }
    throw "Timed out waiting for $Uri. Last error: $lastError"
}

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
$baseUrl = "http://127.0.0.1:$Port"
Write-Host "URL: $baseUrl/"

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

$existingListener = Get-NetTCPConnection -LocalAddress "127.0.0.1" -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existingListener) {
    throw "Port $Port is already in use. Stop the existing local ConnLab server before running the release smoke check."
}

$serverProcess = Start-Process -FilePath $serverExe `
    -ArgumentList @("--host", "127.0.0.1", "--port", "$Port") `
    -WorkingDirectory $resolvedRelease `
    -PassThru
$keepRunning = $Launch.IsPresent

try {
    $healthResponse = Wait-ForConnLabResponse `
        -Uri "$baseUrl/health" `
        -ServerProcess $serverProcess `
        -TimeoutSeconds $StartupTimeoutSeconds
    if ($healthResponse.Content -notmatch '"status"\s*:\s*"ok"') {
        throw "Packaged ConnLab health endpoint did not report status ok."
    }

    $pageResponse = Wait-ForConnLabResponse `
        -Uri "$baseUrl/" `
        -ServerProcess $serverProcess `
        -TimeoutSeconds $StartupTimeoutSeconds
    if ($pageResponse.Content -notmatch '<div id="root"></div>') {
        throw "Packaged ConnLab homepage did not return the browser application shell."
    }

    Write-Host "[OK] Packaged server, health endpoint, and homepage are reachable."
    if ($keepRunning) {
        Write-Host "Launching ConnLab in the default browser..."
        Start-Process -FilePath "$baseUrl/"
    }
}
finally {
    if (-not $keepRunning -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force
        Write-Host "Stopped temporary ConnLab smoke server."
    }
}
