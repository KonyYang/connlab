# TASK_366C Developer Evidence

Date: 2026-07-21

Role: Developer implementation

Lane: `import-matrix-replace-method-authority-sync`

Status: `ready_for_review`

Implementation authorization: authorized by the reconciled TASK_366C source of truth.

## Current Phase And Legal Basis

- Current phase: Phase 11 Project Workbench / Matrix controlled foundation.
- Active task: `TASK_366C_IMPORT_MATRIX_REPLACE_METHOD_AUTHORITY_SYNC`.
- Accepted upstream: TASK_366B at HEAD
  `18df3f34ce0f3bbac8c714b38f9b8aa747d100d7`.
- Reviewer B1/B2 plan re-gate is `reviewer_pass`; the user explicitly approved this
  Developer planning-first pass.
- The board/task wording still says pending Reviewer plan re-gate. Product implementation
  therefore remains unauthorized and the next legal governance action is Planner
  source-of-truth reconciliation.

## Read-Only Code Audit

The pass read the real Import Matrix Replace path, TASK_261 persistence/reuse path,
accepted TASK_366B resolver/catalog/signature/CAS/audit path, route/dependency/session
composition, repositories, frontend client, and Matrix Editor reload behavior.

Confirmed implementation facts:

- `MatrixImportCommitService.commit()` currently returns an existing draft immediately
  on the legacy TASK_261 fingerprint, before any Standard authority read.
- New imports currently call `persist_from_preview()` before building the selected-only
  draft, so source lineage is flushed before Method authority can be evaluated.
- Source snapshot IDs are generated inside the persistence service and are required by
  the selected draft's group/row lineage. A no-write preflight therefore requires a pure
  prepared Source Matrix aggregate, not a second independently built structure.
- `get_session()` supplies one request session and commits after the route returns;
  exceptions roll it back. An injected `session.begin_nested` scope can make the
  application write boundary independently rollback-observable while preserving the
  existing outer transaction.
- `ProjectMatrixDraftRepository.create_snapshot()` already persists
  `method_sync_context_json`; no schema or repository behavior change is needed.
- TASK_366B parser functions already own exact core parsing, candidate resolution,
  downgrade policy, and display-preserving revision replacement. Import mode can call
  those public pure functions directly without changing the saved-draft service.
- The existing frontend Replace path already applies the returned draft immediately.
  It needs only typed summary consumption and one inline status message, not another
  Method preview/apply action.

## Refined Implementation Strategy

### 1. Prepare source and draft before writes

- Mechanically move pure Source Matrix aggregate construction from the current 480-line
  persistence service into `source_matrix_import_builder.py`.
- Preserve existing persistence commands and callers. Add explicit
  `prepare_from_preview()` and `persist_prepared()` boundaries.
- Move selected-only draft construction out of the current 409-line commit service into
  `matrix_import_draft_builder.py` and consume the exact prepared source snapshot IDs.
- Canonicalize the payload once to a private JSON copy. Use it for every fingerprint,
  builder, and persisted payload so caller mutation or alternate serialization cannot
  split authority facts.

### 2. Resolve one immutable Standard authority result

- Add `matrix_import_method_authority.py` with one resource lookup and one accepted
  catalog read. Verify configured/read path and effective/matched worksheet before
  constructing proposals.
- Call TASK_366B parser APIs directly. Do not duplicate regex, matching, ambiguity,
  downgrade, or Method formatting rules.
- Produce ordered stable row decisions, transformed draft, public summary, and strict
  `matrix-import-method-sync:v1` context from the same facts. No second provider read is
  permitted.
- Stable fingerprints bind source locator, canonical payload, ordered selection,
  selected source root/rows, Standard resource/path/sheet/catalog, pre-Method values,
  proposals, resulting Methods, and complete result identity. Random persistence IDs
  are excluded from replay fingerprints.

### 3. Replace legacy reuse with strict replay verification

- A matching TASK_261 fingerprint is lookup information only, never an early return.
- Repeat the full current preflight, parse every mandatory context field, recompute the
  context identity fingerprint, reload existing source/draft aggregates, and compare
  all persisted/current facts.
- Exact equality returns the existing IDs/draft with `commit_status=reused` and no
  count changes.
- Changed resource ID/path/sheet/catalog, source locator, payload/selection, row/proposal
  or result fingerprint, context schema, manual/saved Method state, or missing aggregate
  returns typed `409` and writes nothing. TASK_366C does not create a second import under
  the same legacy fingerprint.

### 4. Persist one read-verified unit

- Source-level authority preflight completes before entering the write scope.
- For a new operation, the injected nested transaction persists prepared source lineage
  then the transformed draft whose root already contains context JSON.
- Reload and verify source IDs/root, child counts, exact context, and post-Method
  fingerprint before releasing the savepoint. Any create, flush, or read-verify failure
  rolls back both aggregates and maps to typed `409`.
- The existing outer request transaction commits before response delivery. No schema,
  new audit table, source workbook write, or confirmed Matrix mutation is involved.

### 5. Typed response and frontend behavior

