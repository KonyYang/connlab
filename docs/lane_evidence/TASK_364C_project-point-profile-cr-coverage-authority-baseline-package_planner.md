# TASK_364C CR Coverage Authority Baseline Package Planner Evidence

Date: 2026-07-19

Role: Planner package-boundary reconciliation

Status: `QA passed / pending Integrator baseline packaging`

## Discovery Result

Confirmed by user:

- TASK_364B must not be packaged if its approved frontend hunks are not self-contained.
- A client-only exact hunk is legal only when the accepted backend authority already
  provides the matching contract; otherwise a serial accepted baseline is required.
- This pass is docs-only and may route only to Reviewer package-boundary re-gate.

Confirmed by repository evidence:

- HEAD is `2dac189d9b45eb68382af216e8144c6140869a71`.
- `git grep` finds no `cr_coverage`, `cr_selected`, or `follow_llcr` contract in HEAD.
- The client candidate is one 11-addition type hunk with no method or serialization
  change.
- The runtime contract remains dirty in eight backend/API/storage files plus four
  focused tests; after the authorized schema assertion their aggregate current
  candidate diff is 596 additions and 17 deletions. The required eighth product hunk
  is one line in `database.py`.
- Existing TASK_364B task/plan authorized this backend/API/client contract during
  implementation, but the later R1 package reconciliation excluded it and never made
  it an accepted HEAD baseline.

Planner conclusion:

- Path A is invalid because the accepted backend baseline does not exist.
- Path B is required. TASK_364C serializes review and packaging of the existing
  backend/API/storage authority candidate before TASK_364B R1 may return to a separate
  client-plus-consumer package re-gate.
- No new business behavior, implementation, or user authorization is inferred.

Not yet confirmed:

- Reviewer must confirm that each backend/test candidate hunk is cleanly attributable
  to the frozen baseline and has no hidden external dependency.
- Integrator package authority remains unavailable until Reviewer/QA gates pass.

## Validation Performed

- Inspected HEAD and worktree client diff: exact 11 additions, no deletions.
- Inspected HEAD contract search: no matching accepted references.
- Inspected backend/API/storage/test candidate status and diff statistics.
- Inspected TASK_364B task, base/R1 plans, Developer/Reviewer/QA evidence, prior final
  reconciliation, and board.
- Current governance stale-status scan found no active `pending Integrator` or
  `accepted backend contract` wording for TASK_364B.
- UTF-8 trailing-whitespace scan was clean.
- Tracked board diff-check and no-index checks for the untracked governance files were
  clean; only repository LF/CRLF conversion notices were emitted.
- Staging is empty. Existing product/test and external-lane worktree residuals remain
  untouched and excluded.
- No product/test file, real DB/file, staging area, commit, or remote was modified.

## B1/B2 Package-Boundary Fix

- B1 accepted: the exact one-line `backend/infrastructure/storage/database.py` hunk is
  part of the baseline whitelist. It prevents generic `Base.metadata.create_all()`
  from pre-creating the CR selection table before dedicated bootstrap validation and
  transaction ownership.
- The future validation boundary permits one bounded assertion in
  `tests/unit/test_contact_point_profile_schema.py` for that ordering. This Planner
  pass does not implement it.
- B2 accepted: the four exact package test modules reproduce `31 passed`. The broader
  historical TASK_364B seven-module suite produced `46 passed`, but those extra fifteen
  tests are not inferred into TASK_364C.
- No hunk-isolated frontend build artifact exists yet. QA must build/typecheck an
  isolated baseline containing only the exact client hunk before Integrator action.
- Post-fix stale scan found no current seven-file/580-addition/46-test-expectation or
  first-gate wording in TASK_364B/C governance.
- UTF-8 trailing scan, tracked board diff-check, and untracked governance no-index
  diff-check passed; only LF/CRLF notices were ignored.
- Staging remains empty. No product/test file, real DB/file, commit, or push was
  touched by the B1/B2 reconciliation.

## Handoff

