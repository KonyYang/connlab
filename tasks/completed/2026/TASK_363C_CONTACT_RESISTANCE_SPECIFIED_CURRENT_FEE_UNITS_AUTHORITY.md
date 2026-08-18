# TASK_363C Contact Resistance Specified Current Fee Units Authority

## Status

`complete / accepted`

Reviewer plan gate passed, the user approved Developer planning-first, the Developer
docs-only planning-first pass completed, Reviewer implementation-readiness passed, and
the user approved the original bounded implementation. That authorization was suspended
when B4 proved a persisted prior automatic-default/authority attestation was required.
TASK_363D completed/was accepted at
`754b79bc7370e4cecd4fc01dd576e6e7e67080fc`; the dependency-release/readiness re-gate
passed, the user renewed approval, and TASK_363C subsequently passed Developer,
Reviewer, QA, and Integrator gates. The accepted local commit is
`2dac189d9b45eb68382af216e8144c6140869a71`; remote push was not performed.

The accepted package includes B1/B2, the exact B3 legacy-test corrections, and the B4
production attestation persistence regression. Earlier unaccepted/replay descriptions
below are historical implementation-contract context and are superseded by this
closeout.

## Lane

`contact-resistance-specified-current-fee-units-authority`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board active task: none is selected by TASK_363C closeout. TASK_364B and
  TASK_365A/B retain their independent states; this reconciliation does not choose
  among them or activate another product lane.
- TASK_363D is complete/accepted at
  `754b79bc7370e4cecd4fc01dd576e6e7e67080fc`. Reviewer passed the dependency-release/
  readiness re-gate and the user renewed explicit approval. The bounded package is now
  accepted at `2dac189d9b45eb68382af216e8144c6140869a71`; this pass records closeout only.
- Upstream accepted facts include TASK_361E confirmed Measurement Plan consumers,
  TASK_361L V2 pricing-draft currentness, TASK_362A/r6 Fee rules, and TASK_363B at
  `1961d2760640c64424bd4b7b51fc3447b2ace18e`.

## Goal

Use the exact confirmed `cr_specified_current` Measurement Plan target as the only
readings authority for each Contact resistance (CR) Fee line. Calculate:

```text
CR Units = owning target readings_per_sample x owning Confirmed Matrix Group sample quantity
```

Keep the reviewed CR price tiers (`<=10` readings/specimen -> `10/reading`, `>10` ->
`5/reading`) and prevent Point Profile, source text, legacy Matrix Step quantities,
another target, or another Group from supplying CR Units.

## Confirmed Business Contract

- The rule is `fee_rule_contact_resistance_specified_current`, not LLCR.
- The target key is the exact confirmed Group + row + Step sequence + normalized suffix.
- The target must be included, usable, and have `contact_kind=cr_specified_current`.
- Every CR Fee line uses only its owning Group sample quantity.
- Multiple parsed Step tokens in one Fee line are accepted only when all exact targets
  are usable and have one homogeneous readings value/source. Values are not summed.
- `<=10` readings/specimen uses Unit Price `10`; `>10` uses Unit Price `5`.
- Unit Type remains `per reading`.
- The Unit Price Reference Base Fee range and temperature-rise waiver remain manual
  operator policy. This lane does not automate or reinterpret that policy.
- Missing, draft, stale, corrupt, omitted, excluded, affected, wrong-kind, divergent,
  or invalid authority returns typed review-required with no automatic Units write.
- Missing or invalid owning Group sample quantity returns typed review-required.
- CR never falls back to the Project Point Profile, source text, or legacy
  `ConfirmedMatrixStepQuantity`, including Measurement Plan `not_started`/`disabled`.
- LLCR and every non-CR rule keep their accepted behavior.

## Confirmed Repository Evidence

- Active r6 maps `Contact Resistance, Specified Current` to
  `fee_rule_contact_resistance_specified_current` with `reading` and the source tier
  text. The controlled source row is `29`.
