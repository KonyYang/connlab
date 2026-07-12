# TASK_361F Contact Measurement Schema Compatibility Bootstrap Corrective Developer Evidence

Date: 2026-07-13

Role: Developer

Status: developer_implementation_complete - ready for Reviewer implementation gate.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361F is the current startup compatibility
corrective. TASK_361E is paused by explicit user instruction and remains paused. The
Reviewer plan gate, implementation-readiness gate, Planner reconciliation, and explicit
user implementation approval authorize this bounded corrective. TASK_361E remains
paused and was not resumed.

## Verified Facts and Refined Strategy

- `init_db()` calls model registration, `create_all()`, and then the authority schema
  migration. Existing-table index evolution must occur only in the migration; no
  `database.py` ordering change is required or authorized.
- The exact invariants are two `measurement_plan_revisions` partial unique indexes on
  `measurement_plan_root_id` for `state = 'confirmed'` and `state IN ('draft',
  'needs_review')`, plus full unique target `(measurement_plan_revision_id,
  stable_target_key)` and impact `(editable_revision_id, impact_identity_key)` pairs.
  The full-pair fields are non-null in the ORM, so an existing nullable variant is not
  semantically equivalent under SQLite NULL-distinctness.
- Future migration code will classify canonical/equivalent/absent/incompatible using
  SQLite pragma metadata and canonical DDL predicate SQL. It preflights every absent
  semantic invariant before DDL, creates only absent canonical indexes inside one
  transaction, then read-verifies all four. No rows, tables, columns, CHECKs, FKs, or
  existing incompatible objects may be changed.
- Incompatible non-index schema, wrong index shape, duplicate keys, or prohibited
  NULL identity states return `authority_corrupt` before DDL. Partial DDL failure
  rolls back, repeated startup is idempotent, and concurrent/locked startup remains a
  readable failure rather than a guessed repair.

## Future May Touch and Locks

Only the existing authority migration plus focused temp-SQLite schema/startup API
tests and TASK_361F docs/evidence may change. Real `data/connlab.sqlite3`, models,
repositories, lifecycle, commands, frontend/API client, TASK_361D, paused TASK_361E,
Fee, generic Test Record/Report semantics, parser, LTR/public-drive, real files, and
external residual cleanup are locked.

## Validation Plan

Use disposable existing SQLite fixtures for all-four/each-missing/equivalent/wrong-
shape/duplicate/partial-failure/idempotency scenarios. Compare rows and non-index DDL
before/after. Run temporary Matrix Editor session, Cancel, and Test Record startup
regressions, fresh schema tests, compile, diff/trailing/line-count/forbidden-path/
no-real-database scans. No real database access is permitted.

## Planning-First Validation

- Re-read AGENTS, board, TASK_361F task/plan/Planner/Reviewer evidence, `init_db`,
  authority migration, ORM constraints, and focused schema test patterns.
- This pass updates only TASK_361F plan/evidence. No product code, tests, database,
  dependency, API/client, or real file changed.
- `git diff --check` on TASK_361F plan/evidence passed and UTF-8 trailing whitespace
  scan was clean. Targeted status confirms only TASK_361F plan/evidence were added by
  this pass; paused TASK_361E, parser/TASK_360Q-R-S, board, and superpowers entries
  remain excluded external residuals.

## Next Role

Reviewer implementation gate.

## Implementation Pass

### Changed Files

- `backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py`
- `tests/unit/test_contact_measurement_plan_schema.py`
- `tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py`
- this Developer evidence file

### Behavior

- Replaced name-only authority index validation with four structured SQLite semantic
  specifications: confirmed and editable partial revision uniqueness plus full target
  and impact pair uniqueness.
- Existing alternate exact-equivalent indexes, including SQLite table-constraint
  autoindexes for full pairs, are accepted without duplicate canonical DDL.
- Missing canonical semantics are preflighted for non-null identity coverage and
  duplicate keys before any DDL. Incompatible named index shapes, malformed
  authority schema, duplicate identities, and nullable identity columns fail closed
  with `authority_corrupt`.
- Missing canonical indexes are created only inside an explicit `BEGIN IMMEDIATE`
  SQLite transaction, then read-verified. A later DDL failure rolls back every new
  index from that bootstrap attempt. A locked or busy writer produces a concise
  bootstrap error without any fallback write.
- Added disposable startup coverage showing repaired compatibility no longer masks
  existing Matrix Editor session, draft Cancel, or current-state Test Record route
  behavior. No route or consumer behavior changed.

### Verification

- TDD red: missing partial semantic index startup failed in the original name-first
  migration with `measurement_plan_revisions is missing required indexes`.
- Focused schema, compatibility startup, and accepted TASK_361B bootstrap suite:
  `17 passed`.
- Focused full TASK_361F backend regression:
  `py -m pytest -p no:cacheprovider --basetemp=tmp\\task_361f_full tests/unit/test_contact_measurement_plan_schema.py tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_matrix_editor_test_record_generation_api.py -q`
  -> `33 passed`.
- `py -m py_compile backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py` passed.
- The migration is 307 lines, below the AGENTS hard limit of 500.

### Scope And Residuals

- No real `data/connlab.sqlite3` or operator database was opened, copied, or
  modified. All database fixtures were under `tmp/`.
- No `database.py` call-order, authority model/repository/lifecycle/API contract,
  frontend/client, TASK_361D, paused TASK_361E, Fee, Test Record semantics, parser,
  LTR/public-drive, or real-file change was made.
- Existing parser/MCR, task-board, TASK_361E governance, superpowers, and task
  residuals remain external and excluded. No staging, commit, or push occurred.

## Reviewer B1 Tests-Only Fix Pass

### Added Coverage

- Added a disposable legacy-shaped SQLite fixture that removes both partial revision
  indexes and the target/impact table-level full-pair unique constraints while
  preserving required columns, checks, foreign keys, rows, and non-index DDL.
- The fixture proves the existing migration creates and read-verifies all four
  canonical semantic indexes, including target
  `(measurement_plan_revision_id, stable_target_key)` and impact
  `(editable_revision_id, impact_identity_key)` full pairs.
- Separate target and impact duplicate-pair fixtures fail with `authority_corrupt`
  before every canonical index DDL. Separate nullable-identity fixtures contain a
  real `NULL` identity value under a schema that permits it; the existing non-null
  shape guard fails closed before any DDL, which is the required SQLite
  null-semantics protection.
- This fix changes tests only. The migration, runtime behavior, and all locked
  product paths remain untouched.

### B1 Verification

- `tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py`
  -> `6 passed`.
- Full TASK_361F focused temporary authority/startup/API regression:
  `38 passed`.
- Re-ran `py_compile`, line-count, `git diff --check`, UTF-8 trailing-whitespace,
  and forbidden-scope/no-real-database scans after the test-only update.

## Reviewer B1R Tests-Only Fix Pass

- The all-four-missing legacy fixture now invokes the real `init_db()` startup
  boundary, then read-verifies all four canonical indexes. This covers the same
  global startup path that previously masked Matrix Editor routes with a `500`.
- Target/impact duplicate and nullable fixtures now assert exact equality with the
  empty canonical-index set across revisions, targets, and impacts. They therefore
  prove no partial or full canonical DDL occurred before `authority_corrupt`.
- No migration product code changed in B1R. Full temporary TASK_361F
  authority/startup/API suite remains `38 passed`.

## Blocking Summary

No implementation blocker. TASK_361E remains paused and must not be routed from this
lane.
