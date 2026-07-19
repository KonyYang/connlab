# TASK_363D Fee Pricing Draft Prior Defaults Attestation Plan

## Status

`complete / Integrator accepted`

## Authorization Reconciliation

- Reviewer plan re-gate passed.
- User approved Developer planning-first only.
- Developer completed the docs-only planning-first pass.
- Reviewer implementation-readiness passed.
- User explicitly approved TASK_363D source-of-truth reconciliation and product
  implementation.
- TASK_363C remains `blocked_by_TASK_363D` until TASK_363D is accepted or a later
  explicit dependency-release gate changes that status.

Authorization is limited to the private single-authority-build result, mechanically
extracted existing status/warning/time helpers, canonical defaults/identities/
pre-flattening row safety/source context from that one result, additive typed V2
`payload_json` attestation, save/load/rebase/CAS/current-v2 sequencing, four bounded
tests, rollback/compatibility, line-count control, and package isolation described
below. No DDL/schema/repository/public API/client change is authorized.

## Discovery Gate

### Confirmed By User / Orchestrator

- TASK_363C changed CR readings must refresh through reviewed safe rebase rather than
  silently hydrating stale automatic values.
- Accepted TASK_361L fingerprints, ordered row identity, manual provenance, generation,
  CAS, token, reload/revalidation, and current-v2-only consumer guards cannot weaken.
- Missing or unsafe evidence must remain typed blocked/no-write.
- This pass is docs/governance only and must not access real data/files.

### Confirmed By Repository Evidence

- `FeePricingDraftSourceContext` stores Measurement Plan status/revision/id/fingerprint
  and `automatic_defaults_fingerprint`, but not the prior automatic values or exact
  authority projection.
- `load_rebase_candidate()` currently rebuilds prior defaults through the current
  provider. A genuine CR readings change therefore produces a fingerprint mismatch and
  correctly blocks under the accepted TASK_361L attestation contract.
- The pricing-draft table already stores canonical envelope JSON in a `TEXT`
  `payload_json` column. Repository CAS compares the exact previous payload.
- The accepted decoder verifies the entire JSON object fingerprint and ignores unknown
  additive fields after verification, providing a non-destructive rollback path.
- `current_automatic_values()` currently flattens `FeeEvaluationDraft` through
  `FeeEvaluationEditedExportValues`. Missing automatic fields become editable `0`/`1`
  placeholders, while line-level `review_required`, review reason, field metadata, and
  exact target-first CR authority diagnostics are lost.
- `ConfirmedMatrixFeeDraftService.build_draft()` already reads the Confirmed Matrix,
  effective Measurement Plan, and confirmed Point Profile as one application build.
  TASK_363D must preserve those same snapshots when deriving values, safety, and source
  context rather than invoking providers independently.

### Planner Decisions

1. Choose Reviewer option 2. Do not relax `_same_non_rule_lineage()` without persisted
   prior automatic defaults bound to the saved authority source context.
2. Use an additive internal attestation object in existing V2 `payload_json`; no SQLite
   schema migration or background data migration.
3. Build a private immutable automatic-default result once per operation. The same
   result contains canonical editable defaults, pre-flattening per-row safety evidence,
   ordered stable identities, and exact source context.
4. Keep existing V2 without attestation current under unchanged context and fail closed
   after source change.
5. Preserve all public V2 statuses and DTO/client shapes unless later evidence forces a
   separately re-gated API change.
6. A CR row is safe only when the actual target-first authority result from that same
   build is usable. Omitted, excluded, affected, wrong-kind, mixed, diagnostic, missing
   lineage, and invalid quantity states are unsafe even if flattened values look valid.
7. Keep TASK_363D serial before TASK_363C B4 continuation.

### Not Yet Confirmed

No blocking product decision. Exact private dataclass/helper names may follow repository
conventions. The attestation stores canonical per-row safety evidence, not copied
Measurement Plan target snapshots. Any need for public DTO/client or persistence schema
changes returns to Planner and Reviewer.

## Implementation Design Draft

### Envelope codec

Extend the V2 codec with an optional typed attestation. Decode validates its kind,
canonical mappings, bounds, fingerprint equality, ordered identity, and relationship to
source context. Unknown/malformed attestation fails closed. Encoding accepts only a
server-built typed object. Bounds are exactly 2,000 automatic rows and 1,048,576
canonical UTF-8 bytes.

The saved object binds all of the following under the existing whole-envelope canonical
fingerprint/integrity token and generation lineage:

