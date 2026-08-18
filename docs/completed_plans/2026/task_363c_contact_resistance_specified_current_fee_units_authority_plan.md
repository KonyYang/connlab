# TASK_363C Contact Resistance Specified Current Fee Units Authority Plan

## Status

`complete / accepted`

Reviewer plan gate passed, the user approved Developer planning-first, Developer
completed the docs-only planning-first pass, Reviewer implementation-readiness passed,
and the user approved the original bounded product scope. That authorization was later
suspended when B4 proved a persisted prior automatic-default/authority attestation was
required. TASK_363D is now complete/accepted at `754b79bc`; Reviewer passed the
dependency-release/readiness re-gate and the user renewed explicit implementation
approval for the bounded replay/fix package. That package subsequently passed Reviewer,
QA, and Integrator gates and was accepted locally as
`2dac189d9b45eb68382af216e8144c6140869a71`; remote push was not performed.

## Dependency Release Reconciliation

- Accepted TASK_363D supplies the single-authority-build result, pre-flattening CR row
  safety, typed prior-default attestation, generation/CAS/token, and reviewed rebase
  baseline required by B4.
- B1/B2 CR resolver, typed authority transport, service routing, CR default-fill, and
  three focused test modules were accepted in the TASK_363C package.
- B3's two exact `test_fee_default_fill.py` corrections were validated at `77 passed`
  before TASK_363D acceptance and were later accepted through exact hunk isolation
  without absorbing unrelated legacy-test changes.
- B4 was replaced by the production attestation persistence regression: attested old
  `current_v2` save, changed confirmed CR target/readings, `rebase_required`, reviewed
  CAS save, `current_v2` reload, automatic Units/Testing Fee refresh, and compatible
  manual-field preservation.
- TASK_363D production attestation files remained unchanged and read-only.

## 1. Discovery Summary

### Confirmed By User

- Specified-current CR is a separate rule from LLCR.
- The formula is `confirmed CR readings_per_sample x owning Group sample quantity`.
- Authority is the exact confirmed CR specified-current Measurement Plan target.
- No Project Point Profile, text, legacy Step quantity, cross-Group, or cross-test
  fallback is allowed.
- The reviewed tiers remain `10/reading` through 10 readings/specimen and `5/reading`
  above 10.
- Base Fee `100~300` and the temperature-rise waiver remain manual.
- Typed review/no-write is required for absent, unusable, stale, affected, excluded,
  corrupt, or invalid authority.

### Confirmed By Repository Evidence

- Active r6 already matches the browser label to
  `fee_rule_contact_resistance_specified_current`.
- The active seed stores amount `10`, Unit Type `reading`, and source text for both the
  10 and 5 tiers. Its controlled source row is 29.
- A read-only COM inspection of
  `D:\Template\FDQF-E-176 Testing Fee Evaluation_Rev_F-v1.xls` found the stated CR
  content at visible row 29; row 28 is DCR. SHA-256
  `FB788038631AA0A12F1A052B630513718D9FA1BB64BAE647E897E18529EF8A5D`
  and file metadata were unchanged after the read and match the controlled source
  snapshot.
- Current assembly requires legacy Step quantity before using a confirmed Measurement
  Plan target and drops `contact_kind` from its local lookup.
- Current CR default fill can parse readings from text and does not apply the >10 tier.
- The typed confirmed consumer already exposes target identity, kind, inclusion,
  readings, status, revision, fingerprint, and diagnostics.
- V2 pricing-draft currentness already includes Measurement Plan and canonical
  automatic-default fingerprints across production persistence composition.
- Current dirty TASK_364B and Fee frontend/API work are external. TASK_364B expressly
  does not make Point Profile CR coverage a Fee or target quantity authority.

### Planner Inference

- This is a backend authority-consumption corrective, not a seed or UI task.
- A dedicated CR helper is safer than extending the accepted 479-line Fee draft service or
  weakening shared LLCR behavior.
- The exact CR target must be selected before legacy Step quantity lookup. Its
  `contact_kind` must be validated rather than inferred from a matched Fee rule.
