# TASK_346B Workbench Folder Actions UI Refocus Plan

Status: complete/accepted after Reviewer implementation gate, QA gate, and Integrator packaging/readiness
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: workbench-folder-actions-ui-refocus
Created: 2026-06-29
Last Updated: 2026-06-29

## 1. Planning Goal

TASK_346B is the first downstream lane after the accepted `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT`.

The goal is to refocus Project Workbench Folder Actions from a readiness/status task panel into a restrained file-operation toolbar. This lane should make the Workbench surface match the accepted IA, while keeping dangerous file operations disabled or blocked until backend workflow lanes exist.

## 2. Accepted Contract Inputs

From TASK_346A:

- Folder Actions is a quiet file operation toolbar, not a readiness/status card system.
- The default UI exposes:
  - Project folder: `Open`
  - Public working copy: `Auto sync` and `Sync now`
  - Approval package: `Submit`
  - Approved folder: `Pull`
- The UI must not show persistent target paths, file counts, timestamps, Ready/Partial/Waiting/Not current statuses, preview item lists, or Source material as a separate card.
- Short inline errors are allowed only for actionable blockers or operation failures.
- Real Sync/Submit/Pull preview and execute behavior belongs to backend and functional wiring lanes.
- Submit enters approval stage after explicit confirmation/checks, but TASK_346B must not implement that transition.

## 3. Discovery Summary

### Repository-Proven Facts

- `ProjectFolderTaskList.tsx` currently renders a `Next step` flow, task step list, detail panel, path lines, Source Book/Public folder labels, and upload preview items.
- `projectFolderTaskSelectors.ts` currently derives task rows for `Request material`, `Required forms`, `Submitted Material`, and `Public drive upload`, including statuses such as `Ready to upload`, `Partial`, `Not checked`, and `Already current`.
- `ProjectWorkbenchActiveMatrixWorkspace.tsx` exposes a `Folder Action` inspector that renders one current task with a status badge and action.
- `ProjectWorkbenchLayout.tsx` routes `public_drive_refresh` and `public_drive_upload` actions to old preview/upload handlers.
- `ProjectWorkbenchLifecycleSections.tsx` hosts `ProjectFolderTaskList` in lifecycle sections and also maps public-drive action targets to old upload handlers.
- `useProjectWorkbenchModel.ts` owns old public-drive preview/upload state and handlers.
- `frontend/src/api/client.ts` has old public-drive upload helpers, but no accepted TASK_346A Sync/Submit/Pull workflow API helpers.
- Focused tests currently assert the old Folder Action and readiness/status behavior.

### Planner Inferences

- The UI slice can be useful before backend TASK_346C if it presents Sync/Submit/Pull as unavailable workflow actions with concise blockers.
- Reusing old public-drive upload helpers as `Sync now`, `Submit`, or `Pull` would misrepresent the accepted contract.
- `frontend/src/api/client.ts` should remain locked in TASK_346B. API helper changes belong to functional wiring after backend `TASK_346C`.

## 4. Implementation Design Draft

### 4.1 Folder Actions Surface

Replace the default Workbench Folder Actions presentation with a compact action cluster:

- `Project folder`
  - primary control: `Open`
  - enabled only when an existing safe local-folder action already exists in the current frontend path
  - otherwise disabled with a short blocker such as `Project folder is not available yet`
- `Public working copy`
  - toggle: `Auto sync`
  - button: `Sync now`
  - both may be disabled or show short blockers until backend workflow exists
- `Approval package`
  - button: `Submit`
  - disabled or blocked until backend submit preview/execute exists
- `Approved folder`
  - button: `Pull`
  - disabled or blocked until backend pull preview/execute exists

Do not show a separate "Source material" item. The local Project folder `Open` action covers manual addition of original materials.

### 4.2 Copy Rules

Allowed default visible labels:

- `Folder Actions`
- `Project folder`
- `Open`
- `Public working copy`
- `Auto sync`
- `Sync now`
- `Approval package`
- `Submit`
- `Approved folder`
- `Pull`

Allowed short blocker examples:

- `Project folder is not available yet.`
- `Sync workflow is not connected yet.`
- `Submit workflow is not connected yet.`
- `Pull workflow is not connected yet.`
- `Sync is locked after submit.`

Do not use default status copy such as `Ready`, `Partial`, `Waiting`, `Not current`, `Already current`, `Ready to upload`, `Refresh public-drive preview`, or `Upload to public drive` in the Folder Actions surface.

### 4.3 API Boundary

`frontend/src/api/client.ts` remains locked.

Reason:

- TASK_346B does not implement backend workflow APIs.
- Existing `fetchPublicDriveUploadPreview` and `uploadPublicDriveProjectFolder` are old upload-only helpers.
- Treating those helpers as new Sync/Submit/Pull semantics would violate TASK_346A.
- New typed API client helpers belong to `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING` after backend `TASK_346C`.

### 4.4 Current Dirty Residuals

