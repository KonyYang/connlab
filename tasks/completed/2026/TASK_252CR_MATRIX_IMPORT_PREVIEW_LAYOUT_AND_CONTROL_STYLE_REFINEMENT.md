# TASK_252CR_MATRIX_IMPORT_PREVIEW_LAYOUT_AND_CONTROL_STYLE_REFINEMENT

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`none` (board-gated). This file is a proposal only until user approval.

## Why This Task Is Allowed Now

- User explicitly requested Matrix import preview UI refinements:
  1. Keep `Import Matrix` and parsed filename on one row.
  2. Reduce blank space in preview by defaulting PDF page to fit-width and opening at Matrix target page with thumbnail/navigation pane visible.
  3. Make `Reparse` visual style consistent with `Cancel/Replace/Append`.
  4. Place `Page` and `Table on page` inputs in one row.
- Scope is UI-only and bounded to existing Matrix import confirmation workflow.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

## Objective

Improve Matrix import confirmation dialog readability and operator efficiency without changing import business behavior.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (targeted static assertions if needed)

Forbidden:

- backend/API/parser logic changes
- `.doc/.pdf/.xlsx` import expansion
- workflow changes beyond visual/layout behavior

## Acceptance Criteria

1. In import dialog header, `Import Matrix` and resolved source filename render on one visual line.
2. Left PDF preview uses a default viewer state that prioritizes fit-width rendering of full page and opens at selected matrix page; thumbnail/navigation pane is visible by default.
3. `Reparse` button style (size, radius, typography, primary blue background) is aligned with `Replace/Append` visual system.
4. `Page` + `Table on page` inputs are displayed side-by-side on normal desktop width; narrow screens can stack responsively.
5. Existing `Cancel`, `Replace`, `Append`, debounce reparse, and import apply behaviors remain unchanged.
6. Frontend build and targeted frontend tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task252"
```

Manual smoke:

1. Open Matrix Editor, click `Import Matrix`, choose a real `.docx`.
2. Confirm dialog title and filename stay on one line.
3. Confirm preview opens on target page with width-fit readability and visible thumbnail/navigation pane.
4. Confirm `Page` + `Table on page` are side-by-side (desktop).
5. Confirm `Reparse` visual style aligns with footer action buttons.
6. Verify `Cancel`, `Replace`, `Append` functional behavior unchanged.
