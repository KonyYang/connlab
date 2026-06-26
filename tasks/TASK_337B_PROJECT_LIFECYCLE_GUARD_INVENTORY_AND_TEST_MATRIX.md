# TASK_337B Project Lifecycle Guard Inventory And Test Matrix

Status: review
Lane: guard-inventory
Owner Role: Developer/Test
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Inventory ConnLab project-scoped write operations that must respect the accepted TASK_336 lifecycle contract.

This task is documentation and test planning only. It prepares downstream implementation work by classifying existing routes and services as read, readonly preview, write, lifecycle action, or out of scope.

## 2. Why This Task Exists

TASK_336 defined the product contract:

- active projects may follow current business write rules
- stopped projects are readonly except Resume and Close
- closed completed and closed administrative projects are readonly archives
- closed projects cannot Resume
- completed close v1 defaults to formal/registered projects
- temporary/no-LTR projects default to Administrative close unless a later approved task defines an exception
- readonly previews may remain available only when they do not mutate state, files, external workbooks, or public-drive resources

TASK_337B converts that contract into an implementation-facing guard inventory and test matrix before any broad write-guard implementation begins.

## 3. Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`
- read-only inspection of relevant backend API route and application service names
- existing lifecycle-related tests for coverage awareness

## 4. Outputs

- `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
- updated `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`

Planner/Integrator may update:

- `docs/task_board.md`
- this task file
- lane evidence notes required to resolve governance or packaging blockers

## 5. Scope

The inventory must cover known project-scoped operations including:

- project lifecycle actions
- Basic Information draft and confirm
- Matrix draft, revision, editor session, import, and confirm operations
- Fee draft, confirm, export, and generated file operations
- Project Folder generation, official workspace, repair, required forms, and request material collection
- Application Form and Section 2 write-back operations
- LTR registration, local commit, workbook commit, and Basic Information workbook sync
- Public Drive upload
- approval package, customer feedback, Test Record, and related output generation operations
- readonly and preview routes that must be classified by real side effects, not by HTTP verb alone

## 6. Non-Goals

This task must not:

- implement lifecycle guards
- change frontend UI
- change backend route, service, repository, or schema behavior
- change Matrix, Fee, Basic Information, LTR, Folder, Public Drive, Office, or output behavior
- modify tests as executable product test changes
- start TASK_337A, TASK_338, TASK_339A, TASK_339B, TASK_340, TASK_341, or any implementation lane
- implement StepInstance, execution persistence, Report generation, AI, permissions, LAN/server, or multi-user scope

## 7. Allowed Files

Developer/Test may touch:

- `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
- `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`

Planner/Integrator may touch for governance or packaging only:

- `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md`
- `docs/task_board.md`
- lane evidence notes under `docs/lane_evidence/`

Must not touch:

- `backend/`
- `frontend/`
- runtime configuration
- database schema/migrations
- Office gateway files
- product test files
- unrelated lane/task files except for Integrator packaging notes

## 8. Validation Gate

TASK_337B is ready for review when:

- formal task file exists
- guard inventory document exists
- every known project write route/service category has an expected active/stopped/closed behavior
- readonly previews are separated from writes and flagged for TASK_338 verification
- proposed tests identify service/API boundaries and no-mutation assertions
- evidence confirms no product behavior changed
- trailing whitespace and markdown sanity checks pass for lane-local files

## 9. Merge Gate

Merge remains blocked until:

- Reviewer accepts the guard inventory and test matrix content
- Planner/Integrator confirms the formal task file exists
- Integrator packages only TASK_337B lane files or otherwise separates unrelated governance/planning changes
- Integrator confirms no product behavior changed

## 10. Current Review State

Developer/Test produced the guard inventory and test matrix and recorded Reviewer handoff in `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`.

Reviewer blocking findings were governance/packaging issues:

- the formal TASK_337B task file was missing
- current worktree packaging includes unrelated governance/planning changes outside the guard-inventory lane scope

This task file resolves the missing formal task-file governance issue. Packaging remains an Integrator merge gate and must not be solved by product-code edits.

## 11. Stop Point

Stop after governance/packaging documentation is updated. Do not implement TASK_338 or any lifecycle guard behavior.
