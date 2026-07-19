# TASK_363C Reviewer Plan Gate

Date: 2026-07-18

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Plan Review

The proposed authority chain is sufficiently narrow and matches the checked-out
implementation gap. The current shared step-quantity builder first requires a legacy
`ConfirmedMatrixStepQuantity` before looking up an effective Measurement Plan target.
The current CR default result then falls back to source text and holds the fixed
10-per-reading amount. TASK_363C correctly replaces only the specified-current CR
path with target-first confirmed authority and retains LLCR's accepted behavior.

The frozen formula and target identity are explicit: exact confirmed Group, row, Step
sequence, and normalized suffix; included usable `cr_specified_current` target
readings multiplied by only the owning Group sample quantity. Multiple steps must be
homogeneous rather than summed. Missing, disabled, stale, affected, wrong-kind,
excluded, corrupt, divergent, invalid, and legacy-only inputs all resolve to typed
review-required without automatic Units or Testing Fee. The `10` through `>10` tier
boundary and manual Base Fee policy are both testable and remain separate.

## Scope And Dependency Review

The planned bounded CR helper, narrow service routing, CR-only default-fill branch,
and three focused tests are appropriate. The 459-line Fee draft service remains below
the hard limit only if the detailed selection logic lives in the new helper. Shared
step-quantity, Measurement Plan lifecycle/storage/API/UI, Point Profile/TASK_364B,
seeds, frontend/API client, workbooks, parser, LTR/public drive, real DB/files, and
composition root are correctly locked.

The V2 pricing-draft plan preserves existing Measurement Plan fingerprint/revision
currentness and requires rebase coverage without changing persistence composition.
The plan includes no silent fallback and no broad CR/LLCR consumer migration.

`TASK_364B` remains the board's current implementation lane. This pass authorizes no
TASK_363C product work: TASK_363C implementation must wait for TASK_364B acceptance
or an explicit user-approved isolated ordering with board reconciliation.

## Validation

- Read AGENTS, board, task, plan, Planner evidence, review checklist, discovery
  protocol, current CR default-fill path, shared step-quantity builder, confirmed
  Measurement Plan consumer boundary, and V2 authority-context code.
- Confirmed the planned helper/tests do not yet exist and this is a planned-only
  governance package.
- Verified current relevant physical line counts: Fee draft service 459, shared
  quantity builder 204, confirmed Measurement Plan adapter 94, default-fill 264, and
  dependency root 1960.
- Governance diff check and UTF-8 trailing-whitespace scans are clean; staged index is
  empty. Existing TASK_364B/frontend/API and other dirty worktree residuals remain
  excluded.

## Decision

`reviewer_pass`

Recommended next role/action: User approval for a Developer planning-first pass only.
Product implementation must remain deferred until TASK_364B is accepted or the user
explicitly approves an isolated sequence and Planner reconciles the board.

Blocking summary: none for the TASK_363C plan gate.

---

# TASK_363C Reviewer Implementation-Readiness Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Readiness Review

The task, plan, Planner/Developer/reconciliation evidence, and board are aligned:
Reviewer plan gate passed, the user approved Developer planning-first, Developer made
only docs changes, and the user-recorded isolated progression from TASK_364B remains
non-executable until final authorization reconciliation.

The implementation is sufficiently concrete and remains bounded:

- a new target-first CR helper resolves exact confirmed Group/row/sequence/suffix
  `cr_specified_current` authority, including status, inclusion, kind, lineage, and
  homogeneous multi-token validation;
- one narrow CR-only branch in the 459-line Fee draft service routes to that helper;
- a CR-only default result removes text/legacy fallback and selects the `10` / `5`
  per-reading tier from confirmed readings;
- three new bounded tests cover helper authority, API two-Group behavior, and V2 stale
  rebase/manual-field preservation.

The no-fallback and failure contracts are explicit: CR cannot use Point Profile,
source text, legacy Step quantities, LLCR/wrong targets, or another Group. Missing,
disabled, stale, corrupt, omitted, excluded, affected, wrong-kind, divergent, and
invalid inputs remain typed review-required with no automatic Units or Testing Fee.
Base Fee range and temperature-rise waiver stay manual.

