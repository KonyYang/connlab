# TASK_364C Project Point Profile CR Coverage Authority Baseline Package Plan

Status: `complete / Integrator accepted`

## Decision

Use a narrowed package path B. Establish the existing backend/API/storage authority as
a separately reviewed and accepted baseline. QA proved that the 11-line client contract
cannot compile without excluded R1 consumers and fixtures, so defer that hunk to the
later TASK_364B package re-gate instead of weakening required DTO fields or expanding
TASK_364C.

## Baseline Contract

- A confirmed Point Profile revision owns `follow_llcr` or `custom` CR coverage.
- Custom coverage persists stable selected category identities atomically with the
  profile revision; follow mode stores no redundant selected set.
- Fingerprint, read projection, typed route response, and direct-confirm request all
  carry the same coverage contract.
- Client types will mirror the accepted route contract in TASK_364B, where they can be
  reviewed and built with their actual consumers.

## File-Level Package Order

1. Review additive selection model, fail-closed migration shape, and the exact
   `database.py` one-line exclusion from generic `create_all()`.
2. Review repository read/write methods and atomic lifecycle/fingerprint behavior.
3. Review read projection and typed route request/response.
4. Review the four focused backend/API test hunks and the completed schema-test
   assertion for dedicated-bootstrap ownership.
5. Re-run the exact four-module package suite (`31 passed` baseline).
6. Only after Reviewer/QA gates may Integrator hunk-stage and commit this baseline.
7. Return TASK_364B to Reviewer package re-gate for the client-plus-consumer package.

## Exact May Touch

The exact file and symbol list in
`tasks/TASK_364C_PROJECT_POINT_PROFILE_CR_COVERAGE_AUTHORITY_BASELINE_PACKAGE.md`
controls. No additional file may be inferred from a whole-file diff.

No further Developer pass is authorized by this reconciliation. The revised package is
the eight existing product candidates and four focused tests only.

## Package Isolation

- `frontend/src/api/client.ts` is excluded from TASK_364C and deferred to TASK_364B.
- `backend/infrastructure/storage/database.py` is mixed and permits exactly one line:
  add `contact_point_profile_cr_category_selections` to `init_db().profile_tables`.
- Backend and test files may be included only after Reviewer confirms their entire
  visible candidate diff belongs to this authority baseline.
- R1 frontend files, client types, SummaryCard, QA PNG, and all downstream/external residuals remain
  outside this baseline.

## Validation

- exact four-module Point Profile backend/API package suite, expected `31 passed`;
- isolated `init_db()` proof that generic `create_all()` cannot create the selection
  table before the dedicated fail-closed Point Profile bootstrap;
- diff-check, UTF-8 trailing, whitelist, line-count, staging, and no-real-mutation scans;
- explicit HEAD scan proving the accepted baseline did not previously exist;
- exact revised package metadata: 12 paths, 596 additions / 17 deletions, migration
  module 203 physical lines, schema test 384 physical lines.

## Rollback

If the assertion requires any product or second test-file edit, stop and return to
Planner. Do not partially package client types or R1 UI.

## Stop Point

Developer tests-only implementation and Reviewer diff gate are complete. QA blocked on
the former client-only build boundary, Planner narrowed the package, and Reviewer
passed the revised backend-only boundary. QA then passed the isolated 12-path package.
Route only to Integrator baseline packaging. No additional product implementation or
push is authorized.
