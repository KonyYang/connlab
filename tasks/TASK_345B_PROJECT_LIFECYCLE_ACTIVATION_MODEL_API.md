# TASK_345B Project Lifecycle Activation Model API

Status: approved - Developer implementation authorized after Reviewer readiness callback and user approval; implementation pending
Lane: project-lifecycle-activation-model-api
Owner Role: Developer implementation / Reviewer / QA / Integrator
Created: 2026-06-28

## Purpose

Create the first downstream backend lifecycle model/API/audit planning lane after the accepted `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`.

This lane defines the implementation contract for replacing the old permanent-readonly closed semantics with the new business lifecycle model:

- stopped and closed projects can use the `Activate` direction;
- `Completed` is one close reason, not a special close path;
- close uses one unified close form/API concept;
- user-facing product semantics must not expose `administrative`;
- audit/history preserves close and activate time, reason, operator, and previous close information.

This task has completed planning-first preparation. Per Planner reconciliation on 2026-06-28, implementation is authorized after:

- Reviewer plan gate passed;
- Developer planning-first completed;
- Reviewer implementation-readiness gate passed via conversational callback;
- user explicitly approved the Developer implementation pass.

Developer implementation must stay inside the backend/API/audit scope and the May Touch list below.

## Upstream Facts

- `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT` passed Reviewer plan gate per the current Orchestrator/User delegation.
- The user approved downstream lane creation after TASK_345A.
- Current repository code still exposes the previous lifecycle model:
  - `ProjectLifecycleState = active | stopped | closed`;
  - `ProjectClosureType = completed | administrative`;
  - lifecycle event types are `stop`, `resume`, `close_completed`, `close_administrative`;
  - closed projects cannot resume through the current lifecycle state service;
  - close API routes are split into `close-completed` and `close-administrative`.

## Scope To Plan

TASK_345B implements the backend/API/audit contract for:

- unified close request/response semantics;
- close reason taxonomy: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`;
- activation from `stopped` and `closed` to active project work;
- event/audit metadata required for previous lifecycle state, previous close reason/category, previous status/progress, operator, timestamp, and note;
- compatibility approach for existing `completed` / `administrative` closure data;
- typed API response shape and conflict/error contract;
- migration/backfill strategy if the implementation requires enum, column, or metadata changes;
- focused backend test scope.

## Non-Goals / Forbidden Scope

- Do not change frontend Workbench, Projects registry, or API client behavior.
- Do not update write guards; that belongs to a later TASK_345C lane.
- Do not implement Temporary Apply/Register LTR UI or public-drive LTR workbook authority writes.
- Do not implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope.
- Do not modify completed TASK_336 to TASK_345A source files except read-only reference.

## May Touch

Developer implementation may touch only:

- `backend/domain/enums.py`
- `backend/domain/models.py`
- `backend/domain/__init__.py`
- `backend/application/project_lifecycle_state_service.py`
- `backend/api/routes_project.py`
- `backend/api/dependencies.py`
- `backend/api/lifecycle_errors.py`
- `backend/infrastructure/storage/database.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/project.py`
- `backend/infrastructure/storage/repositories/project_lifecycle_event.py`
- `tests/unit/test_project_lifecycle_state_service.py`
- `tests/integration/test_project_lifecycle_api.py`
- `tests/integration/test_project_lifecycle_migration.py`
- `tests/integration/test_project_registry_summary_api.py`
- `tests/unit/test_project_lifecycle_write_guard.py` only for baseline assertions that must remain unchanged until TASK_345C
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`

Planner/board reconciliation may touch only:

- `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md`
- `docs/task_345b_project_lifecycle_activation_model_api_plan.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md`
- `docs/task_board.md` planned lane row and next-step text only

## Must Not Touch

- `frontend/`
- `tests/`
- `frontend/src/api/client.ts`
- public-drive, Office, LTR workbook authority files or gateways
- Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive implementation files
- completed TASK_336 to TASK_345A task/plan/evidence files except read-only reference
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

`tests/` is generally locked except for the specific TASK_345B backend test files named in May Touch.

## Locked Paths

- All frontend, API-client, Projects registry, public-drive LTR authority, Office, Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive, StepInstance, Report, AI, permissions, LAN/server, and multi-user paths are locked.
- Backend/API/schema/test paths outside the TASK_345B May Touch list are locked.
- Existing dirty workspace residuals remain outside this lane and must not be packaged with TASK_345B.

## Evidence Files

- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_developer.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_reconciliation_planner.md`

## Developer Validation Gate

- Focused backend lifecycle state service tests pass.
- Focused lifecycle API tests pass.
- Lifecycle migration tests pass.
- Registry summary lifecycle compatibility tests pass when affected.
- `tests/unit/test_project_lifecycle_write_guard.py` remains unchanged in behavior except baseline assertions explicitly needed to preserve TASK_345C boundary.
- `git diff --check` passes for TASK_345B changed files.
- Status check proves no frontend/API-client/public-drive LTR authority/future-scope files are included.

## Merge Gate

- Developer evidence reaches `ready_for_review`.
- Reviewer implementation gate passes with no blocking findings.
- QA gate is required if Reviewer or Integrator determines migration/API smoke needs independent validation; otherwise Integrator may package after Reviewer pass and focused backend validation.
- Integrator confirms no frontend/API-client/public-drive LTR authority/future-scope files are included.

## Recommended Next Role

Developer implementation pass for `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`.

## Stop Point

Stop after Developer implementation evidence reaches `ready_for_review`. Do not implement TASK_345C write guards, frontend UI, Projects registry, Temporary LTR authority, or future scope in this task.
