# TASK_361L Point Profile Fee Pricing Draft Rebase Corrective Reviewer Evidence

Date: 2026-07-15

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## Gate Scope

This is a read-only Reviewer plan gate. No product code, tests, real database, or
real file was written or accessed.

## Facts Confirmed

- The stated defect is real: the existing pricing-draft context contains only Matrix
  id/revision and fee-rule version, while the frontend hydrator overlays every saved
  editable field, including `units`, onto the current Fee source preview. A saved
  LLCR `units=1` can therefore hide TASK_361K's current Point Profile-derived Units.
- A versioned V2 JSON envelope with a canonical automatic-defaults fingerprint and
  explicit per-field manual provenance is an appropriately additive, non-destructive
  storage boundary. It can keep V1 payloads readable for audit without silent
  migration or load-time write.
- The planned authority contract is otherwise sound: exact Measurement Plan target
  authority remains higher priority, Point Profile lineage participates in freshness,
  LLCR Units/testing fee remain derived, and compatible explicit operator edits can be
  retained without treating unknown saved values as manual.
- The task correctly locks Fee rules/pricing formulas, TASK_361K authority selection,
  Point Profile and Measurement Plan writes, workbook layout, generic outputs,
  parser/LTR/public-drive, and real-data/file scope. The Planner pass is docs-only;
  TASK_361F evidence and TASK_361H image residuals remain excluded.

## Blocking Finding

### B1: The plan does not carry the new freshness states through the server-side Update Fee and export consumers

The future V2 contract introduces `legacy_unclassified`, `rebase_required`, and
`blocked` in addition to `missing/current/stale`, and requires Update Fee and export
to refuse blocked or stale authority. However, the current
`ConfirmedFeeVersionService._require_current_pricing_snapshot()` rejects only
`missing` and `stale`; any newly introduced non-current status with a saved snapshot
would otherwise fall through as confirmable. The current browser export path also
submits its edited payload directly, so a UI-only load-state check cannot enforce the
declared no-stale/no-blocked consumer rule for the API boundary.

The listed May Touch paths omit the Confirmed Fee confirmation consumer and the
server-side export guard/boundary. The current plan also leaves the explicit sequence
ambiguous for a read-only `legacy_unclassified` or `rebase_required` load: whether an
operator action first writes a validated V2 merged snapshot, and only then confirms or
exports, must be deterministic. Without this, the proposed V2 provenance can prevent
hydration yet still permit the old payload to be confirmed or exported.

**Required Planner fix:**

1. Freeze one typed state/transition table for `missing`, `current`,
   `legacy_unclassified`, `rebase_required`, `blocked`, and `stale`. Only a validated
   V2 `current` snapshot may be consumed by Update Fee or export. State explicitly
   whether an operator's explicit reviewed rebase first saves a new V2 snapshot under
   expected Matrix/rule/profile/default-fingerprint tokens before those consumers run;
   it must never be a load-time or Cancel write.
2. Extend May Touch and the implementation order to include the narrow server-side
   confirmation guard (`backend/application/confirmed_fee_version_service.py`, plus
   its route/error mapping and tests as needed) and the API/application export guard
   that validates the same context before accepting an edited payload. This may not
   alter workbook layout, writer behavior, pricing rules, or formulas.
3. Define the shared validation boundary so Update Fee, browser export, direct API
   export, autosave, reload, and Cancel cannot disagree on a merged V2 context.
   Expected-token mismatch must be typed `409`/blocked with no write or file output.
4. Add disposable tests that attempt Update Fee and direct export for each
   `legacy_unclassified`, `rebase_required`, `blocked`, and stale mismatch state, and
   assert no Confirmed Fee version, pricing-draft overwrite, or output action occurs.
   Cover the explicit successful reviewed-rebase sequence separately.

## Validation Notes

- Read `AGENTS.md`, the task board, lane orchestration protocol, TASK_361L task/plan/
  Planner evidence, TASK_361K authority context, pricing-draft persistence and route
  code, Confirmed Fee confirmation service, and Fee page hydration/Update/export
  control flow.
- `git diff --check` found no whitespace failure; only established LF/CRLF notices
  for the board and external TASK_361F evidence were emitted. The visible TASK_361L
  changes are governance-only.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner fix pass for B1, then Reviewer plan re-gate.
Do not route User approval, Developer planning-first, or implementation.

