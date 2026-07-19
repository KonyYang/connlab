# TASK_363C Developer Evidence

Date: 2026-07-18

Role: Developer

Status: `implementation_complete / ready_for_reviewer_implementation_gate`

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Phase And Dependency Gate

This is a docs-only Developer planning-first pass. TASK_364B remains the current
implementation lane with R1 work pending Reviewer/QA and user acceptance. TASK_363C
product implementation is not authorized and remains deferred until TASK_364B is
accepted or a later explicit isolated scheduling decision is reconciled.

## Repository Facts Reconciled

- `confirmed_matrix_fee_step_quantities.py` currently builds shared contexts and the CR
  path still requires legacy Step quantity before effective Measurement Plan lookup.
- `contact_measurement_plan_confirmed_consumer_adapter.py` exposes exact target identity,
  contact kind, inclusion/coverage state, readings, revision lineage, and diagnostics.
- `fee_reviewed_extension_defaults.py` currently permits CR text fallback and uses the
  fixed 10-per-reading result; the >10 tier is not selected from confirmed CR authority.
- `confirmed_matrix_fee_draft_service.py` is 459 physical lines and is locked except
  for a future narrow CR routing hunk after red assembly tests pass.
- V2 pricing-draft source context already carries Measurement Plan revision/fingerprint
  and automatic-default currentness; this lane plans regression coverage, not composition
  or DTO/API-client changes.
- TASK_364B CR coverage is Point Profile UI behavior, not Fee Units authority.

## Frozen Implementation Strategy

1. Red-test a bounded target-first CR helper for exact Group/row/step/suffix and
   `cr_specified_current`, status/inclusion/affected/lineage, homogeneous multi-step
   behavior, and all no-fallback states.
2. Red-test two Groups with readings 8/12 and samples 5/3, conflicting legacy Step and
   Point Profile facts, expecting Units 40/36 and tier prices 10/5. A locked service
   failure routes to Planner; it is not fixed by expanding this lane.
3. Red-test CR-only default behavior, invalid sample quantity, missing/wrong-kind target,
   not-started/disabled/corrupt states, and V2 stale/rebase manual preservation.
4. In a later authorized implementation pass, add only the bounded helper, narrow CR
   service branch, and CR-only default logic. LLCR/shared step quantity behavior stays
   unchanged.

## May Touch / Locks

Future May Touch: the new bounded CR application helper, one narrow
`confirmed_matrix_fee_draft_service.py` routing hunk, CR-only default result logic,
three bounded CR test modules, and TASK_363C governance/evidence.

Locked/read-only: `confirmed_matrix_fee_step_quantities.py`, `backend/api/dependencies.py`,
Measurement Plan and Point Profile schema/repository/lifecycle/API/UI, TASK_364B,
Fee seeds/manifest, frontend/API client/DTOs, workbooks/generic outputs, parser/import,
LTR/public drive, real DB/files, `.agents/**`, `docs/project_management/**`, release/dist,
remote push, and all external residuals.

## Validation Plan

- Focused helper, two-Group assembly, CR default, no-fallback, and V2 rebase tests.
- Read-only LLCR/non-CR/consumer regression suites.
- `py_compile` for touched backend modules.
- Physical UTF-8 line count for every new helper/test module, preserving blank lines.
- `git diff --check`, UTF-8 trailing whitespace, exact whitelist, seed-lock,
  forbidden-scope, and no-real-mutation scans.

No product code, schema, API client, test implementation, database, real file, staging,
commit, or push action occurred in this planning-first pass.

## Next Legal Role

Reviewer implementation-readiness gate.

## Implementation Pass Evidence

Date: 2026-07-19

Status: `ready_for_reviewer_implementation_gate`

Implemented only the bounded CR specified-current consumer path:

- Added `backend/application/confirmed_matrix_fee_cr_specified_current.py` as a
  target-first resolver for exact Group/row/step/suffix and
  `cr_specified_current` targets.
- CR resolution accepts only `complete`, `partial_compatible`, or `needs_review`
  exact targets with included coverage, positive finite readings, homogeneous
  readings/source lineage, and no effective-plan diagnostics. Missing,
  not-started, disabled, excluded, wrong-kind, invalid, divergent, or diagnosed
  authority becomes typed review-required context.
- `ConfirmedMatrixFeeDraftService` now uses the resolver only for the CR rule;
  LLCR and all other rule paths retain their existing quantity behavior.
- CR default-fill uses owning Group sample quantity, selects 10 per reading for
  readings <= 10 and 5 per reading above 10, and does not use Point Profile,
  legacy Step quantity, or Matrix prose in the production CR branch. Existing
  direct legacy default-fill callers remain compatibility-only; production CR
  assembly always passes the target-first context.
- No schema, seed, API DTO/client, frontend, workbook, TASK_364B, or real-file
  changes were made by this pass.

Focused test nodes:

- `tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py`:
  12 passed, including exact target resolution, status/kind/exclusion/diagnostic
  blockers, homogeneous multi-step behavior, two-group 8 x 5 and 12 x 3
  production assembly (40 at 10/reading and 36 at 5/reading), missing-plan
  no-fallback, and invalid sample quantity.
- CR/default-fill/confirmed draft/Step quantity regression subset: 106 passed.
- V2 pricing draft rebase/persistence plus CR-focused regression subset: 152 passed.
- Isolated `tests/unit/test_fee_default_fill.py`: 77 passed. The combined
  cross-lane command once exposed the existing order-sensitive Salt Spray
  failure; the node passes in isolation and no Salt Spray code is part of this
  lane.
- `py_compile` passed for all four touched backend modules.
- Physical UTF-8 line counts: CR helper 100, Fee draft service 499, default-fill
  models 81, reviewed defaults 320, focused test module 326.
- UTF-8 trailing-whitespace scan was clean; `git diff --check` passed with only
  the repository's existing LF/CRLF notices.

Known excluded-worktree residual:

- The existing LLCR API regression
  `test_fee_draft_api_uses_confirmed_point_profile_for_llcr_units` remains
  failing in the current TASK_361K/Point Profile residual package (`units` is
  `None`). The TASK_363C diff does not change the LLCR branch or Point Profile
  composition, so it was not modified under this lane.

No staging, commit, push, real database/file access, or next-role routing was
performed. Recommended next role: Reviewer implementation re-gate.

## B3/B4 Bounded Fix Checkpoint

Date: 2026-07-19

Status: `blocked_pending_re_scope`

- Rewrote the two pre-existing direct CR default-fill nodes in
  `tests/unit/test_fee_default_fill.py` so missing typed CR authority is
  explicitly `review_required` with `unit_price`, `units`, and `testing_fee`
  unset. The full file now passes: 77 passed.
- Added a disposable persistence-composition probe for the requested saved V2
  draft plus changed Measurement Plan lineage. The probe showed the current
  production `load_rebase_candidate()` returns `blocked` when the saved and
  current Measurement Plan revision/fingerprint differ, because the existing
  `_same_non_rule_lineage()` gate treats that change as a non-rebaseable
  authority change. It therefore cannot truthfully assert the requested
  `rebase_required` -> reviewed persistence path without changing locked V2
  production logic.
- The probe was removed after diagnosis; no production code was changed and
  no failing test was left in the candidate. This is a production-contract
  mismatch requiring Planner/Reviewer re-scope, not a fixture workaround.

Blocked next action: reconcile whether Measurement Plan lineage changes are
allowed to enter reviewed rebase. Current code fail-closes them as `blocked`,
while the B4 acceptance requirement asks for `rebase_required` and persisted
reviewed values. No Reviewer re-gate is recommended until that boundary is
resolved.

## B1/B2 Reviewer Re-gate Fix Evidence

Date: 2026-07-19

Status: `ready_for_reviewer_implementation_re_gate`

- Replaced the generic CR Step context as an authority carrier with typed
  `CrSpecifiedCurrentAuthority`, including exact Group/Row/Step/Suffix identity,
  `cr_specified_current` kind, readings, revision id/sequence, deterministic
  Measurement Plan fingerprint, and diagnostic/current validity.
- CR default-fill now requires `context.cr_authority.is_valid`; generic
  `FeeStepQuantityContext`, legacy Step quantity, Matrix prose, Point Profile,
  wrong target, missing lineage, disabled/not-started/stale/corrupt/affected
  authority cannot calculate Units or Testing Fee.
- Added the required API module
  `tests/integration/test_confirmed_matrix_fee_cr_specified_current_api.py`.
  It proves the production Fee draft route returns 40 at 10/reading and 36 at
  5/reading, and returns review/no Units/no Testing Fee for invalid owning
  quantity and missing target.
- Added the required V2 module
  `tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py`.
  It proves Measurement Plan lineage fingerprint changes are visible and
  reviewed rebase refreshes CR Units/Testing Fee while retaining manual price
  and discount fields.
- Bounded unit + API + V2 modules: 33 passed. Added missing revision-lineage
  regression: included in the 13 unit tests.
- Read-only confirmed-draft/Step-quantity/V2 persistence regression subset:
  39 passed.
- `py_compile` passed for all touched backend and integration test modules.
- Physical UTF-8 line counts: CR helper 128, Fee draft service 500, fee models
  110, reviewed defaults 285, unit module 339, API module 80, V2 module 69.
- `git diff --check` and trailing-whitespace checks are clean apart from the
  repository's existing LF/CRLF notices.

The two old direct CR assertions in the pre-existing 728-line
`tests/unit/test_fee_default_fill.py` still expect the removed generic Step
fallback/default price behavior; they are intentionally not restored because
they contradict the approved no-fallback contract and the file is outside the
bounded test-module ownership. No staging, commit, push, real DB/file access,
or external-lane modification occurred.

## Renewed TASK_363D Dependency Replay

Date: 2026-07-19

Status: `implementation_complete / ready_for_reviewer_implementation_gate`

