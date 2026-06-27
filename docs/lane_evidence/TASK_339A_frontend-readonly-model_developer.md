# Developer Evidence - TASK_339A Frontend Readonly Model

Status: approved
Task: TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL
Lane: frontend-readonly-model
Role: Frontend Developer
Last Updated: 2026-06-27

## Approval

The user approved Planner to create and activate the TASK_339A frontend-readonly-model planning lane after TASK_338 Integrator completion.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## Why This Lane Is Allowed

TASK_336 lifecycle contract is complete and accepted.

TASK_337A backend lifecycle/API shape is complete and accepted.

TASK_338 lifecycle write guard integration is complete after Reviewer and Integrator gates.

TASK_339A is now allowed as a planning-first Frontend Developer lane. Product code remains blocked until the TASK_339A plan is reviewed and explicitly approved.

## Goal

Plan and then, after explicit user approval, implement the first frontend readonly behavior layer for project lifecycle states in existing project-facing surfaces.

## May Touch

Planner/Integrator activation may touch:

- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_board.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`

Frontend Developer planning may touch:

- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`

Frontend Developer implementation may touch only files explicitly listed in the user-approved TASK_339A implementation plan.

## Must Not Touch

- frontend product code before plan approval
- backend implementation
- TASK_338 backend write guards
- Unified Workbench Shell implementation
- Projects registry redesign
- Office gateway internals
- Matrix/Fee business rules
- Project Folder backend behavior
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- public-drive authority replacement

## Locked Paths

- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- frontend files explicitly listed in the approved TASK_339A implementation plan

## Validation Gate

- Plan file exists and is user-approved before frontend code changes.
- `active` projects preserve current write behavior.
- `stopped` projects render scoped workflows readonly and prevent frontend write submissions.
- `closed_completed` and `closed_administrative` render archived readonly behavior.
- TASK_338 readonly API errors surface as business-readable guidance.
- Non-mutating preview/read actions remain available where TASK_338 classifies them safe.
- Focused frontend tests pass.
- Frontend build passes.

## Merge Gate

Reviewer and Integrator gates are required. Merge remains blocked if implementation exceeds the approved plan, changes backend code, mixes in Workbench Shell implementation or Projects registry redesign, or hides non-mutating preview/read actions without explicit TASK_338 classification.

## Commands Or Checks Run

Planner/Integrator activation:

- Loaded `$impeccable` product-register context from `PRODUCT.md` and `DESIGN.md`.
- Read latest `docs/task_board.md`.
- Read `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`.
- Read `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`.
- Confirmed TASK_338 is complete after Reviewer and Integrator gates.
- Confirmed TASK_339A task/evidence files did not already exist.
- Created TASK_339A task/evidence files.
- Updated `docs/task_board.md` so TASK_339A is the approved planning-first lane.

Frontend planning review blocker:

- Reviewer correctly found three required input files were missing from the current worktree:
  - `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
  - `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
  - `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- The plan was updated to mark this as a Required Input Blocker and explicitly forbid frontend implementation until Planner/Integrator closed the gap.

Integrator required-input closure:

- Restored only the three missing required input files from the preserved governance stash.
- Did not restore unrelated AGENTS/TASK_335/TASK_337B/TASK_338/TASK_340 residual files from the stash.
- Verified all three required input paths now exist.
- Updated `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md` from Required Input Blocker to Required Input Closure.
- Frontend implementation remains blocked until the Frontend Developer rereads the restored inputs and the plan is reviewed and explicitly approved.

## Stop Point

Required-input file gap is closed. Frontend Developer must reread the restored inputs, then the plan must be reviewed and explicitly approved before implementation.

No frontend product code may be written until that plan is explicitly approved.
