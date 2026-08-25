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

function Assert-BrowserFrontendReleaseGuards {
    param([Parameter(Mandatory = $true)][string]$AssetRoot)

    if (-not (Test-Path $AssetRoot)) {
        throw "Frontend assets not found: $AssetRoot"
    }
    $requiredText = "Export Matrix"
    $requiredMatches = Select-String -Path (Join-Path $AssetRoot "*.js") -Pattern $requiredText -SimpleMatch -Encoding UTF8 -ErrorAction SilentlyContinue
    if (-not $requiredMatches) {
        throw "Required frontend capability is missing: Export Matrix"
    }
    $forbiddenText = "Import Matrix will replace the current source session"
    $matches = Select-String -Path (Join-Path $AssetRoot "*.js") -Pattern $forbiddenText -SimpleMatch -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($matches) {
        throw "Frontend build still contains the old native Import Matrix confirm text. Rebuild from the TASK_350C source before packaging."
    }
}

function Invoke-TimedStep {
    param(
        [string]$Label,
        [scriptblock]$Action
    )
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $actionError = $null
    try {
        & $Action
    }
    catch {
        $actionError = $_
    }
    finally {
        try {
            $stopwatch.Stop()
            Write-Host ("[time] {0}: {1:n1}s" -f $Label, $stopwatch.Elapsed.TotalSeconds)
        }
        catch {
            if ($null -eq $actionError) {
                throw
            }
        }
    }
    if ($null -ne $actionError) {
        throw $actionError
    }
}

$ProjectVersion = Read-ProjectVersion
$ReleaseName = "ConnLab_Web_${ReleaseDate}_v${ProjectVersion}${VersionSuffix}"
$ExeName = "ConnLab_Server"
$releaseRoot = Join-Path $repoRoot "dist_release"
$releaseFolder = Join-Path $releaseRoot $ReleaseName
$pyinstallerDist = Join-Path $repoRoot "dist"
$pyinstallerBuild = Join-Path $repoRoot "build"
$pyinstallerOutput = Join-Path $pyinstallerDist $ExeName

Write-Host "===================================="
Write-Host " Building ConnLab Browser Release"
Write-Host "===================================="
Write-Host "Release: $ReleaseName"
Write-Host "URL: http://127.0.0.1:8765/"

Assert-CommandAvailable "npm" "Install Node.js for developer builds."

if ($SkipFrontendBuild) {
    throw "SkipFrontendBuild is disabled for browser releases. A fresh frontend build is required."
}

