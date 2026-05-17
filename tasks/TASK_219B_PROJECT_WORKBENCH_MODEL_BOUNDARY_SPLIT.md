# TASK_219B_PROJECT_WORKBENCH_MODEL_BOUNDARY_SPLIT

## Status

Draft task document. Pending user review and explicit approval.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None. This task must run only after `TASK_219A` is approved and completed, or after the user explicitly approves taking this model-boundary slice first.

## Why This Task Is Allowed Now

`useProjectWorkbenchModel.ts` currently coordinates multiple concerns:

- project identity loading
- LTR/resource/folder loading
- Matrix draft authority/candidate loading
- Matrix edit actions
- runtime projection request building
- output freshness calculation
- approval package manual input state
- evidence preview/place state
- folder status refresh

That model shape matches the old Workbench-as-preparation-workbench direction. It is too broad for the new Project Runtime Console direction and makes it easy for future tasks to add more low-value workflow state into Workbench.

This task is allowed as a maintainability slice after the IA direction is accepted.

## Model Fit Assessment

`GPT-5.3-codex` is suitable because this is a bounded frontend model refactor with typed React hooks and selectors. The task is sensitive to behavior preservation but does not require new backend logic.

## Objective

Split Workbench model responsibility so Runtime Console state is explicit and legacy/support action state is isolated.

Target direction:

```text
ProjectWorkbenchPage
  -> useProjectRuntimeConsoleModel
     -> project identity
     -> Matrix authority/candidate summary
     -> runtime projection snapshot
     -> output status summary
     -> selected runtime token

  -> optional support hooks
     -> folder support action
     -> evidence support action
     -> approval package support action
```

The goal is not a large rewrite. The goal is to prevent one god hook from becoming the long-term Workbench state container.

## Existing Code Context

Observed files:

- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixHelpers.ts`
- `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderResourceSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/api/client.ts`

Current issue:

- `ProjectMatrixEditorPage` also uses `useProjectWorkbenchModel`, so Matrix Editor depends on Workbench support-action state it does not need.

## Scope

Allowed:

- frontend hook extraction and selector movement
- introduce named model types for runtime console and support actions
- keep API client calls centralized in `frontend/src/api/client.ts`
- keep behavior stable
- update affected imports and tests
- create an implementation plan document before code

Forbidden:

- route changes unless needed for import wiring only
- backend/API/DB changes
- changing Matrix draft semantics
- implementing real Step Workspace persistence
- implementing output generation
- deleting existing support actions unless already done in approved TASK_219A
- broad CSS redesign

## Required First Deliverable

Before coding, create:

```text
docs/task_219b_project_workbench_model_boundary_split_plan.md
```

The plan must include:

- current hook state inventory
- proposed hook/type split
- exact files to create or edit
- compatibility strategy for `ProjectWorkbenchLayout`
- Matrix Editor dependency impact
- rollback plan
- validation commands

Stop after writing the plan and wait for explicit user approval.

## Implementation Guidance After Approval

Preferred small-step extraction:

1. Extract runtime projection request building and authority-sync calculation into selectors/helpers.
2. Extract runtime console loading and token selection into a runtime-focused hook.
3. Keep support actions in the old hook or a separate support hook until TASK_219A decides what remains visible.
4. Update `ProjectWorkbenchLayout` props so the primary runtime console does not receive approval/evidence/folder internals unless rendering support surfaces.
5. Update `ProjectMatrixEditorPage` to depend only on Matrix/runtime authority state needed by Definition Studio.

## Acceptance Criteria

- Runtime Console model can be reasoned about without approval package path-entry state.
- Matrix Editor no longer needs the full Workbench support-action model if not required by its UI.
- API access remains centralized in `frontend/src/api/client.ts`.
- No user-visible behavior changes except those already approved in TASK_219A.
- `npm run build` passes.
- Relevant frontend static tests pass or are updated with clear scope.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Recommended:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Manual smoke:

1. Open Project Workbench.
2. Open Matrix Editor from Workbench.
3. Return to Workbench.
4. Select a Matrix token in Runtime Console.
5. Confirm output status and authority sync still render.

