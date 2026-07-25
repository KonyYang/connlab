[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,

    [Parameter(Mandatory = $true)]
    [string]$Summary,

    [Parameter(Mandatory = $true)]
    [string[]]$Paths
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Normalize-RepoPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $normalized = $Path.Replace("\", "/")
    while ($normalized.StartsWith("./", [System.StringComparison]::Ordinal)) {
        $normalized = $normalized.Substring(2)
    }
    return $normalized
}

$repoRootOutput = & git rev-parse --show-toplevel 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Run this script from inside a Git worktree."
}
$repoRoot = [System.IO.Path]::GetFullPath((($repoRootOutput | Select-Object -First 1).Trim())).TrimEnd("\")

$branch = (& git branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch)) {
    throw "Cannot detect current Git branch."
}
if ($branch -notlike "lane/*") {
    throw "Lane checkpoint commits are allowed only on lane/* branches. Current branch: $branch"
}

$initialIndex = @(git diff --cached --name-only)
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect the Git index."
}
if ($initialIndex.Count -ne 0) {
    throw "The Git index must be empty before exact-path staging."
}

$expected = @(
    $Paths |
        ForEach-Object {
            if ([string]::IsNullOrWhiteSpace($_)) {
                throw "Paths must not contain an empty value."
            }

            $absolute = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $_))
            if (-not $absolute.StartsWith($repoRoot + "\", [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Path escapes the repository: $_"
            }
            Normalize-RepoPath -Path $_
        } |
        Sort-Object -Unique
)
if ($expected.Count -eq 0) {
    throw "At least one exact path is required."
}
if ($expected -contains "docs/task_board.md") {
    throw "docs/task_board.md is Integrator-owned and cannot be staged by a lane checkpoint script."
}

$statusPaths = @(
    git status --porcelain=v1 --untracked-files=all |
        ForEach-Object { Normalize-RepoPath -Path $_.Substring(3) } |
        Sort-Object -Unique
)
if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect worktree status."
}

$ambient = @(Compare-Object -ReferenceObject $expected -DifferenceObject $statusPaths |
    Where-Object { $_.SideIndicator -eq "=>" } |
    ForEach-Object { $_.InputObject })
if ($ambient.Count -ne 0) {
    throw "Worktree contains changes outside the exact package:`n$($ambient -join "`n")"
}

try {
    & git add -- $expected
    if ($LASTEXITCODE -ne 0) {
        throw "Exact-path staging failed."
    }

    $staged = @(git diff --cached --name-only | ForEach-Object { Normalize-RepoPath -Path $_ } | Sort-Object -Unique)
    if ($LASTEXITCODE -ne 0) {
        throw "Could not inspect staged paths."
    }

    $scopeDifference = @(Compare-Object -ReferenceObject $expected -DifferenceObject $staged)
    if ($scopeDifference.Count -ne 0) {
        throw "Staged paths do not match the exact package."
    }

    & git diff --cached --check
    if ($LASTEXITCODE -ne 0) {
        throw "git diff --cached --check failed."
    }

    $message = "${TaskId}: $Summary"
    & git commit -m $message
    if ($LASTEXITCODE -ne 0) {
        throw "Local lane checkpoint commit failed."
    }
}
catch {
    & git restore --staged -- $expected 2>$null
    throw
}

$postIndex = @(git diff --cached --name-only)
if ($postIndex.Count -ne 0) {
    throw "Commit succeeded but the Git index is not empty."
}
$postStatus = @(git status --porcelain=v1 --untracked-files=all)
if ($postStatus.Count -ne 0) {
    throw "Commit succeeded but the lane worktree is not clean."
}

$commit = (& git rev-parse HEAD).Trim()
Write-Host "Created local lane checkpoint commit."
Write-Host "Branch: $branch"
Write-Host "Commit: $commit"
Write-Host "Paths: $($expected.Count)"
Write-Host "Remote push: not performed"
