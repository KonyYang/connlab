param(
    [string]$task
)

Write-Host "===================================="
Write-Host " Running Task: $task"
Write-Host "===================================="

# 自动拼接路径
$taskFile = "tasks/$task.md"

if (!(Test-Path $taskFile)) {
    Write-Host "❌ Task file not found: $taskFile"
    exit
}

# 自动生成提示词
$prompt = @"
请执行任务文件：$taskFile

必须遵守：
- AGENTS.md
- TASK_EXECUTION_SKILL.md
- TASK_REVIEW_CHECKLIST.md
- TESTING_SKILL.md

要求：
1. 先输出设计方案
2. 再写代码
3. 自动生成 pytest 测试
4. 提供运行方法
5. 不进入下一个任务
"@

# 调用 Codex
codex $prompt