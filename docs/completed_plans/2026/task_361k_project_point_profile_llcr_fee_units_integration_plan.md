# TASK_361K Project Point Profile LLCR Fee Units Integration Plan

## Status

Complete/accepted locally after Developer implementation, Reviewer implementation
gate, QA disposable smoke, and Integrator package isolation. Remote push was
intentionally not performed.

## Discovery Gate

### Current Phase / Active Task / Role / Why Allowed

- Current phase: Phase 11 controlled Matrix foundation.
- TASK_361J is complete/accepted and the board had no active implementation lane.
- Current task: TASK_361K planned-only.
- Current role: Planner Discovery/formal lane creation after explicit user request.

### Confirmed By User

- A confirmed Project Point Profile is the project-level default LLCR point count.
- `P / 1-4` means `4 readings/sample`.
- Final LLCR Units must distinguish readings/sample from applicable sample quantity.
- Draft Point Profile data must not affect Fee.
- Missing/corrupt/stale/non-authoritative states require review and no silent fallback.
- Existing target-specific Measurement Plan semantics require an explicit precedence
  rule and must never be double-counted with the project profile.
- This pass is planning only and may not touch real DB/files or product code.

### Confirmed By Repository Evidence

- `fee_rules_v2026_06_03.json` maps `Contact Resistance (Low Level)` to
  `fee_rule_llcr`, `per_reading`, unit `reading`.
- `fee_step_quantity_defaults.build_reading_result()` computes
  `units = sample_qty * readings_per_specimen` and selects the existing LLCR price
  tier from readings/specimen.
- Focused tests prove sample quantity `5` and readings/sample `6` produce Units `30`.
- `ConfirmedMatrixFeeDraftService` obtains sample quantity from
  `ConfirmedMatrixGroup.sample_quantity_expression`.
- TASK_361E gives exact included effective Measurement Plan targets precedence for
  LLCR/CR and blocks legacy fallback for active-root omissions/exclusions/corruption.
- `ContactPointProfileReadService` currently exposes active confirmed revision,
  revision fingerprint, ordered categories, and derived `points_per_sample`; it is not
  composed into Fee.
- TASK_361J explicitly excluded Fee consumer migration, and the supplied read-only
  runtime smoke still returns LLCR Units null with `Enter readings/specimen`.
- Fee draft production composition exists in API dependencies, subprocess export,
  required-form construction, and Matrix rebase promotion; inconsistent injection
  would produce divergent defaults.
- The current `build_step_quantity_contexts()` produces an unmatched review context
  (`Confirm Matrix Step quantity`) when a parsed token has no
  `ConfirmedMatrixStepQuantity`. Therefore a profile default cannot be implemented as
  a late fallback after the existing legacy Step-quantity availability check.

### Planner Decisions

- TASK_361K is one backend-only confirmed-consumer lane; no UI/API-client lane is
  needed because existing Fee field metadata can carry source lineage.
- Add a typed Point Profile consumer adapter instead of importing API DTOs or querying
  profile tables from Fee rule code.
- Project Point Profile is an LLCR project default, not a CR default and not a
  Group-Step override.
- For LLCR only, when Measurement Plan is `not_started`/`disabled` and the confirmed
  profile is usable, construct a matched profile context directly from each parsed
  Confirmed Matrix LLCR token/line plus its current group sample quantity. Do not read,
  require, or fall back to `ConfirmedMatrixStepQuantity` or legacy Matrix Step contact
  quantity; their absence must not emit `Confirm Matrix Step quantity`.
- Exact included effective Measurement Plan target wins. Active-root missing/excluded/
  impacted/corrupt target remains blocked. Profile default is considered only for
  Measurement Plan `not_started`/`disabled` states.
- Once TASK_361K composition is active, LLCR with an unusable/missing profile does not
  fall back to requirement text or legacy Matrix quantities.
- Keep current Matrix group sample quantity as multiplier and preserve no cross-Step
  aggregation.
- Preserve all pricing, manual editing, and saved pricing-draft semantics.

### Not Yet Confirmed

None blocking. Reviewer B1 is resolved by freezing the LLCR-only direct profile-context
construction before legacy Matrix Step quantity availability can block it. Reviewer
plan re-gate must verify that this exception is unavailable to CR/non-LLCR paths and
cannot bypass active-root Measurement Plan blockers.

### Planning Risks

