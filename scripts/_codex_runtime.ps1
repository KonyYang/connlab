function Invoke-CodexCli {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Prompt
    )

    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

    $runtimeHome = Join-Path (Get-Location) "tmp\codex-runtime-home"
    New-Item -ItemType Directory -Path $runtimeHome -Force | Out-Null

    $defaultCodexHome = Join-Path $env:USERPROFILE ".codex"
    $authSource = Join-Path $defaultCodexHome "auth.json"
    $configSource = Join-Path $defaultCodexHome "config.toml"

    if (Test-Path $authSource) {
        Copy-Item $authSource (Join-Path $runtimeHome "auth.json") -Force
    } else {
        Write-Host "❌ Codex auth file not found: $authSource"
        return 1
    }

    if (Test-Path $configSource) {
        Copy-Item $configSource (Join-Path $runtimeHome "config.toml") -Force
    }

    $certPath = $null
    try {
        $certPath = (py -c "import certifi; print(certifi.where())").Trim()
    } catch {
        $certPath = $null
    }

    $env:CODEX_HOME = $runtimeHome
    if ($certPath -and (Test-Path $certPath)) {
        $env:SSL_CERT_FILE = $certPath
        $env:CURL_CA_BUNDLE = $certPath
    }

    $codexCmd = Join-Path $env:APPDATA "npm\codex.cmd"
    if (!(Test-Path $codexCmd)) {
        Write-Host "❌ codex.cmd not found: $codexCmd"
        return 1
    }

    $Prompt | & $codexCmd exec --skip-git-repo-check --cd (Get-Location).Path -
    return $LASTEXITCODE
}
