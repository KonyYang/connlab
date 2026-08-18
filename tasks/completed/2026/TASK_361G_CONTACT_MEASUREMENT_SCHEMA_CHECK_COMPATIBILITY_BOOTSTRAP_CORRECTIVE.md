# TASK_361G Contact Measurement Schema CHECK Compatibility Bootstrap Corrective

## Status

Complete / Integrator accepted on 2026-07-13. Developer implementation/fix passes,
Reviewer implementation re-gates, QA disposable legacy SQLite startup/API smoke,
and controlled Integrator package isolation passed. Remote push was intentionally
not performed. TASK_361E remains paused_by_user.

## Lane

`contact-measurement-schema-check-compatibility-bootstrap-corrective`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: Integrator packaging/readiness closeout.
- TASK_361F is complete/accepted at local commit
  `983633b7041ca77afb5f80672cfa168fc8b5cb4b`.
- TASK_361E remains paused_by_user and cannot own this runtime defect.
- A controlled operational smoke found a new pre-index CHECK compatibility blocker in
  the accepted authority schema migration boundary.
- Why allowed: Reviewer implementation blockers are closed, QA passed, and the
  package is limited to the TASK_361G CHECK compatibility bootstrap migration,
  disposable SQLite tests, docs/evidence, and precise board closeout.

## Goal

Restore startup compatibility for existing SQLite databases whose authority tables
and columns exist but whose `measurement_plan_target_snapshots` and
`measurement_plan_impacts` tables lack the five TASK_361B CHECK semantics. The future
correction must be non-destructive, idempotent, preserve all data, and keep invalid or
unknown legacy shapes fail-closed.

## Confirmed Operational Evidence

- `init_db()` fails before TASK_361F index bootstrap with
  `measurement_plan_target_snapshots is missing required checks`.
- Matrix session GET and read-only confirmed Test Record preview GET return `500`.
- Target snapshots lack group-anchor XOR, row-anchor XOR, and target-key prefix CHECKs.
- Impacts lack subject-key prefix and impact-identity prefix CHECKs.
- All six authority tables had zero business rows during the controlled smoke.
- DB SHA-256, size, mtime, all six authority row counts, and canonical index lists were
  unchanged before/after. Cancel/Delete and generation POST were not executed.

This plan does not authorize another real-database operation.

## CHECK Compatibility Decision

SQLite cannot add a physical table CHECK to an existing table without rebuilding the
table. Table rebuild is explicitly forbidden. V1 therefore uses this deterministic
policy:

1. Recognize an existing table CHECK as compatible when its canonical expression is
   exactly one required predicate, regardless of constraint name or harmless SQL
   formatting/outer parentheses.
2. Do not infer broad logical equivalence. A weaker, stronger, combined, ambiguous,
   or same-canonical-name wrong expression is `authority_corrupt` and remains
   fail-closed.
3. When a required predicate has no equivalent table CHECK, preflight every existing
   row against the exact predicate before any DDL. Any violating or indeterminate row
   blocks startup; no data repair, defaulting, deletion, or guessed coercion occurs.
4. After all missing predicates pass preflight, create canonical compatibility guard
   triggers rather than rebuilding tables:
   - `trg_cmp_target_checks_insert_v1`: `BEFORE INSERT` on target snapshots;
   - `trg_cmp_target_checks_update_v1`: `BEFORE UPDATE OF`
     `source_group_snapshot_id`, `manual_group_anchor_id`,
     `source_row_snapshot_id`, `manual_row_anchor_id`, and `stable_target_key`;
   - `trg_cmp_impact_checks_insert_v1`: `BEFORE INSERT` on impacts;
   - `trg_cmp_impact_checks_update_v1`: `BEFORE UPDATE OF impact_subject_key,
     impact_identity_key` on impacts.
   The target pair enforces all three target predicates; the impact pair enforces
   both impact predicates.
5. Canonical trigger SQL raises `ABORT` with
   `authority_corrupt: target CHECK compatibility guard rejected row` or
   `authority_corrupt: impact CHECK compatibility guard rejected row` when a new or
   changed row violates a required predicate. Trigger name, SQL, event, table,
   relevant columns, and predicates must be exact and re-inspected after creation.
6. Exact canonical compatibility triggers are accepted on repeated startup. A
   same-name wrong-shape trigger is fail-closed and is never dropped/replaced. Unknown
   alternate triggers are not treated as authority proof.
7. TASK_361F semantic-index behavior then runs unchanged after CHECK enforcement is
   proven. CHECK guard bootstrap and any still-missing canonical index bootstrap must
   share one contained `BEGIN IMMEDIATE` transaction or otherwise prove no partial
   schema success; Reviewer must approve the final atomic ordering before coding.

## Required Predicates

Target snapshots:

