# ConnLab Task Files

Last Updated: 2026-08-21

Sol-native tasks do not create Task Markdown by default. This directory retains manually published
task artifacts and their history; it is not a live work queue.

## Read Order

1. The User's current request
2. `AGENTS.md`
3. Real code, tests, configuration, and Git state
4. `docs/task_board.md` for compact WIP/recovery state
5. A named Task or Plan artifact only when the current request specifically depends on it

## File Roles

- `TASK_XXX_*.md`: manually published historical scope or acceptance material; the current User
  request remains authoritative.
- `completed/YYYY/`: archive location for archived task files.

## Archive Rule

Sol-native tasks record state in the `docs/task_board.md` JSON control block and do not create
per-task Markdown artifacts by default. When the User asks for cleanup of an archived task file,
move it with Git and update the indexes manually:

```powershell
git mv tasks\TASK_XXX.md tasks\completed\2026\
```

Confirm the task is closed and no current work references it before moving. Update
`docs/archive/TASK_HISTORY_INDEX.md` only when a human-readable lookup entry is useful. See
`docs/markdown_management_rules.md`.
