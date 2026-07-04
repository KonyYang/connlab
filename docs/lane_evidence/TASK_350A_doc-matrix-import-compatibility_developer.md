# TASK_350A Developer Evidence - Doc Matrix Import Compatibility

Status: fix pass complete - pending Reviewer implementation re-gate

Task: `TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY`
Lane: `doc-matrix-import-compatibility`
Role: Developer
Date: 2026-07-04

---

## 1. Gate And Scope

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Allowed reason:

- Planner evidence, Developer planning evidence, and reconciliation evidence record TASK_350A as implementation authorized / pending Developer implementation.
- Scope is limited to `.doc` compatibility for Matrix import preview by converting legacy `.doc` uploads through the Office facade / Word gateway into temporary `.docx`, then reusing the accepted `.docx` Matrix preview, parser, PDF, page/table selection, and commit flow.

Locked scope preserved:

- No database schema or migration changes.
- No Matrix parser business rule changes.
- No Confirmed Matrix authority, Fee Evaluation, Test Record, lifecycle, Workbench, Projects registry, Intake/LTR, Folder Actions, Settings/LTR, release/packaging, `.agents/**`, or `docs/project_management/**` changes from this implementation pass.
- No `frontend/src/api/client.ts` change was needed.
- No real user document or workbook mutation was performed.

---

## 2. Sources Read

Governance and source of truth:

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY.md`
- `docs/task_350a_doc_matrix_import_compatibility_plan.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_planner.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_reconciliation_planner.md`

Implementation context:

- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_word_document_gateway.py`

---

## 3. Changed Files

TASK_350A implementation package:

- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_word_document_gateway.py`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`

Same-file isolation note:

- Reviewer B1 found that `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` still carried broader locator / reparse / commit-flow residuals in the TASK_350A candidate package.
- Developer fix pass isolated the file so the TASK_350A candidate diff now contains only the approved Matrix import file selector accept-list change from `.docx` to `.doc,.docx`.

External residuals excluded:

- Existing `frontend/src/api/client.ts`, `backend/application/ltr_duplicate_resolution_service.py`, Settings/LTR, New Project / intake / precheck, release/packaging, `dist_release/`, `packaging/`, release scripts, and `temp_agents_stash.md` residuals remain outside this package.

---

## 4. Implementation Summary

Backend:

- Added `WordDocumentGateway.convert_legacy_doc_to_docx(source_path, output_path)`.
- Added `OfficeFacade.convert_legacy_doc_to_docx(...)`.
- Added public application-service wrappers for legacy `.doc` conversion, table-location read, and preview PDF export so the API route does not directly reach into `service._office`.
- Updated `POST /api/test-plan/matrix-preview-from-upload` to accept `.doc` and `.docx`.
- `.docx` continues through the existing upload preview path.
- `.doc` upload writes the original bytes to a temporary `.doc`, converts it to a temporary `.docx` through the service/facade/gateway boundary, then feeds the converted `.docx` into the existing Matrix preview flow.
- Temp uploaded `.doc`, converted `.docx`, and preview PDF paths are tracked and unlinked in `finally` on success and failure.
- Conversion failure maps to a concise business-readable `400` response: legacy `.doc` conversion requires Microsoft Word on the workstation.
- Returned preview metadata preserves the original uploaded `.doc` identity with `source_document_name` and `source_format=".doc"` and does not expose the converted temp `.docx` path.

Frontend:

- Matrix Editor import selector now allows `.doc,.docx`.
- Existing upload helper and `.docx` Matrix Editor behavior remain unchanged.

Tests:

- Added integration coverage for `.doc` upload conversion, metadata preservation, cleanup, and readable conversion failure.
- Added Word gateway unit coverage for caller-provided `.docx` output and extension validation.
- Added Matrix Editor coverage that the import selector accepts `.doc,.docx`.

---

## 5. Validation Results

Fresh validation commands run in this implementation pass:

- `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py -q`
  - Result: passed, `13 passed in 4.15s`.
- `npm test -- MatrixEditorWorkspace --run`
  - Result: passed, `1 passed`, `30 passed`.
- `py -m compileall backend/api/routes_project_test_plan.py backend/application/project_test_plan_matrix_preview_service.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/word_document_gateway.py`
  - Result: passed.
- `npm run build`
  - Result: passed. Existing Vite chunk-size warning remains.
- `git diff --check -- backend/api/routes_project_test_plan.py backend/application/project_test_plan_matrix_preview_service.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/word_document_gateway.py frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`
  - Result: passed; Git reported existing LF/CRLF warnings only.
- Trailing whitespace scan on TASK_350A package files
  - Result: no matches.
- `Select-String` scan for `service._office` in `backend/api/routes_project_test_plan.py`
  - Result: no matches.
