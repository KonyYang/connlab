# TASK_252C Plan - Matrix Import Document Page Preview And Confirmation

## 1. Task Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task before this plan: none
- New planned task: `TASK_252C_MATRIX_IMPORT_DOCUMENT_PAGE_PREVIEW_AND_CONFIRMATION`
- Why allowed: `TASK_252B` is complete and the user confirmed the PDF preview confirmation workflow.

## 2. Goal

Add a source-document preview workflow for `.docx` Matrix import:

```text
choose .docx -> upload -> parse Matrix + export PDF preview -> show confirmation dialog -> debounce reparse by page/table/keyword -> Cancel/Replace/Append
```

This is a usability and verification task. It does not add new import formats.

## 3. Backend Design

### 3.1 Word To PDF Preview

Add Office-boundary support under `backend/infrastructure/office`.

Recommended method:

```python
OfficeFacade.export_word_preview_pdf(source_path: Path, output_dir: Path) -> Path
```

Implementation:

- use Word COM inside `WordDocumentGateway`
- open source read-only
- export as PDF into `tmp/matrix_import_previews/`
- close document and Word application reliably
- raise actionable Office automation error when Word COM is unavailable

### 3.2 Temporary Preview Directory

Use:

```text
tmp/matrix_import_previews/
```

Rules:

- create directory if missing
- clean old preview files before generating a new preview
- keep preview PDF only for current workflow validation
- do not treat preview PDF as authoritative project asset

### 3.3 API Contract

Extend upload preview response or add companion response fields:

- `preview_pdf_url` or `preview_pdf_path_token`
- `preview_page_count` if cheaply available
- existing Matrix preview fields:
  - `selected_table_index`
  - `selected_page_number`
  - `selected_page_table_index`
  - `candidate_tables`
  - `groups`
  - `warnings`
  - `blockers`

Recommended:

- keep existing `MatrixPreviewResponse` mostly stable
- add optional preview fields to avoid a separate frontend round trip

### 3.4 Serving Preview PDF

Add a thin API route that serves generated preview PDF by controlled token/path under `tmp/matrix_import_previews/`.

Security constraints:

- do not allow arbitrary file path reads
- route must only serve files inside the preview directory
- reject missing/invalid token

## 4. Frontend Design

### 4.1 Trigger

`Choose .docx` remains the only entry.

After file selection:

1. upload file
2. backend parses and exports PDF
3. open import confirmation dialog

### 4.2 Confirmation Dialog

Large dialog inside Matrix Editor:

- left: PDF preview
- right: locator and parse state
- footer: `Cancel`, `Replace`, `Append`

Locator fields:

- `Page`
- `Table on page`
- `Keyword in table`

State:

- initial auto-parse result shown immediately
- field changes debounce reparse
- while reparse is pending, `Replace` and `Append` disabled
- if reparse fails, show blocker and keep dialog open

### 4.3 PDF Display

First implementation can use browser PDF rendering:

```tsx
<iframe src={previewPdfUrl} />
```

If browser PDF behavior is not good enough, a later task can replace iframe with page-image rendering.

## 5. File-Level Change Plan

Backend:

- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/api/routes_project_test_plan.py`
- optionally `backend/application/project_test_plan_matrix_preview_service.py`

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`

Tests:

- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_frontend_shell_files.py`

Docs:

- `tasks/TASK_252C_MATRIX_IMPORT_DOCUMENT_PAGE_PREVIEW_AND_CONFIRMATION.md`
- `docs/task_board.md`

## 6. Risks

1. Word COM PDF export reliability
   - Mitigation: keep COM inside gateway, close document/application in `finally`, return actionable blocker.

2. Temporary file cleanup
   - Mitigation: clean `tmp/matrix_import_previews/` before creating a new preview.

3. Browser PDF preview differences
   - Mitigation: start with iframe PDF preview; later task can convert pages to images if needed.

4. Debounce stale parse state
   - Mitigation: track selector key and disable `Replace`/`Append` while parsing or stale.

5. Upload filename vs temp filename
   - Mitigation: keep original filename in frontend display and source trace.

## 7. Validation Plan

Backend/API:

```powershell
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
```

Frontend static:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252c or task252b or matrix_editor"
```

Frontend build:

```powershell
cd frontend
npm run build
```

Manual with real sample:

1. choose `GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`
2. verify PDF preview opens in dialog
3. verify auto parse finds Matrix table
4. adjust page/table/keyword and wait for debounce reparse
5. use Cancel, Replace, Append paths

## 8. Stop Point

Do not implement until user explicitly approves `TASK_252C`.

