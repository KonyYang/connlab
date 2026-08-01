[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Task,

    [switch]$Preview,

    [switch]$ControlledLaneV2,

    [string]$RequestJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if (-not $ControlledLaneV2) {
    . "$PSScriptRoot\_codex_runtime.ps1"
}

$taskBoard = "docs/task_board.md"
$taskFile = "tasks/$Task.md"

if ($ControlledLaneV2) {
    if ([string]::IsNullOrWhiteSpace($RequestJson)) {
        throw "-RequestJson is required with -ControlledLaneV2."
    }
    & "$PSScriptRoot\connlab_controlled_lane.ps1" `
        -Command "scan" `
        -RequestJson $RequestJson `
        -DryRun:$Preview
    exit $LASTEXITCODE
}

$gateOutput = @(
    & "$PSScriptRoot\connlab_execution_gate.ps1" `
        -Intent "StartTask" `
        -TaskId $Task `
        -Json
)
$gateExitCode = $LASTEXITCODE
$gateJson = ($gateOutput -join "`n").Trim()
if ($gateExitCode -ne 0) {
    Write-Output $gateJson
    exit $gateExitCode
}
$gateResult = $gateJson | ConvertFrom-Json
if ($gateResult.code -eq "QUEUE_REQUIRED") {
    Write-Output $gateJson
    exit 0
}
$repoRoot = [System.IO.Path]::GetFullPath([string]$gateResult.authority_root).TrimEnd("\")

Push-Location $repoRoot
try {
    if (-not (Test-Path -LiteralPath $taskBoard -PathType Leaf)) {
        throw "Task board not found: $taskBoard"
    }
    if (-not (Test-Path -LiteralPath $taskFile -PathType Leaf)) {
        throw "Task file not found: $taskFile"
    }

    $head = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Could not resolve repository HEAD."
    }
    $branch = (& git branch --show-current).Trim()
    $statusCount = @(git status --porcelain=v1 --untracked-files=all).Count
    $indexCount = @(git diff --cached --name-only).Count
    $refScript = "import hashlib,json,subprocess,sys; root,head,*paths=sys.argv[1:]; refs=[p+'@'+head+'#'+hashlib.sha256(subprocess.check_output(['git','-C',root,'show',head+':'+p])).hexdigest() for p in paths]; print(json.dumps(refs,separators=(',',':')))"
    $readRefs = (& py -c $refScript $repoRoot $head $taskBoard $taskFile) | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) {
        throw "Could not build immutable board/task references."
    }
    $capsule = [ordered]@{
        schema = "connlab.orchestrator-trigger.v1"
        task_id = $Task
        authority = [ordered]@{
            gate = $gateResult.code
            snapshot_digest = $gateResult.snapshot_digest
            primary_head = $head
            branch = $branch
            status_entries = $statusCount
            index_entries = $indexCount
        }
        read_refs = @($readRefs)
        resolve_at_runtime = @(
            "approved plan/current evidence"
            "ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md"
            "EXECUTION_WIP_AND_QUICK_FIX_POLICY.md"
            "LANE_ORCHESTRATION_PROTOCOL.md"
            "ROLE_THREAD_REGISTRY.md"
            "connlab-lane-orchestrator/SKILL.md"
            "git worktree list"
        )
        constraints = @(
            "QUEUE_REQUIRED routes queue governance only; it never dispatches implementation or creates a worktree."
            "Re-resolve primary authority; reuse exact lane; rerun ImplementationDispatch before writes."
            "Preserve WIP=1 through Integrator; use one durable transition and one dispatch, then stop without waiting."
            "No git add -A, rebase, force-remove, discard, destructive cleanup, or push."
        )
        goal = "Continue the approved task through classic permanent roles to local Integrator acceptance."
    }
    $prompt = $capsule | ConvertTo-Json -Compress -Depth 8

    if ($Preview) {
        Write-Output $prompt
        exit 0
    }

    $exitCode = Invoke-CodexCli -Prompt $prompt
    exit $exitCode
}
finally {
    Pop-Location
}