## Scope And Validation

- Re-read current CR default-fill, shared quantity builder, confirmed Measurement Plan
  adapter, Fee draft assembly, V2 authority-context/currentness code, task/plan, board,
  and all planning evidence.
- Confirmed the root cause: shared assembly first requires a legacy Step quantity;
  CR default fill can parse text and keeps the fixed 10 price. The proposed helper and
  CR-only branch address this without modifying the shared LLCR path.
- Confirmed current physical lines: Fee draft service 459, shared builder 204,
  Measurement Plan adapter 94, default-fill 264, and dependency root 1960. The new
  helper and three test modules do not yet exist.
- Governance diff/trailing checks are clean; staging is empty. No backend/frontend/
  schema/API-client/test implementation or real DB/file operation occurred in this
  planning-first pass. TASK_364B and all dirty residuals remain excluded.

## Decision

`reviewer_pass`

Recommended next role/action: User product implementation approval followed by Planner
final source-of-truth reconciliation. Do not start Developer implementation until that
authorization checkpoint is recorded.

Blocking summary: none for implementation readiness.

---

# TASK_363C Reviewer Implementation Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Findings

### B1 - CR default-fill still accepts legacy Step quantity authority

`_specified_current_resistance_result()` initializes `authority` to `None` and
never assigns it. It then calls `matrix_step_readings_per_sample()` over the generic
`FeeStepQuantityContext` values and returns a calculated result when those values are
usable. That is an actual legacy `ConfirmedMatrixStepQuantity` calculation path, not
only a presentation compatibility path. It contradicts the frozen TASK_363C contract
that CR may use only the exact confirmed `cr_specified_current` Measurement Plan
target, including when no effective plan is available.

The same string-shaped transport also loses the required typed authority fields. The
helper returns a generic context and encodes lineage only in `source`; `_lineage()`
returns an empty string when revision id/sequence is absent, after which the default
fill branch can still calculate from the readings. Missing revision/fingerprint
lineage must instead be a typed review-required/no-write outcome.

Minimal fix: introduce or carry a typed CR authority result through the narrow CR
branch (exact target identity, kind, readings, revision id/sequence/fingerprint, and
diagnostic). The CR default result must calculate only from a valid typed result. A
generic legacy Step context, missing lineage, source prose, Point Profile, and an
unavailable/not-started/disabled Measurement Plan must all produce review-required
with Units and Testing Fee unset. Keep LLCR and other rule paths unchanged.

### B2 - Required API and V2 rebase regression boundaries are absent

The approved plan names three bounded test modules. Only
`tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py` exists.
Both required implementation tests are absent:

- `tests/integration/test_confirmed_matrix_fee_cr_specified_current_api.py`
- `tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py`

The existing unit test exercises the builder with in-memory doubles, but it does not
prove the Fee draft API receives the exact target-first result or that a Measurement
Plan lineage change makes a saved V2 draft non-current and a reviewed rebase refreshes
CR Units/Testing Fee while retaining compatible manual fields. Those are explicit
TASK_363C acceptance and validation gates, so the reported aggregate test counts are
not a substitute.

Minimal fix: add the two bounded, disposable integration modules from the plan. Cover
two Groups (8 x 5 => 40 at 10; 12 x 3 => 36 at 5), wrong/missing/excluded/disabled
targets and invalid owning quantity as typed no-write API outcomes, plus V2
currentness/rebase/manual-field preservation after confirmed Measurement Plan lineage
changes.

## Verification Performed

- Read the task, plan, board, Developer evidence, actual candidate diff, helper,
  Fee draft routing, CR default-fill branch, DTOs, and current dirty-worktree scope.
- `py -m pytest tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py -q`
  passed: `12 passed`.
- `py -m py_compile` over the new helper and touched Fee modules passed.
- Confirmed both planned integration test paths are absent from the working tree.
- Confirmed the unrelated LLCR API residual remains excluded. No real DB/files,
  staging, commit, or product-code edits were performed by Reviewer.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded fix pass for B1 and B2 only. Do not
route QA until the typed no-fallback CR authority and the two planned integration
boundaries pass review.

---

