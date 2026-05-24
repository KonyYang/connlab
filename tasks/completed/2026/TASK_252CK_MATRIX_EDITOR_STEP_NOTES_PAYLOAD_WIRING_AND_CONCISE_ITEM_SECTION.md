# TASK_252CK_MATRIX_EDITOR_STEP_NOTES_PAYLOAD_WIRING_AND_CONCISE_ITEM_SECTION

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CK_MATRIX_EDITOR_STEP_NOTES_PAYLOAD_WIRING_AND_CONCISE_ITEM_SECTION`

## Why This Task Is Allowed Now

- User explicitly reported that Step preview note display still does not match expected behavior after parser hardening.
- Root cause is a bounded Matrix Editor frontend wiring gap (local marker-only reconstruction) and note-format verbosity mismatch.
- Scope stays inside Matrix preview/read-only rendering behavior and does not expand runtime domain/persistence.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

## Objective

1. Wire Step preview note cards to imported preview payload note content where available (`source_note`, `source_item_section_note`, `sample_note`), instead of local marker-only placeholders.
2. Keep `Item/Section Notes` concise:
   - format target: `Step 2 | Section:6.5*Simultaneously measure power contact resistance`
   - remove redundant `Test Item` fragment in that card.
3. Preserve card split behavior: `Step Notes`, `Item/Section Notes`, `Samples`, `Samples Notes`.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts` (type-only adjustments if needed)
- `tests/unit/test_frontend_shell_files.py` (targeted static assertions)
- task/plan/board documentation updates

Forbidden:

- backend parser/API contract redesign
- new import formats / OCR / AI parsing
- unrelated matrix layout redesign

## Acceptance Criteria

1. Imported note body text is visible in `Step Notes` card when mapped marker/step exists.
2. `Item/Section Notes` lines are concise and do not include `Test Item` segment by default.
3. `Item/Section Notes` line format follows `Step N | Section:...` style.
4. Existing step/sample cards remain separated and functional.
5. Build/tests relevant to Matrix Editor pass.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor and note"
```

```powershell
cd frontend
npm run build
```
