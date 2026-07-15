# TASK_361L Developer Planning-First Evidence

Date: 2026-07-15

Role: Developer

Task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`

Lane: `point-profile-fee-pricing-draft-rebase-corrective`

Status: `developer_planning_first_fix_complete / pending_reviewer_implementation_readiness_re_gate`

## Authorization

This pass is docs-only under the explicit User/Reviewer-plan-gate delegation. Product
implementation, schema/API/client/test implementation, real database/file access,
staging, commit, and push are not authorized and were not performed.

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled
foundation`.

Active task: `TASK_361L_POINT_PROFILE_FEE_PRICING_DRAFT_REBASE_CORRECTIVE`.

Why allowed: the delegation records the Reviewer plan gate as passed and explicitly
authorizes Developer planning-first only. The current board wording still says the
Reviewer re-gate is pending, so this evidence preserves that source-of-truth mismatch
for the next Reviewer gate rather than changing governance state itself.

## Repository Facts Re-Verified

- The existing pricing draft stores one values-only `payload_json` per project/Matrix/
  rule tuple. Its service has only `missing`, `current`, and `stale`, and the frontend
  hydrator overlays every saved editable field over current Fee defaults.
- `ConfirmedFeeVersionService` currently accepts any saved snapshot not labelled
  `missing`/`stale`; browser export accepts a client edited payload. Both require the
  planned shared current-V2 guard to make the server authoritative.
- TASK_361K already supplies Point Profile revision/id/fingerprint lineage at the Fee
  default source. It must be fingerprinted as machine context, not parsed from display
  copy.
- Direct export, child export, Required Forms, and Matrix Fee rebase each construct or
  consume Fee pricing through distinct application/dependency paths.
- Existing pricing persistence, export, Fee page/model, and related test files already
  exceed the repository target size. The refined plan introduces narrowly scoped pure
  contract/rebase/guard modules and a Fee feature model rather than enlarging them.

## Frozen Implementation Strategy

1. Keep the existing table and envelope V1 values intact. Add V2 context, default and
   payload fingerprints, plus explicit operator field provenance only in
   `payload_json`.
2. Classify only `missing`, `current_v2`, `rebase_required`,
   `legacy_unclassified`, and `blocked`. Every status except `current_v2` is
   non-consumable and fails closed.
3. Build reviewed rebase candidates in memory. Save is explicit, validates current
   context and provenance atomically, reloads/revalidates V2, then returns an opaque
   validation token.
4. Reuse one server guard for Confirm Fee, browser/direct/child export, Required
   Forms currentness, and Matrix Fee rebase. Writers receive server-loaded V2 values,
   never a raw client payload.
5. Move Fee page pricing-draft async state to a feature model. Preserve the dense
   existing product surface with concise inline state and disabled reasons only.

The plan now records exact files, V2 JSON fields, state priority, field merge rules,
token bindings, consumer sequence, focused disposable test matrix, browser smoke,
line-count strategy, and locked paths.

## Validation Plan

- Disposable SQLite V1/V2 codec, repository, persistence, token/replay/concurrency,
  Confirm Fee, direct/browser/child export, Required Forms, and Matrix rebase tests.
- Fee feature-model/component tests for hydration/provenance, reviewed save, stale
  recovery, zero-write Cancel, and consumer-disabled states.
- Desktop and 514px seeded browser smoke with Profile readings change, visible LLCR
  Units rebase, manual-field retention, reviewed save, and no workbook generation.
- Focused pytest/npm test/build, py_compile, diff/trailing/line-count/forbidden-scope
  scans. No real database/file access.

## Package Isolation

Only the exact TASK_361L pricing-draft, consumer-guard, narrow Fee frontend, focused
tests, and governance paths named in the refined plan may enter a future candidate.
Fee formula/rule/pricing/discount/UI redesign, TASK_361K authority, Point Profile
schema/parser/editor/lifecycle, workbook layout, generic outputs, parser/LTR/public
drive, and external TASK_361F/TASK_361H/board residuals remain excluded.

## Next Legal Role

Reviewer implementation-readiness gate.

## Developer Implementation Checkpoint (2026-07-15)