## Final Tests-Only Authorization Reconciliation

- Reviewer package-boundary re-gate passed and closed B1/B2.
- The user explicitly approved only one bounded assertion in
  `tests/unit/test_contact_point_profile_schema.py`.
- The authorization-time 323-line estimate was stale. Developer measured 369 lines
  before the pass; current `(Get-Content -Encoding UTF8).Count` is 384, below 500.
- Developer must reuse existing temporary SQLite fixtures/helpers and prove generic
  `create_all()` exclusion plus dedicated `init_db()` creation/read-verification.
- All eight product candidates, `frontend/src/api/client.ts`, and the other three test
  modules are read-only dependencies for Developer. No product implementation is
  authorized.
- QA must later generate hunk-isolated frontend build/typecheck evidence before any
  Integrator baseline packaging.
- TASK_364B remains Integrator blocked until TASK_364C is accepted and TASK_364B passes
  its own package re-gate.

## Test-Only Completion Reconciliation

- Developer enhanced only the authorized schema test node.
- Exact node passed and the exact four-module package suite remains `31 passed`.
- Reviewer test-only diff gate passed with no blocker.
- Current physical line count is 384; 323 is retained only as a superseded Planner
  estimate and is not a current source fact.
- TASK_364B remains Integrator blocked.

## QA Blocker And Package-Owner Reconciliation

- QA constructed the exact 13-path isolate and reproduced `31 passed`, the exact schema
  node `1 passed`, eight-module py_compile, clean diff/trailing/path/staging scans, and
  no real DB/file access.
- Applying only the approved `frontend/src/api/client.ts` 11-addition type hunk caused
  four `tsc -b` errors: three excluded fixtures lacked required `cr_coverage`, and the
  excluded production model omitted required `cr_selected`.
- The client contract is therefore not self-contained in TASK_364C. It is removed from
  this baseline and deferred to TASK_364B, where Reviewer must freeze a self-contained
  client-plus-consumer/fixture boundary before any Integrator retry.
- TASK_364C is now exactly 12 paths: eight backend/API/storage product files and four
  focused tests. The current diff is 596 additions / 17 deletions. The former 581/17
  value is historical, before the authorized 15-line schema-test increase.
- `backend/infrastructure/storage/contact_point_profile_schema_migration.py` is 203
  UTF-8 physical lines. `tests/unit/test_contact_point_profile_schema.py` is 384 UTF-8
  physical lines. Earlier governance used 384 for the test; it must not be relabeled as
  the migration module count.
- Because the revised TASK_364C package contains no frontend path, frontend build is not
  a TASK_364C gate. TASK_364B must later supply hunk-isolated frontend build/typecheck
  evidence for its client-plus-consumer package.
- TASK_364B remains Integrator blocked. No product/test edit, staging, commit, or push
  is authorized by this reconciliation.

## Reviewer Backend-Only Re-Gate Reconciliation

- Reviewer passed the revised 12-path backend/API/storage/test boundary.
- Reviewer independently reproduced 596 additions / 17 deletions, `31 passed`, eight
  module py_compile, 203/384 physical-line facts, clean diff/trailing checks, and an
  empty index.
- `frontend/src/api/client.ts` remains excluded and deferred to TASK_364B. No frontend
  build applies to TASK_364C.
- TASK_364B remains Integrator blocked; no direct Integrator route is authorized.

## QA Backend-Only Package Pass Reconciliation

- QA rebuilt the package from accepted HEAD in a disposable detached worktree and
  injected exactly the frozen 12 paths.
- The four-module suite passed `31`; the exact schema node passed `1`; eight-module
  py_compile passed.
- QA reproduced `596/17`, migration/schema-test counts `203/384`, the single approved
  `database.py` hunk, and clean whitelist/diff/trailing/no-real-mutation/staging scans.
- Client, R1, SummaryCard, and every frontend path were absent. TASK_364B remains
  Integrator blocked and was not released.

Next legal role: Integrator packaging/readiness for TASK_364C only.
