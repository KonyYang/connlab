# TASK_225_MATRIX_EDITOR_CONTEXT_MENU_INTERACTION_DENSITY_FIX

## Status

Complete. Implemented and validated on 2026-05-18.

This is a Matrix Editor interaction-density hotfix. It replaces space-consuming inline structural controls with right-click context menus.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_225_MATRIX_EDITOR_CONTEXT_MENU_INTERACTION_DENSITY_FIX`.

## Why This Task Is Allowed Now

The user reviewed `TASK_224` and reported poor table density caused by the added row control column and group header inline `...` controls. The requested correction is a bounded Matrix Editor interaction adjustment focused on reclaiming table width while preserving protection rules.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The work is a scoped frontend interaction change in one page and stylesheet.
- It primarily moves trigger surfaces from visible controls to context menus.
- Existing guard/undo logic from `TASK_224` can be reused with minimal API impact.
- No backend/API/domain changes are required.

## Objective

Switch Matrix Editor structural operations to right-click context menu mode to reduce occupied grid width.

Required outcomes:

1. Remove the visible `Row` control column from the data grid.
2. Remove visible group-header `...` action controls.
3. Add right-click context menu support for:
   - row operations on test-item rows
   - group operations on group headers
4. Keep structure-protection guards from `TASK_224`.
5. Preserve inline cell editing behavior.

## Scope

Allowed:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (targeted static assertion updates only)
- task file and board update on completion

Forbidden:

- backend changes
- API contract changes
- matrix domain model changes
- Workbench page changes
- unrelated visual polish

## Interaction Rules (Hotfix Direction)

- Right-click on row body cells opens row operations:
  - insert above
  - insert below
  - duplicate row
  - move up
  - move down
  - delete row
- Right-click on group header cells opens group operations:
  - insert left
  - insert right
  - duplicate group
  - move left
  - move right
  - delete group
- Fixed header row and fixed first five columns remain structurally protected.
- Minimum structure rules remain enforced.
- Disabled operations in context menu show disabled state and reason text in status strip.

## Optional Density Fallback

If row targeting via right-click is hard to discover, allow a compact non-data row index marker that does not carry always-visible action buttons.

This fallback must remain narrower than current `Row` control column and must not reduce group visibility materially.

## Acceptance Criteria

- No persistent visible `Row` action rail in table body.
- No persistent visible group `...` action controls.
- Row/group structural actions are available by right-click.
- Existing minimum-structure guards still block invalid operations.
- Undo remains available for structural actions.
- Group column visibility improves vs `TASK_224`.
- `npm run build` passes.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Targeted check:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task225 or task224 or task223"
```

Result:

- `cd frontend; npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task225 or task224 or task223"` passed (`2 passed`, `71 deselected`).

## Completion Notes

- Removed the persistent row action column from the Matrix Editor grid.
- Removed the persistent group-header `...` controls.
- Added right-click context menus for row and group structural operations.
- Preserved inline cell editing, minimum-structure guards, and structural undo.
- No backend, API contract, domain model, or Workbench page changes were made.