- Read-only workbook verification found the CR content on visible row 29. The user's
  stated row-number offset does not change the matching business content; visible row
  28 is DCR. The workbook hash matched the controlled repository source hash and did
  not change during inspection.
- `ConfirmedMatrixFeeDraftService` currently groups LLCR and specified-current CR into
  one Step-quantity assembly path.
- `build_step_quantity_contexts()` currently requires a legacy Step quantity before it
  checks the effective Measurement Plan target.
- `_specified_current_resistance_result()` currently permits source-text readings
  fallback and uses the rule's fixed amount rather than selecting the `>10` tier.
- The confirmed consumer projection already carries exact target identity,
  `contact_kind`, inclusion, readings, revision, and fingerprint lineage.
- TASK_361L source context already includes Measurement Plan and automatic-default
  fingerprints, so changed CR authority is expected to make a saved V2 pricing draft
  non-current/rebase-required.
- TASK_364B project Point Profile CR coverage explicitly excludes Measurement Plan
  target authority and Fee consumption. It is not a CR readings source.

## Accepted Package Boundary

The accepted commit contains only this reviewed package:

- a new bounded CR authority helper under `backend/application/`, preferably
  `backend/application/confirmed_matrix_fee_cr_specified_current.py`
- `backend/application/confirmed_matrix_fee_draft_service.py` only for narrow CR
  routing to the bounded helper, preserving TASK_363D's accepted
  `build_authority_result()` and single-build contract
- `backend/modules/fee_evaluation/fee_default_fill_models.py` only for the typed
  `CrSpecifiedCurrentAuthority` and CR context fields
- `backend/modules/fee_evaluation/__init__.py` only for that internal type export if
  required by the bounded helper
- `backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py` only to consume
  structured CR readings, remove CR text fallback, and select the frozen 10/5 tier
- bounded focused tests:
  - `tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py`
  - `tests/integration/test_confirmed_matrix_fee_cr_specified_current_api.py`
  - `tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py`, rewritten
    to use TASK_363D's production attested save/load/rebase/CAS/reload boundary
- exact hunk-only updates to the two existing B3 nodes in
  `tests/unit/test_fee_default_fill.py`:
  `test_contact_resistance_specified_current_requires_typed_authority` and
  `test_contact_resistance_specified_current_has_no_default_without_typed_authority`;
  this legacy file's physical line count must not increase
- TASK_363C governance/evidence and its exact board row

`backend/application/confirmed_matrix_fee_step_quantities.py` is an inspected shared
dependency and remains locked by default. If Developer planning-first proves that a
narrow reusable primitive is required there, scope must return to Planner/Reviewer
before implementation authorization.

TASK_363D's accepted private build, V2 envelope/persistence, transition policy, prior-
defaults attestation, CAS, token, and consumer guards are read-only dependencies. No
TASK_363C change to those files is authorized.

## Must Not Touch

- active Fee seed, extension, manifest, aliases, pricing source, or discounts
- LLCR Point Profile schema, lifecycle, parser, editor, or Fee formula
- TASK_364B Point Profile CR coverage implementation or residuals
- Measurement Plan schema, lifecycle, commands, setup UI, or target mutation
- Fee UI, public DTO, API client, or visual behavior
- workbook output, Required Forms layout, Generic Test Record, or Report
- Matrix parser/import, LTR/public drive, real database, real workbook, or artifacts
- TASK_363B accepted commit/history or unrelated dirty residuals
- external `confirmed_matrix_fee_base_fee_policy.py`,
  `confirmed_matrix_fee_rule_resolution.py`, MFG/default-fill/common changes,
  `tests/unit/test_confirmed_matrix_fee_draft_service.py`, and LLCR API residuals

## Locked Paths

