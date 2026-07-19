# TASK_363C Dependency Release / Readiness Reconciliation Evidence

Date: 2026-07-19

Role: Planner source-of-truth reconciliation

Status: `implementation authorized / pending Developer hunk-level replay and fix pass`

TASK_ID: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`

Lane: `contact-resistance-specified-current-fee-units-authority`

## Accepted Dependency Baseline

- HEAD is TASK_363D accepted commit
  `754b79bc7370e4cecd4fc01dd576e6e7e67080fc`.
- TASK_363D accepted one immutable authority build, canonical automatic defaults,
  ordered identities, pre-flattening row safety, typed prior-default attestation,
  generation/CAS/token validation, and reviewed rebase/reload as `current_v2`.
- Integrator evidence records `154 passed`, `py_compile` passed, service size `479`,
  staged scope/trailing/no-real-mutation checks passed, and no remote push.
- This accepted baseline resolves TASK_363C's missing B4 persistence prerequisite. It
  does not accept TASK_363C product/test candidates or restore implementation authority.

## Current TASK_363C Candidate State

- B1/B2 candidate remains unaccepted: bounded target-first CR resolver, typed
  `CrSpecifiedCurrentAuthority`, hunk-only CR service routing, CR-only default-fill, and
  the unit/API test modules.
- B3 remains an unaccepted hunk-only correction to exactly two existing tests:
  `test_contact_resistance_specified_current_requires_typed_authority` and
  `test_contact_resistance_specified_current_has_no_default_without_typed_authority`.
  The prior checkpoint reported the full file green at `77 passed`; it must be replayed
  and rerun from the accepted HEAD package boundary.
- The third candidate test,
  `tests/integration/test_fee_pricing_draft_cr_measurement_plan_rebase.py`, is not an
  acceptable B4 regression yet. It only compares source-context fingerprints and calls
  `rebase_reviewed_values()` with manually supplied defaults.
- B4 must instead use TASK_363D production persistence: save an attested old
  `current_v2` draft, change the exact confirmed CR target/readings, load
  `rebase_required`, perform reviewed CAS save, reload `current_v2`, refresh automatic
  Units/Testing Fee, and preserve only proven compatible manual fields.

## Candidate Package Boundary For Reviewer

Candidate May Touch, not implementation authorization:

- `backend/application/confirmed_matrix_fee_cr_specified_current.py`
- exact CR-only hunks in `backend/application/confirmed_matrix_fee_draft_service.py`
- exact typed authority/context hunks in
  `backend/modules/fee_evaluation/fee_default_fill_models.py`
- matching internal export hunk in `backend/modules/fee_evaluation/__init__.py`
- exact CR-only hunk in
  `backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py`
- the three bounded focused test modules
- the two exact B3 test-node hunks in `tests/unit/test_fee_default_fill.py`
- TASK_363C governance/evidence/board

The worktree service diff is mixed. Its CR resolver import/rule branch/context plumbing
must be replayed hunk-by-hunk on accepted TASK_363D while preserving
`build_authority_result()` and the single-build contract. Do not stage the whole file.

## Locked / Excluded

- TASK_363D automatic-build, attestation, V2 contract/context, persistence, transition
  policy, CAS/token, and consumer-guard production files are read-only.
- `backend/api/dependencies.py`, `fee_default_fill.py`, `fee_default_fill_common.py`,
  `confirmed_matrix_fee_step_quantities.py`, and
  `tests/unit/test_confirmed_matrix_fee_draft_service.py` are locked.
- External `confirmed_matrix_fee_base_fee_policy.py`,
  `confirmed_matrix_fee_rule_resolution.py`, MFG, TASK_364B/365A/365B, frontend, API
  client, Point Profile, PDF/parser, release/dist, and all other dirty residuals remain
  excluded.
- The LLCR API residual (`expected Units 20`, actual `None`) remains external. It must
  not be fixed, attributed, or packaged under TASK_363C.
- No Fee rule/seed/price, Measurement Plan/Point Profile write, workbook/generic output,
  parser/LTR, real database/file, stage, commit, or push belongs to this reconciliation.

## Reviewer Re-Gate Questions

1. Does the exact candidate file/hunk list provide the minimal typed CR authority path
   without modifying TASK_363D or LLCR behavior?
2. Does the revised B4 production persistence test prove the accepted attestation flow
   rather than a disconnected pure merge?
3. Can the candidate be replayed and packaged from HEAD with all mixed external hunks
   excluded and the service remaining below 500 physical UTF-8 lines?

## Validation Summary

Read-only reconciliation confirmed HEAD equals the accepted TASK_363D commit and
identified all TASK_363C candidates as unaccepted worktree changes. Product tests were
not rerun in this docs-only pass. Targeted governance diff-check, trailing-whitespace,
current-stage/stale-planned-only, status, and staging scans passed. The only remaining
`planned-only` occurrences are inside explicitly labeled historical/superseded gate
chains. Staging remains empty.

## B5 Source-Of-Truth Correction

- Reviewer B5 identified one current-stage sentence that still described TASK_363D as
  planned-only. It is superseded by TASK_363D complete/accepted commit
  `754b79bc7370e4cecd4fc01dd576e6e7e67080fc`.
- The TASK_363C current-phase contract now records dependency release for Reviewer
  re-gating only. Historical `planned-only` text is retained only inside gate-chain
  history and is explicitly labeled historical/superseded.
- Reviewer dependency-release/readiness re-gate passed and the user renewed explicit
  TASK_363C implementation approval. B1-B4 replay, production attestation persistence,
  mixed-hunk isolation, and the external LLCR residual exclusion remain unchanged.

## Final Renewed Authorization Reconciliation

- Authorized scope is limited to B1/B2 target-first typed CR authority, exact CR Fee
  routing, CR-only structured default/tier, the two exact B3 legacy-test nodes, and the
  bounded B4 production attestation persistence regression.
- The B3 legacy test file may receive only those two exact node hunks and its physical
  line count must not increase.
- B4 must exercise saved attested V2 -> changed confirmed CR authority -> non-current ->
  reviewed rebase -> CAS save -> reload/current_v2, refreshing automatic Units/Testing
  Fee while preserving proven compatible manual Unit Price/discount fields.
- The mixed Fee draft service must be replayed hunk-by-hunk from accepted TASK_363D;
  wholesale staging is forbidden. TASK_363D production files remain read-only.
- LLCR/Point Profile, the external LLCR API residual, CR Base Fee automation, seeds,
  frontend/API client, outputs, parser/LTR, real data/files, and all parallel residuals
  remain excluded.
- Final reconciliation scans found consistent implementation-authorized status, no
  stale current unauthorized state, clean trailing whitespace and board diff-check,
  and an empty staging area. No product/test or real-data operation was performed.

## Next Legal Role

Developer implementation replay/fix pass. No later Reviewer/QA/Integrator role is
executed by this reconciliation.