Blocking summary: define and enforce the V2 freshness state transition at every
server-side Update Fee/export consumer, not only during frontend hydration.

---

# TASK_361L Reviewer Plan Re-Gate: B1

Date: 2026-07-15

Role: Reviewer

Status: reviewer_pass

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## B1 Re-Gate Result

- B1 is closed. The revised contract defines exactly five semantic states:
  `missing`, `current_v2`, `rebase_required`, `legacy_unclassified`, and `blocked`.
  Only a server-validated V2 `current_v2` snapshot is eligible for Update Fee, direct
  and child export, Required Forms, Matrix Fee rebase, or other production consumers.
- The explicit reviewed-rebase sequence is now safe and deterministic: build current
  defaults, merge only proven manual fields in memory, show the result, atomically save
  V2 with expected authority/default tokens, reload and revalidate, then consume. Load
  and Cancel remain zero-write; `blocked` cannot advance through save.
- The opaque token binds draft id, source-context fingerprint, and canonical payload
  fingerprint. Confirm Fee and edited export must provide it; direct edited export is
  checked against the server-loaded V2 payload, so a raw client payload cannot bypass
  authority freshness. Token/context changes return typed conflict before a Confirmed
  Fee write, artifact/output, Required Forms write, or draft overwrite.
- May Touch now includes the narrow server-side confirmation guard, typed route
  mapping, export/service/child boundary, Required Forms current check, Matrix rebase
  promotion, and associated focused tests. Workbook layout/writer behavior, pricing
  rules and formulas, TASK_361K authority selection, schema/lifecycle, and all other
  locked paths remain unchanged.
- The validation matrix now covers every non-`current_v2` state at Confirmed Fee and
  direct/browser/child export, Required Forms, and rebase boundaries, plus the
  successful explicit reviewed-rebase sequence. It requires no write/artifact/output
  on rejection and keeps all persistence/API/browser scenarios disposable.

## Validation Notes

- Re-read the repaired task, plan, Planner evidence, prior B1 evidence, pricing-draft
  persistence/route flow, Confirmed Fee confirmation guard, direct export behavior,
  Required Forms/rebase composition facts, Fee page hydration and Update/export flow,
  and TASK_361K confirmed authority boundary.
- Planner changes remain governance-only. `git diff --check` and targeted trailing
  whitespace checks are clean apart from established LF/CRLF notices for external
  board/TASK_361F residuals; no product code, test, schema, API client, real database,
  or file was modified or accessed by this re-gate.

## Decision

`reviewer_pass`

Recommended next role/action: User approval for Developer planning-first. Product
implementation remains unauthorized; do not route Developer implementation.

Blocking summary: none for the Reviewer plan re-gate.

---

# TASK_361L Reviewer Implementation-Readiness Gate

Date: 2026-07-15

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## Gate Scope

This is a read-only implementation-readiness review. No product code, tests, real
database, or real file was written or accessed.

## Facts Confirmed

- Source of truth is aligned for this gate: the board, task, Planner reconciliation,
  and Developer evidence record Reviewer plan re-gate pass, user-approved docs-only
  planning-first, and no implementation authorization. The Developer pass is
  governance-only; visible product changes remain external TASK_361F evidence and
  TASK_361H QA artifacts.
- The V2 envelope is appropriately additive inside existing `payload_json`: explicit
  source/default fingerprints, machine Point Profile lineage, canonical row identity,
  and field-level provenance can keep V1 values readable while classifying V1 as
  `legacy_unclassified` without a load-time write.
- The five-state classification, review-first V2 merge, server-loaded writer values,
  and all identified Confirmed Fee/direct-browser-child export/Required Forms/Matrix
  rebase composition points are sufficiently bounded. The planned module split also
  avoids extending the current oversized persistence, export, and page modules.
- The present code confirms why the new boundary is needed: the pricing-draft
  repository currently performs an unconditional context upsert, while Confirmed Fee
  accepts any saved snapshot other than `missing` or `stale`; the proposed guard is
  therefore the correct ownership boundary for the migration.

## Blocking Finding

### B2: The deterministic validation token and save path do not yet define an enforceable replay/concurrency contract

