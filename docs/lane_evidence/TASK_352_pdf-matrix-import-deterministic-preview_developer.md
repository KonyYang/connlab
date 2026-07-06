# TASK_352 Developer Evidence - PDF Matrix Import Deterministic Preview

Status: integrator_accepted

Task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`
Lane: `pdf-matrix-import-deterministic-preview`
Role: Developer
Date: 2026-07-06

---

---

## 0.4 Integrator Packaging Closeout

Date: 2026-07-06

Status: `integrator_accepted`

Integrator accepted the TASK_352 package after Reviewer implementation/re-gate pass and QA re-smoke pass.

Accepted package files:

- `pyproject.toml`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_pdf_matrix_source_gateway.py`
- TASK_352 task/plan/planner/developer/QA/dependency/reconciliation evidence docs
- `docs/task_board.md` TASK_352 closeout

Integrator validation summary:

- Backend focused suite passed: 34 tests.
- Frontend MatrixEditorWorkspace suite passed: 1 file / 38 tests.
- `py_compile` passed for TASK_352 backend modules/routes.
- `npm run build` passed with existing Vite chunk-size warning only.
- Line-count scan passed for TASK_352 backend files.
- Staged diff check, whitelist check, forbidden-path check, trailing whitespace scan, dependency/static scan, code-only no-real-file mutation scan, and future/external scope scans passed.

Scope notes:

- `pyproject.toml` added only `pdfplumber>=0.11,<1.0`.
- No PyMuPDF/MuPDF/fitz, OCR, AI parsing, Excel Matrix import, parser rule expansion, Confirmed Matrix/Fee/Test Record/lifecycle semantic change, storage schema change, or real user sample mutation was included.
- Direct browser click/upload smoke remains a non-blocking tooling residual because browser launch was unavailable in QA; route-level real-PDF upload smoke and focused frontend tests passed.
- Remote push was intentionally not performed.


## 0.2 Developer Implementation Pass

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`.

Allowed reason:

- Planner implementation reconciliation records Reviewer plan gate passed, Developer planning-first complete, dependency decision reconciled to permissive `pdfplumber`, Reviewer implementation-readiness re-gate passed, and User approval for Developer implementation.
- This pass implemented only deterministic text-PDF Matrix import support for the existing Matrix Editor import flow.

Implementation summary:

- Added `pdfplumber>=0.11,<1.0` as the approved product dependency. No direct `pdfminer.six` pin was added because the implementation uses `pdfplumber` APIs only.
- Added a backend PDF source gateway that reads trusted temporary PDF paths, extracts text paragraphs and text tables, preserves page/table locator metadata, and maps unsupported/no-text/no-table cases to business-readable blockers.
- Integrated `.pdf` into the existing Project Test Plan Matrix preview service so PDF tables feed the existing `ProductSpecMatrixParser` through the same neutral tables/paragraphs contract as Word snapshots.
- Extended the upload preview route to accept `.pdf,.doc,.docx`; PDF uploads reuse the existing preview token endpoint by serving the uploaded temporary PDF copy for the iframe.
- Updated Matrix Editor file accept/copy to allow `.pdf,.doc,.docx` while preserving the existing modal, locator, Reparse, TASK_350B stale Replace, Replace/Append, group selection, and commit flow.
- Added focused generated temporary-PDF tests. The temporary PDF generator uses the existing test environment `reportlab` writer only to create disposable text fixtures; runtime product PDF extraction remains `pdfplumber`-only.

Changed files:

- `pyproject.toml`
- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `tests/unit/test_pdf_matrix_source_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`

Validation results:

- `py -m pytest tests/unit/test_pdf_matrix_source_gateway.py tests/integration/test_project_test_plan_preview_api.py tests/unit/test_product_spec_matrix_parser.py -q`
  - Result: 31 passed.
- `npm test -- MatrixEditorWorkspace --run`
  - Result: 1 file / 38 tests passed.
- `py -m py_compile backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/infrastructure/files/pdf_matrix_source_gateway.py`
  - Result: passed.
- `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- `git diff --check -- <TASK_352 package files>`
  - Result: passed with LF/CRLF warnings only.
