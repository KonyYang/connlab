# TASK_361B Contact Measurement Plan Authority Backend Planner Evidence

Date: 2026-07-12

Role: Planner

Status: implementation authorized; B5R reconciled; Reviewer implementation re-gate
blocked pending Developer B3R/B4R fixes. Not complete.

## Current Phase / Why Allowed

Phase 11 controlled Matrix foundation. TASK_361A is complete/accepted as a frozen
contract and downstream planning basis. `TASK_361B` was checked against the board,
tasks, plans, and evidence and was not formally occupied.

## Confirmed By User

- Reconcile TASK_361A as an accepted contract basis without claiming schema/product
  implementation.
- Create the next planned-only backend authority lane.
- Record additive non-destructive schema, idempotent legacy bootstrap,
  rollback/compatibility, stable `cmp-target:v1`, independent lifecycle, impact
  classifier, and partial-compatible projection.
- Keep the UI workspace in TASK_361C. This Planner action does not itself route
  Developer; after reconciliation, Developer implementation is the next legal role.

## Confirmed By Repository Evidence

- Existing contact plans live in draft/confirmed Matrix Step quantity
  `contact_plan_json` and currently promote with Matrix confirmation.
- Imported source snapshot ids exist, while manual Group/Row lineage is nullable and
  generated draft/confirmed ids are not stable cross-revision identities.
- Existing SQLite initialization registers SQLAlchemy model modules and additive
  migration helpers; focused temporary-SQLite tests are an established pattern.
- Current Fee and specialized-workbook consumers read active confirmed Matrix Step
  quantities and have no independent Measurement Plan lifecycle.

## Planner Decisions

- TASK_361B is backend-only and uses six additive first-class tables; no existing
  Matrix table or JSON value is altered.
- Bootstrap is lazy and transactional per Project with unique canonical provenance,
  so startup does not perform an unbounded data rewrite.
- A pure impact classifier feeds an application lifecycle service; API routes remain
  typed and thin.
- The effective projection is explicitly partial-compatible and is exposed for
  later consumers, but consumer migration is deferred to TASK_361E.

## Reviewer B1/B2 Fix

- `measurement_plan_impacts` now has non-null canonical
  `impact_subject_key`/`impact_identity_key`; absent evidence uses literal `none`, and
  SQLite uniqueness is `(editable_revision_id, impact_identity_key)`. Repeated
  unmatched refresh/recovery is idempotent without nullable-UNIQUE semantics.
- Target snapshots now require source-lineage XOR manual-anchor independently for
  Group and Row axes. Canonical `cmp-target:v1` equality is validated in SQLite
  shape checks plus application/repository parsing. Malformed partial rows block as
  `authority_corrupt`; they are never guessed, silently repaired, or used for legacy
  fallback after a root exists.
- Rollback flag ownership is limited to `backend/shared/config.py` as
  `Settings.contact_measurement_plan_authority_enabled`, default `true`, environment
  override `CONNLAB_CONTACT_MEASUREMENT_PLAN_AUTHORITY_ENABLED`, explicit dependency
  injection through `backend/api/dependencies.py`, and direct boolean test injection.
  A dedicated private parser accepts the documented true/false tokens and rejects
  invalid non-blank values without changing the existing shared `_bool_setting` or
  LTR/settings semantics.
  Settings UI/routes, local config, database settings, and LTR/public configuration
  remain locked.

## Not Yet Confirmed

No blocking product decision remains for the reviewed TASK_361B implementation
scope. Any scope expansion remains unconfirmed and requires a new Planner/Reviewer
gate.

## Authorization Reconciliation

- Reviewer B1/B2 plan re-gate passed.
- The user approved Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness passed.
- The user approved source-of-truth reconciliation and implementation of the
  reviewed additive schema/migration/backend/API/config/focused-test package on
  2026-07-12.
- TASK_361B is implementation authorized but remains pending Developer
  implementation. No product, schema, migration, config, API, or test file was
  changed by this Planner reconciliation.

## B5R Helper Scope Reconciliation

- `backend/application/contact_measurement_plan_revision_fingerprint.py` is 46 lines
  and owns only deterministic optimistic-concurrency fingerprints over editable
  authority target/family snapshots.
- `backend/application/contact_measurement_plan_revision_snapshot_helpers.py` is 193
  lines and owns only lifecycle-internal target/family snapshot copy, canonical
  replacement, and idempotent impact persistence.
- Both are below the AGENTS 300-line target and 500-line hard limit. Their imports
  stay within TASK_361B identity plus authority storage model/repository boundaries;
  no frontend, client, Fee/workbook, parser, LTR, or TASK_361C-E dependency exists.
- They are therefore authorized as exact TASK_361B May Touch paths. This is a module
  split reconciliation, not a scope expansion.
- B3R and B4R remain unresolved product findings and are not modified by this
  Planner pass.

## Scope And Locks

Future May Touch is limited to the exact new domain/application/storage/repository/
API modules, narrow database/dependency/main registration, the one backend-only
field/load path in `backend/shared/config.py`, its focused `tests/unit/test_config.py`
coverage, focused backend tests, and TASK_361B governance files listed in the
task/plan. Frontend, Office/workbook,
Fee/formal consumers, generic Test Record, parser/import, Basic Information,
LTR/public-drive, StepInstance/Report, real files, release/settings UI/API/local
config, `.agents/**`,
and `docs/project_management/**` remain locked.

## Validation And Merge Gates

The plan requires fresh/existing temporary SQLite migration tests, repeated/partial
bootstrap, rollback adapter, identity/classifier/lifecycle/projection/API coverage,
compile/diff/trailing/forbidden-scope checks, and full Reviewer/QA/Integrator gates.
No schema or product file is changed in this Planner pass.

Planner fix validation passed: docs diff-check reported only existing LF/CRLF
working-copy warnings; trailing-whitespace scan was clean; stale nullable-impact
UNIQUE and nonexistent shared strict-parser wording were absent. Targeted status
still shows only the pre-existing external parser/test residuals under product paths;
this fix pass changed governance documents only.

Current external parser/test and TASK_360Q residuals are not TASK_361B package
inputs and must remain excluded during Reviewer, Developer, QA, and Integrator
gates.

## Definition Of Ready

Source-of-truth is reconciled for B5R. The next legal role is Developer fix pass for
B3R/B4R, followed by Reviewer implementation re-gate. QA/Integrator remain blocked.

## Evidence Paths

- `tasks/TASK_361B_CONTACT_MEASUREMENT_PLAN_AUTHORITY_BACKEND.md`
- `docs/task_361b_contact_measurement_plan_authority_backend_plan.md`
- `docs/lane_evidence/TASK_361B_contact-measurement-plan-authority-backend_planner.md`
- `docs/lane_evidence/TASK_361A_contact-measurement-plan-authority-impact-contract_reconciliation_planner.md`
- `docs/lane_evidence/TASK_361B_contact-measurement-plan-authority-backend_reconciliation_planner.md`