- `backend/modules/fee_evaluation/seeds/**`
- `frontend/**`
- `backend/api/dependencies.py`
- `backend/application/fee_rule_transition_safe_rebase.py`
- `backend/application/fee_evaluation_pricing_draft_automatic_build.py`
- `backend/application/fee_evaluation_pricing_draft_prior_defaults_attestation.py`
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_common.py`
- Point Profile and Measurement Plan storage/migration/repository/write APIs
- `.agents/**`, `docs/project_management/**`, release/dist, remote push

## Acceptance Criteria

1. Exact specified-current CR rows resolve their own confirmed
   `cr_specified_current` target by Group/row/sequence/suffix.
2. `readings_per_sample=8`, owning quantity `5` yields Units `40`, Unit Price `10`,
   Unit Type `reading`, and deterministic testing-fee subtotal under existing Base Fee
   behavior.
3. `readings_per_sample=12`, owning quantity `3` yields Units `36` and Unit Price `5`.
4. A two-Group fixture proves no cross-Group aggregation, no other-Group quantity,
   and no LLCR/other-target readings multiplier.
5. Exact target-specific confirmed Measurement Plan authority has priority and source
   metadata includes its revision/fingerprint lineage.
6. `not_started`, `disabled`, missing, stale, corrupt, omitted, excluded, affected,
   wrong-kind, divergent, or malformed target authority returns typed review-required
   and no automatic Units/Testing Fee.
7. Missing/invalid owning Group quantity returns typed review-required.
8. No CR path reads Project Point Profile, source-text readings, or legacy Matrix Step
   quantities. Divergent legacy readings in tests do not affect the result.
9. LLCR, other Fee rows, manual pricing fields, and TASK_361L V2 safe rebase remain
   unchanged.
10. A changed confirmed CR target fingerprint makes an old V2 draft non-current;
    reviewed rebase refreshes automatic Units/Testing Fee while preserving compatible
    manual fields. Load/Cancel remains zero-write.
11. Seed/manifest, frontend/API client, real DB/workbook/files, and TASK_363B have no
    TASK_363C diff.

## Validation Gate Draft

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py -q
py -m pytest tests/integration/test_confirmed_matrix_fee_cr_specified_current_api.py -q
py -m pytest tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py tests/unit/test_confirmed_matrix_fee_step_quantities.py tests/unit/test_confirmed_matrix_fee_draft_service.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py -q
py -m py_compile backend/application/confirmed_matrix_fee_cr_specified_current.py backend/application/confirmed_matrix_fee_draft_service.py backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py
git diff --check
```

Also run seed/manifest, frontend/API-client, TASK_363B, real-file, line-count,
whitelist, trailing-whitespace, and package-isolation scans.

## Merge Gate

The following chain records superseded historical gates through TASK_363D acceptance,
then the current TASK_363C gate from dependency release onward:

Planner planned-only -> Reviewer plan gate -> user approval for Developer
planning-first -> Developer docs-only planning-first -> Planner reconciliation ->
Reviewer implementation-readiness -> explicit user implementation approval ->
Developer -> Reviewer -> QA -> Integrator -> B4 dependency discovery -> TASK_363D
Reviewer plan gate -> separate user approvals, implementation, and acceptance at
`754b79bc` -> TASK_363C dependency-release/readiness reconciliation -> Reviewer
dependency-release/readiness re-gate -> renewed user approval -> Developer fix
continuation.

TASK_363D is accepted, the TASK_363C Reviewer dependency-release/readiness re-gate
passed, renewed user approval was recorded, and the bounded package completed all
remaining gates before Integrator acceptance.
Every TASK_364B/TASK_365A/TASK_365B and external worktree hunk remains excluded.

## Definition Of Ready

Complete/accepted. Integrator recorded focused CR authority/default-fill `96 passed`,
profile-consumer `9 passed`, TASK_363D attestation/rebase `27 passed`, successful
compile/package-isolation checks, local commit
`2dac189d9b45eb68382af216e8144c6140869a71`, and no remote push.

## Next Legal Role

User/Orchestrator route decision only. No new product lane is activated automatically.
