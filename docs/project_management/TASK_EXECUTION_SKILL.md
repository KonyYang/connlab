# ConnLab Personal Task Execution

Last Updated: 2026-08-06
Status: normative execution instructions

1. Read `AGENTS.md`, `docs/task_board.md`, and the active task/plan when present.
2. State the current phase, active task ID, and why the requested action is allowed.
3. Run `scripts/connlab_personal_task.py inspect` and respect the single active slot and FIFO.
4. For a simple task, submit the complete classification contract. For a planned task, prepare a
   short plan and wait for explicit User approval before `approve` and implementation.
5. Commit the activation or approval board transition before implementation edits.
6. Modify only `may_touch`; add or adjust tests inside that exact allowlist.
7. Run targeted validation. On failure, keep the task active and record a blocker.
8. On success, call `mark-review`, exact-stage changed task paths plus the board, and create one
   local implementation commit.
9. Stop at `implemented_pending_human_review`. Only explicit User `关闭` authorizes close.

Never dispatch roles, create lanes/worktrees, push, destructively clean, resume frozen legacy
automation, or start the next queued task automatically.
