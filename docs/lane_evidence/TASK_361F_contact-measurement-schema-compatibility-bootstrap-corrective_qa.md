# TASK_361F Contact Measurement Schema Compatibility Bootstrap Corrective - QA Evidence

Date: 2026-07-13
Role: QA / Smoke Owner
Lane: `contact-measurement-schema-compatibility-bootstrap-corrective`
Result: `qa_pass`

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE.md`
- `docs/task_361f_contact_measurement_schema_compatibility_bootstrap_corrective_plan.md`
- `docs/lane_evidence/TASK_361F_contact-measurement-schema-compatibility-bootstrap-corrective_developer.md`
- `docs/lane_evidence/TASK_361F_contact-measurement-schema-compatibility-bootstrap-corrective_reviewer.md`
- TASK_361F migration/test diff and focused schema/startup/API tests

Board note: `docs/task_board.md` still states TASK_361F as implementation-authorized / pending Developer implementation, while the latest Reviewer evidence and delegation callback state `reviewer_pass`. QA used latest lane evidence plus actual diff/status for this gate and did not update the board.

## Validation Commands

Focused temporary authority/startup/API suite:

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_361f_qa_full tests/unit/test_contact_measurement_plan_schema.py tests/integration/test_contact_measurement_plan_schema_compatibility_startup.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_matrix_editor_test_record_generation_api.py -q
```

Result:

```text
38 passed in 40.10s
```

Compile:

```powershell
py -m py_compile backend\infrastructure\storage\contact_measurement_plan_authority_schema_migration.py
```

Result: passed.

Diff / whitespace:

```powershell
git diff --check -- backend\infrastructure\storage\contact_measurement_plan_authority_schema_migration.py tests\unit\test_contact_measurement_plan_schema.py tests\integration\test_contact_measurement_plan_schema_compatibility_startup.py docs\lane_evidence\TASK_361F_contact-measurement-schema-compatibility-bootstrap-corrective_developer.md docs\lane_evidence\TASK_361F_contact-measurement-schema-compatibility-bootstrap-corrective_reviewer.md docs\task_361f_contact_measurement_schema_compatibility_bootstrap_corrective_plan.md tasks\TASK_361F_CONTACT_MEASUREMENT_SCHEMA_COMPATIBILITY_BOOTSTRAP_CORRECTIVE.md
```

Result: passed with existing LF/CRLF warnings only for the migration and unit schema test.

UTF-8 trailing whitespace scan over the same TASK_361F candidate files: no matches.

Line counts:

```text
backend\infrastructure\storage\contact_measurement_plan_authority_schema_migration.py 315
tests\unit\test_contact_measurement_plan_schema.py 318
tests\integration\test_contact_measurement_plan_schema_compatibility_startup.py 257
```

All are below the AGENTS hard limit.

## Disposable Fixture QA Smoke

All smoke used temporary SQLite databases only. QA did not open, copy, or modify real `data/connlab.sqlite3` or any operator database.

Additional direct QA fixture script:

```text
all_four_init_db [] True ['uq_measurement_plan_confirmed_per_root', 'uq_measurement_plan_editable_per_root', 'uq_measurement_plan_impact_identity', 'uq_measurement_plan_target_key']
target_duplicate_preflight authority_corrupt []
```

Interpretation:

- A disposable legacy authority database with all four semantic indexes/constraints removed had an empty canonical-index set before recovery.
- Running the real `init_db()` startup boundary restored and read-verified all four canonical semantic indexes.
- A disposable target duplicate fixture failed with `authority_corrupt`.
- After the duplicate failure, the canonical-index set was still empty, proving no partial canonical DDL from that failed attempt.

Focused suite coverage confirmed:

- legacy missing named indexes complete `init_db()` startup and no longer mask Matrix Editor routes;
- all-four-missing semantic indexes are bootstrapped through `init_db()`;
- alternate equivalent partial index names are accepted;
- target/impact duplicate and NULL identity fixtures fail before canonical DDL;
- mixed/wrong-shape/non-index CHECK/FK incompatibilities fail closed;
- bootstrap idempotency across independent engines;
- DDL rollback on simulated partial failure;
- locked writer reports failure without fallback;
- Matrix Editor session, draft-cancel, and Test Record startup API no longer return the previous global startup `500`.

## Scope / Locked Path Checks

Status/diff observations:

- TASK_361F candidate files are limited to the schema migration, focused schema/startup tests, and TASK_361F docs/evidence.
- `git diff --name-only` locked-scope scan hit only existing external parser residuals:
  - `backend/modules/test_plan/mcr_text_normalizer.py`
  - `backend/modules/test_plan/spec_section_text_extractor.py`
  - `tests/unit/test_mcr_text_normalizer.py`
  - `tests/unit/test_spec_section_text_extractor.py`
- TASK_361F candidate hunk scan found no real database path, frontend/API-client, TASK_361E, Fee, Report, public-drive/LTR, workbook, parser/MCR/spec-section, `.agents/**`, or `docs/project_management/**` scope.
- Untracked paused TASK_361E governance files are present in the worktree but remain external and excluded.
- `docs/task_board.md`, parser/MCR files, TASK_360Q/R/S task/planning files, and superpowers plan files remain external residuals and must be excluded by Integrator.

## Product Source Changes By QA

QA did not modify product code, tests, real databases, or real files. QA added this evidence file only. The temporary pytest basetemp `tmp\task_361f_qa_full` was removed after validation.

## Residual Risk

- QA did not run against a real operator database by design; real `data/connlab.sqlite3` is locked by the task.
- Validation confidence comes from disposable existing-database fixtures, focused startup/API regressions, and the direct extra smoke above.
- TASK_361E remains paused and was not resumed or validated as part of this gate.

## QA Gate Result

`QA gate: pass`

Recommended next role: `Integrator packaging/readiness`

Integrator note: stage only the reconciled TASK_361F migration/test/docs/evidence package. Exclude paused TASK_361E files, parser/MCR residuals, `docs/task_board.md` unless explicitly part of Integrator closeout, TASK_360Q/R/S planning residuals, superpowers plans, and every unrelated dirty file.