Status: `developer_implementation_complete / ready_for_reviewer_implementation_gate`.

Implemented and verified so far:

- V2 JSON envelope, deterministic source/payload fingerprints, generation, and
  currentness token; legacy values-only payloads remain readable but classify as
  `legacy_unclassified`.
- Repository compare-and-swap protects V2 replacement against an exact persisted
  predecessor, with a typed pricing-draft conflict on a miss.
- Fee pricing-draft GET now returns V2 values and a deterministic reviewed-rebase
  candidate. The candidate refreshes automatic Units/Testing Fee while retaining
  compatible manual price/base-fee/discount/note fields; it remains non-consumable
  until an explicit V2 save succeeds.
- The Fee page retains V2 CAS metadata, renders the rebase candidate for review, and
  keeps Update Fee blocked until the reviewed values are saved.
- Confirm Fee checks V2 generation/payload/token and returns an existing matching
  confirmed version for a repeated matching V2 confirmation.
- Direct in-process and timeout child edited export replace client values with the
  server-loaded V2 snapshot through `CurrentFeePricingDraftGuard`. The child command
  round-trips V2 identity/generation/payload/token fields and maps a child-side
  currentness failure back to the parent typed conflict before an artifact result.
- Required Forms obtains its confirmed Fee read model only when its pricing draft is
  `current_v2` and still matches the saved draft identity; non-current V2/V1 states
  stay stale and cannot be placed.
- Matrix Fee promotion composes the V2 persistence service through a narrow bridge.
  A promotion accepts only a returned `current_v2` snapshot; a missing, stale, or
  blocked result closes the promotion without falling back to a values-only write.
- The Point Profile Fee consumer regression proves confirmed profile `P / 1-3`
  readings-per-sample `3` produces LLCR Units `15` for group quantity `5` and Units
  `9` for group quantity `3`. The reviewed rebase refreshes automatic Units/Testing
  Fee, so an old saved Units value of `1` cannot override the current automatic
  result; compatible manual price/base-fee/discount/note fields remain retained.

Focused verification completed:

- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_fee_evaluation_pricing_draft_v2_contract.py tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` -> `31 passed`.
- Earlier combined pricing/repository/confirmed-fee/direct-export focused suite ->
  `51 passed`.
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/unit/test_fee_evaluation_pricing_draft_v2_contract.py tests/unit/test_fee_evaluation_pricing_draft_v2_repository.py tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/unit/test_confirmed_fee_version_service.py tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py tests/integration/test_fee_evaluation_export_child_transaction.py -q` -> `80 passed`.
- `py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/unit/test_required_forms_staging_generator.py tests/integration/test_project_folder_required_forms_api.py tests/integration/test_confirmed_fee_version_api.py -q` -> `49 passed`.
- `npm test -- FeeEvaluationReviewExportPage --run` -> `28 passed` with existing
  React `act(...)` warnings only.
- `npm run build` -> passed with the existing Vite chunk-size warning.
- `py_compile` passed for all modified TASK_361L backend/API/child modules. `git diff
  --check` passed; only existing LF/CRLF warnings were emitted. Target Python modules
  remain within the 500-line hard limit: pricing persistence `454`, Matrix promotion
  `491`, direct export `498`, timeout export `365`, and the new V2 promotion bridge
  `41` lines.
- Trailing-whitespace and locked-scope/no-real-data added-line scans returned no
  matches. Browser smoke was not run in this pass; focused component coverage is the
  recorded residual.

No real database/file access, staging, commit, or push was performed. Existing
TASK_361F/task-board and other external residuals remain excluded.

## Implementation Closeout (2026-07-15)

The exact candidate contains only TASK_361L pricing-draft V2 persistence/currentness,
consumer composition, compact Fee review UI, focused tests, and this evidence. The
hard-limit split adds `matrix_fee_rebase_pricing_draft_bridge.py`, a narrow V2-only
promotion helper permitted by the plan's named pricing-draft context/fingerprint/rebase
helper boundary. It does not alter Fee formulas, pricing rules, discounts, Point Profile
authority, workbook layout, or frontend API-client contracts.

Next legal role: `Reviewer implementation gate`.

