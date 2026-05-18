# TASK_219F Project Workbench Legacy Support Removal Plan

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL`

## Why This Task Is Allowed Now

The task board shows no active implementation task after `TASK_219E`. The user explicitly approved `TASK_219F` after reviewing that the Workbench still shows legacy lower-half preparation flows. This plan is the required first deliverable before implementation.

## Task Understanding

### Goal

Remove visible legacy support workflows from Project Workbench so the page behaves as a Project Runtime Console, not a project setup/preparation workbench.

### Inputs

- Existing Workbench runtime state from `useProjectWorkbenchModel`.
- Existing runtime/support selectors in:
  - `useProjectRuntimeConsoleModel.ts`
  - `useProjectWorkbenchSupportModel.ts`
- Current rendered Workbench JSX in `ProjectWorkbenchLayout.tsx`.
- Current static frontend tests in `tests/unit/test_frontend_shell_files.py`.

### Outputs

- Updated Workbench UI that no longer renders:
  - advanced support wrapper
  - project folder creation workflow
  - approval package manual path form
  - other materials/evidence placement operation panel
  - legacy evidence placement detail
  - read-only lookup panel
- Static tests that fail if these visible legacy labels return.
- Updated task board after implementation completion.

### Modules Involved

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchSupportModel.ts`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`

### Not Allowed

- Backend/API/DB changes.
- Removing backend endpoints or reusable legacy components from the repository.
- Implementing new generation, StepInstance, report, image asset, evidence persistence, AI review, permissions, or LAN behavior.
- Moving the same old workflows under different labels.

## Current Rendered Legacy Section Inventory

### Visible Legacy Wrapper

In `ProjectWorkbenchLayout.tsx`:

- `<section className="project-workbench-supporting" aria-label="Advanced support surfaces">`
- `<summary>Advanced support: folder, approval, evidence, lookup</summary>`
- `<div className="workbench-supporting-stack">`

This is the main source of the unwanted lower-half workflow block.

### Project Folder Workflow

Rendered through:

- `ProjectFolderCreationPanel`
- nested summary `Setup Manager: project folder`

User-visible workflow labels include:

- `Create project folder`
- `Preview folder`
- `Project folder template`
- `Project output root`

Decision: remove from visible Workbench. Project folder status remains only as a compact runtime support card.

### Approval Package Manual Workflow

Rendered through:

- `ApprovalPackagePanel`
- nested summary `Output Status: approval package`

User-visible workflow labels include:

- `Preview approval package`
- `Place approval package`
- `Project folder path`
- `Completed application form path`
- `Test record output path`
- `Fee evaluation output path`
- `Evidence source paths`
- `Allow overwrite when target file already exists`

Decision: remove from visible Workbench. Approval package remains a derived/output status concept, not a manual path-entry workflow.

### Other Materials Lightweight Panel

Rendered through:

- `ProjectWorkbenchMaterialDropPanel`
- nested summary `Setup Manager: other materials`

User-visible labels include:

- `Other materials`
- `Drop files here (desktop workspace)`
- `Preview placement`
- `Confirm placement`
- `Source paths (fallback)`

Decision for TASK_219F: remove from visible Workbench for now. It still calls the same evidence placement preview/place API and appears inside the same advanced block, so keeping it would preserve the old preparation-workbench behavior under a new label. A future task may reintroduce a lightweight material intake only after its backend/source-path behavior is clarified.

### Legacy Evidence Placement Detail

Rendered through:

- `ProjectWorkbenchEvidencePanel`
- nested summary `Legacy: evidence placement detail`

User-visible labels include:

- `Evidence placement`
- `Preview evidence placement`
- `Place evidence`

Decision: remove from visible Workbench.

### Read-only Lookup Panel

Rendered through:

- `ProjectLookupPanel`
- nested summary `Read-only lookup`

User-visible labels include:

- `Project evidence and testing summary`
- `Search LTR, part, product, requestor`
- `Sample summary`
- `Testing condition and method`

Decision: remove from visible Workbench. This lookup may remain as a reusable component elsewhere, but not in Project Runtime Console lower half.

## Exact JSX, Import, And Prop Removal List

### `ProjectWorkbenchLayout.tsx`

Remove imports:

- `ApprovalPackagePanel`
- `ProjectLookupPanel`
- `ProjectFolderCreationPanel`
- `ProjectWorkbenchEvidencePanel`
- `ProjectWorkbenchMaterialDropPanel`
- `ProjectWorkbenchSupportModel`

Change props:

- Remove `supportModel: ProjectWorkbenchSupportModel` from `ProjectWorkbenchLayoutProps`.
- Remove `supportModel` from function parameters.

Remove support model destructuring:

- `approvalInput`
- `approvalInputSources`
- `approvalPreview`
- `approvalResult`
- `evidencePlan`
- `evidenceResult`
- `executingApprovalPackage`
- `folderResources`
- `placingEvidence`
- `previewingApprovalPackage`
- `previewingEvidence`
- `setApprovalInput`
- `onExecuteApprovalPackage`
- `onFolderCreated`
- `onPlaceEvidence`
- `onPreviewApprovalPackage`
- `onPreviewEvidence`

Keep from runtime model:

- `folderReady`

Reason: `folderReady` is used by compact Runtime Support status cards and already belongs to `ProjectRuntimeConsoleModel`.

Update Runtime Support status cards:

- Keep `Project Folder` card with `folderReady` only.
- Keep `Approval Package` card as static/status-only if needed, but do not base it on preview/execute manual workflow state.
- Keep `Other Materials` card as static/status-only if needed, with copy such as `Managed outside Workbench`.
- Remove `Lookup Diagnostics` card if it implies a hidden advanced support surface remains available.

Remove full JSX block:

```tsx
<section className="project-workbench-supporting" aria-label="Advanced support surfaces">
  ...
