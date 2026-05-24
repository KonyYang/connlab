# ConnLab Task Files

Last Updated: 2026-05-24

Use this directory for current, planned, recently completed, and not-yet-archived task files.

## Read Order

1. `AGENTS.md`
2. `docs/task_board.md`
3. The current `tasks/TASK_XXX_*.md`
4. The corresponding `docs/task_XXX_*_plan.md`
5. Task-specific guideline documents referenced by the task

## File Roles

- `TASK_XXX_*.md`: executable task scope, constraints, acceptance criteria, and validation.
- `completed/YYYY/`: future archive location for completed task files after final board alignment.

## Archive Rule

Do not manually move completed task files. Use:

```powershell
py scripts\archive_completed_markdown.py --task TASK_XXX --dry-run
py scripts\archive_completed_markdown.py --task TASK_XXX --apply
py scripts\archive_completed_markdown.py --all-completed --dry-run
py scripts\archive_completed_markdown.py --all-completed --apply
```

The script checks `docs/task_board.md` before moving files and updates archive indexes in `docs/`.
