param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Create', 'Inspect', 'Retire')]
    [string]$Action,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$TaskId,
    [Parameter(Mandatory = $true)]
    [string]$Branch,
    [Parameter(Mandatory = $true)]
    [string]$Worktree,
    [string]$WorktreeRoot,
    [ValidatePattern('^[0-9a-f]{40}$')]
    [string]$ExpectedBase,
    [ValidatePattern('^[0-9a-f]{40}$')]
    [string]$ExpectedHead,
    [string]$IntegrationCommit,
    [string]$UserCloseRef,
    [switch]$HostStopped,
    [switch]$DryRun,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Invoke-Git([string]$Directory, [string[]]$Arguments, [switch]$AllowFailure) {
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $gitOutput = @(& git -C $Directory @Arguments 2>&1)
        $gitExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if (-not $AllowFailure -and $gitExitCode -ne 0) { throw ($gitOutput -join "`n") }
    return [pscustomobject]@{ Output = $gitOutput; ExitCode = $gitExitCode }
}

function Emit([string]$Code, [bool]$Allowed, [object]$Changed, [string]$Reason, [hashtable]$Facts) {
    $result = [ordered]@{
        schema = 'connlab.serial-worktree-result'
        version = 1
        code = $Code
        allowed = $Allowed
        action = $Action
        task_id = $TaskId
        changed = $Changed
        facts = $Facts
        reason = $Reason
    }
    if ($Json) { $result | ConvertTo-Json -Depth 8 -Compress } else { $result.GetEnumerator() | ForEach-Object { "{0}: {1}" -f $_.Key, $_.Value } }
}

function Get-RegisteredWorktrees([string]$PrimaryRoot) {
    $porcelain = (Invoke-Git $PrimaryRoot @('worktree', 'list', '--porcelain')).Output
    return @($porcelain | Where-Object { $_ -like 'worktree *' } | ForEach-Object {
        [IO.Path]::GetFullPath($_.Substring(9).Trim())
    })
}

function Get-TargetFacts([string]$PrimaryRoot, [string]$TargetPath, [string]$ExpectedBranch, [string]$BaseSha) {
    $branchProbe = Invoke-Git $PrimaryRoot @('show-ref', '--verify', '--quiet', "refs/heads/$ExpectedBranch") -AllowFailure
    $branchExists = $branchProbe.ExitCode -eq 0
    $pathExists = Test-Path -LiteralPath $TargetPath
    $registered = $TargetPath -in (Get-RegisteredWorktrees $PrimaryRoot)
    $actualBranch = $null
    $actualHead = $null
    $dirtyPaths = @()
    if ($pathExists -and $registered) {
        $actualBranch = ((Invoke-Git $TargetPath @('branch', '--show-current')).Output -join "`n").Trim()
        $actualHead = ((Invoke-Git $TargetPath @('rev-parse', 'HEAD')).Output -join "`n").Trim()
        $dirtyPaths = @((Invoke-Git $TargetPath @('status', '--porcelain=v1', '--untracked-files=all')).Output)
    }
    $clean = $pathExists -and $registered -and $dirtyPaths.Count -eq 0
    return [ordered]@{
        branch = $ExpectedBranch; worktree = $TargetPath; base_sha = $BaseSha; head_sha = $actualHead
        clean = $clean; branch_exists = $branchExists; path_exists = $pathExists
        registered = $registered; actual_branch = $actualBranch; dirty_paths = $dirtyPaths
        exact = ($branchExists -and $pathExists -and $registered -and $actualBranch -eq $ExpectedBranch -and $actualHead -eq $BaseSha -and $clean)
    }
}

