# TASK_313A_PROJECT_WORKBENCH_LIFECYCLE_MODE_REDESIGN

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_313A is a controlled frontend/UI prerequisite before resuming TASK_313 package execution. TASK_313 remains valid but is deferred until the Workbench can present package execution inside the correct project lifecycle mode.

## Model Fit Assessment

GPT-5.3-codex is suitable for TASK_313A because the task is a bounded frontend information-architecture refactor using existing React state, API DTOs, selectors, and Workbench components. It requires careful product and task-boundary judgment, but it does not require backend schema work, Office automation, StepInstance persistence, evidence storage, report generation, AI review, permissions, or multi-user design.

## Goal

Redesign Project Workbench into a lifecycle-mode driven project management console so operators can understand:

- what stage the project is currently in,
- what the next required action is,
- which tools belong to the current stage,
- when package preparation is appropriate,
- when Matrix execution and Step Workspace are appropriate.

This task fixes the current Workbench confusion caused by displaying temporary planning, registered setup, package preparation, and execution surfaces all at once.

## Business Context

ConnLab started as an MVP/demo flow to prove intake, DL/LTR registration, and project folder creation. That was correct for early validation, but the product has now evolved into a project management workbench. Formal DL projects have longer lifecycles and need clearer stage ownership than the current single-screen function stack provides.

The intended operator model is:

- No DL number: temporary project planning. Use Matrix to estimate groups, steps, conditions, and fee.
- DL registered but no active Matrix authority: prepare and publish the authoritative Matrix.
- Active Matrix authority available: prepare Test Record, Confirmed Fee, Section 2 sync, Customer Feedback, and package readiness.
- Testing in progress or execution-focused review: use the Matrix execution map and Step Workspace for future step data, evidence, and lifecycle state.

TASK_313A creates the UI foundation for this model before TASK_313 adds package execution.

## Current Code Reality

- `ProjectWorkbenchPage` composes one large `ProjectWorkbenchLayout`.
- `useProjectWorkbenchModel` currently owns mixed concerns: old approval/evidence state, Matrix draft/session state, runtime projection state, Section 2 sync, project folder state, package preview, and output freshness.
- `ProjectWorkbenchLayout` currently renders preparation strips, project folder creation, Section 2 sync, package preview, Matrix table, Step Workspace, and Fee summary in one vertical page.
- `ProjectPackagePreviewPanel` currently supports preview/readiness only. TASK_313 plans to add execute.
- Matrix Editor and Fee Evaluation have independent routes and should remain separate focused work surfaces.
- Step execution persistence, evidence/image handling, report generation, AI, permissions, and multi-user behavior are not implemented and remain out of scope.

## V1 Contract

Add a frontend-only Workbench lifecycle view model and layout separation.

### Lifecycle Modes

V1 must derive one primary mode from existing frontend-available state:

```text
temporary_planning
registered_setup
package_preparation
execution_console
```

Mode intent:

- `temporary_planning`: project has no DL/LTR number. Show Matrix/Fee planning entry points. Hide formal folder/package/Section 2/package execution surfaces.
- `registered_setup`: project has DL/LTR but no active Matrix authority. Focus on editing and confirming Matrix authority. Hide package and execution as primary surfaces.
- `package_preparation`: project has active Matrix authority and package readiness is relevant. Show readiness checklist, folder, Section 2, Confirmed Fee, Customer Feedback, and package preview. Keep execution surfaces secondary or collapsed.
- `execution_console`: project has active Matrix authority and operator chooses execution view. Show Matrix execution map and right Step Workspace as the main content. Do not show package setup as the dominant visual priority.

V1 may expose `Package` and `Execution` as operator tabs once active Matrix authority exists, with `Package` defaulting when package blockers exist and `Execution` defaulting only when no package-preparation blockers require immediate attention.

### Next Action Model

Add a display-only selector that produces:

- current stage label,
- next action title,
- next action reason,
- primary action label when an approved route/action already exists,
- blocker/warning tone.

The selector must use existing API DTOs and frontend model state only. It must not invent persisted business truth.

### UI Structure

Project Workbench should render:

```text
Header / project identity
Current stage and next action banner
Lifecycle mode tabs or segmented control
Mode content
```

Mode content:

- Temporary planning: compact Matrix and Fee planning entry cards.
- Registered setup: Matrix authority setup panel and Matrix Editor entry.
- Package preparation: checklist/readiness surface, ProjectFolderCreationPanel, ProjectSection2SyncPanel, ProjectPackagePreviewPanel, and Fee summary entry.
- Execution console: ProjectWorkbenchMatrixProjectionPanel and right Step Workspace/Fee context.

### Copy Rules

Remove or avoid user-facing development/task language:

- `TASK_313`
- `placeholder`
- `read-only in this task`
- implementation route names
- future-scope button labels that look active

Future execution controls must either be hidden or clearly inactive with business-readable wording.

## In Scope

- Frontend lifecycle selector and display model.
- Workbench layout split into lifecycle sections/components.
- Stage/next-action banner.
- Mode tabs or segmented control.
- Repositioning existing Workbench panels into the correct mode.
- Copy cleanup for operator-facing Workbench text.
- Static frontend shell guards and Vitest coverage.
- Browser smoke guidance for the Workbench URL.
- Task board update after implementation.

## Out Of Scope