The plan calls `pricing_draft_validation_token` a deterministic hash of draft id,
source-context fingerprint, and canonical payload fingerprint, while also requiring
the guard to reject a “replayed token.” A deterministic stateless hash cannot reveal
that the identical valid token was submitted a second time. In particular, the
existing Confirmed Fee service creates a new version after validating the current
draft, so a repeated valid Confirm request has no documented idempotency or
single-consumption outcome. The plan also calls the V2 save atomic but does not define
a repository compare-and-swap predicate for two writers that loaded the same draft id
and authority context. The existing repository's context upsert would allow the later
request to overwrite the earlier request's values and provenance.

This leaves the requested token replay and concurrent reviewed-save protection
ambiguous. It is not sufficient to list replay/concurrency in the test matrix; the
write/consumer contract must name the observable server behavior before product code
is authorized.

**Required Developer docs-only planning fix:**

1. Define a real optimistic-concurrency precondition for V2 save, including the exact
   expected prior canonical payload fingerprint (or an equivalent immutable revision
   value) and a repository-level conditional create/update. Both the source/default
   preflight and that conditional write must be in one transaction. A zero-row update
   or competing initial insert must return typed `409`, reload the current V2 envelope,
   and preserve both the existing row and its provenance; no last-writer-wins upsert.
2. Resolve the word “replay” per consumer. Either make Confirm Fee idempotent for the
   exact validated V2 draft/lineage and specify the lookup/unique or transactional
   boundary, or introduce a server-verifiable one-time consumption record. If exports
   are intentionally repeatable, state that the token is a freshness attestation, not
   a one-time credential, and restrict “replay rejection” to stale/mismatched
   context/payload. Matrix rebase auto-confirm requires the same retry/idempotency
   decision.
3. Add disposable regression cases for two concurrent reviewed saves with the same
   prior V2 snapshot, duplicate Confirm requests with the same valid token, and the
   chosen repeat-export behavior. Each case must assert the precise `409` or
   idempotent result, no lost manual provenance, no duplicate Confirmed Fee version
   where idempotency is selected, and no unexpected writer/artifact/output action.
   Keep V1 load/Cancel zero-write and all locked scopes unchanged.

## Validation Notes

- Read `AGENTS.md`, the task board, TASK_361L task/plan/Planner/Developer/
  reconciliation/Reviewer evidence, current pricing persistence/repository,
  Confirmed Fee, export, Required Forms, Matrix rebase, dependency composition, and
  Fee page autosave/Cancel behavior.
- `git diff --check` and targeted trailing-whitespace scans found no TASK_361L
  failure; the established LF/CRLF notices concern the board and external TASK_361F
  evidence. No product test was run, as required for this readiness gate.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer docs-only planning fix for B2, then Reviewer
implementation-readiness re-gate. Do not route implementation approval,
reconciliation for implementation, Developer implementation, QA, or Integrator.

Blocking summary: specify enforceable V2 compare-and-swap and deterministic
consumer-specific replay/idempotency semantics before implementation.

---

# TASK_361L Reviewer Implementation-Readiness Re-Gate: B2

Date: 2026-07-15

Role: Reviewer

Status: reviewer_pass

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## B2 Re-Gate Result

- B2 is closed. The deterministic token is now correctly limited to a currentness and
  integrity attestation for one draft id, V2 generation, source context, and canonical
  payload. It is explicitly not presented as a one-time replay credential.
- The V2 envelope now carries a positive generation. First save uses a conditional
  unique insert; V2 autosave/manual/reviewed-rebase updates use the exact prior draft
  id, generation, persisted snapshot fingerprint, `updated_at`, and prior payload
  condition; V1 upgrade uses the raw V1 snapshot fingerprint. Each competing write
  fails with typed `409`, reloads, and leaves winning values and provenance intact.
  Authority/default preflight, conditional write, and `current_v2` post-write
  revalidation are specified as one transaction.
- Consumer retry behavior is now explicit and bounded: Confirm Fee returns the
  existing version for the exact V2 generation/lineage/summary in a serialized
  transaction; Matrix Fee rebase has the same promotion identity rule; exports are
  intentionally repeatable but revalidate on every call before any writer or artifact
  work; Required Forms revalidates embedded V2 lineage before placement.
- The disposable matrix now covers competing first/V2/V1 saves, duplicate Confirm,
  repeat and stale exports, rebase retry, stale Required Forms lineage, and frontend
  stale-CAS reload. It preserves V1 load/Cancel zero-write and continues to require
  the observable `15`/`9` LLCR Units correction with compatible manual fields kept.
