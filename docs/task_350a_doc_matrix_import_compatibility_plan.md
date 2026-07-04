# TASK_350A Doc Matrix Import Compatibility Plan

Status: complete - Integrator accepted
Task: `TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY`
Lane: `doc-matrix-import-compatibility`
Created: 2026-07-04

## 1. Discovery Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: `TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY` / `doc-matrix-import-compatibility`, Planner Discovery / formal lane planning only.

Current role: ConnLab Planner.

Why allowed: user routed Planner Discovery Gate for a new Matrix import compatibility lane and explicitly prohibited product-code implementation or Developer routing.

## 2. User Goal

Matrix Editor `Import Matrix` should allow operators to choose legacy Word `.doc` specification files. The implementation direction is compatibility-only: convert `.doc` through Microsoft Word COM into a temporary `.docx`, then reuse the existing `.docx` Matrix preview, PDF preview, page/table locator, group selection, and commit workflow. Existing `.docx` import must remain unchanged.

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_word_document_gateway.py`
- Current `git status --short`
- Filename search for `TASK_349A_DOCX_MATRIX_PARSER_BUGFIX`, `TASK_350A`, `DOCX`, `MATRIX`, and `PARSER` task/evidence files.

## 4. Confirmed By User

- `.docx` existing import flow must not break.
- `.doc` is only a compatibility input format.
- `.doc` must be opened/read through backend Word COM / Office gateway, not from the API route body or frontend directly.
- Converted files must be temporary and cleaned after processing.
- Word COM missing, document open failure, or conversion failure must return business-readable errors.
- PDF direct parsing is out of scope.
- Matrix parser rules are locked unless a separate parser bugfix dependency is explicitly approved.
- Matrix business lifecycle, Confirmed Matrix, Fee, and Test Record semantics are out of scope.

## 5. Confirmed By Repository Evidence

- The current Matrix Editor hidden file input accepts only `.docx`.
- The current upload endpoint rejects non-`.docx` suffixes with `Only .docx is supported.`
- The current upload route already writes uploaded `.docx` content to a temp file, generates a Word PDF preview, reads table locations, and passes the temp `.docx` into `ProjectTestPlanMatrixPreviewService.preview_from_path`.
- `ProjectTestPlanMatrixPreviewService.preview_from_path` only supports `.docx`.
- The service already returns a specific deferred blocker for `.doc`: `Legacy .doc product specifications require a Word COM conversion/read gateway in a later task.`
- `OfficeFacade` is the existing Office gateway boundary.
- `WordDocumentGateway` already contains Word COM automation helpers and closes documents / quits Word in finally blocks for existing table-location and PDF export paths.
- No current formal task/evidence file named `TASK_349A_DOCX_MATRIX_PARSER_BUGFIX` or similarly active parser-bugfix source was found by filename search. Existing parser-related tasks are historical/completed Matrix import hardening tasks.
- Current worktree has unrelated dirty residuals, including `frontend/src/api/client.ts` and `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`; this Planner pass must not alter those product files.

## 6. Planner Inferences

- TASK_350A can be independent from parser bugfix work if it preserves the parser as a `.docx` consumer and treats conversion as a pre-processing compatibility step.
- The safest implementation shape is to add a narrow Office gateway conversion method and keep upload orchestration responsible for temp lifecycle.
- The implementation may not need a frontend API client type change because upload remains multipart file preview; the likely frontend change is file input accept/copy and tests.
- The backend should avoid exposing temp converted paths as operator-facing document identity; responses should preserve the original uploaded file name and concise compatibility metadata where feasible.

## 7. Not Yet Confirmed

- Whether the implementation should expose `source_format: ".doc"` in the preview response for converted sources or keep the current internal `.docx` source format. This does not block a planned lane; Reviewer can require the least disruptive contract during plan gate.
- Whether the Developer machine / QA machine has Microsoft Word COM available for real `.doc` smoke. This does not block mocked automated tests; it should be recorded as an optional manual smoke residual if unavailable.

## 8. Definition Of Ready

DoR is satisfied for a planned lane and Reviewer plan gate:

- User scenario is clear.
- Current `.docx` route/service/frontend behavior has been checked from code.
- Existing Office gateway boundary is identified.
- Dependencies and non-goals are explicit.
- May Touch, Must Not Touch, Locked Paths, evidence, validation gate, and merge gate are concrete.
- Acceptance is testable with mocked gateway tests plus existing `.docx` regressions.

DoR is not an implementation approval. TASK_350A remains `planned` until Reviewer plan gate, Developer planning-first, Reviewer implementation-readiness, user approval, and source-of-truth reconciliation happen through normal lane flow.

## 9. Recommended API / Service Design

Backend shape:

- Add a narrow Office gateway operation such as `OfficeFacade.convert_legacy_doc_to_docx(source_path: Path, output_path: Path) -> Path`.
- Implement conversion in `WordDocumentGateway` using Word COM:
  - require source suffix `.doc`;
  - open read-only and hidden;
  - disable alerts;
  - save as `.docx` to a caller-provided temp path;
  - close the document without saving source changes;
  - quit Word and uninitialize COM in `finally`;
  - raise `OfficeAutomationUnavailable` or a clear gateway exception when pywin32/Word/open/save fails.
- Update `POST /api/test-plan/matrix-preview-from-upload` to accept `.doc` and `.docx`.
- For `.docx`, keep the existing path.
- For `.doc`, write the uploaded `.doc` into a temp file, convert into a separate temp `.docx`, and pass only the converted `.docx` to current table-location, PDF export, and preview parsing calls.
- Track every temp path created by the request and unlink it in `finally`.
- Convert Word COM failures into a business-readable HTTP error such as `Cannot convert legacy .doc for Matrix import. Microsoft Word is required on this workstation.`
- Preserve the existing preview PDF token behavior.

Frontend shape:

- Change Matrix import file input acceptance from `.docx` to `.doc,.docx`.
- Keep `previewProjectTestPlanMatrixFromUpload` as the upload helper unless a Reviewer-approved response type adjustment is needed.
- Keep UI copy concise and operational; do not add a new long explanation panel.
- Existing import modal, PDF preview, locator fields, Replace/Append, group selection, and commit UI must remain unchanged.

Parser boundary:

- Do not modify Matrix parser rules.
- Do not parse `.doc` directly.
- The parser must still receive `.docx` snapshots through `OfficeFacade.read_word_document`.

## 10. May Touch

- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py` only if needed for `.doc` deferred blocker removal or metadata consistency.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts` only if type changes are necessary; default is locked unless implementation proves a typed response/request update is required.
- `tests/unit/test_word_document_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_350A task, plan, evidence, and board files through normal lane flow.