</section>
```

### `ProjectWorkbenchPage.tsx`

Remove import:

- `selectProjectWorkbenchSupportModel`

Remove local const:

- `const supportModel = selectProjectWorkbenchSupportModel(model);`

Remove prop passed to layout:

- `supportModel={supportModel}`

### `useProjectWorkbenchSupportModel.ts`

Do not delete in TASK_219F unless TypeScript/build proves it is now orphaned and no other imports reference it.

Preferred decision:

- Leave the file in place for this task.
- It becomes unused by Workbench layout after removal.
- A later model cleanup task may delete or repurpose it.

Reason: TASK_219F is a UI removal task, not a hook architecture cleanup task.

### `useProjectWorkbenchModel.ts`

Do not remove backend-facing support state/functions in TASK_219F unless build requires it.

Reason: Removing these would expand scope into model cleanup and may affect Matrix Editor or output status fallback behavior.

## Other Materials Decision

`Other materials` should not remain visible in TASK_219F.

Reason:

- The current component uses `onPreviewEvidence` and `onPlaceEvidence`.
- It still depends on existing evidence placement service behavior.
- It appears as another setup manager inside the advanced support block.
- Keeping it would fail the user's explicit instruction that these old flows no longer appear.

Future direction:

- A separate task may design a truly lightweight material intake once the desktop/browser source-path behavior is resolved.
- That future task must not expose old `Preview evidence placement` or legacy evidence detail workflows.

## CSS Cleanup List

### Remove if no longer referenced by rendered Workbench

Candidates in `frontend/src/workbench.css`:

- `.project-workbench-supporting`
- `.workbench-supporting-panel`
- `.workbench-supporting-panel > summary`
- `.workbench-supporting-panel > :not(summary)`
- `.workbench-supporting-stack`
- `.workbench-supporting-nested`
- `.workbench-supporting-nested > summary`
- `.workbench-supporting-nested > :not(summary)`

### Keep for now unless confirmed orphaned

Keep these styles in TASK_219F unless a quick search proves no component uses them:

- `.project-folder-*`
- `.evidence-placement-*`
- `.approval-*`
- `.project-lookup-*`
- `.lookup-*`
- `.material-drop-*`

Reason: the reusable components remain in the repository and historical tests may still validate their standalone implementation. Removing those styles could create unintended regressions outside visible Workbench.

## Static Test Assertions

Update `tests/unit/test_frontend_shell_files.py`.

### Update TASK_219D/TASK_219E Assertions

Current tests still assert that `Legacy: evidence placement detail` exists. TASK_219F must reverse that expectation.

Expected changes:

- Remove or update assertions that require `Legacy: evidence placement detail` in `ProjectWorkbenchLayout.tsx`.
- Add a new `test_task219f_project_workbench_removes_legacy_support_surfaces`.

### New Guard Test

Read `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`.

Assert present:

- `Derived outputs` or `ProjectWorkbenchDocumentStatusPanel`
- `Runtime Support`
- `Project setup status`
- `Edit Matrix Definition`

Assert absent:

- `Advanced support: folder, approval, evidence, lookup`
- `Setup Manager: project folder`
- `Output Status: approval package`
- `Setup Manager: other materials`
- `Legacy: evidence placement detail`
- `Read-only lookup`
- `ProjectFolderCreationPanel`
- `ApprovalPackagePanel`
- `ProjectWorkbenchEvidencePanel`
- `ProjectWorkbenchMaterialDropPanel`
- `ProjectLookupPanel`
- `Preview approval package`
- `Place approval package`
- `Preview evidence placement`
- `Place evidence`
- `Project evidence and testing summary`

Read `ProjectWorkbenchPage.tsx`.

Assert absent:

- `selectProjectWorkbenchSupportModel`
- `supportModel=`

## Data Structure Design

No new backend or API data structures.

Frontend props after TASK_219F:

```ts
type ProjectWorkbenchLayoutProps = {
  runtimeModel: ProjectRuntimeConsoleModel;
  project: Project;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
};
```

`RuntimeSupportCard` remains local to `ProjectWorkbenchLayout.tsx` and receives plain display strings only.

## API Or Function Signatures

No API changes.

Expected frontend signature change only:

```ts
export function ProjectWorkbenchLayout({
  runtimeModel,
  project,
  onBack,
  onOpenMatrixEditor
}: ProjectWorkbenchLayoutProps): ReactElement
```

## Dependency Direction

Before:

```text
ProjectWorkbenchPage
  -> useProjectWorkbenchModel
  -> selectProjectRuntimeConsoleModel
  -> selectProjectWorkbenchSupportModel
  -> ProjectWorkbenchLayout(runtimeModel, supportModel)