- canonical automatic editable-values payload and its fingerprint;
- ordered stable row identities and their fingerprint;
- ordered canonical per-row safety objects and their fingerprint;
- exact source-context fingerprint used by the build; and
- attested generation and payload lineage.

Missing, malformed, oversized, divergent, or out-of-order content is typed `blocked`.

### Private single-build result

Add a bounded private application helper/provider adapter that obtains one
`ConfirmedMatrixFeeDraftService` build and derives all three outputs from the same read:

1. canonical editable automatic defaults;
2. canonical pre-flattening row safety; and
3. exact authority source context.

It must not call Measurement Plan, Point Profile, Matrix, or rule providers a second
time. If exposing the already-read facts requires a narrow private result/refactor in
`confirmed_matrix_fee_draft_service.py`, that change may add at most 20 physical lines
and the file must remain at or below its 500-line hard limit. It cannot change Fee
formulae, rules, target selection, or authority writes; otherwise the lane returns to
Planner.

### Attestation helper

The new pure attestation helper owns canonicalization and validation. It has no
repository, route, authority mutation, or provider side effects. Each row safety object
contains stable row identity, row kind, matched rule id, automatic field states,
`safe_for_rebase`, and a typed diagnostic class with canonical diagnostic text.

Safety is derived from the unflattened `FeeEvaluationDraft` line and its exact authority
inputs. A field intentionally left for manual completion, such as current CR Base Fee,
does not by itself make otherwise valid automatic CR Units/Unit Price unsafe. By
contrast, `review_required` caused by missing or invalid automatic authority is unsafe.

For CR specified-current rows, classification must reuse the actual target-first
resolver against the same Confirmed Matrix group/row tokens and the same effective
Measurement Plan snapshot. It must preserve omission/exclusion/affected/wrong-kind/
mixed/diagnostic/missing-lineage/invalid-quantity outcomes as unsafe diagnostics. It
must never infer safety from flattened `0`/`1` values, and it must not copy target
snapshots into pricing persistence.

### Persistence sequencing

1. Explicit save invokes the private single-build adapter exactly once.
2. The adapter emits canonical defaults, ordered row safety, and exact source context
   from the same authority snapshots.
3. Server validates row identities, row safety, source binding, and operator provenance.
4. Server creates the attestation and V2 envelope for the next generation.
5. Repository performs existing exact-payload CAS.
6. Transaction-visible reload verifies payload/source/default/safety fingerprints and
   `current_v2`; failure rolls back.

Load, Cancel, and classification never upgrade or rewrite a record.

### Rebase sequencing

1. Decode and validate saved attestation independently of current providers, including
   saved per-row safety and generation/payload binding.
2. Prove saved defaults, identities, safety, and source-context fingerprints agree with
   the saved envelope and edited rows; every applicable saved row must be safe.
3. Invoke the private current automatic-default build exactly once.
4. Require matching-safe ordered row identities, compatible row-safety classes, and a
   safe current authority result. Any unsafe saved/current row is typed `blocked`.
5. Merge only accepted saved manual provenance over current automatic defaults.
6. Return read-only `rebase_required` candidate.
7. On explicit reviewed save, repeat every check under CAS, write next generation,
   reload, and require `current_v2`.

### Compatibility and rollback

- No DDL, model, repository lookup, uniqueness, or real-data migration.
- V1 stays legacy/unmodified.
- Unattested V2 stays readable/current only under unchanged context.
- Additive attested V2 can be read by the accepted decoder/fingerprint behavior; a code
  rollback ignores the optional object and safely returns to stricter blocking.
- No automatic downgrade or field deletion.

## File-Level TDD Order

1. Add private single-build and row-safety tests, including a provider-call counter.
2. Add pure codec/attestation tests for defaults, identity, safety, context, generation,
   size, malformed, and divergent bindings.
3. Add policy tests proving safe saved + safe current changed defaults can become
   `rebase_required`; unsafe saved/current rows remain `blocked`.
4. Add disposable persistence/API tests for save, reload, reviewed CAS, rollback, and
   V1/unattested-V2 compatibility.
5. Implement the bounded single-build helper and V2 codec/attestation extension.
6. Wire explicit save and rebase load through exactly one build result per operation.
7. Run all TASK_361L consumer guards read-only and prove non-current states write no
   Confirmed Fee or artifact.
8. Run TASK_363C B4 only after TASK_363D is accepted.

## Developer Planning-First Refinement

### Verified Current Call Graph

