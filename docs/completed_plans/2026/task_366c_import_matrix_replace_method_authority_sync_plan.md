# TASK_366C Import Matrix Replace Method Authority Sync Plan

## Current Phase / Active Task / Role / Why Allowed

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: `TASK_366C_IMPORT_MATRIX_REPLACE_METHOD_AUTHORITY_SYNC`.
- Role: Integrator accepted closeout.
- Why allowed: Reviewer B1/B2 plan re-gate passed, the user approved Developer
  planning-first, Developer docs-only planning-first is complete, Planner has
  resolved Reviewer B3/B4 governance blockers, Reviewer implementation-readiness
  re-gate passed, and the user explicitly approved TASK_366C product implementation.
  Developer implementation and the approved test-only fixture fix are complete,
  Reviewer passed, QA passed, and the controlled local package passed the Integrator
  merge gate. This closeout marks the earlier fixture-scope pending state as superseded
  and does not activate another product lane.

## Goal Restatement

Import Matrix Replace should no longer require a separate Method sync Preview/Apply step. During Replace, ConnLab should commit the selected imported Matrix into an editable Matrix draft and automatically synchronize safe EIA-364 / 364-xx Method revision updates from the Settings Standard record Excel plus effective Sheet authority. Matrix Editor should display the authoritative Method immediately after Replace returns.

## Confirmed Facts

- `TASK_366A` accepted `.xls` read compatibility at `2e8d7ddd2b7d08bff49987763cbdce66c0ebc4c6`.
- `TASK_366B` accepted Standard record Method version sync and Sheet configuration at `18df3f34ce0f3bbac8c714b38f9b8aa747d100d7`.
- Source workbooks must remain read-only for `.xls` and `.xlsx`.
- Existing Confirm Matrix remains the only confirmed Matrix publication action.
- Implementation was later explicitly authorized, completed by Developer, passed
  Reviewer and QA, and is now complete/accepted after Integrator packaging. Schema/database
  changes were never authorized for this lane.

## Repository Evidence

- `MatrixImportCommitService.commit()` validates preview payload and selected groups, computes a task261 commit fingerprint, persists source lineage, builds a selected-only editable `ProjectMatrixDraftSnapshot`, and stores it with `draft_store.create_snapshot(...)`.
- `_build_selected_only_draft(...)` pulls Method text from preview `method`, `method_summary`, or `reference_standard` fields into draft rows.
- `routes_matrix_import_commit.py` returns the full draft snapshot to the frontend.
- `MatrixEditorWorkspace.tsx` calls `commitMatrixImport(...)` when Replace is clicked, applies `response.project_matrix_draft` to editor state, and closes the import dialog. The existing stale locator path reparses before commit.
- `MatrixMethodVersionSyncService` from TASK_366B reads the effective Standard record resource and worksheet, computes catalog and target fingerprints, builds row proposals, and applies selected row Method changes with CAS and audit context.
- `standard_method_version_parser.py` already owns `364-\d{2}` core extraction, Standard catalog parsing, candidate resolution, and Method proposal formatting.

## Planner Inference

- The cleanest implementation is a backend composition around Import Matrix commit, not a frontend second action.
- The import commit service must reuse TASK_366B catalog/proposal code and transform the in-memory draft snapshot only after all import payload and current Standard catalog authority facts are validated before any persistence.
- The sync context should be stored as import-mode audit metadata in existing `method_sync_context_json` unless implementation proves that current storage cannot safely represent the operation.
- Source-level authority read failures must block Replace to avoid a false impression that Replace completed authoritative Method sync.
- Row-level unsafe outcomes can be non-blocking but must remain explicit and no-write per row.

## Proposed Implementation Shape

1. Mechanically extract the pure Source Matrix aggregate construction currently inside
   `source_matrix_import_persistence_service.py` into a bounded builder. The existing
   persistence service delegates to it, preserving every current caller, and exposes
   `prepare_from_preview(...)` plus `persist_prepared(...)`. Preparation creates the
   import record and source snapshot in memory but performs no repository call.
2. Move selected-only draft construction out of the current 409-line commit service into a
   bounded pure builder. It consumes the prepared source snapshot, so the draft's
   source group/row IDs refer to the exact aggregate later persisted.
3. Add one import-specific Method authority resolver. It performs one configured
   Standard resource lookup and one accepted `ExternalExcelReadService` catalog read,
   verifies returned path and matched worksheet against that resource, and calls the
   accepted `parse_catalog_method()`, `parse_matrix_method()`, and
   `build_method_proposal()` functions directly. It must not copy parser regexes,
   candidate resolution, downgrade policy, or display formatting.
