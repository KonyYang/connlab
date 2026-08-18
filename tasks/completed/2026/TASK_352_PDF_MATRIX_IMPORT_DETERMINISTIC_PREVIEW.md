# TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW

Status: complete - Integrator accepted
Lane: pdf-matrix-import-deterministic-preview
Owner: Planner / Reviewer
Created: 2026-07-05

## Goal

Plan a controlled Matrix Editor import lane that adds deterministic text-PDF Matrix preview support. PDF input should produce the same neutral document shape used by the existing Word path: tables, paragraphs, page/table locator metadata, and a preview PDF token, then reuse the current `ProductSpecMatrixParser`, Matrix preview API response, PDF preview iframe, locator Reparse, Replace/Append, group selection, and commit flow.

This lane is first-version text-PDF support only. It must not implement OCR, scanned-PDF support, AI parsing, Excel Matrix import, Matrix parser rule expansion, Confirmed Matrix semantic changes, Fee/Test Record/lifecycle changes, or storage schema changes unless separately planned and approved.

## Current Phase And Authorization

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current board context: TASK_350A `.doc` compatibility, TASK_350B stale-preview Reparse guard, and TASK_350C native confirm removal are complete/accepted. TASK_351 is separately implementation-authorized and must not be mixed with TASK_352.
- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Dependency decision was reconciled to the permissive `pdfplumber` / optional direct `pdfminer.six` path.
- Developer planning update completed.
- Reviewer implementation-readiness re-gate passed.
- User approved source-of-truth reconciliation and Developer implementation.
- Developer implementation is authorized only for the scope in this task/plan and remains pending.
- PyMuPDF / MuPDF is not approved as a default TASK_352 product dependency. Do not add `pymupdf`, `pymupdf4llm`, or `pymupdfpro` unless a later explicit AGPL/commercial-license decision reopens that path.

## Confirmed By User

- Matrix Editor should support importing PDF Matrix source files.
- PDF extraction should follow the existing Word `.docx` / `.doc` Matrix extraction rules and methods where possible.
- First version is limited to text PDFs. Scanned PDFs and OCR are out of scope.
- User supplied sample PDFs:
  - `C:/Users/White/Desktop/AI information/Spec/GS-12-2186 DC PDU_Rev1-20260424__for qualification test.pdf`
  - `C:/Users/White/Desktop/AI information/Spec/PRODSPEC GS-12-2268 Customized REC 4HP+4S Cable  Assembly CO.pdf`
  - `C:/Users/White/Desktop/AI information/Spec/GS-12-1507 RA Coplanar Rev7 (3).pdf`
  - `C:/Users/White/Desktop/AI information/Spec/PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`
- User accepted current first-pass sample findings that `GS-12-1507` and `PRODSPEC GS-12-1941` are text PDFs with extractable target Matrix tables.
- User accepted locator expectations: `GS-12-1507` Matrix is page 8 table 2; `PRODSPEC GS-12-1941` Matrix is page 11 table 2.

## Confirmed By Repository Evidence