- The exact module split, existing JSON-only additive storage boundary, dependency
  composition, line-limit approach, frontend model boundary, and locked scopes remain
  adequate. No schema change, formula/rule/UI redesign, Point Profile authority
  mutation, workbook layout change, generic output work, or external residual is
  authorized.

## Validation Notes

- Re-read the updated TASK_361L task/plan/Developer evidence, Planner reconciliation,
  prior B2 evidence, task board, current pricing-draft repository/service, Confirmed
  Fee model/service, export/Required Forms/Matrix rebase composition, and Fee
  autosave/Cancel flow.
- The current working tree remains governance-only for this lane. `git diff --check`
  and targeted trailing-whitespace scans are clean apart from established LF/CRLF
  notices for the external board/TASK_361F entries. No product test was run and no
  real database or file was accessed, as required for this readiness gate.

## Decision

`reviewer_pass`

Recommended next role/action: User implementation approval, then Planner
source-of-truth reconciliation before Developer implementation. Do not route
Developer implementation directly from this gate.

Blocking summary: none for implementation-readiness. Product implementation remains
unauthorized pending the explicit user approval and reconciliation.

---

# TASK_361L Reviewer Implementation Gate

Date: 2026-07-15

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## Gate Scope

Read-only implementation review of the actual TASK_361L candidate. No product code or
test was modified; no real database or real file was accessed.

## Blocking Finding

### B3: Confirm Fee does not enforce the V2 attestation or retain the V2 lineage required by downstream currentness

`backend/application/confirmed_fee_version_service.py` builds the V2 comparison tuple
inside `_validate_v2_pricing_snapshot()` but never evaluates it. The `if any(...)`
check is instead indented after the unconditional return in
`_confirmed_fee_is_current_v2()`, where it is unreachable. Consequently, a Confirm
request with a mismatched or missing V2 generation, payload fingerprint, or validation
token can create a Confirmed Fee version.

The same service writes `pricing_snapshot_json` as the old edited-values-only JSON.
It does not retain V2 generation, source-context fingerprint, or payload fingerprint.
`_confirmed_fee_is_current_v2()` then compares only Matrix/rule context and
`pricing_draft_edit_id`. The pricing-draft CAS deliberately preserves that draft id
across generations, so a newer V2/rebased pricing draft can leave an older Confirmed
Fee incorrectly `current`, allowing Required Forms past the promised V2 lineage gate.
`_matching_confirmed_fee()` has the same missing generation/lineage comparison, so it
does not implement the planned exact-generation Confirm idempotency boundary.

This breaks the core TASK_361L currentness contract despite the focused suites passing.

**Required bounded Developer fix:**

1. Keep the token/generation/payload checks inside `_validate_v2_pricing_snapshot()`
   and require all three for every persisted V2 confirmation. Map failure through the
   existing typed conflict path before any Confirmed Fee write.
2. Persist a backward-compatible confirmed-pricing envelope that includes the exact
   validated V2 generation, source-context fingerprint, and payload fingerprint with
   the server-loaded edited values. Make `_confirmed_fee_is_current_v2()` and
   `_matching_confirmed_fee()` compare that complete lineage, not draft id alone.
   Existing pre-V2 confirmed versions must fail closed as non-current for TASK_361L
   consumers unless an already-approved compatibility contract proves otherwise.
3. Add service/API regressions for missing/mismatched V2 attestation with zero
   Confirmed Fee write, an older Confirmed Fee after the same draft id advances to a
   new V2 generation (Required Forms must remain blocked with no placement), and
   duplicate Confirm of the exact same V2 generation/lineage/summary returning one
   version. Keep the existing P/1-3 Units `15`/`9`, export, rebase, and locked scope
   regressions green.

## Validation Notes

- Direct source review confirmed the unreachable check and lineage loss in
  `backend/application/confirmed_fee_version_service.py`.
- Re-ran the Developer's main disposable backend suite: `80 passed`.
- Re-ran Required Forms/Confirmed Fee focused suite: `49 passed`.
- Re-ran `npm test -- FeeEvaluationReviewExportPage --run`: `28 passed`, with the
  established React `act(...)` warnings. Candidate backend `py_compile` also passed.
- The passing tests do not cover the above mismatch/currentness path. `git diff
  --check` and trailing-whitespace scans were clean apart from established LF/CRLF
  notices. The unrelated TASK_361F evidence and TASK_361H artifacts remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded fix pass for B3, then Reviewer
implementation re-gate. Do not route QA or Integrator.

