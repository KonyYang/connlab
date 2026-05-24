# TASK_237_MATRIX_EDITOR_FIXED_COLUMNS_BG_AND_GROUP_HEADER_DENSITY

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_237_MATRIX_EDITOR_FIXED_COLUMNS_BG_AND_GROUP_HEADER_DENSITY`.

## Why This Task Is Allowed Now

User requested a focused Matrix Editor UI refinement:

- clearer background treatment for the fixed left 6 columns
- tighter group header capsule input height with larger outer click area

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only CSS/UI tuning with existing behavior preserved.
- No backend/API/domain/model changes.

## Objective

1. Apply a subtle consistent background style for fixed left 6 columns in matrix main table:
   - row selector
   - Test Item
   - Section
   - Method
   - Condition
   - Requirement
2. Reduce group header capsule input inner height/padding.
3. Increase clickable padding/blank area in the group header cell outside capsule input so selecting the group column is easier.

## Scope

Allowed:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (static guard if needed)
- task file and board update

Forbidden:

- backend/API/domain changes
- matrix interaction logic changes
- right-side Step preview logic changes

## Acceptance Criteria

- Left fixed 6 columns have a distinct but restrained background from group columns.
- Group header capsule appears visually shorter.
- Group header cell has more outer spacing to improve click target for column selection.
- Existing column-selection/right-click behavior remains unchanged.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task237 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task237 or task236 or matrix_editor"` passed (`16 passed`, `69 deselected`).