The current production composition injects one `ConfirmedMatrixFeeDraftService` as the
automatic-default provider and also injects the Point Profile and Measurement Plan
adapters separately into `FeeEvaluationPricingDraftPersistenceService`. The current
save path calls `current_automatic_values()` once for provenance, then
`build_authority_source_context()` calls it again and independently rereads both
adapters. Load/rebase can call `_source_context()` more than once and then rebuild
current defaults again inside `load_rebase_candidate()`. Those reads can observe
different authority revisions and are the exact TOCTOU boundary this task must remove.

`ConfirmedMatrixFeeDraftService.build_draft()` already reads the active Confirmed
Matrix, active rule library, effective Measurement Plan, and effective Point Profile
before constructing the unflattened `FeeEvaluationDraft`. The future implementation
must expose those already-read facts through a private result; it must not add a second
Matrix, profile, plan, or rule-library provider call.

The checked-out `confirmed_matrix_fee_draft_service.py` is currently exactly 500
physical lines and contains external TASK_363C candidate hunks. A future TASK_363D
change cannot add lines to it without a mechanical split and hunk-level isolation.
Before adding the private result method, move only the existing time/status/warning
helpers to the bounded support module named below. Their behavior and call order stay
byte-for-byte equivalent at the return-value level. The service must finish below 480
physical lines, while TASK_363D additions to its orchestration remain at or below 20
physical lines. Any need to edit CR resolution, group/line calculation, rules, or
formulae returns to Planner.

### Exact Private Build Contracts

Create `backend/application/confirmed_matrix_fee_draft_build_result.py` with the
private immutable result:

```python
@dataclass(frozen=True, slots=True)
class ConfirmedMatrixFeeAuthorityBuildResult:
    draft: FeeEvaluationDraft
    confirmed_matrix: ConfirmedMatrixSnapshot
    rule_library: FeeRuleLibrary
    effective_measurement_plan: EffectiveContactMeasurementPlan | None
    effective_point_profile: EffectiveConfirmedPointProfile | None
```

`ConfirmedMatrixFeeDraftService.build_draft()` remains the public read method and
returns `build_authority_result(command).draft`. The private
`build_authority_result()` performs the existing reads once and returns the five facts
above. `backend/application/confirmed_matrix_fee_draft_build_support.py` receives only
the existing `_now_iso`, `_root_warnings`, and `_draft_status` helpers to create line
headroom; it must not own calculations or authority selection.

Create `backend/application/fee_evaluation_pricing_draft_automatic_build.py` with:

```python
@dataclass(frozen=True, slots=True)
class FeePricingDraftAutomaticBuildResult:
    fee_draft: FeeEvaluationDraft
    confirmed_matrix: ConfirmedMatrixSnapshot
    automatic_values: FeeEvaluationEditedExportValues
    ordered_row_identities: tuple[FeeEvaluationEditedRowIdentity | FeeEvaluationManualRowIdentity, ...]
    row_safety: tuple[FeePricingDraftAutomaticRowSafety, ...]
    source_context: FeePricingDraftSourceContext
```

`build_current_pricing_defaults(project_id, provider)` calls
`provider.build_authority_result()` exactly once. It derives the basic-fill validation
surface from `confirmed_matrix` with the existing pure
`build_basic_fill_from_confirmed_snapshot()` function; it does not invoke the basic
fill service or any authority adapter again. It converts `fee_draft` to editable
defaults once, classifies safety before flattening evidence is discarded, and builds
source context from the returned Matrix/rule/profile/plan facts.

The existing separately injected profile/plan provider fields may remain temporarily
for constructor compatibility, but TASK_363D code must not call them. Production
`backend/api/dependencies.py` therefore stays read-only. Counting fakes must fail the
test if either compatibility provider is called or if the automatic provider is
called twice.

### Canonical Attestation Shape

Create `backend/application/fee_evaluation_pricing_draft_prior_defaults_attestation.py`
as a pure codec/validator. Its private dataclasses and JSON shape are frozen as:

```text
automatic_defaults_attestation:
  kind: fee-automatic-defaults:v1
  attested_generation: positive integer equal to envelope generation
  source_context_fingerprint: sha256 of exact canonical source-context payload
  automatic_values_payload: canonical edited_values_to_payload(defaults)
  automatic_defaults_fingerprint: sha256 of automatic_values_payload
  ordered_row_identities: matrix rows in payload order, then manual rows in payload order
  ordered_row_identity_fingerprint: sha256 of the ordered identity list
  row_safety: one object per automatic Matrix row, in identical matrix-row order
  row_safety_fingerprint: sha256 of the ordered row_safety list
```

