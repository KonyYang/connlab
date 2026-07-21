# TASK_366C Planner Discovery Evidence

## Lane

- TASK_ID: `TASK_366C_IMPORT_MATRIX_REPLACE_METHOD_AUTHORITY_SYNC`
- Lane: `import-matrix-replace-method-authority-sync`
- Role: Planner
- Status: Developer implementation complete / Reviewer pass / QA pass / pending Integrator packaging-readiness
- Product implementation: authorized, implemented, reviewed, and QA-passed within the frozen TASK_366C boundaries

## Current Phase / Active Task / Why Allowed

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task after this reconciliation: `TASK_366C_IMPORT_MATRIX_REPLACE_METHOD_AUTHORITY_SYNC`.
- Why allowed: Reviewer B1/B2 plan re-gate passed, User approved Developer planning-first, Developer docs-only planning-first is complete, Planner resolved Reviewer B3/B4 governance blockers, Reviewer implementation-readiness re-gate passed, the user explicitly approved TASK_366C product implementation, Developer implementation plus the approved test-only fixture fix are complete, Reviewer passed, and QA passed. Planner may reconcile the post-QA package source-of-truth and route only to Integrator packaging/readiness.

## User Confirmed

- Import Matrix Replace should write imported data into editable Matrix draft and synchronize authoritative Method revisions in the same Replace flow.
- No separate Method sync Preview/Apply should be required after Replace.
- Reuse TASK_366B catalog parsing/matching/signature/CAS/audit concepts.
- Only unique safe EIA-364 / 364-xx matches auto-update.
- Preserve Method family display and update revision token, not whole catalog text.
- Replace must define transaction order, fingerprints, TOCTOU, and no-silent-wrong-write policy.
- Replace success must show updated Method in Matrix Editor immediately.
- Confirm Matrix remains the only confirmed Matrix publication.
- Standard record files are read-only.

## Repository Evidence

- `backend/application/matrix_import_commit_service.py`
  - `MatrixImportCommitService.commit()` validates payload, selected groups, source commit fingerprint, existing import reuse, source lineage persistence, selected-only draft build, and draft snapshot creation.
  - `_build_selected_only_draft(...)` maps preview Method values into `ProjectMatrixDraftRow.method`.
- `backend/api/routes_matrix_import_commit.py`
  - `POST /api/projects/{project_id}/matrix-import/commit` returns `MatrixImportCommitResponse` with full `project_matrix_draft`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - `commitImportedPreview(...)` calls `commitMatrixImport(...)`, applies `response.project_matrix_draft`, clears draft/session markers, sets saved state, and closes the import dialog.
  - `applyImportedMatrixDirectly()` reparses stale locator preview before calling the same commit path.
- `backend/application/matrix_method_version_sync_service.py`
  - Provides accepted TASK_366B catalog read, effective worksheet, draft signature, proposal, fingerprint, apply, and audit behavior.
- `backend/modules/test_plan/standard_method_version_parser.py`
  - Owns EIA-364 core extraction, catalog row parsing, candidate resolution, proposal status, and display-preserving Method update text.
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
  - Existing `method_sync_context_json` supports Method sync audit context; `apply_method_sync(...)` proves method-only row CAS is already modeled for saved drafts.

## Reviewer B1/B2 Fix Decision

Reviewer blocked the initial plan because it allowed source-import persistence before Standard catalog authority validation and because the legacy TASK_261 reuse path could early-return before current catalog/source fingerprint checks.

Planner fixes the contract as follows:

- TASK_366C Replace has one application-level atomic boundary: import payload validation, selected source facts, current Standard resource/path/effective sheet/catalog read, method proposals, source/root/row fingerprints, stale/reuse checks, and proposal/result fingerprints must all complete before any source lineage, draft, or method audit/context write.
- Source-level authority failure is zero-write across source import, source snapshot, draft, and method audit/context state.
- After preflight succeeds, source import lineage, source snapshot, transformed editable draft, and import-mode method authority context must be written in one transaction. Any conflict rolls back the whole transaction and returns typed `409`.
- TASK_261 fingerprint reuse alone is forbidden. Reuse requires current Standard source context, catalog fingerprint, proposal/result fingerprint, pre/post Method fingerprints, source import identity, selected group fingerprint, and persisted import-mode context version to match exactly.
- Resource/path/sheet/catalog/proposal/result/context mismatch, missing context, or stale context returns typed `409` no-write. TASK_366C does not authorize creating a second source import under the same legacy fingerprint.

## Planner Decision

Keep `TASK_366C` as implemented/reviewed/QA-passed and route the current checkpoint to Integrator packaging/readiness. The approved implementation integrates Method authority sync into the backend Import Matrix commit path and keeps frontend changes limited to consuming the returned draft and optional summary metadata.

Route only to Integrator packaging/readiness after this reconciliation.

## Frozen Contract

- Source-level catalog availability and worksheet validity are preconditions for authoritative Replace sync. Failure is typed zero-write across source import, source snapshot, draft, and method audit/context state.
- Row-level unsafe statuses do not modify that row and must be reported.
- Safe row updates use TASK_366B proposal output and preserve original Method family formatting.
- Replace persists source lineage, source snapshot, one editable draft snapshot, and import-mode method sync context only after all authority preflight checks pass and within one rollback-capable transaction.
- Existing source-import/draft reuse is allowed only when the stored import-mode context exactly matches the current request's source, selected groups, Standard resource/path/sheet, catalog, proposal/result, and pre/post Method fingerprints.
- Existing Confirm Matrix publication boundary remains unchanged.
- `.xls` / `.xlsx` Standard record sources remain read-only.

