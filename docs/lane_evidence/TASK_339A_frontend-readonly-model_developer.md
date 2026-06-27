# Developer Evidence - TASK_339A Frontend Readonly Model

Status: developer fix pass complete - pending review
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

TASK_339A is allowed as the approved frontend-readonly-model lane. The user explicitly approved TASK_339A frontend implementation after the restored-input reread blocker was closed.

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

Frontend Developer restored-input reread:

- Reread `docs/project_management/PARALLEL_EXECUTION_MODEL.md`.
- Reread `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`.
- Reread `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`.
- Confirmed the TASK_339A plan remains aligned with the accepted TASK_336 lifecycle/workbench contract:
  - stopped and closed projects are readonly
  - stopped projects may expose Resume and Close actions
  - closed projects must not expose Resume
  - read and non-mutating preview surfaces remain available
  - lifecycle readonly UI remains inside existing Project Workbench surfaces and does not implement TASK_340 shell
- Updated `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md` to record restored-input reread completion.

Frontend implementation:

- Added frontend lifecycle API DTOs and action helpers in `frontend/src/api/client.ts`.
- Added shared readonly model and TASK_338 readonly error copy in `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`.
- Wired Project Workbench lifecycle readonly state into the lifecycle selector, runtime model, active Matrix workspace, and Project Folder write actions.
- Wired Basic Information to load lifecycle state, show readonly guidance, disable field edits and Confirm, suppress autosave, and map lifecycle readonly API errors.
- Wired Matrix Editor to consume runtime lifecycle state, show readonly guidance, disable import/test-record/confirm and editable matrix controls, suppress autosave, and avoid discard writes on readonly Cancel.
- Wired Fee Evaluation to load lifecycle state, show readonly guidance, disable pricing edits / Fee Form / Update Fee, suppress autosave, and avoid pricing restore writes on readonly Cancel.
- Did not modify backend runtime behavior, Office gateways, TASK_338 backend guards, TASK_340 shell, Projects registry redesign, StepInstance, Report generation, AI, permissions, LAN/server, multi-user, or public-drive authority behavior.

Developer fix pass for Reviewer blockers:

- B1 package scope: updated `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md` so the approved TASK_339A frontend touch list explicitly includes the implementation-required readonly propagation files:
  - `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - `frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx`
  - `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- B1 package boundary: did not modify governance/orchestration files during this fix pass. Current worktree may still contain unrelated dirty governance/orchestration paths from outside this Developer lane; TASK_339A review/merge packaging must exclude them.
- B2 Workbench readonly writes: changed `ProjectWorkbenchLayout` so stopped/closed readonly Workbench states do not render `TemporaryPlanningMode`, `RegisteredSetupMode`, or `ProjectLifecycleManagementPanel` write surfaces in the no-active-Matrix branch. Closed readonly no longer exposes `Stop project`.
- B3 Workbench readonly reads: changed `deriveProjectWorkbenchLifecycle(...)` so readonly states keep the underlying read/preview tabs instead of returning `tabs: []`, while the displayed next action remains read-only and has no write target.
- Added focused regressions in `projectWorkbenchLifecycleSelectors.test.ts` and `ProjectWorkbenchLayout.test.tsx` for preserved readonly tabs and closed/no-active-Matrix Stop suppression.

Validation:

- `npm test -- --run src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` -> 2 files passed, 46 tests passed.
- `npm test -- --run src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx src/features/project-workbench/useProjectWorkbenchModel.test.tsx src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx` -> 8 files passed, 129 tests passed. Existing Fee Evaluation React `act(...)` warnings still appear, with no failures.
- `npm run build` -> passed.
- `git diff --check -- <TASK_339A touched files>` -> passed; only CRLF normalization warnings.
- `git status --short -- docs/task_board.md backend backend\infrastructure\office backend\infrastructure\files tasks\TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md` -> no output.

## Stop Point

TASK_339A frontend implementation is complete and stopped for Reviewer/Integrator review.

Do not update the global task board, merge, or start TASK_340 / any later implementation lane from this Developer lane.

## Integrator Packaging / Readiness Gate

Date: 2026-06-27

Reviewer latest conclusion: `Reviewer gate: pass`.

Package accepted files:

- `docs/task_board.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

Explicitly excluded dirty governance/orchestration residuals:

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/`
- `.agents/skills/connlab-planner/`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

Integrator validation rerun:

- `npm test -- --run src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx src/features/project-workbench/useProjectWorkbenchModel.test.tsx src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx` -> passed, `8` files and `129` tests. Existing Fee Evaluation React `act(...)` warnings still appear, with no failures.
- `npm run build` -> passed.
- `git diff --check -- <TASK_339A package files>` -> passed; CRLF normalization warnings only.
- `git status --short -- backend tests tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md` -> no output.
- `git status --short -- AGENTS.md .agents docs/project_management` -> dirty external governance/orchestration residuals remain present but excluded from TASK_339A package.

Integrator decision: `Integrator gate: accepted`.

Stop point: TASK_339A is complete. Do not start TASK_339B, TASK_341, TASK_342, Workbench shell implementation, or Projects registry redesign until Planner/Integrator creates or activates a separate approved lane.