try {
    $primaryRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
    $primaryTop = ((Invoke-Git $primaryRoot @('rev-parse', '--show-toplevel')).Output -join "`n").Trim()
    $primaryTop = (Resolve-Path -LiteralPath $primaryTop).Path
    $primaryBranch = ((Invoke-Git $primaryRoot @('branch', '--show-current')).Output -join "`n").Trim()
    if ($primaryTop -ne $primaryRoot -or $primaryBranch -ne 'master' -or -not (Test-Path -LiteralPath (Join-Path $primaryRoot '.git') -PathType Container)) {
        Emit 'BLOCKED_PRIMARY_FACTS' $false $false 'Primary master worktree could not be verified.' @{}
        exit 2
    }

    if ($Action -eq 'Create') {
        if (-not $ExpectedBase -or -not $WorktreeRoot -or $ExpectedHead) {
            Emit 'BLOCKED_WORKTREE_INPUT' $false $false 'Create requires WorktreeRoot and ExpectedBase, and does not accept ExpectedHead.' @{}
            exit 2
        }
        if (-not (Test-Path -LiteralPath $WorktreeRoot -PathType Container)) {
            Emit 'BLOCKED_WORKTREE_INPUT' $false $false 'WorktreeRoot must be an existing directory.' @{}
            exit 2
        }
        $normalizedWorktreeRoot = (Resolve-Path -LiteralPath $WorktreeRoot).Path
        $targetWorktree = [IO.Path]::GetFullPath($Worktree)
        $targetParent = [IO.Path]::GetDirectoryName($targetWorktree)
        if (-not $targetParent -or $targetParent -ne $normalizedWorktreeRoot -or $targetWorktree -eq $normalizedWorktreeRoot) {
            Emit 'BLOCKED_WORKTREE_INPUT' $false $false 'Worktree must be a direct child of WorktreeRoot.' @{ worktree = $targetWorktree; worktree_root = $normalizedWorktreeRoot }
            exit 2
        }
        $primaryHead = ((Invoke-Git $primaryRoot @('rev-parse', 'HEAD')).Output -join "`n").Trim()
        $primaryDirty = @((Invoke-Git $primaryRoot @('status', '--porcelain=v1', '--untracked-files=all')).Output)
        if ($primaryHead -ne $ExpectedBase -or $primaryDirty.Count -ne 0) {
            Emit 'BLOCKED_PRIMARY_FACTS' $false $false 'Primary HEAD or cleanliness differs from the approved base.' @{ head_sha = $primaryHead; clean = ($primaryDirty.Count -eq 0); dirty_paths = $primaryDirty }
            exit 2
        }

        $beforeFacts = Get-TargetFacts $primaryRoot $targetWorktree $Branch $ExpectedBase
        if ($beforeFacts.exact) {
            $beforeFacts.Remove('exact')
            Emit 'ALLOW_WORKTREE_REUSE' $true $false 'Existing exact clean task worktree reused.' $beforeFacts
            exit 0
        }
        if ($beforeFacts.branch_exists -or $beforeFacts.path_exists -or $beforeFacts.registered) {
            $beforeFacts.Remove('exact')
            Emit 'BLOCKED_WORKTREE_CONFLICT' $false $false 'Existing branch, path, or registration does not form the exact clean host.' $beforeFacts
            exit 2
        }

        $createResult = Invoke-Git $primaryRoot @('worktree', 'add', '-b', $Branch, $targetWorktree, $ExpectedBase) -AllowFailure
        $afterFacts = Get-TargetFacts $primaryRoot $targetWorktree $Branch $ExpectedBase
        if ($afterFacts.exact) {
            $afterFacts.Remove('exact')
            Emit 'ALLOW_WORKTREE_CREATE' $true $true 'Exact clean task worktree created and verified.' $afterFacts
            exit 0
        }
        $failureText = ($createResult.Output -join "`n")
        $afterFacts.git_error = $failureText
        $afterFacts.Remove('exact')
        if ($afterFacts.branch_exists -or $afterFacts.path_exists -or $afterFacts.registered) {
            Emit 'BLOCKED_WORKTREE_PARTIAL' $false $null 'Worktree creation left a partial state; retained without cleanup.' $afterFacts
        } elseif ($failureText -match '(?i)access.*denied|permission denied|not permitted') {
            Emit 'BLOCKED_WORKTREE_PERMISSION' $false $false 'Worktree creation was denied without observable Git or path changes.' $afterFacts
        } else {
            Emit 'BLOCKED_WORKTREE_INPUT' $false $false 'Worktree creation failed without observable Git or path changes.' $afterFacts
        }
        exit 2
    }

    if (-not $ExpectedHead) {
        Emit 'BLOCKED_WORKTREE_INPUT' $false $false 'Inspect and Retire require ExpectedHead.' @{}
        exit 2
    }
    $targetWorktree = (Resolve-Path -LiteralPath $Worktree).Path
    if ($targetWorktree -notin (Get-RegisteredWorktrees $primaryRoot)) {
        Emit 'BLOCKED_WORKTREE_FACTS' $false $false 'Expected worktree is not registered.' @{}
        exit 2
    }
    $actualBranch = ((Invoke-Git $targetWorktree @('branch', '--show-current')).Output -join "`n").Trim()
    $actualHead = ((Invoke-Git $targetWorktree @('rev-parse', 'HEAD')).Output -join "`n").Trim()
    $dirtyPaths = @((Invoke-Git $targetWorktree @('status', '--porcelain=v1', '--untracked-files=all')).Output)
    if ($actualBranch -ne $Branch -or $actualHead -ne $ExpectedHead) { throw 'Worktree branch or HEAD differs from expected authority.' }
    $facts = [ordered]@{ branch = $actualBranch; worktree = $targetWorktree; head = $actualHead; clean = ($dirtyPaths.Count -eq 0); dirty_paths = $dirtyPaths }
    if ($Action -eq 'Inspect') {
        Emit 'ALLOW_WORKTREE_INSPECT' $true $false 'Exact worktree facts verified.' $facts
        exit 0
    }
    if (-not $IntegrationCommit -or -not $UserCloseRef -or -not $HostStopped) { throw 'Retirement requires integration, User close, and stopped-host proof.' }
    if ($dirtyPaths.Count -ne 0) { Emit 'BLOCKED_RETIREMENT_PENDING' $false $false 'Dirty worktree is retained.' $facts; exit 2 }
    $ancestor = Invoke-Git $primaryRoot @('merge-base', '--is-ancestor', $ExpectedHead, $IntegrationCommit) -AllowFailure
    if ($ancestor.ExitCode -ne 0) { throw 'Expected worktree HEAD is not integrated.' }
    if ($DryRun) { Emit 'ALLOW_WORKTREE_RETIRE_DRY_RUN' $true $false 'Retirement preconditions verified; no change made.' $facts; exit 0 }
    $removeResult = Invoke-Git $primaryRoot @('worktree', 'remove', '--', $targetWorktree) -AllowFailure
    if ($removeResult.ExitCode -ne 0) { throw 'Non-forced worktree retirement failed.' }
    $facts.removed = $true
    Emit 'ALLOW_WORKTREE_RETIRE' $true $true 'Clean integrated worktree retired without deleting its branch.' $facts
    exit 0
} catch {
    Emit 'BLOCKED_WORKTREE_FACTS' $false $false $_.Exception.Message @{}
    exit 2
}
