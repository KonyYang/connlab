# Task Plan Index

Last Updated: 2026-05-26
Status: no active planned task plan

## Decision

`TASK_203 Slice C` decision:

- Keep `docs/task_XXX_*_plan.md` files in place.
- Do not move them into `docs/archive/task_plans/` in this slice.

Reason:

- `docs/task_board.md` contains extensive historical references to existing plan paths.
- Path stability is more important than directory compactness at this stage.
- Current runtime direction emphasizes execution velocity and low-risk changes.

## DOCS_001 Update

`DOCS_001_MARKDOWN_INFORMATION_ARCHITECTURE_AND_AUTO_ARCHIVE_RULES` introduced and applied a controlled archive path for completed plan files:

- Completed plan files may move to `docs/completed_plans/YYYY/`.
- Moves must use `scripts/archive_completed_markdown.py`.
- Dry-run review is required before apply mode.
- `docs/plan_archive_index.md` records archived plan paths.
- `docs/markdown_management_rules.md` defines protected files and archive eligibility.

## How To Use Task Plan Files

- Treat each `docs/task_XXX_*_plan.md` as planning/review history for that task.
- Use `docs/task_board.md` as the authoritative status source.
- Use the corresponding `tasks/TASK_XXX_*.md` for execution scope.
- Do not treat older plan files as current product truth unless referenced by the active task.

## Current Plan File Pattern

Root-level active/proposed/review pattern:

```text
docs/task_XXX_*_plan.md
```

Current active planned task plan:

```text
none
```

Latest completed task plan history:

```text
docs/task_276_workbench_execution_surface_density_polish_plan.md
```

Archived completed-plan pattern:

```text
docs/completed_plans/YYYY/task_XXX_*_plan.md
```

## Future Bulk Migration Trigger

Revisit bulk migration of task plan files only when both conditions are true:

1. `docs/task_board.md` reference format is intentionally refactored.
2. A dedicated path-rewrite validation task is approved.

Individual completed-task cleanup may happen earlier through the DOCS_001 archive helper when the task board already marks that task complete and the user explicitly requests cleanup.