- Keep the commit request unchanged.
- Add a server-derived `method_authority_sync` summary with status, updated/current/review
  counts, source identity display facts, context/catalog fingerprints, and ordered row
  decisions.
- Matrix Editor applies `project_matrix_draft` exactly as today, then shows one concise
  inline count summary. It never recalculates authority or changes Method locally.
- Confirm Matrix remains the sole publication action.

## Exact Future May Touch

- `backend/application/source_matrix_import_persistence_service.py`
- new `backend/application/source_matrix_import_builder.py`
- `backend/application/matrix_import_commit_service.py`
- new `backend/application/matrix_import_draft_builder.py`
- new `backend/application/matrix_import_method_authority.py`
- `backend/api/routes_matrix_import_commit.py`
- exact `get_matrix_import_commit_service` hunk in `backend/api/dependencies.py`
- contiguous response types in `frontend/src/api/client.ts`
- exact Replace success/status hunks in
  `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- bounded TASK_366C unit/integration tests plus fixture-only adaptation in the existing
  import commit unit test
- TASK_366C governance/evidence after later role gates

Read-only regression dependencies include TASK_366B service/parser/catalog, source and
draft repositories, Matrix session/Confirm services, and accepted frontend behavior.

## Locked Scope

- No schema/database migration or new uniqueness claim.
- No TASK_366B saved-draft Preview/Apply behavior change.
- No parser/import extraction rule change.
- No confirmed Matrix direct write, Generic Test Record, TASK_360B, Fee, LTR, Report,
  project lifecycle, workbook output, source workbook save/convert, or real file access.
- No `.agents/**`, `docs/project_management/**`, external residual cleanup, stage,
  commit, or push.

## TDD And Validation Gate

- Pure authority unit cases cover every accepted parser status plus stable identity,
  deterministic fingerprints, and safe transformation.
- Disposable API tests prove updated Method output, typed summary, source-level
  all-table zero-write, exact reuse/no duplicates, every source/context switch conflict,
  and post-source/post-draft/read-verify rollback.
- Frontend regression proves returned authoritative Methods appear immediately and the
  summary is inline without a separate sync action.
- Read-only TASK_261, source persistence, TASK_366B Preview/Apply, Matrix session, and
  Confirm Matrix suites must remain green.
- Required validation: focused pytest, focused Matrix Editor tests, frontend build,
  py_compile, diff/trailing/UTF-8 physical line counts, exact May Touch/forbidden scope,
  staging-empty, and no-real-data scans.

Current size facts use UTF-8 physical-line count including blanks:
`(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`. Current counts are
`matrix_import_commit_service.py` = 409 and
`source_matrix_import_persistence_service.py` = 480. Earlier `465` / `536` counts are
superseded historical planning notes and are not current package facts. The split remains
required because source persistence is close to the 500-line hard limit. Future touched
bounded Python modules and tests must be below 500; the extracted services target below
300. Do not pass the limit through blank-line suppression. Existing oversized
dependency/client/workspace files receive only their exact approved hunks.

## Docs-Only Validation

- Product/backend/frontend/test files changed by this pass: none.
- Targeted status for every exact future TASK_366C product/test May Touch path is empty.
- Plan/evidence no-index diff checks report no whitespace errors (only the repository's
  expected LF/CRLF notices). Existing board diff-check also reports no error.
- UTF-8 physical lines/trailing scan: plan `349/0`, Developer evidence `185/0` before
  this final validation note; both governance files remain bounded and clean.
- Real database, public drive, attachment, source workbook, or generated file accessed:
  none.
- Stage/commit/push: none.
- Governance changes by this Developer pass are limited to the TASK_366C plan and this
  Developer evidence. The pre-existing dirty board/task/Planner/Reviewer docs remain
  untouched.

## Planning-First Historical Blocker Summary

Superseded by the later authorization and implementation sections below. At that time,
there was no technical planning blocker; governance was intentionally pending Planner
source-of-truth reconciliation because the board/task still predated the passed Reviewer
re-gate and user planning-first approval. Implementation was unauthorized at that point.

## Planner B3/B4 Governance Correction

This Developer planning-first evidence is updated by Planner source-of-truth
reconciliation to reflect the Reviewer B3/B4 docs-only fix:

- The formal task/plan/Planner evidence/board now include source persistence
  delegation plus `source_matrix_import_builder.py`,
  `matrix_import_draft_builder.py`, and `matrix_import_method_authority.py`.
- Current UTF-8 physical-line facts are `source_matrix_import_persistence_service.py`
  = 480 and `matrix_import_commit_service.py` = 409; earlier `536` / `465` figures
  are superseded historical notes only.
- Source persistence is close to the 500-line hard limit, so later implementation must
  use the planned narrow mechanical extraction/delegation and keep final/new Python
  modules and tests below 500 without blank-line suppression.
- The source-of-truth status at that point was ready for Reviewer
  implementation-readiness re-gate; product implementation was still unauthorized.

## Planning-First Historical Next Legal Role

Superseded by the current checkpoint below. The next role at that time was Planner
source-of-truth reconciliation, then Reviewer implementation-readiness gate as
recorded by Planner. Do not start Developer implementation without explicit subsequent
user approval.

## Authorized Implementation Pass

The reconciled authorization was subsequently granted. This pass implemented the
approved Replace-time Method authority boundary without changing TASK_366B saved-draft
Preview/Apply, repositories, schema, or confirmed Matrix publication.

Implemented behavior:

- `source_matrix_import_builder.py` now owns pure construction of the complete Source
  Matrix aggregate. The existing persistence service exposes no-write prepare and
  prepared-persist boundaries while retaining its public compatibility methods.
- `matrix_import_draft_builder.py` owns selected-only draft construction using the exact
  prepared source IDs.
- `matrix_import_method_authority.py` performs one cached Standard resource/catalog read,
  reuses the accepted TASK_366B parser/proposal functions, applies safe Method updates,
  emits typed ordered row summaries, and binds the full source/resource/path/effective
  sheet/catalog/proposal/result identity in `matrix-import-method-sync:v1` context.
- Legacy TASK_261 fingerprint lookup is no longer an early return. Reuse now re-runs the
  complete authority preflight and read-verifies the persisted source and draft facts.
  Changed or malformed replay identity is typed `409` with no duplicate import.
- New writes run inside the injected nested transaction, persist source then draft, and
  reload/read-verify both before releasing the savepoint. Injected post-draft failure is
  covered as an all-table rollback.
- The route/client expose the typed `method_authority_sync` summary. Matrix Editor keeps
  using the returned authoritative draft and adds one `aria-live` inline Replace result;
  Confirm Matrix remains the only publication action.

TDD progression:

- `tests/unit/test_matrix_import_method_authority.py` first failed because the bounded
  authority module did not exist, then passed all five resolver/identity/source-context
  cases.
- `tests/integration/test_matrix_import_method_authority_commit_api.py` first failed
  because the route lacked the typed summary, then passed six disposable SQLite cases:
  successful update and strict reuse, catalog switch, same-content resource path switch,
  missing/mutated context, source-authority zero-write, and post-draft rollback.
- The Matrix Editor summary regression first failed on missing inline text, then passed
  through the full existing component file.

## Implementation Validation

Passing checks:

- Candidate resolver/commit/API/source-persistence set: `18 passed`.
- Planned backend gate after the authorized fixture fix: `28 passed`.
- Source persistence regressions were included in the passing candidate set.
- `npm test -- MatrixEditorWorkspace --run`: `1 file / 44 tests passed`.
- `npm run build`: passed; only the existing Vite chunk-size warning remains.
- `py -m py_compile` for all TASK_366C backend and Python test candidates: passed.
- Candidate tracked `git diff --check`: passed with LF/CRLF notices only.
- Staging area: empty. `git status --short -- data`: empty. No real database, public
  drive, attachment, source workbook, or generated workbook was accessed or modified.

UTF-8 physical-line counts including blank lines:

- `routes_matrix_import_commit.py`: 257
- `matrix_import_commit_service.py`: 320
- `source_matrix_import_persistence_service.py`: 150
- `source_matrix_import_builder.py`: 409
- `matrix_import_draft_builder.py`: 152
- `matrix_import_method_authority.py`: 448
- `test_matrix_import_commit_service.py`: 337
- `test_matrix_import_method_authority.py`: 250
- `test_matrix_import_method_authority_commit_api.py`: 358
- `test_matrix_import_group_selection_commit_api.py`: 219

`backend/api/dependencies.py` remains an existing oversized composition module at 2242
physical lines; TASK_366C changed only its explicitly authorized provider hunk. The
bounded route, services, helpers, and Python tests are all below the 500-line hard limit.

## Tests-Only Fixture Fix

Reviewer fixture-scope/readiness re-gate authorized one setup-only hunk at:

`tests/integration/test_matrix_import_group_selection_commit_api.py::test_matrix_import_commit_api_creates_selected_only_draft_and_reuses_same_input`

The node now creates a minimal Standard catalog workbook under its disposable
`tmp_path`, registers it through the existing External Resource API, and then executes
the unchanged Replace request and business assertions. Production composition reads the
temporary XLSX through the real read-only gateway and resolver. No product fallback,
mock authority shortcut, source workbook access, or assertion weakening was introduced.

Validation:

- Exact previously failing node: `1 passed`.
- Complete planned backend gate: `28 passed`.
- Test module physical lines including blanks: `219`, below the hard limit.
- Its diff contains only the required `Workbook` import and disposable setup hunk; the
  existing created/reused, selected-group, lineage, and identity assertions are unchanged.
- File `py_compile`, diff-check, UTF-8 trailing-whitespace, exact-path, no-real-data, and
  staging-empty checks passed. The temporary workbook was pytest-owned and no real
  database, public drive, attachment, or operator workbook was accessed.

## Current Checkpoint And Next Legal Role

TASK_366C Developer implementation and the authorized tests-only fixture fix are complete.
Status is `ready_for_review`; blocker summary is `none`. The next legal role is Reviewer
implementation re-gate. Do not route QA or Integrator from this Developer pass.
