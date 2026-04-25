param(
    [string]$task
)

Write-Host "===================================="
Write-Host " Auto Fix Failed Tests"
Write-Host " Task: $task"
Write-Host "===================================="

$taskFile = "tasks/$task.md"
$logFile = "logs/pytest_last.log"

if (!(Test-Path $taskFile)) {
    Write-Host "❌ Task file not found: $taskFile"
    Write-Host "Example: .\scripts\fix_tests.ps1 TASK_002_DATABASE"
    exit 1
}

if (!(Test-Path $logFile)) {
    Write-Host "❌ pytest log not found: $logFile"
    Write-Host "Please run .\scripts\run_tests.ps1 first."
    exit 1
}

$failureLog = Get-Content $logFile -Raw

$prompt = @"
请根据 pytest 失败日志修复当前任务相关代码。

当前任务文件：
$taskFile

必须遵守：
- AGENTS.md
- AUTO_FIX_SKILL.md
- TASK_REVIEW_CHECKLIST.md
- TESTING_SKILL.md

pytest 失败日志如下：

$failureLog

要求：
1. 先诊断失败原因
2. 只做最小必要修复
3. 不允许删除或跳过测试
4. 不允许实现额外功能
5. 修复后说明需要运行的测试命令
6. 不进入下一个 Task
"@

codex $prompt