- Treating `4 readings/sample` as total Units would undercharge multi-sample groups.
- Applying both profile and target-specific plan would double-count readings.
- Letting active-root omissions use project defaults would bypass TASK_361E review
  safety.
- Updating only the GET preview composition would leave subprocess export or Matrix
  rebase defaults inconsistent.
- Reading editable profile rows would leak unconfirmed operator input into Fee.

## Authority Flow

```text
active Confirmed Matrix
  -> Group sample quantity + LLCR row/Step lineage

effective confirmed Measurement Plan
  -> exact included Group-Step override, when usable
  -> active-root omission/exclusion/corruption => review-required

active confirmed Project Point Profile
  -> LLCR project default only when Measurement Plan is not_started/disabled
  -> readings_per_sample = confirmed included count total
  -> direct LLCR context from parsed Matrix token/line; no Step quantity dependency

Fee LLCR
  -> Units = selected readings_per_sample * Matrix group sample quantity
  -> existing unit-price tier and pricing pipeline unchanged
```

## Typed Adapter Design

Create `ContactPointProfileConfirmedConsumerAdapter` with a read-only repository port.
It returns an immutable effective projection containing status, project id, revision
id/sequence/fingerprint, readings/sample, and optional category audit facts.

Validation is fail-closed:

- `confirmed`: active pointer resolves to a confirmed revision; ordered included
  categories are valid; derived total is positive; persisted fingerprint/derived
  count are internally consistent.
- `not_started`: no root exists.
- `disabled`: reserved dependency-injected rollback state; no Settings UI/public
  config is introduced.
- `stale`: a pinned read observes active revision/fingerprint change before completion.
- `authority_corrupt`: root exists but active pointer/revision/category/fingerprint/
  total invariants fail.

Only `confirmed` may provide a default. Every other state maps to a structured
review-required Fee context. Draft/editable revisions are ignored.

## Fee Selection Design

Refine the current contact-rule boolean into an explicit rule kind so LLCR and CR
specified-current can follow different default policies.

For each LLCR token:

1. Use an exact effective confirmed Measurement Plan target when available/included.
2. Under an active independent root, preserve current omission/exclusion/review block.
3. Under Measurement Plan not-started/disabled, use the confirmed Point Profile total
   to build a matched context directly from the parsed LLCR token/line. This branch is
   evaluated without consulting `ConfirmedMatrixStepQuantity`; no missing legacy Step
   quantity review context may be created first or substituted later.
4. If Point Profile is unusable, emit a matched review context so
   `build_reading_result()` cannot fall through to text parsing.

Represent selected profile readings in the existing `FeeStepQuantityContext` shape:
test points/total readings = profile total, readings/point = `1`, source = confirmed
profile lineage. Repeated equal values across tokens remain one per-sample value; they
are not summed.

The direct branch still requires a valid current Confirmed Matrix group sample
quantity at calculation time. Missing, zero, non-numeric, or invalid sample quantity
returns review-required (`Confirm sample quantity`) with no Units or write. If an
independent Measurement Plan root is active, target omission/exclusion/affected/corrupt
status is resolved first and remains review-required; the profile branch is not
eligible. CR specified-current and non-LLCR tokens keep the existing context builder.

Existing `FeeFieldMetadata.source` carries a deterministic source string containing
authority type, revision sequence/id, and fingerprint. This keeps API/client shape
compatible while making the default auditable.

## Composition Plan

Inject the same adapter into every production `ConfirmedMatrixFeeDraftService` path:

- read-only Fee draft API dependency;
- direct Fee export builder and subprocess child;
- required-project-forms Fee composition;
- Matrix Fee rebase promotion when it creates a new default draft.

Tests may continue constructing the service without the adapter for isolated legacy
regressions, but production composition must be explicit. A profile reconfirm affects
only subsequently built defaults; it does not rewrite existing saved operator edits.

## Exact Future File Boundary

### May Touch

