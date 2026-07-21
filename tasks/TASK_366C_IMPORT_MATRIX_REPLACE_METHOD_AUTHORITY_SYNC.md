# TASK_366C_IMPORT_MATRIX_REPLACE_METHOD_AUTHORITY_SYNC

## Status

Reviewer plan re-gate passed. User approved Developer planning-first; Developer docs-only planning-first is complete. Planner B3/B4 docs-only fix is complete. Reviewer implementation-readiness re-gate passed. User explicitly approved product implementation. Developer implementation and the approved test-only fixture fix are complete. Reviewer passed the implementation and fixture gates, QA passed, and Integrator accepted the isolated local package. The earlier locked-fixture checkpoint is superseded and closed. Remote push was intentionally not performed.

## Current Phase / Role / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: `TASK_366C_IMPORT_MATRIX_REPLACE_METHOD_AUTHORITY_SYNC`.
- Role: Integrator accepted closeout.
- Why allowed: Developer implementation and the approved tests-only fixture fix are complete, Reviewer passed, QA passed, and the controlled package passed the Integrator merge gate. This closeout does not activate another product lane.

## User Goal

When a user imports a Matrix, selects a specification, completes parsing, and clicks `Replace`, ConnLab should write the imported information into the editable Matrix draft and, within the same Replace workflow, synchronize recognizable EIA-364 / 364-xx Method revisions from the Settings Standard record Excel plus effective Sheet authority. After Replace completes, the Matrix Editor Method column should already display the authoritative revision. Users should not need to run a separate Method sync Preview/Apply step for this imported draft.

## Confirmed By User

- Reuse the accepted `TASK_366B` Standard record catalog parsing, matching, saved signature, CAS, and audit concepts. Do not copy or fork the rules.
- Auto-update only rows whose Method contains a recognizable EIA-364 / 364-xx core and whose Standard record match is uniquely safe.
- Preserve the Matrix Method business family and update only the authority revision token. Do not blindly replace the Matrix Method with the full catalog row text.
- Replace must be transactional and must define source fingerprint, row identity, catalog fingerprint, and TOCTOU boundaries.
- Missing matches, ambiguous matches, downgrade conflicts, source unavailability, and invalid Sheet must be explicit. Silent wrong writes are forbidden.
- Replace success must reload or apply the returned draft so Matrix Editor immediately shows the authoritative Method.
- Only editable Matrix draft is mutated. Existing Confirm Matrix remains the only confirmed publication action.
- Standard record `.xls` / `.xlsx` sources are always read-only. No write, conversion, save-as, or real public file mutation.

## Repository Evidence