- `backend/application/project_test_plan_matrix_preview_service.py` already coordinates Matrix previews and currently defers `.pdf` with a blocker message.
- `backend/api/routes_project_test_plan.py` already exposes `POST /api/test-plan/matrix-preview-from-upload`, optional `page_number`, `page_table_index`, and `table_text_query` form fields, and `GET /api/test-plan/matrix-preview-pdf/{token}` for the preview iframe.
- `ProjectTestPlanMatrixPreview` already carries source format, selected table/page metadata, candidate tables, preview PDF token, parsed rows, groups, warnings, and blockers.
- `ProductSpecMatrixParser.parse_tables(...)` already accepts neutral `tables`, optional `paragraphs`, `selected_table_index`, and `table_contexts`.
- TASK_350A added `.doc` support by wrapping legacy source conversion and reusing the `.docx` Matrix preview flow. This is the pattern TASK_352 should follow for PDF: add a source gateway, not a new parser or frontend workflow.
- TASK_350B and TASK_350C completed the current Matrix import modal behavior for stale locator Reparse/Replace and direct Import Matrix entry.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` currently accepts `.doc,.docx`, calls `previewProjectTestPlanMatrixFromUpload(...)`, uses preview PDF tokens, locator fields, Replace/Append, group selection, and commit flow.
- `tests/integration/test_project_test_plan_preview_api.py` currently asserts `.pdf` is deferred. TASK_352 should replace or extend this coverage.
- `pyproject.toml` currently has no obvious PDF table extraction dependency. Developer planning must choose a deterministic dependency/adapter or implement an approved lightweight gateway.

## Inferred By Planner

- TASK_352 should be one formal planned lane covering backend PDF gateway/API integration plus small frontend accept-list/regression tests, because the value appears only when upload, preview, locator, parser reuse, and UI flow work together.
- The core backend abstraction should be a new PDF source gateway that returns a Word-like neutral snapshot: `paragraphs`, `tables`, table locations, and page/table metadata.
- The API route should not parse PDFs directly. It should call the application service, which calls the infrastructure gateway.
- The existing PDF preview iframe can serve the uploaded PDF itself or a controlled temp copy/token instead of exporting a new PDF.
- Developer planning must confirm the deterministic PDF table extraction library/approach, sample fixture strategy, and failure messages before implementation.

## Not Yet Confirmed

- Exact implementation details must remain inside the approved dependency strategy: `pdfplumber>=0.11,<1.0` is the primary dependency; direct `pdfminer.six>=20240706,<20270000` is allowed only if lower-level layout API usage is proven necessary during implementation.
- Whether user sample PDFs can be committed as sanitized fixtures. If not, tests should use generated/minimal text-PDF fixtures and record real-sample smoke as QA/manual residual.
- Whether all four provided PDFs should be in V1 acceptance, or whether V1 requires at least the two confirmed text-PDF locator cases plus graceful blockers for unsupported PDFs.

These unknowns do not block the reconciled implementation authorization if Developer keeps the approved dependency, fixture, and validation boundaries and records any residual sample-smoke limits in evidence.

Dependency/license decision:

- User chose option 1: permissive-license path using `pdfplumber` / `pdfminer.six`.
- PyMuPDF / MuPDF remains locked out as a default product dependency.
- `pyproject.toml` May Touch is limited to `pdfplumber` / `pdfminer.six` or their Reviewer-approved transitive requirements during future implementation authorization.

## Planned Scope

In scope after later approval:

- Add deterministic text-PDF source gateway behind backend infrastructure/application boundaries.
- Allow Matrix preview upload for `.pdf`.
- Convert PDF source content into neutral tables/paragraphs/page-table locator metadata compatible with `ProductSpecMatrixParser`.
- Reuse existing Matrix preview response, preview PDF token, locator Reparse, Replace/Append, group selection, and commit flow.
- Preserve `.docx` and `.doc` import behavior from TASK_350A.
- Add business-readable failures for scanned PDFs, no text, extraction failure, no Matrix table, and locator mismatch.
- Add focused backend/frontend tests and, if possible, real-sample manual smoke notes for the provided PDFs.

Out of scope:

- OCR or scanned PDF support.
- AI parsing or heuristic free-form interpretation beyond deterministic table/text extraction.
- Excel Matrix import.
- Matrix parser business rule expansion.
- Confirmed Matrix, Fee Evaluation, Test Record, lifecycle, Workbench, Projects, Intake/LTR, or Folder Actions semantic changes.
- Storage schema/migrations unless separately justified and re-gated.
- Real user document mutation.

## May Touch Draft

- `backend/application/project_test_plan_matrix_preview_service.py`
- New backend PDF gateway under `backend/infrastructure/files/` or `backend/infrastructure/office/` if it keeps PDF reading out of API routes.
- `backend/api/routes_project_test_plan.py`
- `backend/api/dependencies.py` only if dependency injection for the PDF gateway/service changes.
- `backend/modules/test_plan/product_spec_matrix_parser.py` only for compatibility tests or adapter-facing assumptions; no parser rule changes unless Reviewer explicitly approves a separate parser bugfix.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if DTO/type changes are unavoidable.
- `pyproject.toml` only for a Reviewer/User-approved permissive PDF extraction dependency path, expected to start with `pdfplumber` / `pdfminer.six`; PyMuPDF remains locked unless separately approved.
- Focused backend/frontend tests for PDF upload preview, locator, parser reuse, and regressions.
- TASK_352 docs/evidence/board through normal lane flow.

## Must Not Touch

- OCR/scanned-PDF engines or AI parsing.
- Matrix parser business rules unless split into a separately approved parser lane.
- Confirmed Matrix authority, Fee Evaluation, Test Record, lifecycle, Workbench, Folder Actions, Intake/LTR, Projects registry/list.
- Database schema/migrations unless separately justified and re-gated.
- Real user PDFs outside controlled read-only smoke; no mutation of sample files.
- Real public-drive, workbook, or project folder data.
- Release/settings/basic-information residual cleanup.
- `.agents/**`
- `docs/project_management/**`

## Locked Paths

- `backend/modules/fee_evaluation/**`
- `frontend/src/features/fee-evaluation/**`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `dist_release/**`
- `packaging/**`
- Real `D:\Test Project/**`, `D:\PublicProject/**`, public-drive roots, workbook authority files, and user PDF sources.

## Acceptance Criteria Draft

- Matrix Editor file selector allows `.pdf,.doc,.docx`.
- Existing `.docx` and `.doc` import flows remain green.
- Uploading a text PDF calls a backend PDF source gateway and returns a normal Matrix preview response.
- PDF preview iframe opens the same uploaded PDF preview token and page locator.
- Page / Table on page / Keyword locator works for PDF candidate table metadata and participates in existing TASK_350B Reparse/Replace behavior.
- The two confirmed text-PDF samples are supported by manual/QA smoke or equivalent controlled fixtures:
  - `GS-12-1507`, page 8, table 2.
  - `PRODSPEC GS-12-1941`, page 11, table 2.
- Scanned/no-text PDFs return a business-readable blocker and do not call Matrix commit.
- No OCR, AI, parser-rule expansion, Confirmed Matrix authority change, Fee/Test Record/lifecycle change, schema change, or real-file mutation is included.

## Validation Gate Draft

- Backend unit tests for PDF gateway text/table extraction and failure mapping.
- Backend integration tests for `POST /api/test-plan/matrix-preview-from-upload` with `.pdf`, including supported text PDF, no-text/scanned-style blocker, locator success, locator mismatch, temp/token cleanup, and `.docx` / `.doc` regression.
- Frontend focused tests proving file selector accepts `.pdf,.doc,.docx`, PDF preview response opens the existing import modal/iframe, locator Reparse works, and Replace/Append remain the existing flow.
- Build and package scans:
  - `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_product_spec_matrix_parser.py -q`
  - new focused PDF gateway tests
  - `npm test -- MatrixEditorWorkspace --run`
  - `npm run build`
  - `git diff --check`
  - trailing whitespace and forbidden-scope status scans.
- QA/manual smoke on the provided real PDFs if available in the local environment, read-only only.

## Merge Gate Draft

- Reviewer plan gate must pass before Developer planning-first.
- User must explicitly approve Developer planning-first.
- Developer planning-first confirmed the PDF extraction dependency/gateway, fixture strategy, and exact implementation file list.
- Reviewer implementation-readiness re-gate passed before implementation authorization.
- User explicitly approved implementation after source-of-truth reconciliation.
- Reviewer implementation gate, QA gate, and Integrator packaging/readiness must pass before completion.

## Definition Of Ready

Ready for planned lane creation: yes.

Ready for Developer planning update: complete. The plan has been updated away from PyMuPDF and onto the permissive `pdfplumber` / optional direct `pdfminer.six` path.

Ready for approved implementation: yes. TASK_352 is implementation-authorized and pending Developer implementation only within the reconciled deterministic text-PDF scope, dependency decision, May Touch list, and locked paths above.

## Integrator Closeout

Date: 2026-07-06

Integrator gate: accepted.

Acceptance facts:

- Reviewer implementation gate and re-gate passed.
- QA re-smoke gate passed after Developer fix pass.
- The accepted package adds deterministic text-PDF Matrix import support through the approved permissive `pdfplumber>=0.11,<1.0` dependency and a backend PDF source gateway.
- PDF source extraction produces Word-like tables, paragraphs, page/table locator metadata, and table context for the existing Matrix parser and preview flow.
- Matrix Editor now accepts `.pdf,.doc,.docx`; the existing modal, preview iframe, locator/Reparse, TASK_350B stale Replace, Replace/Append, group selection, and commit flow remain reused.
- Read-only real-sample smoke passed for all four user PDFs; the accepted B1 locators now pass.
- Direct Playwright browser upload smoke remains a non-blocking tooling residual because browser launch was unavailable; route-level real-PDF upload smoke and frontend focused tests passed.
- No PyMuPDF/MuPDF/fitz, OCR, AI parsing, Excel Matrix import, parser rule expansion, Confirmed Matrix/Fee/Test Record/lifecycle semantic change, schema change, real user sample mutation, `.agents/**`, or `docs/project_management/**` changes were included.
- Remote push was intentionally not performed.