- The B4 persistence probe proved that TASK_361L alone could not attest prior CR
  automatic defaults across changed Measurement Plan lineage. Accepted TASK_363D now
  supplies that missing single-build persisted attestation without weakening the
  existing fail-closed policy. TASK_363C must consume and verify that production path.

### Not Yet Confirmed

No blocker for plan review. Private helper names and exact typed diagnostic codes may
follow existing conventions, but their semantics must remain one-to-one with this
contract.

## 2. Authority Selection Contract

For each CR Fee row:

1. Require matched rule id `fee_rule_contact_resistance_specified_current`.
2. Parse the Matrix Step tokens using the existing parser without changing it.
3. Build the canonical key:
   `(confirmed_group_id, confirmed_row_id, step_sequence, normalized_suffix)`.
4. Load the effective confirmed Measurement Plan once for the project.
5. Resolve the exact target and validate:
   - authority status permits the exact target;
   - target exists and is unaffected;
   - `included=true`;
   - `contact_kind=cr_specified_current`;
   - `readings_per_sample` is a positive, finite, canonical numeric value;
   - revision/fingerprint lineage is present and valid.
6. If a Fee line has multiple Step tokens, require every exact target to pass and all
   readings/source lineage to be homogeneous. Do not sum across Steps.
7. Parse only the owning Group sample quantity through the accepted group-quantity
   parser. Missing, zero/negative, marker, or malformed values block.
8. Calculate Units from the frozen formula.

Status policy:

- `complete` / `partial_compatible` / `needs_review`: an exact unaffected compatible
  target may be consumed; omission, exclusion, affected target, or relevant diagnostic
  blocks that line.
- `not_started` / `disabled`: block CR with a typed authority message. Unlike LLCR,
  there is no Point Profile or legacy fallback.
- `authority_corrupt`, missing provider/snapshot, stale identity, malformed target, or
  mixed source: block and do not auto-write Units or Testing Fee.

## 3. Calculation Contract

```text
readings = exact confirmed CR target readings_per_sample
samples = owning Confirmed Matrix Group sample quantity
units = readings * samples
unit_price = 10 when readings <= 10, otherwise 5
unit_type = per reading
testing_fee = unit_price * units under the existing numeric Base Fee/discount behavior
```

This lane does not choose the textual `100~300` Base Fee or decide the temperature-rise
waiver. It must not convert that policy into a new automatic amount. Existing manual
Fee edits and V2 provenance remain protected. Reviewer should verify that the UI's
existing Base Fee review behavior remains unchanged while the CR Units/tier calculation
becomes deterministic.

## 4. No-Fallback Contract

The CR path must not consume:

- Project Point Profile, including TASK_364B CR category coverage;
- LLCR target or LLCR readings;
- source Matrix prose such as `10 readings/specimen`;
- legacy `ConfirmedMatrixStepQuantity` values;
- another Group, row, sequence, suffix, or contact kind;
- a saved V2 pricing-draft automatic value whose source context is non-current.

Tests must deliberately provide plausible conflicting values in each forbidden source
so accidental fallback is observable.

## 5. V2 Pricing-Draft And Production Consumer Boundary

TASK_361L remains the persistence/currentness authority:

- a change in Measurement Plan revision/fingerprint or automatic CR defaults marks the
  saved V2 envelope non-current;
- load is zero-write and returns a reviewed-rebase state;
- reviewed rebase reloads current backend defaults, refreshes automatic CR Units and
  Testing Fee, preserves only proven compatible manual fields, saves by CAS, reloads,
  and revalidates current before Update/export;
- V1, stale, blocked, mixed-provenance, or integrity-invalid drafts remain rejected by
  server consumers;
- Cancel remains zero-write.

### B4 persisted-attestation dependency reconciliation

The accepted TASK_361L contract classifies a valid V2 context/default change as
`rebase_required` when source rows are safely matchable, and reserves `blocked` for
malformed, mixed, unsafe, missing, corrupt, stale, or divergent authority. Therefore
TASK_363C keeps its changed-target B4 acceptance, but a policy-only hunk is rejected.
`FeePricingDraftSourceContext` stores only Measurement Plan status/revision/id/
fingerprint and the old automatic-default fingerprint. It does not store the old exact
target projection or prior automatic-default payload. Rebuilding "prior" defaults
through the current provider is valid only when the rebuilt fingerprint still equals
the saved fingerprint; changed CR readings correctly fail that attestation.

