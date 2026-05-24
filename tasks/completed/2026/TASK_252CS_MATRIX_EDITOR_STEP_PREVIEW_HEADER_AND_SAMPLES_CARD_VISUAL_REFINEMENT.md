# TASK_252CS_MATRIX_EDITOR_STEP_PREVIEW_HEADER_AND_SAMPLES_CARD_VISUAL_REFINEMENT

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`none` (board-gated). This file is proposal only until user approval.

## Why This Task Is Allowed Now

- User explicitly requested Step preview header simplification and Samples card background consistency.
- Scope is bounded to Matrix Editor frontend presentation only.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

## Objective

1. Top group display changes from plain number (e.g., `9`) to `Group 9`.
2. Enlarge the top group label typography and render step count as suffix text (e.g., `10 steps`) in the same header area.
3. Remove redundant `Step preview` title and `Selected group` badge.
4. Apply matching background color treatment to the Samples card area.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (targeted static assertions if needed)

Forbidden:

- backend/API/parser changes
- step extraction logic changes
- non-Step-preview workflow changes

## Acceptance Criteria

- Step preview top area shows `Group <n>` with enlarged typography.
- Step count remains visible as `<n> steps`.
- `Step preview` and `Selected group` UI elements are removed from that area.
- Samples card background color is visually aligned with the note-card background style expected by this panel.
- Existing step rows, sample value edit behavior, and notes content behavior remain unchanged.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task252"
```

```powershell
cd frontend
npm run build
```
