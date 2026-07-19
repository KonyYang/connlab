# TASK_364C Project Point Profile CR Coverage Authority Baseline Package

## Status

`complete / Integrator accepted`

No product implementation, staging, commit, or integration is authorized. The user
explicitly authorized one bounded test assertion only.

## Current Phase / Active Task / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: Planner package-owner reconciliation after QA isolation blocker.
- TASK_364B is user accepted but Integrator blocked because its R1 frontend candidate
  imports a CR coverage client contract absent from accepted HEAD.
- The user authorized a docs-only A/B decision. Repository evidence requires a serial
  backend/API/storage authority baseline before packaging R1. QA proved that the
  required client types cannot compile without their R1 consumers, so the client hunk
  is deferred to the later TASK_364B package re-gate.

## Goal

Create a self-contained accepted backend/API/storage baseline for the already
implemented Project Point Profile CR coverage authority contract. This is a packaging
lane for existing candidate hunks, not authorization to write or redesign product
behavior. Frontend client types and consumers remain outside this baseline.

## Lane Control

- Lane: `project-point-profile-cr-coverage-authority-baseline-package`
- Type: docs/review/qa/integration package baseline
- Owner now: Planner reconciliation; next owner: Integrator baseline packaging
- Branch/worktree: current shared worktree, read-only until Reviewer approves an exact
  isolated package; no branch creation or staging in this pass
- Depends on: accepted HEAD `2dac189d`; blocks TASK_364B R1 packaging
- Conflict scope: Point Profile CR coverage backend/API/storage authority only
- Evidence:
  `docs/lane_evidence/TASK_364C_project-point-profile-cr-coverage-authority-baseline-package_planner.md`

## Confirmed Repository Facts

- Accepted HEAD is `2dac189d9b45eb68382af216e8144c6140869a71`.
- HEAD contains no backend or client references to `cr_coverage`, `cr_selected`, or
  `follow_llcr`.
- `frontend/src/api/client.ts` has one mixed-file hunk with 11 additions and no
  deletions. QA proved that applying it alone causes four TypeScript errors in excluded
  production/test consumers. It is not part of TASK_364C and remains deferred to the
  TASK_364B package re-gate.
- The corresponding backend/API/storage candidate remains unaccepted: 596 additions
  and 17 deletions across eight product files and four focused tests. The eighth file
  is the required one-line `database.py` profile-table exclusion hunk.
- The migration module is 203 UTF-8 physical lines. The separately authorized schema
  test is 384 UTF-8 physical lines. These are distinct files and both remain below 500.
- No generated client artifact or separate backend commit supplies this contract.

## Exact Candidate May Touch For Review

Product candidate, existing hunks only:

- `backend/infrastructure/storage/models_contact_point_profile.py`
- `backend/infrastructure/storage/contact_point_profile_schema_migration.py`
- `backend/infrastructure/storage/repositories/contact_point_profile_authority.py`
- `backend/infrastructure/storage/database.py`, only the one-line addition of
  `contact_point_profile_cr_category_selections` to `init_db().profile_tables`
- `backend/application/contact_point_profile_fingerprint.py`
- `backend/application/contact_point_profile_lifecycle_service.py`
- `backend/application/contact_point_profile_read_service.py`
- `backend/api/routes_contact_point_profile.py`
Focused candidate tests:

- `tests/unit/test_contact_point_profile_fingerprint.py`
- `tests/unit/test_contact_point_profile_lifecycle.py`
- `tests/unit/test_contact_point_profile_schema.py`
- `tests/integration/test_contact_point_profile_api.py`

The only future test edit that may be proposed after gate approval is one bounded
assertion in `tests/unit/test_contact_point_profile_schema.py` proving that generic
`Base.metadata.create_all()` excludes the CR selection table and that `init_db()`
creates and verifies it only through the dedicated Point Profile bootstrap. No other
test expansion is implied. The user has now explicitly authorized this assertion.

## Exact Developer Tests-Only Authorization

Developer may modify only:

- `tests/unit/test_contact_point_profile_schema.py`

The change must add or migrate one bounded assertion that proves both:

1. generic `Base.metadata.create_all()` does not create
   `contact_point_profile_cr_category_selections`; and
2. real `init_db()` against disposable temporary SQLite creates and read-verifies that
   table through the dedicated Point Profile bootstrap.

The authorization-time 323-line estimate was stale. Developer measured 369 physical
lines before the pass and the current UTF-8 physical count is 384, still below 500.
Existing fixtures/helpers were reused. No product file, other test file, staging area,
real DB/file, or external lane may be changed.

Governance:

- this task, its plan/evidence, TASK_364B package-boundary reconciliation, and exact
  TASK_364B/TASK_364C board hunks

## Must Not Touch / Locked Paths

- No product edits. The one-line `database.py` candidate already exists and is read-only
  for Developer. Only the exact schema-test assertion above is implementation-authorized.
- No `frontend/src/api/client.ts` hunk in TASK_364C. Its exact 11-addition contract is
  deferred to TASK_364B and may be packaged only with a Reviewer-approved,
  self-contained consumer/fixture boundary.
- No TASK_364B R1 selectors, hook, editor, CSS, SummaryCard, or QA PNG in the baseline
  package.
- No Matrix Group totals, Measurement Plan authority, Fee, workbook, Generic Test
  Record/Report, parser/import, LTR/public drive, real DB/files, release/dist, or
  dependencies.
- No TASK_363C/D, TASK_365A/B/C, or other dirty residuals.
- No `.agents/**`, `docs/project_management/**`, stage, commit, or push before gates.

## Validation Gate

- Reviewer confirms every candidate hunk belongs to the frozen CR coverage authority
  contract and that no hidden backend/client dependency is missing.
- Re-run the exact four-module package command; the reproducible baseline is
  `31 passed`, not the broader historical TASK_364B `46 passed` suite.
- TASK_364C has no frontend/client path after this reconciliation, so frontend
  build/typecheck is not a gate for this backend-only baseline.
- TASK_364B must later provide its own hunk-isolated frontend build/typecheck with the
  exact client contract and all Reviewer-approved required consumers/fixtures.
- Run diff-check, UTF-8 trailing, exact whitelist, staging-empty, and no-real-mutation
  scans.

## Merge Gate

Reviewer package-boundary re-gate, QA validation of the revised 12-path backend/test
package, and Integrator hunk-isolated baseline packaging. TASK_364B remains blocked
until this baseline is accepted, then requires its own client-plus-consumer package
re-gate before Integrator retry.

## Definition Of Ready

Developer's exact assertion and Reviewer test-only diff gate are complete. QA found a
package-boundary blocker rather than a product defect, Planner narrowed the package,
Reviewer passed the revised boundary, and QA passed the isolated 12-path backend-only
package. No further product implementation is authorized; only Integrator packaging of
the frozen baseline is ready.

## Next Legal Role

Integrator packaging/readiness for the revised 12-path backend/test baseline only.
