param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,

    [Parameter(Mandatory = $true)]
    [string]$Summary
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$branch = (git branch --show-current).Trim()
if ([string]::IsNullOrWhiteSpace($branch)) {
    throw "Cannot detect current git branch."
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$message = "${TaskId}: $Summary ($timestamp)"

git add -A

$hasStaged = git diff --cached --name-only
if ([string]::IsNullOrWhiteSpace(($hasStaged | Out-String).Trim())) {
    Write-Host "No staged changes detected. Skip commit/push."
    exit 0
}

git commit -m $message
git push origin $branch

Write-Host "Committed and pushed to origin/$branch"
Write-Host "Message: $message"