Accepted TASK_363D now owns the additive persisted prior-default/authority attestation
inside the existing pricing-draft `payload_json` boundary. TASK_363C may consume that
baseline only through existing production save/load/rebase APIs; it may not modify the
attestation, transition policy, token, CAS, persistence, manual provenance, reload/
revalidation, or consumer guards.

Composition regressions must cover confirmed Fee update, direct export, Required Forms,
child/subprocess export, and Matrix fee rebase where existing tests expose those paths.
TASK_363D already supplies the production pricing-draft composition; no
`backend/api/dependencies.py` change is required or eligible for TASK_363C.

## 6. File-Level Design

Accepted TASK_363C implementation sequence (historical execution record):

1. Add `backend/application/confirmed_matrix_fee_cr_specified_current.py` with a
   bounded target-first context builder and typed CR authority diagnostics.
2. Add a narrow branch in
   `backend/application/confirmed_matrix_fee_draft_service.py` that calls the CR
   helper only for the explicit rule id. LLCR retains the current path.
3. Add the typed `CrSpecifiedCurrentAuthority` transport in
   `fee_default_fill_models.py` plus the narrow package export, then update only the CR
   helper in
   `backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py` to reject
   unstructured fallback and select the 10/5 tier from structured readings.
4. Add bounded tests:
   - `tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py`
   - `tests/integration/test_confirmed_matrix_fee_cr_specified_current_api.py`
   - `tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py`
5. Replay only the two B3 CR test nodes in `tests/unit/test_fee_default_fill.py`; no
   other hunk in that currently mixed file belongs to TASK_363C, and its physical line
   count must not increase.
6. Replace the disconnected B4 test with the accepted TASK_363D production attestation
   save/load/rebase/CAS/reload flow.
7. Execute existing shared tests read-only, including:
   - `tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py`
   - `tests/unit/test_confirmed_matrix_fee_step_quantities.py`
   - `tests/unit/test_confirmed_matrix_fee_draft_service.py`
   - TASK_361L persistence/rebase/export suites
8. Rerun B4 through TASK_363D's attested prior-default boundary. TASK_363C does not own
   V2 envelope, persistence, automatic-build, attestation, or policy production files.

Current physical line facts use
`(Get-Content <path> -Encoding UTF8 | Measure-Object -Line).Lines`:

- accepted TASK_363D baseline `confirmed_matrix_fee_draft_service.py`: 479 physical
  lines; accepted TASK_363C hunk-isolated package: 497 physical lines, below the 500-line
  hard limit
- `confirmed_matrix_fee_step_quantities.py`: 204
- `contact_measurement_plan_confirmed_consumer_adapter.py`: 94
- `fee_reviewed_extension_defaults.py`: 264
- `fee_step_quantity_defaults.py`: 125
- `backend/api/dependencies.py`: locked; no TASK_363C composition change required

The CR routing hunk must preserve TASK_363D's accepted single-build method and keep the
Fee draft service below its 500-line hard limit.

## 7. May Touch / Must Not Touch / Locked Paths

### Accepted TASK_363C Package Boundary

Integrator accepted only the following exact package:

- new bounded CR application helper;
- narrow CR routing hunk in `confirmed_matrix_fee_draft_service.py`;
- typed CR authority/context additions in `fee_default_fill_models.py`;
- matching internal type export hunk in `backend/modules/fee_evaluation/__init__.py`;
- CR-only default result logic in `fee_reviewed_extension_defaults.py`;
- the three existing bounded CR focused tests;
- exact two B3 CR test-node hunks in `tests/unit/test_fee_default_fill.py`, with no
  physical-line increase in that legacy file;
- TASK_363C governance.

### Must Not Touch

- Fee seeds/extensions/manifest and price/reference data
- shared matcher/rule resolution unless a new blocker returns to Planner
- LLCR Point Profile and TASK_364B CR coverage
- Measurement Plan storage/lifecycle/write/API/UI
- public DTO/client/frontend visual behavior
- workbook or Generic output behavior
- Matrix parser/import, LTR/public drive, real data/files