- exactly one non-empty source/manual Group anchor;
- exactly one non-empty source/manual Row anchor;
- `stable_target_key` begins with `cmp-target:v1|`.

Impacts:

- `impact_subject_key` begins with `cmp-target:v1|` or `cmp-candidate:v1|`;
- `impact_identity_key` begins with `cmp-impact:v1|`.

## Authorized May Touch For Developer Implementation

- `backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py`
- `tests/unit/test_contact_measurement_plan_schema.py`
- one focused new module such as
  `tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py`
- existing `tests/integration/test_matrix_editor_session_api.py` only if a narrow
  temporary-startup session assertion is necessary
- existing `tests/integration/test_matrix_editor_test_record_generation_api.py` only
  if a narrow read-only preview startup assertion is necessary
- TASK_361G task/plan/evidence and `docs/task_board.md` through normal lane flow

`backend/infrastructure/storage/database.py`, authority ORM models, repositories,
lifecycle, services, routes, and DTOs are read-only evidence and remain locked.

## Must Not Touch / Locked Paths

- Never open, copy, modify, migrate, rebuild, delete, or smoke-test the real
  `data/connlab.sqlite3` or another operator database in Developer/Reviewer work.
- No table rebuild, shadow-table swap, writable-schema edit, column/CHECK/FK rewrite,
  business-row update, defaulting, repair, deletion, backfill, or authority audit
  mutation.
- No TASK_361F index semantic expansion; it is an accepted regression baseline.
- No TASK_361E consumer migration or resume; no TASK_361D draft workbook change.
- No frontend, API client, route/DTO behavior, Generic Test Record/Report behavior,
  Fee rules/pricing/default-fill, formal workbook consumer, Matrix parser/import,
  LTR/public drive, Office/workbook/folder, release/settings, or unrelated cleanup.
- `.agents/**`, `docs/project_management/**`, remote push, destructive git operations,
  parser/MCR, TASK_360Q/R/S, superpowers, and all external residuals remain locked.

## Acceptance Criteria

1. A disposable old-database fixture with valid authority tables/data but missing all
   five CHECKs completes `init_db()` through CHECK guards and TASK_361F indexes.
2. Exact equivalent table CHECK expressions under alternate names are recognized and
   do not create redundant guards.
3. Missing semantics create only the four canonical INSERT/UPDATE guard triggers;
   repeated startup is a no-op and exact trigger SQL is revalidated.
4. Existing rows and all non-approved schema objects are byte/row equivalent before
   and after; only approved triggers plus TASK_361F indexes may be added.
5. Any invalid existing target/impact row blocks before DDL and remains unchanged.
6. Wrong/ambiguous table CHECK or same-name wrong trigger fails closed without drop,
   replacement, data repair, or index creation.
7. Trigger guards reject invalid future INSERT and relevant UPDATE while allowing
   valid authority writes expected by TASK_361B lifecycle tests.
8. TASK_361F index recognition/bootstrap, fresh database schema, and authority
   lifecycle/repository/API regressions remain unchanged.
9. Matrix session GET and read-only confirmed Test Record preview GET succeed against
   disposable old-database fixtures; write/delete/generation endpoints are not used
   for real-database validation.

## Validation Gate

- Unit/temp-SQLite tests cover exact alternate-name CHECK recognition, all-five/each
  missing, mixed CHECK/guard states, valid populated rows, invalid existing rows,
  same-name wrong trigger, ambiguous CHECK, DDL rollback, idempotency, and lock/busy.
- Trigger enforcement tests cover invalid INSERT/UPDATE and valid TASK_361B lifecycle
  writes without changing business semantics.
- Before/after snapshots compare all authority rows, non-approved `sqlite_master`
  objects, DB containment, and TASK_361F index results.
- Temporary startup/API regressions cover Matrix session and read-only confirmed Test
  Record preview; no real database or real file is used.
- Existing TASK_361B/F focused suites pass, plus Python compile, diff/trailing,
  line-count, whitelist/forbidden, no-real-database-path, and external-residual scans.

## Merge Gate

Complete. Reviewer plan/readiness gates, explicit user approvals, Developer
implementation/fix passes, Reviewer implementation re-gates, QA disposable
old-database startup/API smoke, and Integrator file/hunk isolation passed.
The accepted package excludes real DB access, table rebuild/data repair,
TASK_361D/E, frontend/client, API behavior, Fee/Test Record/Report/formal workbook,
parser, LTR/public-drive, and external residuals.

## Definition Of Ready

Satisfied and closed for TASK_361G. The lane is accepted as the narrow SQLite CHECK
compatibility bootstrap corrective only. Acceptance does not resume or authorize
TASK_361E and does not authorize real DB repair, frontend/API client changes,
consumer semantics, parser/MCR work, or external cleanup.

## Blocking Questions

None for Developer implementation.
