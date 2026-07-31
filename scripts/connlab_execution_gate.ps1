[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Inspect", "StartTask", "CreateWorktree", "ImplementationDispatch", "QuickFixPreempt", "Reconcile", "Resume")]
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
$script:Digest = $null
$script:AuthorityRoot = $null

function Value([AllowNull()][object]$Object, [string]$Name) {
    if ($null -eq $Object -or $Object.PSObject.Properties.Name -notcontains $Name) { return $null }
    return $Object.$Name
}
function Emit([string]$Code, [bool]$Allowed, [string]$Reason, [int]$ExitCode = 0) {
    $position = $null
    if ($null -ne $script:Control -and $TaskId) {
        foreach ($item in @(Value $script:Control "queue")) {
            if ((Value $item "task_id") -eq $TaskId) { $position = Value $item "queue_position"; break }
        }
    }
    $result = [ordered]@{
        code=$Code; allowed=$Allowed; zero_write=$true; intent=$Intent; task_id=$TaskId; lane=$Lane
        execution_state=(Value $script:Control "execution_state")
        execution_token_owner=(Value $script:Control "execution_token_owner")
        queue_position=$position; snapshot_digest=$script:Digest; authority_root=$script:AuthorityRoot; reason=$Reason
    }
    if ($Json) { $result | ConvertTo-Json -Compress -Depth 10 }
    else { foreach ($key in $result.Keys) { Write-Output "${key}: $($result[$key])" } }
    exit $ExitCode
}
function Deny([string]$Code, [string]$Reason) { Emit $Code $false $Reason 2 }
function GitRead([string]$Directory, [string[]]$Arguments) {
    $old = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    try { $output = @(& git -C $Directory @Arguments 2>&1); $exitCode = $LASTEXITCODE }
    finally { $ErrorActionPreference = $old }
    return [pscustomobject]@{ ExitCode=$exitCode; Output=$output }
}
function Required([AllowNull()][object]$Object, [string[]]$Names) {
    if ($null -eq $Object) { return $false }
    foreach ($name in $Names) {
        if ($Object.PSObject.Properties.Name -notcontains $name) { return $false }
        $value = Value $Object $name
        if ($null -eq $value -or ($value -is [string] -and [string]::IsNullOrWhiteSpace($value))) { return $false }
    }
    return $true
}
function PositiveInteger([AllowNull()][object]$Value) {
    return ($Value -is [byte] -or $Value -is [int16] -or $Value -is [int32] -or $Value -is [int64]) -and [int64]$Value -gt 0
}
function StringArray([object]$Object, [string]$Name, [bool]$AllowEmpty) {
    if ($Object.PSObject.Properties.Name -notcontains $Name) { return $false }
    $raw = $Object.$Name
    if ($raw -is [string]) { return $false }
    $items = @($raw)
    if (-not $AllowEmpty -and $items.Count -eq 0) { return $false }
    foreach ($item in $items) { if ($item -isnot [string] -or [string]::IsNullOrWhiteSpace($item)) { return $false } }
    return @($items | Select-Object -Unique).Count -eq $items.Count
}
function NormalLocks([AllowNull()][object]$Values) {
    return @(foreach ($value in @($Values)) {
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            ([string]$value).Replace("\", "/").TrimEnd("/").ToLowerInvariant()
        }
    })
}
function LocksOverlap([AllowNull()][object]$Left, [AllowNull()][object]$Right) {
    foreach ($leftLock in @(NormalLocks $Left)) {
        foreach ($rightLock in @(NormalLocks $Right)) {
            if ($leftLock -eq $rightLock -or $leftLock.StartsWith("$rightLock/") -or $rightLock.StartsWith("$leftLock/")) { return $true }
        }
    }
    return $false
}
function ResolvePrimary([string]$Start) {
    $commonResult = GitRead $Start @("rev-parse", "--git-common-dir")
    if ($commonResult.ExitCode -ne 0) { Deny "BLOCKED_PRIMARY_ROOT_UNRESOLVED" "Git common directory is unavailable." }
    $common = [string]($commonResult.Output | Select-Object -First 1)
    if (-not [IO.Path]::IsPathRooted($common)) { $common = Join-Path $Start $common }
    $common = [IO.Path]::GetFullPath($common).TrimEnd("\")
    $candidate = [IO.Path]::GetFullPath((Split-Path -Parent $common)).TrimEnd("\")
    $top = GitRead $candidate @("rev-parse", "--show-toplevel")
    $branch = GitRead $candidate @("branch", "--show-current")
    if ($top.ExitCode -ne 0 -or ([string]($top.Output | Select-Object -First 1)).Trim().Replace("/", "\") -ne $candidate.Replace("/", "\") -or
        -not (Test-Path -LiteralPath (Join-Path $candidate ".git") -PathType Container) -or
        $branch.ExitCode -ne 0 -or ([string]($branch.Output | Select-Object -First 1)).Trim() -ne "master") {
        Deny "BLOCKED_PRIMARY_ROOT_UNVERIFIED" "The main master worktree cannot be verified."
    }
    return $candidate
}
function CheckGitRecord([object]$Record, [string]$ExpectedHead, [string]$ExpectedBranch) {
    $worktree = [string](Value $Record "worktree")
    if (-not (Test-Path -LiteralPath $worktree -PathType Container)) { Deny "BLOCKED_ACTIVE_WORKTREE_MISSING" "The recorded worktree is missing." }
    $status = GitRead $worktree @("status", "--porcelain=v1")
    if ($status.ExitCode -ne 0) { Deny "BLOCKED_GIT_FACTS_UNAVAILABLE" "Could not read worktree status." }
    if (@($status.Output).Count -ne 0) { Deny "BLOCKED_ACTIVE_WORKTREE_DIRTY" "The recorded worktree must be clean." }
    $head = GitRead $worktree @("rev-parse", "HEAD")
    if ($head.ExitCode -ne 0 -or ([string]($head.Output | Select-Object -First 1)).Trim() -ne $ExpectedHead) { Deny "BLOCKED_ACTIVE_HEAD_DRIFT" "The recorded worktree HEAD differs from the board." }
    $branch = GitRead $worktree @("branch", "--show-current")
    if ($branch.ExitCode -ne 0 -or ([string]($branch.Output | Select-Object -First 1)).Trim() -ne $ExpectedBranch) { Deny "BLOCKED_ACTIVE_BRANCH_MISMATCH" "The recorded worktree branch differs from the board." }
}
function CheckPausedCheckpoint([object]$Paused) {
    $worktree = [string]$Paused.worktree
    if (-not (Test-Path -LiteralPath $worktree -PathType Container)) { Deny "BLOCKED_CHECKPOINT_WORKTREE_MISSING" "The preserved worktree is missing." }
    $status = GitRead $worktree @("status", "--porcelain=v1")
    if ($status.ExitCode -ne 0) { Deny "BLOCKED_GIT_FACTS_UNAVAILABLE" "Could not read preserved worktree status." }
    if (@($status.Output).Count -ne 0) { Deny "BLOCKED_CHECKPOINT_DIRTY" "The preserved worktree is not clean." }
    $head = GitRead $worktree @("rev-parse", "HEAD")
    if ($head.ExitCode -ne 0 -or ([string]($head.Output | Select-Object -First 1)).Trim() -ne [string]$Paused.checkpoint_sha) { Deny "BLOCKED_CHECKPOINT_DRIFT" "The preserved worktree HEAD differs from checkpoint_sha." }
    $branch = GitRead $worktree @("branch", "--show-current")
    if ($branch.ExitCode -ne 0 -or ([string]($branch.Output | Select-Object -First 1)).Trim() -ne [string]$Paused.branch) { Deny "BLOCKED_CHECKPOINT_BRANCH_MISMATCH" "The preserved worktree branch differs from pause record." }
}
function IsAncestor([string]$Older, [string]$Newer) {
    return (GitRead $script:AuthorityRoot @("merge-base", "--is-ancestor", $Older, $Newer)).ExitCode -eq 0
}

try {
    $scriptRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..")).TrimEnd("\")
    if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) { $RepositoryRoot = ResolvePrimary $scriptRoot }
    elseif (-not $AllowTestRepositoryRoot) {
        $primary = ResolvePrimary $scriptRoot
        if ([IO.Path]::GetFullPath($RepositoryRoot).TrimEnd("\") -ne $primary) { Deny "BLOCKED_PRIMARY_ROOT_MISMATCH" "Production calls must use the verified primary worktree." }
        $RepositoryRoot = $primary
    }
    else { $RepositoryRoot = [IO.Path]::GetFullPath($RepositoryRoot).TrimEnd("\") }
    $script:AuthorityRoot = $RepositoryRoot

    $boardPath = Join-Path $RepositoryRoot "docs\task_board.md"
    if (-not (Test-Path -LiteralPath $boardPath -PathType Leaf)) { Deny "BLOCKED_BOARD_MISSING" "The task board is missing." }
    $text = Get-Content -LiteralPath $boardPath -Raw -Encoding UTF8
    $begin = "<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->"; $end = "<!-- CONNLAB_EXECUTION_CONTROL_END -->"
    $beginCount = ([regex]::Matches($text, [regex]::Escape($begin))).Count
    $endCount = ([regex]::Matches($text, [regex]::Escape($end))).Count
    if ($beginCount -eq 0 -or $endCount -eq 0) { Deny "BLOCKED_MARKERS_MISSING" "The execution-control markers are missing." }
    if ($beginCount -ne 1 -or $endCount -ne 1) { Deny "BLOCKED_MARKERS_DUPLICATE" "Execution-control markers must be unique." }
    $start = $text.IndexOf($begin) + $begin.Length; $finish = $text.IndexOf($end)
    if ($finish -le $start) { Deny "BLOCKED_MARKER_ORDER" "Execution-control markers are out of order." }
    $match = [regex]::Match($text.Substring($start, $finish - $start), '(?s)^\s*```json\s*(.*?)\s*```\s*$')
    if (-not $match.Success) { Deny "BLOCKED_JSON_INVALID" "The control block must contain one fenced JSON object." }
    $jsonText = $match.Groups[1].Value
    $bytes = [Text.Encoding]::UTF8.GetBytes($jsonText); $sha = [Security.Cryptography.SHA256]::Create()
    try { $script:Digest = ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant() } finally { $sha.Dispose() }
    try { $script:Control = $jsonText | ConvertFrom-Json } catch { Deny "BLOCKED_JSON_INVALID" "The execution-control JSON is malformed." }

    $rootFields = @("schema", "version", "wip_limit", "execution_token_owner", "execution_state", "active", "queue", "paused", "quick_fix", "residuals", "parallel_exception", "last_governance_commit", "evidence")
    foreach ($name in $rootFields) { if ($script:Control.PSObject.Properties.Name -notcontains $name) { Deny "BLOCKED_SCHEMA_INVALID" "Missing required key: $name" } }
    if ($script:Control.schema -ne "connlab.execution-control" -or [int]$script:Control.version -ne 1) { Deny "BLOCKED_SCHEMA_UNSUPPORTED" "Unsupported execution-control schema/version." }
    if ([int]$script:Control.wip_limit -ne 1) { Deny "BLOCKED_WIP_LIMIT_INVALID" "The execution WIP limit must remain one." }
    $state = [string]$script:Control.execution_state; $owner = $script:Control.execution_token_owner
    $states = @("idle", "queued", "implementation_running", "gate_running", "paused_preempted", "quick_fix_running", "reconciling", "complete", "cancelled")
    if ($state -notin $states) { Deny "BLOCKED_STATE_INVALID" "Unknown execution state." }
    $owned = @("queued", "implementation_running", "gate_running", "quick_fix_running", "reconciling")
    $ownerless = @("idle", "paused_preempted", "complete", "cancelled")
    if (($state -in $owned -and [string]::IsNullOrWhiteSpace([string]$owner)) -or ($state -in $ownerless -and -not [string]::IsNullOrWhiteSpace([string]$owner))) { Deny "BLOCKED_OWNER_STATE_CONTRADICTION" "Token owner contradicts execution state." }

    $positions = @(); $sequences = @(); $queuedTasks = @(); $queueRecords = @()
    foreach ($item in @($script:Control.queue)) {
        $queueFields = @("task_id", "lane", "enqueue_sequence", "enqueued_at", "dependencies", "locked_paths", "requested_priority", "queue_position", "evidence")
        foreach ($field in $queueFields) { if ($item.PSObject.Properties.Name -notcontains $field) { Deny "BLOCKED_QUEUE_INVALID" "A queue record is incomplete." } }
        $requiredQueueValues = @("task_id", "lane", "enqueue_sequence", "enqueued_at", "locked_paths", "requested_priority", "queue_position", "evidence")
        $queuedAt = [datetimeoffset]::MinValue
        if (-not (Required $item $requiredQueueValues) -or -not (PositiveInteger $item.enqueue_sequence) -or -not (PositiveInteger $item.queue_position) -or
            $item.task_id -isnot [string] -or $item.lane -isnot [string] -or $item.enqueued_at -isnot [string] -or $item.requested_priority -isnot [string] -or $item.evidence -isnot [string] -or
            -not [datetimeoffset]::TryParse($item.enqueued_at, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind, [ref]$queuedAt) -or
            -not (StringArray $item "dependencies" $true) -or -not (StringArray $item "locked_paths" $false) -or @($item.dependencies) -contains [string]$item.task_id) {
            Deny "BLOCKED_QUEUE_INVALID" "A queue record has incomplete or invalid frozen FIFO fields."
        }
        if ($positions -contains [int]$item.queue_position) { Deny "BLOCKED_QUEUE_POSITION_DUPLICATE" "Queue positions must be unique." }
        if ($queuedTasks -contains [string]$item.task_id) { Deny "BLOCKED_QUEUE_TASK_DUPLICATE" "Queued task identities must be unique." }
        if ($sequences -contains [int64]$item.enqueue_sequence) { Deny "BLOCKED_QUEUE_SEQUENCE_DUPLICATE" "Enqueue sequences must be unique." }
        $positions += [int]$item.queue_position; $sequences += [int64]$item.enqueue_sequence; $queuedTasks += [string]$item.task_id
        $queueRecords += [pscustomobject]@{ Task=[string]$item.task_id; Position=[int]$item.queue_position; Sequence=[int64]$item.enqueue_sequence; Time=$queuedAt; Priority=[string]$item.requested_priority }
    }
    if ($positions.Count -gt 0 -and ($positions -join ",") -ne (1..$positions.Count -join ",")) { Deny "BLOCKED_QUEUE_FIFO_INVALID" "Queue records must be stored in contiguous queue-position order." }
    $bySequence = @($queueRecords | Sort-Object Sequence)
    for ($index = 1; $index -lt $bySequence.Count; $index++) { if ($bySequence[$index].Time -lt $bySequence[$index - 1].Time) { Deny "BLOCKED_QUEUE_FIFO_INVALID" "Enqueue sequence/time facts contradict FIFO order." } }
    foreach ($priorityGroup in @($queueRecords | Group-Object Priority)) {
        $fifo = @($priorityGroup.Group | Sort-Object Sequence, Time, Task)
        $positioned = @($priorityGroup.Group | Sort-Object Position)
        if (($fifo.Task -join ",") -ne ($positioned.Task -join ",")) { Deny "BLOCKED_QUEUE_FIFO_INVALID" "Equal-priority records must retain FIFO sequence/time order." }
    }

    $activeFields = @("task_id", "lane", "role", "branch", "worktree", "base_sha", "head_sha", "locked_paths", "evidence")
    if ($state -in @("implementation_running", "gate_running", "reconciling")) {
        if (-not (Required $script:Control.active $activeFields)) { Deny "BLOCKED_ACTIVE_RECORD_INCOMPLETE" "Owned normal states require a complete active record." }
        if ([string]$script:Control.active.task_id -ne [string]$owner) { Deny "BLOCKED_ACTIVE_OWNER_MISMATCH" "Token owner must equal active.task_id." }
        if ($state -eq "implementation_running" -and [string]$script:Control.active.role -ne "Developer") { Deny "BLOCKED_ACTIVE_ROLE_MISMATCH" "Implementation state requires Developer role." }
        if ($state -eq "gate_running" -and [string]$script:Control.active.role -notin @("Reviewer", "QA", "Integrator")) { Deny "BLOCKED_ACTIVE_ROLE_MISMATCH" "Gate state requires Reviewer, QA, or Integrator." }
    }
    $pauseFields = @("task_id", "lane", "branch", "worktree", "previous_owner", "paused_reason", "preempted_by", "checkpoint_sha", "pause_master_sha", "resume_condition", "unfinished_items", "locked_paths", "evidence")
    if ($state -in @("paused_preempted", "reconciling") -and -not (Required $script:Control.paused $pauseFields)) { Deny "BLOCKED_PAUSE_INCOMPLETE" "Paused/reconciling states require a complete pause record." }

    $qfFields = @("task_id", "lane", "role", "risk_gate", "goal", "why_safe", "may_touch", "must_not_touch", "locked_paths", "targeted_validation", "required_gates", "planner_required", "full_plan_required", "qa_required", "branch", "worktree", "base_sha", "head_sha", "evidence")
    if ($null -ne $script:Control.quick_fix -and -not (Required $script:Control.quick_fix $qfFields)) { Deny "BLOCKED_QUICK_FIX_INCOMPLETE" "Quick Fix capsule is incomplete." }
    if ($null -ne $script:Control.quick_fix -and [string]$script:Control.quick_fix.risk_gate -notin @("QF-1", "QF-2", "QF-3")) { Deny "BLOCKED_QUICK_FIX_RISK" "QF-4/unknown scope requires Planner/User." }
    if ($state -eq "quick_fix_running") {
        if ($null -eq $script:Control.quick_fix -or [string]$script:Control.quick_fix.task_id -ne [string]$owner -or [string]$script:Control.quick_fix.role -ne "Quick Fixer") { Deny "BLOCKED_OWNER_STATE_CONTRADICTION" "Quick Fix owner/role differs from token owner." }
        if ([string]$script:Control.quick_fix.risk_gate -eq "QF-1" -and ((@($script:Control.quick_fix.required_gates) -join ",") -ne "Integrator" -or $script:Control.quick_fix.planner_required -ne $false -or $script:Control.quick_fix.full_plan_required -ne $false -or $script:Control.quick_fix.qa_required -ne $false)) { Deny "BLOCKED_QUICK_FIX_GATE_MISMATCH" "QF-1 must use Quick Fixer -> Integrator only." }
    }
    if ($state -eq "reconciling") {
        if ($null -eq $script:Control.quick_fix -or $script:Control.quick_fix.accepted_on_master -ne $true -or [string]::IsNullOrWhiteSpace([string]$script:Control.quick_fix.accepted_head)) { Deny "BLOCKED_QUICK_FIX_NOT_ACCEPTED" "Reconciling requires accepted Quick Fix proof." }
        if ([string]$script:Control.paused.task_id -ne [string]$owner) { Deny "BLOCKED_ACTIVE_OWNER_MISMATCH" "Reconciliation owner must be the paused original." }
    }

    foreach ($residual in @($script:Control.residuals)) { if (-not (Required $residual @("task_id", "residual_owner", "disposition", "evidence"))) { Deny "BLOCKED_RESIDUAL_INCOMPLETE" "Residual ownership is incomplete." } }
    if ($state -in @("complete", "cancelled") -and @($script:Control.residuals).Count -eq 0) { Deny "BLOCKED_TERMINAL_RESIDUAL_REQUIRED" "Terminal state requires residual closeout ownership." }
    if ($state -eq "paused_preempted" -and $null -ne $script:Control.quick_fix -and (-not [string]::IsNullOrWhiteSpace([string]$script:Control.quick_fix.accepted_head) -or -not [string]::IsNullOrWhiteSpace([string]$script:Control.quick_fix.residual_owner))) {
        $ownedResidual = @($script:Control.residuals | Where-Object { $_.task_id -eq $script:Control.quick_fix.task_id -and -not [string]::IsNullOrWhiteSpace([string]$_.residual_owner) })
        if ($ownedResidual.Count -ne 1) { Deny "BLOCKED_PREEMPTION_RESIDUAL_REQUIRED" "Failed/cancelled preemption requires exact Quick Fix residual ownership." }
    }

    $parallel = $script:Control.parallel_exception
    if ($null -ne $parallel) {
        $parallelFields = @("primary_task_id", "secondary_execution_token_owner", "secondary_task_id", "secondary_lane", "secondary_role", "secondary_branch", "secondary_worktree", "secondary_head_sha", "user_approval_evidence", "scope_proof", "independence_proof", "locked_paths", "end_condition")
        if ([string]::IsNullOrWhiteSpace([string]$owner) -or $null -eq $script:Control.active) { Deny "BLOCKED_PARALLEL_PRIMARY_REQUIRED" "Parallel exception requires a valid primary owner." }
        if (-not (Required $parallel $parallelFields)) { Deny "BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE" "Parallel proof is incomplete." }
        foreach ($field in @("primary_task_id", "secondary_execution_token_owner", "secondary_task_id", "secondary_lane", "secondary_role", "secondary_branch", "secondary_worktree", "secondary_head_sha", "user_approval_evidence", "scope_proof", "independence_proof", "end_condition")) {
            if ($parallel.$field -isnot [string]) { Deny "BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE" "Parallel proof fields must use canonical string types." }
        }
        if (-not (StringArray $parallel "locked_paths" $false)) { Deny "BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE" "Parallel locked_paths must be a non-empty unique string array." }
        if ([string]$parallel.primary_task_id -ne [string]$owner -or [string]$parallel.secondary_task_id -ne [string]$parallel.secondary_execution_token_owner) { Deny "BLOCKED_PARALLEL_OWNER_MISMATCH" "Parallel owner facts are inconsistent." }
        if ([string]$parallel.secondary_execution_token_owner -eq [string]$owner) { Deny "BLOCKED_PARALLEL_OWNER_DUPLICATE" "Primary and secondary owners must differ." }
        if ($parallel.secondary_role -isnot [string] -or [string]$parallel.secondary_role -ne "Developer" -or $parallel.secondary_branch -isnot [string] -or [string]$parallel.secondary_branch -ne "lane/$($parallel.secondary_lane)" -or
            $parallel.secondary_worktree -isnot [string] -or -not [IO.Path]::IsPathRooted([string]$parallel.secondary_worktree) -or $parallel.secondary_head_sha -isnot [string] -or [string]$parallel.secondary_head_sha -notmatch '^[0-9a-fA-F]{40}$' -or
            [string]$parallel.secondary_branch -eq [string]$script:Control.active.branch -or [IO.Path]::GetFullPath([string]$parallel.secondary_worktree).TrimEnd("\") -eq [IO.Path]::GetFullPath([string]$script:Control.active.worktree).TrimEnd("\")) {
            Deny "BLOCKED_PARALLEL_GIT_FACTS_INVALID" "Parallel secondary role/branch/worktree/HEAD facts are invalid or collide with primary."
        }
        if (LocksOverlap $script:Control.active.locked_paths $parallel.locked_paths) { Deny "BLOCKED_LOCKED_PATH_OVERLAP" "Parallel locks overlap." }
    }

    switch ($Intent) {
        "Inspect" { Emit "ALLOW_INSPECT" $true "Execution authority is valid and internally consistent." }
        "StartTask" {
            if (-not $TaskId) { Deny "BLOCKED_TASK_ID_REQUIRED" "StartTask requires TaskId." }
            if ([string]$owner -eq $TaskId) { Emit "ALLOW_RESUME" $true "Requested task already owns the token." }
            if ($null -ne $parallel -and [string]$parallel.secondary_execution_token_owner -eq $TaskId) { Emit "ALLOW_START_PARALLEL" $true "Requested task is the approved secondary owner." }
            if (-not [string]::IsNullOrWhiteSpace([string]$owner)) { Emit "QUEUE_REQUIRED" $true "Another task retains the token." }
            if ($state -eq "paused_preempted") { Deny "BLOCKED_PAUSED_RECONCILIATION_REQUIRED" "Paused recovery has priority." }
            Emit "ALLOW_START" $true "No task owns the token."
        }
        "CreateWorktree" {
            if (-not $TaskId) { Deny "BLOCKED_TASK_ID_REQUIRED" "CreateWorktree requires TaskId." }
            if ([string]$owner -eq $TaskId) {
                $record = if ($state -eq "quick_fix_running") { $script:Control.quick_fix } else { $script:Control.active }
                if ($null -ne $record -and [string]$record.lane -ne $Lane) { Deny "BLOCKED_LANE_MISMATCH" "Requested lane differs from owner lane." }
                Emit "ALLOW_WORKTREE_CREATE" $true "Requested task is the primary token owner."
            }
            if ($null -ne $parallel -and [string]$parallel.secondary_execution_token_owner -eq $TaskId -and [string]$parallel.secondary_lane -eq $Lane) { Emit "ALLOW_WORKTREE_CREATE" $true "Requested task is the approved secondary owner." }
            if (-not [string]::IsNullOrWhiteSpace([string]$owner)) { Emit "QUEUE_REQUIRED" $true "Another task retains the token; no worktree may be created." }
            Deny "BLOCKED_TOKEN_OWNED" "Requested task is not an execution owner."
        }
        "ImplementationDispatch" {
            if ($state -notin @("implementation_running", "quick_fix_running")) { Deny "BLOCKED_DISPATCH_STATE" "Implementation writes require implementation_running/Developer or quick_fix_running/Quick Fixer." }
            $record = $null
            if ([string]$owner -eq $TaskId) { $record = if ($state -eq "quick_fix_running") { $script:Control.quick_fix } else { $script:Control.active } }
            elseif ($null -ne $parallel -and [string]$parallel.secondary_execution_token_owner -eq $TaskId) {
                if (-not (Required $parallel @("secondary_role", "secondary_branch", "secondary_worktree", "secondary_head_sha"))) { Deny "BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE" "Secondary dispatch Git/role facts are incomplete." }
                $record = [pscustomobject]@{ task_id=$TaskId; lane=$parallel.secondary_lane; role=$parallel.secondary_role; branch=$parallel.secondary_branch; worktree=$parallel.secondary_worktree; head_sha=$parallel.secondary_head_sha }
            }
            else { Deny "BLOCKED_TOKEN_OWNED" "Only an execution owner may receive implementation dispatch." }
            if ([string]$record.task_id -ne $TaskId -or [string]$record.lane -ne $Lane) { Deny "BLOCKED_LANE_MISMATCH" "Dispatch task/lane differs from board." }
            $expectedRole = if ($state -eq "quick_fix_running") { "Quick Fixer" } else { "Developer" }
            if ([string]$record.role -ne $expectedRole) { Deny "BLOCKED_DISPATCH_ROLE" "Dispatch role is not write-authorized for this state." }
            CheckGitRecord $record ([string]$record.head_sha) ([string]$record.branch)
            Emit "ALLOW_DISPATCH" $true "State, role, token, lane, worktree, and HEAD facts match."
        }
        "QuickFixPreempt" {
            if ($state -eq "quick_fix_running") { Deny "BLOCKED_NESTED_PREEMPTION" "Quick Fix preemption cannot nest." }
            if ($state -ne "paused_preempted" -or $null -ne $owner) { Deny "BLOCKED_PAUSE_REQUIRED" "Preemption requires owner-null paused_preempted." }
            if ([string]$script:Control.paused.preempted_by -ne $TaskId -or [string]$script:Control.quick_fix.task_id -ne $TaskId -or [string]$script:Control.quick_fix.lane -ne $Lane) { Deny "BLOCKED_QUICK_FIX_MISMATCH" "Requested Quick Fix differs from pause/capsule." }
            if (LocksOverlap $script:Control.paused.locked_paths $script:Control.quick_fix.locked_paths) { Deny "BLOCKED_LOCKED_PATH_OVERLAP" "Quick Fix locks overlap paused original." }
            CheckPausedCheckpoint $script:Control.paused
            Emit "ALLOW_PREEMPT_CHECKPOINTED" $true "Original is clean, checkpointed, and disjoint."
        }
        "Reconcile" {
            if ($state -ne "quick_fix_running" -or $null -eq $script:Control.paused) { Deny "BLOCKED_RECONCILIATION_STATE" "Reconciliation requires accepted preempting Quick Fix." }
            if ([string]$script:Control.paused.task_id -ne $TaskId -or [string]$script:Control.paused.lane -ne $Lane) { Deny "BLOCKED_RECONCILIATION_OWNER" "Requested task/lane differs from paused original." }
            if ($script:Control.quick_fix.accepted_on_master -ne $true -or [string]::IsNullOrWhiteSpace([string]$script:Control.quick_fix.accepted_head)) { Deny "BLOCKED_QUICK_FIX_NOT_ACCEPTED" "Quick Fix acceptance is not proven." }
            CheckPausedCheckpoint $script:Control.paused
            if (-not (IsAncestor ([string]$script:Control.quick_fix.accepted_head) "master")) { Deny "BLOCKED_QUICK_FIX_NOT_ON_MASTER" "Accepted Quick Fix is not on master." }
            if (-not (IsAncestor ([string]$script:Control.paused.pause_master_sha) "master")) { Deny "BLOCKED_PAUSE_BASE_DRIFT" "Pause master is not an ancestor of current master." }
            Emit "ALLOW_RECONCILE" $true "Accepted master and preserved checkpoint facts allow merge reconciliation."
        }
        "Resume" {
            if ($state -ne "reconciling" -or [string]$owner -ne $TaskId) { Deny "BLOCKED_RESUME_STATE" "Resume requires original reconciling ownership." }
            $resumeFields = @("reconciliation_checkpoint_sha", "reconciliation_validation_passed", "reconciliation_validation_evidence")
            if (-not (Required $script:Control.paused $resumeFields) -or $script:Control.paused.reconciliation_validation_passed -ne $true) { Deny "BLOCKED_RECONCILIATION_VALIDATION" "Resume requires durable reconciliation validation proof." }
            $checkpoint = [string]$script:Control.paused.reconciliation_checkpoint_sha
            if ($checkpoint -eq [string]$script:Control.paused.checkpoint_sha) { Deny "BLOCKED_RECONCILIATION_CHECKPOINT_STALE" "Untouched pre-merge checkpoint cannot resume." }
            if ([string]$script:Control.active.head_sha -ne $checkpoint) { Deny "BLOCKED_RECONCILIATION_HEAD_MISMATCH" "Active HEAD must name the reconciliation checkpoint." }
            CheckGitRecord $script:Control.paused $checkpoint ([string]$script:Control.paused.branch)
            if (-not (IsAncestor ([string]$script:Control.quick_fix.accepted_head) "master")) { Deny "BLOCKED_QUICK_FIX_NOT_ON_MASTER" "Accepted Quick Fix is not on master." }
            if (-not (IsAncestor ([string]$script:Control.paused.pause_master_sha) "master")) { Deny "BLOCKED_PAUSE_BASE_DRIFT" "Pause master is not on current master." }
            if (-not (IsAncestor "master" $checkpoint)) { Deny "BLOCKED_MASTER_NOT_MERGED" "Current master is not merged into preserved lane." }
            Emit "ALLOW_RESUME" $true "Accepted Quick Fix, master merge, clean checkpoint, and validation proof match."
        }
    }
}
catch { Deny "BLOCKED_INTERNAL_ERROR" $_.Exception.Message }