# TASK_363C Reviewer Implementation Re-Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## B1/B2 Closure

The prior production authority blocker is closed. The CR helper now constructs a
typed `CrSpecifiedCurrentAuthority` with the exact Group/row/sequence/suffix,
kind, readings, revision, deterministic fingerprint, and diagnostic. The Fee draft
passes that typed fact into default-fill, which now refuses generic contexts and
calculates only when the typed authority is valid. The API test also proves the
two-Group 40/36 and 10/5 results, missing target handling, and invalid owning
quantity behavior.

## Findings

### B3 - Two obsolete CR fallback tests leave the existing regression file red

The old CR assertions in `tests/unit/test_fee_default_fill.py` now fail exactly
because they expect the rejected generic Step-quantity/default-price behavior.
Reviewer reproduced the complete file: `2 failed, 75 passed`.

They are not an external residual: both tests exercise the rule behavior changed by
TASK_363C. Leaving them unchanged means a normal focused default-fill regression is
red and retains a misleading behavioral contract. Do not restore the fallback to
make them green. The bounded repair is to remove or rewrite only these two obsolete
test nodes to assert typed CR authority is required and missing generic authority is
review-required with no Units/Testing Fee (and no automatic price). Keep the
pre-existing file's physical size non-increasing; the new bounded CR test modules
remain the detailed authority coverage.

### B4 - The new V2 test does not exercise stale/currentness or production rebase

`test_fee_pricing_draft_cr_measurement_plan_rebase.py` demonstrates that two
manually built source contexts have different fingerprints, then calls the pure
`rebase_reviewed_values()` helper with manually supplied `36`/`180` defaults. It
does not classify the old saved V2 draft as non-current, build refreshed CR defaults
from the current confirmed Fee draft, or exercise the reviewed rebase/persistence
composition. A disconnected rebase helper would still make this test pass.

Minimal fix: expand only the new V2 integration module to run the existing production
V2 currentness and reviewed-rebase composition with an old saved CR draft, a changed
confirmed Measurement Plan lineage, and the current CR Fee draft output. Assert
stale/non-current before rebase, refreshed Units/Testing Fee after rebase, and
preservation of compatible manual Unit Price/discount. No V2 production code, API
client, or unrelated test module change is authorized.

## Verification Performed

- `py -m pytest tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py tests/integration/test_confirmed_matrix_fee_cr_specified_current_api.py tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py -q`
  passed: `17 passed`.
- `py -m pytest tests/unit/test_fee_default_fill.py -q` failed: `2 failed, 75
  passed`, both obsolete CR fallback/default-price assertions.
- `py_compile` passed for the candidate backend and new test modules. Candidate
  physical lines are at or below the hard limit; the Fee draft service is 465 lines.
- Candidate trailing-whitespace scans are clean. `git diff --check` has only existing
  LF/CRLF worktree notices. External LLCR/Point Profile/TASK_364B/front-end residuals
  remain excluded.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded fix pass for B3 and B4 only. Do not
route QA until the stale regression nodes are migrated and the V2 test covers the
actual currentness/rebase composition.

---

# TASK_363C Reviewer Scope/Readiness Re-Gate: B4 Policy

Date: 2026-07-19

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Scope Finding

The proposed one-file Measurement Plan-only eligibility hunk is not yet
implementable against the stated safety contract.

`FeePricingDraftSourceContext` persists only Measurement Plan status, revision id,
revision sequence, and fingerprint. It does not retain the prior effective target
projection, exact CR target identity/coverage/kind/readings, or a prior automatic
defaults payload. `load_rebase_candidate()` then rebuilds `prior_defaults` through
the current automatic-defaults provider. Consequently:

- the proposed policy cannot directly prove that the old and current exact CR target
  is unaffected, despite that being a required eligibility condition;
- when an exact CR target's readings actually change, rebuilding the prior defaults
  against the current provider changes the prior-default fingerprint, so the existing
  mandatory attestation correctly returns `blocked` before rebase; and
- bypassing that fingerprint check to force a refreshed 40/36-style CR result would
  weaken the accepted TASK_361L prior-default/row-identity attestation and is outside
  the requested narrow scope.