## 11. Must Not Touch

- Database schema/migrations.
- Matrix parser business rules unless a separate approved parser dependency is created.
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.
- Folder Actions / public folder workflow.
- Intake / LTR workflow.
- Workbench lifecycle / Projects registry behavior.
- Real user documents outside controlled temp or fixture paths.
- `.agents/**`, `docs/project_management/**`, release/packaging residuals, Basic Information residuals, Settings/LTR residuals, or unrelated dirty files.

## 12. Locked Paths

- `backend/infrastructure/storage/**`
- `backend/modules/test_plan/product_spec_matrix_parser.py` unless Reviewer explicitly approves a parser dependency.
- `backend/application/public_folder_*`
- `backend/application/*ltr*`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `.agents/**`
- `docs/project_management/**`
- Real user document folders outside temporary test fixtures.

## 13. Validation Gate

Backend:

- Focused API tests prove `.docx` upload still follows existing behavior.
- Focused API tests prove `.doc` upload calls conversion gateway, then returns Matrix preview through the existing `.docx` preview service.
- Conversion failure and Word COM unavailable cases map to readable HTTP errors.
- Temp `.doc` and converted `.docx` cleanup is covered on success and failure.
- `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py -q` or narrower focused equivalents pass.

Frontend:

- Matrix Editor file input accepts `.doc,.docx`.
- `.doc` file selection still calls `previewProjectTestPlanMatrixFromUpload`.
- Existing import modal, locator controls, Replace/Append, and group-selection tests remain green.
- `npm test -- --run MatrixEditorWorkspace --watch=false` passes.
- `npm run build` passes, or unrelated pre-existing build blockers are documented.

Manual / environment:

- If Windows + Microsoft Word is available, perform a disposable `.doc` smoke against Matrix import.
- If Word COM is unavailable, record the manual smoke residual and rely on mocked conversion tests for automation.

## 14. Merge Gate

- Reviewer plan gate passes this planned lane.
- Developer planning-first updates implementation detail and evidence without coding beyond approved scope.
- Reviewer implementation-readiness passes.
- User explicitly approves implementation.
- Planner/source-of-truth reconciliation marks implementation authorized.
- Developer implementation stays within May Touch and updates Developer evidence.
- Reviewer implementation gate verifies parser and Matrix authority semantics are unchanged.
- QA verifies `.docx` regression, `.doc` compatibility, failure handling, and temp cleanup.
- Integrator packages only TASK_350A-scoped files and excludes current external residuals.

