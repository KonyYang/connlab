# TASK_241 Matrix Editor Row No. Warning For Missing Steps Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_241_MATRIX_EDITOR_ROW_NO_WARNING_FOR_MISSING_STEPS`
- Allowed now: user requested correction of warning communication strategy.

## Goal

Avoid misleading users that all blank step cells must be filled by default, while still warning missing step numbering.

## Minimal Change Design

1. Keep row-level predicate:
- `rowHasNoGroupSteps` remains computed in row render.

2. Move warning target:
- remove `is-row-step-empty` use from group step input class.
- add warning class on row selector button/cell when `rowHasNoGroupSteps`.
- add `title="缺少步骤编号"` on warning state target.

3. CSS tuning:
- new style for row selector warning state (text color and/or subtle background).
- retain selected-row priority.

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- move warning class/tooltip from group inputs to row selector control.

2. `frontend/src/workbench.css`
- add `.matrix-editor-row-selector-button.is-step-missing` (and optional cell style).
- keep/remove old `.is-row-step-empty` as unused cleanup if safe.

3. `tests/unit/test_frontend_shell_files.py`
- add TASK_241 static assertions for new class and tooltip wiring.

## Risks

- Row selected highlight and warning style may conflict; warning style should remain visible but not overpower selection.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task241 or matrix_editor"
```

## Out Of Scope

- changing step-rule business logic
- additional mandatory-field policy changes