### Locked

- `backend/modules/fee_evaluation/seeds/**`
- `frontend/**`
- `backend/api/dependencies.py` in full; accepted TASK_363D already owns the required
  production pricing-draft composition
- `backend/application/confirmed_matrix_fee_step_quantities.py` production hunks by
  default
- Point Profile/Measurement Plan schema and repositories
- `.agents/**`, `docs/project_management/**`, release/dist, remote push

## 8. TDD And Validation Order

1. Red unit tests for exact target key/kind/status and no-fallback behavior.
2. Red two-Group integration test with distinct readings and sample quantities.
3. Red tier boundary tests at `10` and `>10`.
4. Minimal bounded helper and routing implementation.
5. Red V2 stale/rebase tests with old automatic CR Units and compatible manual fields;
   execution depends on TASK_363D's attested prior-default boundary and unchanged
   five-state consumer guards.
6. Existing LLCR/non-CR/consumer regression execution.
7. Static, line, scope, seed, no-real-mutation, and package-isolation checks.

Required cases include:

- Group A readings 8 / samples 5 -> Units 40 / Unit Price 10;
- Group B readings 12 / samples 3 -> Units 36 / Unit Price 5;
- divergent legacy Step quantities and LLCR profile do not change either line;
- wrong-kind exact target blocks;
- missing/excluded/affected/corrupt target blocks;
- `not_started` and `disabled` block without fallback;
- invalid owning quantity blocks;
- mixed exact CR target readings on one Fee line block rather than aggregate;
- profile/LLCR/non-CR/manual field behavior remains unchanged;
- Measurement Plan reconfirm makes an old V2 draft non-current and reviewed rebase
  refreshes automatic CR fields without overriding compatible manual fields.

## 9. Package Isolation

- Accepted HEAD is TASK_363D commit
  `754b79bc7370e4cecd4fc01dd576e6e7e67080fc`.
- TASK_364B and existing Fee frontend/API worktree changes are external and must remain
  untouched.
- Governance staging must be exact-file/hunk. Future implementation must stage only
  approved CR helper/routing/default/test hunks.
- No product implementation may begin while candidate files contain unowned residuals
  unless the board records an explicit isolation decision.
- No real DB, workbook, artifact, export, or public-drive operation is permitted.

## 10. Merge Gate And Dependencies

Functional prerequisites TASK_361E, TASK_361L, TASK_362A, TASK_363A/B, and TASK_363D
are accepted.
TASK_364B is not a Fee authority dependency, but it remains a separate implementation
lane and overlaps the dirty workspace. The prior TASK_363C approval did not include
persisted prior defaults/authority. TASK_363D has now released that dependency, but
Reviewer dependency-release/readiness re-gate passed, renewed explicit user approval
was recorded, and the exact bounded package subsequently passed Reviewer/QA/Integrator.

Gate chain (historical/superseded through TASK_363D acceptance, current from the
TASK_363C readiness reconciliation onward):

```text
Planner planned-only
-> Reviewer plan gate
-> User planning-first approval
-> Developer docs-only planning-first
-> Planner reconciliation
-> Reviewer implementation-readiness
-> User implementation approval
-> Developer B3/B4 probe
-> Planner B4 dependency discovery
-> TASK_363D Reviewer plan gate and separate approval chain
-> TASK_363D acceptance
-> TASK_363C readiness reconciliation and renewed User implementation approval
-> Developer fix continuation -> Reviewer -> QA -> Integrator
```

## 11. Developer Planning-First Refinement

### Bounded implementation order

1. Add red unit tests for a pure CR target-first helper: exact Group/row/step/suffix,
   normalized suffix, `contact_kind=cr_specified_current`, included status, positive
   readings, lineage, and all no-fallback/block states. The helper must return a typed
   CR context or typed review diagnostic and must not mutate authority.
2. Add a red two-Group assembly test through the existing Fee draft public builder.
   Group A uses readings 8/sample 5 and Group B uses readings 12/sample 3, with
   conflicting legacy Step quantities and LLCR/Point Profile values. Expected CR
   results are Units 40/36 and Unit Price 10/5. A failure in the locked service
   boundary stops this lane and routes back to Planner.
