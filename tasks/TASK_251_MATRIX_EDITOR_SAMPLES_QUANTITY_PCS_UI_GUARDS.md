# TASK_251_MATRIX_EDITOR_SAMPLES_QUANTITY_PCS_UI_GUARDS

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_251_MATRIX_EDITOR_SAMPLES_QUANTITY_PCS_UI_GUARDS`.

## Why This Task Is Allowed Now

`TASK_250` completed feasibility assessment and confirmed staged implementation.

User approved continuing with the recommended best path. The first implementation slice is a bounded Matrix Editor frontend-only change:

- add a fixed final row `Samples Quantity (PCS)` in the Matrix edit grid
- make per-group quantity required
- enforce integer-only and `>= 1` UI validation

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only feature slice with localized state and validation changes.
- No backend/API/domain contract changes in this task.
- Existing static test pattern can lock behavior.

## Objective

Implement Matrix Editor UI support for per-group sample quantity capture:

1. Add fixed final row label: `Samples Quantity (PCS)`.
2. Provide one editable quantity cell per group column.
3. Require each group quantity value.
4. Allow only integer values `>= 1`.
5. Keep existing step-token validation behavior for normal test-item rows unchanged.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css` (only if minimal style support is needed)
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- Matrix draft API contract changes
- fee/report/test-form downstream wiring
- row/group structural operation redesign

## Acceptance Criteria

- Matrix grid renders a fixed final row with title `Samples Quantity (PCS)`.
- Final row includes one editable cell per group column.
- Quantity cells are required; empty value shows existing error cue style pattern.
- Quantity cells reject non-numeric input and invalid values (`0`, negative, decimal).
- Existing group step-token validation continues to apply only to test-item rows.
- Add/insert/delete/move/duplicate group operations keep quantity cells synchronized by `group.id`.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task251 or matrix_editor"
```
