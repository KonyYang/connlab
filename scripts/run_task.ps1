[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Task,

    [Parameter(Mandatory = $true)]
    [string]$RequestJson,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedBoardSha256,

    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,

    [switch]$Preview,

    [switch]$ControlledLaneV2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$helper = Join-Path $PSScriptRoot "connlab_personal_task.py"

if ($ControlledLaneV2) {
    $snapshotText = @(& py $helper inspect --repo-root $RepositoryRoot --json) -join "`n"
    if ($LASTEXITCODE -ne 0) {
        Write-Output $snapshotText
        exit $LASTEXITCODE
    }
    $result = $snapshotText | ConvertFrom-Json
    $result.code = "BLOCKED_LEGACY_MODE_FROZEN"
    $result.allowed = $false
    $result.command = "submit"
    $result.task_id = $Task
    $result.reason = "Controlled Lane V2 is frozen and cannot be started from run_task.ps1."
    $result | ConvertTo-Json -Compress -Depth 20
    exit 2
}

if ($Preview) {
    $output = @(& py $helper inspect --repo-root $RepositoryRoot --json) -join "`n"
    $exitCode = $LASTEXITCODE
    Write-Output $output
    exit $exitCode
}

$nativeRequestJson = $RequestJson.Replace('"', '\"')
$output = @(
    & py $helper submit `
        --repo-root $RepositoryRoot `
        --expected-board-sha256 $ExpectedBoardSha256 `
        --task-id $Task `
        --request-json $nativeRequestJson `
        --json
) -join "`n"
$exitCode = $LASTEXITCODE
Write-Output $output
exit $exitCode
