# TASK_361G QA Gate

Date: 2026-07-13

Role: QA / Smoke Owner

Task: `TASK_361G_CONTACT_MEASUREMENT_SCHEMA_CHECK_COMPATIBILITY_BOOTSTRAP_CORRECTIVE`

Lane: `contact-measurement-schema-check-compatibility-bootstrap-corrective`

Result: `qa_pass`

## Scope And Boundary

- Read `AGENTS.md`, `docs/task_board.md`, lane orchestration protocol/registry, TASK_361G task/plan, reconciliation, Developer evidence, and Reviewer evidence.
- QA was limited to disposable legacy SQLite fixtures, startup/API probes, static/package checks, and this evidence file.
- Did not open, copy, or modify real `data/connlab.sqlite3`.
- Did not execute Cancel/Delete, Test Record generation, real `.docx`, real LTR/public-drive, or real business write flows.
- TASK_361E remains paused and was not resumed.
- Board/task status still lags the latest Reviewer callback in some files; latest Reviewer evidence and user route authorize this QA gate.

## Candidate Scope Observed

TASK_361G candidate files verified by status/diff:

- `backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py`
- `tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py`
- `tests/integration/test_contact_measurement_plan_schema_check_guard_enforcement.py`
- TASK_361G lane evidence/task/plan documents

External residuals observed and excluded from this QA gate/package:

- `backend/modules/test_plan/mcr_text_normalizer.py`
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_mcr_text_normalizer.py`
- `tests/unit/test_spec_section_text_extractor.py`
- `docs/task_board.md`
- TASK_361E evidence/plan/task residuals and other unrelated docs/plans

## Validation Commands

### Disposable full authority/startup/API suite

Command:

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_361g_qa_full tests/unit/test_contact_measurement_plan_schema.py tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py tests/integration/test_contact_measurement_plan_schema_check_guard_enforcement.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_confirmed_matrix_test_record_preview_api.py -q
```

Observed result:

```text
57 passed in 19.72s
```

Coverage confirmed from the focused modules:

- Missing all required authority CHECKs bootstraps canonical guard triggers via `init_db()`.
- Alternate exact physical CHECK names are accepted without redundant guards.
- Mixed cross-table marker case does not let impact CHECK semantics satisfy target CHECK semantics.
- Malformed/wrong/invalid legacy rows fail closed before trigger/index DDL.
- Canonical guards reject invalid future INSERT and relevant UPDATE for all five predicates.
- `trg_cmp_impact_checks_update_v1` coverage is present.
- Valid authority writes remain accepted.
- Guard/index DDL rollback, idempotency, and locked-writer behavior are covered.
- Matrix Editor session GET returns 200 against disposable old-schema startup probe.
- Read-only confirmed Test Record preview GET returns 200 and `preview_status: empty` against disposable old-schema startup probe.

### Python compile

Command:

```powershell
py -m py_compile backend\infrastructure\storage\contact_measurement_plan_authority_schema_migration.py tests\integration\test_contact_measurement_plan_schema_check_compatibility_startup.py tests\integration\test_contact_measurement_plan_schema_check_guard_enforcement.py
```

Observed result: passed.

### Diff and whitespace checks

Command:

```powershell
git diff --check -- backend\infrastructure\storage\contact_measurement_plan_authority_schema_migration.py tests\integration\test_contact_measurement_plan_schema_check_compatibility_startup.py tests\integration\test_contact_measurement_plan_schema_check_guard_enforcement.py docs\lane_evidence\TASK_361G_contact-measurement-schema-check-compatibility-bootstrap-corrective_developer.md docs\lane_evidence\TASK_361G_contact-measurement-schema-check-compatibility-bootstrap-corrective_reviewer.md
```

Observed result: passed with the known LF/CRLF warning only for the migration file.

UTF-8 trailing-whitespace scan on TASK_361G candidate files and evidence: no matches.

### Line-count check

Observed line counts:

```text
backend\infrastructure\storage\contact_measurement_plan_authority_schema_migration.py: 412
tests\integration\test_contact_measurement_plan_schema_check_compatibility_startup.py: 468
tests\integration\test_contact_measurement_plan_schema_check_guard_enforcement.py: 172
```

All checked files remain below the 500-line hard limit.

### Locked-scope / no-real-db scan

Static scans on TASK_361G candidate files found no real `data/connlab.sqlite3`, `D:\Test Project`, `D:\PublicProject`, public-drive, LTR workbook, frontend/API-client, TASK_361E, Fee, Report, parser, or real-file mutation target in production migration diff.

The only `DROP TABLE`, `ALTER TABLE`, `INSERT`, or `UPDATE` matches are inside disposable test helpers used to construct legacy SQLite fixtures and prove guard enforcement/rollback. No production table rebuild, data repair, delete, update, or business write path was found.

## QA Observations

- The disposable legacy SQLite fixture path exercises the approved real startup path through `init_db()` without touching the operator database.
- The Matrix Editor session probe is a GET and verified non-500 behavior.
- The confirmed Test Record preview probe is a GET and verified non-500 behavior; generation was not executed.
- The accepted TASK_361F index bootstrap remains covered in the same full suite.
- External parser/MCR, TASK_361E, board, release/settings, and unrelated documentation residuals must remain excluded by Integrator packaging.

## Residual Risk

- No production/operator DB smoke was performed in this QA gate because the active TASK_361G instruction explicitly forbids real `data/connlab.sqlite3`.
- This gate relies on disposable old-schema fixtures plus read-only startup/API probes for compatibility assurance.

## Decision

`QA gate: pass`

Recommended next role: Integrator packaging/readiness.

Integrator package guidance: stage only TASK_361G migration, focused disposable tests, and TASK_361G evidence/task/plan files. Exclude parser/MCR residuals, TASK_361E paused residuals, `docs/task_board.md` if not intentionally part of this package, real DB/files, frontend/API-client, Fee/Report/workbook/parser/LTR/public-drive, `.agents/**`, and `docs/project_management/**`.
