param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Inspect', 'Retire')]
    [string]$Action,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$TaskId,
    [Parameter(Mandatory = $true)]
    [string]$Branch,
    [Parameter(Mandatory = $true)]
    [string]$Worktree,
    [Parameter(Mandatory = $true)]
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

function Invoke-Git([string[]]$Arguments) {
    $output = & git -C $RepoRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($output -join "`n") }
    return @($output)
}

function Emit([string]$Code, [bool]$Allowed, [string]$Reason, [hashtable]$Facts) {
    $result = [ordered]@{
        schema = 'connlab.serial-worktree-result'
        version = 1
        code = $Code
        allowed = $Allowed
        action = $Action
        task_id = $TaskId
        changed = $false
        facts = $Facts
        reason = $Reason
    }
    if ($Json) { $result | ConvertTo-Json -Depth 8 -Compress } else { $result.GetEnumerator() | ForEach-Object { "{0}: {1}" -f $_.Key, $_.Value } }
}

try {
    $root = (Resolve-Path -LiteralPath $RepoRoot).Path
    $target = (Resolve-Path -LiteralPath $Worktree).Path
    $top = (Resolve-Path -LiteralPath (@(Invoke-Git @('rev-parse', '--show-toplevel')))[0].Trim()).Path
    $primaryBranch = (@(Invoke-Git @('branch', '--show-current')))[0].Trim()
    if ($top -ne $root -or $primaryBranch -ne 'master' -or -not (Test-Path -LiteralPath (Join-Path $root '.git') -PathType Container)) {
        throw 'Primary master worktree could not be verified.'
    }
    $listed = Invoke-Git @('worktree', 'list', '--porcelain')
    $registered = @($listed | Where-Object { $_ -like 'worktree *' } | ForEach-Object {
        (Resolve-Path -LiteralPath $_.Substring(9)).Path
    })
    if ($target -notin $registered) { throw 'Expected worktree is not registered.' }
    $actualBranch = (& git -C $target branch --show-current).Trim()
    $actualHead = (& git -C $target rev-parse HEAD).Trim()
    $dirty = @(& git -C $target status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0) { throw 'Worktree Git facts could not be read.' }
    if ($actualBranch -ne $Branch -or $actualHead -ne $ExpectedHead) { throw 'Worktree branch or HEAD differs from expected authority.' }
    $facts = [ordered]@{ branch = $actualBranch; worktree = $target; head = $actualHead; clean = ($dirty.Count -eq 0); dirty_paths = $dirty }
    if ($Action -eq 'Inspect') {
        Emit 'ALLOW_WORKTREE_INSPECT' $true 'Exact worktree facts verified.' $facts
        exit 0
    }
    if (-not $IntegrationCommit -or -not $UserCloseRef -or -not $HostStopped) { throw 'Retirement requires integration, User close, and stopped-host proof.' }
    if ($dirty.Count -ne 0) { Emit 'BLOCKED_RETIREMENT_PENDING' $false 'Dirty worktree is retained.' $facts; exit 2 }
    & git -C $root merge-base --is-ancestor $ExpectedHead $IntegrationCommit 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'Expected worktree HEAD is not integrated.' }
    if ($DryRun) { Emit 'ALLOW_WORKTREE_RETIRE_DRY_RUN' $true 'Retirement preconditions verified; no change made.' $facts; exit 0 }
    & git -C $root worktree remove -- $target
    if ($LASTEXITCODE -ne 0) { throw 'Non-forced worktree retirement failed.' }
    $facts.removed = $true
    $result = [ordered]@{ schema = 'connlab.serial-worktree-result'; version = 1; code = 'ALLOW_WORKTREE_RETIRE'; allowed = $true; action = $Action; task_id = $TaskId; changed = $true; facts = $facts; reason = 'Clean integrated worktree retired without deleting its branch.' }
    if ($Json) { $result | ConvertTo-Json -Depth 8 -Compress } else { $result.GetEnumerator() | ForEach-Object { "{0}: {1}" -f $_.Key, $_.Value } }
    exit 0
} catch {
    Emit 'BLOCKED_WORKTREE_FACTS' $false $_.Exception.Message @{}
    exit 2
}
