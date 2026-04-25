param(
    [string]$task
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
. "$PSScriptRoot\_codex_runtime.ps1"

Write-Host "===================================="
Write-Host " Auto Fix Failed Tests"
Write-Host " Task: $task"
Write-Host "===================================="

$taskBoard = "docs/task_board.md"
$taskFile = "tasks/$task.md"
$logFile = "logs/pytest_last.log"

if (!(Test-Path $taskBoard)) {
    Write-Host "❌ Task board not found: $taskBoard"
    exit 1
}

if (!(Test-Path $taskFile)) {
    Write-Host "❌ Task file not found: $taskFile"
    Write-Host "Example: .\scripts\fix_tests.ps1 TASK_002_CONFIG_LOGGING"
    exit 1
}

if (!(Test-Path $logFile)) {
    Write-Host "❌ pytest log not found: $logFile"
    Write-Host "Please run .\scripts\run_tests.ps1 first."
    exit 1
}

$taskBoardContent = Get-Content $taskBoard -Encoding UTF8 -Raw
$activeTaskMatch = [regex]::Match($taskBoardContent, 'Current Active Task:\s*`([^`]+)`')
$phaseMatch = [regex]::Match($taskBoardContent, 'Current Phase:\s*`([^`]+)`')

if (!$activeTaskMatch.Success) {
    Write-Host "❌ Could not determine current active task from $taskBoard"
    exit 1
}

$activeTask = $activeTaskMatch.Groups[1].Value
$currentPhase = if ($phaseMatch.Success) { $phaseMatch.Groups[1].Value } else { "Unknown Phase" }

if ($task -ne $activeTask) {
    Write-Host "❌ Task mismatch"
    Write-Host "Requested: $task"
    Write-Host "Active from board: $activeTask"
    Write-Host "Fix only the current active task."
    exit 1
}

$failureLog = Get-Content $logFile -Encoding UTF8 -Raw

$prompt = @(
    "Fix the current task code based on the pytest failure log."
    ""
    "Read and obey documents in this order before acting:"
    "1. AGENTS.md"
    "2. $taskBoard"
    "3. $taskFile"
    ""
    "Current task file:"
    "$taskFile"
    ""
    "Must follow:"
    "- AGENTS.md"
    "- docs/task_board.md"
    "- AUTO_FIX_SKILL.md"
    "- TASK_REVIEW_CHECKLIST.md"
    "- TESTING_SKILL.md"
    ""
    "Current phase: $currentPhase"
    "Current active task: $activeTask"
    ""
    "Pytest failure log:"
    ""
    $failureLog
    ""
    "Requirements:"
    "1. State the current phase, task, and why only this task may be fixed now."
    "2. Diagnose the failure first."
    "3. Make only the minimum necessary fix."
    "4. Do not delete or skip tests."
    "5. Do not implement extra features."
    "6. Provide the test command to rerun."
    "7. If the fix is completed and verified, update docs/task_board.md."
    "8. Do not move to the next task."
) -join "`n"

$exitCode = Invoke-CodexCli -Prompt $prompt
exit $exitCode
