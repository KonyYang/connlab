# TASK_352 PDF Matrix Import Deterministic Preview QA Evidence

Task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`
Lane: `pdf-matrix-import-deterministic-preview`
Role: QA / Smoke Owner
Status: `qa_pass`
Date: 2026-07-06

---

## 0.2 QA Re-smoke After Developer Fix Pass

Status: `qa_pass`
Date: 2026-07-06

Reviewer re-gate reported QA B1 closed. QA re-read Developer evidence, prior QA evidence, current diff/status, PDF gateway/service/API/frontend code, and reran the required focused validation.

Developer fix scope was confirmed as limited to:

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `tests/unit/test_pdf_matrix_source_gateway.py`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`

The fix did not change `ProductSpecMatrixParser`, API client, schema/migration, frontend workflow semantics, OCR/scanned-PDF support, AI parsing, Excel Matrix import, PyMuPDF/MuPDF/fitz dependency, or forbidden adjacent scopes.

### Re-run Validation

Backend focused suite:

```powershell
py -m pytest tests/unit/test_pdf_matrix_source_gateway.py tests/integration/test_project_test_plan_preview_api.py tests/unit/test_product_spec_matrix_parser.py -q
```

Result: `34 passed in 2.68s`.

Frontend focused suite:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace --run
```

Result: `1 file / 38 tests passed`.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed with existing Vite chunk-size warning only.

Python compile:

```powershell
py -m py_compile backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/infrastructure/files/pdf_matrix_source_gateway.py
```

Result: passed with no output.

Static checks:

- `git diff --check -- <TASK_352 package files + QA evidence>` passed with LF/CRLF warnings only.
- trailing whitespace scan on TASK_352 package files + QA evidence returned no matches.
- added-line dependency/scope/no-real-path scan found no PyMuPDF/MuPDF/fitz, OCR engine, AI parsing, Excel Matrix import, user sample path, public-drive/workbook, project-folder, or real-file mutation additions. The only file-copy hit was the approved upload preview temp-copy path `copyfile(temp_path, preview_pdf_path)`.
- forbidden-scope diff scan found no TASK_352 changes under Fee Evaluation, New Project, Workbench, Projects list, `.agents/**`, `docs/project_management/**`, release/packaging, or LTR/public-folder application paths.

### B1 Read-only Real Sample Re-smoke

All four user-provided PDF sample paths were present. QA used `PYTHONDONTWRITEBYTECODE=1` and `PYTHONIOENCODING=utf-8` and probed through `PdfMatrixSourceGateway` plus `ProjectTestPlanMatrixPreviewService` without modifying or copying the original sample files.

Results:

- `GS-12-2186 DC PDU_Rev1-20260424__for qualification test.pdf`
  - gateway: ok, `18` extracted candidate tables
  - preview: `supported`, selected page/table `(9, 2)`, `11` groups, `2` rows, no blockers
- `PRODSPEC GS-12-2268 Customized REC 4HP+4S Cable Assembly CO.pdf`
  - gateway: ok, `15` extracted candidate tables
  - preview: `supported`, selected page/table `(11, 2)`, `15` groups, `28` rows, no blockers
- `GS-12-1507 RA Coplanar Rev7 (3).pdf`
  - target locator: page `8`, table `2`
  - gateway: ok, `11` extracted candidate tables
  - preview with locator: `supported`, selected `(8, 2)`, `10` groups, `26` rows, no blockers
  - auto preview: `supported`, selected `(8, 2)`, `10` groups, `26` rows, no blockers
- `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`
  - target locator: page `11`, table `2`
  - gateway: ok, `17` extracted candidate tables
  - preview with locator: `supported`, selected `(11, 2)`, `11` groups, `24` rows, no blockers
  - auto preview: `supported`, selected `(11, 2)`, `11` groups, `24` rows, no blockers

B1 is closed.

### Upload Route Smoke With Real PDFs

QA also used FastAPI `TestClient` to exercise the live upload-preview route against all four read-only sample PDFs. This covers upload validation, `.pdf` source format, locator forwarding, preview token creation, and PDF preview token retrieval without browser commit actions.

Route:

```text
POST /api/test-plan/matrix-preview-from-upload
GET /api/test-plan/matrix-preview-pdf/{token}
```

Results:

- all four uploads returned HTTP `200`;
- all four returned `capability_status: supported`;
- all four returned `source_format: .pdf`;
- all four returned a `preview_pdf_token`;
- all four preview tokens returned HTTP `200` with `content-type: application/pdf`;
- B1 target samples selected `(8, 2)` and `(11, 2)` respectively with no blockers.

### Browser / Live UI Note

QA started the local backend/frontend dev scripts and verified:

- `http://127.0.0.1:8000/health` returned HTTP `200`;
- `http://localhost:5173/projects` returned HTTP `200`;
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` has the expected hidden file input `accept=".pdf,.doc,.docx"` and `Source PDF Preview` iframe path;
- focused MatrixEditorWorkspace tests passed, covering the UI import behavior.

Direct Playwright browser click/upload smoke could not complete because:

- bundled Playwright Chromium executable is missing;
- using system Chrome executable failed with `spawn EPERM` in this sandboxed thread.

This is recorded as a non-blocking tooling residual because the route-level upload smoke with real PDFs and the frontend focused UI tests both passed, and the original B1 was a backend PDF gateway/service acceptance failure that is now directly verified closed.

Local frontend dev process was stopped after the probe. Backend process cleanup was attempted; Windows reported an orphan/stale listener on `127.0.0.1:8000` with PID `12580` that `Get-Process`, WMI, and `taskkill` could not resolve. This appears to be an environment cleanup residual, not a TASK_352 product finding.

### Re-smoke Result

`QA re-smoke gate: pass`

Recommended next role: Integrator packaging/readiness.

Residual risks:

- Direct browser click/upload smoke remains a tooling residual due unavailable browser launch, but backend upload route, preview token, sample locator behavior, and frontend component behavior are covered.
- External Settings/LTR, desktop/release, New Project test residuals, board residuals, and unrelated packaging files remain excluded from TASK_352 packaging.

---

## Sources Read

QA re-read and verified the gate against:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md`
- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_planner.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_decision_planner.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_reconciliation_planner.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_implementation_reconciliation_planner.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`
- Reviewer callback reporting `reviewer_pass`
- Current `git status --short` and TASK_352 diff
- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- focused TASK_352 tests

QA did not modify product code, tests, board, package files, real PDFs, public-drive folders, workbook files, or project folders.

---

## Automated Validation

Backend focused suite:

```powershell
py -m pytest tests/unit/test_pdf_matrix_source_gateway.py tests/integration/test_project_test_plan_preview_api.py tests/unit/test_product_spec_matrix_parser.py -q
```

Result: `31 passed in 2.69s`.

Frontend focused suite:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace --run
```

Result: `1 file / 38 tests passed`.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed with existing Vite chunk-size warning only.

Python compile:

```powershell
py -m py_compile backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/infrastructure/files/pdf_matrix_source_gateway.py
```

Result: passed with no output.

Diff/static checks:

- `git diff --check -- <TASK_352 package files>`: passed with LF/CRLF warnings only.
- trailing whitespace scan on TASK_352 package files: no matches.
- dependency/scope scan: no `pymupdf`, `pymupdf4llm`, `pymupdfpro`, `fitz`, direct Excel Matrix import, AI parsing, or OCR engine imports. One expected blocker copy mentions OCR is not supported.
- `pyproject.toml` added only `pdfplumber>=0.11,<1.0`.
- Matrix Editor changed file accept to `.pdf,.doc,.docx`.
- No forbidden-scope diff was found under Fee Evaluation, New Project, Workbench, Projects list, `.agents/**`, `docs/project_management/**`, release/packaging, or LTR/public-folder application paths.
- Added-line no-real-path scan found only the approved upload preview temp-copy implementation (`copyfile(temp_path, preview_pdf_path)`), not real user/public-drive/workbook/project-folder mutation.

---

## Read-Only Real Sample Smoke

All four user-provided PDFs were present and probed read-only through `PdfMatrixSourceGateway` and `ProjectTestPlanMatrixPreviewService`. No sample file was copied, edited, deleted, committed, or packaged.

Probe command shape:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
py -c "<read-only PdfMatrixSourceGateway + ProjectTestPlanMatrixPreviewService probe over the four user sample paths>"
```

Sample observations:

- `GS-12-2186 DC PDU_Rev1-20260424__for qualification test.pdf`
  - gateway: ok, `19` extracted tables
  - preview: `supported`, selected page/table `(10, 3)`, `1` group, `3` rows
- `PRODSPEC GS-12-2268 Customized REC 4HP+4S Cable Assembly CO.pdf`
  - gateway: ok, `16` extracted tables
  - preview: `supported`, selected page/table `(11, 2)`, `15` groups, `28` rows
- `GS-12-1507 RA Coplanar Rev7 (3).pdf`
  - gateway: ok, `11` extracted tables
  - expected accepted locator from task/plan: page `8`, table `2`
  - locator page `8`, table `2` maps to extracted table index `9`, rows `34`, cols `13`, preview starts with `TEST GROUP ID: | 1 | 2 | 3 | ...`
  - preview with locator returned `unsupported`
  - blocker: `Selected table 9 is not a valid Matrix table.`
  - auto preview without locator also returned `unsupported`
  - auto blocker: `No Matrix table with test items, section, and Group columns was found.`
- `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`
  - gateway: ok, `18` extracted tables
  - expected accepted locator from task/plan: page `11`, table `2`
  - locator page `11`, table `2` maps to extracted table index `16`, rows `27`, cols `14`, preview starts with `TEST GROUP ID: | 1 | 2 | 3 | ...`
  - preview with locator returned `unsupported`
  - blocker: `Selected table 16 is not a valid Matrix table.`
  - auto preview without locator returned `supported`, but selected page/table `(12, 2)` with only `1` group and `1` row, which is not the task-accepted target Matrix locator.

Browser smoke was not run after the real-sample service/gateway probe produced blocking acceptance failures. The read-only backend probe exercises the relevant deterministic PDF gateway, locator, and parser path directly without mutating real files.

---

## Historical Blocking Finding - Closed In Re-smoke 0.2

### B1 - Accepted real-sample PDF locators fail Matrix preview

Original severity: blocking

Current disposition: closed by Developer fix pass and QA re-smoke 0.2 above.

Expected:

- TASK_352 acceptance and source-of-truth records require the two confirmed text-PDF locator samples to be supported:
  - `GS-12-1507`, page `8`, table `2`
  - `PRODSPEC GS-12-1941`, page `11`, table `2`
- Upload/preview should reuse the deterministic PDF gateway, locator selection, and existing Matrix parser to return a normal Matrix preview for these target tables, or at minimum not reject the accepted target tables as invalid.

Observed:

- `GS-12-1507` page `8`, table `2` is extracted as table index `9` with a Matrix-like `TEST GROUP ID` preview, but preview returns `unsupported` with `Selected table 9 is not a valid Matrix table.`
- `GS-12-1941` page `11`, table `2` is extracted as table index `16` with a Matrix-like `TEST GROUP ID` preview, but preview returns `unsupported` with `Selected table 16 is not a valid Matrix table.`
- `GS-12-1941` without locator auto-selects a different table `(12, 2)` and returns only `1` group / `1` row, so auto-selection does not satisfy the accepted locator smoke either.

Repro steps:

1. Ensure the two local read-only sample PDFs exist at:
   - `C:/Users/White/Desktop/AI information/Spec/GS-12-1507 RA Coplanar Rev7 (3).pdf`
   - `C:/Users/White/Desktop/AI information/Spec/PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`
2. From repo root, run a read-only probe:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
py -c "from pathlib import Path; from backend.infrastructure.files.pdf_matrix_source_gateway import PdfMatrixSourceGateway; from backend.application.project_test_plan_matrix_preview_service import ProjectTestPlanMatrixPreviewService, MatrixPreviewFromPathCommand; gateway=PdfMatrixSourceGateway(); service=ProjectTestPlanMatrixPreviewService(pdf_gateway=gateway); samples=[('GS-12-1507', r'C:/Users/White/Desktop/AI information/Spec/GS-12-1507 RA Coplanar Rev7 (3).pdf', (8,2)), ('GS-12-1941', r'C:/Users/White/Desktop/AI information/Spec/PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf', (11,2))]; [print(label, service.preview_from_path(MatrixPreviewFromPathCommand(project_id='QA-TASK-352', source_path=Path(path), page_number=loc[0], page_table_index=loc[1])).capability_status, list(service.preview_from_path(MatrixPreviewFromPathCommand(project_id='QA-TASK-352', source_path=Path(path), page_number=loc[0], page_table_index=loc[1])).blockers)) for label,path,loc in samples]"
```

3. Observe `unsupported` with the selected-table invalid blockers above.

Historical suggested next role: Developer fix pass.

Likely fix area: TASK_352 implementation boundary, probably PDF gateway table normalization/table-context extraction and/or parser compatibility for PDF-extracted Matrix tables. Do not expand into OCR, AI parsing, Excel import, or general Matrix parser rule expansion beyond the approved TASK_352 compatibility need without Planner/Reviewer reconciliation.

---

## Historical Initial Result

`QA gate: blocked` before Developer fix pass.

Current result is superseded by `QA re-smoke gate: pass` in section 0.2.

Historical blocker summary: accepted real-sample PDF locator smoke failed for `GS-12-1507` page `8` table `2` and `GS-12-1941` page `11` table `2`; both target tables were extracted but rejected as invalid Matrix tables.
