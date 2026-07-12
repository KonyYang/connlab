# TASK_361G Contact Measurement Schema CHECK Compatibility Bootstrap Corrective

Date: 2026-07-13

Role: Developer

Status: developer_implementation_complete - ready for Reviewer implementation gate.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. `TASK_361G` is the active planned corrective
after the accepted TASK_361F index bootstrap. The Reviewer plan gate passed and the
user approved Developer planning-first only. `TASK_361E` remains paused_by_user and
was not resumed or incorporated.

## Verified Planning Facts

- `init_db()` reaches the authority migration before Matrix Session and read-only
  confirmed Test Record preview services. Missing named table CHECKs therefore block
  startup before TASK_361F index compatibility logic can run.
- SQLite cannot add a physical CHECK to an existing table without the explicitly
  forbidden rebuild/swap path. The only planned non-destructive compatibility form
  is exact physical-CHECK recognition or an exact canonical trigger guard after row
  preflight.
- Three target predicates and two impact predicates have frozen canonical SQL,
  trigger names, `BEFORE INSERT`/relevant `BEFORE UPDATE OF` events, and `RAISE(ABORT,
  ...)` messages in the updated TASK_361G plan.
- `IS NOT 1` is required both for existing-row preflight and guards so false and NULL
  do not pass under SQLite three-valued logic.
- The future migration must first classify all physical CHECKs/triggers and run all
  missing-CHECK row preflights plus unchanged TASK_361F index preflights. Only then
  may it start one `BEGIN IMMEDIATE` transaction to create/revalidate absent guards
  and indexes together.

## Exact Future Scope

Future implementation is limited to the authority migration, focused temporary
schema/startup tests, and TASK_361G governance. No new helper module, dependency,
model/repository/lifecycle/API/client/frontend change is planned. `database.py` call
order, real databases, table rebuild/data repair, TASK_361D, paused TASK_361E, Fee,
generic Test Record/Report behavior, parser, LTR/public-drive, Settings/release,
`.agents/**`, `docs/project_management/**`, and external residuals stay locked.

## Validation Plan

- Disposable SQLite only: exact alternate physical CHECK recognition, all-five/each
  missing, wrong/combined expressions, canonical/malformed triggers, valid and
  invalid rows, trigger INSERT/UPDATE enforcement, atomic rollback, idempotency and
  lock/busy handling.
- Compare authority rows and every non-approved schema object before/after. Only the
  four frozen triggers and TASK_361F semantic indexes may appear.
- Run temporary Matrix Session GET and read-only confirmed Test Record preview GET
  probes. Do not call Cancel/Delete, generation/download, or document routes.
- Run focused pytest, `py_compile`, line count, diff/trailing, whitelist/forbidden,
  no-real-database-path and dirty-worktree isolation scans.

## Planning-First Validation

- Re-read AGENTS, the task board, TASK_361G task/plan/Planner/Reviewer/reconciliation
  evidence, TASK_361F accepted migration, and current worktree status.
- Updated only the TASK_361G plan and this Developer evidence. No migration, test,
  API/client, dependency, database, file, or product behavior was changed.
- No real `data/connlab.sqlite3`, operator database, Cancel/Delete, Test Record
  generation, or real `.docx` was opened or invoked.

## Next Role

Reviewer implementation-readiness gate.

## Blocking Summary

No implementation blocker. TASK_361E remains paused and must not be routed from this
lane.

## Implementation Pass

### Changed Files

- `backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py`
- `tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py`
- this Developer evidence file

### Behavior

- Replaced name-only CHECK rejection with five exact semantic CHECK specifications.
  Exact physical table CHECKs are accepted under alternate names; wrong named or
  semantically overlapping/ambiguous CHECK expressions fail closed.
- Missing target or impact semantics are guarded by the four frozen canonical
  `BEFORE INSERT` and relevant-column `BEFORE UPDATE OF` triggers. Every condition
  uses `IS NOT 1`, so invalid and NULL/indeterminate values abort with the approved
  concise `authority_corrupt` message.
- Existing rows are preflighted before any DDL. The missing-CHECK preflight and the
  accepted TASK_361F index duplicate/NULL preflight run before one shared
  `BEGIN IMMEDIATE` transaction creates/revalidates missing triggers and indexes.
- Wrong same-name guards, invalid legacy target/impact rows, DDL failure, and locked
  writers fail closed without table rebuild, data repair, or partial new guards.

### Verification

- TDD red: a disposable legacy fixture missing all five authority CHECKs failed
  through `init_db()` with `measurement_plan_target_snapshots is missing required
  checks` before migration changes.