Each identity is the existing full tuple returned by `edited_row_identity()` or
`manual_row_identity()`; `source_line_id` alone is never sufficient. Each row-safety
object contains that full Matrix-row identity, `row_kind`, `matched_rule_id`, ordered
field states (`field`, `state`, `source`, `required_for_rebase`),
`safe_for_rebase`, and a typed diagnostic (`code`, concise canonical text). Duplicate
identities, row-safety count/order mismatch, unknown fields/states/codes, noncanonical
payloads, fingerprint mismatch, more than 2,000 Matrix rows, or a canonical envelope
larger than 1,048,576 UTF-8 bytes raises the existing typed envelope/attestation error
before persistence CAS.

The envelope encoder accepts an optional typed attestation only. The decoder validates
the full object and returns it on `DecodedFeePricingDraftPayload`; callers cannot pass
an arbitrary mapping through. The attestation remains inside the existing whole
payload fingerprint and validation token. No response DTO or request field exposes it.

### Pre-Flattening Safety Rules

Safety classification iterates the unflattened `FeeEvaluationDraft` and deterministically
maps each `FeeEvaluationLineItem` plus step token/index to the corresponding edited-row
identity. It records all existing `FeeFieldMetadata` states before
`edited_values_from_fee_draft()` substitutes `0` or `1`.

For `fee_rule_contact_resistance_specified_current`, the fields required for automatic
rebase are `unit_price`, `unit_label` (serialized as `unit_type`), `units`, and
`testing_fee`. They are safe only when the line metadata proves the existing exact
target-first CR authority supplied authoritative values and lineage. Missing lineage
or readings, invalid owning Group quantity, omitted/excluded/affected/wrong-kind/mixed
targets, resolver diagnostics, missing required field metadata, or a manual/not-
available state on any required field produces `safe_for_rebase=False`. A separately
manual CR `base_fee` state is recorded but has `required_for_rebase=False`; it cannot
invalidate otherwise authoritative Units/Unit Price/Testing Fee. No diagnostic is
parsed from flattened values, and no target snapshot is serialized.

For other rows, existing `FeeFieldMetadata` remains the source of field state. A field
that would be refreshed automatically must be `auto_filled`; an explicit manual-only
field is nonrequired. A line-level review reason caused by an automatic required field
is unsafe. Rule matching, prices, calculations, and existing manual provenance remain
unchanged.

### Save, Load, And Rebase Sequencing

1. `save()` builds one `FeePricingDraftAutomaticBuildResult` before validating rows.
   It validates incoming identities against the basic fill derived from that result's
   captured Confirmed Matrix, infers provenance against its `automatic_values`, and
   builds source context and attestation from the same result.
2. The V2 encoder binds attestation generation to the next CAS generation. Existing
   exact-payload CAS writes the envelope. A transaction-visible reload must decode the
   attestation and verify all fingerprints before returning `current_v2`.
3. `load()` builds current automatic facts once. Exact unchanged source context follows
   the existing `current_v2` path. A changed source passes the already-built result to
   rebase policy; policy cannot receive a provider for a second current build.
4. An attested Measurement-Plan-only change may become `rebase_required` only when
   Matrix, rule version, and Point Profile lineage retain the accepted TASK_361L
   compatibility, saved and current ordered identities match, and every saved/current
   applicable row is safe. Current automatic defaults supply refreshed values; existing
   provenance merge preserves only operator-owned fields.
5. Existing fee-rule-version transition behavior and its prior bundled-seed validation
   remain unchanged. The new attested Measurement Plan path must not weaken or replace
   TASK_363A logic. Unattested V2 with changed source remains blocked.
6. Reviewed save repeats one current build and all safety/fingerprint checks under the
   existing CAS expectation, increments generation, reloads, and requires
   `current_v2`. Stale generation/token/payload or CAS mismatch remains typed `409` and
   zero overwrite.
7. Load and Cancel never add an attestation. Confirm/Update, Required Forms, direct/
   browser/child export, and Matrix rebase continue to consume only server-reloaded
   `current_v2`; blocked/rebase-required states perform no writer or artifact call.

### Exact Future File Order And Ownership

1. Add the four bounded test modules listed below and confirm red behavior.
2. Create `confirmed_matrix_fee_draft_build_result.py` and
   `confirmed_matrix_fee_draft_build_support.py`; mechanically split status helpers and
   add the private service result without changing Fee output.
3. Create `fee_evaluation_pricing_draft_automatic_build.py`; prove one authority build
   and derive values/safety/context/basic-fill from its captured facts.
4. Create `fee_evaluation_pricing_draft_prior_defaults_attestation.py`, then extend the
   V2 contract encoder/decoder with the optional typed field.