Blocking summary: make Confirmed Fee enforce and persist the exact V2 attestation so
Required Forms and Confirm idempotency cannot treat an older generation as current.

---

# TASK_361L Reviewer Implementation Re-Gate: B3

Date: 2026-07-15

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## B3 Result

B3 is closed. `ConfirmedFeeVersionService.confirm()` now evaluates the required V2
generation, payload-fingerprint, and validation-token attestations before a store
write. `pricing_snapshot_json` now carries a backward-compatible V2 envelope with
the server-loaded edited values and full lineage. Currentness and same-lineage retry
matching compare that envelope, so a later generation for the same pricing-draft id
makes the earlier Confirmed Fee stale; Required Forms remains behind its currentness
guard. Matrix Fee automatic confirmation writes the same V2 envelope.

## Blocking Finding

### B4: Production Confirm Fee lookup/create is not transactionally idempotent

The accepted TASK_361L contract requires a serialized Confirmed Fee store transaction
for exact V2-lineage confirmation: it must return the prior version for a duplicate
request and never create a second revision. The production path does not provide that
boundary. `ConfirmedFeeVersionService.confirm()` calls `list_by_project()`, computes
the next revision, and later calls `create()`. `ConfirmedFeeAuthorityRepository.create()`
only adds and flushes the row; it does not begin an immediate transaction, lock the
project confirmation sequence, catch the unique-conflict, or re-read an exact matching
lineage. The only database uniqueness is `(project_id, confirmed_fee_revision)`.

Two concurrent exact V2 confirms can therefore both read an empty/latest-equivalent
version set and calculate the same next revision. One request can fail with a raw
integrity error rather than returning the already-confirmed version. The focused
in-memory idempotency test cannot prove the required production serialization.

**Required bounded Developer fix:**

1. Move the exact-lineage lookup and insert into one production repository/service
   transaction with SQLite write serialization, or use an equivalent atomic
   insert-conflict-reload mechanism. On an exact duplicate, re-read and return that
   version; on a conflicting lineage or summary, return the existing typed conflict.
   Do not expose an `IntegrityError`.
2. Keep the complete V2 envelope comparison established by B3 as the exact identity.
   Preserve the legacy compatibility path only where the accepted TASK_361L contract
   allows it.
3. Add a disposable SQLite repository/API concurrency regression using two sessions
   or an equivalent deterministic interleaving. It must prove one persisted revision,
   an idempotent duplicate result, no raw database error, and no duplicate downstream
   placement. Keep the B3 attestation/currentness and Required Forms regressions
   green.

## Validation Notes

- Directly reviewed the B3 code path, the V2 envelope helper, Required Forms
  composition, Matrix Fee automatic confirmation, the production Confirmed Fee
  repository, model constraint, and dependency composition.
- Re-ran the focused core backend suite: `84 passed`.
- Re-ran Required Forms/Confirmed Fee coverage: `49 passed`.
- Re-ran `npm test -- FeeEvaluationReviewExportPage --run`: `28 passed`, with the
  established React `act(...)` warnings. Candidate `py_compile` passed.
- `git diff --check` and targeted trailing-whitespace checks remain clean apart from
  established LF/CRLF notices. No real database or file was accessed. External
  TASK_361F evidence and TASK_361H artifacts remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded fix pass for B4, then Reviewer
implementation re-gate. Do not route QA or Integrator.

Blocking summary: B3 is fixed, but production Confirm Fee still lacks the serialized
lookup/create boundary required for exact V2 confirmation idempotency.

---

# TASK_361L Reviewer Implementation Re-Gate: B4

Date: 2026-07-15

Role: Reviewer

Status: reviewer_pass

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## Re-Gate Result

B4 is closed. The production `ConfirmedFeeAuthorityRepository` now performs the
revision insert and conflict recovery through `create_or_get_exact()`: an SQLite
revision uniqueness conflict rolls back the failed insert, reloads the persisted
revision, and returns it only when the complete confirmation identity matches. A
different V2 lineage or summary is translated to the typed
`ConfirmedFeeVersionConflictError`, which follows the existing Confirm Fee HTTP 409
path rather than leaking `IntegrityError`.

