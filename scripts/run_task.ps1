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
    $worktreeSnapshot = (git worktree list --porcelain | Out-String).Trim()

    $prompt = @(
        "User command: execute $Task."
        ""
        "Treat this as the ConnLab default execute-task trigger."
        "The user does not need to repeat worktree/branch setup or continuation to Integrator."
        ""
        "Read and obey, in order:"
        "1. AGENTS.md"
        "2. $taskBoard"
        "3. $taskFile"
        "4. docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md"
        "5. docs/project_management/PARALLEL_EXECUTION_MODEL.md"
        "6. docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md"
        "7. docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md"
        "8. .agents/skills/connlab-lane-orchestrator/SKILL.md"
        ""
        "Current repository snapshot:"
        "- execution gate: $gateJson"
        "- invoking branch: $branch"
        "- HEAD: $head"
        "- worktree status entries: $statusCount"
        "- staged entries: $indexCount"
        "- git worktrees:"
        $worktreeSnapshot
        ""
        "Required orchestration behavior:"
        "1. Re-read board/task/plan/evidence, role-thread state when available, and git worktree state."
        "2. If this TASK already has a valid lane worktree, resume it; never create a duplicate."
        "3. Compare shared files, authority paths, and Locked Paths with every active lane."
        "4. Obey the execution-gate decision. QUEUE_REQUIRED routes queue governance only; it never dispatches implementation or creates a worktree."
        "5. If planning or implementation approval is missing, route the smallest required Planner/User gate first."
        "6. For approved product/tests-only implementation, create an isolated lane/* branch and sibling worktree automatically, even when no other task is active."
        "7. Keep the primary master worktree for planning/integration only."
        "8. Retain the original task token through Developer/Reviewer/QA/fix/Integrator gates until accepted/cancelled or durably paused."
        "9. Require clean lane commits, clean Reviewer/QA inputs, an exact residual ledger, and clean non-force worktree retirement."
        "10. Never run git add -A, force-remove a worktree, discard changes, or push remote."
        ""
        "Stop only for missing explicit approval, scope/product-contract change, shared-path conflict, ambiguous test failure, destructive discard, or unauthorized merge/push."
        "Before any write-capable dispatch, rerun -Intent ImplementationDispatch against the board authority."
        "Perform only the next legal routing action per callback, but keep the task-level Goal active until local Integrator acceptance."
    ) -join "`n"

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
