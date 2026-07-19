# TASK_363C Planner Discovery Evidence

## Routing

- Task: `TASK_363C_CONTACT_RESISTANCE_SPECIFIED_CURRENT_FEE_UNITS_AUTHORITY`
- Lane: `contact-resistance-specified-current-fee-units-authority`
- Role: Planner final renewed-authorization reconciliation
- Status: `implementation authorized / pending Developer hunk-level replay and fix pass`
- Implementation: authorized only for the reviewed bounded TASK_363C replay/fix package
- Date: 2026-07-19

## Current Phase / Active Task / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Board active lane remains TASK_365C pending user acceptance; TASK_365A/B and
  TASK_364B retain their separate parallel gate states.
- This pass is allowed because it changes TASK_363C governance only after TASK_363D
  Integrator acceptance released its declared dependency. It does not route Developer
  or alter any parallel lane.

## User Goal

Connect specified-current CR Fee rows to their own exact confirmed Measurement Plan
readings and owning Group sample quantity. Preserve CR/LLCR separation, reviewed tier
pricing, typed failure behavior, V2 safe rebase, and all existing consumer locks.

## Confirmed By User

- Formula: CR Units = confirmed CR readings/sample x owning Group sample quantity.
- CR uses only its confirmed `cr_specified_current` target.
- No LLCR Point Profile, text, legacy Step quantity, cross-Group, or wrong-test fallback.
- Price tiers remain 10/reading through 10 and 5/reading above 10.
- Base Fee range/waiver remains manual.
- Unusable authority or invalid sample quantity is review-required/no-write.
- Two-Group and V2 safe-rebase regressions are mandatory.

## Confirmed By Repository Evidence

- r6 alias and Unit Type already match; the browser's missing field is Units.
- Controlled seed source row is 29 and contains both CR tiers.
- The read-only source workbook contains matching CR content at visible row 29; the
  user's row-number offset is non-blocking. Workbook hash and metadata did not change.
- Existing assembly checks legacy Step quantity before the Measurement Plan target.
- Existing CR default logic allows text fallback and currently uses fixed amount 10.
- Effective Measurement Plan target DTO contains exact identity, kind, inclusion,
  readings, and confirmed lineage.
- V2 currentness includes Measurement Plan and automatic-default fingerprints.
- TASK_364B excludes Fee/Measurement Plan target authority and cannot supply CR Units.
- HEAD is accepted TASK_363D commit
  `754b79bc7370e4cecd4fc01dd576e6e7e67080fc`; all visible TASK_364B/365A/365B and other
  worktree changes remain external residuals.

## Planner Decisions

1. Create an independent backend-only planned lane.
2. Use a target-first CR-specific helper; do not broaden the shared LLCR path.
3. Require exact Group/row/sequence/suffix and `contact_kind=cr_specified_current`.
4. Block `not_started`/`disabled` for CR; do not inherit LLCR fallback policy.
5. Require homogeneous target readings for multiple tokens and never aggregate.
6. Select the 10/5 tier from authoritative readings without changing seed/manifest.
7. Keep textual Base Fee/waiver automation outside scope and preserve manual edits.
8. Reviewer proved that a policy-only hunk cannot attest changed CR readings. Accepted
   TASK_363D now supplies the persisted prior-default/safety attestation; TASK_363C may
   consume but must not modify that boundary.
9. Keep TASK_363C isolated from TASK_364B/365A/365B and all external residuals. Reviewer
   dependency-release/readiness passed and renewed user authorization is recorded.

## Dependency Release / Remaining Gate

TASK_363D is accepted and provides the private single-authority-build result,
pre-flattening CR row safety, typed automatic-default attestation, and CAS/reload/
`current_v2` baseline required by B4. Reviewer passed the dependency-release/readiness
re-gate and the user renewed explicit implementation approval. Existing candidate
hunks remain unaccepted until Developer replays and validates them.

B1/B2 resolver, typed authority transport, CR-only service/default-fill, and three test
modules remain unaccepted. B3's two exact old-test corrections were previously green at
`77 passed` but remain unaccepted. The current B4 test is still a disconnected pure-
merge example and must later be rewritten through TASK_363D's production attested save,
lineage change, `rebase_required`, reviewed CAS save, and `current_v2` reload.

## Scope Summary

Authorized May Touch is the bounded CR resolver, typed CR authority
and internal export, hunk-only CR service routing, CR-only reviewed default, three
focused modules, and the two exact B3 test nodes. TASK_363D automatic-build/attestation/
persistence/rebase files, `backend/api/dependencies.py`, `fee_default_fill.py/common`,
old service tests, external base-fee/rule-resolution/MFG hunks, seeds, frontend/API
client, authority writes, LLCR, outputs, parser/LTR, real files, and dirty residuals
remain locked.

## Validation Draft

- exact target/kind/status unit tests;
- two-Group API assembly with readings `8`/`12` and sample quantities `5`/`3`;
- Units `40`/`36`, tiers `10`/`5`, no cross-Group/no legacy/no LLCR fallback;
- wrong-kind, omitted, excluded, affected, corrupt, not-started, disabled, mixed, and
  invalid sample quantity review-required/no-write;
- V2 Measurement Plan lineage stale/rebase and manual-field preservation;
- LLCR/non-CR/export/Required Forms/Matrix rebase read-only regressions;
- py_compile, diff/trailing/line/whitelist/seed/no-real/package-isolation scans.

## Definition Of Ready

Satisfied for bounded Developer replay/fix. Reviewer dependency-release/readiness passed
and the user renewed TASK_363C implementation approval.

## Next Legal Role

Developer implementation replay/fix pass for TASK_363C.
