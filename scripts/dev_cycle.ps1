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
Write-Host " ConnLab Dev Cycle"
Write-Host " Task: $task"
Write-Host " Max Fix Attempts: $MaxFixAttempts"
Write-Host "===================================="

& ".\scripts\run_task.ps1" $task
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ run_task failed or was blocked."
    exit $LASTEXITCODE
}

& ".\scripts\run_tests.ps1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dev cycle completed without auto-fix."
    exit 0
}

for ($attempt = 1; $attempt -le $MaxFixAttempts; $attempt++) {
    Write-Host "------------------------------------"
    Write-Host " Auto-fix attempt $attempt / $MaxFixAttempts"
    Write-Host "------------------------------------"

    & ".\scripts\fix_tests.ps1" $task
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ fix_tests failed or was blocked."
        exit $LASTEXITCODE
    }

    & ".\scripts\run_tests.ps1"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dev cycle completed after auto-fix."
        exit 0
    }
}

Write-Host "❌ Dev cycle stopped after $MaxFixAttempts auto-fix attempts."
Write-Host "Please review logs/pytest_last.log and the latest code changes before continuing."
exit 1