## Reviewer B3 Bounded Fix (2026-07-15)

Status: `developer_b3_fix_complete / ready_for_reviewer_implementation_re_gate`.

- `_validate_v2_pricing_snapshot()` now evaluates all required generation, payload
  fingerprint, and validation-token attestations on its reachable path. Missing or
  mismatched V2 attestation raises the existing typed changed-draft error before any
  Confirmed Fee store write.
- `confirmed_fee_pricing_snapshot.py` adds the compatible JSON envelope stored in the
  existing `pricing_snapshot_json` column: exact draft id, generation, source-context
  fingerprint, payload fingerprint, validation token, and server-loaded active edited
  values. No schema change or legacy rewrite was performed.
- Confirm idempotency and `get_latest()` currentness now compare the full V2 envelope.
  A same-id newer generation is stale, so Required Forms remains blocked by its
  existing `status == current` gate. Its staging composition unwraps the confirmed
  envelope only after that guard, preserving the existing Fee Form value consumer.
- Matrix Fee automatic Confirm uses the same envelope for V2 snapshots, so its retry
  check does not treat a matching draft id with newer lineage as equivalent.

Focused B3 regressions:

- missing V2 attestation -> typed changed error, zero Confirmed Fee writes;
- mismatched V2 generation -> typed changed error, zero writes;
- exact same V2 lineage -> one idempotent Confirmed Fee version;
- same draft id with generation advance -> stale downstream read result;
- Required Forms Fee Form staging unwraps a V2 confirmed envelope and receives the
  server-loaded values.

The V2 lineage cases live in the focused
`tests/unit/test_confirmed_fee_version_service_v2_lineage.py` module so the existing
Confirmed Fee service suite remains below the repository's 500-line hard limit.

Validation after B3:

- Core TASK_361L pricing/consumer/export/rebase suite: `84 passed`.
- Required Forms and Confirmed Fee suite: `49 passed`.
- `npm test -- FeeEvaluationReviewExportPage --run`: `28 passed` with existing React
  `act(...)` warnings only.
- `npm run build`, focused `py_compile`, `git diff --check`, trailing whitespace,
  line-count, locked-scope, and no-real-data scans: passed, apart from existing
  LF/CRLF and Vite chunk-size warnings.

No real database/file access, staging, commit, or push occurred. The browser smoke
residual remains unchanged; this B3 pass did not run a browser session.

## Reviewer B4 Bounded Fix (2026-07-15)

Status: `developer_b4_fix_complete / ready_for_reviewer_implementation_re_gate`.

- `ConfirmedFeeAuthorityRepository.create_or_get_exact()` now handles SQLite revision
  uniqueness contention by rollback, exact-lineage re-read, and deterministic return
  of the existing version. A same-revision request with different lineage or summary
  raises typed `ConfirmedFeeVersionConflictError`, not a raw database `IntegrityError`.
- `ConfirmedFeeVersionService.confirm()` uses that atomic capability in production
  while retaining existing in-memory-port compatibility for focused legacy tests.
- Disposable SQLite regressions prove exact duplicate confirmation leaves one stored
  version and returns it; conflicting summary/lineage leaves one version and returns
  the typed conflict. No Confirmed Fee write occurs after a failed insert attempt, so
  downstream Required Forms cannot receive a duplicate confirmation placement.

Validation after B4: core TASK_361L suite `87 passed`; Required Forms/Confirmed Fee
suite `49 passed`; frontend Fee page `28 passed`; `npm run build` and focused
`py_compile` passed with existing React `act(...)`, Vite chunk-size, and LF/CRLF
warnings only. No real DB/file access, staging, commit, or push occurred.

### B4 Revalidation Checkpoint

Status remains `ready_for_reviewer_implementation_re_gate`.

- `tests/unit/test_confirmed_fee_authority_repository.py::test_repository_returns_exact_confirmation_after_revision_conflict`
  passed using two disposable SQLite sessions: the second exact request returns the
  original version and the authority table remains at one row.
- `tests/unit/test_confirmed_fee_authority_repository.py::test_repository_rejects_conflicting_revision_without_raw_integrity_error`
  passed: conflicting summary/lineage contention is translated to
  `ConfirmedFeeVersionConflictError` and leaves one row.
