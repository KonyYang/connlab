param(
    [string]$task,
    [int]$MaxFixAttempts = 3
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ([string]::IsNullOrWhiteSpace($task)) {
    Write-Host "❌ Task is required."
    Write-Host "Example: .\scripts\dev_cycle.ps1 TASK_002_CONFIG_LOGGING"
    exit 1
}

if ($MaxFixAttempts -lt 0) {
    Write-Host "❌ MaxFixAttempts must be 0 or greater."
    exit 1
}

Write-Host "===================================="
Write-Host " ConnLab Orchestrated Task Cycle"
Write-Host " Task: $task"
Write-Host "===================================="

if ($MaxFixAttempts -ne 3) {
    Write-Host "MaxFixAttempts is retained for CLI compatibility but is no longer used."
    Write-Host "Developer/Reviewer fix passes now run inside the isolated lane workflow."
}

& ".\scripts\run_task.ps1" -Task $task
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ run_task failed or was blocked."
    exit $LASTEXITCODE
}

Write-Host "✅ Orchestrated task cycle returned successfully."
Write-Host "Validation and bounded fix passes are owned by the lane worktree role chain."
exit 0
