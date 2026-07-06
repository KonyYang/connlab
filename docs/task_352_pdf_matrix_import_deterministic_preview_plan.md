# TASK_352 PDF Matrix Import Deterministic Preview Plan

Status: complete - Integrator accepted
Task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`
Lane: `pdf-matrix-import-deterministic-preview`
Date: 2026-07-05
Role: Planner / Developer planning refinement / implementation reconciliation

## 1. Current Phase / Active Task / Role / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task context: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW` is implementation-authorized and pending Developer implementation after Reviewer implementation-readiness re-gate and user approval.
- Current role: Planner source-of-truth reconciliation.
- Why allowed: the user and Orchestrator explicitly requested minimal TASK_352 source-of-truth reconciliation before Developer implementation. This pass updates docs/board/evidence only and does not write product code.

## 2. User Goal Restatement

Matrix Editor should support importing Matrix data from text-based PDF product specifications. The first version should follow the existing Word `.docx` / `.doc` Matrix extraction method instead of creating a separate PDF parser experience. PDF should become another source gateway that yields tables, paragraphs, and page/table locator metadata, then the existing parser, preview modal, PDF iframe, locator Reparse, Replace/Append, group selection, and commit flow should continue to do the work. Scanned PDFs, OCR, AI parsing, Excel import, and parser-rule expansion are out of scope.

## 3. Evidence Read

Governance:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `$impeccable` context from `PRODUCT.md` / `DESIGN.md`, register: product
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

Matrix import and recent lane context:

- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts`
- `tests/integration/test_project_test_plan_preview_api.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_qa.md`
- `docs/lane_evidence/TASK_350B_matrix-import-stale-preview-reparse-guard_developer.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`
- `pyproject.toml`
- Current `git status --short`

## 4. Confirmed By User

- Add Matrix Editor PDF Matrix import capability.
- PDF extraction should reference the existing Word Matrix extraction rules/method.
- First version is text-PDF only.
- Do not implement scanned PDF / OCR.
- User supplied four PDF samples:
  - `C:/Users/White/Desktop/AI information/Spec/GS-12-2186 DC PDU_Rev1-20260424__for qualification test.pdf`
  - `C:/Users/White/Desktop/AI information/Spec/PRODSPEC GS-12-2268 Customized REC 4HP+4S Cable  Assembly CO.pdf`
  - `C:/Users/White/Desktop/AI information/Spec/GS-12-1507 RA Coplanar Rev7 (3).pdf`
  - `C:/Users/White/Desktop/AI information/Spec/PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`
- User accepted first-pass findings that `GS-12-1507` and `PRODSPEC GS-12-1941` are text PDFs with extractable target Matrix tables.
- User accepted locator facts for two samples:
  - `GS-12-1507`: page 8, table 2.
  - `PRODSPEC GS-12-1941`: page 11, table 2.

## 5. Confirmed By Repository Evidence

- `ProjectTestPlanMatrixPreviewService.preview_from_path()` currently supports `.docx`, and defers `.pdf` through `_unsupported_format_blocker()`.
- `POST /api/test-plan/matrix-preview-from-upload` accepts `.doc,.docx`, writes upload bytes to temp, exports/serves a PDF preview token, reads table locations, and reuses the preview service.
- The Matrix preview API already has locator form fields: `page_number`, `page_table_index`, and `table_text_query`.
- `MatrixPreviewResponse` already carries candidate table metadata, selected page/table, preview PDF token, rows, groups, warnings, and blockers.
- `ProductSpecMatrixParser.parse_tables()` already accepts neutral tables/paragraphs and an optional selected table index.
- `MatrixEditorWorkspace.tsx` already handles import upload, PDF iframe display through `matrixPreviewPdfUrl`, locator Reparse, stale Replace auto-Reparse, Replace/Append, group selection, and commit.
- TASK_350A proved the compatibility-wrapper pattern for `.doc`: add source conversion/gateway support, then reuse existing `.docx` preview/parser/commit flow.
- TASK_350B proved locator changes must participate in Reparse/Replace freshness.
- TASK_350C removed native confirm without changing the import flow.
- `pyproject.toml` currently has no obvious PDF table extraction dependency.

## 6. Inferred By Planner

- TASK_352 should be a formal lane, not a quick fix, because it touches backend file parsing boundaries, upload API behavior, temporary preview tokens, frontend accepted file types, and real-sample QA expectations.
- The safest architecture is a deterministic PDF source gateway that produces a Word-like neutral snapshot: paragraphs, tables, and page/table metadata.
- The existing Matrix parser should remain unchanged in TASK_352 unless a separate parser bugfix lane is approved.
- The uploaded PDF can likely serve as its own preview PDF token instead of generating another PDF.
- A new PDF extraction dependency may be needed, but the exact dependency must be validated in Developer planning and Reviewer implementation-readiness before product implementation.

## 7. Not Yet Confirmed

No blocker prevents planned lane creation.

Items for Developer planning / Reviewer plan gate:

- Exact deterministic PDF extraction dependency or in-house extraction adapter.
- Whether the provided sample PDFs can be committed as sanitized fixtures, or whether tests must use generated fixtures plus QA read-only smoke on local samples.
- Whether V1 acceptance requires all four samples or the two confirmed text-PDF locator samples plus graceful blockers for unsupported cases.

## 8. Planning Risk

- A PDF library could add packaging or Windows compatibility risk if chosen casually.
- PDF table extraction can look correct visually but produce row/column fragmentation. TASK_352 must validate against page/table locators and not silently parse the wrong table.
- If parser rules are expanded inside TASK_352, the lane could accidentally regress `.docx` Matrix import.
- Real user sample PDFs must not be mutated, copied into uncontrolled package scope, or treated as committed fixtures without explicit approval.

## 9. Task Shape Decision

Recommended lane: one planned lane, `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`.

Why one lane:

- The backend gateway, upload route, frontend accept list, locator behavior, parser reuse, and tests form one vertical compatibility slice.
- Splitting backend and frontend would leave no useful operator-visible PDF import path until both finish.

Fallback split if Reviewer finds risk too high:

- `TASK_352A_PDF_SOURCE_GATEWAY_AND_PREVIEW_API`
- `TASK_352B_MATRIX_EDITOR_PDF_IMPORT_WIRING`
- `TASK_352C_PDF_MATRIX_REAL_SAMPLE_QA`

## 10. Proposed Design

Backend:

- Add a deterministic PDF gateway behind infrastructure/application boundaries.
- Gateway output should be compatible with current parser input:
  - `paragraphs: list[str]`
  - `tables: list[list[list[str]]]`
  - table locations with global table index, PDF page number, page-table index, text preview, row count, column count, and preceding/nearby text context where possible.
- Service should call the PDF gateway for `.pdf` and `ProductSpecMatrixParser.parse_tables(...)` with the selected table index from locator metadata.
- API route should accept `.pdf,.doc,.docx` upload but keep PDF parsing out of the route body.
- Preview token should serve a controlled temp copy of the uploaded PDF through the existing preview PDF endpoint.
- Failure mapping should be business-readable:
  - no extractable text
  - scanned/OCR required but unsupported
  - no Matrix table found
  - selected page/table mismatch
  - PDF extraction dependency unavailable or failed

Frontend:

- Matrix file selector accepts `.pdf,.doc,.docx`.
- Existing import modal, preview iframe, locator fields, Reparse, Replace/Append, group selection, and commit remain the same.
- PDF-specific copy should be minimal and only appear when blocked, for example `No text Matrix table found in this PDF. OCR is not supported in this version.`
- Do not add a separate PDF import page, card stack, or status panel.

## 11. May Touch Draft

- `backend/application/project_test_plan_matrix_preview_service.py`
- New backend PDF gateway under `backend/infrastructure/files/` or `backend/infrastructure/office/`
- `backend/api/routes_project_test_plan.py`
- `backend/api/dependencies.py` only if dependency injection changes
- `backend/modules/test_plan/product_spec_matrix_parser.py` only for adapter-facing compatibility tests, not parser rule changes
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if DTO/type changes are unavoidable
- `pyproject.toml` only if Reviewer approves a deterministic PDF extraction dependency
- Focused backend/frontend tests
- TASK_352 task/plan/evidence/board docs

## 12. Must Not Touch / Locked Paths Draft

Must not touch:

- OCR/scanned-PDF engines.
- AI parsing.
- Excel Matrix import.
- Matrix parser business rules unless separately approved.
- Confirmed Matrix authority, Fee Evaluation, Test Record, lifecycle, Workbench, Folder Actions, Intake/LTR, Projects registry/list.
- Database schema/migrations unless separately justified and re-gated.
- Real sample PDFs except read-only manual/QA smoke.
- Real public-drive, workbook, LTR workbook, or project folder data.
- Release/settings/basic-information residual cleanup.
- `.agents/**`
- `docs/project_management/**`

Locked paths:

- `backend/modules/fee_evaluation/**`
- `frontend/src/features/fee-evaluation/**`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `dist_release/**`
- `packaging/**`
- Real user PDF sources, real `D:\Test Project/**`, real `D:\PublicProject/**`, public-drive roots, and workbook authority files.

## 13. Acceptance Criteria Draft

- `.docx` import behavior remains unchanged.
- `.doc` compatibility from TASK_350A remains unchanged.
- File selector allows `.pdf,.doc,.docx`.
- Uploading a supported text PDF returns a standard Matrix preview response with candidate tables, selected page/table metadata, parsed rows/groups, and preview PDF token.
- Existing PDF iframe and locator controls work for PDF preview.
- Reparse/Replace honors TASK_350B stale preview behavior for PDF.
- Replace/Append/commit reuse existing Matrix import flow.
- `GS-12-1507` page 8 table 2 and `PRODSPEC GS-12-1941` page 11 table 2 are covered by controlled fixture tests or QA read-only smoke.
- Scanned/no-text PDFs return blockers and do not commit.
- No OCR, AI parsing, Excel Matrix import, parser-rule expansion, Confirmed Matrix/Fee/Test Record/lifecycle semantic change, schema change, or real-file mutation is included.

## 14. Validation Gate Draft

Backend:

- PDF gateway unit tests for text extraction, table extraction, page/table locator metadata, no-text/scanned-style blocker, and extraction failure mapping.
- Matrix preview service tests proving PDF source reuses `ProductSpecMatrixParser`.
- API tests for `.pdf` upload success, locator success, locator mismatch, no text, no Matrix table, temp/token cleanup, `.docx` regression, and `.doc` regression.

Frontend:

- MatrixEditorWorkspace focused tests for `.pdf,.doc,.docx` accept list.
- PDF preview response opens the current import dialog/iframe path.
- Locator Reparse and stale Replace behavior remain green.
- Replace/Append/commit flow unchanged.

Commands:

```powershell
py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_product_spec_matrix_parser.py -q
py -m pytest <new-focused-pdf-gateway-tests> -q
npm test -- MatrixEditorWorkspace --run
npm run build
git diff --check
```

Static checks:

- trailing whitespace scan
- forbidden-scope status scan
- no real sample file mutation scan

QA/manual smoke:

- Read-only smoke with local samples if available, especially:
  - `GS-12-1507`, page 8, table 2.
  - `PRODSPEC GS-12-1941`, page 11, table 2.

## 15. Merge Gate Draft

- Reviewer plan gate must pass this planned lane.
- User must explicitly approve Developer planning-first.
- Developer planning-first must confirm extraction dependency/gateway, fixture strategy, exact implementation file list, and any `pyproject.toml` change.
- Reviewer implementation-readiness must pass.
- User must explicitly approve implementation after source-of-truth reconciliation.
- Reviewer implementation gate, QA gate, and Integrator packaging/readiness must pass before completion.

## 16. Definition Of Ready

Ready for planned lane creation: yes.

Ready for Reviewer plan gate: yes.

Ready for approved implementation: yes, after the section 22 source-of-truth reconciliation. TASK_352 is implementation-authorized and pending Developer implementation within the reconciled dependency and scope boundaries.

## 17. Recommended Next Role

Developer implementation pass. Earlier planning-only recommendations are superseded by section 22 after Reviewer implementation-readiness re-gate and user approval.

## 18. Developer Planning-First Refinement - 2026-07-06

### 18.1 Authorization And Source-Of-Truth Note

The Developer planning-first pass is allowed by the Orchestrator/User delegation, which records Reviewer plan gate passed and User approval for Developer planning-first. Product implementation remains not authorized. The local board/task/planner files still contain planned or Reviewer-plan-gate wording in some places; this planning pass records the implementation-readiness strategy only and does not authorize code.

### 18.2 Current Code Facts Confirmed By Developer

- `ProjectTestPlanMatrixPreviewService.preview_from_path()` is currently `.docx` only and returns a deferred blocker for `.pdf`.
- `POST /api/test-plan/matrix-preview-from-upload` currently accepts `.doc,.docx`, creates a controlled preview PDF token, reads Word table locations, and delegates Matrix extraction to the application service.
- `WordDocumentSnapshot` and `WordTableLocation` already provide the shape TASK_352 needs: paragraphs, tables, global table index, page number, page-table index, nearby context, text preview, and row/column counts.
- `ProductSpecMatrixParser.parse_tables(...)` already consumes neutral `tables`, optional `paragraphs`, optional `selected_table_index`, and `table_contexts`; TASK_352 should not change parser rules.
- `frontend/src/api/client.ts` already has a generic upload helper with optional locator fields and a Matrix preview response with source format, candidate tables, selected page/table, groups, rows, blockers, and preview PDF token.
- `MatrixEditorWorkspace.tsx` already handles preview PDF iframe display, locator Reparse, TASK_350B stale Replace auto-Reparse, TASK_350C direct Import Matrix entry, Replace/Append, group selection, and commit. TASK_352 frontend work should be accept-list/copy/regression only.

### 18.3 Deterministic PDF Gateway Decision

Future implementation should add a new deterministic PDF source gateway under `backend/infrastructure/files/`, not under API routes and not inside the Matrix parser.

Recommended gateway:

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- Optional small model module only if needed to keep line counts under AGENTS limits, for example `backend/infrastructure/files/pdf_matrix_source_models.py`

Preferred dependency:

- Superseded by the dependency reconciliation in sections 19-21. Do not use `PyMuPDF` / MuPDF as the default TASK_352 product dependency.
- Use the permissive-license path selected by the user: `pdfplumber` as the primary table/text extraction dependency, with `pdfminer.six` as the underlying layout engine and direct fallback only if implementation proves `pdfplumber` APIs are insufficient.
- Add PDF extraction dependencies to `pyproject.toml` only after Reviewer implementation-readiness re-gate and later explicit implementation authorization.

Gateway contract:

- Input: trusted local temp PDF path supplied by the upload route/service.
- Output:
  - `paragraphs: list[str]`
  - `tables: list[list[list[str]]]`
  - table locations compatible with `WordTableLocation` fields: `table_index`, `page_number`, `page_table_index`, `preceding_paragraph`, `text_preview`, `row_count`, `column_count`
  - capability/failure metadata only through application-service blockers, not frontend-only interpretation.
- The gateway must not OCR, rasterize for interpretation, call AI, write to the source PDF, or create persistent source artifacts.

### 18.4 Backend Service And API Strategy

`ProjectTestPlanMatrixPreviewService` should accept an optional PDF gateway dependency and branch by suffix:

- `.docx`: unchanged Word path.
- `.doc`: unchanged TASK_350A conversion wrapper path.
- `.pdf`: call the PDF gateway, resolve selected table index using the existing page/table/keyword selector logic, then call `ProductSpecMatrixParser.parse_tables(...)` with the PDF tables and paragraphs.

For `.pdf` uploads, `routes_project_test_plan.py` should:

- accept `.pdf,.doc,.docx`;
- save the upload to a temporary path;
- create a controlled preview token that serves a copied temp PDF through the existing `/api/test-plan/matrix-preview-pdf/{token}` endpoint;
- call the application service with locator fields;
- preserve original uploaded file identity in `source_document_name` and `source_format=".pdf"`;
- clean temp upload and preview temp files using the existing token lifecycle pattern.

The route may copy the PDF for iframe serving, but it must not parse PDF content directly. Parsing remains in the gateway through the application service boundary.

### 18.5 Failure Modes And User-Facing Errors

Application/service blockers should be concise and business-readable:

- no extractable text: `This PDF has no extractable text. OCR is not supported in this version.`
- scanned/image-only PDF: same no-text blocker, with no OCR attempt.
- no tables extracted: `No text table was found in this PDF.`
- no Matrix table after parsing: reuse the existing `No Matrix table with test items, section, and Group columns was found.`
- selected page/table mismatch: reuse current locator mismatch behavior.
- extraction dependency unavailable/failure: `Cannot read this PDF for Matrix import on this workstation.`

No blocker should suggest AI/OCR/Excel fallback inside TASK_352.

### 18.6 Frontend Strategy

Future frontend implementation should:

- change the hidden Matrix import file input from `.doc,.docx` to `.pdf,.doc,.docx`;
- keep `previewProjectTestPlanMatrixFromUpload(...)` unchanged unless implementation proves DTO fields are missing;
- change Word-specific loading/help copy to neutral wording such as `ConnLab is reading the source document and preparing the preview.`;
- keep the existing import modal, iframe, locator fields, Reparse, stale Replace auto-Reparse, Replace/Append, group selection, and commit flow;
- show PDF-specific copy only when the backend returns a blocker.

No separate PDF page, card stack, parser UI, or frontend-side PDF parsing is allowed.

### 18.7 Exact Future May Touch

Backend:

- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `backend/infrastructure/files/pdf_matrix_source_models.py` only if needed for line-count control
- `backend/api/routes_project_test_plan.py`
- `backend/api/dependencies.py` only if dependency injection needs a factory change
- `pyproject.toml` only for the Reviewer/User-approved permissive PDF dependency path, expected `pdfplumber` / `pdfminer.six`; `pymupdf`, `pymupdf4llm`, and `pymupdfpro` remain locked out

Frontend:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if a typed contract gap is proven; current planning expects no client contract change

Tests:

- `tests/unit/test_pdf_matrix_source_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- existing focused parser/MatrixEditor tests as regressions

Docs/evidence:

- TASK_352 plan/evidence/board through normal lane flow only.

### 18.8 Must Not Touch / Locked For Implementation

- `ProductSpecMatrixParser` business rules, except read-only import or fixture regression checks.
- Backend schema/migrations.
- Confirmed Matrix authority, Fee Evaluation, Test Record, lifecycle, Workbench, Folder Actions, Intake/LTR, Projects registry/list.
- OCR/scanned-PDF engines, AI parsing, Excel Matrix import.
- Real user sample PDFs except read-only manual/QA smoke.
- Real public-drive, workbook, LTR workbook, project folder, `D:\Test Project/**`, or `D:\PublicProject/**` data.
- Release/settings/basic-information residual cleanup.
- `.agents/**`
- `docs/project_management/**`

### 18.9 Test And Fixture Strategy

Automated tests should not commit or mutate the user-provided PDFs. Use generated temporary PDF fixtures:

- A small text PDF with a drawn/text table that the PDF gateway can extract into rows/columns.
- A text PDF with multiple page-local tables to prove `page_number` plus `page_table_index` selects the requested table.
- A PDF with text but no Matrix-like table.
- A minimal image-only/no-text PDF or mocked no-text gateway result for the scanned-PDF blocker.

If generated table extraction is too brittle for API integration tests, split coverage:

- gateway unit tests exercise real deterministic extraction on generated PDFs;
- service/API tests use dependency overrides/fakes to prove `.pdf` routing, locator handling, preview token behavior, cleanup, and parser reuse.

Real sample validation remains a QA/manual smoke residual unless sanitized fixtures are explicitly approved.

### 18.10 Validation Commands For Future Implementation

Expected validation after implementation:

```powershell
py -m pytest tests/unit/test_pdf_matrix_source_gateway.py tests/integration/test_project_test_plan_preview_api.py -q
py -m pytest tests/unit/test_product_spec_matrix_parser.py -q
npm test -- MatrixEditorWorkspace --run
npm run build
py -m py_compile backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/infrastructure/files/pdf_matrix_source_gateway.py
git diff --check
```

Static scans:

- trailing whitespace scan on TASK_352 package files;
- forbidden-scope status for locked backend/frontend paths;
- scan proving no OCR/AI/Excel Matrix import code was introduced;
- no-real-file mutation scan for user PDF paths, public-drive/workbook paths, and project folder roots.

### 18.11 Implementation Readiness Decision

Developer planning recommends Reviewer implementation-readiness re-gate after the dependency update in section 21. `PyMuPDF` / MuPDF is no longer a TASK_352 dependency decision point under the current user-selected option. The remaining Reviewer decision is whether the `pdfplumber` / `pdfminer.six` implementation strategy, version pins, fixture strategy, and packaging checks are sufficient for later implementation authorization.

## 19. Planner Dependency/Prototype Decision Pass - 2026-07-06

### 19.1 Reviewer Blocker

Reviewer implementation-readiness blocked TASK_352 on B1: Developer planning-first proposed `pymupdf>=1.24,<2.0`, but the plan/evidence did not record a project/user decision for PyMuPDF/MuPDF AGPL compliance, commercial licensing, or a permissive-license alternative/prototype path.

Implementation remains not authorized. No product dependency may be added until this decision is resolved and the implementation plan is re-gated.

### 19.2 License Facts Checked

Planner checked current official/public package sources on 2026-07-06:

- PyPI lists `pymupdf` license metadata as `Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License` and describes it as built on MuPDF.
- PyMuPDF's product comparison states the AGPL option requires open-sourcing the application when distributed, while commercial licensing is for proprietary/commercial use without AGPL obligations.
- PyMuPDF/MuPDF capability fit remains strong for local text/table extraction, but licensing is not a neutral engineering choice in ConnLab's offline Windows packaging/distribution context.
- PyPI lists `pdfplumber` as MIT License and says it works best on machine-generated rather than scanned PDFs, with table extraction and visual debugging.
- PyPI lists `pdfminer.six` with MIT license expression; it is a pure-Python PDF parser/analyzer focused on extracting text/layout data and is the foundation for `pdfplumber`.
- PyPI lists `pypdf` as BSD-3-Clause, but its public package description emphasizes splitting/merging/cropping/transforming and text/metadata retrieval rather than table extraction, so it is more likely a support/utility candidate than the primary table gateway.

Sources recorded for Reviewer/User reference:

- `https://pypi.org/project/pymupdf/`
- `https://pymupdf.io/`
- `https://pypi.org/project/pdfplumber/`
- `https://pypi.org/project/pdfminer.six/`
- `https://pypi.org/project/pypdf/`

### 19.3 Planner Decision

Do not proceed with PyMuPDF as the default TASK_352 product dependency.

TASK_352 should stay `planned_blocked` until one of these paths is chosen:

1. Recommended permissive-license path: revise Developer planning-first to evaluate and use `pdfplumber` / `pdfminer.six` as the first product dependency candidate. This preserves the text-PDF/no-OCR/no-AI scope and avoids AGPL/commercial licensing blockers. It still requires Developer planning update, Reviewer implementation-readiness re-gate, and explicit user implementation approval before code.
2. PyMuPDF license-approved path: user/project explicitly approves either AGPL compliance obligations for ConnLab distribution or a commercial Artifex license. Only then may `pymupdf` return to May Touch for `pyproject.toml`.
3. Prototype-only dependency evaluation path: create a separate docs/prototype lane that tests PyMuPDF, pdfplumber/pdfminer.six, and possibly pypdf against generated fixtures and read-only local samples, without adding a product runtime dependency. The prototype reports extraction quality/licensing/packaging findings back to Planner/Reviewer.

Planner recommendation: choose option 1 unless the user specifically wants to buy/approve a PyMuPDF commercial license or perform a prototype bake-off first.

### 19.4 Source-Of-Truth Changes

- TASK_352 remains a valid planned PDF Matrix Import lane.
- TASK_352 is not implementation-ready.
- `pyproject.toml` is no longer May Touch for `pymupdf` by default. It may only be touched for:
  - a Reviewer/User-approved permissive PDF extraction dependency such as `pdfplumber` / `pdfminer.six`; or
  - an explicitly approved PyMuPDF AGPL/commercial license path.
- Developer must not add `pymupdf`, `pymupdf4llm`, `pymupdfpro`, OCR tooling, AI parsing, or scanned-PDF support under the current authorization.

### 19.5 Updated Next Role

Recommended next role: User dependency/license decision.

After user chooses option 1, 2, or 3, route either:

- Developer planning-first update + Reviewer readiness re-gate for option 1 or 2; or
- Planner prototype/dependency-evaluation lane creation for option 3.

## 20. Planner Dependency Decision Reconciliation - 2026-07-06

### 20.1 User Decision

User/Orchestrator approved option 1:

- Use the recommended permissive-license path with `pdfplumber` / `pdfminer.six`.
- PyMuPDF / MuPDF is not approved as the default TASK_352 product dependency.
- Product implementation remains not authorized until source-of-truth update, Developer planning update, Reviewer implementation-readiness re-gate, explicit user implementation approval, and implementation authorization reconciliation.

### 20.2 Updated Dependency Strategy

Developer planning update must replace the prior PyMuPDF-first strategy with a permissive-license text-PDF extraction strategy:

- Primary candidate: `pdfplumber`.
  - Current public package metadata checked by Planner on 2026-07-06 lists `pdfplumber` as MIT License.
  - The package description says it works best on machine-generated rather than scanned PDFs, matching TASK_352's text-PDF-only / no-OCR scope.
  - It exposes text characters, line/rectangle objects, page metadata, and table extraction helpers built on `pdfminer.six`, which appear aligned with the Word-like neutral snapshot design.
- Foundation/transitive candidate: `pdfminer.six`.
  - Current public package metadata checked by Planner on 2026-07-06 lists `pdfminer.six` as MIT license expression.
  - It is a pure-Python PDF parser/analyzer focused on extracting text and layout data; Developer must determine whether direct use is needed or whether `pdfplumber` is sufficient.
- Support candidate only if needed: `pypdf`.
  - Prior Planner check found BSD-3-Clause metadata, but it is not the primary table-extraction candidate.

### 20.3 Packaging / Implementation Planning Requirements

Developer planning update must document before Reviewer re-gate:

- exact proposed dependency version pins for `pdfplumber` and any direct `pdfminer.six` requirement;
- whether `pdfplumber` alone is enough or whether direct `pdfminer.six` access is needed;
- Windows offline packaging impact and transitive dependencies;
- generated-fixture approach for text tables, multi-page/page-table locators, no-text/scanned-style blockers, and no-Matrix-table blockers;
- whether the two user-confirmed sample locators remain QA/manual smoke only or can be represented by generated fixtures;
- how table extraction output maps into the existing Word-like neutral `tables`, `paragraphs`, and table-location metadata;
- how failures stay business-readable without adding OCR, AI, or parser-rule expansion.

### 20.4 Source-Of-Truth Decision

- Historical note superseded by section 22: TASK_352 returned from `planned_blocked` to `planned` for Developer planning update at this point in the lane history.
- Historical note superseded by section 22: implementation is now authorized after Developer planning update, Reviewer implementation-readiness re-gate, user approval, and source-of-truth reconciliation.
- `pyproject.toml` May Touch is limited to the permissive dependency path, expected `pdfplumber` / `pdfminer.six`, and only after Reviewer/User implementation authorization.
- `pymupdf`, `pymupdf4llm`, and `pymupdfpro` are locked out unless a later explicit AGPL/commercial license decision reopens that path.

### 20.5 Updated Next Role

Historical recommendation superseded by section 22: Developer planning update.

Historical note superseded by section 22: Developer completed the plan/evidence update, replacing PyMuPDF planning with the `pdfplumber` / `pdfminer.six` strategy, then stopped for Reviewer implementation-readiness re-gate.

## 21. Developer Planning Update - pdfplumber/pdfminer Strategy - 2026-07-06

### 21.1 Authorization And Scope

This update is planning/evidence only. It replaces the previous PyMuPDF-first planning language after the user selected the permissive-license option. Product implementation, dependency installation, and `pyproject.toml` edits remain unauthorized.

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`.

Allowed reason: Planner dependency reconciliation records TASK_352 as planned with dependency decision resolved for the permissive `pdfplumber` / `pdfminer.six` path and routes Developer planning update only.

### 21.2 Dependency Strategy

Future implementation should use:

- `pdfplumber>=0.11,<1.0` as the primary product dependency for deterministic text-PDF extraction.
- `pdfminer.six>=20240706,<20270000` only if direct lower-level layout access is required beyond the transitive dependency already supplied by `pdfplumber`.

Implementation should first try to keep `pdfminer.six` as a transitive dependency of `pdfplumber`. Add a direct `pdfminer.six` pin only if tests prove direct layout APIs are used by ConnLab code.

PyMuPDF / MuPDF policy:

- `pymupdf`, `pymupdf4llm`, and `pymupdfpro` are not approved for TASK_352.
- Do not add PyMuPDF imports, optional fallbacks, dependency declarations, docs-as-implementation guidance, or tests that require PyMuPDF.
- Reopening PyMuPDF requires a separate explicit AGPL/commercial license decision.

### 21.3 PDF Gateway Approach With pdfplumber

The PDF source gateway should stay under `backend/infrastructure/files/`, for example:

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `backend/infrastructure/files/pdf_matrix_source_models.py` only if needed to keep files below AGENTS line limits

Gateway extraction flow:

1. Open the trusted temporary PDF path with `pdfplumber.open(...)`.
2. Iterate pages in source order, preserving 1-based `page_number`.
3. Extract page text with `page.extract_text(...)` and split it into paragraph-like text blocks. These feed the existing parser as `paragraphs`.
4. Extract tables with `page.extract_tables(...)` or a narrowly configured table-settings wrapper. Each extracted table becomes `list[list[str]]` after cell cleanup.
5. Maintain `page_table_index` per PDF page and global 1-based `table_index` across the document.
6. Build Word-like location metadata: `table_index`, `page_number`, `page_table_index`, `preceding_paragraph`, `text_preview`, `row_count`, and `column_count`.
7. Return a neutral snapshot to the application service; do not parse Matrix semantics in the gateway.

The gateway may use `pdfplumber` character/line/rectangle objects to improve table-settings choices, but it must not introduce visual/OCR interpretation. If a page has text but no extractable table, return no table for that page and let service/parser blockers explain the result.

### 21.4 Backend Service/API Integration

`ProjectTestPlanMatrixPreviewService` should accept an optional PDF gateway dependency and branch by suffix:

- `.docx`: unchanged existing Word path.
- `.doc`: unchanged TASK_350A conversion path.
- `.pdf`: call the PDF gateway, resolve locator input with existing `_select_table_index(...)`, and call `ProductSpecMatrixParser.parse_tables(...)` with PDF `tables`, `paragraphs`, and table contexts.

`routes_project_test_plan.py` should:

- accept `.pdf,.doc,.docx` in upload validation;
- write uploads to caller-owned temp paths;
- for `.pdf`, copy the uploaded temp PDF into the existing preview-token directory and serve it through `/api/test-plan/matrix-preview-pdf/{token}`;
- preserve original filename/source format;
- never parse PDF business content directly in the route;
- clean temp upload paths in `finally`.

### 21.5 Failure Mapping

Business-readable blockers:

- no text: `This PDF has no extractable text. OCR is not supported in this version.`
- text but no tables: `No text table was found in this PDF.`
- no Matrix table after parser: reuse existing `No Matrix table with test items, section, and Group columns was found.`
- page/table mismatch: reuse existing locator mismatch behavior.
- pdfplumber/pdfminer extraction failure: `Cannot read this PDF for Matrix import on this workstation.`
- encrypted/password-protected PDF if encountered: `Cannot read this protected PDF for Matrix import.`

Do not suggest OCR, AI parsing, Excel import, or manual parser-rule changes in TASK_352 blockers.

### 21.6 Fixture And Test Strategy

Generated fixtures only:

- Use temporary generated PDFs in tests, not the user-provided sample files.
- Prefer `pdfplumber`-readable text/table fixtures generated by a small test helper using an existing or test-only PDF writer if available in the environment.
- If no PDF writer is already available, use checked-in minimal fixture bytes only if they are generated within the test suite or explicitly approved; otherwise use gateway fakes for API/service tests and leave real table extraction to gateway unit fixtures.

Coverage:

- text PDF with one Matrix-like table;
- multi-page PDF with multiple page-local tables proving `page_number` and `page_table_index` mapping;
- text PDF with no tables;
- no-text/image-only style blocker via generated minimal PDF or mocked gateway result;
- extraction failure mapping via fake gateway exception;
- `.docx` and `.doc` regression paths unchanged;
- TASK_350B stale Reparse/Replace frontend regression unchanged.

User sample PDFs remain read-only QA/manual smoke residuals:

- `GS-12-1507`, page 8, table 2.
- `PRODSPEC GS-12-1941`, page 11, table 2.

### 21.7 Updated Future May Touch

Backend:

- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `backend/infrastructure/files/pdf_matrix_source_models.py` only if needed for line-count control
- `backend/api/routes_project_test_plan.py`
- `backend/api/dependencies.py` only if dependency injection changes
- `pyproject.toml` only for `pdfplumber` and a direct `pdfminer.six` pin if Reviewer/User later authorize implementation

Frontend:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if a typed contract gap is proven

Tests:

- `tests/unit/test_pdf_matrix_source_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- Existing focused parser and MatrixEditorWorkspace tests as regressions

### 21.8 Updated Validation Planning

Future implementation validation:

```powershell
py -m pytest tests/unit/test_pdf_matrix_source_gateway.py tests/integration/test_project_test_plan_preview_api.py -q
py -m pytest tests/unit/test_product_spec_matrix_parser.py -q
npm test -- MatrixEditorWorkspace --run
npm run build
py -m py_compile backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/infrastructure/files/pdf_matrix_source_gateway.py
git diff --check
```

Additional static checks:

- dependency/license scan proving no `pymupdf`, `pymupdf4llm`, `pymupdfpro`, OCR, AI parsing, or Excel Matrix import dependency/code was added;
- package/status scan for `pdfplumber` / direct `pdfminer.six` only after implementation authorization;
- trailing whitespace scan;
- forbidden-scope status scan;
- no-real-file mutation scan for user PDFs, public-drive/workbook paths, and project folder roots.

### 21.9 Updated Recommendation

Recommended next role: Reviewer implementation-readiness re-gate.

Reviewer should evaluate:

- `pdfplumber>=0.11,<1.0` as the primary dependency;
- whether direct `pdfminer.six` pinning is needed or should remain transitive;
- Windows/offline packaging impact;
- fixture strategy and table locator mapping;
- preserved no-OCR/no-AI/no-parser-rule-expansion scope.

## 22. Planner Implementation Authorization Reconciliation - 2026-07-06

Status: implementation authorized - pending Developer implementation.

This section reconciles repository source-of-truth after the permissive dependency planning update and Reviewer implementation-readiness re-gate.

Fact chain recorded:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Dependency decision was reconciled to the permissive path.
- Developer planning update completed.
- Reviewer implementation-readiness re-gate passed.
- User approved TASK_352 reconciliation and Developer implementation.

Authorized implementation scope:

- Add deterministic text-PDF Matrix import support for Matrix Editor Import Matrix.
- Add a backend PDF source gateway that extracts text-PDF content into Word-like tables, paragraphs, page/table locator facts, and table context metadata.
- Reuse existing `ProductSpecMatrixParser`, Matrix preview API, PDF preview iframe, locator/Reparse, TASK_350B stale Replace behavior, Replace/Append, group selection, and commit flow.
- Preserve TASK_350A `.doc/.docx` behavior and TASK_350C import-entry behavior.

Dependency source-of-truth:

- `pdfplumber>=0.11,<1.0` is the primary approved dependency.
- Direct `pdfminer.six>=20240706,<20270000` is allowed only if implementation proves lower-level layout API usage is necessary.
- PyMuPDF / MuPDF packages (`pymupdf`, `pymupdf4llm`, `pymupdfpro`) remain locked out for TASK_352 unless a later explicit AGPL/commercial decision reopens them.

Locked scope remains:

- V1 text-PDF only.
- No OCR.
- No scanned PDF support.
- No AI parsing.
- No Excel Matrix import.
- No Matrix parser rule expansion unless a separate approved parser lane exists.
- No storage schema changes unless separately justified and approved.
- No Confirmed Matrix, Fee, Test Record, or lifecycle semantic changes.
- API routes and frontend must not parse PDF business content directly.
- No real user sample mutation.
- No Workbench, Folder Actions, Intake, Projects, release, or settings cleanup.
- No `.agents/**` or `docs/project_management/**` changes.

Next legal role:

- Developer implementation pass.
- Completion still requires Developer evidence, Reviewer implementation gate, QA gate, and Integrator packaging/readiness.

## 23. Integrator Closeout - 2026-07-06

Status: complete - Integrator accepted.

Accepted scope:

- `pdfplumber>=0.11,<1.0` was added as the approved permissive text-PDF extraction dependency.
- `backend/infrastructure/files/pdf_matrix_source_gateway.py` owns deterministic text-PDF extraction and maps PDF tables/text into the Word-like neutral snapshot used by the existing parser path.
- `backend/application/project_test_plan_matrix_preview_service.py` and `backend/api/routes_project_test_plan.py` now route `.pdf` uploads through the same preview, locator, and parser path as Word imports.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` accepts `.pdf,.doc,.docx` while keeping the existing import modal, preview iframe, locator/Reparse, Replace/Append, group selection, and commit flow.

Validation accepted:

- Backend focused gateway/service/API/parser suite passed: 34 tests.
- Frontend MatrixEditorWorkspace suite passed: 1 file / 38 tests.
- `npm run build` passed with the existing Vite chunk-size warning only.
- `py_compile` passed for TASK_352 backend modules/routes.
- Line-count, diff, trailing whitespace, dependency/static, no-real-file mutation, and forbidden-scope checks passed.
- QA read-only real-sample smoke passed for all four user PDFs, including the two B1 accepted locator samples.

Residual:

- Direct browser click/upload smoke remained a non-blocking tooling residual because browser launch was unavailable in QA. Route-level upload smoke with real PDFs and focused frontend tests passed.

Remote push was intentionally not performed.