- `backend/application/contact_point_profile_confirmed_consumer_adapter.py` (new)
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py` only for optional
  backward-compatible internal lineage fields
- `backend/api/dependencies.py` only for adapter composition
- `backend/infrastructure/office/fee_evaluation_export_child.py` only for consistent
  read-adapter composition
- `backend/application/matrix_fee_rebase_promotion_service.py` only for injected
  adapter use in new default Fee draft construction
- focused tests:
  - `tests/unit/test_contact_point_profile_confirmed_consumer_adapter.py` (new)
  - `tests/unit/test_confirmed_matrix_fee_step_quantities.py`
  - `tests/unit/test_fee_default_fill.py`
  - `tests/unit/test_confirmed_matrix_fee_draft_service.py`
  - `tests/integration/test_confirmed_matrix_fee_draft_api.py`
  - `tests/unit/test_matrix_fee_rebase_promotion_service.py`
  - `tests/integration/test_fee_evaluation_export_child_transaction.py`
  - existing export/pricing tests as unchanged regressions
- TASK_361K task/plan/evidence and board

### Must Not Touch / Locked Paths

- Point Profile persistence/model/migration/repository writes/expression parser/
  lifecycle/API commands/frontend/client.
- Measurement Plan persistence/lifecycle/commands/projection semantics except consuming
  its existing typed output.
- Fee rule library/seed/matcher/pricing/discount/base-fee/manual-edit/UI/export layout.
- CR specified-current authority behavior beyond regression proof.
- TASK_360B/TASK_361D workbook services/routes/layout/artifacts.
- Generic Test Record/Report, Matrix parser/import, Matrix persistence, LTR/public
  drive, Office template behavior, real DB/files/folders.
- `.agents/**`, `docs/project_management/**`, release/settings, external TASK_361F/
  TASK_361H artifacts, unrelated residuals, remote push.

## Validation Gate

1. Pure adapter state/lineage/fingerprint/count/reconfirm/draft-isolation tests.
2. Fee unit tests for formula, <=20/>20 tier preservation, exact target override,
   `not_started` and `disabled` profile success with no
   `ConfirmedMatrixStepQuantity`, no `Confirm Matrix Step quantity` reason, active-root
   omission no-profile-fallback, no fallback, no double count, multiple-token equality,
   invalid group sample quantity review-required/no-write, and metadata.
3. Disposable SQLite/API integration for `P / 1-4`, Matrix sample quantity, local
   unconfirmed edit isolation, reconfirm update, missing/corrupt review-required, and
   non-LLCR invariance.
4. Composition tests for preview/export/required-form/rebase consistency.
5. TASK_351/357D/361E/361I/J, pricing draft, and Fee export regressions.
6. `py_compile`, focused pytest, diff/trailing/line-count/whitelist/forbidden-scope/
   no-real-mutation scans. No product browser test is required for backend-only V1.

## Merge Gate

Reviewer plan gate -> user approval for Developer planning-first -> Developer docs-only
planning-first -> Reviewer implementation-readiness -> explicit implementation
approval -> Developer implementation -> Reviewer implementation gate -> disposable
API QA -> Integrator package isolation and acceptance.

## Package Isolation

Current external residuals are TASK_361F operational evidence and TASK_361H QA images.
They are excluded. Integrator must stage only TASK_361K adapter/Fee composition/tests/
governance hunks and must not absorb Point Profile, workbook, frontend, real-data, or
unrelated board changes.

## Definition Of Ready

Definition of Ready is satisfied for bounded implementation. Reviewer plan re-gate and
implementation-readiness re-gate passed; the user explicitly approved product
implementation. The LLCR-only context path remains independent of legacy Step quantity
availability, and homogeneous source metadata is fail-closed; blocking questions: none.

## Next Legal Role

Orchestrator/User decision for a separately approved lane. TASK_361K is complete/
accepted locally.

## Developer Planning-First Refinement (2026-07-15)

### Authorization And Source Alignment

This was a docs-only Developer planning-first pass explicitly authorized by the user
after the Reviewer plan re-gate passed. Planner reconciliation now aligns the board,
task, plan, and evidence with that completed gate chain. No implementation status is
claimed here. Reviewer implementation-readiness remains mandatory before any later
implementation approval or authorization.

### Confirmed Repository Integration Point

`ConfirmedMatrixFeeDraftService.build_draft()` currently obtains the effective
Measurement Plan once, then `_build_group_lines()` always calls
`build_step_quantity_contexts()` with the legacy `ConfirmedMatrixStepQuantity` lookup.
That helper emits `Confirm Matrix Step quantity` before default fill when a token has
no stored Step quantity. TASK_361K must introduce its LLCR-only decision before that
unmatched legacy context is created:

1. Parse the current Confirmed Matrix cell and classify the matched Fee rule.
2. For `fee_rule_llcr`, ask the existing effective Measurement Plan adapter first.
3. If its status is active (`complete`, `partial_compatible`, `needs_review`, `empty`,
   or `authority_corrupt`), preserve its exact target decision. An absent, excluded,
   affected, unmatched, empty, or review-required target returns the existing typed
   review context. Do not query Point Profile or legacy Step quantities in that case.
4. Only if the Measurement Plan status is `not_started` or `disabled`, ask the new
   confirmed Point Profile adapter. For each parsed LLCR token, construct a matched
   `FeeStepQuantityContext` directly from the profile's confirmed
   `readings_per_sample`; do not call `build_step_quantity_lookup()` or read
   `ConfirmedMatrixStepQuantity` for this branch.
5. If the profile adapter reports `draft`, `stale`, `missing`, or
   `authority_corrupt`, construct a matched review-required context. This prevents
   `build_reading_result()` from falling through to requirement-text parsing or a
   legacy Matrix Step quantity.
6. For `fee_rule_contact_resistance_specified_current` and every non-LLCR rule, retain
   the existing `build_step_quantity_contexts()` path unchanged.

This sequencing preserves target-specific Measurement Plan precedence and prevents
double counting: profile readings are one per-sample value for each same-valued LLCR
token, not a sum across tokens or Steps. `build_reading_result()` remains the sole
place that multiplies selected readings by the current group's
`sample_quantity_expression`, preserves the existing `<=20`/`>20` price tier, and
returns `Confirm sample quantity` without Units/testing fee for an invalid quantity.

### New Read-Only Profile Consumer Contract

Create `backend/application/contact_point_profile_confirmed_consumer_adapter.py` as a
consumer-specific read adapter. It may use the existing
`ContactPointProfileAuthorityRepository` read methods only:

- no root: `not_started`;
- root with no editable/confirmed authority exposed to consumers: `missing` or
  `authority_corrupt` according to pointer/revision/category/fingerprint validation;
- active confirmed revision with valid included categories: `confirmed` with derived
  `readings_per_sample`, revision id, revision sequence, fingerprint, and immutable
  category lineage;
- an editable draft never becomes a source and is surfaced as `draft` only as a
  review-required consumer status;
- an injected read-only disabled adapter is `disabled`, preserving the existing
  feature rollback boundary without a Settings route or UI.

The adapter must use the existing Point Profile expression/count semantics to derive
the included total and read-verify the active pointer, revision state, category order,
and revision fingerprint. It creates no roots, drafts, revisions, categories, or
normalization writes. Its result carries a deterministic internal lineage string such
as `Confirmed Project Point Profile: revision <sequence> (<revision id>;
<fingerprint>)`; that string is passed through the existing `FeeFieldMetadata.source`
field only. No API response, frontend, or pricing-draft persistence contract changes.

### Exact Implementation Order

1. Add the read-only Point Profile adapter plus focused temporary-SQLite tests for
   confirmed, no-root, draft isolation, stale/corrupt pointer, disabled, category
   total, fingerprint, and lineage. Keep it under 300 lines.
2. Extend `confirmed_matrix_fee_step_quantities.py` with a narrow context factory for
   the direct LLCR profile branch and typed review contexts. Keep existing legacy and
   CR helpers behaviorally unchanged. The direct factory receives parsed token and
   adapter result, not a `ConfirmedMatrixStepQuantity`.
3. Thread the Point Profile adapter into `ConfirmedMatrixFeeDraftService` and select
   contexts in `_build_group_lines()` before the legacy lookup for LLCR only. Retain
   the existing Measurement Plan adapter as the first authority decision.
4. Update `fee_step_quantity_defaults.build_reading_result()` to derive one selected
   authority source from the successful `FeeStepQuantityContext` values and pass it to
   `calculated_result()`. It must no longer unconditionally replace every successful
   context source with the literal `Matrix Step quantity`. Preserve the established
   legacy Matrix Step source and exact `confirmed_measurement_plan` source unchanged;
   a direct Profile context must retain the adapter-provided deterministic `Confirmed
   Project Point Profile` revision/id/fingerprint lineage. If selected contexts are
   mixed, absent, or carry divergent sources, return review-required/no-write rather
   than choosing an arbitrary source. Keep the current public DTO/API shape. Touch
   `fee_default_fill_models.py` only if optional, backward-compatible internal lineage
   metadata cannot otherwise reach field metadata; do not alter fee rules, prices,
   discounts, or UI semantics.
5. Add a private dependency composition helper in `backend/api/dependencies.py` that
   builds the same read-only Point Profile adapter beside
   `_confirmed_contact_measurement_consumer_adapter`. Supply both adapters at all
   confirmed Fee default-construction paths: Fee draft route,
   `build_direct_confirmed_matrix_fee_evaluation_export_service`, and
   `get_project_folder_required_forms_service`.
6. Compose the adapter in the isolated child-process export builder
   (`fee_evaluation_export_child.py`) and inject it into
   `MatrixFeeRebasePromotionService` rather than constructing a different authority
   reader inside `_save_default_draft`. Existing saved pricing drafts/manual edits
   remain immutable; only newly built default drafts use the latest confirmed profile.
7. Add the focused test matrix, then rerun existing Fee/default-fill/export/rebase
   regressions. No frontend/browser work is planned because no client contract changes.

### Field And Lineage Contract

For a selected profile branch, create one matched `FeeStepQuantityContext` per parsed
LLCR token with `test_points_per_sample` and `total_readings` equal to the confirmed
Profile's included `readings_per_sample`, `readings_per_point` equal to `"1"`, and
source set to the confirmed-profile lineage. This is a Fee internal read fact, not a
new Point Profile or Matrix write. The resulting Fee field metadata must identify the
confirmed Point Profile revision and fingerprint. It must not state that a generic
Matrix Step quantity was used.

For exact active Measurement Plan targets, retain source
`confirmed_measurement_plan`; never combine its readings with the Profile result.
For active-root review states, use the existing Measurement Plan review message rather
than an inferred Profile or text value. Profile states other than `confirmed` create a
matched review-required LLCR context with a concise typed reason, so no hidden fallback
can produce Units or a write-ready line.

`matrix_step_readings_per_sample()` must select numeric readings and exactly one common
source as one fail-closed decision. A successful source set is homogeneous: legacy
Matrix Step contexts retain their established source, exact confirmed Measurement Plan
contexts retain `confirmed_measurement_plan`, and Profile contexts retain one
byte-for-byte identical adapter lineage string. Missing, mixed, or divergent source
strings are review-required/no-write even when their numeric readings agree.
`build_reading_result()` passes the selected source to `calculated_result()` so the
existing auto-filled `FeeFieldMetadata.source` remains auditable without a DTO/API
change.

### Production Composition And Rollback

`get_confirmed_matrix_fee_draft_service()` is the normal preview path. The direct
export builder, required-forms builder, child-process export builder, and rebase
promotion builder currently construct `ConfirmedMatrixFeeDraftService` separately;
all must receive the same read-only adapter composition. The adapter is read-only and
has no persistence side effects, so feature rollback consists of omitting that adapter
from composition. Existing saved Fee pricing snapshots are not recalculated, rewritten,
or deleted. No runtime Settings UI/config route is introduced.

### Focused TDD Matrix

- `tests/unit/test_contact_point_profile_confirmed_consumer_adapter.py` (new):
  disposable SQLite confirmed profile totals, lineage/fingerprint, missing/draft/stale/
  corrupt/disabled review states, and no repository writes.
- `tests/unit/test_confirmed_matrix_fee_step_quantities.py`: direct LLCR profile
  contexts never inspect a Step quantity; active-root omission/exclusion/affected/
  corrupt blocks stay review-required; CR context remains legacy behavior.
- `tests/unit/test_confirmed_matrix_fee_draft_service.py` and
  `tests/unit/test_fee_default_fill.py`: `P / 1-4` with Matrix sample quantity `5`
  yields Units `20`; tier behavior is unchanged; `not_started` and `disabled` succeed
  without `ConfirmedMatrixStepQuantity`; profile missing/draft/stale/corrupt and invalid
  group quantity produce review/no-write; exact target wins; equal multi-token values
  are not summed; calculated Profile metadata contains the exact confirmed revision/id/
  fingerprint lineage; legacy Matrix Step and target-specific Measurement Plan metadata
  retain their existing sources; conflicting source sets are review-required/no-write;
  CR/non-LLCR remain unchanged.
- `tests/integration/test_confirmed_matrix_fee_draft_api.py`: disposable SQLite typed
  preview metadata and review states, including unconfirmed Point Profile edits not
  affecting a confirmed preview and reconfirm affecting only a newly built preview.
- `tests/integration/test_fee_evaluation_export_child_transaction.py`,
  `tests/unit/test_fee_evaluation_export_subprocess_runner.py`,
  `tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py`, and
  `tests/unit/test_matrix_fee_rebase_promotion_service.py`: normal/export/required-
  forms/rebase construction all receive the same adapter and do not rewrite saved
  pricing drafts.

Run focused `pytest`, `py_compile` for every touched Python module, line-count checks
(each new or edited Python file below the 500-line hard limit), `git diff --check`,
UTF-8 trailing-whitespace, whitelist/forbidden-scope, and no-real-DB/file scans. The
disposable fixtures own every database and artifact root.

### Final Package Boundary

The future candidate package is limited to the exact adapter, narrow Fee context
selection/composition files, their focused tests, and TASK_361K governance. Do not
absorb the current TASK_361F operational evidence, TASK_361H images, board residual,
or any Point Profile schema/editor/migration hunk. If the required adapter cannot read
the confirmed Profile without mutating its repository/model/lifecycle boundary, stop
for Planner reconciliation rather than widening this lane.

## Reviewer Readiness B1 Planning Fix (2026-07-15)

Reviewer implementation-readiness correctly identified that the current successful
reading calculation overwrites all selected Step-context sources with `Matrix Step
quantity`. The future implementation must therefore modify
`backend/modules/fee_evaluation/fee_step_quantity_defaults.py`, already in the May
Touch list, as a narrow provenance propagation change. This is not a Fee rule, price,
discount, or DTO/API change:

- select numeric readings and one common selected source together;
- pass that selected source to `calculated_result()` and its existing field metadata;
- use the adapter's deterministic `Confirmed Project Point Profile: revision
  <sequence> (<revision id>; <fingerprint>)` string for the Profile branch;
- preserve existing legacy Matrix Step and exact confirmed Measurement Plan source
  semantics;
- fail closed with review-required/no-write when source values are absent, mixed, or
  divergent, even if readings are otherwise equal.

The future disposable test suite must assert Profile lineage metadata, preservation of
legacy and exact-target sources, and no-write review behavior for a conflicting source
set. Product implementation remains unauthorized pending Reviewer
implementation-readiness re-gate.

## Source-Of-Truth Reconciliation (2026-07-15)

- Reviewer plan re-gate: passed; B1 closed.
- User approval: Developer planning-first only.
- Developer planning-first: docs-only complete.
- Reviewer implementation-readiness initially blocked on source metadata propagation;
  the Developer docs-only planning fix froze homogeneous source selection and exact
  lineage preservation.
- Reviewer implementation-readiness re-gate: passed.
- User approval: explicit TASK_361K product implementation approval.
- Developer implementation: complete within the authorized scope.
- Reviewer implementation gate: passed with no product blocker.
- QA passed the disposable smoke; Integrator package isolation and acceptance are
  complete.
- Frozen behavior remains unchanged: LLCR formula, direct profile context independent
  of legacy Step quantity, active-root blockers, and unchanged CR/non-LLCR paths.

## Final Implementation Authorization

Authorization is limited to the confirmed Project Point Profile LLCR Fee Units read
integration, LLCR-only direct contexts, homogeneous readings/source selection and
metadata lineage, production composition, and focused disposable tests. Profile
metadata must include revision sequence/id/fingerprint. Existing legacy Matrix Step
and exact confirmed Measurement Plan source metadata remain unchanged. Missing,
mixed, or divergent sources are typed review-required/no-write.

Fee rules/pricing/discount/UI, TASK_361J schema/parser/editor/lifecycle, frontend/API
client, public DTO/API shape, workbook behavior, Generic Test Record/Report, Matrix
parser/import, LTR/public drive, real DB/files, and external residuals remain locked.

## Post-Implementation Governance Reconciliation

- Developer evidence records the bounded implementation and disposable backend suite:
  `94 passed`.
- Reviewer inspected the actual diff and passed the implementation gate.
- Formula, authority precedence, no-double-count, no-legacy-Step dependency, typed
  no-write states, source lineage, CR/non-LLCR preservation, and locked paths remain
  unchanged.
- Integrator package isolation is complete and the lane is accepted locally. The next
  legal action is an Orchestrator/User decision for a separately approved lane.
