# TASK_342 Lifecycle Integration QA And Board Closeout

Status: complete
Lane: lifecycle-integration-qa-and-board-closeout
Owner Role: Developer/QA/Integrator
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Plan first, then perform final lifecycle/workbench series closeout.

TASK_342 is not a product feature implementation lane. It exists to verify that the accepted lifecycle/workbench series is internally consistent, that required evidence and board state match, that residual QA risks are explicitly dispositioned, and that Integrator can close the series on `docs/task_board.md`.

## 2. Planner Gate

Planner Discovery Gate is recorded in:

```text
docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md
```

This lane is approved for closeout planning first because:

- `TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL` is complete and accepted.
- `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS` is complete and accepted.
- `TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN` is complete and accepted as planning output only.
- `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION` is complete and accepted after Reviewer, QA, and Integrator gates.
- Latest local commit observed by Planner: `d87345e feat(frontend): complete TASK_341 workbench shell`.
- `docs/task_board.md` reports no active implementation lane and calls for Planner creation or activation of the next formal planning-first lane.

## 3. Required Plan First

The next role is Developer acting as Closeout Coordinator. This is a documentation and validation-coordination pass, not product coding.

Closeout Coordinator must first review and update:

```text
docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md
docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md
```

The planning pass must stop for user review before QA or Integrator closeout runs.

The closeout planning pass must define:

- exact evidence files to verify
- exact board consistency checks
- final smoke commands, if any
- residual QA risk disposition, especially TASK_341 narrow viewport and real tab-order coverage
- Reviewer, QA, and Integrator handoff gates
- exact files that may be touched by each role

## 4. Required Inputs

Closeout Coordinator, Reviewer, QA, and Integrator must read:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
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
- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_qa.md`

## 5. Scope

Allowed scope:

- verify lifecycle/workbench series evidence consistency
- verify `docs/task_board.md` consistency for TASK_339A, TASK_339B, TASK_340, and TASK_341
- verify required Reviewer, QA, and Integrator gate records are present where required
- define and execute final QA smoke if approved after the planning pass
- attempt to close TASK_341 residual QA risk around narrow viewport and real tab order when tooling is available
- explicitly record any remaining residual risk and whether it is blocking or non-blocking
- prepare final board closeout for Integrator

This task may read product files or run tests for validation, but it must not modify product code.

## 6. Non-Goals

This task must not:

- implement frontend or backend product features
- rewrite the Workbench shell
- redesign Projects registry beyond accepted TASK_339B
- change backend lifecycle API shape
- change TASK_338 backend write guards
- change database schema or migrations
- implement Report generation
- implement StepInstance, test execution persistence, image evidence management, or execution records
- introduce AI, permissions, LAN/server, or multi-user scope
- change Office gateway, public-drive authority, LTR workbook behavior, Matrix/Fee business rules, or Project Folder backend behavior
- push remote
- mix unrelated external governance/orchestration residuals into product implementation packaging

## 7. May Touch

Planner may touch:

- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
- `docs/task_board.md`

Closeout Coordinator planning may touch:

- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`

Reviewer may touch:

- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`

QA may touch:

- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md` only to add a QA handoff pointer if the approved plan requires it

Integrator may touch:

- `docs/task_board.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md` only for integration decision notes

## 8. Must Not Touch

- frontend product source
- backend product source
- root `tests/` or frontend test source files
- database migrations or schema files
- Office gateway internals
- public-drive/LTR authority paths
- Matrix/Fee business rules
- Project Folder backend behavior
- Projects registry implementation
- Workbench shell implementation
- TASK_339A/TASK_339B/TASK_340/TASK_341 product package files except read-only verification
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residual files unless a separate governance lane explicitly owns them

## 9. Locked Paths

- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md` once QA creates it

## 10. Validation Gate

Before review:

- Closeout planning pass confirms all required TASK_339A/339B/340/341 task, plan, and evidence files exist.
- Closeout planning pass confirms board status matches evidence status for TASK_339A, TASK_339B, TASK_340, and TASK_341.
- Closeout planning pass defines the final smoke scope and whether browser/manual smoke is available.
- No product source files are changed.
- No TASK_342 QA or Integrator closeout is performed before the planning pass is reviewed and approved.

Before Integrator closeout:

- Reviewer gate passes for closeout plan/evidence consistency.
- QA gate passes or records a clear non-blocking residual-risk disposition.
- Any final smoke commands declared in the approved plan are run or explicitly waived with reason.
- External governance/orchestration dirty residuals are excluded from the TASK_342 product closeout package unless separately approved as governance scope.

## 11. Merge Gate

Reviewer, QA, and Integrator gates are required before TASK_342 can be accepted.

Merge remains blocked if:

- product code is modified from TASK_342
- board and evidence disagree on accepted status for TASK_339A/339B/340/341
- TASK_341 residual QA risk is ignored rather than dispositioned
- final smoke failures are unresolved
- backend guard changes, Workbench rewrite, registry redesign, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope appear
- remote push is attempted

## 12. Role Sequence And Stop Gates

1. Closeout Coordinator planning pass:
   - update TASK_342 plan/evidence only
   - confirm evidence checklist and final smoke plan
   - stop for user approval

2. Reviewer gate:
   - review TASK_342 plan/evidence/diff for scope and consistency
   - write pass/blocking findings into TASK_342 evidence
   - stop

3. QA gate:
   - run approved final smoke/checks
   - create or update QA evidence
   - explicitly disposition residual risk
   - stop

4. Integrator gate:
   - confirm Reviewer/QA gates are passed
   - update `docs/task_board.md` to close the lifecycle/workbench series
   - record final integration decision
   - do not push remote

## 13. Stop Point

This lane is complete and accepted after Reviewer, QA, and Integrator gates.

The TASK_339A-TASK_342 lifecycle/workbench series is locally closed. Do not push remote or start new feature scope from this lane.