if (-not $SkipTests) {
    Invoke-TimedStep "[1/5] Running focused release tests" {
        Write-Host "[1/5] Running focused release tests"
        $previousPytestDisablePluginAutoload = $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD
        $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
        try {
            $pytestBaseTemp = Join-Path $repoRoot "tmp\pytest-browser-release"
            py -m pytest `
                tests\unit\test_desktop_packaged_runtime_paths.py `
                tests\unit\test_desktop_packaged_static.py `
                tests\unit\test_desktop_release_scripts.py `
                tests\unit\test_logging.py `
                tests\unit\test_support_diagnostic_bundle_service.py `
                tests\integration\test_support_diagnostics_api.py `
                tests\unit\test_word_numbering.py `
                tests\unit\test_test_record_template_resource.py `
                tests\unit\test_matrix_record_sample_quantity.py `
                tests\unit\test_matrix_editor_llcr_cr_record_projection.py `
                tests\unit\test_confirmed_matrix_llcr_cr_record_projection.py `
                tests\unit\test_draft_measurement_plan_workbook_projection.py `
                tests\integration\test_matrix_editor_test_record_generation_api.py `
                tests\unit\test_llcr_cr_specialized_record_workbook_gateway.py `
                tests\integration\test_matrix_editor_llcr_cr_record_generation_api.py `
                tests\integration\test_llcr_cr_specialized_record_workbook_api.py `
                -q -p no:cacheprovider --basetemp $pytestBaseTemp
            if ($LASTEXITCODE -ne 0) {
                throw "Release tests failed."
            }
        }
        finally {
            $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = $previousPytestDisablePluginAutoload
        }
    }
}
else {
    Write-Host "[1/5] Skipping tests"
}

Invoke-TimedStep "[2/5] Building frontend" {
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

if (-not (Test-Path "frontend\dist\index.html")) {
    throw "frontend\dist\index.html not found. Run frontend build before packaging."
}
Assert-BrowserFrontendReleaseGuards -AssetRoot (Join-Path $repoRoot "frontend\dist\assets")

Invoke-TimedStep "[3/5] Checking PyInstaller" {
    Write-Host "[3/5] Checking PyInstaller"
    py -m PyInstaller --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller is required. Install developer release dependencies before building."
    }
}

Invoke-TimedStep "[4/5] Running PyInstaller" {
    Write-Host "[4/5] Running PyInstaller"
    if (Test-Path $pyinstallerBuild) {
        Remove-Item -LiteralPath $pyinstallerBuild -Recurse -Force
    }
    if (Test-Path $pyinstallerOutput) {
        Remove-Item -LiteralPath $pyinstallerOutput -Recurse -Force
    }
    $env:CONNLAB_RELEASE_NAME = $ExeName
    py -m PyInstaller packaging\connlab_browser_server.spec --clean --noconfirm --distpath dist --workpath build
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller packaging failed."
    }
}

Invoke-TimedStep "[5/5] Preparing release folder" {
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

    $stableExe = Join-Path $releaseFolder "ConnLab_Server.exe"
    if (-not (Test-Path $stableExe)) {
        throw "Expected ConnLab_Server.exe not found: $stableExe"
    }
    $packagedFrontend = Join-Path $releaseFolder "_internal\frontend_dist"
    if (-not (Test-Path $packagedFrontend)) {
        New-Item -ItemType Directory -Path $packagedFrontend | Out-Null
    }
    Copy-Item -Path "frontend\dist\*" -Destination $packagedFrontend -Recurse -Force
    # Guard the path the packaged server actually serves at runtime.
    # In one-folder PyInstaller mode datas land under <releaseFolder>\_internal,
    # and runtime_paths.default_frontend_dist() resolves to
    # <releaseFolder>\_internal\frontend_dist via sys._MEIPASS.
    Assert-BrowserFrontendReleaseGuards -AssetRoot (Join-Path $packagedFrontend "assets")
    Copy-Item -LiteralPath "packaging\Start_ConnLab.bat" -Destination (Join-Path $releaseFolder "Start_ConnLab.bat") -Force
    Copy-Item -LiteralPath "packaging\README_FOR_BROWSER_OPERATOR.md" -Destination (Join-Path $releaseFolder "README_FOR_OPERATOR.md") -Force
    Copy-Item -LiteralPath "packaging\RELEASE_NOTES_BROWSER.md" -Destination (Join-Path $releaseFolder "RELEASE_NOTES.md") -Force

    $gitCommit = git rev-parse HEAD
    if (-not $?) {
        $gitCommit = "unknown"
    }
    else {
        $gitCommit = $gitCommit.Trim()
    }
    $releaseManifest = [ordered]@{
        release_name = $ReleaseName
        version = $ProjectVersion
        git_commit = $gitCommit
        built_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        server_sha256 = (Get-FileHash -LiteralPath $stableExe -Algorithm SHA256).Hash.ToLowerInvariant()
    } | ConvertTo-Json
    $manifestPath = Join-Path $releaseFolder "_internal\release_manifest.json"
    [System.IO.File]::WriteAllText(
        $manifestPath,
        $releaseManifest,
        [System.Text.UTF8Encoding]::new($false)
    )
}

Write-Host ""
Write-Host "[OK] ConnLab browser release folder is ready:"
Write-Host $releaseFolder
Write-Host ""
Write-Host "Copy the whole folder to the operator computer and run Start_ConnLab.bat."
Write-Host "ConnLab will open at http://127.0.0.1:8765/."
