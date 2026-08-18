# DOCS_001_MARKDOWN_INFORMATION_ARCHITECTURE_AND_AUTO_ARCHIVE_RULES

Status: complete
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Last Updated: 2026-05-24

## Purpose

Reduce navigation noise in `docs/` and `tasks/` by defining a durable Markdown information architecture and adding a controlled archive helper for completed task files and completed task plan files.

This task is documentation-governance only. It must not change Matrix runtime behavior, frontend workflow behavior, backend APIs, database schema, or TASK_261-TASK_267 smoke-flow behavior.

## Scope

In scope:

- Define the relationship and priority order among root rules, task board, current task files, task plans, archive indexes, and historical documents.
- Add a concise operator guide for `tasks/`.
- Add task and plan archive index files.
- Add a dry-run-first archive script that can move completed task files and completed plan files only after task board alignment.
- Add unit coverage for the archive script.
- Update the task board to record the governance change.

Out of scope:

- Bulk moving historical Markdown files in this task.
- Rewriting historical `docs/task_board.md` links.
- Changing task execution protocol.
- Changing product, backend, frontend, runtime, Matrix, Test Record, report, or StepInstance behavior.

## Model Fit Assessment

`GPT-5.3-codex` with medium reasoning is suitable for this task because it is a repository-structure and documentation-governance task with a small standard-library Python helper and focused unit tests. It does not require long-context architecture synthesis beyond existing project rules and task-board status.

## Deliverables

- `docs/markdown_management_rules.md`
- `docs/task_archive_index.md`
- `docs/plan_archive_index.md`
- `tasks/README.md`
- `scripts/archive_completed_markdown.py`
- `tests/unit/test_markdown_archive_tool.py`
- Updates to `docs/README.md`
- Updates to `docs/task_plan_index.md`
- Updates to `docs/task_board.md`

## Acceptance Criteria

- Root source-of-truth documents are explicitly protected from archiving.
- Completed task files have a clear future archive destination under `tasks/completed/YYYY/`.
- Completed plan files have a clear future archive destination under `docs/completed_plans/YYYY/`.
- The archive helper supports a dry run that does not move files.
- The archive helper refuses to archive a task unless the task board indicates the task is complete and not the active implementation task.
- The archive helper updates archive indexes only in apply mode.
- TASK_267 files are not moved by this task.

## Validation

- `py -m pytest tests\unit\test_markdown_archive_tool.py -q`
- `py scripts\archive_completed_markdown.py --task TASK_267 --dry-run`
- `git diff --check`

## Completion Notes

Implemented as a first-stage Markdown governance baseline, then applied the archive workflow to all root-level task files and plan files that could be verified as completed by `docs/task_board.md` or by their own `Status` section. A follow-up cleanup also moved historical phase plans, validation summaries, external modification logs, and nonstandard completed task artifacts out of the `docs/` root into `docs/archive/`. Remaining root-level task/plan files are proposed, pending, planned, paused, or review-only records. Future mainline `TASK_268` remains uncreated and unblocked.

The archive helper was retired as legacy on 2026-08-18. Sol-native tasks record state in the `docs/task_board.md` JSON control block instead of per-task Markdown, so archiving is now a manual `git mv` plus index update. See `docs/markdown_management_rules.md`.
