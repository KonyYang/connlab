# Planner Evidence - TASK_343B Workbench Close Completed/Admin UX

Status: ready_for_review
Task: TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW
Lane: workbench-close-completed-admin-ux
Role: Planner/Designer
Updated: 2026-06-27

## Role Boundary

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active implementation lane: none. TASK_343A is complete/accepted by Integrator.

Planner is allowed to act because the user explicitly requested formal planning-first lane creation/activation for TASK_343B after TASK_343A acceptance.

This pass creates planning docs and board state only. It does not modify frontend code, backend code, tests, database schema, API implementation, runtime routing, or product behavior.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product/design context and product register
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- TASK_336 task and contract plan
- TASK_337A task, plan, and developer evidence
- TASK_338 plan and developer evidence
- TASK_339A plan and developer evidence
- TASK_340 task and plan
- TASK_341 task, plan, and developer evidence
- TASK_342 task and plan
- parent TASK_343 task, plan, and Planner evidence
- TASK_343A task, plan, developer evidence, and QA evidence
- read-only close API/client snippets in `backend/api/routes_project.py` and `frontend/src/api/client.ts`

## Discovery Gate Summary

Confirmed by user:

- TASK_343A was accepted by Integrator in local commit `27de54907f9f46f8c15669822328b49f07059969`.
- TASK_343B goal is Close as completed / Close administratively UX.
- Completed close v1 uses manual confirmation and output status summary because StepInstance does not exist.
- Administrative close requires explicit confirmation/reason/note and archives readonly.
- This Planner pass must not write product code or touch TASK_343A implementation.

Confirmed by repository evidence:

- Board marks TASK_343A complete/accepted and points TASK_343B as the next formal Discovery Gate.
- Parent TASK_343 split reserves close UI, confirmation dialog, output summary, note/reason fields, and close API calls for TASK_343B.
- TASK_337A backend routes and frontend API client helpers for completed/admin close already exist.
- TASK_336/TASK_337A require formal/registered eligibility for completed close by default and administrative close for temporary/no-LTR projects.
- TASK_338/TASK_339A/TASK_341 provide stopped/closed readonly behavior.

Inferred by Planner:

- TASK_343B can be frontend-only by default.
- Developer planning must verify completion summary data before implementation. If existing response data is insufficient, the lane should stop and request a separate approved backend/API scope change.
- QA is required because close archives the project and changes the main Workbench lifecycle flow.

Not yet confirmed:

- exact confirmation UI pattern.
- exact component decomposition.
- browser availability for QA.

These are not activation blockers because the plan keeps them inside Reviewer/Developer planning and QA gates.

Planner gate: ready.

## Files Created Or Updated

- `tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md`
- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_planner.md`
- `docs/task_board.md`

## May Touch

Planner activation:

- `tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md`
- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_planner.md`
- `docs/task_board.md`

Future Developer planning-first after Reviewer plan pass:

- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md`

Future implementation only after explicit approval:

- approved Workbench lifecycle/action frontend files under `frontend/src/features/project-workbench/`
- approved focused frontend tests
- `frontend/src/workbench.css`
- TASK_343B developer evidence

## Must Not Touch

- product code during this Planner pass
- `backend/`
- root `tests/`
- `frontend/src/api/client.ts` by default
- Projects registry implementation and `frontend/src/pages/ProjectListPage.tsx`
- TASK_343A implementation behavior
- TASK_343C files
- TASK_336 through TASK_342 files except read-only reference
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

## Locked Paths

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts`
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_*`
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- TASK_336 through TASK_342 task/plan/evidence files except read-only reference

## Validation Planned

Planner validation:

- TASK_343B task, plan, and Planner evidence exist.
- board row names `workbench-close-completed-admin-ux`.
- plan contains `Planner gate: ready`.
- plan contains formal/registered completed close boundary.
- `git diff --check` passes for TASK_343B planning docs and board.
- forbidden product scope status remains clean for backend, root tests, frontend API client, and Projects registry.

Future implementation validation is defined in `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`.

## Validation Results

Planner validation run on 2026-06-27:

- File existence check passed for:
  - `tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md`
  - `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
  - `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_planner.md`
  - `docs/task_board.md`
- `Select-String` checks found:
  - `workbench-close-completed-admin-ux`
  - `Planner gate: ready`
  - `formal/registered`
  - `temporary/no-LTR`
  - `manual confirmation`
  - `output status summary`
  - `closeProjectCompletedLifecycle`
  - `closeProjectAdministrativeLifecycle`
  - `Reviewer plan gate`
  - `StepInstance`
  - `TASK_343C`
- `git diff --check -- tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md docs/task_343b_close_completed_admin_confirmation_flow_plan.md docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_planner.md docs/task_board.md` passed with only the existing `docs/task_board.md` LF/CRLF working-copy warning.
- Forbidden product scope status was clean for:
  - `backend`
  - `tests`
  - `frontend/src/api/client.ts`
  - `frontend/src/features/projects-registry`
  - `frontend/src/pages/ProjectListPage.tsx`
  - `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
  - `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- Current remaining dirty paths outside TASK_343B are unrelated governance/orchestration residuals:
  - `AGENTS.md`
  - `.agents/skills/*`
  - `docs/project_management/*`

## Stop Point

Status: ready_for_review.

Recommended next role: Reviewer plan gate.

Do not route directly to Developer implementation. Do not start TASK_343C, backend changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, commit, push, reset, delete, or unrelated cleanup from this Planner pass.
