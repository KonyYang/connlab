# TASK_252A Plan - Matrix Editor Import UI And Entry Refinement

## 1. Task Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task before this plan: none
- New planned task: `TASK_252A_MATRIX_EDITOR_IMPORT_UI_AND_ENTRY_REFINEMENT`
- Why allowed now: user requested execution of focused UX follow-up after `TASK_252` completion

## 2. Goal

Turn current Matrix import flow from path-first engineering UI to operator-friendly file-picker-first UI, while preserving existing `.docx` preview/apply capability.

## 3. Design Decisions

1. Keep `Undo` in top bar for import rollback safety.
2. Remove duplicate structural buttons in top bar:
   - `Add test item`
   - `Add group`
3. Remove placeholder controls until real behavior exists:
   - `Display options`
   - `Filter`
   - search input
4. Make `Import Matrix` open file chooser for `.docx`.
5. Introduce upload-based preview API entry rather than relying only on absolute path input.

## 4. Backend Plan

### 4.1 API

Add route in `backend/api/routes_project_test_plan.py`:

- `POST /api/test-plan/matrix-preview-from-upload`
- multipart form fields:
  - `project_id` (optional)
  - `file` (`.docx` only)
  - `page_number` (optional)
  - `page_table_index` (optional)
  - `table_text_query` (optional)

### 4.2 Application Service Reuse

Reuse existing `ProjectTestPlanMatrixPreviewService.preview_from_path` by:

1. writing upload bytes into controlled temporary file with `.docx` suffix
2. invoking existing command path
3. removing temp file after preview

No parser redesign in this task.

### 4.3 Validation Guard

- reject non-`.docx` upload at API layer with actionable error
- keep existing deferred behavior for path-based `.doc`/`.pdf` endpoint unchanged

## 5. Frontend Plan

### 5.1 API Client

Add client method:

- `previewProjectTestPlanMatrixFromUpload(formData)`

Keep current `previewProjectTestPlanMatrixFromPath` for diagnostics compatibility.

### 5.2 Matrix Editor UI

In `MatrixEditorWorkspace.tsx`:

1. Top action bar:
   - keep `Import Matrix`, `Undo`
   - remove top-level `Add test item`, `Add group`, right-side placeholders
2. Import panel:
   - add hidden `<input type="file" accept=".docx">`
   - `Import Matrix` triggers file input
   - selected file name shown in import panel
   - preview uses upload API first
   - optional manual selectors still available for re-preview
3. Apply path unchanged:
   - replace/append behavior
   - create new draft before apply
   - source trace visible

## 6. Files To Change

Backend:

- `backend/api/routes_project_test_plan.py`
- optionally small helper in application layer if needed for temporary upload handling

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`

Tests:

- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_frontend_shell_files.py`

Docs:

- `tasks/TASK_252A_MATRIX_EDITOR_IMPORT_UI_AND_ENTRY_REFINEMENT.md`
- `docs/task_board.md`

## 7. Risks And Mitigations

1. Upload temp-file lifecycle:
   - risk: temp artifacts left behind
   - mitigation: `try/finally` cleanup
2. Frontend state branching between path preview and upload preview:
   - risk: regress existing import apply
   - mitigation: keep one unified preview response state model
3. Browser file dialog limitations:
   - risk: cannot enforce initial folder
   - mitigation: accept current browser behavior; keep manual path diagnostic route

## 8. Validation

```powershell
py -m pytest tests\integration\test_project_test_plan_preview_api.py tests\integration\test_project_test_plan_source_candidates_api.py -q
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252a or task252 or matrix_editor"
```

```powershell
cd frontend
npm run build
```

Manual:

1. Open Matrix Editor and verify simplified action bar.
2. Use `Import Matrix` file chooser with `.docx`.
3. Validate preview summary and blockers/warnings.
4. Apply replace and append separately.
5. Verify source trace and sample quantity row behavior.

## 9. Stop Point

Do not implement until explicit user approval for `TASK_252A`.