The complete V2 envelope remains the effective identity: the persisted JSON includes
the server-validated generation, source-context fingerprint, payload fingerprint,
validation token, and values. The service preserves the B3 pre-write attestation,
full-lineage currentness, Required Forms guard, and Matrix Fee automatic-confirm
envelope behavior. No Fee rule/pricing formula/UI, Point Profile/Measurement Plan,
workbook, generic output, parser, LTR/public-drive, or real-data scope expanded.

## Validation Notes

- Directly reviewed the repository/service/retry branch, route conflict mapping,
  V2 envelope identity, dependency transaction boundary, and the disposable
  repository/API regressions. The two-session SQLite case proves a duplicate revision
  returns the original version with one persisted row; a divergent lineage/summary
  produces the typed conflict and retains one row.
- Re-ran the full focused TASK_361L backend pricing/consumer/export/rebase suite:
  `87 passed`.
- Re-ran Required Forms, Confirmed Fee, and API coverage: `50 passed`.
- Re-ran `npm test -- FeeEvaluationReviewExportPage --run`: `28 passed`, with only
  the established React `act(...)` warnings.
- Focused `py_compile` and `npm run build` passed; build emitted only the established
  Vite chunk-size warning. `git diff --check`, trailing-whitespace, line-count, and
  locked-scope/no-real-data scans passed apart from established LF/CRLF notices.
  Candidate Python files remain under the 500-line hard limit.
- No real database or file was accessed; no staging, commit, or push occurred.
  Existing TASK_361F evidence and TASK_361H artifacts remain excluded.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate. QA should run the declared disposable
SQLite/API and controlled Fee page/browser smoke, including the `15`/`9` LLCR display,
old saved Units `1` suppression, V2 currentness/Required Forms guard, and Confirm
duplicate/conflict behavior. Do not route Integrator directly.

Blocking summary: none for Reviewer implementation re-gate.

---

# TASK_361L Reviewer Focused Implementation Re-Gate: Integrator Line-Count Split

Date: 2026-07-16

Role: Reviewer

Status: reviewer_blocked

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

## Blocking Finding

### B5: The physical Python line counts still exceed the AGENTS hard limit

The helper extraction and V2 test relocation are mechanically coherent, and the two
API modules pass together. However, the claimed `495`/`494` counts are not physical
source-line counts: they result from a pipeline that suppresses blank lines. Reading
the checked-out UTF-8 files shows:

- `backend/api/routes_confirmed_matrix_fee_evaluation_export.py`: `542` lines;
- `tests/integration/test_fee_evaluation_pricing_draft_api.py`: `556` lines;
- `backend/api/fee_evaluation_pricing_draft_http.py`: `31` lines;
- `tests/integration/test_fee_evaluation_pricing_draft_v2_api.py`: `228` lines.

The first two remain over the `AGENTS.md` 500-line Python hard limit. The Integrator
blocker therefore remains open, despite the nonblank-line count of the committed Git
blob being below 500. The exact working-tree physical-line measurement, including
blank lines, is the applicable maintainability gate.

**Required bounded Developer fix:**

1. Further split the export route and the historical pricing-draft API test module so
   each checked-out Python file is at or below 500 physical UTF-8 lines. Keep route
   coordination, request DTO/API behavior, and V2 regression semantics unchanged.
2. Use a physical-line check that includes blank lines for every TASK_361L candidate
   Python file, and record that command/result in Developer evidence.
3. Re-run the two API modules together, focused compile/diff/trailing/locked-scope
   checks, and preserve the already-passed QA behavior package. Do not re-run QA until
   this structural blocker is actually closed.

## Validation Notes

- Directly reviewed the `411a5f59` helper extraction and V2 API-test move. The
  attestation DTO/error mapping is self-contained, and the three moved historical
  API tests retain their assertions in the dedicated V2 module.
- Re-ran both pricing-draft API modules together: `14 passed`.
- Focused `py_compile` for the export route, helper, and pricing-draft route passed.
- A direct UTF-8 physical-line scan reported the above `542`/`556` counts. The
  Developer's Git-pipeline count reports `495`/`494` because blank output lines are
  suppressed; it is not a valid hard-limit check.
- QA evidence remains `qa_pass` and Integrator evidence remains `integrator_blocked`.
  This fix is structural-only, but it does not close the stated packaging gate yet.
  No real database/file was accessed and no product code was changed by Reviewer.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded fix pass for B5, then Reviewer
focused implementation re-gate. Do not route QA or Integrator.

Blocking summary: the mechanical split is sound, but the actual route and historical
API test module still exceed the 500-line hard limit.
