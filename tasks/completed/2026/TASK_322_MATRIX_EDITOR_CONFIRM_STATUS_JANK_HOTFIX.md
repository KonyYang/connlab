# TASK_322 Matrix Editor Confirm Status Jank Hotfix

> Status: Approved and implemented in the same execution turn after user approval.
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
> Plan: `docs/task_322_matrix_editor_confirm_status_jank_hotfix_plan.md`

## Goal

Remove the visible Matrix Editor layout jump caused by the transient `Preparing confirm...` autosave status card above the Matrix grid.

## Approved Scope

- Hide normal Matrix autosave progress copy from the operator-facing grid layout.
- Keep Matrix save failures visible near the grid controls.
- Keep Confirm Matrix gating and bottom dock blocker copy.
- Do not change backend autosave, Confirm Matrix semantics, Matrix authority data, StepInstance, reports, AI, permissions, LAN, or multi-user scope.

## Validation

- `cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task322"`
- `cd frontend; npm run build`
- Browser smoke on `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f/matrix-editor`.
