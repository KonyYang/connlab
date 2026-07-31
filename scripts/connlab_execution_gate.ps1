[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "Inspect",
        "StartTask",
        "CreateWorktree",
        "ImplementationDispatch",
        "QuickFixPreempt",
        "Reconcile",
        "Resume"
    )]
    [string]$Intent,
    [string]$TaskId,
    [string]$Lane,
    [string]$RepositoryRoot,
    [switch]$AllowTestRepositoryRoot,
    [switch]$Json
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$script:Control = $null
$script:SnapshotDigest = $null
$script:DefaultRepositoryRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $PSScriptRoot "..")
).TrimEnd("\")
function Get-PropertyValue {
    param(
        [AllowNull()]
        [object]$Object,
        [Parameter(Mandatory = $true)]
        [string]$Name
    )
    if ($null -eq $Object) {
        return $null
    }
    if ($Object.PSObject.Properties.Name -notcontains $Name) {
        return $null
    }
    return $Object.$Name
}
function Write-GateDecision {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Code,
        [Parameter(Mandatory = $true)]
        [bool]$Allowed,
        [Parameter(Mandatory = $true)]
        [string]$Reason,
        [int]$ExitCode = 0
    )
    $state = Get-PropertyValue -Object $script:Control -Name "execution_state"
    $owner = Get-PropertyValue -Object $script:Control -Name "execution_token_owner"
    $queuePosition = $null
    if ($null -ne $script:Control -and -not [string]::IsNullOrWhiteSpace($TaskId)) {
        foreach ($entry in @(Get-PropertyValue -Object $script:Control -Name "queue")) {
            if ((Get-PropertyValue -Object $entry -Name "task_id") -eq $TaskId) {
                $queuePosition = Get-PropertyValue -Object $entry -Name "queue_position"
                break
            }
        }
    }
    $result = [ordered]@{
        code = $Code
        allowed = $Allowed
        zero_write = $true
        intent = $Intent
        task_id = $TaskId
        lane = $Lane
        execution_state = $state
        execution_token_owner = $owner
        queue_position = $queuePosition
        snapshot_digest = $script:SnapshotDigest
        reason = $Reason
    }
    if ($Json) {
        $result | ConvertTo-Json -Compress -Depth 8
    }
    else {
        foreach ($key in $result.Keys) {
            Write-Output "${key}: $($result[$key])"
        }
    }
    exit $ExitCode
}
function Deny {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Code,
        [Parameter(Mandatory = $true)]
        [string]$Reason
    )
    Write-GateDecision -Code $Code -Allowed $false -Reason $Reason -ExitCode 2
}
function Get-Sha256 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}
function Invoke-GitRead {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Directory,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = @(& git -C $Directory @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    return [pscustomobject]@{
        ExitCode = $exitCode
        Output = $output
    }
}
function Test-RequiredProperties {
    param(
        [AllowNull()]
        [object]$Object,
        [Parameter(Mandatory = $true)]
        [string[]]$Names
    )
    if ($null -eq $Object) {
        return $false
    }
    foreach ($name in $Names) {
        if ($Object.PSObject.Properties.Name -notcontains $name) {
            return $false
        }
        $value = Get-PropertyValue -Object $Object -Name $name
        if ($null -eq $value) {
            return $false
        }
        if ($value -is [string] -and [string]::IsNullOrWhiteSpace($value)) {
            return $false
        }
    }
    return $true
}
function Get-NormalizedLocks {
    param(
        [AllowNull()]
        [object]$Values
    )
    return @(
        foreach ($value in @($Values)) {
            if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
                ([string]$value).Replace("\", "/").TrimEnd("/").ToLowerInvariant()
            }
        }
    )
}
function Test-LockOverlap {
    param(
        [AllowNull()]
        [object]$Left,
        [AllowNull()]
        [object]$Right
    )
    $leftLocks = @(Get-NormalizedLocks -Values $Left)
    $rightLocks = @(Get-NormalizedLocks -Values $Right)
    foreach ($left in $leftLocks) {
        foreach ($right in $rightLocks) {
            if ($left -eq $right -or $left.StartsWith("$right/") -or $right.StartsWith("$left/")) {
                return $true
            }
        }
    }
    return $false
}

function Test-PreservedCheckpoint {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Paused
    )

    $worktree = [string](Get-PropertyValue -Object $Paused -Name "worktree")
    if (-not (Test-Path -LiteralPath $worktree -PathType Container)) {
        Deny -Code "BLOCKED_CHECKPOINT_WORKTREE_MISSING" -Reason "The preserved worktree does not exist."
    }
    $status = Invoke-GitRead -Directory $worktree -Arguments @("status", "--porcelain=v1")
    if ($status.ExitCode -ne 0) {
        Deny -Code "BLOCKED_GIT_FACTS_UNAVAILABLE" -Reason "Could not read preserved worktree status."
    }
    if (@($status.Output).Count -ne 0) {
        Deny -Code "BLOCKED_CHECKPOINT_DIRTY" -Reason "The preserved worktree is not clean."
    }
    $headResult = Invoke-GitRead -Directory $worktree -Arguments @("rev-parse", "HEAD")
    $head = [string]($headResult.Output | Select-Object -First 1)
    if ($headResult.ExitCode -ne 0 -or $head.Trim() -ne [string]$Paused.checkpoint_sha) {
        Deny -Code "BLOCKED_CHECKPOINT_DRIFT" -Reason "The preserved worktree HEAD differs from checkpoint_sha."
    }
    $branchResult = Invoke-GitRead -Directory $worktree -Arguments @("branch", "--show-current")
    $branch = [string]($branchResult.Output | Select-Object -First 1)
    if ($branchResult.ExitCode -ne 0 -or $branch.Trim() -ne [string]$Paused.branch) {
        Deny -Code "BLOCKED_CHECKPOINT_BRANCH_MISMATCH" -Reason "The preserved worktree branch differs from the pause record."
    }
}

