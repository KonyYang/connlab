[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Create", "Inspect", "List", "Retire")]
    [string]$Action,

    [string]$Lane,

    [string]$BaseRef = "HEAD",

    [string]$IntegrationRef = "master",

    [string]$Branch,

    [string]$WorktreeRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Directory,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & git -C $Directory @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($exitCode -ne 0) {
        $rendered = $Arguments -join " "
        throw "git $rendered failed in ${Directory}:`n$($output -join "`n")"
    }
    return @($output)
}

function Get-NormalizedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    return [System.IO.Path]::GetFullPath($Path).TrimEnd("\")
}

$repoRootOutput = & git rev-parse --show-toplevel 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Run this script from inside the ConnLab Git repository."
}
$repoRoot = Get-NormalizedPath -Path (($repoRootOutput | Select-Object -First 1).Trim())

if ([string]::IsNullOrWhiteSpace($WorktreeRoot)) {
    $repoParent = Split-Path -Parent $repoRoot
    $repoName = Split-Path -Leaf $repoRoot
    $WorktreeRoot = Join-Path $repoParent "${repoName}-worktrees"
}
$WorktreeRoot = Get-NormalizedPath -Path $WorktreeRoot

if ($Action -eq "List") {
    Invoke-Git -Directory $repoRoot -Arguments @("worktree", "list", "--porcelain")
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Lane)) {
    throw "-Lane is required for Action $Action."
}
if ($Lane -notmatch "^[a-z0-9][a-z0-9._-]*$") {
    throw "Lane must use lowercase letters, digits, dots, underscores, or hyphens."
}

if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = "lane/$Lane"
}
if ($Branch -notmatch "^lane/[a-z0-9][a-z0-9._/-]*$") {
    throw "Branch must remain under lane/ and use a stable lowercase lane name."
}

$target = Get-NormalizedPath -Path (Join-Path $WorktreeRoot $Lane)

switch ($Action) {
    "Create" {
        $primaryStatus = @(Invoke-Git -Directory $repoRoot -Arguments @("status", "--porcelain=v1"))
        if ($primaryStatus.Count -ne 0) {
            throw "Primary worktree must be clean before creating a parallel lane."
        }

        & git -C $repoRoot show-ref --verify --quiet "refs/heads/$Branch"
        if ($LASTEXITCODE -eq 0) {
            throw "Branch already exists: $Branch"
        }
        if ($LASTEXITCODE -ne 1) {
            throw "Could not verify whether branch exists: $Branch"
        }
        if (Test-Path -LiteralPath $target) {
            throw "Worktree target already exists: $target"
        }

        New-Item -ItemType Directory -Path $WorktreeRoot -Force | Out-Null
        Invoke-Git -Directory $repoRoot -Arguments @(
            "worktree",
            "add",
            "--quiet",
            "-b",
            $Branch,
            $target,
            $BaseRef
        ) | Out-Host

        $head = (Invoke-Git -Directory $target -Arguments @("rev-parse", "HEAD") | Select-Object -First 1).Trim()
        Write-Host "Lane worktree created."
        Write-Host "Lane: $Lane"
        Write-Host "Branch: $Branch"
        Write-Host "Path: $target"
        Write-Host "Base commit: $head"
    }

    "Inspect" {
        if (-not (Test-Path -LiteralPath $target -PathType Container)) {
            throw "Lane worktree does not exist: $target"
        }

        $actualBranch = (Invoke-Git -Directory $target -Arguments @("branch", "--show-current") | Select-Object -First 1).Trim()
        $head = (Invoke-Git -Directory $target -Arguments @("rev-parse", "HEAD") | Select-Object -First 1).Trim()
        $status = @(Invoke-Git -Directory $target -Arguments @("status", "--short"))
        $range = "$IntegrationRef...HEAD"
        $counts = (Invoke-Git -Directory $target -Arguments @("rev-list", "--left-right", "--count", $range) | Select-Object -First 1).Trim()

        Write-Host "Lane: $Lane"
        Write-Host "Branch: $actualBranch"
        Write-Host "Path: $target"
        Write-Host "HEAD: $head"
        Write-Host "$IntegrationRef...HEAD: $counts"
        Write-Host "Status entries: $($status.Count)"
        if ($status.Count -gt 0) {
            $status | Out-Host
        }
    }

    "Retire" {
        if (-not (Test-Path -LiteralPath $target -PathType Container)) {
            throw "Lane worktree does not exist: $target"
        }

        $actualBranch = (Invoke-Git -Directory $target -Arguments @("branch", "--show-current") | Select-Object -First 1).Trim()
        if ($actualBranch -ne $Branch) {
            throw "Expected branch $Branch but found $actualBranch."
        }

        $status = @(Invoke-Git -Directory $target -Arguments @("status", "--porcelain=v1"))
        if ($status.Count -ne 0) {
            throw "Lane worktree is dirty. Retire refuses to discard or force-remove it."
        }

        $head = (Invoke-Git -Directory $target -Arguments @("rev-parse", "HEAD") | Select-Object -First 1).Trim()
        & git -C $repoRoot merge-base --is-ancestor $head $IntegrationRef
        if ($LASTEXITCODE -eq 1) {
            throw "Lane HEAD $head is not integrated into $IntegrationRef."
        }
        if ($LASTEXITCODE -ne 0) {
            throw "Could not verify integration ancestry for $head."
        }

        Invoke-Git -Directory $repoRoot -Arguments @("worktree", "remove", $target) | Out-Null
        Invoke-Git -Directory $repoRoot -Arguments @("branch", "-d", $Branch) | Out-Host

        Write-Host "Lane worktree retired without force."
        Write-Host "Lane: $Lane"
        Write-Host "Integrated HEAD: $head"
        Write-Host "Integration ref: $IntegrationRef"
    }
}
