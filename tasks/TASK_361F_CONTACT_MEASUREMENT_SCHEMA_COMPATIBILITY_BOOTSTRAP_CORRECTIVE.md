# TASK_361F Contact Measurement Schema Compatibility Bootstrap Corrective

## Status

Complete / Integrator accepted on 2026-07-13. Developer implementation, Reviewer
implementation re-gates, QA disposable startup/API smoke, and controlled Integrator
package isolation passed. Remote push was intentionally not performed. TASK_361E
remains paused.

## Lane

`contact-measurement-schema-compatibility-bootstrap-corrective`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Role: Integrator packaging/readiness closeout.
- TASK_361B is accepted at local commit `8cafc79e`; TASK_361C/D are accepted.
- TASK_361E is explicitly paused by the user and cannot own this runtime defect.
- A production startup traceback identifies a narrow existing-SQLite compatibility
  failure in TASK_361B's schema migration boundary.
- Why allowed: Reviewer implementation blocking findings are closed, QA passed, and
  the package is limited to the TASK_361F schema compatibility bootstrap migration,
  focused temporary SQLite startup/API tests, docs/evidence, and precise board
  closeout.

## Goal

Restore startup compatibility for existing SQLite databases whose six Contact
Measurement Plan authority tables and data exist but whose schema lacks one or more
required unique-index semantics/canonical names. The future correction must be
SQLite-only, non-destructive, idempotent, and preserve every authority row and
constraint semantic.

## Confirmed Runtime Failure

- Matrix Editor Test Record and Cancel return Internal Server Error.
- `GET /api/projects/{project_id}/matrix-editor/session` returns `500`.
- The FastAPI traceback reaches `init_db()`, then
  `migrate_contact_measurement_plan_authority_schema()`, and fails with
  `measurement_plan_revisions is missing required indexes`.
- The affected existing database lacks the expected canonical index names:
  `uq_measurement_plan_confirmed_per_root`,
  `uq_measurement_plan_editable_per_root`, `uq_measurement_plan_target_key`, and
  `uq_measurement_plan_impact_identity`.

No real database inspection or mutation is authorized by this task plan.

## Root Cause Boundary

`Base.metadata.create_all()` creates indexes for fresh tables but does not evolve an
already existing table. The current authority migration validates required index
names and shapes after `create_all()` and raises immediately when they are absent;
it has no compatibility recognition or safe index bootstrap step. Because
`init_db()` is called during dependency construction, this global startup failure can
surface through unrelated Matrix Editor actions. Fee/formal-workbook consumer logic
is not on this failure path.

## Future Corrective Contract

1. Run only for SQLite and only inside the existing authority schema migration.
2. Validate required tables, columns, CHECK expressions, foreign-key shapes, and
   non-index authority invariants before attempting index compatibility work.
3. Describe the four required unique indexes by semantic shape, not name alone:
   - one confirmed revision per root: unique root id where `state = 'confirmed'`;
   - one editable revision per root: unique root id where state is `draft` or
     `needs_review`;
   - unique `(measurement_plan_revision_id, stable_target_key)`;
   - unique `(editable_revision_id, impact_identity_key)`.
4. Accept an existing differently named/SQLite-autoindex object only when its
   uniqueness, ordered columns, partial/full kind, and canonical predicate exactly
   match the required semantic shape. A same-name wrong-shape object remains corrupt.
5. If no equivalent semantic index exists, preflight all four datasets for duplicate
   keys before any DDL. Any conflict returns a readable `authority_corrupt` error and
   makes no schema or data change.
6. After a clean all-index preflight, create only the missing canonical unique
   indexes using contained transactional SQLite DDL. Do not rebuild tables or alter
   columns, CHECKs, foreign keys, rows, revision states, root pointers, or audits.
7. Re-inspect all four semantic shapes after bootstrap. Repeated `init_db()` must be
   a no-op and must not add duplicate indexes.
8. Fresh databases keep the existing TASK_361B schema. Partial or malformed tables,
   wrong predicates/columns, duplicate authority keys, invalid CHECKs, and invalid
   foreign keys remain hard blockers; the corrective must not guess or repair data.

## Authorized May Touch For Developer Implementation

