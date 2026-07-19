# TASK_364C QA Evidence - Hunk-Isolated Package Validation

**Date:** 2026-07-19
**Role:** QA / Smoke Owner
**Status:** `qa_pass` for the reconciled 12-path backend/API/storage/test package

> This evidence retains the earlier 13-path client-hunk blocker for audit history. The
> revised-boundary revalidation below is the controlling QA conclusion for TASK_364C.

## Scope And Isolation

Validated only the frozen TASK_364C baseline candidate. No product or test source was
edited, no files were staged, and no commit, push, real database, or real user file was
used.

Construction used a disposable detached worktree at
`tmp/task_364c_isolated_package`, created from accepted `HEAD`
`2dac189d9b45eb68382af216e8144c6140869a71`. The only injected paths were:

1. `backend/api/routes_contact_point_profile.py`
2. `backend/application/contact_point_profile_fingerprint.py`
3. `backend/application/contact_point_profile_lifecycle_service.py`
4. `backend/application/contact_point_profile_read_service.py`
5. `backend/infrastructure/storage/contact_point_profile_schema_migration.py`
6. `backend/infrastructure/storage/database.py`
7. `backend/infrastructure/storage/models_contact_point_profile.py`
8. `backend/infrastructure/storage/repositories/contact_point_profile_authority.py`
9. `frontend/src/api/client.ts`
10. `tests/integration/test_contact_point_profile_api.py`
11. `tests/unit/test_contact_point_profile_fingerprint.py`
12. `tests/unit/test_contact_point_profile_lifecycle.py`
13. `tests/unit/test_contact_point_profile_schema.py`

The isolated `git diff --name-only` matched that whitelist exactly. `git diff --cached
--name-only` was empty. No TASK_364B R1 selector/model/editor/CSS hunk,
`ContactMeasurementPlanSummaryCard` hunk, TASK_363C/D, TASK_365A/B/C, or other
worktree residual was injected.

`database.py` contained only the approved profile-tables addition:

```text
+        "contact_point_profile_cr_category_selections",
```

The injected `frontend/src/api/client.ts` hunk was exactly `11 additions / 0 deletions`
for the five approved CR coverage types/fields.

## Validation Performed

In the isolated worktree, with pytest temporary output contained under its own ignored
`tmp/` directory:

```powershell
py -m pytest tests/unit/test_contact_point_profile_fingerprint.py \
  tests/unit/test_contact_point_profile_lifecycle.py \
  tests/unit/test_contact_point_profile_schema.py \
  tests/integration/test_contact_point_profile_api.py -q
```

Actual result: **31 passed in 14.83s**.

Exact schema regression:

```powershell
py -m pytest tests/unit/test_contact_point_profile_schema.py::test_point_profile_schema_registers_cr_category_selection_table -q
```

Actual result: **1 passed in 1.24s**.

`py -m py_compile` over all eight isolated backend product candidates passed. The
focused suite exercises disposable SQLite fixtures only; no `data/connlab.sqlite3` or
real project file path was used.

Static package checks in the isolated tree:

- Exact whitelist: pass.
- `git diff --check`: exit 0; no non-line-ending finding.
- UTF-8 added-line trailing-whitespace scan: no match.
- Added-line real-data/path scan for `D:\\Test Project`, `D:\\PublicProject`,
  `public-drive`, `connlab.sqlite3`, `.xlsx`, and `.docx`: no match.
- Staging isolation: cached path count 0.

## Blocking Finding

The required isolated frontend build/typecheck cannot pass with only the approved
client contract hunk and without the explicitly excluded R1/SummaryCard consumer
hunks:

```powershell
cd frontend
npm run build
```

Actual result: **failed during `tsc -b`** with these four errors:

```text
src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx(34,5):
  TS2741: Property 'cr_coverage' is missing in a ProjectPointProfileRevision fixture.
src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx(13,59):
  TS2345: a ProjectPointProfileRevision fixture is missing 'cr_coverage'.
src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx(23,66):
  TS2345: a ProjectPointProfileRevision fixture is missing 'cr_coverage'.
src/features/contact-measurement-plan/useProjectPointProfileModel.ts(56,9):
  TS2322: mapped direct categories omit required 'cr_selected'.
```