5. Change `fee_evaluation_pricing_draft_v2_authority_context.py` from provider reads to
   pure source-context construction from `FeePricingDraftAutomaticBuildResult`.
6. Change persistence save/load to consume exactly one automatic build result per
   operation and retain the existing CAS/reload boundary.
7. Add the attested Measurement Plan branch to
   `fee_rule_transition_safe_rebase.py`; leave existing seed transition and
   `fee_evaluation_pricing_draft_v2_rebase.py` merge semantics unchanged.
8. Run TASK_361L consumer regressions and package/scope scans. TASK_363C remains
   untouched until this lane is accepted and separately reconciled.

### Exact Focused Tests

- `tests/unit/test_fee_pricing_draft_automatic_build_safety.py` (target <= 350 lines):
  `test_single_build_uses_one_matrix_profile_and_plan_snapshot`,
  `test_cr_manual_base_fee_does_not_block_automatic_safety`, and a parameterized
  `test_cr_unsafe_authority_is_recorded_before_flattening` covering omitted, excluded,
  affected, wrong-kind, mixed, missing-lineage, invalid readings, invalid quantity,
  and diagnostic states.
- `tests/unit/test_fee_pricing_draft_prior_defaults_attestation.py` (target <= 400
  lines): round trip plus generation/context/default/identity/safety fingerprint,
  duplicate/order, unknown kind/state/code, row-count, and byte-size failures.
- `tests/unit/test_fee_rule_transition_safe_rebase_measurement_plan.py` (target <= 350
  lines): safe changed CR defaults -> `rebase_required`; unattested, unsafe saved,
  unsafe current, identity-divergent, non-Measurement-Plan lineage, stale token, and
  existing fee-rule transition boundaries -> blocked/no-write.
- `tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py`
  (target <= 450 lines): disposable save/reload, changed CR reviewed rebase, automatic
  Units/Testing Fee refresh with manual Unit Price/discount preservation, CAS conflict,
  transaction-visible reload, V1/unattested V2 compatibility, and writer/artifact call
  counters for blocked states.

Each new module must remain below 500 physical lines. Existing oversized
`tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py` and the currently
478-line `tests/unit/test_confirmed_matrix_fee_draft_service.py` are read-only
regression dependencies; TASK_363D tests must not be appended to them.

### Dependency And Recovery Gate

TASK_363C remains `blocked_by_TASK_363D`. It can resume only after TASK_363D
implementation, Reviewer/QA acceptance, Integrator package acceptance, a TASK_363C
dependency reconciliation, and renewed TASK_363C user authorization, unless an explicit
dependency-release gate records a different safe sequence. TASK_363D authorization does
not authorize or resume TASK_363C implementation.

## Authorized May Touch / Locks

Authorized May Touch and locks are exactly those in the task. The bounded helper is
`backend/application/fee_evaluation_pricing_draft_automatic_build.py`. A narrow private
result/refactor in `backend/application/confirmed_matrix_fee_draft_service.py` is allowed
only to expose values, safety inputs, and source context already obtained in one build;
it cannot change authority selection or Fee behavior. The V2 codec, attestation helper,
persistence orchestration, authority-context adapter, and safe-rebase policy may consume
that private result. Each new module remains below 500 physical lines.

Focused tests add `tests/unit/test_fee_pricing_draft_automatic_build_safety.py` plus the
bounded codec/persistence/rebase/API modules named in the task. `payload_json` remains
the only persistence boundary. Repository schema, public API/DTO/client, frontend, Fee
rules/formulae, and authority writes are locked. Any proved need for them returns to
Planner/Reviewer.

## Risks

- Snapshot bloat: bound row count and serialized bytes and fail closed before CAS.
- Incomplete authority metadata: block attestation creation rather than store an
  unverifiable defaults payload.
- TOCTOU between values and safety: one application build must own defaults, safety,
  and source context; a second provider read is a test failure.
- Flattening ambiguity: safety is captured before editable placeholder conversion;
  flattened `0`/`1` values are never evidence of a usable CR authority row.
- False manual preservation: use only accepted row provenance; automatic fields always
  refresh from current defaults.
- Rollback drift: tests must run the accepted decoder against additive payload and
  verify safe strict behavior.
- Dirty-worktree contamination: exact hunk/file whitelist excludes TASK_363C/364B and
  all external residuals.

## Definition Of Ready

Reviewer implementation-readiness passed and the user explicitly approved product
implementation. The lane is ready for the Developer implementation pass within the
exact authorized files, sequencing, line-count, test, and lock boundaries in this plan.
TASK_363C remains `blocked_by_TASK_363D`.

## Next Legal Role

Developer implementation pass.
