# TASK_350A QA Evidence - Doc Matrix Import Compatibility

Date: 2026-07-04

Role: QA / Smoke Owner

Task: `TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY`

Lane: `doc-matrix-import-compatibility`

Result: `qa_pass`

---

## 1. Gate And Role Boundary

- Current phase from `docs/task_board.md`: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Orchestrator delegation states Reviewer re-gate passed and QA gate is required.
- Local `docs/task_board.md` still describes TASK_350A as implementation authorized / pending Developer implementation; QA records this as a board timing mismatch against the newer Orchestrator delegation and did not update the board.
- QA performed validation and evidence only.
- QA did not modify product source, tests, backend/API implementation, frontend implementation, `docs/task_board.md`, real user documents, public-drive folders, release/packaging residuals, or temp-stash files.
- QA did not stage, commit, push, package, or run destructive cleanup.

## 2. Sources Read

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/task_board.md`
- `tasks/TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY.md`
- `docs/task_350a_doc_matrix_import_compatibility_plan.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_planner.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_reconciliation_planner.md`
- Actual status/diff for TASK_350A candidate files and visible external residuals.

## 3. Candidate Package / Scope Check

TASK_350A candidate implementation files observed:

- `backend/api/routes_project_test_plan.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tests/integration/test_project_test_plan_preview_api.py`
- `tests/unit/test_word_document_gateway.py`
- `docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md`

Observed implementation facts:

- Upload route accepts `.doc` and `.docx`.
- `.docx` remains the direct preview path.
- `.doc` writes upload bytes to a request-scoped temp `.doc`, converts through `ProjectTestPlanMatrixPreviewService.convert_legacy_doc_to_docx(...)` / `OfficeFacade.convert_legacy_doc_to_docx(...)` / `WordDocumentGateway.convert_legacy_doc_to_docx(...)`, then feeds the converted temp `.docx` into existing table-location, PDF preview, and Matrix preview parsing.
- Converted `.doc` responses preserve original uploaded identity with `source_document_name` and `source_format=".doc"` and do not expose the converted temp `.docx` path.
- Temp uploaded `.doc` and converted `.docx` paths are tracked in `temp_paths` and unlinked on success/failure.
- Conversion failure maps to business-readable HTTP 400 text requiring Microsoft Word on the workstation.
- API route no longer reaches `service._office` directly for upload table-location/PDF preview work.
- Frontend Matrix import selector diff is isolated to `accept=".doc,.docx"`.

Reviewer B1 isolation check:

```powershell
git diff -U4 -- frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx
```

Observed result:

- The diff only changes the hidden file input from `accept=".docx"` to `accept=".doc,.docx"`.
- No Matrix import locator, reparse, commit-flow, Confirm Matrix, Fee, Test Record, or broader Matrix Editor residual hunks are part of the TASK_350A candidate diff.

External residuals still visible and excluded:

- `frontend/src/api/client.ts`
- `backend/application/ltr_duplicate_resolution_service.py`
- New Project / Intake / Precheck residuals
- release/packaging/desktop residuals, `dist_release/`, `packaging/`, and `temp_agents_stash.md`

## 4. Backend Focused Tests

Command:

```powershell
py -m pytest tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py -q
```

Observed result:

- Passed.
- `13 passed in 2.22s`.

Coverage confirmed:

- `.docx` preview API regression remains covered by existing integration tests.
- `.doc` upload conversion calls the gateway/facade path.
- `.doc` metadata is preserved as original `.doc` identity.
- Converted temp `.docx` path is not exposed.
- Temp source/converted files are removed.
- Conversion failure returns readable HTTP 400 and does not invoke preview parsing.
- Word gateway validates `.doc` input and `.docx` output extensions.

## 5. Frontend Focused Tests

Command:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace --run
```

Observed result:

- Passed.
- `1` test file passed.
- `30` tests passed.

Coverage confirmed:

- Matrix import selector accepts `.doc,.docx`.
- Existing Matrix import UI, locator controls, group selection, Replace/Append, and adjacent Matrix Editor behaviors remain green in the focused suite.

## 6. Compile / Build

Command:

```powershell
py -m compileall backend/api/routes_project_test_plan.py backend/application/project_test_plan_matrix_preview_service.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/word_document_gateway.py
```

Observed result:

- Passed with no output.

Command:

```powershell
cd frontend
npm run build
```

Observed result:

- Passed.
- Existing Vite chunk-size warning only.

## 7. Static Checks