The B3 migration is properly reconciled: the focused existing default-fill file is
now green at `77 passed`. The remaining blocker is only the B4 scope contract.

## Required Planner Reconciliation

Choose and document one of these mutually exclusive, reviewable paths before any
Developer continuation:

1. **Keep the narrow policy hunk.** Define safe Measurement Plan-only eligibility in
   terms of facts the existing V2 envelope can prove: all non-Measurement-Plan
   lineage matches; both plan lineages are present and usable; rebuilding prior
   defaults with the current provider exactly matches the saved automatic-defaults
   fingerprint and ordered row identities; current defaults/provenance rebase safely.
   This permits only a plan lineage change observationally irrelevant to automatic
   defaults. It must continue to block an exact CR readings/coverage/kind change.
2. **Support refreshed CR values after an exact target change.** Plan an additional,
   non-destructive persisted old-authority/defaults attestation boundary capable of
   reconstructing and validating the old target projection. That exceeds the proposed
   one-policy-file May Touch list and requires a separate Discovery/scope gate.

The new policy test must prove the chosen semantics, including a safe
lineage-only/no-default-change `rebase_required` case, a changed CR target/defaults
fingerprint `blocked` case for path 1, all missing/unsafe state no-write cases, and
existing CAS/reload/current_v2 consumer guards. The existing CR rebase integration
must not claim a refreshed changed-target result unless path 2 is explicitly planned
and authorized.

## Verification Performed

- Read AGENTS, board, TASK_363C task/plan, Planner scope reconciliation, Developer
  and prior Reviewer evidence, and accepted TASK_361L evidence.
- Directly reviewed `fee_rule_transition_safe_rebase.py`, V2 source-context/envelope
  construction, pricing-draft persistence composition, and current safe-rebase unit
  coverage.
- Confirmed `_same_non_rule_lineage()` currently treats all Measurement Plan lineage
  fields as exact equality, while the proposed policy's stated target-level safety
  facts are absent from the stored source context.
- Confirmed board state: TASK_363C is `blocked pending re-scope`, original
  authorization is suspended, TASK_364B remains a separate excluded lane, and staging
  is empty. No product code, tests, real DB/files, staging, commit, or push was
  performed by Reviewer.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner docs-only scope fix. After a coherent choice is
recorded, return to Reviewer scope/readiness re-gate. Developer implementation remains
unauthorized and renewed user approval cannot be requested until this contract is
closed.

---

# TASK_363C Reviewer Dependency-Release And Implementation-Readiness Re-Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Dependency Review

`TASK_363D` is accepted at `754b79bc7370e4cecd4fc01dd576e6e7e67080fc`. Its accepted
single authority build and server-owned V2 attestation now provide the required B4
persistence boundary. The future TASK_363C B4 regression is sufficiently concrete:
production save of an attested old `current_v2` draft, exact confirmed CR target change,
load as `rebase_required`, reviewed CAS save, and reload as `current_v2`, with refreshed
Units/Testing Fee and preserved proven manual fields. It must replace the current
disconnected pure-helper test; TASK_363D persistence, attestation, and rebase policy
remain read-only.

The B1/B2/B3 replay boundary is also narrow: the typed CR helper, exact CR routing
hunks, typed context/default result hunks, three bounded focused modules, and only the
two obsolete CR fallback test nodes. The mixed Fee-draft-service worktree hunk must be
replayed from accepted HEAD rather than staged wholesale. The accepted service is 446
UTF-8 physical lines; the current mixed worktree copy is 450, leaving room below the
500-line hard limit only for the declared CR hunk.

## Blocking Finding

### B5 - Current task source-of-truth still describes TASK_363D as planned-only

The active "Current Phase / Role / Why Allowed" text in
`tasks/TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY.md` states
that this pass records a dependency on "planned-only TASK_363D" and that it "does not
authorize either lane." That is not marked as historical and conflicts with the task
status, board, dependency reconciliation, and accepted commit `754b79bc`.

