param(
    [string]$ReleaseDate = (Get-Date -Format "yyyyMMddHHmm"),
    [string]$VersionSuffix = "",
    [switch]$SkipTests,
    [switch]$SkipFrontendBuild
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

function Read-ProjectVersion {
    $pyproject = Get-Content "pyproject.toml" -Encoding UTF8
    foreach ($line in $pyproject) {
        if ($line -match '^version\s*=\s*"([^"]+)"') {
            return $Matches[1]
        }
    }
    throw "Cannot find project version in pyproject.toml"
}

function Assert-CommandAvailable {
    param([string]$Name, [string]$InstallHint)
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "$Name is required. $InstallHint"
    }
}

$ProjectVersion = Read-ProjectVersion
$ReleaseName = "ConnLab_${ReleaseDate}_v${ProjectVersion}${VersionSuffix}"
$releaseRoot = Join-Path $repoRoot "dist_release"
$releaseFolder = Join-Path $releaseRoot $ReleaseName
$pyinstallerDist = Join-Path $repoRoot "dist"
$pyinstallerBuild = Join-Path $repoRoot "build"
$pyinstallerOutput = Join-Path $pyinstallerDist $ReleaseName

Write-Host "===================================="
Write-Host " Building ConnLab Desktop Release"
Write-Host "===================================="
Write-Host "Release: $ReleaseName"

Assert-CommandAvailable "npm" "Install Node.js for developer builds."

if (-not $SkipTests) {
    Write-Host "[1/5] Running focused release tests"
    $previousPytestDisablePluginAutoload = $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    py -m pytest tests\unit\test_desktop_packaged_runtime_paths.py tests\unit\test_desktop_packaged_static.py tests\unit\test_desktop_release_scripts.py -q -p no:cacheprovider
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = $previousPytestDisablePluginAutoload
    if ($LASTEXITCODE -ne 0) {
        throw "Release tests failed."
    }
}
else {
    Write-Host "[1/5] Skipping tests"
}

if (-not $SkipFrontendBuild) {
    Write-Host "[2/5] Building frontend"
    Push-Location "frontend"
    try {
        npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend build failed."
        }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "[2/5] Skipping frontend build"
}

if (-not (Test-Path "frontend\dist\index.html")) {
    throw "frontend\dist\index.html not found. Run frontend build before packaging."
}

Write-Host "[3/5] Checking PyInstaller"
py -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller is required. Install developer release dependencies before building."
}

Write-Host "[4/5] Running PyInstaller"
if (Test-Path $pyinstallerBuild) {
    Remove-Item -LiteralPath $pyinstallerBuild -Recurse -Force
}
if (Test-Path $pyinstallerOutput) {
    Remove-Item -LiteralPath $pyinstallerOutput -Recurse -Force
}
$env:CONNLAB_RELEASE_NAME = $ReleaseName
py -m PyInstaller packaging\connlab_desktop.spec --clean --noconfirm --distpath dist --workpath build
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller packaging failed."
}

Write-Host "[5/5] Preparing release folder"
if (-not (Test-Path $releaseRoot)) {
    New-Item -ItemType Directory -Path $releaseRoot | Out-Null
}
if (Test-Path $releaseFolder) {
    Remove-Item -LiteralPath $releaseFolder -Recurse -Force
}
Move-Item -LiteralPath $pyinstallerOutput -Destination $releaseFolder
$releaseConfig = Join-Path $releaseFolder "config"
New-Item -ItemType Directory -Path $releaseConfig | Out-Null
Copy-Item -LiteralPath "connlab.admin.example.toml" -Destination (Join-Path $releaseConfig "connlab.admin.example.toml") -Force

$versionedExe = Join-Path $releaseFolder "$ReleaseName.exe"
$stableExe = Join-Path $releaseFolder "ConnLab.exe"
if (-not (Test-Path $versionedExe)) {
    throw "Expected versioned EXE not found: $versionedExe"
}
Copy-Item -LiteralPath $versionedExe -Destination $stableExe -Force
Copy-Item -LiteralPath "packaging\README_FOR_OPERATOR.md" -Destination (Join-Path $releaseFolder "README_FOR_OPERATOR.md") -Force
Copy-Item -LiteralPath "packaging\RELEASE_NOTES.md" -Destination (Join-Path $releaseFolder "RELEASE_NOTES.md") -Force

Write-Host ""
Write-Host "[OK] ConnLab release folder is ready:"
Write-Host $releaseFolder
Write-Host ""
Write-Host "Copy the whole folder to the operator computer and run ConnLab.exe."