Current workspace has pre-existing dirty frontend residuals:

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`

Planning decision:

- Both files can be legitimate future TASK_346B May Touch paths if Folder Actions placement or styling requires them.
- Their current dirty changes are outside this Planner package.
- A future Developer must inspect these residuals before editing and record whether any final changes are intentional TASK_346B changes.
- Integrator must not package unrelated residuals as TASK_346B just because the files are in May Touch.

## 5. Future Developer File Plan

Expected frontend implementation paths:

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - replace task/detail/readiness UI with four-action toolbar presentation
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - replace readiness task derivation or add a UI-only selector model for the four operation groups
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - align Active Matrix Folder Actions region with the four-action model
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - stop routing old public-drive upload actions from the new Folder Actions toolbar
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - only if Workbench lifecycle sections host the Folder Actions surface
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - only to prevent old preview/upload execution from being exposed by the new toolbar
- `frontend/src/workbench.css`
  - compact toolbar layout/states only
- focused frontend tests under `frontend/src/features/project-workbench/`

## 6. May Touch

For future implementation after Reviewer/user gates:

- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_planner.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_qa.md` if QA is routed
- `docs/task_board.md`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only when needed for Folder Actions hosting
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` only to stop exposing old upload action wiring
- focused `ProjectFolderTaskList`, `projectFolderTaskSelectors`, `ProjectWorkbenchLayout`, and Workbench model tests
- `frontend/src/workbench.css` for scoped Folder Actions styling

## 7. Must Not Touch

- `frontend/src/api/client.ts`
- `backend/`
- backend tests
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/`
- Matrix Editor business logic
- public-drive roots or local project folders
- LTR workbook files
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- `TASK_346C+` future implementation files
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 8. Locked Paths

- `frontend/src/api/client.ts`
- `backend/**`
- `tests/**` outside focused frontend tests
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`

## 9. UI Acceptance Criteria

Implementation should satisfy:

- Workbench Folder Actions default surface shows the four operation groups and no task/readiness flow.
- Default surface does not show:
  - `Ready`
  - `Partial`
  - `Waiting`
  - `Not current`
  - `Already current`
  - `Ready to upload`
  - `Refresh public-drive preview`
  - `Upload to public drive`
  - target paths
  - file counts
  - last sync/submit/pull timestamps
  - public-drive preview item lists
  - Source material as a separate action/card
- Sync, Submit, and Pull do not call old public-drive upload helpers.
- Disabled or blocked controls use concise, actionable copy.
- Existing lifecycle readonly behavior still blocks writes in states where backend write guards require activation.
- The UI remains restrained, dense, and operational, following `$impeccable` and ConnLab design rules.

## 10. Browser Smoke Expectations

QA or Developer browser smoke should cover at minimum:

- Registered Active Matrix Workbench:
  - Folder Actions shows `Open`, `Auto sync`, `Sync now`, `Submit`, and `Pull`.
  - No readiness/status card labels are visible in the default Folder Actions surface.
  - Sync/Submit/Pull are disabled or show short blockers and do not execute file operations.
- Registered no-Matrix Workbench:
  - Folder Actions remains compact and does not become a readiness panel.
  - Matrix absence does not expose file-operation execution.
- Stopped or closed project:
  - Existing lifecycle readonly/activation behavior remains intact.
  - Folder Actions does not bypass write guards.
- Narrow in-app browser width:
  - Buttons/toggle wrap or compress cleanly.
  - No overlap, thick decorative side stripes, or hidden primary labels.
- Keyboard:
  - Focus reaches enabled controls.
  - Disabled controls expose their reason by accessible label/title or adjacent short blocker.

## 11. Validation Gate

Reviewer plan gate:

- Confirms TASK_346B is scoped to frontend UI refocus only.
- Confirms `frontend/src/api/client.ts`, backend services, and file-operation behavior remain locked.
- Confirms old public-drive upload helpers are not accepted as Sync/Submit/Pull.
- Confirms existing dirty frontend residuals are documented and not automatically part of the lane package.
- Confirms tests and browser smoke expectations are adequate for future implementation.

Developer validation after implementation:

- Focused frontend tests for Folder Actions selectors/components/layout.
- `npm run build`.
- Source scan of changed Workbench files for banned default Folder Actions labels.
- Source scan proving no new API client/backend/Projects registry/Matrix/future-scope files changed.
- Browser smoke or QA handoff evidence for active registered and no-Matrix Workbench.

## 12. Merge Gate

TASK_346B implementation cannot merge until:

- Reviewer plan gate passes.
- User approves Developer implementation.
- Developer evidence records scoped frontend-only changes and validation.
- Reviewer implementation gate passes.
- QA gate runs if routed.
- Integrator confirms no backend/API/client/Projects/Matrix/future-scope/unrelated residuals are packaged.

Current stop point after reconciliation: Developer implementation pass. Do not route Reviewer until Developer evidence is updated to `ready_for_review`.

## 13. Developer Planning-First Addendum

Developer planning-first was performed after the conversational Reviewer plan gate pass and user approval for Developer planning-first. The repository board still contains pre-existing task-board residuals, so this pass remains docs-only and does not authorize product implementation.

### 13.1 Confirmed Implementation Strategy

The future implementation should treat Folder Actions as one quiet operation surface, not as a readiness workflow. The surface should present four stable entries in this order:

1. `Project folder` with `Open`
2. `Public working copy` with `Auto sync` and `Sync now`
3. `Approval package` with `Submit`
4. `Approved folder` with `Pull`

`Open` must only be enabled if the implementation discovers an existing safe local project-folder open path. Current reconnaissance did not find a clear frontend helper for opening the local project folder; old folder actions are mostly generate/update/preview/upload workflows. If no safe open path exists, `Open` should be disabled with a short blocker rather than mapped to create/update behavior.

`Auto sync`, `Sync now`, `Submit`, and `Pull` remain placeholders in TASK_346B. They must not call old public-drive upload preview or upload helpers. Their disabled copy should be short and operational, for example:

- `Sync workflow is not connected yet.`
- `Submit workflow is not connected yet.`
- `Pull workflow is not connected yet.`

### 13.2 Command And Copy Removal Rules

Future implementation should remove or hide the following from the default Folder Actions surface:

- `Next step`
- `Project Folder progress`
- `Folder Action` singular inspector status card
- readiness/status task rows and detail panels
- `Request material` / source-material card treatment
- `Source Book` and `Public folder` path rows in the default surface
- persistent path, file-count, preview-item, timestamp, and submit/pull history displays
- `Ready`, `Partial`, `Waiting`, `Not current`, `Already current`, `Ready to upload`, `Refresh public-drive preview`, and `Upload to public drive`

Underlying data and future backend wiring may remain available to later lanes, but TASK_346B should not show them as default operator guidance.

### 13.3 Refined Future File List

Developer reconnaissance confirms the original file list is mostly correct and adds one narrow selector risk:

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - replace task/detail/readiness UI with the four-entry operation surface
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - derive a UI-only four-action model or reduce old task derivation so the default surface no longer exposes readiness rows
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - align Active Matrix Folder Actions placement with the new surface
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - needed only where the Workbench shell hosts Folder Actions outside the active Matrix workspace
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - stop routing old `public_drive_refresh` / `public_drive_upload` targets from the new Folder Actions surface
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - narrow May Touch only if the old Workbench next-action banner still exposes `Refresh public-drive preview` or `Upload to public drive`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - narrow May Touch only to stop exposing old upload action wiring in the new default surface; do not change API behavior
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts` if the lifecycle selector is touched
- `frontend/src/workbench.css`
  - scoped compact operation-surface styles only