Minimal Planner docs-only fix: replace that current-state sentence with the accepted
dependency fact and preserve the real guard: TASK_363D is accepted; TASK_363C's prior
authorization remains suspended; this re-gate and a renewed explicit user approval are
still required before any Developer replay. Then scan TASK/plan/Planner/Developer/
reconciliation evidence for the same stale planned-only assertion. Do not change
product/test candidates, alter B1-B4 scope, release TASK_363C, or absorb the external
LLCR API residual.

## Verification

- Verified accepted HEAD and commit `754b79bc`; reviewed its single-build persistence,
  attestation, CAS, and safe Measurement Plan rebase boundaries.
- Inspected the B1/B2 helper and routing candidate, B3 exact test-node diff, current
  disconnected B4 test, and the declared future production-persistence sequence.
- Confirmed the external LLCR API residual (`expected Units 20`, actual `None`) remains
  outside TASK_363C and is not a permitted fix target.
- Performed read-only status/diff/line-count inspection only; no product/test/real-data
  mutation, staging, commit, or push.

## Decision

`reviewer_blocked`

Recommended next role/action: Planner docs-only fix for B5, then Reviewer
dependency-release/readiness re-gate. Developer implementation remains unauthorized.

---

# TASK_363C Reviewer Dependency-Release And Implementation-Readiness Re-Gate: B5

Date: 2026-07-19

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Re-Gate Result

B5 is closed. The current task phase now identifies `TASK_363D` as complete/accepted
at `754b79bc7370e4cecd4fc01dd576e6e7e67080fc`, and states the correct boundary:
dependency release permits this Reviewer re-gate only; TASK_363C implementation remains
unauthorized until renewed explicit user approval. The prior planned-only wording is no
longer presented as current source-of-truth.

The released B1-B4 package remains implementation-ready without scope expansion:

- B1/B2 replay only the typed target-first CR helper, CR rule routing hunk, typed
  transport/default result, and bounded focused tests.
- B3 replays only the two obsolete generic-fallback test nodes.
- B4 replaces the disconnected pure-helper test with an accepted TASK_363D production
  attested save -> changed exact CR target -> `rebase_required` -> reviewed CAS save
  -> `current_v2` reload path. It must assert refreshed automatic Units/Testing Fee,
  compatible manual-field preservation, and no-write behavior for unsafe authority.
- `confirmed_matrix_fee_draft_service.py` must be replayed hunk-by-hunk from accepted
  TASK_363D, retaining its single-build boundary and staying below 500 physical lines.

TASK_363D persistence/attestation/rebase production files remain read-only. The external
LLCR API residual (`expected Units 20`, actual `None`) remains outside this lane and is
not a permitted repair target.

## Verification

- Read the corrected TASK, plan, Planner and dependency-reconciliation evidence, board,
  and accepted TASK_363D baseline.
- Confirmed the stale current-stage `planned-only TASK_363D` assertion no longer occurs;
  remaining historic gate-chain wording is explicitly labelled as history/superseded.
- Rechecked candidate isolation: unaccepted B1/B2/B3/B4 worktree hunks are still
  separate from accepted TASK_363D production files; staging is empty.
- Governance `git diff --check` and UTF-8 trailing-whitespace checks are clean apart
  from existing LF/CRLF notices on the task board.

## Decision

`reviewer_pass`

Recommended next role/action: User renewed implementation approval, then Planner final
source-of-truth reconciliation. Do not start Developer implementation directly.

---

# TASK_363C Reviewer Implementation Gate

Date: 2026-07-19

Role: Reviewer

Status: reviewer_blocked

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Finding

### B6 - Locked shared CR profile-consumer assertion still requires prohibited fallback

`tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py::test_specified_current_contact_resistance_never_uses_llcr_fallback`
constructs a `not_started` Measurement Plan and still asserts automatic CR `unit_price`
of `10`. The actual target-first CR implementation correctly produces
`review_required` with `unit_price`, `units`, and `testing_fee` unset. The exact node
was rerun independently and fails only at that obsolete `Decimal("10")` expectation.

This is a test-contract migration owned by TASK_363C B3, not a reason to restore a
generic Matrix Step, text, LLCR, or Point Profile fallback. The node name already
states the intended no-fallback policy; its remaining assertion is stale against the
accepted B3 contract.

## Narrow Authorized Fix