4. The resolver returns an immutable result containing the transformed in-memory draft,
   ordered row decisions, public summary, and strict import-mode context/fingerprints.
   It never persists and never calls a provider twice.
5. `MatrixImportCommitService.commit()` becomes a thin orchestrator: freeze canonical
   request facts, prepare source and draft aggregates, resolve current Method authority,
   then evaluate existing TASK_261 reuse. No persistence method is called before all of
   those steps succeed.
6. Exact reuse returns the existing read-verified draft. A new operation enters an
   injected application transaction scope backed by the request SQLAlchemy session's
   nested transaction, persists the prepared source aggregate and already-transformed
   draft, reloads and verifies both while the savepoint is open, then releases it.
   The outer `get_session()` transaction commits before FastAPI sends the response.
7. Add a typed `method_authority_sync` result to the commit response. The frontend
   continues applying `project_matrix_draft` immediately and displays one concise inline
   success/review message; it does not add another preview, apply action, or modal.

## Pure Preparation And Stable Identity

- The request payload is serialized once with canonical JSON
  (`ensure_ascii=False`, sorted keys, compact separators), decoded to a private deep
  copy, and then used for fingerprinting, source preparation, draft construction, and
  persistence. Non-JSON values are a typed validation failure before any write.
- Selected group keys are trimmed, uniqueness-checked, and retained in request order.
  Their fingerprint is over that exact normalized ordered tuple.
- Source locator identity binds normalized source path, trimmed document name, and
  normalized source format. Path canonicalization is lexical only (Windows
  `normpath`/`normcase`); it must not resolve, stat, open, or otherwise touch the file.
- Each import row receives a stable pre-persistence key derived from source row index
  plus canonical row order. Missing or duplicate source row indices remain stable for
  fingerprinting but receive explicit `row_identity_missing` or
  `row_identity_duplicate` decisions and cannot auto-update.
- Generated import/snapshot/draft UUIDs are audit identities only. They are excluded
  from canonical payload, row, proposal, and result fingerprints so an exact replay can
  compare current request facts with a prior operation.

## Atomic Boundary And Write Order

- The application boundary is one complete Replace preflight followed by one injected
  transaction scope. The transaction port returns a context manager; production passes
  `session.begin_nested`, while unit tests use a rollback-observable fake. Application
  code does not import SQLAlchemy.
- Preflight must finish before any source-import, source-snapshot, draft, or method audit/context write:
  - canonical payload, selected groups, and source locator identity;
  - prepared Source Matrix import record/snapshot and selected-only draft candidate;
  - current Standard resource ID, canonical configured path, effective worksheet, one
    catalog result, returned path/matched-sheet verification, and catalog fingerprint;
  - stable source root/row fingerprints, ordered row decisions, proposal fingerprint,
    pre-transform Method fingerprint, post-transform Method fingerprint, result
    fingerprint, context identity fingerprint, and serialized context.
- Source-level authority failures are zero-write across every related table or audit/context field, not just "no new draft."
- The prepared draft record already contains `method_sync_context_json`; there is no
  separate audit table or later context update.
- Write order inside the savepoint after successful preflight:
  1. prepared source import record and complete source snapshot aggregate;
  2. editable Matrix draft aggregate with transformed Method values and import context;
  3. reload source import/snapshot and draft through repositories;
  4. verify source IDs, source root fingerprint, persisted context equality, post-Method
     fingerprint, and child counts;
  5. release the savepoint, then let the existing request transaction commit.
- Any conflict during this transaction rolls back all source lineage, source snapshot, draft, and audit/context writes and returns typed `409`.
- Missing resource or unreadable/invalid Standard workbook/sheet/catalog is a typed
  validation/authority error through the existing commit route (`422`) and is zero-write.
  Reuse mismatch, stale context, and persistence/read-verify conflict are typed `409`.
- No schema migration is authorized or required. If implementation proves a database
  uniqueness constraint or new audit column is necessary, stop and return to
  Planner/Reviewer rather than adding it.

## TASK_261 Reuse Strategy