- `backend/application/matrix_import_commit_service.py` currently commits Import Matrix previews through `MatrixImportCommitService.commit()`. It persists source lineage, builds a selected-only `ProjectMatrixDraftSnapshot`, and calls `draft_store.create_snapshot(...)`.
- `_build_selected_only_draft(...)` maps preview row detail into `ProjectMatrixDraftRow.method`, including values from `method`, `method_summary`, or `reference_standard`.
- Existing import idempotency reuses an existing source-import/draft pair when `compute_task261_fingerprint(...)` matches. Reviewer B2 found this early-return would bypass TASK_366C's current Standard record source/sheet/catalog authority validation unless the reuse contract is changed.
- `backend/api/routes_matrix_import_commit.py` exposes `POST /api/projects/{project_id}/matrix-import/commit` and returns the full `project_matrix_draft`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` calls `commitMatrixImport(...)` from `commitImportedPreview(...)`, then applies `response.project_matrix_draft` directly into the editor state.
- The frontend stale-preview path reparses the selected locator before commit, then calls the same commit function.
- `backend/application/matrix_method_version_sync_service.py` from TASK_366B already centralizes Standard record catalog reading, effective worksheet name, saved draft signature validation, parser use, preview fingerprints, selected apply, audit context, and method-only root/row CAS.
- `backend/modules/test_plan/standard_method_version_parser.py` already extracts Matrix cores with `364-\d{2}`, parses Standard catalog entries such as `ANSI/EIA-364-04B-2015`, resolves deterministic safe candidates, and builds proposals that preserve the original method family.
- `backend/infrastructure/storage/repositories/project_matrix_draft.py` has `apply_method_sync(...)` for method-only CAS and `replace_snapshot(...)` / `create_snapshot(...)` style aggregate persistence. TASK_366C must choose a self-contained Replace integration rather than silently running a second user workflow.

## Planner Inference

- The smallest product shape is a backend-side import-commit integration: validate all imported payload facts and current Standard catalog authority before any source lineage, draft, or audit write; build the selected-only draft snapshot in memory; run the accepted TASK_366B catalog resolver against its in-memory rows; transform safe Method values; then persist source lineage, draft, and import-mode method-sync context in one explicit transaction.
- For newly imported drafts, root/row CAS differs from TASK_366B's saved-draft apply. TASK_366C should bind the operation to the source-import fingerprint, selected group set, in-memory row identity, catalog fingerprint, worksheet identity, and transformed target fingerprint.
- Source-level failures such as missing Standard record configuration, unreadable catalog, invalid Sheet, or malformed catalog header should block Replace with a typed no-write error, because the requested workflow requires consulting that authority during Replace.
- Row-level no-core/no-match/ambiguous/downgrade statuses should not silently write. Safe rows may update; unsafe rows remain imported as-is and must be reported in a bounded import-method-sync summary.
- No database schema is expected because `ProjectMatrixDraftRecord.method_sync_context_json` already exists from TASK_366B. If implementation proves the current audit context cannot represent import-mode sync without loss, Developer must stop and route back to Planner before adding schema.

## Contract

### Data Authority Chain

1. Import Matrix preview supplies source rows, selected groups, and raw Method values.
2. Settings Standard record resource plus effective worksheet name supplies the Method revision authority.
3. TASK_366B parser/resolver supplies EIA-364 core extraction, catalog candidate resolution, proposal status, and display-format preservation.
4. Replace writes only an editable Matrix draft.
5. Confirm Matrix remains the only confirmed Matrix publication action.

### Replace Application Atomic Boundary And TOCTOU

- Normalize and validate preview payload and selected groups as today.
- Compute canonical imported payload fingerprint, selected-group fingerprint, and source-row/root fingerprints before mutation.
- Build selected source facts and the selected-only draft candidate in memory before mutation. If the implementation cannot build the required candidate without first writing source lineage, it must introduce an explicitly scoped application unit-of-work that rolls back source import, source snapshot, draft, and audit writes on every authority error; this requires Reviewer/User approval before implementation.
- Resolve the current Standard resource, canonical path, effective worksheet, catalog rows, catalog fingerprint, proposal summary, pre-transform Method fingerprint, and post-transform Method fingerprint before any source lineage, draft, or audit write.
- All source-level authority failures are typed zero-write: no source-import row, no source snapshot, no draft, and no method-sync audit/context write.
- Only after the full preflight succeeds may the implementation open one transaction and write source import lineage, source snapshot, editable draft snapshot, method authority result/context, and response audit facts.
- Transaction write order must be deterministic: source import lineage and snapshot, then editable draft aggregate with already-transformed Method values, then import-mode method-sync context/audit attached to the same draft record, then commit.
- If source import uniqueness, draft uniqueness, stale context, or persistence conflict occurs during the transaction, roll back all writes and return typed `409`.
- The response must be built from the committed draft snapshot; Matrix Editor reload/apply consumes that returned draft and shows the authoritative Method values immediately.

### TASK_261 Source-Import Reuse Policy

- The current early return on TASK_261 payload/selected-group fingerprint alone is forbidden for TASK_366C.
- A matching source-import fingerprint may be reused only after the current request repeats the full no-write preflight and the existing draft's import-mode method-sync context exactly matches:
  - source import identity;
  - canonical imported payload fingerprint;
  - selected group fingerprint;
  - Standard resource identity and canonical path;
  - effective worksheet name;
  - catalog fingerprint;
  - pre-transform row/root Method fingerprint;
  - proposal/result fingerprint;
  - post-transform Method fingerprint;
  - context schema/version.
- If any resource, path, worksheet, catalog, proposal/result, row/root fingerprint, or context version is missing or different, the old draft must not be returned.
- TASK_366C does not authorize silently creating a second source import with the same legacy TASK_261 fingerprint. The mismatch result is typed `409` conflict/no-write unless a future separately reviewed plan authorizes a distinct persistence identity.
- Same-payload/current-catalog reuse must not duplicate source import, source snapshot, draft, or audit records.

### Row Status Policy

- `update_available` and `revision_missing` with one uniquely safe catalog candidate: update Method.
- `current`: leave Method unchanged and report current.
- `no_method_core`, `multiple_method_cores`, `catalog_no_match`, `catalog_ambiguous`, `downgrade_conflict`, malformed Method, or missing row identity: leave Method unchanged and report a row status.
- The Replace response should expose a concise summary or metadata sufficient for frontend/operator review without introducing a new standalone Preview/Apply workflow.

### Display Format

- Preserve the original Method family text and replace or insert only the revision token adjacent to the recognized `364-xx` core.
- Do not replace Matrix Method with the full Standard catalog text, file name, title, or year unless TASK_366B parser already defines that exact safe formatting rule.
- Existing TASK_366B parser behavior is the source of truth for revision token extraction and display proposal construction.

### Frontend Behavior

- The Replace button remains the entry point.
- After a successful commit, Matrix Editor uses the returned `project_matrix_draft` and immediately shows the authoritative Method values.
- A separate Method sync panel may remain available for saved editable drafts, but TASK_366C must not require it for imported Replace completion.
- UI copy should stay calm, operational, and inline with the Matrix Editor workflow. No modal-first redesign is planned.

## Authorized May Touch (Implementation)

- `backend/application/source_matrix_import_persistence_service.py`: product hunk limited to mechanical delegation from existing persistence flow to a prepared-source builder and `prepare_from_preview(...)` / `persist_prepared(...)` boundaries. No behavior change outside TASK_366C import commit preparation.
- `backend/application/source_matrix_import_builder.py`: new bounded product module for pure Source Matrix aggregate construction, zero-write preparation, stable IDs/facts, and compatibility with existing source persistence behavior.
- `backend/application/matrix_import_commit_service.py`: product hunk limited to orchestration, strict replay, transaction entry, and response assembly.
- `backend/application/matrix_import_draft_builder.py`: new bounded product module for selected-only editable draft construction from the prepared source aggregate.
- `backend/application/matrix_import_method_authority.py`: new bounded product module for single-read Standard authority resolution, TASK_366B parser/proposal reuse, transformed draft, typed summary, and import-mode context/fingerprints.
- `backend/api/routes_matrix_import_commit.py`: bounded response DTO and error mapping only.
- `backend/api/dependencies.py`: exact `get_matrix_import_commit_service` provider/transaction dependency hunk only.
- `frontend/src/api/client.ts`: contiguous commit response DTO additions only.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: exact Replace success/status summary consumption only.
- Tests: fixture-only adaptation in `tests/unit/test_matrix_import_commit_service.py`; new bounded `tests/unit/test_matrix_import_method_authority.py`; new bounded `tests/integration/test_matrix_import_method_authority_commit_api.py`; focused Matrix Editor Replace regression in the existing Matrix Editor test file; existing source-persistence and TASK_366B tests read-only regression execution only.
- Test-only fixture reconciliation: `tests/integration/test_matrix_import_group_selection_commit_api.py` may receive only the minimal fixture/setup hunk needed to seed disposable Standard resource/catalog authority for `test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input`. This authorization is test-only, must not alter the business assertions, must not weaken the no-authority typed `422`/atomic zero-write contract, must not touch other nodes in the file, and must use disposable temp-file/fake-catalog strategy only.
- TASK_366C task/plan/Planner/Developer/Reviewer/reconciliation evidence and board governance docs.

Explicit read-only dependencies, not May Touch:

- `backend/application/matrix_method_version_sync_service.py`
- `backend/application/external_excel_read_service.py`
- `backend/modules/test_plan/standard_method_version_parser.py`
- `backend/infrastructure/storage/repositories/source_matrix_import.py`
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
- Matrix session/Confirm services and accepted TASK_366B focused suites.

## Must Not Touch

- Product code, tests, schema, database, frontend, or API client in this Planner reconciliation pass.
- Confirmed Matrix direct mutation.
- Generic Test Record, TASK_360B specialized workbook output, Fee, LTR, project lifecycle, Report, Matrix parser/import extraction rules outside the Replace commit integration.
- Standard record workbook write/save/convert behavior.
- Real DB, public-drive files, user attachments, or source workbooks.
- No TASK_366B saved-draft Preview/Apply behavior/context change.
- No source/draft repository behavior change and no new database uniqueness claim.
- No change to the original business assertions in `tests/integration/test_matrix_import_group_selection_commit_api.py`; only the one Standard authority fixture/setup hunk is allowed after Reviewer re-gate.
- External dirty residuals.
- `.agents/**`, `docs/project_management/**`, remote push.

## Line-Count Gate

- Current UTF-8 physical-line count command: `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`, counting blanks.
- Current facts: `backend/application/source_matrix_import_persistence_service.py` = `480`; `backend/application/matrix_import_commit_service.py` = `409`.
- Superseded historical counts from earlier Developer notes: `536` / `465`; those are not current package facts.
- Because source persistence is already close to the 500-line hard limit, TASK_366C must first do a narrow mechanical extraction/delegation before adding behavior. The final source persistence service, commit service, and every new Python module/test must remain below 500 physical lines. Blank-line deletion or formatting churn may not be used as the primary way to pass the limit.

## Validation Gate Draft

- Unit: import draft rows with safe EIA-364 catalog candidates update Method via TASK_366B proposal builder.
- Unit: no-core, multiple-core, no-match, ambiguous, downgrade, malformed catalog, and invalid Sheet statuses do not silently write.
- Unit/API: source-level authority unavailable or invalid Sheet returns typed no-write and does not create a draft.
- Unit/API: missing Standard resource, unreadable workbook, invalid worksheet, malformed catalog, and catalog read exception leave source-import count, source-snapshot count, draft count, and method-audit/context count unchanged.
- API: successful Replace returns a draft whose Method column values already include authoritative revision tokens and includes a bounded sync summary.
- API: idempotent same preview/fingerprint reuse is allowed only when current Standard source context, catalog fingerprint, proposal/result fingerprint, post-transform fingerprint, and persisted import-mode context all match; it must not duplicate source imports, source snapshots, drafts, or audits.
- API: same import payload with changed Standard path, worksheet, catalog revision, missing import-mode context, stale context version, or divergent proposal/result returns typed `409` no-write.
- API: transaction rollback proves no partial source lineage, draft, or audit writes after persistence conflict.
- Frontend: clicking Replace applies the returned draft and displays updated Methods without a separate Method sync Apply action.
- Regression: Confirm Matrix remains the only publication step; Standard record sources are read-only; existing TASK_366B Preview/Apply still works for saved drafts.
- Regression fixture fix: `tests/integration/test_matrix_import_group_selection_commit_api.py::test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input` must keep its original `201` created/reused assertions, but the fixture must provide a disposable Standard resource/catalog authority so the success path is tested under the approved full-preflight contract. The same suite must still prove missing/invalid authority paths return typed no-write in TASK_366C-specific tests.
- Verification commands draft: focused pytest for import commit/method sync/API; focused MatrixEditorWorkspace test; `py -m py_compile` for touched backend modules; `npm test -- MatrixEditorWorkspace --run`; `npm run build`; diff/trailing/status/no-real-file scans.

## Definition Of Ready / Authorization

DoR, implementation authorization, Developer implementation, Reviewer gate, QA gate, and Integrator packaging gate are satisfied. The lane is complete/accepted:

- User goal and upstream accepted baselines are explicit.
- Repository evidence identifies the actual Replace path and TASK_366B reuse points.
- May Touch, Must Not Touch, transaction boundaries, row statuses, display policy, validation, and package isolation are frozen for review.
- Product implementation remained strictly within the Authorized May Touch and Must Not Touch boundaries above; the only reconciled fixture scope was the test-only legacy fixture/setup hunk.
- Reviewer plan re-gate passed; User approved Developer planning-first; Developer docs-only planning-first is complete; Planner B3/B4 docs-only fix is complete; Reviewer implementation-readiness re-gate passed; User explicitly approved product implementation; Developer implementation and tests-only fixture fix are complete; Reviewer passed; QA passed.
- QA validation recorded disposable backend/API/replay `28 passed`, `MatrixEditorWorkspace` `44` tests passed, frontend build and candidate `py_compile` passed, diff/trailing/staging/data clean except existing LF/CRLF notices, safe EIA-364 updates in returned editable draft and aria-live summary, authority/replay changes and persistence failure typed zero-write, Confirm Matrix as the only publication step, and the only workbook save under pytest `tmp_path`.
- Integrator staged only the frozen TASK_366C candidate whitelist/hunks, preserved hunk isolation in mixed files, excluded all external residuals, and performed no real DB/public-drive/attachment/source-workbook access. The local accepted commit is recorded in Integrator evidence; remote push was not performed.

Blocking questions: none. Next legal role: User/Orchestrator; no product lane is activated by this closeout.
