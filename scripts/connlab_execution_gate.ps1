[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "Inspect", "Implementation", "Close",
        "StartTask", "CreateWorktree", "ImplementationDispatch",
        "QuickFixPreempt", "Reconcile", "Resume"
    )]
    [string]$Intent,

    [string]$TaskId,

    [string]$RepositoryRoot,

    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$helper = Join-Path $PSScriptRoot "connlab_personal_task.py"
$legacyIntents = @(
    "StartTask", "CreateWorktree", "ImplementationDispatch",
    "QuickFixPreempt", "Reconcile", "Resume"
)

# Version-2 role transitions are authorized by the board writer's closed command/state matrix.
# This adapter remains a read-only gate for Inspect, direct Implementation, and User Close only.

if ($legacyIntents -contains $Intent) {
    $snapshotText = @(& py $helper inspect --repo-root $RepositoryRoot --json) -join "`n"
    if ($LASTEXITCODE -ne 0) {
        Write-Output $snapshotText
        exit $LASTEXITCODE
    }
    $result = $snapshotText | ConvertFrom-Json
    $result.code = "BLOCKED_LEGACY_MODE_FROZEN"
    $result.allowed = $false
    $result.command = "check"
    $result.task_id = if ([string]::IsNullOrWhiteSpace($TaskId)) { $null } else { $TaskId }
    $result.reason = "Legacy lane, worktree, quick-fix, dispatch, and reconciliation intents are frozen."
    if ($Json) {
        $result | ConvertTo-Json -Compress -Depth 20
    } else {
        foreach ($property in $result.PSObject.Properties) {
            Write-Output "$($property.Name): $($property.Value)"
        }
    }
    exit 2
}

$arguments = @($helper, "check", "--repo-root", $RepositoryRoot, "--intent", $Intent)
if (-not [string]::IsNullOrWhiteSpace($TaskId)) {
    $arguments += @("--task-id", $TaskId)
}
if ($Json) {
    $arguments += "--json"
}

$output = @(& py @arguments) -join "`n"
$exitCode = $LASTEXITCODE
Write-Output $output
exit $exitCode