- Reuse by legacy TASK_261 payload/selected-group fingerprint alone is forbidden.
- Existing source import/draft reuse is allowed only after the same no-write preflight succeeds for the current request and the persisted import-mode method sync context matches all current authority facts.
- Required equality set:
  - existing source import ID, source snapshot ID, draft ID, project ID, normalized
    source locator fingerprint, and legacy TASK_261 commit fingerprint;
  - canonical imported payload fingerprint and ordered selected-group fingerprint;
  - prepared source root fingerprint and stable ordered row fingerprint;
  - Standard resource ID, canonical configured path, effective worksheet, verified
    matched worksheet, and catalog fingerprint;
  - pre-transform Method, ordered proposal, post-transform Method, and result
    fingerprints;
  - `matrix-import-method-sync:v1` schema, `replace_import` mode, and recomputed context
    identity fingerprint.
- Any resource/path/sheet/catalog/proposal/result/fingerprint/context difference rejects old reuse. TASK_366C freezes this as typed `409` no-write rather than creating a second source import under the same legacy fingerprint.
- Missing import-mode context, stale context version, or malformed context is also typed `409` no-write.
- Strict context parsing validates every explicit field as well as the aggregate identity
  fingerprint; matching only the aggregate hash is insufficient.
- The existing source snapshot and draft are reloaded and verified against stored
  context before reuse. A later saved-draft Method sync, manual Method edit, draft
  replacement, missing child aggregate, or divergent persisted Method result therefore
  blocks reuse.
- Same-payload/current-catalog reuse returns the existing source/draft identifiers and
  current summary and must prove source-import, source-snapshot, draft, and audit/context
  counts do not increase.

## Import-Mode Context And API Shape

`ProjectMatrixDraftRecord.method_sync_context_json` stores canonical JSON with this
private schema. All identity fields are mandatory on read:

```text
schema = matrix-import-method-sync:v1
mode = replace_import
project_id
source_import_id
source_snapshot_id
project_matrix_draft_id
task261_commit_fingerprint
source_locator_fingerprint
payload_fingerprint
selected_group_fingerprint
source_root_fingerprint
source_row_fingerprint
standard_resource_id
standard_resource_path
effective_worksheet_name
matched_worksheet_name
catalog_fingerprint
pre_method_fingerprint
proposal_fingerprint
post_method_fingerprint
result_fingerprint
context_identity_fingerprint
applied_at
row_results[]
```

- `context_identity_fingerprint` covers every field above except itself, `applied_at`,
  and the generated row/draft IDs inside display-only response data. `row_results` are
  canonical ordered records keyed by stable source row key and include row order,
  test item, current Method, status, resulting Method, matched Standard code/source
  row, reason, and `applied`.
- The response adds `method_authority_sync` with `status` (`synchronized` or
  `review_required`), `updated_count`, `current_count`, `review_count`, resource ID,
  effective worksheet, catalog/context fingerprints, and ordered row results. It does
  not expose or accept authority decisions from the client.
- Request DTO and endpoint stay unchanged. The response summary is server-derived from
  the same immutable resolution used to persist the draft; route code only maps types.
- Frontend derives one message such as `Matrix replaced. 3 Methods updated; 2 rows need
  review.` from the typed counts. It applies the returned draft first, then shows the
  inline message near the Matrix grid. It does not recompute row eligibility or modify
  Method values locally.

## Source-Level And Row-Level Policies

- Source-level blocker: missing Standard record resource, unreadable file, invalid worksheet, invalid catalog headers, unsupported workbook format, or catalog read exception. Result: typed no-write, no new draft.
- Row-level safe update: one recognized Method core and one safe catalog candidate with `update_available` or `revision_missing`.
- Accepted parser row statuses are preserved verbatim: `current`, `no_method_core`,
  `multiple_method_cores`, `catalog_missing`, `ambiguous`, and `downgrade_conflict`.
  Import identity validation may additionally return `row_identity_missing` or
  `row_identity_duplicate`. Only `update_available` and `revision_missing` set
  `applied=true` and change Method.
- Individual unparseable catalog codes are ignored by the accepted parser and reflected
  by row outcomes; parser/header/read exceptions remain source-level blockers. TASK_366C
  does not invent a new catalog matching rule.
- Row statuses must be included in audit/context or response summary so the operator can understand what did and did not update.

## Authorized May Touch

Exact future product May Touch:

- `backend/application/source_matrix_import_persistence_service.py`: mechanical
  delegation to the pure preparation module; preserve existing public commands and
  behavior, add prepare/persist-prepared boundaries.
- new `backend/application/source_matrix_import_builder.py`: moved pure aggregate
  construction only.
