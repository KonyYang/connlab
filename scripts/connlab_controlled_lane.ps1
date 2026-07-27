[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "scan",
        "route-plan",
        "registry-status",
        "recover",
        "worktree-preflight",
        "integration-preflight",
        "retire-preflight",
        "prepare-dispatch",
        "mark-invocation-started",
        "record-action-result",
        "record-callback",
        "ack-dispatch",
        "advance-state"
    )]
    [string]$Command,

    [Parameter(Mandatory = $true)]
    [string]$RequestJson,

    [string]$RegistryRoot,

    [switch]$AllowTestRegistryRoot,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..")).TrimEnd("\")
$arguments = @(
    "-m",
    "scripts.connlab_controlled_lane.cli",
    $Command,
    "--request-json",
    $RequestJson
)
if ($DryRun) {
    $arguments += "--dry-run"
}
if (-not [string]::IsNullOrWhiteSpace($RegistryRoot)) {
    $arguments += @("--registry-root", $RegistryRoot)
}
if ($AllowTestRegistryRoot) {
    $arguments += "--allow-test-registry-root"
}

Push-Location $repoRoot
try {
    & py @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
