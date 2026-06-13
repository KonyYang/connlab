# Task Plan Index

Last Updated: 2026-06-13
Status: TASK_317E complete after TASK_317D. TASK_317A UI blueprint remains the accepted planning prerequisite for the Project Folder direction. TASK_318 implements Official project folder check/repair in the Project Folder model and replaces TASK_312's user-facing readiness/check role without enhancing the old package-preview surface.

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

Latest completed task plan:

```text
docs/task_313a_project_workbench_lifecycle_mode_redesign_plan.md
```

Latest task plan accepted for planning:

```text
docs/task_313b_official_project_workspace_plan.md
```

Latest execution guide accepted for planning:

```text
docs/task_313b_official_project_workspace_execution_guide.md
```

Latest completed task file:

```text
tasks/TASK_317E_TEMPORARY_PROJECT_STOP_AND_SAFE_DELETE.md
```

Latest completed executable plan:

```text
docs/task_317e_temporary_project_stop_and_safe_delete_plan.md
```

Latest proposed task file:

```text
None
```

Latest proposed executable plan:

```text
None
```

Latest accepted planning prerequisite:

```text
tasks/TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT.md
docs/task_317a_project_folder_preparation_ui_blueprint_plan.md
```

Latest completed task plan history:

```text
docs/task_284_matrix_editor_test_days_and_project_schedule_plan.md
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
