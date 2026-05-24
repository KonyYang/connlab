# TASK_252B_MATRIX_EDITOR_SINGLE_CARD_IMPORT_FLOW

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252B_MATRIX_EDITOR_SINGLE_CARD_IMPORT_FLOW`

## Why This Task Is Allowed Now

`TASK_252A` is complete. User approved the next focused refinement to simplify Matrix import interaction and reduce duplicated entry controls.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- UI/interaction refinement on top of existing `.docx` import infrastructure
- no new format support
- bounded frontend and light API wiring updates with existing contracts

## Objective

Convert current dual-entry import UX into a single-card flow:

1. Remove top `Import Matrix` toggle entry.
2. Keep one primary entry: `Choose .docx`.
3. Auto-run parse preview right after file selection.
4. Keep page/table correction inputs for quick recalibration.
5. Remove separate `Preview` and `Apply import` buttons.
6. Use `Replace` and `Append` as the only explicit write actions.
7. Keep parsing as an automatic preview step, not an automatic write step.
8. Display the original selected file name, not the backend temporary upload name.

## Scope

Allowed:

- Matrix Editor import UI simplification
- auto-preview on file selection and correction-field updates/explicit reparse control
- remove duplicate entry and redundant action buttons
- keep existing parser/service behavior and `.docx` boundary
- preserve original upload filename in UI/source trace display

Forbidden:

- `.doc`/`.pdf`/`.xlsx` support
- embedding in-browser document viewer
- forcing OS app launch from browser-only path
- parser algorithm redesign

## Acceptance Criteria

- Only one import entry card remains in Matrix Editor.
- `Choose .docx` directly selects file and auto-previews.
- `Source document` field remains read-only display; no extra `Browse` button.
- `Preview` and `Apply import` buttons are removed.
- `Replace` and `Append` apply imported result as explicit commit actions.
- `Replace` and `Append` stay disabled until a successful auto-preview exists.
- Selecting a file never mutates the Matrix grid until user clicks `Replace` or `Append`.
- Current import summary still shows selected page/table metadata and source trace.
- Current import summary uses the selected document's original filename instead of `tmp*.docx`.
- If the user edits page/table/text correction fields after a preview, UI must make the preview stale or re-run parsing before allowing commit.
- Existing tests/build pass with updated assertions.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252b or task252a or task252 or matrix_editor or task224 or task222"
```

Result: passed, `31 passed`, `69 deselected`.

```powershell
cd frontend
npm run build
```

Result: passed.

Implemented notes:

- Removed top `Import Matrix` button; kept `Choose .docx` and `Undo`.
- Import card is now always visible (single-card flow).
- Removed inner `Browse` button from source row.
- Removed `Preview` and `Apply import` actions.
- Added auto-parse on file selection.
- Added `Reparse` action for manual correction refresh.
- `Replace` and `Append` are now explicit commit actions and disabled for stale preview state.
- User-facing source trace now shows the original selected filename instead of backend temporary `tmp*.docx` names.
