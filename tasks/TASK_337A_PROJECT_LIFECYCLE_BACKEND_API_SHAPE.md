# TASK_337A Project Lifecycle Backend API Shape

Status: complete
Lane: lifecycle-backend-api
Owner Role: Developer
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Define and then implement the backend lifecycle/API shape for Project Stop, Resume, Close as completed, and Close as administrative.

This task must run before TASK_338 write guard integration so downstream write guards can depend on stable lifecycle state, DTOs, error structure, and transition rules.

## 2. Required Plan First

Developer must first create:

```text
docs/task_337a_project_lifecycle_backend_api_shape_plan.md
```

The plan must be reviewed and explicitly approved before product code changes.

The plan must define:

- how lifecycle state is represented
- whether and how current `cancelled` compatibility remains
- API DTOs and response shapes
- Stop endpoint behavior
- Resume endpoint behavior
- Close completed endpoint behavior
- Close administrative endpoint behavior
- completed/admin close rules
- temporary/no-LTR project boundaries
- reason/note requiredness
- error structure for lifecycle actions
- tests to add or update
- write guard work explicitly deferred to TASK_338

## 3. Required Inputs

Developer must read, in order:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md`
- `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`

## 4. Scope

Allowed implementation scope after plan approval:

- backend lifecycle state/API shape
- Stop/Resume/Close application service behavior
- typed request/response DTOs
- lifecycle action routes
- lifecycle action tests
- compatibility handling for existing `cancelled` semantics

## 5. Non-Goals

This task must not:

- implement broad write guard integration from TASK_338
- guard Matrix/Fee/Basic Information/Folder/LTR/Public Drive write paths beyond lifecycle actions
- implement frontend readonly model
- implement Workbench shell UI
- implement Projects registry lifecycle views
- implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- change Office gateway behavior
- replace public-drive LTR Excel authority

## 6. May Touch

Only after user approval of the TASK_337A implementation plan:

- backend domain/application/API files explicitly listed in the approved plan
- lifecycle-related repositories or storage files explicitly listed in the approved plan
- backend tests explicitly listed in the approved plan
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`

Planner may touch:

- this task file
- `docs/task_board.md`
- TASK_337A lane evidence

## 7. Must Not Touch

- frontend UI
- Workbench shell implementation
- Projects registry implementation
- broad write guard integration from TASK_338
- Matrix/Fee/LTR/Folder/Basic Information/Public Drive behavior outside lifecycle action shape
- Office gateway internals
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope
- unrelated backend routes/services outside the approved plan

## 8. Locked Paths

- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`
- product files explicitly listed in the approved TASK_337A plan

## 9. Validation Gate

Before review:

- plan approved by user before product code changes
- lifecycle transition tests pass
- reason/note requiredness tests pass
- temporary/no-LTR completed-close boundary is covered
- closed cannot resume
- stopped can resume or close
- compatibility behavior for existing `cancelled` is explicit
- TASK_338 write guard scope remains untouched

## 10. Merge Gate

Reviewer must confirm the backend lifecycle/API shape matches TASK_336.

Integrator must confirm TASK_337A is complete before TASK_338 is unblocked.

Reviewer gate passed on 2026-06-27 with no remaining blocking findings.

Integrator completion on 2026-06-27 confirms the package is limited to TASK_337A allowed files, TASK_338 write guard integration remains deferred, and no frontend, Workbench shell, Office gateway, Matrix/Fee/LTR/Folder/Basic Information/Public Drive, Report, StepInstance, AI, permissions, LAN/server, or multi-user scope was introduced.

## 11. Stop Point

TASK_337A is complete. Do not start TASK_338 until the task board explicitly unblocks and approves the next lane step.
