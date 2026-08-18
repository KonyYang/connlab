# DOCS_001 Markdown Information Architecture And Auto Archive Rules Plan

Status: complete
Task: `DOCS_001_MARKDOWN_INFORMATION_ARCHITECTURE_AND_AUTO_ARCHIVE_RULES`
Last Updated: 2026-05-24

## Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task before execution: none after `TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX` completion.
- Allowed reason: the user explicitly requested Markdown management optimization after TASK_267 review, and the task board had no active implementation task.

## Problem

`docs/` and `tasks/` contain many completed task files and completed plan files. The project still needs historical traceability, but daily navigation should prioritize current rules, current task state, and current execution documents.

## Design

Create a lightweight information architecture:

1. Keep source-of-truth files in place.
2. Keep active/planned task and plan files in place.
3. Archive only completed task files and completed plan files after task-board alignment.
4. Make archival dry-run-first and index-backed.
5. Do not rewrite historical task-board references in this first stage.

## File-Level Changes

- Add `docs/markdown_management_rules.md` to define document categories, source-of-truth priority, archive eligibility, and the automatic archive workflow.
- Add `tasks/README.md` as a short navigation guide.
- Add `docs/task_archive_index.md` and `docs/plan_archive_index.md` for future archive traceability.
- Add `scripts/archive_completed_markdown.py` with dry-run and apply modes.
- Add `tests/unit/test_markdown_archive_tool.py` to cover dry-run, apply, and refusal behavior.
- Update `docs/README.md` and `docs/task_plan_index.md` to point to the new management rules.
- Update `docs/task_board.md` after validation.

## Risks And Controls

- Risk: accidental movement of active task files.
  Control: the script requires task-board completion evidence and refuses active implementation tasks.
- Risk: broken historical links.
  Control: this task does not move historical files; future moves append indexes and preserve task IDs.
- Risk: ambiguity between product docs and task artifacts.
  Control: rules explicitly protect current product, architecture, task-board, and guideline documents.

## Validation

- Unit-test the archive helper with a temporary repository.
- Run a repository dry-run for `TASK_267`.
- Run `git diff --check`.

## Scope Boundary

No backend, frontend, API, database, Matrix workflow, Test Record workflow, report, StepInstance, permissions, or AI recommendation behavior is changed.

## Archive Application

After the governance baseline was in place, the archive helper was applied to all root-level task files and plan files that could be verified as completed by `docs/task_board.md` or by their own `Status` section.

The final cleanup pass left only proposed, pending, planned, paused, or review-only root-level task/plan files in `tasks/` and `docs/`.

Historical nonstandard Markdown files were also moved into:

- `docs/archive/historical_plans/`
- `docs/archive/validation_summaries/`
- `docs/archive/external_ai/`
- `docs/archive/task_artifacts/2026/`

Archived files are recorded in:

- `docs/task_archive_index.md`
- `docs/plan_archive_index.md`
