# TASK_341 Unified Project Workbench Shell Implementation

Status: complete
Lane: unified-workbench-shell-implementation
Owner Role: Frontend Developer
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Plan first, then implement the first controlled frontend slice of the accepted Unified Project Workbench Shell.

TASK_341 uses the accepted TASK_340 shell plan as its information architecture input and the completed TASK_339A/TASK_339B lifecycle frontend work as its lifecycle/registry baseline. The implementation must make the existing Project Workbench feel like one lifecycle-aware workspace without starting TASK_342 closeout or any future execution/reporting scope.

## 2. Planner Gate

Planner Discovery Gate is recorded in:

```text
docs/task_341_unified_project_workbench_shell_implementation_plan.md
```

This lane is approved for Frontend Developer planning first because:

- `TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT` is complete and accepted.
- `TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE` is complete and accepted.
- `TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION` is complete and accepted.
- `TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL` is complete and accepted.
- `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS` is complete and accepted.
- `TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN` is complete and accepted as planning output only.
- `docs/task_board.md` reports no active implementation lane and calls for Planner to create or activate the next formal planning-first lane.

## 3. Required Plan First

Frontend Developer must first review and update:

```text
docs/task_341_unified_project_workbench_shell_implementation_plan.md
```

The Developer planning pass must stop for user review before frontend product code changes.

The Developer plan update must define:

- exact Workbench shell implementation slice
- existing feature components to preserve
- shell regions to implement or reshape
- lifecycle header/banner behavior for active, stopped, closed completed, and closed administrative states
- Matrix-primary workspace behavior
- supporting output rail behavior using only current features
- history/evidence surface scope, if any
- responsive and keyboard smoke expectations
- exact frontend file list
- focused tests and build validation

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
- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`
- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`

Because this is frontend/UI work, `$impeccable` product-register guidance applies: the shell must remain calm, operational, state-first, business-readable, and current-feature-only.

## 5. Scope

Allowed implementation scope after Developer plan approval:

- Project Workbench shell layout and information architecture for the first controlled slice
- lifecycle-aware Project Workbench header and state banner
- Matrix-first primary workspace ordering and display emphasis
- compact supporting output rail for current features only
- existing Workbench navigation/tabs/anchors reshaped only as approved in the TASK_341 plan
- readonly shell behavior that consumes TASK_339A lifecycle readonly model
- project registry context only as already accepted by TASK_339B, with no registry redesign
- focused frontend tests and build validation

Target behavior:

- active temporary projects show temporary planning without implying formal completion
- active registered projects without active Matrix show Matrix authority setup as the primary work
- active registered projects with active Matrix show Matrix as the primary workspace
- stopped projects remain readable, readonly, and may expose allowed Resume/Close actions where already supported
- closed completed projects are readonly archives with no Resume action
- closed administrative projects are readonly archives with no Resume action
- non-mutating read/preview controls remain available only where TASK_337B/TASK_338 classify them as safe
- UI copy uses business labels, not raw backend enum names

## 6. Non-Goals

This task must not:

- implement TASK_342 lifecycle integration QA and board closeout
- change backend lifecycle API shape
- change TASK_338 backend write guards
- change database schema or migrations
- implement Projects registry redesign beyond already accepted TASK_339B
- implement lifecycle Stop/Resume/Close backend behavior
- implement Report generation
- implement StepInstance, test execution persistence, image evidence management, or execution records
- introduce AI, permissions, LAN/server, or multi-user scope
- change Office gateway, public-drive authority, LTR workbook behavior, Matrix/Fee business rules, or Project Folder backend behavior
- expose unavailable future features as active UI
- mix external governance/orchestration dirty residuals into the TASK_341 product implementation package

## 7. May Touch

Planner/Integrator may touch:

- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/task_board.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`

Frontend Developer planning may touch:

- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`

Frontend Developer implementation may touch only after user approval of the Developer plan:

- `frontend/src/features/project-workbench/**` files explicitly listed in the approved TASK_341 plan
- `frontend/src/pages/ProjectWorkbenchPage.tsx` only if explicitly listed in the approved TASK_341 plan
- `frontend/src/workbench.css` only for Workbench shell styles explicitly listed in the approved TASK_341 plan
- `frontend/src/api/client.ts` only for consuming already-accepted DTOs, with no API contract change, and only if explicitly listed in the approved TASK_341 plan
- focused frontend tests explicitly listed in the approved TASK_341 plan
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`

## 8. Must Not Touch

- frontend product code before Developer plan approval
- backend implementation
- TASK_338 backend write guards
- database migrations or schema files
- Office gateway internals
- public-drive/LTR authority paths
- Matrix/Fee business rules
- Project Folder backend behavior
- Projects registry implementation beyond accepted TASK_339B context
- TASK_342 task, plan, evidence, QA, or closeout scope
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residual files

## 9. Locked Paths

- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
- frontend Workbench files explicitly listed in the approved TASK_341 plan

## 10. Validation Gate

Before review:

- Developer plan is approved by the user before frontend product code changes.
- Active temporary, active registered without Matrix, active registered with Matrix, stopped, closed completed, and closed administrative shell states are covered.
- Matrix remains the primary authority workspace when active Matrix exists.
- Supporting output surfaces remain compact status/entry surfaces and do not outrank Matrix.
- Stopped and closed states are readonly with visible lifecycle reasons.
- Closed states do not expose Resume.
- Readonly preview/read controls remain available only where TASK_337B/TASK_338 classify them as non-mutating.
- No raw enum words such as `cancelled`, `closed_completed`, or `closed_administrative` appear as user-facing shell copy.
- Current shell does not expose StepInstance, Report generation, AI, permissions, LAN/server, or multi-user controls.
- Narrow viewport preserves lifecycle label, readonly reason, and primary action without overlapping text.
- Keyboard focus order reaches header, banner, primary workspace, supporting outputs, and history/evidence surface in a logical order where those regions exist.
- Focused frontend tests pass.
- Frontend build passes.

## 11. Merge Gate

Reviewer, QA, and Integrator gates are required before TASK_341 can be accepted.

QA is required because this lane changes the main Workbench shell operator flow. QA must include at least a reproducible smoke checklist covering active, stopped, closed completed, and closed administrative shell states. Browser/manual smoke may be used if automated coverage cannot inspect layout and workflow behavior sufficiently.

Merge remains blocked if:

- frontend code is changed before Developer plan approval
- backend code is changed from this lane
- Workbench shell implementation expands into TASK_342 closeout
- Projects registry redesign beyond accepted TASK_339B is mixed in
- current-feature-only rule is violated
- Matrix loses primary visual priority to outputs after active Matrix exists
- readonly write blocking or preview availability contradicts TASK_337B/TASK_338/TASK_339A
- external governance/orchestration residuals are packaged as TASK_341 product work

## 12. Stop Point

This lane is complete and accepted after Reviewer, QA, and Integrator gates.

Do not implement TASK_342 or any backend/QA/Integrator closeout work from this lane. The next lifecycle/workbench series step requires a separate formal planning-first lane.