- `backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py`
- `tests/unit/test_contact_measurement_plan_schema.py`
- one focused new temp-SQLite compatibility test module under `tests/integration/`
  if API/startup coverage cannot remain readable in the unit module
- existing `tests/integration/test_matrix_editor_session_api.py` only for focused
  startup/session/draft-cancel regression assertions
- existing `tests/integration/test_matrix_editor_test_record_generation_api.py` only
  for startup/Test Record regression assertions
- TASK_361F task/plan/evidence and `docs/task_board.md` through normal lane flow

`backend/infrastructure/storage/database.py` is read-only evidence in the current
plan because it already calls the migration after model registration/create-all. A
future Developer must stop and request Planner/Reviewer re-gate before changing that
call order or file.

## Must Not Touch / Locked Paths

- Never open, edit, copy, replace, rebuild, delete, or manually migrate the real
  `data/connlab.sqlite3` or any operator database.
- No authority table/column/CHECK/foreign-key redesign, model change, repository
  write, lifecycle command, bootstrap data rewrite, audit rewrite, or feature-flag
  semantic change.
- No TASK_361E Fee consumer or formal LLCR/CR workbook-source migration.
- No TASK_361D draft workbook route/service/artifact/client/UI change.
- No frontend, `frontend/src/api/client.ts`, API route/DTO contract, generic Test
  Record semantics, Report, Fee rules/pricing/default-fill/UI, Matrix parser/import,
  LTR/public drive, Office/workbook/folder, release/settings, or unrelated cleanup.
- `.agents/**`, `docs/project_management/**`, remote push, destructive git operations,
  TASK_360Q/R/S, parser/MCR, superpowers, and all external residuals remain locked.

## Acceptance Criteria

1. A disposable existing-database fixture with valid authority tables/data and the
   four missing semantic indexes completes `init_db()` successfully.
2. Missing semantic indexes are either recognized as exact equivalent indexes or
   created with the canonical TASK_361B shape; no row or non-index schema object
   changes.
3. Repeating `init_db()` produces the same index set and preserves row values/counts,
   revision states, root pointers, family facts, impacts, and audits.
4. Duplicate confirmed/editable roots, duplicate target keys, or duplicate impact
   identities block before DDL and preserve the fixture unchanged.
5. Same-name wrong-shape indexes, malformed tables, CHECKs, or foreign keys remain
   blocked with a readable compatibility/corruption error.
6. Fresh-database TASK_361B schema registration remains unchanged.
7. On a disposable compatibility fixture, Matrix Editor session read, draft cancel,
   and current-state Test Record API paths no longer fail during `init_db()`.
8. No test or smoke action touches the real ConnLab database or real files.

## Validation Gate

- Focused schema tests cover fresh DB, all-four-missing, each independently missing,
  exact alternate-name semantic compatibility, repeated startup, conflict preflight,
  wrong shape, and malformed non-index schema.
- Before/after fixture assertions compare all authority table rows and non-index
  schema SQL; only approved index objects may differ.
- Focused Matrix Editor session/draft-cancel and Test Record API regressions run on
  temporary databases.
- Existing TASK_361B schema/repository/API suites pass.
- Python compile, `git diff --check`, UTF-8 trailing-whitespace, line-count,
  whitelist/forbidden-path, dependency, no-real-database-path, and external-residual
  scans pass.

## Merge Gate

Complete. Reviewer plan/readiness gates, explicit user approvals, Developer
implementation/fix passes, Reviewer implementation re-gates, QA disposable
existing-database startup/API smoke, and Integrator file/hunk isolation passed.
The accepted package excludes real databases, TASK_361D/E, frontend/client,
authority model/repository/lifecycle changes, Fee, Test Record semantics, parser,
LTR/public-drive, release/settings, and external residuals.

## Definition Of Ready

Satisfied and closed for TASK_361F. The lane is accepted as the narrow SQLite
schema compatibility bootstrap corrective only. Acceptance does not resume or
authorize TASK_361E and does not authorize real database repair, frontend/API client,
Fee/Test Record semantic changes, parser/MCR work, or external cleanup.

## Blocking Questions

None for Developer implementation.