Expected: the accepted `HEAD` frontend compiles with only the TASK_364C `+11/-0`
client type contract hunk.
Observed: the new required fields make excluded existing consumers and tests fail type
checking. Including those files would violate the frozen package boundary, so QA did
not broaden the whitelist.

## Frozen Metadata Mismatch

The authorization/task/evidence claim that the exact backend/API/storage/test candidate
is `581 additions / 17 deletions` and that the schema migration is 384 UTF-8 physical
lines. The actual isolated diff assembled from the current source exact paths is
`596 additions / 17 deletions`, and both the source and isolated schema migration file
measure **203 UTF-8 physical lines**. This prevents QA from attesting that the current
candidate equals the documented frozen baseline, independently of the frontend build
failure.

## Previous QA Decision (Superseded)

**QA gate: blocked.**

Return to the **Planner / Integrator package owner** for source-of-truth package
reconciliation. They must decide, without mixing TASK_364B R1, whether the client
contract needs a bounded compatibility shape or whether the required consumer/type-test
changes belong to a separately reconciled package. They must also reconcile the frozen
`581/17` and 384-line metadata with the actual candidate before another QA isolation
run. TASK_364B R1 remains excluded and is not released by this result.

## Reconciled 12-Path QA Revalidation

**Executed:** 2026-07-19
**Boundary source:**
`docs/lane_evidence/TASK_364C_project-point-profile-cr-coverage-authority-baseline-package_qa_blocker_reconciliation_planner.md`

The Planner/Reviewer reconciliation removed `frontend/src/api/client.ts` from
TASK_364C and deferred its type contract plus consumer/fixture compatibility work to
TASK_364B. The revised package is limited to the eight backend/API/storage candidates
and four focused tests already enumerated above, excluding the former item 9
(`frontend/src/api/client.ts`). No frontend build/typecheck applies to this backend-only
TASK_364C boundary.

A new disposable detached-HEAD worktree was constructed at
`tmp/task_364c_backend12_isolated` from
`2dac189d9b45eb68382af216e8144c6140869a71`; only the revised twelve paths were injected.
The worktree contains no client hunk, R1 selector/model/editor/CSS, SummaryCard, or
other residual hunk.

Commands and actual results:

```powershell
py -m pytest tests/unit/test_contact_point_profile_fingerprint.py \
  tests/unit/test_contact_point_profile_lifecycle.py \
  tests/unit/test_contact_point_profile_schema.py \
  tests/integration/test_contact_point_profile_api.py -q \
  --basetemp=tmp\task_364c_backend12_pytest
# 31 passed in 19.74s

py -m pytest tests/unit/test_contact_point_profile_schema.py::test_point_profile_schema_registers_cr_category_selection_table -q \
  --basetemp=tmp\task_364c_backend12_schema
# 1 passed in 1.43s

py -m py_compile backend/api/routes_contact_point_profile.py \
  backend/application/contact_point_profile_fingerprint.py \
  backend/application/contact_point_profile_lifecycle_service.py \
  backend/application/contact_point_profile_read_service.py \
  backend/infrastructure/storage/contact_point_profile_schema_migration.py \
  backend/infrastructure/storage/database.py \
  backend/infrastructure/storage/models_contact_point_profile.py \
  backend/infrastructure/storage/repositories/contact_point_profile_authority.py
# passed
```

The exact schema node uses disposable SQLite, calls `init_db()`, and verifies that the
CR selection table is absent before the observed bootstrap then present afterward with
the expected foreign key and unique constraints. No real database or business file was
accessed.

Isolated static/package audit:

- Whitelist match: true; 12 modified paths only.
- `frontend/src/api/client.ts` included: false.
- R1/SummaryCard/frontend path included: 0.
- Candidate numstat: `596 additions / 17 deletions`.
- Migration UTF-8 physical lines: 203; schema test UTF-8 physical lines: 384.
- `database.py` approved selection-table profile-list hunk count: 1.
- `git diff --check`: exit 0 with no non-line-ending finding.
- Added-line trailing whitespace: 0; added-line real-path mutation markers: 0.
- Cached/staged path count: 0; `data/` status count: 0.

## Current QA Decision

**QA gate: pass** for the reconciled TASK_364C 12-path backend/API/storage/test baseline.

TASK_364B remains Integrator blocked and its client-plus-consumer package is not
validated or released by this result. The next legal action is Planner/Orchestrator
governance routing; do not route TASK_364B directly to Integrator from this QA result.
