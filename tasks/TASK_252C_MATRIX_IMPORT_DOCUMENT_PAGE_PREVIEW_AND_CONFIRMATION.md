# TASK_252C_MATRIX_IMPORT_DOCUMENT_PAGE_PREVIEW_AND_CONFIRMATION

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252C_MATRIX_IMPORT_DOCUMENT_PAGE_PREVIEW_AND_CONFIRMATION`

## Why This Task Is Allowed Now

`TASK_252B` is complete. User confirmed the desired next import workflow:

- select `.docx`
- automatically parse Matrix
- convert selected Word document to PDF preview
- open a large Matrix Editor confirmation dialog
- let user review the original document page like print preview
- reparse by page/table/keyword with debounce
- commit by `Replace` or `Append`, or exit with `Cancel`

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable, but the task is larger than `TASK_252B`.

Reason:

- Requires backend Office gateway work, temporary PDF preview asset handling, API response updates, and a frontend confirmation dialog.
- Still bounded to `.docx` only and reuses existing Matrix parser/import apply flow.
- Does not require AI extraction, PDF table parsing, `.doc` support, Excel support, or execution-domain expansion.

## Objective

Add a document-page preview confirmation workflow for `.docx` Matrix import.

The goal is to let operators verify the source Matrix visually against the original Word document page before importing into Matrix Editor.

## Scope

Allowed:

- `.docx -> PDF` preview generation through Word COM inside Office infrastructure
- temporary preview files under `tmp/matrix_import_previews/`
- automatic cleanup of old preview files when generating a new preview
- upload-based `.docx` Matrix preview extended with PDF preview metadata
- large Matrix Editor modal/dialog for import confirmation
- left-side PDF preview
- right-side locator fields:
  - `Page`
  - `Table on page`
  - `Keyword in table`
- automatic debounce reparse when locator fields change
- `Cancel`, `Replace`, `Append` actions
- existing replace/append import apply behavior

Forbidden:

- `.doc`, `.pdf`, `.xlsx` import support
- embedded Word editing
- browser-side Office automation
- AI extraction
- PDF table extraction
- report/fee/test execution features
- long-term storage of preview PDFs as authoritative project assets

## Acceptance Criteria

- Selecting a `.docx` generates a PDF preview and Matrix parse result.
- Matrix Editor opens a large confirmation dialog after file selection.
- Dialog displays the document preview and current parse summary.
- Dialog shows editable `Page`, `Table on page`, and `Keyword in table`.
- Changing locator fields triggers debounce reparse.
- `Cancel` closes dialog and does not change Matrix grid.
- `Replace` applies parsed Matrix to replace current grid.
- `Append` appends parsed Matrix to current grid.
- Source trace uses original selected filename.
- Temporary PDF preview files are cleaned up on new preview generation.
- If Word COM/PDF export fails, user gets actionable blocker text.
- Existing Matrix import parser behavior remains unchanged for `.docx`.

## Validation

```powershell
py -m pytest tests\integration\test_project_test_plan_preview_api.py tests\unit\test_frontend_shell_files.py -q -k "task252c or task252b or matrix_editor"
```

```powershell
cd frontend
npm run build
```

Manual smoke:

1. Open Matrix Editor.
2. Choose a real `.docx`.
3. Verify confirmation dialog opens.
4. Verify PDF preview renders.
5. Verify automatic parse summary appears.
6. Change page/table/keyword and wait for debounce reparse.
7. Click `Cancel`, verify grid unchanged.
8. Reopen and click `Replace`, verify grid replaced.
9. Reopen and click `Append`, verify grid appended.
