# TASK_345B Project Lifecycle Activation Model API

Status: planned - planning-first backend/API contract draft, not approved for implementation
Lane: project-lifecycle-activation-model-api
Owner Role: Planner / Reviewer plan gate
Created: 2026-06-28

## Purpose

Create the first downstream backend lifecycle model/API/audit planning lane after the accepted `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`.

This lane defines the implementation contract for replacing the old permanent-readonly closed semantics with the new business lifecycle model:

- stopped and closed projects can use the `Activate` direction;
- `Completed` is one close reason, not a special close path;
- close uses one unified close form/API concept;
- user-facing product semantics must not expose `administrative`;
- audit/history preserves close and activate time, reason, operator, and previous close information.

This task is a planning-first lane only. It must not implement backend, frontend, test, schema, public-drive LTR workbook authority, Office, StepInstance, Report, AI, permissions, LAN/server, or multi-user product code.

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

TASK_345B must plan the backend/API/audit contract for:

- unified close request/response semantics;
- close reason taxonomy: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`;
- activation from `stopped` and `closed` to active project work;
- event/audit metadata required for previous lifecycle state, previous close reason/category, previous status/progress, operator, timestamp, and note;
- compatibility approach for existing `completed` / `administrative` closure data;
- typed API response shape and conflict/error contract;
- migration/backfill strategy if the implementation requires enum, column, or metadata changes;
- focused backend test scope.

## Non-Goals

- Do not implement product code in this Planner pass.
- Do not change frontend Workbench, Projects registry, or API client behavior.
- Do not update write guards; that belongs to a later TASK_345C lane.
- Do not implement Temporary Apply/Register LTR UI or public-drive LTR workbook authority writes.
- Do not implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope.
- Do not modify completed TASK_336 to TASK_345A source files except read-only reference.

## May Touch

- `tasks/TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API.md`
- `docs/task_345b_project_lifecycle_activation_model_api_plan.md`
- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`
- `docs/task_board.md` planned lane row and next-step text only

Future implementation after Reviewer/user approval may propose backend/API/test paths in its own Developer plan, but those paths are locked during this Planner pass.

## Must Not Touch

- `backend/`
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

## Locked Paths

- All product implementation paths are locked for this Planner lane.
- Backend/API/schema/test files are candidate future implementation paths only; they are not editable until TASK_345B passes Reviewer plan gate and receives explicit implementation approval.
- Existing dirty workspace residuals remain outside this lane and must not be packaged with TASK_345B.

## Evidence File

- `docs/lane_evidence/TASK_345B_project-lifecycle-activation-model-api_planner.md`

## Validation Gate

- TASK_345B task, plan, evidence, and board row exist.
- Lane status remains `planned`, not approved implementation.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate are explicit.
- Plan names downstream dependencies: write guard, Workbench UI, Projects registry, Temporary Apply/Register LTR entrypoint, QA/integration.
- `git diff --check` passes for TASK_345B planning files and board update.
- Status check records any existing dirty product paths as outside this Planner package.

## Merge Gate

- Reviewer plan gate must pass before TASK_345B can be accepted as a backend/API implementation plan.
- User approval is required before any Developer implementation may start.
- Orchestrator must not route Developer from this planned lane.

## Recommended Next Role

Reviewer plan gate for `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`.

## Stop Point

Stop after creating/updating this task, plan, Planner evidence, and planned board row. Do not route Developer implementation.