## 15. Blockers

None for planned lane creation.

Potential implementation-time residuals:

- Real Word COM smoke depends on local Microsoft Word availability.
- If converted `.docx` exposes an existing parser bug, stop and route a separate parser bugfix lane instead of expanding TASK_350A by default.

## 16. Developer Planning-First Addendum

Date: 2026-07-04

Developer planning-first authorization:

- Orchestrator delegated TASK_350A Developer planning-first after Reviewer plan gate pass and user approval.
- Local `docs/task_board.md`, task file, plan header before this addendum, and Planner evidence still recorded TASK_350A as planned / ready for Reviewer plan gate only.
- No implementation should start until Planner/Orchestrator reconciles source-of-truth to record Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness, and explicit implementation approval.

### Current Code Confirmation

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` uses a hidden file input with `accept=".docx"`.
- `frontend/src/api/client.ts` already uses multipart `FormData` for `previewProjectTestPlanMatrixFromUpload`; no default typed client change is needed just to upload `.doc`.
- `backend/api/routes_project_test_plan.py` currently rejects uploads whose suffix is not `.docx`, then writes one temp `.docx`, reads table locations, exports the PDF preview, and calls `ProjectTestPlanMatrixPreviewService.preview_from_path`.
- `ProjectTestPlanMatrixPreviewService.preview_from_path` keeps the parser as a `.docx` consumer and returns a deferred blocker for `.doc`.
- `OfficeFacade` is the correct application-facing Office boundary. `WordDocumentGateway` already owns Word COM sessions for table locations and PDF export and is the right place for conversion.
- Existing route code currently reaches `service._office` for table locations and PDF preview. TASK_350A implementation should avoid increasing this leakage; if feasible, move upload-source preparation into the application service while keeping route logic thin.

### Exact Future Implementation File List

Implementation May Touch should be limited to:

- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/__init__.py` only if new public conversion result/error types must be exported
- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tests/unit/test_word_document_gateway.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- TASK_350A plan/evidence docs through normal lane flow

Keep `frontend/src/api/client.ts` locked by default. Touch it only if implementation proves a response/request type update is unavoidable, and record the reason in Developer evidence before review.

### Conversion Service Design

Add a narrow legacy conversion method at the Office boundary:

- `WordDocumentGateway.convert_legacy_doc_to_docx(source_path: Path, output_path: Path) -> Path`
- `OfficeFacade.convert_legacy_doc_to_docx(source_path: Path, output_path: Path) -> Path`

Conversion contract:

- Accept only `.doc` source paths and `.docx` output paths.
- Require the source file to exist.
- Use Word COM / `ApplicationFormWordSession`-style lifecycle discipline or equivalent direct COM lifecycle:
  - initialize COM where needed;
  - open hidden/read-only;
  - disable alerts;
  - do not add to recent files;
  - save/copy as `.docx` to the caller-provided temp output;
  - close the source with no source save;
  - quit Word and uninitialize COM in `finally`.
- Return only the converted temp `.docx` path to backend code, never to frontend/operators.
- Convert `pywin32` missing, Word unavailable, open failure, save failure, and output missing into business-readable route errors.

### Upload Flow Design

For `.docx`:

- Keep the current route/service behavior as a regression path.
- Existing PDF preview token, table locator fields, Replace/Append, group selection, and commit flow remain unchanged.

For `.doc`:

- Accept suffix `.doc` in `POST /api/test-plan/matrix-preview-from-upload`.
- Write the uploaded original `.doc` bytes to a request-scoped temp file.
- Convert that temp `.doc` to a separate temp `.docx` using the Office gateway.
- Feed only the converted `.docx` into the existing `.docx` table-location, PDF-preview, and Matrix parser flow.
- Track both temp files and unlink them in `finally` on success and failure.
- If conversion fails, do not call the Matrix parser and do not leave temp files behind.

### Source Metadata Decision

For converted `.doc` uploads, preserve the original uploaded identity:

- `source_document_name`: original uploaded `.doc` filename.
- `source_format`: `.doc`.
- `source_document_path`: do not expose the converted temp `.docx` path. Use the original upload identity/display path already available to the route, or a stable non-temp upload label if the current API cannot represent a real client path.
- `preview_pdf_token`: may still point to a generated PDF preview from the converted `.docx`.

Do not add raw temp paths, conversion tokens, COM details, or backend stack wording to frontend-visible payloads.

### Frontend Plan