- trailing whitespace scan on TASK_352 package files
  - Result: no matches.
- dependency/static scan on TASK_352 package files for `pymupdf`, `pymupdf4llm`, `pymupdfpro`, `fitz`, OCR engines, AI parsing, and Excel Matrix scope
  - Result: no matches.
- no-real-file mutation/static scan on TASK_352 package diff for user sample paths, public project roots, LTR workbook, `.agents`, and `docs/project_management`
  - Result: no matches.
- targeted forbidden-scope status
  - Result: TASK_352 package changed only approved Matrix preview/backend gateway/frontend Matrix Editor files plus evidence. `frontend/src/api/client.ts`, parser business rules, Fee Evaluation, Workbench, Projects list, `.agents/**`, and `docs/project_management/**` were not changed by this pass.

Residuals and exclusions:

- QA/manual smoke against the user-provided sample PDFs remains a Reviewer/QA residual because automated tests use generated temporary PDFs only and do not mutate or commit real user samples.
- `frontend/src/features/new-project/newProjectRequiredState.test.ts` is visible as an external untracked residual and is excluded from TASK_352.
- Existing LF/CRLF warnings from Git remain unchanged.

Recommended next role: Reviewer implementation gate.


---

## 0.3 Developer Fix Pass For QA B1

Status: fix pass complete - pending Reviewer re-gate / QA re-smoke

QA blocker addressed:

- B1 reported that accepted real-sample PDF locators were extracted but rejected as invalid Matrix tables:
  - `GS-12-1507 RA Coplanar Rev7 (3).pdf`, page `8`, table `2`
  - `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`, page `11`, table `2`
- QA also reported that `PRODSPEC GS-12-1941` auto-selection preferred a later page `12`, table `2` revision-record table instead of the accepted target Matrix table.

Root cause:

- The PDF gateway passed `pdfplumber` table fragments directly to the existing Word-oriented parser.
- In the accepted samples, PDF extraction split Matrix headers across multiple rows: the `TEST GROUP ID` row was separated from the `TEST DESCRIPTION` / `Section` header row by visual group-description rows.
- One sample extracted `SECTION` as `SECTIO N`.
- A PDF revision-record table with `Rev / Page / Description / Date` cells was also passed through as a candidate and scored above the accepted target table, causing wrong auto-selection.

Fix:

- Kept the fix inside `backend/infrastructure/files/pdf_matrix_source_gateway.py`.
- Added PDF table normalization that:
  - repairs the known split `SECTIO N` header token to `SECTION`;
  - collapses PDF-fragmented Matrix header rows so `TEST GROUP ID` and `TEST DESCRIPTION` / `Section` become adjacent in the Word-like table shape consumed by the existing parser;
  - filters obvious PDF revision-record tables before they can become Matrix candidates.
- Did not change `ProductSpecMatrixParser`, parser rules, OCR/scanned-PDF handling, AI parsing, Excel import, API client, schema, or frontend Matrix workflow semantics.

Fix-pass changed files:

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `tests/unit/test_pdf_matrix_source_gateway.py`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`

Validation results after B1 fix:

- `py -m pytest tests/unit/test_pdf_matrix_source_gateway.py tests/integration/test_project_test_plan_preview_api.py tests/unit/test_product_spec_matrix_parser.py -q`
  - Result: 34 passed.
- `npm test -- MatrixEditorWorkspace --run`
  - Result: 1 file / 38 tests passed.
- `py -m py_compile backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/infrastructure/files/pdf_matrix_source_gateway.py`
  - Result: passed.
- `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- Read-only real-sample smoke:
  - `GS-12-2186`: supported.
  - `GS-12-2268`: supported.
  - `GS-12-1507` target locator page `8`, table `2`: supported, selected page/table `8/2`, `10` groups, `26` rows.
  - `GS-12-1507` auto: supported, selected page/table `8/2`, `10` groups, `26` rows.
  - `GS-12-1941` target locator page `11`, table `2`: supported, selected page/table `11/2`, `11` groups, `24` rows.
  - `GS-12-1941` auto: supported, selected page/table `11/2`, `11` groups, `24` rows.
