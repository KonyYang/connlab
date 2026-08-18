# TASK_338 Project Lifecycle Write Guard Integration

Status: complete
Lane: write-guard-integration
Owner Role: Developer
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Implement focused lifecycle write guards after TASK_337A backend lifecycle/API shape and TASK_337B guard inventory are complete.

The goal is to make stopped and closed projects read-only for approved high-risk write paths while preserving active-project behavior and preserving explicitly non-mutating preview/read endpoints.

## 2. Required Plan First

Developer must first create:

```text
docs/task_338_project_lifecycle_write_guard_integration_plan.md
```

The plan must be reviewed and explicitly approved before product code changes.

The plan must define:

- lifecycle guard primitive or helper shape
- first-slice write paths to guard
- error code and HTTP behavior for stopped/closed writes
- readonly preview endpoint classification
- tests to add or update
- rollback and compatibility risks
- files to edit

## 3. Required Inputs

Developer must read, in order:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md`
- `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`

## 4. Scope

Allowed implementation scope after plan approval:

- a narrow backend lifecycle write guard helper or application primitive
- representative high-risk write paths from the TASK_337B inventory
- stopped/closed project write rejection with stable API errors
- active-project behavior regression protection
- tests proving guarded write paths do not mutate stopped or closed projects
- tests proving approved non-mutating preview/read endpoints remain available

Recommended first slice:

- Basic Information draft or confirm write path
- Matrix draft/session/confirm representative write path
- Fee pricing draft or confirmed fee representative write path
- Project Folder or Required Forms representative file/Office write path
- LTR/Public Drive/workbook commit representative external write path

## 5. Non-Goals

This task must not:

- change TASK_337A lifecycle API shape except for explicitly approved narrow fixes
- implement frontend readonly model
- implement Workbench shell UI
- implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- replace public-drive LTR Excel authority
- block non-mutating preview/read endpoints unless the approved plan proves they mutate state
- broaden database schema beyond an explicitly approved plan need

## 6. May Touch

Only after user approval of the TASK_338 implementation plan:

- backend guard helper/service files explicitly listed in the approved plan
- backend services/routes for the first-slice guarded write paths explicitly listed in the approved plan
- backend tests explicitly listed in the approved plan
- `docs/task_338_project_lifecycle_write_guard_integration_plan.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`

Planner/Integrator may touch:

- this task file
- `docs/task_board.md`
- TASK_338 lane evidence

## 7. Must Not Touch

- frontend UI, styling, Workbench shell, or frontend readonly model
- Projects registry UI
- unrelated backend routes/services outside the approved first slice
- Office gateway internals except explicit test fakes or explicit approved guard insertion points
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope
- unrelated board lanes or global governance outside Planner/Integrator updates

## 8. Locked Paths

- `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`
- `docs/task_338_project_lifecycle_write_guard_integration_plan.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`
- product files explicitly listed in the approved TASK_338 plan

## 9. Validation Gate

Before review:

- plan approved by user before product code changes
- guarded stopped/closed write paths return the agreed error structure
- active-project write behavior remains covered
- stopped/closed writes prove no downstream mutation
- readonly preview/read endpoints remain available only when classified as non-mutating
- focused backend tests pass

## 10. Merge Gate

Reviewer and Integrator gates are required before TASK_338 can be accepted.

Merge remains blocked if:

- any product code is changed before plan approval
- guarded paths are not traceable to TASK_337B inventory
- frontend readonly model or Workbench shell implementation is mixed into this lane
- non-mutating preview/read endpoints are blocked without explicit approval

Reviewer gate passed on 2026-06-27 with no remaining blocking findings.

Integrator completion on 2026-06-27 confirms the package is limited to TASK_338 allowed files, focused backend tests passed, non-mutating preview/read endpoints remain available, and no frontend readonly model, Workbench shell, Projects registry UI, StepInstance, Report, AI, permissions, LAN/server, multi-user, or public-drive authority replacement scope was introduced.

## 11. Stop Point

TASK_338 is complete. Stop here and wait for separate explicit approval before starting TASK_339, frontend readonly model work, Workbench implementation, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
