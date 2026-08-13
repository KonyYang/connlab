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
$boardPath = Join-Path $repoRoot "docs\task_board.md"
$boardText = [System.IO.File]::ReadAllText($boardPath, [System.Text.Encoding]::UTF8)
$controlBlock = [regex]::Match(
    $boardText,
    '(?s)<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->\s*```json\s*(.*?)\s*```\s*<!-- CONNLAB_EXECUTION_CONTROL_END -->'
)
if ($controlBlock.Success) {
    $control = $controlBlock.Groups[1].Value | ConvertFrom-Json
}
if ($null -ne $control -and
    $control.schema -eq "connlab.personal-serial-control" -and
    $control.version -eq 2 -and
    $control.mode -eq "personal_serial") {
    [ordered]@{
        code = "BLOCKED_LEGACY_MODE_FROZEN"
        allowed = $false
        changed = $false
        zero_write = $true
        command = $Command
        reason = "Controlled Lane V2 is frozen while Personal Serial Workflow V2 is authoritative."
    } | ConvertTo-Json -Compress
    exit 2
}
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
