# TASK_345A Project Lifecycle Business Model Contract

Status: complete (archived 2026-08-18; planning contract delivered - evidence in docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md)
Lane: project-lifecycle-business-model-contract
Owner Role: Planner / Reviewer plan gate
Created: 2026-06-28

## Purpose

Create the replacement business model contract for Project lifecycle behavior after `DISCOVERY_project-lifecycle-business-model-rework`.

This task is a planning and contract lane only. It must not write backend, frontend, test, schema, LTR authority, Office, public-drive, Matrix, Fee, Folder, Report, StepInstance, AI, permissions, LAN/server, or multi-user product code.

## Confirmed Direction

- Workbench lifecycle UI should show one primary lifecycle action at a time.
- Active projects use `Close project` as the primary lifecycle action.
- Stopped and closed projects use an Activate direction. `Reopen project` is not the only or permanent closed-state semantic.
- `Close project` is a business phase transition, not irreversible archive sealing.
- `Completed` is not a separate close endpoint or special close path in the new model. All close reasons use one unified close form.
- Close reasons are business reasons: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, `Other`.
- User-facing UI must not expose internal `administrative` wording.
- Lifecycle audit history must preserve close and activate time, reason, operator, and previous close type/reason.
- Temporary projects should expose an `Apply LTR number` / `Register LTR` workflow entrypoint.
- Public-drive LTR workbook authority writeback remains out of this first contract implementation series. A later authority lane must handle actual workbook authority writes.

## Repository Facts

- `docs/task_board.md` reports no active implementation lane and `TASK_344C` complete/accepted.
- `docs/lane_evidence/DISCOVERY_project-lifecycle-business-model-rework_planner.md` records the current code and task evidence.
- Current accepted TASK_336 to TASK_344 semantics treat closed projects as readonly archives that cannot resume.
- Current backend lifecycle API exposes stop, resume, close-completed, and close-administrative endpoints, with `ProjectClosureType = completed | administrative`.
- Current frontend still exposes user-facing administrative close copy in Workbench and readonly archive copy in Workbench/Projects registry.
- Current frontend has no activate/reopen client helper for closed projects.
- Current Workbench temporary formalization entrypoint is present as copy/placeholder behavior only. Same-project LTR registration is not wired.

## Scope

This lane defines the contract that later implementation lanes must follow:

- lifecycle state and action vocabulary
- state transition rules
- close reason taxonomy
- activate behavior for stopped and closed projects
- audit/history expectations
- temporary Apply/Register LTR entrypoint boundary
- UI copy requirements
- backend/API implementation lane split
- write guard update lane split
- Workbench UI lane split
- Projects registry copy/routing lane split
- QA/audit/integration closeout lane split

## Non-Goals

- Do not implement backend lifecycle APIs.
- Do not implement database migrations.
- Do not update write guards.
- Do not update frontend Workbench or Projects registry runtime behavior.
- Do not write public-drive LTR workbook authority.
- Do not implement temporary-to-formal LTR authority writes.
- Do not implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope.
- Do not rewrite or reopen completed TASK_336 to TASK_344 files except by read-only reference.

## May Touch

- `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- `docs/task_board.md` planned/proposed lane row and next-step text only
- `docs/lane_evidence/DISCOVERY_project-lifecycle-business-model-rework_planner.md` read-only reference

## Must Not Touch

- `backend/`
- `frontend/`
- `tests/`
- `frontend/src/api/client.ts`
- public-drive, Office, LTR workbook authority files or gateways
- Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive implementation files
- completed TASK_336 to TASK_344 task/plan/evidence files except read-only reference
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

## Locked Paths

- Product implementation paths are locked for this lane.
- No backend, frontend, or test runtime path is reserved or editable by this lane.
- Future implementation lanes must declare their own locked paths after this contract is accepted.

## Validation Gate

- Contract plan exists and names the new target lifecycle semantics.
- Contract plan clearly states that this lane is not approved implementation.
- Contract plan documents May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate.
- Contract plan includes downstream lane split and serial/parallel guidance.
- Contract plan includes no TASK_345A product code changes; any pre-existing product dirty paths must be recorded as outside this Planner package and excluded from routing.
- `git diff --check` passes for TASK_345A planning files and board update.

## Merge Gate

- Reviewer plan gate must pass before the contract can become accepted.
- User approval is required before any downstream implementation lane may be marked approved.
- Orchestrator must not route Developer from this planned contract draft.

## Recommended Next Role

Reviewer plan gate for `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`.

## Stop Point

Stop after creating/updating this task, plan, Planner evidence, and planned board row. Do not route Developer implementation.
