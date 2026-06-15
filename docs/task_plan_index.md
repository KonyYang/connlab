# Task Plan Index

Last Updated: 2026-06-15
Status: TASK_321 complete after explicit user approval. TASK_314 split accepted; TASK_314A Matrix Editor draft persistence is complete. TASK_314B Fee Evaluation background draft persistence is complete after separate explicit user approval. TASK_314C Matrix/Fee/Project Folder regression is complete after separate explicit user approval. TASK_315 split accepted; TASK_315 is an umbrella, TASK_315A Matrix-to-Fee rebase core is complete after separate explicit user approval, TASK_315B pending rebase persistence/autosave/cancel lifecycle plus review follow-up is complete after separate explicit user approval, TASK_315C Matrix Confirm promotion plus review follow-up is complete after separate explicit user approval, TASK_315D Fee UI + Project Folder regression is complete after separate explicit user approval, TASK_315D Fee Confirm action dock follow-up is complete after separate explicit user approval, TASK_315D remove Fee Confirmed-by UI follow-up is complete after separate explicit user approval, TASK_315D remove Fee Confirm status card follow-up is complete after separate explicit user approval, and TASK_315D Fee rebase saveable defaults follow-up is complete after user-reproduced regression feedback. Old TASK_313 package execution shape remains historical/deferred and is superseded by Project Folder Required forms generation. Do not enter a later task without separate user approval.

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
docs/task_321_project_folder_required_forms_generation_plan.md
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
tasks/TASK_315D_FOLLOWUP_FEE_REBASE_SAVEABLE_DEFAULTS.md
```

Latest completed executable plan:

```text
docs/task_315d_followup_fee_rebase_saveable_defaults_plan.md
```

Current proposed/follow-up task plans:

```text
tasks/TASK_314_MATRIX_AND_FEE_BACKGROUND_DRAFT_PERSISTENCE.md
docs/task_314_matrix_and_fee_background_draft_persistence_plan.md
tasks/TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE.md
docs/task_314a_matrix_editor_draft_persistence_plan.md
tasks/TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE.md
docs/task_314b_fee_evaluation_background_draft_persistence_plan.md
tasks/TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION.md
docs/task_314c_matrix_fee_project_folder_regression_plan.md
tasks/TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE.md
docs/task_315_matrix_draft_to_fee_draft_incremental_rebase_plan.md
tasks/TASK_315A_MATRIX_TO_FEE_REBASE_CORE.md
docs/task_315a_matrix_to_fee_rebase_core_plan.md
tasks/TASK_315B_PENDING_REBASE_PERSISTENCE_AND_MATRIX_AUTOSAVE_CANCEL_LIFECYCLE.md
docs/task_315b_pending_rebase_persistence_and_matrix_autosave_cancel_lifecycle_plan.md
tasks/TASK_315C_MATRIX_CONFIRM_PROMOTION.md
docs/task_315c_matrix_confirm_promotion_plan.md
tasks/TASK_315D_FEE_UI_PROJECT_FOLDER_REGRESSION.md
docs/task_315d_fee_ui_project_folder_regression_plan.md
tasks/TASK_315D_FOLLOWUP_FEE_CONFIRM_ACTION_DOCK.md
docs/task_315d_followup_fee_confirm_action_dock_plan.md
tasks/TASK_315D_FOLLOWUP_REMOVE_FEE_CONFIRMED_BY_UI.md
docs/task_315d_followup_remove_fee_confirmed_by_ui_plan.md
tasks/TASK_315D_FOLLOWUP_REMOVE_FEE_CONFIRM_STATUS_CARD.md
docs/task_315d_followup_remove_fee_confirm_status_card_plan.md
tasks/TASK_315D_FOLLOWUP_FEE_REBASE_SAVEABLE_DEFAULTS.md
docs/task_315d_followup_fee_rebase_saveable_defaults_plan.md
```

Status note:

- `TASK_314` is now an umbrella/historical split rationale and must not be implemented as one combined task.
- `TASK_314A` is complete and is the Matrix prerequisite for `TASK_315`.
- `TASK_314B` Fee Evaluation background draft persistence is complete after separate explicit user approval.
- `TASK_314C` Matrix/Fee/Project Folder linkage regression is complete after separate explicit user approval.
- `TASK_315` is now an umbrella/split rationale and must not be implemented as one combined task.
- `TASK_315A` Matrix-to-Fee rebase core is complete after separate explicit user approval.
- `TASK_315B` pending rebase persistence and Matrix autosave/cancel lifecycle, including review follow-up for step index preservation, Cancel race cleanup, and database-level generation CAS, is complete after separate explicit user approval.
- `TASK_315C` Matrix Confirm promotion plus review follow-up is complete after separate explicit user approval.
- `TASK_315D` Fee UI + Project Folder regression is complete after separate explicit user approval.
- `TASK_315D_FOLLOWUP` Fee Confirm action dock is complete after separate explicit user approval.
- `TASK_315D_FOLLOWUP` remove Fee Confirmed-by UI is complete after separate explicit user approval.
- `TASK_315D_FOLLOWUP` remove Fee Confirm status card is complete after separate explicit user approval.
- `TASK_315D_FOLLOWUP` Fee rebase saveable defaults is complete after user-reproduced regression feedback.

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
