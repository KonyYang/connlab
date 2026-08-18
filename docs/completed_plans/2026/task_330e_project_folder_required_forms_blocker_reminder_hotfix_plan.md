# TASK_330E Project Folder Required Forms Blocker Reminder Hotfix Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task ID

`TASK_330E_PROJECT_FOLDER_REQUIRED_FORMS_BLOCKER_REMINDER_HOTFIX`

## Why This Task Is Allowed Now

`TASK_330D_PROJECT_FOLDER_UPDATE_PERFORMANCE_AND_COLLECT_DTO_HOTFIX` is complete and the task board is stopped for a separately approved next task. The user confirmed the observed behavior should have an operator reminder after actual testing showed the generation was correctly blocked by unconfirmed Basic Information, not by a generation failure.

This plan is limited to a frontend reminder/flow clarity hotfix. It does not change the backend blocker rule or output-generation semantics.

## Problem Statement

Actual API test on project `72fbbfa290294da9a507344b68ff900f` showed:

- `GET /api/projects/{project_id}/project-folder/required-forms/preview` returned `status: "blocked"`.
- Blocker: `Confirm Basic Information before generating Project Folder outputs.`
- `GET /api/projects/{project_id}/basic-information` returned `status: "unconfirmed"`.
- Missing required labels were `Project Leader` and `Lab Performing the Tests`.

The backend behavior is correct. The UX problem is that the `Update project folder` button chain can feel like the forms failed to generate, while the real next action is to confirm Basic Information. If the blocker is already known before the operator clicks, the one-click action should be unavailable rather than waiting until click-time to explain the same blocker.

## Scope

### In Scope

- Project Workbench frontend reminder behavior.
- Required forms selector copy for Basic Information blockers.
- Disabled state for the one-click Project Folder action when known blockers prevent the flow from completing.
- Automatic `Update project folder` chain handling when Required forms preview is blocked.
- Manual Required forms generate guard when preview is blocked.
- Frontend regression tests.

### Out Of Scope

- Backend Required forms rules.
- Basic Information API or persistence.
- Office template field mapping.
- Fee Form COM optimization.
- Report, StepInstance, AI, permission, LAN/server, or multi-user work.
- Broad visual redesign.

## Design

### 1. Keep Backend as Source of Truth

The frontend will continue to consume `ProjectFolderRequiredFormsPreview.blockers` and `status`. It will not infer hidden authority state or bypass generation guards.

### 2. Add a Focused Reminder Selector

In `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`, refine the blocked Required forms branch:

- If the blocked preview contains the Basic Information blocker, set summary to an operational next action such as `Confirm Basic Information before generating Required forms.`
- Preserve the original backend blocker in `blockers` so details remain traceable.
- Keep conflicts and other blockers unchanged.

This keeps copy centralized in the selector instead of scattering conditional strings through JSX.

### 3. Disable the One-Click Action When the Blocker Is Known

The active Matrix workspace top action currently derives disabled state mostly from Matrix/Fee authority and folder creation state. Extend that derived command path so a known blocked Project Folder task can make the one-click `Update project folder` action disabled.

Behavior:

- If the local project folder still needs creation or repair, keep the relevant folder action available.
- If the folder exists and the current Project Folder task is Required forms blocked by Basic Information, disable `Update project folder`.
- Show the blocker reason near the Folder Action panel and expose the same reason through the existing button disabled/title pattern.
- Do not add a modal.
- Do not add new backend state. Use existing Required forms preview blocker text and derived task state.

This avoids a misleading click target whose known result is no generation.

### 4. Make the Button Flow Non-Silent

In `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`:

- In `generateRequiredFormsAfterFolderCreate`, after fetching preview, if `preview.status === "blocked"`, set `requiredFormsError` or an equivalent visible state from the first preview blocker and return.
- Do not call `generateProjectFolderRequiredForms` unless preview is ready and has generate/update items.
- Keep current behavior for `current`, `ready`, and `conflict` except where an existing conflict branch already blocks generation.

For manual Required forms generation:

- Before building the generate request, check `requiredFormsPreview.status`.
- If blocked, show the blocker instead of allowing `buildRequiredFormsGenerateRequest` to throw the generic `Required forms preview is missing generation context.`

### 5. UI Placement

No new modal. The reminder appears in existing Project Folder surfaces:

- Active Matrix side `Folder Action` panel through `FolderTaskMessages`.
- Project Folder task list primary/detail panels through `TaskMessages`.
- Required forms detail remains able to show preview status and targets when available.
- The top one-click button is disabled with a visible reason when the blocker is already known.

This follows ConnLab's product UI rule: state before action, familiar inline feedback, no extra modal for a workflow blocker.

## File-Level Changes

Planned files:

- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - Add helper to recognize Basic Information Required forms blockers.
  - Improve summary for that blocked state.
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - Extend the derived top-button command inputs/logic to disable `Update project folder` for known Required forms Basic Information blockers while preserving create/repair availability.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - Surface blocked preview blockers during automatic update and manual generate.
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - Add blocked Basic Information reminder selector test.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` or `ProjectFolderTaskList.test.tsx`
  - Add UI-level assertion that the reminder is visible.

No backend files are planned.

## Risks

- If `requiredFormsError` is used for both API failures and business blockers, the UI may style a normal blocker as an error. Keep the selector/blocker path as the primary display and only use error state where the existing flow needs a visible message after a button click.
- Disabling the top action too broadly could prevent useful folder creation or request-material collection. The implementation must only disable the one-click update when the relevant current blocker is already known and the folder action cannot complete.
- Tests must avoid depending on this specific live project data. Use mocked preview DTOs.
- Do not add navigation from Folder Action to Basic Information unless explicitly approved; the top Workbench button already exists.

## Validation Plan

Run:

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout --watch=false
```

If TypeScript or shared component wiring changes:

```powershell
cd frontend
npm run build
```

Manual smoke:

1. Use a project with unconfirmed Basic Information and missing required fields.
2. Refresh Project Workbench.
3. Confirm the Folder Action panel shows the Basic Information blocker.
4. Confirm `Update project folder` is disabled with the blocker reason.
5. Confirm Basic Information and verify Required forms can proceed normally.

## Completion

`TASK_330E_PROJECT_FOLDER_REQUIRED_FORMS_BLOCKER_REMINDER_HOTFIX` is complete, including review follow-up.

Implemented:

- Required forms Basic Information blockers now produce the summary `Confirm Basic Information before generating Required forms.`
- The active Matrix Workbench top `Update project folder` action is disabled when Required forms are already known to be blocked by Basic Information and the project folder already exists.
- The top action scans the Required forms task for the blocker even when an earlier Project Folder task is still warning/blocked.
- The disabled button exposes the backend blocker reason in its title.
- The Folder Action panel continues to show the blocker inline.
- Automatic and manual Required forms generation paths now surface blocked preview blockers instead of silently returning or falling through to a generic missing-context error.
- The automatic one-click update flow stops after a blocked Required forms preview and downgrades the overall message instead of continuing to Section 2, application-form write-back, package preview, and public-drive preview.
- Hook-level regression coverage now asserts those downstream callbacks are not invoked after a blocked Required forms preview.

Validation:

```powershell
cd frontend
npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --watch=false
# 44 passed

npm run build
# passed
```
