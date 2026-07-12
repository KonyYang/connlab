# TASK_361B Contact Measurement Plan Authority Backend

## Status

Complete / Integrator accepted on 2026-07-12 after Developer implementation,
Reviewer final implementation re-gate, QA gate, and controlled Integrator
packaging/readiness. B3R2, B4R4/B4R5, B5R, and B6 are closed.

## Lane

`contact-measurement-plan-authority-backend`

## Current Phase / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Upstream: TASK_361A is complete/accepted as the frozen contract basis.
- Role: Integrator packaging/readiness.
- Why allowed: Reviewer final implementation re-gate passed, QA gate passed, and
  the package is limited to the reviewed backend authority/config/API/test scope
  plus TASK_361A/B source-of-truth documents and precise board closeout.

## Goal

Plan the additive, non-destructive SQLite authority storage, migration/bootstrap,
domain/repository/application lifecycle, deterministic Matrix impact classifier,
typed backend APIs, and effective confirmed projection for an independent Contact
Measurement Plan.

This lane is backend-only. The dedicated setup workspace remains TASK_361C, draft
workbook output remains TASK_361D, and formal consumer migration remains TASK_361E.

## Contract Deliverables

1. Six-table additive authority schema with exact columns, constraints, and indexes.
2. Idempotent active-confirmed legacy bootstrap and compatibility/rollback adapter.
3. `cmp-target:v1` imported-lineage/manual-anchor identity implementation boundary.
4. `draft` / `needs_review` / `confirmed` / `superseded` lifecycle and stale guards.
5. Pure Matrix impact classifier and partial-compatible effective projection.
6. Typed backend read/command API foundation with no Office or UI logic.
7. Focused unit, migration, repository, application, and API validation plan.

## Authorized May Touch For Developer Implementation

- `backend/domain/contact_measurement_plan_authority_models.py`
- `backend/application/contact_measurement_plan_identity.py`
- `backend/application/contact_measurement_plan_impact_classifier.py`
- `backend/application/contact_measurement_plan_bootstrap_service.py`
- `backend/application/contact_measurement_plan_lifecycle_service.py`
- `backend/application/contact_measurement_plan_projection_service.py`
- `backend/application/contact_measurement_plan_revision_fingerprint.py` only for
  deterministic editable-revision optimistic-concurrency fingerprints over
  authority target/family snapshots
- `backend/application/contact_measurement_plan_revision_snapshot_helpers.py` only
  for lifecycle-internal target/family snapshot copy, canonical target replacement,
  and idempotent impact persistence
- `backend/infrastructure/storage/models_contact_measurement_plan_authority.py`
- `backend/infrastructure/storage/contact_measurement_plan_authority_schema_migration.py`
- `backend/infrastructure/storage/repositories/contact_measurement_plan_authority.py`
- `backend/infrastructure/storage/repositories/__init__.py`
- `backend/infrastructure/storage/database.py`
- `backend/shared/config.py` only for the backend-only
  `contact_measurement_plan_authority_enabled` runtime flag
- `backend/api/routes_contact_measurement_plan.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_config.py` only for the scoped runtime flag
- focused new tests under `tests/unit/` and `tests/integration/`
- TASK_361B task/plan/evidence and board through normal lane flow

The implementation package must remain within these paths unless Planner and
Reviewer re-gate an explicitly justified addition.

The two revision helpers are an internal module split of the already authorized
identity/classifier/lifecycle boundary. Current files are 46 and 193 lines,
respectively, below the AGENTS 300-line target and 500-line hard limit. They do not
authorize TASK_361C-E, frontend/API client, Fee/workbook, Matrix parser,
LTR/public-drive, or other locked scope.

## Must Not Touch / Locked Paths

- No `frontend/**` or frontend API client; TASK_361C owns setup UI/client wiring.
- No TASK_360B workbook generation/artifact code; TASK_361D owns draft output and
  TASK_361E owns confirmed specialized-workbook consumer migration.
- No Fee rules/default-fill or formal Fee consumer migration before TASK_361E.
- No generic Test Record semantics, Matrix parser/import, Basic Information,
  LTR/public-drive, Folder Actions, StepInstance/execution, Report, release/settings,
  or real workbook/folder mutation.
- No Settings UI, settings route, local-config persistence, LTR/public configuration,
  or operator-editable settings expansion. The rollback flag is backend environment
  configuration only.
- Existing Matrix `contact_plan_json` columns and values are compatibility input and
  must not be rewritten, deleted, or relaxed.
- `.agents/**`, `docs/project_management/**`, remote push, and destructive git
  operations remain locked.

## Validation Gate

- Exact schema, fresh-db registration, existing-db additive migration, indexes, and
  lifecycle constraints are covered with temporary SQLite tests.
- Bootstrap tests cover eligible legacy state, no eligible state, repeated runs,
  partial prior runs, invalid JSON, provenance uniqueness, and no legacy mutation.
- Unit tests cover stable keys, manual-anchor non-auto-match, family validation,
  per-axis source/manual XOR rejection, canonical unmatched-impact dedupe, repeated
  recovery, impact categories, stale `409` paths, lifecycle transitions, and
  immutable history.
- Config tests prove the authority flag defaults enabled, parses its one environment
  override, is injected explicitly, and selects read-only legacy compatibility when
  disabled without mutating either authority store.
- Projection/API tests prove compatible-only output, omission diagnostics, no draft
  leakage, and no fallback to legacy JSON after an independent root exists.
- No frontend, Office, workbook, real-file, or formal-consumer mutation occurs.
- `py -m pytest` focused suites, compile checks, `git diff --check`, trailing
  whitespace, and forbidden-scope scans pass.

## Merge Gate

Reviewer plan re-gate, user-approved Developer planning-first, explicit
schema/backend implementation authorization, Developer implementation, Reviewer
final implementation re-gate, QA gate, and Integrator packaging/readiness are
complete. The accepted package excludes frontend/API client, parser residuals,
TASK_360Q/R/S, TASK_361C-E, Fee/workbook consumers, release/settings residuals,
real files, `.agents/**`, and `docs/project_management/**`.

## Definition Of Ready

Complete. TASK_361B is accepted as the backend authority foundation for later
TASK_361C/D/E lanes, which still require their own planning, review, QA, and
Integrator gates before implementation or packaging.

## Blocking Questions

None for plan review.
