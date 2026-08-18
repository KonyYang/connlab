# TASK_323 Project Folder Conflict Dialog Style Hotfix

> Status: Approved and implemented after user refined the scope.
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Plan: `docs/task_323_project_folder_conflict_dialog_style_plan.md`

## Goal

Restyle the existing Project Folder conflict dialog so its font, buttons, and modal formatting match the ConnLab workbench style.

## Approved Scope

- Keep the user's optimized dialog content unchanged.
- Keep the existing button titles unchanged: `Backup and Rebuild`, `Overwrite`, and `Cancel`.
- Keep the current dialog structure and business callbacks unchanged.
- Apply ConnLab workbench typography, button styling, modal surface, and path formatting.

## Out Of Scope

- No backend changes.
- No new conflict choices.
- No folder creation semantics change.
- No additional function cards or explanatory blocks.
- No Project Workbench redesign.

## Validation

- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task323"`
- `cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false`
- `cd frontend; npm run build`
