# Markdown Management Rules

Keep current authority small and keep history recoverable.

## Current authority

Never auto-archive:

- `AGENTS.md`;
- `README.md`, `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json`;
- `docs/project_management/SOL_NATIVE_WORKFLOW.md`;
- `docs/PROJECT_CONTEXT.md` and `docs/FRONTEND_GUIDE.md`;
- `docs/task_board.md`;
- current architecture documents directly relevant to active product behavior.

Task files, Plans, evidence, and validation summaries are not execution authority after completion.
Archive them only when their task is closed, no current work references them, and the User has asked
for cleanup or the active task includes cleanup.

## Archive helper

Sol-native tasks do not create per-task Markdown artifacts by default; the JSON control block in
`docs/task_board.md` is the authoritative record. Archiving completed files is a lightweight manual
cleanup; no archive helper participates in the current workflow:

1. Confirm the task is closed and no current work references it.
2. Preview what Git tracks, then move with `git mv`:
   ```powershell
   git ls-files tasks/
   git mv tasks/TASK_XXX.md tasks/completed/2026/
   ```
3. Update `docs/archive/TASK_HISTORY_INDEX.md` when a human-readable history entry is useful.
4. Commit. Git remains the recovery source for removed historical governance files.

Do not bulk-migrate history during an unrelated product task.