- Change the hidden Matrix import file input from `.docx` to `.doc,.docx`.
- Keep the same `previewProjectTestPlanMatrixFromUpload` helper and same import modal semantics.
- Do not add new Matrix parser options, PDF direct parsing controls, or new operator workflow steps.
- Add focused test coverage that the file input accepts `.doc,.docx` and `.doc` selection still calls the existing upload helper.

### Test Plan Refinement

Backend focused tests:

- `.docx` upload regression still returns a Matrix preview through the existing path.
- `.doc` upload writes temp `.doc`, calls `OfficeFacade.convert_legacy_doc_to_docx`, parses the returned temp `.docx`, and returns original `.doc` metadata without exposing converted temp path.
- Conversion failure maps to a business-readable `400` or appropriate client-safe error and does not call parser/PDF/table-location flow after failure.
- Temp `.doc` and converted `.docx` files are cleaned on success and failure.
- `preview_from_path` `.doc` local-path deferred blocker may remain for local path preview unless implementation explicitly adds local `.doc` conversion; TASK_350A is primarily upload compatibility.

Frontend focused tests:

- Matrix Editor import input has `accept=".doc,.docx"`.
- Selecting `legacy-spec.doc` calls `previewProjectTestPlanMatrixFromUpload(file, projectId, locator?)`.
- Existing `.docx` import modal, locator, Replace/Append, and group-selection tests remain green.

Suggested validation commands for implementation:

- `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py -q`
- `npm test -- MatrixEditorWorkspace --run`
- `npm run build`
- `git diff --check` on TASK_350A package files
- trailing whitespace scan on TASK_350A package files
- targeted forbidden-scope status proving no parser rules, storage schema, confirmed Matrix, Fee, Test Record, lifecycle, Workbench, Projects, Intake/LTR, release, `.agents`, or `docs/project_management` changes

Manual smoke:

- If Microsoft Word is available, use a disposable `.doc` fixture and verify Matrix import reaches the existing preview modal and can select/commit the converted preview path.
- If Word COM is unavailable, record the smoke as a QA residual; mocked gateway tests remain required.

## 17. Planner Source-Of-Truth Reconciliation

Date: 2026-07-04

Reconciliation facts recorded from Orchestrator/User routing context and repository evidence:

- Reviewer plan gate passed.
- User approved TASK_350A Developer planning-first.
- Developer planning-first completed in `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`.
- Reviewer implementation-readiness gate passed.
- User approved TASK_350A source-of-truth reconciliation and Developer implementation.

Source-of-truth decision:

- TASK_350A is now implementation authorized / pending Developer implementation.
- TASK_350A is not complete.
- Future implementation remains limited to `.doc` compatibility wrapper behavior: convert legacy `.doc` via `OfficeFacade` / `WordDocumentGateway` into temporary `.docx`, clean temp files, and reuse the existing `.docx` Matrix preview/parser/PDF/page-table/group-selection/commit flow.

Scope locks remain unchanged:

- No Matrix parser rule changes.
- No PDF direct parsing.
- No Confirmed Matrix, Fee, Test Record, lifecycle semantic changes.
- No Folder Actions, Intake/LTR workflow, release/settings cleanup, `.agents/**`, or `docs/project_management/**`.
- No unrelated backend/frontend/tests/API-client residual cleanup.

## 18. Integrator Closeout

Date: 2026-07-04

Outcome:

- Integrator gate: accepted.
- Reviewer implementation re-gate: pass.
- QA gate: pass.
- Package readiness validated with focused backend tests (`13 passed`), MatrixEditorWorkspace frontend tests (`30 passed`), compileall, frontend build, staged diff check, staged whitelist/forbidden-path checks, trailing whitespace scan, and static no-real-doc/no-forbidden-scope scans.
- The accepted package preserves `.docx` behavior and adds `.doc` only as a compatibility wrapper through Office facade / Word gateway conversion into temporary `.docx`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` package hunk is limited to the input accept-list change from `.docx` to `.doc,.docx`.
- No Matrix parser rule changes, direct PDF parsing, Confirmed Matrix/Fee/Test Record/lifecycle semantic changes, Folder/Intake/LTR/release/settings cleanup, `.agents/**`, `docs/project_management/**`, or unrelated residuals were packaged.
- Real Microsoft Word COM `.doc` happy-path smoke remains a non-blocking manual residual because QA lacked a verified disposable `.doc` fixture/harness; mocked API/gateway coverage verified conversion handoff, cleanup, metadata, failure mapping, and `.docx` regression.
- Remote push was intentionally not performed.