```

After:

```text
ProjectWorkbenchPage
  -> useProjectWorkbenchModel
  -> selectProjectRuntimeConsoleModel
  -> ProjectWorkbenchLayout(runtimeModel)
```

The API client remains the only fetch boundary. UI still does not directly access Office, SQLite, or filesystem operations.

## Risk List

- `useProjectWorkbenchModel` may still carry unused support state after visible UI removal. This is acceptable in TASK_219F and should be addressed by a later cleanup task if needed.
- Existing historical static tests may expect legacy components to remain wired into Workbench. TASK_219F must update only the tests that conflict with the new approved boundary.
- Removing `Other materials` may temporarily remove the only visible route to evidence placement. This is intended because the current evidence placement UI is still the old workflow shape.
- Runtime Support card copy must not claim unavailable hidden workflows remain accessible.
- CSS cleanup must avoid deleting styles used by components that remain in the repository.

## Implementation Steps After User Approval

1. Edit `ProjectWorkbenchLayout.tsx`.
2. Remove support model prop and legacy imports.
3. Remove the advanced support JSX block.
4. Adjust Runtime Support cards to status-only copy that does not reference hidden advanced actions.
5. Edit `ProjectWorkbenchPage.tsx` to stop selecting/passing support model.
6. Remove only clearly orphaned `.project-workbench-supporting` and `.workbench-supporting-*` CSS rules.
7. Update `tests/unit/test_frontend_shell_files.py` with TASK_219F guard assertions.
8. Run frontend build and frontend static tests.
9. Update `tasks/TASK_219F_PROJECT_WORKBENCH_LEGACY_SUPPORT_REMOVAL.md` status and `docs/task_board.md` after implementation completion.

## Validation Commands

Required:

```powershell
cd frontend
npm run build
```

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Recommended after board update:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Manual Smoke Path

1. Start the frontend and backend as usual.
2. Open any Project Workbench route.
3. Confirm the Runtime Console primary area is still visible.
4. Confirm `Derived outputs` remains visible.
5. Confirm `Runtime Support` and `Project setup status` remain visible as compact status-only cards.
6. Confirm the page does not show `Advanced support`.
7. Confirm the page does not show project folder creation workflow.
8. Confirm the page does not show approval package path-entry form.
9. Confirm the page does not show legacy evidence placement or read-only lookup.
10. Click `Edit Matrix Definition` and confirm Matrix Editor route still opens.

## Review Checklist Before Coding

- Scope is frontend-only.
- No backend endpoint deletion.
- No new data entry workflow.
- No future Step execution/report/evidence persistence.
- No direct file/Office access in UI.
- No broad model cleanup beyond what build requires.