- `git diff --check -- <TASK_352 package files>`
  - Result: passed with LF/CRLF warnings only.
- trailing whitespace scan on TASK_352 package files
  - Result: no matches.
- dependency/static scan for `pymupdf`, `pymupdf4llm`, `pymupdfpro`, `fitz`, OCR engines, AI parsing, and Excel Matrix scope
  - Result: no matches.
- no-real-file mutation/static scan
  - Result: only the approved temp upload preview copy `copyfile(temp_path, preview_pdf_path)` was found; no real user sample, public-drive, workbook, or project folder mutation code was added.
- line-count check
  - `backend/infrastructure/files/pdf_matrix_source_gateway.py`: 228 lines.
  - `backend/application/project_test_plan_matrix_preview_service.py`: 262 lines.
  - `backend/api/routes_project_test_plan.py`: 306 lines.

Residuals and exclusions:

- QA should re-smoke the live UI/import path if required by the gate; this fix pass verified the backend deterministic gateway/service path and existing frontend focused suite.
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_qa.md` is visible as external QA evidence and was not edited.
- `frontend/src/features/new-project/newProjectRequiredState.test.ts` remains an external untracked residual and is excluded from TASK_352.

Recommended next role: Reviewer re-gate / QA re-smoke.

---

## 0.1 Developer Planning Update After Dependency Reconciliation

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`.

Allowed reason:

- Planner dependency reconciliation records that User selected option 1, the permissive-license dependency path using `pdfplumber` / `pdfminer.six`.
- Product implementation remains unauthorized.
- This pass updates planning/evidence only and does not add dependencies or modify product code.

Dependency update:

- The previous PyMuPDF-first planning strategy is superseded.
- `pymupdf`, `pymupdf4llm`, and `pymupdfpro` are not approved for TASK_352 under the current decision.
- Future implementation should use `pdfplumber>=0.11,<1.0` as the primary deterministic text-PDF extraction dependency.
- Direct `pdfminer.six>=20240706,<20270000` should be added only if implementation code uses lower-level `pdfminer.six` APIs beyond the transitive dependency supplied by `pdfplumber`.

Updated gateway plan:

- Keep the PDF gateway under `backend/infrastructure/files/`.
- Use `pdfplumber.open(...)` on trusted temporary PDF paths.
- Extract page text into paragraph-like blocks for the existing parser.
- Extract page tables with `page.extract_tables(...)` or a narrowly configured table-settings wrapper.
- Preserve 1-based PDF `page_number`, per-page `page_table_index`, and global `table_index`.
- Return Word-like neutral `tables`, `paragraphs`, and table-location metadata to `ProjectTestPlanMatrixPreviewService`.
- Do not OCR, call AI, parse Excel, expand Matrix parser rules, mutate PDFs, or parse PDF content in API routes.

Planning files updated in this pass:

- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`

Recommended next role: Reviewer implementation-readiness re-gate.

---

## 1. Gate And Scope

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Allowed reason:

- Orchestrator/User delegation records Reviewer plan gate passed and User approval for TASK_352 Developer planning-first.
- This pass is planning/evidence only. Product implementation is not authorized.

Source-of-truth note:

- Local board/task/plan text still contains planned or Reviewer-plan-gate wording in places.
- This Developer pass does not start implementation and does not update the board.
- Future implementation still requires Reviewer implementation-readiness, explicit User implementation approval, and source-of-truth reconciliation.

Locked scope preserved:

- No backend, frontend, tests, API client, schema, Matrix parser, OCR, AI, Excel import, lifecycle, Workbench, Folder Actions, Intake/LTR, Projects, release/settings, `.agents/**`, or `docs/project_management/**` product changes were made.

---

## 2. Sources Read

Governance and orchestration:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

Product/UI context:

- `$impeccable` context from `PRODUCT.md` / `DESIGN.md`, register: product
- `$impeccable` product reference

TASK_352:

- `tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md`
- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_planner.md`

Matrix import implementation context:

- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `backend/infrastructure/office/models.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/integration/test_project_test_plan_preview_api.py`
- `pyproject.toml`

Recent accepted lane context:

- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`

---

## 3. Current Code Findings

- `ProjectTestPlanMatrixPreviewService.preview_from_path()` currently supports `.docx` and returns a deferred blocker for `.pdf`.
- The upload route already accepts locator fields and serves a controlled preview PDF token, but currently accepts only `.doc,.docx`.
- `WordDocumentSnapshot` and `WordTableLocation` already provide the neutral data shape needed by PDF support.
- `ProductSpecMatrixParser.parse_tables(...)` already accepts neutral tables, paragraphs, selected table index, and table context. TASK_352 should not change parser rules.
- `frontend/src/api/client.ts` already has a generic file upload helper and Matrix preview DTO. No API client contract change is expected for TASK_352.
- `MatrixEditorWorkspace.tsx` already provides the import modal, PDF iframe, locator Reparse, TASK_350B stale Replace behavior, Replace/Append, group selection, and commit flow. Frontend implementation should remain small.
- `pyproject.toml` has no PDF extraction dependency today.
- Current status includes external residuals such as board/planner files, release/packaging, Settings/LTR, desktop, and New Project files. They remain excluded from TASK_352.

---

## 4. Developer Planning Decisions

PDF gateway boundary:

- Add a deterministic PDF source gateway under `backend/infrastructure/files/`.
- Do not parse PDF content in API routes.
- Do not put PDF business extraction inside the Matrix parser.

Dependency decision:

- Superseded by Planner dependency reconciliation and the Developer planning update above.
- Use `pdfplumber>=0.11,<1.0` as the primary implementation candidate for text/table extraction.
- Keep `pdfminer.six` transitive through `pdfplumber` unless direct lower-level layout access is proven necessary.
- Treat `pyproject.toml` as May Touch only after Reviewer/User later authorize implementation of the permissive dependency path.
- PyMuPDF / MuPDF is not approved for TASK_352 under the current decision.

Neutral source shape:

- PDF gateway should produce `paragraphs`, `tables`, and table locations compatible with existing Word location fields: global table index, page number, page-table index, preceding/nearby text, text preview, row count, and column count.
- The application service should resolve locator input through the existing `_select_table_index(...)` path and call `ProductSpecMatrixParser.parse_tables(...)`.

API strategy:

- Extend upload acceptance to `.pdf,.doc,.docx`.
- For PDF uploads, serve a controlled temp copy through the existing preview PDF token endpoint.
- Preserve original uploaded `.pdf` identity in response metadata.
- Keep `.docx` and TASK_350A `.doc` behavior unchanged.

Frontend strategy:

- Change Matrix import file accept list to `.pdf,.doc,.docx`.
- Keep existing upload helper, modal, iframe, locator, Reparse, Replace/Append, group selection, and commit behavior.
- Replace Word-specific loading copy with neutral source-document copy if needed.
- Show PDF-specific wording only when backend blockers return it.

---

## 5. Future May Touch

Backend:

- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `backend/infrastructure/files/pdf_matrix_source_models.py` only if needed for line-count control
- `backend/api/routes_project_test_plan.py`
- `backend/api/dependencies.py` only if dependency injection changes
- `pyproject.toml` only for Reviewer/User-authorized `pdfplumber` and, if needed, direct `pdfminer.six` pins

Frontend:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if implementation proves the existing DTO/helper is insufficient

Tests:

- `tests/unit/test_pdf_matrix_source_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- Existing focused Matrix parser and MatrixEditorWorkspace tests as regressions

Docs/evidence:

- TASK_352 docs/evidence/board via normal lane flow only.

---

## 6. Locked Paths And Exclusions

Do not touch in TASK_352 implementation:

- OCR/scanned-PDF engines
- AI parsing
- Excel Matrix import
- Matrix parser business rules unless a separate parser lane is approved
- Confirmed Matrix authority, Fee Evaluation, Test Record, lifecycle, Workbench, Folder Actions, Intake/LTR, Projects registry/list
- Backend schema/migrations
- Real user sample PDFs except read-only manual or QA smoke
- Real public-drive, workbook, LTR workbook, project folder, `D:\Test Project/**`, or `D:\PublicProject/**` data
- Release/settings/basic-information residual cleanup
- `.agents/**`
- `docs/project_management/**`

---

## 7. Test And Validation Plan

Future implementation tests:

- Gateway unit tests with generated temporary text PDFs for table extraction, page/table locator metadata, and no-text blocker behavior.
- Service/API tests for `.pdf` upload success, locator success, locator mismatch, no Matrix table, no text, preview token behavior, cleanup, `.docx` regression, and `.doc` regression.
- Frontend tests for `.pdf,.doc,.docx` accept list, PDF preview modal/iframe path, locator Reparse, TASK_350B stale Replace behavior, and Replace/Append regressions.

Fixture strategy:

- Do not commit or mutate user sample PDFs in automated tests.
- Use generated temp PDFs and dependency overrides/fakes where table extraction would otherwise be brittle.
- Keep the user-provided sample PDFs as read-only QA/manual smoke residuals, especially `GS-12-1507` page 8 table 2 and `PRODSPEC GS-12-1941` page 11 table 2.

Expected commands after implementation:

- `py -m pytest tests/unit/test_pdf_matrix_source_gateway.py tests/integration/test_project_test_plan_preview_api.py -q`
- `py -m pytest tests/unit/test_product_spec_matrix_parser.py -q`
- `npm test -- MatrixEditorWorkspace --run`
- `npm run build`
- `py -m py_compile backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `git diff --check`
- trailing whitespace scan
- forbidden-scope status scan
- dependency/license scan proving no `pymupdf`, `pymupdf4llm`, `pymupdfpro`, OCR, AI, or Excel Matrix import code/dependency was added
- no-real-file mutation scan for user PDFs, public-drive/workbook paths, and project folder roots

---

## 8. Planning Validation Results

Changed files in this planning-first pass:

- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`

No product code or tests were changed.

Validation:

- Required TASK_352 docs/evidence: present after this pass.
- `git diff --check -- docs/task_352_pdf_matrix_import_deterministic_preview_plan.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`
  - Result: passed, no output.
- trailing whitespace scan on TASK_352 plan/evidence
  - Result: no matches.
- required docs existence check
  - Result: plan, Developer evidence, task file, and Planner evidence all present.
- targeted forbidden-scope status
  - Result: this planning pass changed only TASK_352 plan/evidence. No `MatrixEditorWorkspace`, `MatrixEditorWorkspace.test`, `frontend/src/api/client.ts`, `.agents/**`, or `docs/project_management/**` changes were made.
  - Existing external residuals visible in targeted status remain excluded: `backend/api/routes_settings.py`, `backend/application/ltr_workbook_local_config_service.py`, `backend/application/ltr_workbook_password_settings_service.py`, and `backend/desktop/**`.

Planning update validation:

- Final `git diff --check -- docs/task_352_pdf_matrix_import_deterministic_preview_plan.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`
  - Result: passed, no output.
- Final trailing whitespace scan on TASK_352 plan/evidence
  - Result: no matches.
- Targeted current-strategy scan for old PyMuPDF approval language
  - Result: no active recommendation or approval request for PyMuPDF remains. Remaining `pymupdf>=1.24,<2.0` mention is historical Reviewer B1 context only; current decision locks PyMuPDF out.
- Final targeted forbidden-scope status
  - Result: this planning update changed only TASK_352 plan/evidence. No `pyproject.toml`, `MatrixEditorWorkspace`, `MatrixEditorWorkspace.test`, `frontend/src/api/client.ts`, `.agents/**`, or `docs/project_management/**` changes were made.
  - Existing external residuals visible in targeted status remain excluded: `backend/api/routes_settings.py`, `backend/application/ltr_workbook_local_config_service.py`, `backend/application/ltr_workbook_password_settings_service.py`, and `backend/desktop/**`.

---

## 9. Recommendation

Recommended next role: Reviewer implementation-readiness re-gate.

Reviewer decision points:

- Evaluate `pdfplumber>=0.11,<1.0` as the primary TASK_352 product dependency.
- Confirm whether direct `pdfminer.six` pinning is needed or should remain transitive.
- Confirm Windows/offline packaging impact, generated fixture strategy, table locator mapping, and preserved no-OCR/no-AI/no-parser-rule-expansion scope.
