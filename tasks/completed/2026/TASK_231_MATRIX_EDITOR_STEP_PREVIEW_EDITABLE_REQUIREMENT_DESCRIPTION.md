# TASK_231_MATRIX_EDITOR_STEP_PREVIEW_EDITABLE_REQUIREMENT_DESCRIPTION

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_231_MATRIX_EDITOR_STEP_PREVIEW_EDITABLE_REQUIREMENT_DESCRIPTION`.

## Why This Task Is Allowed Now

User confirmed a simplified Step preview direction: derive selected group step list from Matrix grid, show Test Item as read-only, and allow Requirement / Step Description edits using Matrix Requirement as default.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only Matrix Editor feature refinement.
- Uses existing grid state and selected group.
- No backend/API/domain/persistence change.
- Scope is bounded to right-side Step preview behavior.

## Objective

For the currently selected group, render a Step preview list sorted by step number:

1. `Step No.` from group step cells.
2. `Test Item` imported from Matrix row and read-only.
3. `Requirement` defaults from Matrix row Requirement and is editable.
4. `Step Description` defaults from Matrix row Requirement and is editable.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css` if minor layout styling is required
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain changes
- persistence
- report/test-record generation
- AI/smart fill
- Workbench page changes

## Acceptance Criteria

- Right Step preview reflects selected group.
- Steps are sorted by numeric step number.
- Test Item is read-only.
- Requirement and Step Description are editable fields.
- Both editable fields default to Matrix row Requirement.
- User edits are preserved by stable key `groupId + stepNo + rowId` while the step remains present.
- Existing Matrix grid editing and validation remain functional.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task231 or task230 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task231 or task230 or matrix_editor"` passed (`10 passed`, `69 deselected`).