`frontend/src/api/client.ts`, backend files, Projects registry files, Matrix Editor business logic, and real file-operation behavior remain locked.

### 13.4 Dirty Residual Classification

Current dirty files observed before this Developer planning-first edit:

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`

These are pre-existing frontend residuals from prior Workbench lifecycle/button styling work, not changes made by this TASK_346B planning-first pass. They may become legitimate TASK_346B implementation files only if the later implementation edits them for Folder Actions hosting or scoped styling, and Developer evidence must explicitly distinguish pre-existing content from TASK_346B changes.

### 13.5 Focused Test Plan

Future implementation tests should cover:

- four operation entries render in the default Folder Actions surface
- `Open`, `Auto sync`, `Sync now`, `Submit`, and `Pull` labels render with stable accessible names
- Sync/Submit/Pull are disabled or blocked without invoking old public-drive upload helpers
- banned old readiness/status copy does not render in the default Folder Actions surface
- old `public_drive_refresh` and `public_drive_upload` action targets are not emitted by the new surface
- active Matrix, registered no-Matrix, stopped, and closed Workbench states preserve lifecycle behavior
- narrow width wraps the four entries without hiding labels or overlapping controls

### 13.6 Developer Planning Validation

Planning-first validation is docs-only:

- Required TASK_346B task/plan/planner-evidence files exist.
- Developer evidence is recorded at `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`.
- No frontend, backend, tests, or API client product code is changed by this planning-first pass.
- `git diff --check` and trailing whitespace scans are required for the TASK_346B plan/evidence files before callback.

Current stop point for the Developer planning-first addendum was Reviewer implementation-readiness gate. That gate has since passed by callback; see section 14.

## 14. Planner Reconciliation Addendum

Source-of-truth reconciliation was performed on 2026-06-29 after explicit user approval for Developer implementation.

Recorded fact chain:

1. TASK_346B Reviewer plan gate passed.
2. User approved Developer planning-first.
3. Developer planning-first completed and updated only TASK_346B plan/evidence.
4. Reviewer implementation-readiness content review passed; planning is concrete enough.
5. Reviewer noted implementation should wait until board/source-of-truth authorization was aligned.
6. User explicitly approved Developer implementation.

Current authorization:

- TASK_346B is implementation-authorized after user approval.
- Implementation remains pending Developer work.
- Implementation is not complete.
- Scope locks remain unchanged: Workbench Folder Actions UI refocus only; no backend/API/file operations, no public folder resolver, no Sync/Submit/Pull execute, no public-drive authority writes, no `frontend/src/api/client.ts`, no Projects list, no Matrix Editor business logic, and no future scope.

Reconciliation evidence:

- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_reconciliation_planner.md`

Current stop point: Developer implementation pass. Do not route Reviewer until Developer evidence is updated to `ready_for_review`.
