# TASK_364C QA Blocker Package-Boundary Reconciliation

Date: 2026-07-19

Role: Planner / package owner

Status: `QA passed / pending Integrator baseline packaging`

## Source Evidence

- QA evidence:
  `docs/lane_evidence/TASK_364C_project-point-profile-cr-coverage-authority-baseline-package_qa.md`
- Accepted HEAD used by QA: `2dac189d9b45eb68382af216e8144c6140869a71`.
- QA's isolated 13-path candidate passed the four-module backend suite (`31 passed`),
  exact schema node (`1 passed`), eight-module py_compile, diff/trailing/path/staging
  scans, and did not access real DB/files.

## Blocker Resolution

The exact `frontend/src/api/client.ts` 11-addition type hunk is not self-contained when
applied without TASK_364B consumers. `tsc -b` reported four errors: three existing test
fixtures omitted required `cr_coverage`, and the existing model mapping omitted required
`cr_selected`.

TASK_364C is therefore narrowed to the backend/API/storage authority baseline only:

1. eight exact backend/API/storage product paths;
2. four focused tests, including the already authorized schema assertion;
3. no frontend or client path.

The exact client hunk is deferred to TASK_364B. After TASK_364C is accepted, TASK_364B
must receive a separate Reviewer package-boundary re-gate that freezes a self-contained
client-plus-consumer/fixture whitelist. This reconciliation does not authorize adding
SummaryCard, R1, compatibility, or optional-field product hunks.

## Frozen Package Facts

- Revised TASK_364C whitelist: 12 paths.
- Revised candidate diff: 596 additions / 17 deletions.
- Historical 581/17: superseded pre-test-only-assertion count.
- `contact_point_profile_schema_migration.py`: 203 UTF-8 physical lines.
- `test_contact_point_profile_schema.py`: 384 UTF-8 physical lines.
- Exact test baseline: `31 passed`; exact schema node: `1 passed`.
- No frontend build gate applies to TASK_364C after client exclusion.

## Locks

- No product/test edit or new compatibility hunk.
- No `frontend/src/api/client.ts` or consumer/fixture hunk in TASK_364C.
- No TASK_364B R1/SummaryCard/CSS/QA artifact packaging in this baseline.
- No TASK_363C/D, TASK_365A/B/C, downstream authority/consumer, real DB/file, or
  external residual absorption.
- No stage, commit, push, or Integrator retry.

## Validation And Route

Governance diff-check, no-index checks for untracked governance files, UTF-8
trailing/stale metadata scans, targeted status, and staging-empty checks passed. Only
the intended governance paths changed in this Planner action; existing external
worktree residuals remain untouched. The next legal role is Reviewer package-boundary
re-gate. Reviewer passed that boundary and QA passed the revised 12-path backend/test
package. TASK_364B remains Integrator blocked until TASK_364C is accepted and its own
client-plus-consumer package re-gate passes.
