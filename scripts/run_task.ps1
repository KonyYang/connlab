param(
    [string]$task
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
. "$PSScriptRoot\_codex_runtime.ps1"

Write-Host "===================================="
Write-Host " Running Task: $task"
Write-Host "===================================="

$taskBoard = "docs/task_board.md"
$taskFile = "tasks/$task.md"

if (!(Test-Path $taskBoard)) {
    Write-Host "❌ Task board not found: $taskBoard"
    exit 1
}

if (!(Test-Path $taskFile)) {
    Write-Host "❌ Task file not found: $taskFile"
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
    Write-Host "Read $taskBoard and execute only the current active task."
    exit 1
}

$prompt = @(
    "Read and obey documents in this order before acting:"
    "1. AGENTS.md"
    "2. $taskBoard"
    "3. $taskFile"
    ""
    "Must follow:"
    "- AGENTS.md"
    "- docs/task_board.md"
    "- docs/project_management/TASK_EXECUTION_SKILL.md"
    "- docs/project_management/TASK_REVIEW_CHECKLIST.md"
    "- docs/project_management/TESTING_SKILL.md"
    ""
    "Current phase: $currentPhase"
    "Current active task: $activeTask"
    ""
    "Requirements:"
    "1. State the current phase, task ID, and why this task is allowed now."
    "2. Output a design plan first."
    "3. Then write code."
    "4. Add or update pytest tests."
    "5. Run relevant tests."
    "6. Update docs/task_board.md after completion."
    "7. Provide run instructions."
    "8. Do not move to the next task."
) -join "`n"

$exitCode = Invoke-CodexCli -Prompt $prompt
exit $exitCode
