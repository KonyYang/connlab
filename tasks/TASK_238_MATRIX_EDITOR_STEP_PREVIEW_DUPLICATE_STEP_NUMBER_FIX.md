# TASK_238_MATRIX_EDITOR_STEP_PREVIEW_DUPLICATE_STEP_NUMBER_FIX

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_238_MATRIX_EDITOR_STEP_PREVIEW_DUPLICATE_STEP_NUMBER_FIX`.

## Why This Task Is Allowed Now

Manual smoke test found a functional defect:

- After adding a group, Step preview can show duplicated step number entries (e.g., repeated `Step 1`) unexpectedly.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only bug fix in existing step preview derivation path.
- Bounded scope with deterministic behavior.
- No backend/API/domain/persistence changes.

## Objective

Fix Step preview row derivation so step entries are not duplicated unexpectedly after group operations.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- new feature additions unrelated to duplicate-step defect
- visual redesign

## Acceptance Criteria

- Reproduced duplicate-step condition is resolved.
- Step preview keeps valid expected rows only.
- Existing step sorting and override behaviors remain intact.
- Existing special description/requirement rules still work.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task238 or task237 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task238 or task237 or matrix_editor"` passed (`17 passed`, `69 deselected`).