- Static scan confirmed TASK_350A hooks for `convert_legacy_doc_to_docx`, `temp_paths`, and frontend `accept=".doc,.docx"` are present.
- Targeted forbidden-scope status showed external residuals in API client, duplicate-resolution service, release/packaging folders, and temp stash remain visible but excluded from TASK_350A.

---

## 5A. Reviewer B1 Fix Pass

Reviewer B1:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` candidate diff included unapproved Matrix import locator / stale reparse / commit-flow changes beyond TASK_350A `.doc,.docx` compatibility.

Fix:

- Removed the non-TASK_350A MatrixEditorWorkspace candidate hunks from the working diff.
- Preserved the approved frontend TASK_350A change: the hidden Matrix import input now accepts `.doc,.docx`.
- Backend `.doc` conversion implementation was not changed during this fix pass.

Post-fix candidate proof:

- `git diff -- frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` now shows only:
  - `accept=".docx"` changed to `accept=".doc,.docx"`.
- Candidate dependency/scope scan found no `ImportLocatorSnapshot`, `lastParsedLocator`, `buildLocatorSnapshot`, `fetchImportPreview`, or `committingImport` locator-control residuals in the MatrixEditorWorkspace diff.

Fresh validation after B1 fix:

- `npm test -- MatrixEditorWorkspace --run`
  - Result: passed, `1 passed`, `30 passed`.
- `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py -q`
  - Result: passed, `13 passed in 4.05s`.
- `py -m compileall backend/api/routes_project_test_plan.py backend/application/project_test_plan_matrix_preview_service.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/word_document_gateway.py`
  - Result: passed.
- `npm run build`
  - Result: passed. Existing Vite chunk-size warning remains.
- `git diff --check` on TASK_350A package files
  - Result: passed with Git LF/CRLF warnings only.
- Trailing whitespace scan on TASK_350A package files
  - Result: no matches.
- Targeted forbidden-scope status still shows external `frontend/src/api/client.ts`, duplicate-resolution, release/packaging, and temp-stash residuals; these remain excluded from TASK_350A.

Manual smoke:

- A real Word COM `.doc` smoke was not run in this Developer thread because no safe disposable real `.doc` fixture / Word COM smoke harness was established here. Mocked gateway and API tests cover conversion handoff, cleanup, metadata, and failure mapping. QA should run a real `.doc` smoke if Microsoft Word and a disposable fixture are available.

---

## 6. Risks And Follow-Ups

- Real `.doc` conversion depends on Microsoft Word / pywin32 availability on the workstation. API failure is now business-readable, but QA should validate the happy path on a Word-enabled machine.
- The Matrix parser remains `.docx`-based by design; TASK_350A intentionally adds only a compatibility wrapper for legacy `.doc`.
- Pre-existing MatrixEditorWorkspace residuals should be reviewed as their own package context and not attributed wholesale to TASK_350A.

---

## 7. Stop Point

Developer implementation and Reviewer B1 fix pass are complete and stopped at Reviewer implementation re-gate.

Recommended next role:

- Reviewer implementation re-gate.

Blocking summary:

- None for Developer implementation re-gate. Real Word COM smoke remains a QA residual.

---

## 8. Integrator Packaging Closeout

Date: 2026-07-04

Integrator gate: accepted.

Accepted package:

- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_word_document_gateway.py`
- TASK_350A task/plan/planner/developer/QA/reconciliation evidence docs
- `docs/task_board.md` TASK_350A closeout

Packaging notes:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` was accepted only for the `accept=".docx"` to `accept=".doc,.docx"` hunk.
- No Matrix import locator, stale reparse, or commit-flow residual hunks were packaged.
- External API-client/New Project/LTR duplicate/release/packaging/temp-stash/Settings/LTR/Basic Information residuals, `.agents/**`, `docs/project_management/**`, real user docs, Workbench, Projects, public folder, parser-rule, direct PDF parsing, Confirmed Matrix, Fee, Test Record, and lifecycle semantic changes were excluded.

Integrator validation:

- `py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py -q`: passed, `13 passed`.
- `npm test -- MatrixEditorWorkspace --run`: passed, `30 passed`.
- `py -m compileall backend/api/routes_project_test_plan.py backend/application/project_test_plan_matrix_preview_service.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/word_document_gateway.py`: passed.
- `npm run build`: passed with the existing Vite chunk-size warning only.
- `git diff --cached --check`: passed with LF/CRLF warnings only.
- Staged whitelist/forbidden-path, trailing whitespace, no-real-doc, direct-PDF/parser/future-scope, and MatrixEditorWorkspace accept-only scans passed.

Residual:

- Real Microsoft Word COM `.doc` happy-path smoke remains non-blocking because no verified disposable `.doc` fixture/harness was available in QA. Mocked API/gateway tests cover conversion handoff, temp cleanup, original `.doc` metadata, readable conversion failure, and `.docx` regression.
