# TASK_242_MATRIX_EDITOR_MISSING_STEP_TOOLTIP_EN_COPY

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_242_MATRIX_EDITOR_MISSING_STEP_TOOLTIP_EN_COPY`.

## Why This Task Is Allowed Now

User requested copy-only adjustment:

- change row-number hover tooltip from Chinese to English

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Small frontend text-only change.
- No backend/API/domain logic involved.

## Objective

Replace tooltip text:

- from: `缺少步骤编号`
- to: `Missing step number`

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- any behavior change
- backend/API/domain changes

## Acceptance Criteria

- Tooltip text on row `No.` warning uses English `Missing step number`.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task242 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task242 or matrix_editor"` passed (`19 passed`, `69 deselected`).