- `backend/application/matrix_import_commit_service.py`: thin preflight/reuse/write
  orchestration and typed authority/conflict errors.
- new `backend/application/matrix_import_draft_builder.py`: moved selected-only draft
  construction and stable source-row key derivation.
- new `backend/application/matrix_import_method_authority.py`: configured source
  validation, accepted parser calls, transformation, fingerprints, strict context, and
  response summary.
- `backend/api/routes_matrix_import_commit.py`: typed summary response mapping only.
- `backend/api/dependencies.py`: exact existing Matrix import provider hunk only,
  wiring one shared resource repository/catalog reader and `session.begin_nested`.
- `frontend/src/api/client.ts`: contiguous response summary types only.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: existing Replace
  success hunk and one inline status render only.
- focused test paths:
  - adapt existing `tests/unit/test_matrix_import_commit_service.py` fixtures only;
  - new `tests/unit/test_matrix_import_method_authority.py`;
  - new `tests/integration/test_matrix_import_method_authority_commit_api.py`;
  - test-only fixture/setup hunk in
    `tests/integration/test_matrix_import_group_selection_commit_api.py` for
    `test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input`
    only, limited to disposable Standard resource/catalog authority seeding so the
    existing `201` created/reused assertions run under the approved preflight contract;
  - existing source-persistence and TASK_366B tests as read-only regressions;
  - one focused Matrix Editor Replace regression, with no unrelated workspace cleanup.
- TASK_366C task/plan/Developer/Reviewer/Planner reconciliation evidence and the exact
  future board status hunk.

Explicit read-only dependencies:

