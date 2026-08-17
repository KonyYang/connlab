# Markdown Management Rules

Keep current authority small and keep history recoverable.

## Current authority

Never auto-archive:

- `AGENTS.md`;
- `README.md`, `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`;
- `docs/project_management/TASK_WORKFLOW.md`;
- `docs/task_board.md`;
- current architecture documents directly relevant to active product behavior.

Task files, Plans, evidence, and validation summaries are not execution authority after completion.
Archive them only when their task is closed, no current work references them, and the User has asked
for cleanup or the active task includes cleanup.

## Archive helper

Preview before applying:

```powershell
py scripts/archive_completed_markdown.py --task TASK_XXX --dry-run
```

Apply only after the preview has the intended exact paths:

```powershell
py scripts/archive_completed_markdown.py --task TASK_XXX --apply
```

Do not bulk-migrate history during an unrelated product task. Git remains the recovery source for
removed historical governance files.