3. Add red CR-only default-fill contract tests for the 10 and >10 tiers, invalid
   quantities, wrong-kind/missing target, and no text/legacy/profile fallback.
4. Implement the bounded helper in
   `backend/application/confirmed_matrix_fee_cr_specified_current.py`, then add only a
   narrow CR-only rule-id branch in the Fee draft assembly. The existing LLCR path and
   shared step-quantity builder remain behaviorally unchanged.
5. Add the smallest CR-only default result adapter needed to consume the helper context;
   it calculates `readings * owning_group_samples`, selects 10/5, preserves manual
   Base Fee/waiver behavior, and never parses prose or legacy quantities.
6. Consume the accepted TASK_363D attestation through its existing production
   persistence interfaces. Do not modify V2 policy, persistence, automatic-build, or
   attestation production files.

### Exact helper and routing contract

- Helper input is existing confirmed snapshot lineage plus one parsed Step token and the
  effective confirmed Measurement Plan projection. It builds
  `(confirmed_group_id, confirmed_row_id, step_sequence, normalized_suffix)`.
- Output carries status, exact target identity, `cr_specified_current` kind, readings,
  revision id/sequence/fingerprint, and typed diagnostics. It rejects omission,
  exclusion, affected/corrupt/stale state, wrong kind, divergent readings,
  non-positive/non-finite readings, and multiple source lineages.
- The CR branch is selected only for
  `fee_rule_contact_resistance_specified_current`; LLCR, contact-retention, non-CR,
  and pricing-draft DTO/API behavior remain unchanged.
- Multiple Step tokens require homogeneous readings and lineage; no summation. Units
  use only the current Group's validated positive sample quantity. Empty, marker,
  zero, negative, decimal-invalid, or malformed quantity returns typed review-required
  with Units/Testing Fee unset.
- `not_started`, `disabled`, missing provider/snapshot, and legacy-only inputs block CR
  directly. There is no Point Profile, text, or ConfirmedMatrixStepQuantity fallback.

### May Touch and package isolation

Accepted TASK_363C package files/hunks:

- new bounded `backend/application/confirmed_matrix_fee_cr_specified_current.py`;
- one narrow CR-only routing hunk in `backend/application/confirmed_matrix_fee_draft_service.py`;
- typed CR authority/context hunks in
  `backend/modules/fee_evaluation/fee_default_fill_models.py` and the matching export
  in `backend/modules/fee_evaluation/__init__.py`;
- CR-only default result logic in `backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py`;
- three bounded CR focused test modules;
- exact two B3 CR test-node hunks in `tests/unit/test_fee_default_fill.py`;
- TASK_363C governance/evidence.

`backend/application/confirmed_matrix_fee_step_quantities.py`, TASK_363D automatic-
build/attestation/persistence/rebase files, `backend/api/dependencies.py`,
`fee_default_fill.py`, `fee_default_fill_common.py`, Measurement Plan authority/storage/
lifecycle/API/UI, Point Profile/TASK_364B, Fee seeds/manifest, frontend/API client,
workbooks, generic outputs, parser/import, LTR/public drive, and real DB/files are
read-only or locked. The package must not absorb external base-fee/rule-resolution/MFG,
old service-test, LLCR, TASK_364B/365A/365B, or other worktree hunks. Integrator staged
only TASK_363C-owned hunks from accepted HEAD and did not stage mixed files wholesale.

Every new Python helper/test module must be below 500 physical UTF-8 lines. Validate
with `Path.read_text(encoding="utf-8").splitlines()` without suppressing blank lines,
plus exact whitelist, diff/trailing, seed-lock, forbidden-scope, and no-real-mutation
scans.

## 12. Definition Of Ready

Complete/accepted. TASK_363D remains accepted at `754b79bc`; TASK_363C completed its
dependency-release/readiness, renewed approval, Developer, Reviewer, QA, and Integrator
gates. Integrator recorded `96 + 9 + 27` passing tests, package isolation, local commit
`2dac189d9b45eb68382af216e8144c6140869a71`, and no remote push.

## 13. Next Legal Role

User/Orchestrator route decision only. No later product lane is activated by this
closeout.