Candidate diff check:

```powershell
git diff --check -- backend/api/routes_project_test_plan.py backend/application/project_test_plan_matrix_preview_service.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/word_document_gateway.py frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_developer.md docs/task_350a_doc_matrix_import_compatibility_plan.md tasks/TASK_350A_DOC_MATRIX_IMPORT_COMPATIBILITY.md docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_planner.md docs/lane_evidence/TASK_350A_doc-matrix-import-compatibility_reconciliation_planner.md
```

Observed result:

- Passed with LF/CRLF warnings only.

Trailing whitespace scan:

```powershell
Select-String -Path <TASK_350A candidate files/docs> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result:

- No matches.

Forbidden-scope/status check:

```powershell
git status --short -- backend/api/routes_project_test_plan.py backend/application/project_test_plan_matrix_preview_service.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/word_document_gateway.py frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx tests/integration/test_project_test_plan_preview_api.py tests/unit/test_word_document_gateway.py frontend/src/api/client.ts backend/modules/test_plan/product_spec_matrix_parser.py backend/infrastructure/storage backend/application/public_folder_sync_service.py backend/application/public_folder_submit_service.py backend/application/public_folder_pull_service.py backend/application/ltr_duplicate_resolution_service.py frontend/src/features/new-project frontend/src/features/project-workbench frontend/src/pages/ProjectListPage.tsx .agents docs/project_management dist_release packaging temp_agents_stash.md
```

Observed result:

- TASK_350A candidate files are dirty as expected.
- `backend/modules/test_plan/product_spec_matrix_parser.py`, storage/schema paths, public folder workflow files, Project Workbench, ProjectListPage, `.agents/**`, and `docs/project_management/**` did not appear as TASK_350A changes.
- External API-client/New Project/LTR duplicate/release/packaging/temp-stash residuals remain visible and excluded from TASK_350A.

Static scan:

```powershell
Select-String -Path backend/api/routes_project_test_plan.py,backend/application/project_test_plan_matrix_preview_service.py,backend/infrastructure/office/office_facade.py,backend/infrastructure/office/word_document_gateway.py,frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx -Pattern 'service\._office|product_spec_matrix_parser|Confirmed Matrix|Fee Evaluation|public_folder|ltr_duplicate|D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|temp_paths|unlink\(|convert_legacy_doc_to_docx|accept="\.doc,\.docx"|Only \.doc and \.docx are supported' -Encoding UTF8
```

Observed result:

- Positive TASK_350A hooks found: `convert_legacy_doc_to_docx`, `temp_paths`, `unlink(...)`, `.doc/.docx` support, and `accept=".doc,.docx"`.
- No `service._office` match in the upload route.
- No real `D:\Test Project` / `D:\PublicProject` paths in TASK_350A production files.
- MatrixEditorWorkspace still contains existing Test Record preview text outside the TASK_350A candidate diff; QA classifies this as pre-existing Matrix Editor scope, not TASK_350A change.
- `backend/application/project_test_plan_matrix_preview_service.py` still contains the existing unsupported `.pdf` blocker helper; TASK_350A does not add direct PDF parsing.

## 8. Real `.doc` Smoke

Real Microsoft Word COM `.doc` browser/API smoke was not executed.

Reason:

- QA did not have a verified disposable legacy `.doc` fixture and Word COM smoke harness for this thread.
- The task forbids using real user documents.

Disposition:

- Non-blocking residual for TASK_350A because mocked API/gateway tests verify `.doc` conversion handoff, temp cleanup, original `.doc` metadata preservation, readable conversion failure, and `.docx` regression behavior.
- A future manual smoke can be run on a Word-enabled workstation using a disposable `.doc` fixture.

## 9. QA Decision

QA gate: pass.

Blocking findings: none.

Residual risks:

- Real Microsoft Word COM `.doc` happy-path smoke remains a manual verification residual because no safe disposable `.doc` fixture/harness was available.
- External API-client/New Project/LTR duplicate/release/packaging/temp-stash residuals remain dirty and must not be staged or packaged with TASK_350A.

Recommended next role:

- Integrator packaging/readiness.

Integrator instruction:

- Stage/package only the TASK_350A candidate files/hunks listed in this evidence and Developer evidence.
- Exclude external API-client/New Project/LTR duplicate/release/packaging/temp-stash residuals.
- Confirm `MatrixEditorWorkspace.tsx` package hunk remains only the `.doc,.docx` accept-list change.
