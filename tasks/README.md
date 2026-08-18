# ConnLab Task Files

Last Updated: 2026-08-18

Use this directory for current, planned, recently completed, and not-yet-archived task files.

## Read Order

1. `AGENTS.md`
2. `docs/task_board.md`
3. The current `tasks/TASK_XXX_*.md`
4. The corresponding `docs/task_XXX_*_plan.md`
5. Task-specific guideline documents referenced by the task

## File Roles

- `TASK_XXX_*.md`: executable task scope, constraints, acceptance criteria, and validation (created only when a manual publishing flow requires one).
- `completed/YYYY/`: archive location for archived task files.

## Archive Rule

Sol-native tasks record state in the `docs/task_board.md` JSON control block and do not create
per-task Markdown artifacts by default. When the User asks for cleanup of an archived task file,
move it with Git and update the indexes manually:

```powershell
git mv tasks\TASK_XXX.md tasks\completed\2026\
```

Confirm the task is closed and no current work references it before moving. Update
`docs/task_archive_index.md` and `docs/plan_archive_index.md`. See `docs/markdown_management_rules.md`.