- `backend/application/matrix_method_version_sync_service.py`;
- `backend/application/external_excel_read_service.py`;
- `backend/modules/test_plan/standard_method_version_parser.py`;
- `backend/infrastructure/storage/repositories/source_matrix_import.py`;
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`;
- Matrix Confirm/session publication services and TASK_366B focused suites.

## Must Not Touch / Locked Paths

- No product implementation in this Planner pass.
- No schema/database migration unless a future Reviewer/User gate explicitly approves it.
- No confirmed Matrix direct write.
- No Generic Test Record, TASK_360B specialized workbook, Fee, LTR, Report, project lifecycle, or output generation changes.
- No Standard record workbook write/save/convert.
- No real DB, public-drive, user attachment, source workbook, or generated-file access.
- No parser extraction rule changes outside reusing TASK_366B Method parser/resolver.
- No changes to TASK_366B saved-draft Preview/Apply behavior or context schema.
- No source/draft repository behavior change and no new database uniqueness claim.
- No assertion change, no product-contract relaxation, and no other-node edit in
  `tests/integration/test_matrix_import_group_selection_commit_api.py`; only the
  Standard authority fixture/setup hunk is allowed after Reviewer scope/readiness
  re-gate.
- No external dirty residual absorption.
- `.agents/**`, `docs/project_management/**`, remote push.

## Validation Gate Draft

- Pure authority tests: safe revision replacement, revision insertion, current, no core,
  multiple cores, no match (`catalog_missing`), ambiguity, downgrade, missing/duplicate
  stable row identity, deterministic ordered row/proposal/result fingerprints, and
  no duplicated parser policy.
- Pure preparation compatibility: current source-persistence API emits byte-equivalent
  domain values after extraction; prepared aggregates are zero-write until explicitly
  persisted.
- Service/API success: Replace returns transformed Methods plus the typed summary;
  source and draft audit IDs/context agree; only selected groups persist; Confirm Matrix
  remains a separate action.
- Source blocker matrix: missing/inactive resource, returned catalog path mismatch,
  invalid/missing matched sheet, unreadable workbook, invalid header, and catalog reader
  exception each leave source-import, source-snapshot, source rows/groups/cells, draft
  root/children, and method-context counts unchanged.
- Reuse matrix: exact same canonical payload/selection/source locator/current Standard
  authority/context returns `reused` and every count remains unchanged. Identical rows
  under switched resource ID, path, or effective sheet; changed catalog revision;
  missing/malformed/stale context; changed source locator; changed proposal/result;
  manually changed persisted Method; or missing source/draft child returns typed `409`
  and no count changes.
- Transaction tests use disposable SQLite and an injected post-source or post-draft
  failure. The savepoint must roll back all source and draft rows and permit a clean
  retry. A read-verify mismatch also rolls back.
- Frontend: one Replace response with transformed Methods immediately updates the Method
  column and displays updated/review counts without invoking TASK_366B Preview/Apply.
  A typed `409` keeps the existing editor/import state and shows the existing inline
  error path.
- Read-only regressions: TASK_261 import commit, source persistence, TASK_366B parser and
  saved-draft Preview/Apply, Matrix session reload, and Confirm Matrix.
- Legacy fixture reconciliation: rerun
  `tests/integration/test_matrix_import_group_selection_commit_api.py::test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input`
  after adding only disposable Standard resource/catalog authority setup. It must keep
  its existing success/reuse assertions, must not prove a no-authority fallback, and
  must not write real DB/files or touch real Standard workbooks.

Future focused commands:

```text
py -m pytest tests/unit/test_matrix_import_commit_service.py tests/unit/test_matrix_import_method_authority.py tests/integration/test_matrix_import_method_authority_commit_api.py tests/integration/test_matrix_import_group_selection_commit_api.py tests/integration/test_project_test_plan_source_matrix_import_persistence_api.py tests/unit/test_standard_method_version_parser.py tests/unit/test_matrix_method_version_sync_service.py tests/integration/test_matrix_method_version_sync_api.py -q
npm test -- MatrixEditorWorkspace --run
npm run build
py -m py_compile <exact TASK_366C backend product/test paths>
```

Static gates: `git diff --check`; UTF-8 trailing whitespace; physical line count without
blank-line suppression; exact May Touch and forbidden-scope scans; `git diff --cached`
empty; `git status --short -- data` empty; no real source/Standard workbook path in
test logs or fixtures.

## Module Size And Split Gate

- Current UTF-8 physical-line count command:
  `(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`, counting blanks.
- Current `matrix_import_commit_service.py` is 409 physical lines. Move draft building
  before orchestration changes; final target is below 300 and hard limit below 500.
- Current `source_matrix_import_persistence_service.py` is 480 physical lines. Because
  TASK_366C must touch its preparation boundary and the file is close to the 500-line
  hard limit, first move pure builders through a narrow mechanical delegation so the
  service stays below 500, preferably below 300, and the new builder remains below 500.
- Superseded historical count notes `465` / `536` are not current package facts.
- New authority and draft-builder modules each target below 300 and must remain below
  500. New Python tests remain below 500.
- Do not pass the size gate by deleting blank lines or formatting churn; use the
  planned mechanical split and bounded modules.
- `routes_matrix_import_commit.py` is 200 lines and must remain below 300.
- `backend/api/dependencies.py`, `client.ts`, and `MatrixEditorWorkspace.tsx` are accepted
  oversized shared composition surfaces. Only the exact provider/type/Replace-status
  hunks above are allowed; inspect their diff hunks separately and do not use TASK_366C
  to refactor them.

## Package Isolation

- Treat TASK_366B accepted HEAD as the baseline.
- Stage only TASK_366C hunks when implementation is later approved.
- Do not absorb current Fee, frontend, release, TASK_364/TASK_365, or other dirty residuals.
- Any mixed file such as `MatrixEditorWorkspace.tsx`, `frontend/src/api/client.ts`, `backend/api/dependencies.py`, or repository/service files must be hunk-isolated and explained in Developer evidence.
- Do not modify or stage current TASK_366B B3 residuals or any unrelated Fee, parser,
  release/dist, TASK_364/TASK_365, or future lane files.

## Definition Of Ready / Authorization

Developer planning-first is complete. Planner B3/B4 docs-only fix is complete.
Reviewer implementation-readiness re-gate passed, and the user explicitly approved
TASK_366C product implementation. Developer implementation and the approved test-only
fixture fix are complete. Reviewer passed, QA passed, and Integrator accepted the
isolated local package.

Package checkpoint facts:

- Disposable backend/API/replay validation: `28 passed`.
- Matrix Editor frontend validation: `MatrixEditorWorkspace` `44` tests passed.
- Frontend build and candidate backend `py_compile` passed.
- Diff, trailing, staging, and `data/**` scans were clean except existing LF/CRLF notices.
- Safe EIA-364 updates appeared in the returned editable draft and aria-live summary.
- Authority/replay changes and persistence failure remained typed zero-write.
- Confirm Matrix remains the only publication step.
- The only workbook save is the authorized pytest `tmp_path` fixture setup.
- Browser tooling residual is non-blocking: no disposable live Matrix route exists and
  in-app Browser local-file fixture navigation was rejected by URL safety policy.

No blocking questions. The lane is complete/accepted; remote push was intentionally not performed.
