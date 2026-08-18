# TASK_339A Project Lifecycle Frontend Readonly Model

Status: complete (archived 2026-08-18; implementation evidence in docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md)
Lane: frontend-readonly-model
Owner Role: Frontend Developer
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Plan and then implement the first frontend readonly behavior layer for project lifecycle states after TASK_337A backend lifecycle/API shape and TASK_338 lifecycle write guards are complete.

This task makes the existing frontend respect `active`, `stopped`, `closed_completed`, and `closed_administrative` project states without starting the Unified Project Workbench Shell implementation.

## 2. Required Plan First

Frontend Developer must first create:

```text
docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md
```

The plan must be reviewed and explicitly approved before frontend product code changes.

The plan must define:

- lifecycle state data source and frontend type usage
- readonly selector/helper/hook shape
- existing surfaces and write actions to update
- TASK_338 `project_lifecycle_readonly` error handling strategy
- non-mutating preview/read actions that must remain available
- UX copy for stopped and closed readonly states
- frontend tests to add or update
- files to edit

## 3. Required Inputs

Frontend Developer must read, in order:

- `AGENTS.md`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/task_board.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`
- `docs/task_338_project_lifecycle_write_guard_integration_plan.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`

Because this is frontend/UI work, `$impeccable` product-register guidance applies: the UI should remain calm, operational, state-first, and business-readable.

## 4. Scope

Allowed implementation scope after plan approval:

- frontend lifecycle API client/type consumption for existing project-facing screens
- shared frontend readonly helper, selector, or hook for lifecycle state
- existing Workbench and project-facing components that render lifecycle-dependent write actions
- disabled/readonly states for write actions covered by TASK_338 first slice
- consistent handling of TASK_338 readonly API errors
- focused frontend tests and build validation

Target behavior:

- `active`: preserve current write behavior.
- `stopped`: readonly business workflows; Resume and allowed Close actions remain visible where already supported by lifecycle UI/API surfaces.
- `closed_completed`: archived readonly; Resume unavailable.
- `closed_administrative`: archived readonly; Resume unavailable.
- Non-mutating preview/read actions remain available where TASK_338 classifies them as safe.

## 5. Non-Goals

This task must not:

- implement the Unified Project Workbench Shell from TASK_340
- redesign Projects registry lifecycle views
- implement new navigation IA beyond the readonly affordances needed in existing surfaces
- change backend lifecycle API shape
- change TASK_338 backend write guards
- implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- change Office gateway, public-drive authority, Matrix/Fee business rules, or Project Folder backend behavior
- hide preview/read actions broadly without TASK_338 non-mutating classification

## 6. May Touch

Only after user approval of the TASK_339A plan:

- frontend API client/type files explicitly listed in the approved plan
- frontend lifecycle readonly helper/selector/hook files explicitly listed in the approved plan
- existing frontend project-facing components explicitly listed in the approved plan
- frontend tests explicitly listed in the approved plan
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`

Planner/Integrator may touch:

- this task file
- `docs/task_board.md`
- TASK_339A lane evidence

## 7. Must Not Touch

- frontend product code before plan approval
- backend implementation
- TASK_338 backend guards
- Unified Workbench Shell implementation
- Projects registry redesign
- Office gateway internals
- Matrix/Fee business rules
- Project Folder backend behavior
- StepInstance, Report generation, AI, permissions, LAN/server, multi-user scope
- unrelated board lanes or global governance outside Planner/Integrator updates

## 8. Locked Paths

- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- frontend files explicitly listed in the approved TASK_339A plan

## 9. Validation Gate

Before review:

- plan approved by user before frontend product code changes
- `active` projects preserve current write behavior
- `stopped` projects render business workflows readonly and prevent frontend write submissions for scoped actions
- `closed_completed` and `closed_administrative` render archived readonly behavior
- Resume is unavailable for closed states
- TASK_338 readonly API errors surface as business-readable guidance
- non-mutating preview/read actions remain available where TASK_338 classifies them safe
- focused frontend tests pass
- frontend build passes

## 10. Merge Gate

Reviewer and Integrator gates are required before TASK_339A can be accepted.

Merge remains blocked if:

- frontend code is changed before plan approval
- backend code is changed from this lane
- Workbench Shell implementation or Projects registry redesign is mixed in
- frontend guesses backend guard behavior instead of consuming accepted TASK_337A/TASK_338 contract
- non-mutating preview/read actions are hidden broadly without explicit classification
- future scope appears under the readonly task

## 11. Stop Point

Frontend Developer must first create the TASK_339A plan and stop for user review.

No frontend product code may be written until the TASK_339A plan is explicitly approved.
