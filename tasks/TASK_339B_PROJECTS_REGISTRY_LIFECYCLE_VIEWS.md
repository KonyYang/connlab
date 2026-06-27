# TASK_339B Projects Registry Lifecycle Views

Status: approved
Lane: projects-registry-lifecycle-views
Owner Role: Frontend Developer
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Plan and then implement Projects registry lifecycle views after TASK_339A frontend readonly model is accepted.

This task is limited to Projects registry lifecycle visibility: filters, row status labels, lifecycle-aware grouping, and business-readable registry signals for active, stopped, closed completed, and closed administrative projects.

## 2. Planner Gate

Planner Discovery Gate is recorded in:

```text
docs/task_339b_projects_registry_lifecycle_views_plan.md
```

The lane is approved for planning first after Planner restored the TASK_340 source files from `stash@{0}^3` on 2026-06-27.

Restored TASK_340 source files:

- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`

TASK_340 remains background for the later TASK_341 Workbench shell implementation. TASK_339B must not implement the Workbench shell.

## 3. Required Plan First

After the Planner blocker is closed and this lane is activated, Frontend Developer must first review or update:

```text
docs/task_339b_projects_registry_lifecycle_views_plan.md
```

The plan must be reviewed and explicitly approved before frontend product code changes.

The plan must define:

- Projects registry lifecycle data source
- lifecycle view/filter behavior
- row status and badge copy
- default view behavior for active/stopped/closed projects
- relationship to TASK_339A readonly model
- frontend tests to add or update
- files to edit

## 4. Required Inputs

Frontend Developer must read, in order:

- `AGENTS.md`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/task_board.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`

- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`

Because this is frontend/UI work, `$impeccable` product-register guidance applies: the registry should remain dense, operational, state-first, and business-readable.

## 5. Scope

Allowed implementation scope after lane activation and plan approval:

- Projects registry lifecycle filters or views
- Projects registry row lifecycle status/badge copy
- Projects registry lifecycle sorting/grouping helpers
- frontend API client/type use only if the current Projects registry DTO already exposes the needed lifecycle fields, or if the approved plan explicitly keeps any DTO change frontend-only
- focused frontend tests

Target behavior:

- active projects remain visible in the normal operational registry flow
- stopped projects are visible as paused/read-only and easy to find
- closed completed projects are visible as completed archives
- closed administrative projects are visible as administrative archives
- registry copy must use business labels, not backend enum names

## 6. Non-Goals

This task must not:

- implement the Unified Project Workbench Shell
- implement TASK_341 or TASK_342
- change backend lifecycle API shape
- change TASK_338 backend guards
- change TASK_339A readonly model behavior outside registry consumption
- implement lifecycle Stop/Resume/Close actions from the registry unless explicitly approved later
- implement Report generation
- implement StepInstance or execution persistence
- introduce AI, permissions, LAN/server, or multi-user scope
- change Office gateway, public-drive authority, LTR workbook behavior, Matrix/Fee business rules, or Project Folder backend behavior

## 7. May Touch

Only after this lane is activated and the TASK_339B plan is explicitly approved:

- `frontend/src/pages/ProjectListPage.tsx`
- frontend registry helper/test files explicitly listed in the approved TASK_339B plan
- `frontend/src/api/client.ts` only for typed consumption of already-available registry lifecycle fields explicitly listed in the approved plan
- frontend CSS files explicitly listed in the approved plan for registry lifecycle badges/views
- focused frontend tests explicitly listed in the approved plan
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`

Planner/Integrator may touch:

- this task file
- `docs/task_board.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- TASK_339B lane evidence

## 8. Must Not Touch

- frontend product code before lane activation and plan approval
- backend implementation
- TASK_338 backend write guards
- Unified Workbench Shell implementation
- Project Workbench shell layout or navigation IA
- Office gateway internals
- Matrix/Fee business rules
- Project Folder backend behavior
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- public-drive authority replacement
- unrelated governance/orchestration residual files

## 9. Locked Paths

- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`
- frontend registry files explicitly listed in the approved TASK_339B plan

## 10. Validation Gate

Before review:

- plan approved by user before frontend product code changes
- active/stopped/closed completed/closed administrative registry views are covered
- registry copy uses business labels and does not expose raw enum names
- default registry view remains operational for active work
- archived closed projects remain findable without crowding the active work queue
- focused frontend tests pass
- frontend build passes

## 11. Merge Gate

Reviewer, QA if required by the approved plan, and Integrator gates are required before TASK_339B can be accepted.

Merge remains blocked if:

- frontend code is changed before lane activation and plan approval
- backend code is changed from this lane
- Workbench Shell implementation, TASK_341, or TASK_342 is mixed in
- Projects registry starts lifecycle write actions without explicit approval
- future scope appears under the registry lifecycle views task

## 12. Stop Point

This lane is approved for Frontend Developer planning first.

Frontend Developer must review/update the TASK_339B plan and stop for user approval before frontend product code changes.
