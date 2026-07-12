# TASK_361B Contact Measurement Plan Authority Backend - QA Evidence

Date: 2026-07-12

Role: QA / Smoke Owner

Task: `TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND`

Lane: `contact-measurement-plan-authority-backend`

Gate: QA gate

## Scope Read

- Read `AGENTS.md`; current phase remains Phase 11 controlled Project Workbench / Matrix / Approval Package foundation.
- Read `docs/task_board.md`; board/task text still lags the latest Reviewer callback and contains older blocked notes for TASK_361B. QA used the latest Reviewer evidence plus actual diff/status as the operative gate source.
- Read `tasks/TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND.md`.
- Read `docs/task_361b_contact_measurement_plan_authority_backend_plan.md`.
- Read TASK_361B Planner, reconciliation, Developer, and Reviewer evidence:
  - `docs/lane_evidence/TASK_361B_contact-measurement-plan-authority-backend_planner.md`
  - `docs/lane_evidence/TASK_361B_contact-measurement-plan-authority-backend_reconciliation_planner.md`
  - `docs/lane_evidence/TASK_361B_contact-measurement-plan-authority-backend_developer.md`
  - `docs/lane_evidence/TASK_361B_contact-measurement-plan-authority-backend_reviewer.md`
- Inspected current worktree status and TASK_361B candidate boundaries.

QA did not modify product source, tests, task board, real user DBs, real project folders, real LTR files, or public-drive paths. This file is QA evidence only.

## Candidate Package / External Residuals

Observed TASK_361B candidate package includes backend authority models, migration, repository, lifecycle/bootstrap/projection/impact/fingerprint helpers, typed API route registration, config flag, focused tests, and TASK_361B docs/evidence.

External residuals visible and excluded from TASK_361B packaging:

- `backend/modules/test_plan/mcr_text_normalizer.py`
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_mcr_text_normalizer.py`
- `tests/unit/test_spec_section_text_extractor.py`
- `docs/task_board.md`
- TASK_361A/discovery docs and unrelated future task docs
- `docs/superpowers/` plan files

Forbidden-scope status check found no TASK_361B frontend/client/TASK_361C-E/Fee/workbook/parser/LTR/public-drive/real-file package entry. A broad diff-context scan hit existing `backend/api/main.py` test-record-fee route context only; no semantic change to Test Record/Fee was found for TASK_361B.

## Validation Commands

Focused TASK_361B suite:

```powershell
py -m pytest tests/unit/test_config.py tests/unit/test_contact_measurement_plan_identity.py tests/unit/test_contact_measurement_plan_impact_classifier.py tests/unit/test_contact_measurement_plan_projection_service.py tests/unit/test_contact_measurement_plan_schema.py tests/integration/test_contact_measurement_plan_authority_bootstrap.py -q
```

Result: `29 passed in 7.24s`.

Python compile:

```powershell
py -m py_compile backend/domain/contact_measurement_plan_authority_models.py backend/application/contact_measurement_plan_identity.py backend/application/contact_measurement_plan_impact_classifier.py backend/application/contact_measurement_plan_bootstrap_service.py backend/application/contact_measurement_plan_lifecycle_service.py backend/application/contact_measurement_plan_projection_service.py backend/application/contact_measurement_plan_revision_fingerprint.py backend/application/contact_measurement_plan_revision_snapshot_helpers.py backend/infrastructure/storage/models_contact_measurement_plan_authority.py backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py backend/infrastructure/storage/repositories/contact_measurement_plan_authority.py backend/api/routes_contact_measurement_plan.py backend/api/dependencies.py backend/api/main.py backend/shared/config.py
```

Result: passed, exit code `0`.

Diff/trailing checks:

```powershell
git diff --check -- <TASK_361B candidate files>
```

Result: passed with LF/CRLF normalization warnings only.

Trailing whitespace scan over TASK_361B candidate files: no matches.

Line-count scan:

- `contact_measurement_plan_lifecycle_service.py`: 450 lines
- `contact_measurement_plan_bootstrap_service.py`: 377 lines
- `routes_contact_measurement_plan.py`: 371 lines
- all other checked TASK_361B Python files were below those counts

Result: all checked candidate Python files remain under the 500-line hard limit.

## Controlled Temp SQLite / API Smoke

All smoke used disposable OS temp directories and temp SQLite databases. No real user DB/project/file path was used.

Fresh schema + idempotency smoke:

```text
fresh_tables_present True
schema_idempotent_second_init True
revision_partial_index_names True True
revision_index_shapes (1, ('measurement_plan_root_id',)) (1, ('measurement_plan_root_id',))
target_fk_count 2
```

Enabled API, lifecycle patch, confirm, partial-compatible projection, and disabled typed write smoke:

```text
enabled_summary_open_patch_confirm_projection 200 not_started 200 200 200 confirmed 200 partial_compatible
disabled_read_write 200 disabled 503 contact_measurement_plan_authority_disabled
```

Candidate rebind / fingerprint / stale-token smoke:

```text
rebind_fingerprint_confirm True True True True needs_review
```

This confirms candidate subjects use `cmp-candidate:v1`, rebind advances fingerprint, old fingerprint confirm is rejected as stale, repeated rebind is idempotent enough to clear unresolved impacts, new fingerprint confirm succeeds, and effective projection remains `needs_review` after the active Matrix supersede scenario.

Malformed existing-schema rejection smoke:

```text
malformed_existing_schema_blocked True True
```

This covered a same-name extra partial predicate and a changed CHECK grouping. Both were rejected as `authority_corrupt` during `init_db()` without authority fallback.

## Behavior Coverage

Covered by focused tests plus controlled smoke:

- Fresh migration creates the six authority tables with required FK/index/check protections.
- Existing-good schema is idempotent on repeated `init_db()`.
- Wrong partial index predicate and changed CHECK grouping block with `authority_corrupt`.
- Active-confirmed legacy bootstrap, partial recovery, and root-no-fallback paths are covered by focused tests.
- Feature flag disabled mode keeps read surface typed and returns write `503`.
- Draft / confirmed / superseded lifecycle and stale confirm behavior are covered.
- Candidate rebind refreshes revision fingerprint; old token is rejected and new token can confirm.
- Impact classifier and partial-compatible projection are covered by unit/API smoke.
- Typed API route surface is covered by integration tests.

## QA Decision

`qa_pass`

Recommended next role/action: Integrator packaging/readiness.

Blocking summary: none.

Residual risk / packaging note: `docs/task_board.md` and older task text lag the latest Reviewer/QA pass state; Integrator should package only the reconciled TASK_361B candidate files and exclude the visible external parser/discovery/future-task residuals.