try {
    if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
        $RepositoryRoot = $script:DefaultRepositoryRoot
    }
    $RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd("\")
    if ($RepositoryRoot -ne $script:DefaultRepositoryRoot -and -not $AllowTestRepositoryRoot) {
        Deny -Code "BLOCKED_TEST_ROOT_NOT_ALLOWED" -Reason "Alternate repository roots require -AllowTestRepositoryRoot."
    }

    $boardPath = Join-Path $RepositoryRoot "docs\task_board.md"
    if (-not (Test-Path -LiteralPath $boardPath -PathType Leaf)) {
        Deny -Code "BLOCKED_BOARD_MISSING" -Reason "The task board is missing."
    }
    $boardText = Get-Content -LiteralPath $boardPath -Raw -Encoding UTF8
    $beginMarker = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"
    $endMarker = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
    $beginCount = ([regex]::Matches($boardText, [regex]::Escape($beginMarker))).Count
    $endCount = ([regex]::Matches($boardText, [regex]::Escape($endMarker))).Count
    if ($beginCount -eq 0 -or $endCount -eq 0) {
        Deny -Code "BLOCKED_MARKERS_MISSING" -Reason "The execution-control markers are missing."
    }
    if ($beginCount -ne 1 -or $endCount -ne 1) {
        Deny -Code "BLOCKED_MARKERS_DUPLICATE" -Reason "The execution-control markers must be unique."
    }

    $beginIndex = $boardText.IndexOf($beginMarker) + $beginMarker.Length
    $endIndex = $boardText.IndexOf($endMarker)
    if ($endIndex -le $beginIndex) {
        Deny -Code "BLOCKED_MARKER_ORDER" -Reason "The execution-control markers are out of order."
    }
    $rawBlock = $boardText.Substring($beginIndex, $endIndex - $beginIndex)
    $fenced = [regex]::Match($rawBlock, '(?s)^\s*```json\s*(.*?)\s*```\s*$')
    if (-not $fenced.Success) {
        Deny -Code "BLOCKED_JSON_INVALID" -Reason "The execution-control block must contain one fenced JSON object."
    }
    $jsonText = $fenced.Groups[1].Value
    $script:SnapshotDigest = Get-Sha256 -Value $jsonText
    try {
        $script:Control = $jsonText | ConvertFrom-Json
    }
    catch {
        Deny -Code "BLOCKED_JSON_INVALID" -Reason "The execution-control JSON is malformed."
    }

    $requiredRoot = @(
        "schema", "version", "wip_limit", "execution_token_owner", "execution_state",
        "active", "queue", "paused", "quick_fix", "residuals", "parallel_exception",
        "last_governance_commit", "evidence"
    )
    foreach ($name in $requiredRoot) {
        if ($script:Control.PSObject.Properties.Name -notcontains $name) {
            Deny -Code "BLOCKED_SCHEMA_INVALID" -Reason "Missing required execution-control key: $name"
        }
    }
    if ($script:Control.schema -ne "connlab.execution-control" -or [int]$script:Control.version -ne 1) {
        Deny -Code "BLOCKED_SCHEMA_UNSUPPORTED" -Reason "Unsupported execution-control schema or version."
    }
    if ([int]$script:Control.wip_limit -ne 1) {
        Deny -Code "BLOCKED_WIP_LIMIT_INVALID" -Reason "The default execution WIP limit must remain one."
    }

    $validStates = @(
        "idle", "queued", "implementation_running", "gate_running", "paused_preempted",
        "quick_fix_running", "reconciling", "complete", "cancelled"
    )
    $state = [string]$script:Control.execution_state
    if ($state -notin $validStates) {
        Deny -Code "BLOCKED_STATE_INVALID" -Reason "Unknown execution state."
    }
    $owner = $script:Control.execution_token_owner
    $ownerRequired = @("queued", "implementation_running", "gate_running", "quick_fix_running", "reconciling")
    $ownerForbidden = @("idle", "paused_preempted", "complete", "cancelled")
    if (($state -in $ownerRequired -and [string]::IsNullOrWhiteSpace([string]$owner)) -or
        ($state -in $ownerForbidden -and -not [string]::IsNullOrWhiteSpace([string]$owner))) {
        Deny -Code "BLOCKED_OWNER_STATE_CONTRADICTION" -Reason "Token owner contradicts the execution state."
    }

    $positions = @()
    foreach ($entry in @($script:Control.queue)) {
        if (-not (Test-RequiredProperties -Object $entry -Names @("task_id", "queue_position"))) {
            Deny -Code "BLOCKED_QUEUE_INVALID" -Reason "A queue record is incomplete."
        }
        $position = [int]$entry.queue_position
        if ($position -lt 1) {
            Deny -Code "BLOCKED_QUEUE_INVALID" -Reason "Queue positions must be positive."
        }
        if ($positions -contains $position) {
            Deny -Code "BLOCKED_QUEUE_POSITION_DUPLICATE" -Reason "Queue positions must be unique."
        }
        $positions += $position
    }

    $pausedFields = @(
        "task_id", "lane", "branch", "worktree", "previous_owner", "paused_reason",
        "preempted_by", "checkpoint_sha", "pause_master_sha", "resume_condition",
        "unfinished_items", "locked_paths", "evidence"
    )
    if ($state -in @("paused_preempted", "reconciling") -and
        -not (Test-RequiredProperties -Object $script:Control.paused -Names $pausedFields)) {
        Deny -Code "BLOCKED_PAUSE_INCOMPLETE" -Reason "The paused state requires a complete pause record."
    }
    if ($state -eq "quick_fix_running") {
        if (-not (Test-RequiredProperties -Object $script:Control.quick_fix -Names @("task_id", "lane", "risk_gate", "locked_paths"))) {
            Deny -Code "BLOCKED_QUICK_FIX_INCOMPLETE" -Reason "The running Quick Fix record is incomplete."
        }
        if ([string]$script:Control.quick_fix.task_id -ne [string]$owner) {
            Deny -Code "BLOCKED_OWNER_STATE_CONTRADICTION" -Reason "Quick Fix owner differs from the token owner."
        }
    }
    if ($state -eq "reconciling" -and [string]$script:Control.paused.task_id -ne [string]$owner) {
        Deny -Code "BLOCKED_OWNER_STATE_CONTRADICTION" -Reason "Reconciliation owner must be the paused original task."
    }

    if ($null -ne $script:Control.parallel_exception) {
        $parallelFields = @(
            "secondary_execution_token_owner", "secondary_lane", "user_approval_evidence",
            "scope_proof", "locked_paths", "end_condition"
        )
        if (-not (Test-RequiredProperties -Object $script:Control.parallel_exception -Names $parallelFields)) {
            Deny -Code "BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE" -Reason "Parallel exception proof is incomplete."
        }
        if ([string]$script:Control.parallel_exception.secondary_execution_token_owner -eq [string]$owner) {
            Deny -Code "BLOCKED_PARALLEL_OWNER_DUPLICATE" -Reason "Primary and secondary owners must differ."
        }
        $activeLocks = Get-PropertyValue -Object $script:Control.active -Name "locked_paths"
        if (Test-LockOverlap -Left $activeLocks -Right $script:Control.parallel_exception.locked_paths) {
            Deny -Code "BLOCKED_LOCKED_PATH_OVERLAP" -Reason "Parallel owners may not share locked paths."
        }
    }

    switch ($Intent) {
        "Inspect" {
            Write-GateDecision -Code "ALLOW_INSPECT" -Allowed $true -Reason "Execution authority is valid and internally consistent."
        }
        "StartTask" {
            if ([string]::IsNullOrWhiteSpace($TaskId)) {
                Deny -Code "BLOCKED_TASK_ID_REQUIRED" -Reason "StartTask requires TaskId."
            }
            if ([string]$owner -eq $TaskId) {
                Write-GateDecision -Code "ALLOW_RESUME" -Allowed $true -Reason "The requested task already owns the token."
            }
            if ($null -ne $script:Control.parallel_exception -and
                [string]$script:Control.parallel_exception.secondary_execution_token_owner -eq $TaskId) {
                Write-GateDecision -Code "ALLOW_START_PARALLEL" -Allowed $true -Reason "The requested task is the approved secondary owner."
            }
            if (-not [string]::IsNullOrWhiteSpace([string]$owner)) {
                Write-GateDecision -Code "QUEUE_REQUIRED" -Allowed $true -Reason "Another task retains the execution token."
            }
            if ($state -eq "paused_preempted") {
                Deny -Code "BLOCKED_PAUSED_RECONCILIATION_REQUIRED" -Reason "A paused original must be reconciled or explicitly governed first."
            }
            Write-GateDecision -Code "ALLOW_START" -Allowed $true -Reason "No task owns the execution token."
        }
        "CreateWorktree" {
            if ([string]::IsNullOrWhiteSpace($TaskId)) {
                Deny -Code "BLOCKED_TASK_ID_REQUIRED" -Reason "CreateWorktree requires TaskId."
            }
            if ([string]$owner -eq $TaskId) {
                $activeLane = [string](Get-PropertyValue -Object $script:Control.active -Name "lane")
                if (-not [string]::IsNullOrWhiteSpace($activeLane) -and $activeLane -ne $Lane) {
                    Deny -Code "BLOCKED_LANE_MISMATCH" -Reason "Requested lane differs from the active owner lane."
                }
                Write-GateDecision -Code "ALLOW_WORKTREE_CREATE" -Allowed $true -Reason "The requested task is the primary token owner."
            }
            if ($null -ne $script:Control.parallel_exception -and
                [string]$script:Control.parallel_exception.secondary_execution_token_owner -eq $TaskId -and
                [string]$script:Control.parallel_exception.secondary_lane -eq $Lane) {
                Write-GateDecision -Code "ALLOW_WORKTREE_CREATE" -Allowed $true -Reason "The requested task is the approved secondary owner."
            }
            Deny -Code "BLOCKED_TOKEN_OWNED" -Reason "The requested task is not an execution owner."
        }
        "ImplementationDispatch" {
            $active = $null
            if ([string]$owner -eq $TaskId) {
                $active = $script:Control.active
            }
            elseif ($null -ne $script:Control.parallel_exception -and
                [string]$script:Control.parallel_exception.secondary_execution_token_owner -eq $TaskId) {
                $parallel = $script:Control.parallel_exception
                if (-not (Test-RequiredProperties -Object $parallel -Names @(
                    "secondary_lane", "secondary_branch", "secondary_worktree", "secondary_head_sha"
                ))) {
                    Deny -Code "BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE" -Reason "Secondary dispatch Git facts are incomplete."
                }
                $active = [pscustomobject]@{
                    task_id = $TaskId; lane = $parallel.secondary_lane; branch = $parallel.secondary_branch
                    worktree = $parallel.secondary_worktree; head_sha = $parallel.secondary_head_sha
                    locked_paths = $parallel.locked_paths; evidence = $parallel.user_approval_evidence
                }
            }
            else {
                Deny -Code "BLOCKED_TOKEN_OWNED" -Reason "Only the recorded token owner may receive implementation dispatch."
            }
            if (-not (Test-RequiredProperties -Object $active -Names @("task_id", "lane", "branch", "worktree", "head_sha", "locked_paths", "evidence"))) {
                Deny -Code "BLOCKED_ACTIVE_RECORD_INCOMPLETE" -Reason "Implementation dispatch requires a complete active record."
            }
            if ([string]$active.task_id -ne $TaskId -or [string]$active.lane -ne $Lane) {
                Deny -Code "BLOCKED_LANE_MISMATCH" -Reason "Dispatch task/lane differs from the active record."
            }
            if (-not (Test-Path -LiteralPath ([string]$active.worktree) -PathType Container)) {
                Deny -Code "BLOCKED_ACTIVE_WORKTREE_MISSING" -Reason "The active worktree does not exist."
            }
            $status = Invoke-GitRead -Directory ([string]$active.worktree) -Arguments @("status", "--porcelain=v1")
            if ($status.ExitCode -ne 0 -or @($status.Output).Count -ne 0) {
                Deny -Code "BLOCKED_ACTIVE_WORKTREE_DIRTY" -Reason "The active worktree must be clean before dispatch."
            }
            $head = Invoke-GitRead -Directory ([string]$active.worktree) -Arguments @("rev-parse", "HEAD")
            if ($head.ExitCode -ne 0 -or ([string]($head.Output | Select-Object -First 1)).Trim() -ne [string]$active.head_sha) {
                Deny -Code "BLOCKED_ACTIVE_HEAD_DRIFT" -Reason "The active worktree HEAD differs from the board."
            }
            Write-GateDecision -Code "ALLOW_DISPATCH" -Allowed $true -Reason "Token, lane, worktree, and HEAD facts match."
        }
        "QuickFixPreempt" {
            if ($state -eq "quick_fix_running" -or ($null -ne $script:Control.paused -and
                [string](Get-PropertyValue -Object $script:Control.paused -Name "preempted_by") -ne $TaskId)) {
                Deny -Code "BLOCKED_NESTED_PREEMPTION" -Reason "Quick Fix preemption cannot nest."
            }
            if ($state -ne "paused_preempted" -or $null -ne $owner) {
                Deny -Code "BLOCKED_PAUSE_REQUIRED" -Reason "Quick Fix activation requires a durable owner-null paused_preempted state."
            }
            if (-not (Test-RequiredProperties -Object $script:Control.paused -Names $pausedFields)) {
                Deny -Code "BLOCKED_PAUSE_INCOMPLETE" -Reason "Quick Fix activation requires a complete pause record."
            }
            if (-not (Test-RequiredProperties -Object $script:Control.quick_fix -Names @("task_id", "lane", "risk_gate", "locked_paths"))) {
                Deny -Code "BLOCKED_QUICK_FIX_INCOMPLETE" -Reason "Quick Fix activation requires a complete candidate record."
            }
            if ([string]$script:Control.paused.preempted_by -ne $TaskId -or
                [string]$script:Control.quick_fix.task_id -ne $TaskId -or
                [string]$script:Control.quick_fix.lane -ne $Lane) {
                Deny -Code "BLOCKED_QUICK_FIX_MISMATCH" -Reason "Requested Quick Fix differs from the pause/candidate record."
            }
            if ([string]$script:Control.quick_fix.risk_gate -notin @("QF-1", "QF-2", "QF-3")) {
                Deny -Code "BLOCKED_QUICK_FIX_RISK" -Reason "QF-4 and unknown risk classes require Planner/User."
            }
            if (Test-LockOverlap -Left $script:Control.paused.locked_paths -Right $script:Control.quick_fix.locked_paths) {
                Deny -Code "BLOCKED_LOCKED_PATH_OVERLAP" -Reason "Quick Fix locks overlap the paused original."
            }
            Test-PreservedCheckpoint -Paused $script:Control.paused
            Write-GateDecision -Code "ALLOW_PREEMPT_CHECKPOINTED" -Allowed $true -Reason "The original lane is clean, checkpointed, and disjoint."
        }
        "Reconcile" {
            if ($state -ne "quick_fix_running" -or $null -eq $script:Control.paused) {
                Deny -Code "BLOCKED_RECONCILIATION_STATE" -Reason "Reconciliation requires an accepted preempting Quick Fix."
            }
            if ([string]$script:Control.paused.task_id -ne $TaskId -or [string]$script:Control.paused.lane -ne $Lane) {
                Deny -Code "BLOCKED_RECONCILIATION_OWNER" -Reason "Requested task/lane differs from the paused original."
            }
            if ($script:Control.quick_fix.accepted_on_master -ne $true -or
                [string]::IsNullOrWhiteSpace([string]$script:Control.quick_fix.accepted_head)) {
                Deny -Code "BLOCKED_QUICK_FIX_NOT_ACCEPTED" -Reason "Quick Fix acceptance on master is not proven."
            }
            Test-PreservedCheckpoint -Paused $script:Control.paused
            $accepted = Invoke-GitRead -Directory $RepositoryRoot -Arguments @(
                "merge-base", "--is-ancestor", [string]$script:Control.quick_fix.accepted_head, "master"
            )
            if ($accepted.ExitCode -ne 0) {
                Deny -Code "BLOCKED_QUICK_FIX_NOT_ON_MASTER" -Reason "The accepted Quick Fix is not an ancestor of master."
            }
            $pauseBase = Invoke-GitRead -Directory $RepositoryRoot -Arguments @(
                "merge-base", "--is-ancestor", [string]$script:Control.paused.pause_master_sha, "master"
            )
            if ($pauseBase.ExitCode -ne 0) {
                Deny -Code "BLOCKED_PAUSE_BASE_DRIFT" -Reason "pause_master_sha is not an ancestor of master."
            }
            Write-GateDecision -Code "ALLOW_RECONCILE" -Allowed $true -Reason "Accepted Quick Fix and preserved checkpoint facts allow merge-based reconciliation."
        }
        "Resume" {
            if ($state -ne "reconciling" -or [string]$owner -ne $TaskId) {
                Deny -Code "BLOCKED_RESUME_STATE" -Reason "Resume requires the original task to own reconciling state."
            }
            Write-GateDecision -Code "ALLOW_RESUME" -Allowed $true -Reason "The original task owns the reconciliation token."
        }
    }
}
catch {
    Deny -Code "BLOCKED_INTERNAL_ERROR" -Reason $_.Exception.Message
}