- New TASK_361G disposable CHECK/bootstrap/startup module: `12 passed`.
- Focused final regression:
  `py -m pytest -p no:cacheprovider --basetemp=tmp\\task_361g_final tests/unit/test_contact_measurement_plan_schema.py tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_test_record_preview_api.py -q`
  -> `51 passed`.
- Temporary Matrix Session GET and read-only confirmed Test Record preview GET pass
  against missing-CHECK fixtures. No Cancel/Delete, generation, download, or real
  document route was called.

### Scope And Residuals

- All database fixtures were under `tmp/`. No real `data/connlab.sqlite3` or operator
  database was opened, copied, or modified.
- No `database.py`, authority model/repository/lifecycle/API contract, frontend/client,
  TASK_361D, paused TASK_361E, Fee, generic Test Record/Report, parser, LTR/public
  drive, real-file, Settings, release, staging, commit, or push change occurred.
- Existing parser/MCR, board, TASK_361E governance, superpowers, and task residuals
  remain external and excluded.

## Reviewer B1 Fix Pass

### Root Cause And Narrow Fix

- The physical-CHECK recognizer pooled canonical expressions from target and impact
  tables. Both the target stable-key and impact subject predicates contain the
  `cmp-target:v1|` marker, so a valid impact subject CHECK incorrectly made a
  missing target-key CHECK look incompatible.
- `_missing_check_specs()` now keeps the canonical CHECK name/expression registry
  and marker comparison scoped to each physical table. Trigger predicates, trigger
  SQL, row preflight, transaction ordering, and all other compatibility behavior
  are unchanged.

### Regression Coverage And Verification

- Added a disposable mixed legacy fixture that removes only the target stable-key
  CHECK, retains the exact impact subject CHECK, and reaches the production
  `init_db()` boundary. It creates only the two target canonical guards; the impact
  physical CHECK remains recognized and receives no new impact guards.
- TDD red reproduced the former `authority_corrupt` startup failure; the same
  regression is green after table-scoped recognition.
- Focused temporary SQLite suite:
  `py -m pytest -p no:cacheprovider --basetemp=tmp\task_361g_b1_full tests/unit/test_contact_measurement_plan_schema.py tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_test_record_preview_api.py -q`
  -> `52 passed`.
- `py -m py_compile backend\infrastructure\storage\contact_measurement_plan_authority_schema_migration.py tests\integration\test_contact_measurement_plan_schema_check_compatibility_startup.py` passed.
- The migration is 412 lines and its focused integration module is 446 lines, both
  below the 500-line hard limit. `git diff --check` passed with only existing
  LF/CRLF warnings; the TASK_361G files have no trailing whitespace.
- Candidate scope remains only the approved migration, disposable integration test,
  and TASK_361G evidence. Existing `backend/modules/test_plan` and related test
  residuals remain external and excluded. No real database path appears in this
  pass outside the explicit prohibition and disposable fixture descriptions.

### Reviewer Re-gate State

Ready for Reviewer implementation re-gate. No real database, locked product scope,
or external residual was modified by this B1 pass.

## Reviewer B2 Tests-Only Fix Pass

### Coverage Added

- Added a compact disposable SQLite guard-enforcement module, keeping the existing
  bootstrap module below its hard limit while reusing its approved temporary fixture.
- Parameterized target cases prove Group-anchor XOR, Row-anchor XOR, and stable-key
  prefix guard enforcement on both guarded INSERT and relevant-column UPDATE.
- Parameterized impact cases prove subject prefix and identity prefix guard
  enforcement on both guarded INSERT and relevant-column UPDATE, explicitly covering
  `trg_cmp_impact_checks_update_v1`.
- Every case asserts an invalid INSERT leaves no row, an invalid UPDATE rolls back,
  and a valid authority INSERT remains accepted.

### Verification

- Guard-enforcement module: `5 passed`.
- Full temporary TASK_361G suite, now including enforcement coverage:
  `py -m pytest -p no:cacheprovider --basetemp=tmp\task_361g_b2_full tests/unit/test_contact_measurement_plan_schema.py tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py tests/integration/test_contact_measurement_plan_schema_check_guard_enforcement.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_test_record_preview_api.py -q`
  -> `57 passed`.
- `py_compile` passed. Migration/startup/enforcement files are 412/468/172 lines,
  all below 500. `git diff --check` passed with only existing LF/CRLF warnings;
  trailing-whitespace and locked-scope/no-real-database scans are clean.

### Reviewer Re-gate State

Ready for Reviewer implementation re-gate. This pass added tests only and did not
change migration, trigger, transaction, product, or locked-scope behavior.