- No backend/API/domain/storage changes.
- No TASK_313 package execute endpoint or button.
- No deletion of TASK_313, TASK_314, or TASK_315.
- No StepInstance, TestResult, evidence/image persistence, report generation, AI review, permission, LAN, or multi-user scope.
- No Matrix/Fee autosave or draft lifecycle changes. Those remain TASK_314.
- No Matrix Draft to Fee Draft rebase. That remains TASK_315.
- No public-drive publish beyond existing approved behavior.
- No package-level or artifact-level `ProjectOutputRecord` changes.
- No generic tools page.

## Expected File Changes

Likely frontend files:

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` if useful
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx` only for copy/placement-safe adjustments
- `frontend/src/features/project-workbench/ProjectPackagePreviewPanel.tsx` only for copy/placement-safe adjustments
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts` if the layout needs a narrower mode-facing model
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Task/document files:

- `docs/task_313a_project_workbench_lifecycle_mode_redesign_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `docs/task_306_313_project_package_execution_series_plan.md`

## Acceptance Criteria

- Workbench shows a clear current stage and next action before any large work surface.
- No-DL projects show temporary planning content and do not show formal package/Section 2/Submitted Material surfaces as primary content.
- DL projects without active Matrix authority focus on Matrix setup and do not show package execute or Step Workspace as primary content.
- Active-Matrix projects separate `Package preparation` from `Execution console`.
- Active-Matrix detection uses the current active Confirmed Matrix authority, not legacy `test-plan/drafts reviewed` state.
- Package preparation mode contains folder readiness, Section 2 sync, package preview, and Confirmed Fee readiness in one coherent checklist/readiness flow.
- Execution console mode contains the Matrix table and right Step Workspace as the main work surface.
- The Workbench first screen no longer displays all lifecycle surfaces at once.
- User-facing Workbench copy does not include `TASK_313`, `placeholder`, or `read-only in this task`.
- Future-scope Step controls do not appear as active available actions.
- Existing Matrix Editor navigation remains available.
- Existing Fee Evaluation navigation remains available.
- Existing package preview behavior remains unchanged.
- No backend files are changed.
- No TASK_313 package execute behavior is implemented.

## Validation Plan

After implementation approval, run:

```powershell
cd frontend
npm test -- --run ProjectWorkbench --watch=false
npm test -- --run ProjectWorkbenchMatrixProjectionPanel ProjectPackagePreview --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "project_workbench or task313a"
git diff --name-only -- backend
git diff --check
```

Browser smoke after implementation approval:

```text
Open http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
Confirm the page shows current stage and next action.
Confirm package preparation and execution are separated.
Confirm Matrix table and Step Workspace are visible only in Execution mode.
Confirm package blockers appear in Package mode.
Confirm no package execute action appears in TASK_313A.
Confirm no future-scope active Step data/image/evidence actions appear.
```

## Follow-Up Ordering

Recommended sequence after TASK_313A:

1. Re-review TASK_314/TASK_315 priority against the new Workbench lifecycle.
2. Prefer TASK_314 and TASK_315 before TASK_313 if the product priority is long-lived Matrix/Fee editing stability.
3. Resume TASK_313 when package execution should be added inside Package Preparation mode.

TASK_313 remains valid and should not be deleted unless a later task explicitly supersedes package execution.

## Stop Point

Stop after TASK_313A implementation, validation, and task board update. Do not proceed to TASK_313, TASK_314, TASK_315, StepInstance, report generation, evidence/image handling, AI, permissions, or multi-user behavior without separate approval.

## Follow-Up Authority Correction

2026-06-11 browser smoke on project `2cd4b0e7ff6f4df99448c9ffdd78629f` found that Workbench still treated a project with active Confirmed Matrix as `registered_setup` because the lifecycle source used legacy `test-plan/drafts reviewed`.

The accepted correction keeps TASK_313A frontend-only scope and changes Workbench active authority to the active Confirmed Matrix source. Execution runtime projection must read the Confirmed-Matrix-backed projection API so Package and Execution modes represent the current Matrix authority.

## Follow-Up Lifecycle Narration Correction

2026-06-11 review on project `ce15026d119f408f80970ea7077f6e41` clarified that Workbench remains the project-management entry, but the first screen must explain the current lifecycle state before exposing large work surfaces.

The accepted correction keeps TASK_313A frontend-only scope and tightens the UI around:

- Definition Mode for DL projects without active Matrix authority: Matrix setup only, no Package or Execution surfaces.
- Active-Matrix modes: `Overview | Package | Execution`.
- Overview: lifecycle summary, controlled delivery checklist, and current blockers.
- Package: checklist-first package preparation, top `Next action`, and package detail panels below the checklist.
- Execution: Matrix execution map and Step Workspace only in Execution mode.
- Project folder template missing/inactive/invalid routes the top `Next action` to Settings instead of asking the user to attempt folder creation first.

Scope boundary still holds: no backend/API/domain/storage change, no package execute, no StepInstance/TestResult/evidence/image/report/AI/permission/multi-user work.

## Follow-Up Package Mode Cleanup

2026-06-11 Package mode review found that the lifecycle shell was in place, but Package Preparation still felt like a tool stack because Folder, Section 2, Fee, and package preview panels were all visible together.

The accepted cleanup keeps Package Preparation focused on:

- one top Next Action from the stage banner
- readiness checklist
- Package outputs preview
- secondary links for Matrix Editor and Fee Evaluation
- collapsed detail panels for Folder setup, Section 2, and Fee details

The package preview now hides future execution-scope items such as evidence placement candidates. This keeps Package Preparation focused on approved package outputs without exposing future Step/evidence execution concerns.

Scope boundary still holds: no backend/API/domain/storage change, no package execute, no StepInstance/TestResult/evidence/image/report/AI/permission/multi-user work.
