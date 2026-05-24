# TASK_252A_MATRIX_EDITOR_IMPORT_UI_AND_ENTRY_REFINEMENT

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252A_MATRIX_EDITOR_IMPORT_UI_AND_ENTRY_REFINEMENT`

## Why This Task Is Allowed Now

`TASK_252` is complete. User requested immediate execution of a focused follow-up to improve Matrix import usability:

- simplify top action area to avoid duplicate controls
- remove placeholder controls with no current business behavior
- replace manual path-first import with file-picker-first import flow
- keep scope limited to `.docx` and existing parser capabilities

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- bounded full-stack slice with frontend UI refinement and backend upload-entry adapter
- reuses existing `.docx` preview parser and Matrix import apply flow from `TASK_252`
- requires careful API/DTO boundary updates and focused regression tests, not parser redesign

## Objective

Refine Matrix Editor import UX so operators can select `.docx` files through an open-file dialog (instead of path typing), preview extraction quality, then apply replace/append.

## Scope

Allowed:

- simplify Matrix Editor top action controls
- keep `Import Matrix` and `Undo`
- remove currently unused placeholder controls in action bar
- add file-picker-first `.docx` import entry
- add backend preview entry that accepts uploaded `.docx` file
- keep manual selector support (page number + table on page + text query) in preview step
- preserve replace/append apply behavior and draft version creation
- display source metadata after apply
- update tests and task board

Forbidden:

- `.doc`/`.pdf`/`.xlsx` support
- cross-project Matrix copy
- parser architecture changes beyond compatibility fixes for upload entry
- report/fee/approval/test execution scope

## UX Requirements

1. Top action area:
   - keep: `Import Matrix`, `Undo`
   - remove: `Add test item`, `Add group`
   - remove placeholder right-side controls: `Display options`, `Filter`, search input
2. `Import Matrix` opens file chooser for `.docx`.
3. After selection, preview runs and shows:
   - selected table info
   - candidate table count / key details
   - group and step counts
   - warnings / blockers
4. User can optionally refine preview with:
   - `page_number`
   - `page_table_index`
   - `table_text_query`
5. User can apply as `Replace` or `Append`.

## Backend/API Requirements

- add a preview API path that accepts uploaded `.docx` as multipart file
- service stores uploaded input into controlled temp path and reuses existing preview service
- response contract should remain aligned with current `MatrixPreviewResponse` fields
- keep route thin; no Office access in route body

## Acceptance Criteria

- Matrix Editor action bar no longer shows duplicate structural edit buttons or placeholder controls.
- User can import `.docx` through file picker without manually typing file path.
- Preview/apply flow remains functional with replace/append and draft version creation.
- Existing manual selector fields still work for correction scenarios.
- `TASK_252` parser/API capabilities remain intact for path-based diagnostics.
- Build and targeted tests pass.

## Validation

```powershell
py -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_source_candidates_api.py -q
```

Result: passed, `7 passed`.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252a or task252 or matrix_editor or task224 or task222"
```

Result: passed, `28 passed`, `69 deselected`.

```powershell
cd frontend
npm run build
```

Result: passed.

Manual smoke:

1. Open Matrix Editor.
2. Verify top action bar only keeps `Import Matrix` and `Undo`.
3. Click `Import Matrix`; choose a local `.docx` from file dialog.
4. Verify preview appears with extraction summary.
5. Optionally enter page/table and re-preview.
6. Apply as replace; verify grid changes and source trace.
7. Re-run with append.

Implemented notes:

- Added upload preview API: `POST /api/test-plan/matrix-preview-from-upload` (`.docx` only).
- Matrix Editor import now supports file-picker-first flow through hidden file input and `Choose .docx` / `Browse`.
- Matrix Editor top action bar now keeps `Import Matrix`, `Choose .docx`, and `Undo` only.
- Removed top placeholder controls: `Display options`, `Filter`, search input.