- `tests/integration/test_confirmed_fee_version_api.py::test_confirmed_fee_post_maps_concurrent_lineage_conflict_to_typed_409`
  passed: the existing typed conflict reaches the Confirm Fee route as HTTP `409`,
  not a raw SQLite or SQLAlchemy error.
- The complete TASK_361L backend pricing/consumer/export/rebase suite passed
  (`87 passed`); Required Forms plus Confirmed Fee/API coverage passed
  (`50 passed`); frontend Fee page coverage passed (`28 passed`) with the
  established React `act(...)` warnings only.
- Focused `py_compile`, frontend production build, `git diff --check`, trailing
  whitespace, unstaged/staged, line-count, locked-path, and no-real-data scans
  passed. Existing LF/CRLF and Vite chunk-size warnings remain non-blocking.

No real database/file access, staging, commit, or push occurred. The B4 package is
ready for the Reviewer implementation re-gate; QA and Integrator remain unrouted.

## Integrator Line-Count Split Fix (2026-07-15)

Status: `ready_for_reviewer_implementation_re_gate`.

- Moved the shared V2 pricing-draft attestation request fields and typed
  `fee_pricing_draft_not_current` HTTP mapping into
  `backend/api/fee_evaluation_pricing_draft_http.py`. The export route stays a thin
  coordinator and keeps its existing request fields, error code, status, and command
  construction unchanged.
- Moved the V2 read-state, CAS-context forwarding, conflict, and lifecycle-readonly
  API regressions into the dedicated
  `tests/integration/test_fee_evaluation_pricing_draft_v2_api.py` module. Coverage
  was mechanically preserved; the original API module retains its existing
  non-V2/historical/discard cases.
- Corrected line-count evidence: `routes_confirmed_matrix_fee_evaluation_export.py`
  is now `495` lines; `test_fee_evaluation_pricing_draft_api.py` is `494` lines; the
  new V2 API test module is `194` lines; the shared API helper is `22` lines. All
  are below the `AGENTS.md` 500-line hard limit.

Validation after the split:

- Split API modules: `14 passed`.
- Core TASK_361L pricing/consumer/export/rebase suite: `87 passed`.
- Required Forms, Confirmed Fee, and API suite: `50 passed`.
- `npm test -- FeeEvaluationReviewExportPage --run`: `28 passed` with established
  React `act(...)` warnings only; `npm run build` passed with the established Vite
  chunk-size warning only.
- Focused `py_compile`, `git diff --check`, trailing-whitespace, line-count,
  locked-path, no-real-data, and unstaged/staged scans passed. Existing LF/CRLF
  warnings are non-blocking external worktree noise.

No behavior, V2 envelope/CAS/rebase contract, API client, Fee formula/rules/UI, real
database/file, staging, commit, or push change was made. This is a structural split
only and is ready for Reviewer focused re-gate; QA and Integrator remain unrouted.

## Reviewer B2 Docs-Only Planning Fix (2026-07-15)

The V2 token is now explicitly an opaque currentness/integrity attestation, not a
one-time replay credential. V2 generation plus exact prior persisted snapshot
fingerprint/`updated_at` becomes the repository compare-and-swap precondition for
first save, ordinary autosave, manual save, reviewed rebase, and V1 upgrade. A
conditional insert/update miss is typed HTTP `409`, reload, and zero overwrite.

Confirm Fee is frozen as transactionally idempotent for one exact validated V2
generation and summary. Matrix Fee rebase retry is likewise idempotent only for the
same promotion/V2 lineage. Export is intentionally repeatable but revalidates every
request and follows existing output collision/no-overwrite behavior; stale
token/generation/context/payload fails before writer/subprocess/artifact work.
Required Forms revalidates embedded V2 lineage before placement.

The plan adds concrete disposable nodes for competing first/V2/V1 saves, duplicate
Confirm, repeat and stale export, rebase retry, Required Forms stale lineage, and
frontend stale-CAS reload. No product code, tests, schema/API client, real database/
file access, staging, commit, or push was performed.