## Authorized May Touch

- `backend/application/source_matrix_import_persistence_service.py`: mechanical source persistence delegation only.
- `backend/application/source_matrix_import_builder.py`: new bounded pure source aggregate/preflight builder.
- `backend/application/matrix_import_commit_service.py`: orchestration, strict replay, transaction/read-verify, response assembly.
- `backend/application/matrix_import_draft_builder.py`: new bounded selected-only draft builder.
- `backend/application/matrix_import_method_authority.py`: new bounded single-read Standard authority/proposal/context helper.
- `backend/api/routes_matrix_import_commit.py`: bounded response/error mapping.
- `backend/api/dependencies.py`: exact `get_matrix_import_commit_service` provider/transaction hunk only.
- `frontend/src/api/client.ts`: contiguous response DTO additions only.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: exact Replace status summary consumption only.
- Tests: fixture-only `tests/unit/test_matrix_import_commit_service.py`; new `tests/unit/test_matrix_import_method_authority.py`; new `tests/integration/test_matrix_import_method_authority_commit_api.py`; focused Matrix Editor Replace regression; existing source-persistence and TASK_366B suites read-only.
- Test-only fixture reconciliation: `tests/integration/test_matrix_import_group_selection_commit_api.py` may receive only the minimal fixture/setup hunk for `test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input` to seed disposable Standard resource/catalog authority. The original `201` created/reused assertions, no-authority no-fallback contract, and all other nodes remain unchanged.
- TASK_366C governance docs/evidence/board.

Read-only dependencies: `backend/application/matrix_method_version_sync_service.py`, `backend/application/external_excel_read_service.py`, `backend/modules/test_plan/standard_method_version_parser.py`, source/draft repositories, Matrix session/Confirm services, and accepted TASK_366B focused suites.

## Must Not Touch / Locked Paths

- No product/test/schema/database/frontend/API implementation during Planner reconciliation pass.
- No confirmed Matrix direct writes.
- No Generic Test Record, TASK_360B specialized workbook, Fee, LTR, Report, project lifecycle, or output generation changes.
- No Standard record write/save/convert and no real DB/public-drive/attachment/source-workbook access.
- No TASK_366B saved-draft Preview/Apply behavior/context change.
- No source/draft repository behavior change and no new database uniqueness claim.
- No business assertion change and no other-node edit in `tests/integration/test_matrix_import_group_selection_commit_api.py`; no real DB/public-drive/attachment/source-workbook access.
- No external dirty residual absorption.
- `.agents/**`, `docs/project_management/**`, remote push.

## Line-Count Facts

- Current UTF-8 physical-line count command: `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`, counting blanks.
- Current facts: `backend/application/source_matrix_import_persistence_service.py` = `480`; `backend/application/matrix_import_commit_service.py` = `409`.
- Prior `536` / `465` figures are superseded historical notes only.
- Source persistence is close to the 500-line hard limit, so future implementation must first perform narrow mechanical extraction/delegation and keep all final/new Python files and tests below 500 without using blank-line suppression as the limit strategy.

## Validation Draft

- Backend unit: safe Method revision update; current/no-op; no core; multiple cores; no match; ambiguous match; downgrade; invalid catalog; source-level blocker.
- API: Replace commit returns draft with updated Method values and sync summary.
- API: source-level blocker leaves source-import count, source-snapshot count, draft count, and method-audit/context count unchanged.
- API: repeated same preview/selected groups with same current Standard catalog/context reuses deterministically without duplicate writes.
- API: same legacy TASK_261 fingerprint with changed Standard path, changed worksheet, changed catalog, missing/stale context, or divergent proposal/result returns typed `409` no-write.
- API: persistence conflict rolls back source lineage, draft, and audit/context writes.
- Frontend: Replace applies returned draft and shows updated Method without separate Method sync Apply.
- Regression: TASK_366B saved-draft Preview/Apply still works; Confirm Matrix remains separate.
- Fixture-scope regression: the locked legacy integration success/reuse node may be updated only by seeding disposable Standard authority in fixture/setup; it must not restore a no-authority fallback.

## Definition Of Ready

Satisfied for Integrator packaging/readiness. Product implementation and the approved test-only fixture/setup hunk are complete, Reviewer passed, and QA passed. The earlier fixture-scope pending checkpoint is superseded.

Blocking questions: none.

## Board Update

The board is updated to record `TASK_366B` as complete/accepted at HEAD `18df3f34ce0f3bbac8c714b38f9b8aa747d100d7` and `TASK_366C` as Developer implementation complete / Reviewer pass / QA pass / pending Integrator packaging-readiness. QA validation recorded disposable backend/API/replay `28 passed`, `MatrixEditorWorkspace` `44` tests passed, frontend build and candidate `py_compile` passed, diff/trailing/staging/data clean except existing LF/CRLF notices, safe EIA-364 updates in the returned editable draft and aria-live summary, authority/replay changes and persistence failure typed zero-write, Confirm Matrix as the only publication step, and the only workbook save under pytest `tmp_path`. Browser tooling residual remains non-blocking because no disposable live Matrix route exists and in-app Browser local-file fixture navigation was rejected.
