# TASK_232_MATRIX_EDITOR_STEP_PREVIEW_DESCRIPTION_FROM_TEST_ITEM

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_232_MATRIX_EDITOR_STEP_PREVIEW_DESCRIPTION_FROM_TEST_ITEM`.

## Why This Task Is Allowed Now

User clarified Step preview business expectation:

- Remove `Test Item` column from Step preview.
- `Step Description` default should come from Matrix `Test Item` (not from Matrix `Requirement`).
- Keep scope minimal and avoid speculative rule automation for LLCR/IR/DWV/mating-unmating exceptions at this stage.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only adjustment in existing Matrix Editor Step preview mapping.
- Requires bounded data-field remap and table column update.
- No backend/API/domain/persistence/model changes.

## Objective

Adjust Matrix Editor Step preview behavior to match clarified business usage:

1. Remove preview `Test Item` column.
2. Keep `Requirement` editable with default from Matrix `Requirement`.
3. Keep `Step Description` editable, but default from Matrix `Test Item`.
4. Preserve existing local override behavior by stable key `groupId + stepNo + rowId`.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css` (only if minimal style updates are needed)
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain changes
- persistence changes
- matrix model contract changes
- report/test-record generation logic
- smart inference for LLCR/IR/DWV/mating/un-mating exception filling

## Acceptance Criteria

- Step preview no longer renders a `Test Item` column.
- Step preview still sorted by step number for selected group.
- `Requirement` remains editable and defaults from Matrix row `Requirement`.
- `Step Description` remains editable and defaults from Matrix row `Test Item`.
- Existing user overrides continue to persist locally by stable key while row/step exists.
- Existing Matrix grid editing/validation behavior is unchanged.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task232 or task231 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task232 or task231 or matrix_editor"` passed (`11 passed`, `69 deselected`).