Route a Developer **tests-only bounded fix pass**. The only permitted product-adjacent
edit is the exact named test node in
`tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py`:

- assert `review_required is True`;
- assert `unit_price`, `units`, and `testing_fee` are all `None`;
- assert the business-readable review reason identifies missing confirmed CR Measurement
  Plan authority.

No production file, helper, default-fill rule, seed, authority path, API client, or
other test node is authorized by this finding. Preserve the existing LLCR profile
consumer assertions in the same module and continue excluding the staged TASK_365C
package and all other external residuals.

## Verified Candidate Behavior

- The B1/B2 exact typed CR resolver requires a matching confirmed Group/Row/Step/Suffix
  `cr_specified_current` target, valid lineage, included coverage, and finite positive
  readings. Missing, wrong-kind, diagnostic, or invalid authority remains typed
  `review_required` with no fallback.
- The CR default path uses exact authority readings and the owning Group sample quantity;
  the 10/5 price tier remains intact, while manual Base Fee does not block valid automatic
  Unit Price/Units/Testing Fee.
- The B4 integration test exercises the accepted TASK_363D path: attested V2 save,
  changed confirmed CR target, `rebase_required`, reviewed CAS save, and `current_v2`
  reload. It verifies refreshed automatic Units/Testing Fee and preservation of compatible
  manual Unit Price/discount values; unsafe current CR authority stays blocked with no
  persistence write.
- Mixed worktree changes in `confirmed_matrix_fee_draft_service.py` remain hunk-isolated;
  the CR routing hunk is below the 500-line hard limit and does not absorb the unrelated
  base-policy/rule-resolution work.

## Verification

- `py -m pytest tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py tests/integration/test_confirmed_matrix_fee_cr_specified_current_api.py tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py tests/unit/test_fee_default_fill.py -q` -> `96 passed`.
- TASK_363D attestation/rebase regressions -> `27 passed`.
- `py -m py_compile` passed for the CR candidate modules.
- Candidate `git diff --check` passed apart from existing LF/CRLF notices; UTF-8 trailing
  whitespace is clean. Candidate Python physical line counts are 458, 129, 98, 252, 303,
  63, and 210, all below the hard limit.
- The exact locked stale node was rerun and failed at its old `Decimal("10")` assertion;
  no real database/files, staging, commit, or push was used by Reviewer.

## Decision

`reviewer_blocked`

Recommended next role/action: Developer bounded tests-only fix pass for B6. Do not route
QA until the exact shared assertion has been migrated and the focused regressions are green.

---

# TASK_363C Reviewer Implementation Re-Gate: B6

Date: 2026-07-19

Role: Reviewer

Status: reviewer_pass

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Re-Gate Result

B6 is closed by the sole authorized tests-only hunk in
`tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py::test_specified_current_contact_resistance_never_uses_llcr_fallback`.
The test now asserts the approved behavior for a `not_started` Measurement Plan:
`review_required`, no automatic Unit Price/Units/Testing Fee, and a business-readable
confirmed CR Measurement Plan authority reason. It neither restores a generic fallback
nor changes the LLCR profile-consumer assertions in the same module.

The final candidate remains consistent with the accepted TASK_363D baseline. Exact CR
authority is target-first and fail-closed; the B4 regression uses the real attested V2
save -> changed target -> `rebase_required` -> reviewed CAS save -> `current_v2` reload
path. No production code changed in this B6 pass.

## Verification

- Exact B6 node and complete profile-consumer module: `9 passed`.
- TASK_363C CR authority/API/B4 plus full default-fill suite: `96 passed`.
- TASK_363D attestation/rebase suite: `27 passed`.
- Candidate `py_compile`, `git diff --check`, and UTF-8 trailing-whitespace scan passed;
  only existing LF/CRLF notices remain.
- Cached index is empty. No real database/files, staging, commit, or push was used.
- Re-measured B6 test file: `177` UTF-8 physical lines in the worktree, below the hard
  limit. The Developer evidence's `223` count is not reproducible in the current
  worktree and does not affect the B6 scope or result.

External TASK_365C and other dirty worktree residuals remain excluded.

## Decision

`reviewer_pass`

Recommended next role/action: QA gate. Do not route Integrator directly.
