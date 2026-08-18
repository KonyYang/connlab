# TASK_344A Closed Lifecycle Smoke Data Fixture

Status: complete - Integrator accepted with documented data gap
Lane: closed-lifecycle-smoke-data-fixture
Owner Role: Planner/Reviewer/QA/Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Last Updated: 2026-06-28

## 1. Goal

Create a formal planning-first lane for safe closed completed/admin smoke data or a documented QA procedure after post-acceptance smoke found that the current local `/api/projects/registry` and lifecycle overlays did not contain closed completed/admin projects.

This lane exists so QA can verify closed `Open archive` rows and closed Workbench archive behavior with real or controlled local data without reopening accepted `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`.

## 2. Scope

In scope:

- Identify or create a safe local-only closed completed project for smoke verification.
- Identify or create a safe local-only closed administrative project for smoke verification.
- Document exact project IDs, setup steps, route checks, and cleanup/disposability.
- Verify `/projects` shows closed completed/admin rows with archive copy.
- Verify closed Workbench states are readonly and show no Stop, Resume, Close again, or close type conversion controls.

Out of scope:

- Production or authoritative data mutation.
- Backend/API/schema changes.
- Frontend product code changes.
- Workbench lifecycle behavior changes.
- TASK_343A/B/C implementation changes.
- Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## 3. May Touch

Planner activation may touch:

- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md`
- `docs/task_board.md`

Future QA/Closeout pass may touch:

- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_qa.md`
- optional docs-only QA procedure under `docs/qa_smoke/`

Future fixed fixture work is not approved by this Planner gate. If Reviewer decides a fixture script is necessary, Developer planning-first must propose exact non-product paths and prove the fixture is local, disposable, and non-destructive before any script is written.

## 4. Must Not Touch

- production or user business SQLite databases
- public-drive folders, Office files, LTR workbooks, or external authority files
- `backend/`
- `frontend/`
- root `tests/`
- database migrations or schemas
- `frontend/src/api/client.ts`
- Workbench lifecycle implementation
- TASK_343A/B/C accepted implementation files
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

## 5. Locked Paths

- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md`
- future `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_qa.md`
- any future `docs/qa_smoke/TASK_344A_*` procedure file, if QA creates one after routing

## 6. Validation Gate

Planner gate requires:

- task, plan, Planner evidence, and board row exist.
- lane explicitly avoids destructive production data mutation.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate are explicit.
- lane does not authorize product code changes.

Future QA gate requires:

- closed completed smoke data exists or a blocker explains why it cannot be safely prepared.
- closed administrative smoke data exists or a blocker explains why it cannot be safely prepared.
- `/projects` closed rows are inspected for `Open archive` and closed status copy.
- Workbench closed archive screens are inspected for no Stop/Resume/Close controls.
- data source, setup steps, project IDs, and cleanup/disposability are recorded.

## 7. Reviewer / QA / Merge Gates

Reviewer plan gate is required before QA uses this lane to prepare or document smoke data.

QA may run after Reviewer plan gate passes. Integrator may close the lane only after QA evidence is complete or a concrete blocker is recorded.

Merge remains blocked if the lane writes product code, touches production data, modifies backend/API/schema/frontend files, or mixes unrelated residuals.

## 8. Stop Point

Stop after Integrator packaging/readiness, local controlled commit, and completion callback.

Accepted outcome: QA documented that the current local data has no closed completed/admin lifecycle rows. This is a documented smoke-data gap, not a closed-row smoke success.

Recommended next role: User/Planner decision. If repeatable closed completed/admin smoke data is required later, route a separate Developer fixture-planning lane.

Do not prepare fixture data, write product code, push remote, reset, delete, or clean unrelated residuals from this TASK_344A closeout.