Accepted baseline: TASK_363D commit
`754b79bc7370e4cecd4fc01dd576e6e7e67080fc`.

### Implemented

- Replayed the bounded target-first CR resolver and typed
  `CrSpecifiedCurrentAuthority`. Exact Group/row/Step/suffix, contact kind,
  readings, revision id/sequence, fingerprint, and diagnostic state now travel
  together into CR default-fill.
- Missing or malformed effective-plan lineage now returns typed
  review-required context instead of raising `AttributeError`; legacy/minimal
  adapters cannot recover through Step quantity, prose, or Point Profile.
- CR default-fill calculates only from valid exact authority and owning Group
  sample quantity: 8 x 5 = 40 at 10/reading and 12 x 3 = 36 at 5/reading.
- Production CR field metadata uses the deterministic confirmed CR Measurement
  Plan lineage for Unit Price, Unit Type, Units, and Testing Fee. The external
  Base Fee policy remains unchanged.
- Replaced the disconnected B4 probe with a disposable SQLite production flow:
  saved attested V2 generation 1, changed confirmed CR authority, visible
  `rebase_required`, current confirmed Fee draft rebuild, reviewed CAS save to
  generation 2, reload as `current_v2`. Automatic Units/Testing Fee refresh to
  36/180 while manual Unit Price 99 and discount 15 remain intact.
- Added an unsafe-current-target regression proving a missing current CR target
  returns `blocked` and leaves the persisted generation/payload unchanged.
- Updated only the two authorized B3 nodes in
  `tests/unit/test_fee_default_fill.py`; their combined TASK_363C hunk is net
  three physical lines smaller and does not contribute to that mixed legacy
  module's existing size excess.

### Validation

- TASK_363C bounded unit/API/V2/B3 nodes: `21 passed`.
- Full direct default-fill regression module: `77 passed`.
- Shared confirmed-draft, Step-quantity, TASK_363D attestation, V2 persistence,
  transition, compatibility, and export suites: `92 passed, 1 deselected`.
- The deselected node was also run directly and fails only because the locked
  read-only test
  `test_specified_current_contact_resistance_never_uses_llcr_fallback` expects
  legacy automatic Unit Price `10` under `not_started`; the approved B3/no-
  fallback contract requires Unit Price, Units, and Testing Fee all unset. No
  product fallback was restored and the locked test was not edited.
- `py_compile` passed for all TASK_363C product and focused test modules.
- Physical UTF-8 line counts (blank lines preserved): CR helper 148, mixed Fee
  draft service 486, default-fill models 118, reviewed defaults 281, package
  export 89, unit module 358, API module 79, V2 integration module 241. All
  TASK_363C product/new test modules are below the 500-line hard limit.
- Tracked and no-index `git diff --check` passed with only existing LF/CRLF
  notices; UTF-8 trailing-whitespace scan is clean.
- No TASK_363C candidate file is staged. The global index currently contains an
  external TASK_365C package; it was not changed, cleared, or attributed to this
  lane. `data/**`, Fee seeds/manifest, and TASK_363D automatic-build,
  attestation, persistence, transition-policy, dependency-composition files have
  no worktree changes. No real DB/file access, frontend/API-client change,
  TASK_363C stage, commit, or push occurred.
- Frontend build was not run because this backend-only lane did not touch
  frontend or API-client code.

### Package Isolation

`confirmed_matrix_fee_draft_service.py` remains a mixed worktree file. Only the
exact CR routing/lineage hunks belong to TASK_363C; external Base Fee and rule-
resolution hunks must remain excluded by any later package owner. TASK_363D
production attestation files are unchanged and remain the read-only baseline.

## Next Legal Role

Reviewer implementation gate. The Reviewer must explicitly reconcile the one
locked stale CR fallback assertion above; this Developer pass cannot modify it
without expanding the exact test ownership approved for TASK_363C.

## B6 Tests-Only Fix Pass

Date: 2026-07-19

Status: `ready_for_reviewer_implementation_re_gate`

- Migrated only
  `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py::test_specified_current_contact_resistance_never_uses_llcr_fallback`.
- The node now asserts `review_required`, leaves Unit Price, Units, and Testing
  Fee unset, and requires a business-readable confirmed CR Measurement Plan
  authority reason. No fallback or production behavior changed.
- Exact B6 node: `1 passed`.
- Owning shared profile-consumer module: `9 passed`.
- TASK_363C CR/API/B4 plus full default-fill suite: `96 passed`.
- TASK_363D automatic-build, attestation, Measurement Plan transition, and
  integration rebase suite: `27 passed`.
- The shared test file remains 223 physical UTF-8 lines, exactly matching HEAD;
  its B6 diff is 3 additions and 3 deletions.
- `git diff --check` passed with only the existing LF/CRLF notice; UTF-8 trailing
  whitespace is clean. No TASK_363C candidate file is staged.
- This pass changed no production file or other test node and did not access a
  real database/file, stage, commit, push, or modify the external TASK_365C
  package.

Recommended next role: Reviewer implementation re-gate only.
