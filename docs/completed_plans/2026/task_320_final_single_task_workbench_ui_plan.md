# TASK_320 Final Single-Task Workbench UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the remaining Project Folder status grid and disconnected panels with a single process-based task list and focused current-task detail surface.

**Architecture:** Keep all authoritative behavior in existing backend/API services. Add a frontend selector that maps existing Workbench previews into stable Project Folder task rows, then render those rows through focused Project Folder components. Existing request-material, official-folder, Section 2, fee, and public-drive APIs remain unchanged.

**Tech Stack:** React + TypeScript feature components, existing typed API DTOs in `frontend/src/api/client.ts`, Vitest, pytest static shell guards, existing `frontend/src/workbench.css`.

---

## Status

Implemented. TASK_320 scope is complete after explicit user approval.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Task file: `tasks/TASK_320_FINAL_SINGLE_TASK_WORKBENCH_UI.md`

## Required Context

Follow:

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT.md`
- `docs/task_317a_project_folder_preparation_ui_blueprint_plan.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product UI guidance

Product scene:

- Lab operators work on offline Windows workstations during daily project administration.
- The UI should be calm, dense, and operational.
- Every Workbench page should answer current state, blocker, and next action.
- File/folder operations must stay preview-first.

## Scope

TASK_320 is frontend/UI cleanup only.

Allowed:

- Create a Project Folder task-row selector.
- Create focused Project Folder task list/detail components.
- Move Request material and Public drive upload preview into task details.
- Compact the top next-action banner visually.
- Remove remaining user-facing `Package`/`Workspace` wording from Project Folder flow.
- Update tests and static guards.
- Update task board after implementation.

Forbidden:

- Backend API behavior changes.
- Database migrations.
- File copy, folder repair, upload, or Office write behavior changes.
- Implementing Test Record/Fee form/Customer Feedback generation.
- Implementing StepInstance, execution persistence, evidence/photos, report, AI, permissions, LAN, or multi-user scope.
- Renaming backend/API/internal `package` names where that would be a separate compatibility task.

## Current Implementation Summary

Current relevant files:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Derives lifecycle, project identity, and `setupMaterials`.
  - Still passes a flat `setupMaterials` list into `PackagePreparationMode`.
  - Still uses `packagePreview`/`packageStatus` as an input to user-facing Project Folder decisions.

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - Renders `PackagePreparationMode`.
  - Current Project Folder UI is a horizontal readiness grid followed by Request material panel and Public drive upload preview panel.
  - Contains stage banner, tabs, temporary planning, registered setup, and lifecycle management components.

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - Derives next action.
  - Still uses `actionTarget: "package"` and package-facing helper names internally.

- `frontend/src/workbench.css`
  - Contains Workbench layout, readiness grid, request-material panel, public-drive preview panel, and execution styles.

## Target File Structure

Create:

- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - Owns operator-facing Project Folder row model.
  - Maps existing Workbench preview DTOs into stable task rows.
  - Decides selected/current row from next action target and blocking state.

- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - Unit tests for row ordering, statuses, current row selection, and user-facing labels.

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - Renders compact row list and current row detail.
  - Keeps user-facing Project Folder wording out of `ProjectWorkbenchLayout.tsx`.

Modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Build `projectFolderTasks` via selector.
  - Pass task rows and callbacks to `PackagePreparationMode` or renamed internal component.
  - Keep route/page state minimal.

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - Replace readiness grid + separate panels with the new Project Folder task surface.
  - Keep temporary planning, registered setup, tabs, and lifecycle management stable.

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - Replace user-facing package action wording with Project Folder wording.
  - Remove `package` action target from user-facing next-action paths where possible.
  - Retain internal package-preview refresh only as a compatibility action when no better current approved action exists.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - Update tests from status-card assertions to task-row/detail assertions.

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
  - Lock one-action priority and no premature public-drive upload.

- `frontend/src/workbench.css`
  - Replace readiness grid emphasis with a compact task list + detail layout.
  - Maintain responsive behavior with no horizontal overflow at 1280px and 740px.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_320 static guards for no user-facing Package/Workspace terms in Project Folder flow and presence of the new task selector/component.

## Proposed UI Model

Add these types in `projectFolderTaskSelectors.ts`:

```ts
export type ProjectFolderTaskKey =
  | "local_project_folder"
  | "request_material"
  | "confirmed_fee_authority"
  | "required_forms"
  | "section2"
  | "submitted_material"
  | "public_drive_upload";

export type ProjectFolderTaskStatus =
  | "ready"
  | "blocked"
  | "warning"
  | "neutral";

export type ProjectFolderTaskActionTarget =
  | "folder"
  | "request_material"
  | "fee"
  | "official_folder_repair"
  | "official_folder_refresh"
  | "package_refresh"
  | "public_drive_upload"
  | "public_drive_refresh"
  | "section2"
  | null;

export type ProjectFolderTaskRow = {
  key: ProjectFolderTaskKey;
  title: string;
  statusLabel: string;
  status: ProjectFolderTaskStatus;
  summary: string;
  actionLabel?: string;
  actionTarget?: ProjectFolderTaskActionTarget;
  detailKind:
    | "folder"
    | "request_material"
    | "fee_authority"
    | "required_forms"
    | "section2"
    | "submitted_material"
    | "public_drive";
  blockers: string[];
  warnings: string[];
};
```

Selection is a separate UI concern:

```ts
export type ProjectFolderTaskSelection = {
  currentTaskKey: ProjectFolderTaskKey;
  selectedTaskKey: ProjectFolderTaskKey;
};
```

Rules:

- `currentTaskKey` is derived from readiness/blocker priority.
- `selectedTaskKey` defaults to `currentTaskKey` when the Project Folder tab first renders.
- Users can click any task row to change `selectedTaskKey`.
- Changing `selectedTaskKey` must only change the detail panel. It must not mutate lifecycle state or recompute backend readiness.

Selector input should reuse the existing data already available to `ProjectWorkbenchLayout`:

```ts
export type ProjectFolderTaskSelectorInput = {
  folderReady: boolean;
  matrixAuthorityReady: boolean;
  officialFolderCheckPreview: ProjectRuntimeConsoleModel["officialFolderCheckPreview"];
  requestMaterialPreview: ProjectRuntimeConsoleModel["requestMaterialPreview"];
  requestMaterialError: string | null;
  publicDriveUploadPreview: ProjectRuntimeConsoleModel["publicDriveUploadPreview"];
  publicDriveUploadError: string | null;
  section2SyncPreview: ProjectRuntimeConsoleModel["section2SyncPreview"];
  versionStatus: ProjectRuntimeConsoleModel["versionStatus"];
  confirmedFeeLatest: ConfirmedFeeLatestResponse | null;
  confirmedFeeAuthorityStatus: "missing" | "confirmed" | "stale" | "unknown";
};
```

The selector must not call APIs or mutate state.

Data-source rules:

- `Confirmed Fee authority` reads only Confirmed Fee authority state. If Workbench does not already load it, TASK_320 may add frontend-only loading of the existing `getConfirmedFeeLatest(projectId)` API response. It must not infer authority from generated Fee form files.
- `Required forms` reads generated output state from `versionStatus.downstream`, which is already derived from `ProjectOutputStatusSummary`. It must not infer generated form readiness from old package preview strings.
- `packagePreview` may remain loaded for compatibility with earlier code, but TASK_320 must not use it as the Project Folder row source for Confirmed Fee authority, Required forms, Customer Feedback, or Submitted Material readiness.

## Task Breakdown

### Task 1: Lock Project Folder task row model with failing tests

**Files:**

- Create: `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- Create: `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`

- [ ] **Step 1: Write the failing selector tests**

Create tests for row order and labels:

```ts
import { describe, expect, it } from "vitest";
import {
  deriveProjectFolderTasks,
  selectCurrentProjectFolderTaskKey,
} from "./projectFolderTaskSelectors";

describe("deriveProjectFolderTasks", () => {
  it("returns the fixed Project Folder task order with operator-facing labels", () => {
    const tasks = deriveProjectFolderTasks({
      folderReady: true,
      matrixAuthorityReady: true,
      packagePreview: readyPackagePreview,
      officialFolderCheckPreview: readyOfficialFolderCheckPreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      requestMaterialError: null,
      publicDriveUploadPreview: currentPublicDriveUploadPreview,
      publicDriveUploadError: null,
      section2SyncPreview: currentSection2Preview,
    });

    expect(tasks.map((task) => task.title)).toEqual([
      "Local project folder",
      "Request material",
      "Confirmed Fee authority",
      "Required forms",
      "Application Form Section 2",
      "Submitted Material",
      "Public drive upload",
    ]);
    expect(tasks.map((task) => task.title).join(" ")).not.toMatch(/Package|Workspace|manifest|SQLite/);
  });

  it("selects Request material when review is required", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput,
      requestMaterialPreview: reviewRequiredRequestMaterialPreview,
    });

    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("request_material");
  });

  it("selects Public drive upload only after Project Folder readiness is ready", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput,
      publicDriveUploadPreview: readyPublicDriveUploadPreview,
    });

    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("public_drive_upload");
  });

  it("keeps Confirmed Fee authority separate from generated Fee form output", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput,
      confirmedFeeLatest: currentConfirmedFeeLatest,
      confirmedFeeAuthorityStatus: "confirmed",
      versionStatus: versionStatusWithMissingFeeForm,
    });

    expect(taskByTitle(tasks, "Confirmed Fee authority").statusLabel).toBe("Confirmed");
    expect(taskByTitle(tasks, "Required forms").summary).toMatch(/Fee form/);
    expect(taskByTitle(tasks, "Required forms").status).not.toBe("ready");
  });
});
```

Use local fixtures inside the test file. Keep fixtures small and typed enough to satisfy TypeScript.

- [ ] **Step 2: Run the tests and confirm failure**

Run:

```powershell
cd frontend; npm test -- --run projectFolderTaskSelectors --watch=false
```

Expected:

- Fails because `projectFolderTaskSelectors.ts` does not exist or exported functions are missing.

- [ ] **Step 3: Implement minimal selector**

Create `projectFolderTaskSelectors.ts` with:

- fixed row order,
- status mapping from existing DTOs,
- no API calls,
- no React imports,
- no raw user-facing package/workspace labels.

Implementation expectations:

```ts
export function selectCurrentProjectFolderTaskKey(
  tasks: ProjectFolderTaskRow[]
): ProjectFolderTaskKey {
  return (
    tasks.find((task) => task.status === "blocked")?.key ??
    tasks.find((task) => task.status === "warning")?.key ??
    "local_project_folder"
  );
}
```

Refine the priority so request-material review-only and public-drive conflict select their own rows.

- [ ] **Step 4: Run selector tests**

Run:

```powershell
cd frontend; npm test -- --run projectFolderTaskSelectors --watch=false
```

Expected:

- New selector tests pass.

### Task 2: Replace Project Folder readiness grid with task list/detail

**Files:**

- Create: `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`

- [ ] **Step 1: Write failing layout tests**

Add tests to `ProjectWorkbenchLayout.test.tsx`:

```ts
it("shows Project Folder as a task list with one focused detail area", () => {
  renderWorkbench({
    latestLtr: "DL-2026-06-001",
    activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
    matrixAuthorityDraft: testPlanDraft,
    packagePreview: readyPackagePreview,
    requestMaterialPreview: collectedRequestMaterialPreview,
    officialFolderCheckPreview: customerFeedbackDeferredOfficialFolderCheckPreview,
    publicDriveUploadPreview: readyPublicDriveUploadPreview,
    folderReady: true,
  });

  expect(screen.getByRole("tab", { name: "Project Folder" })).toBeTruthy();
  expect(screen.getByLabelText("Project Folder tasks")).toBeTruthy();
  expect(screen.getByLabelText("Current Project Folder task")).toBeTruthy();
  expect(screen.getByText("Local project folder")).toBeTruthy();
  expect(screen.getByText("Request material")).toBeTruthy();
  expect(screen.getByText("Public drive upload")).toBeTruthy();
  expect(screen.queryByLabelText("Project Folder preparation checklist")).toBeNull();
});
```

Add a test that public-drive preview details are under the current task detail:

```ts
it("renders public-drive preview inside the Public drive upload task detail", () => {
  renderWorkbench({
    latestLtr: "DL-2026-06-001",
    activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
    matrixAuthorityDraft: testPlanDraft,
    packagePreview: readyPackagePreview,
    requestMaterialPreview: collectedRequestMaterialPreview,
    officialFolderCheckPreview: customerFeedbackDeferredOfficialFolderCheckPreview,
    publicDriveUploadPreview: readyPublicDriveUploadPreview,
    folderReady: true,
  });

  const detail = screen.getByLabelText("Current Project Folder task");
  expect(detail.textContent).toContain("Public drive upload");
  expect(detail.textContent).toContain("Submitted Material/application.docx");
});
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false
```

Expected:

- Fails because the new task list/detail labels do not exist.

- [ ] **Step 3: Create `ProjectFolderTaskList.tsx`**

The component should accept:

```ts
type ProjectFolderTaskListProps = {
  tasks: ProjectFolderTaskRow[];
  currentTaskKey: ProjectFolderTaskKey;
  selectedTaskKey: ProjectFolderTaskKey;
  onSelectTask: (taskKey: ProjectFolderTaskKey) => void;
  onTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  requestMaterialPreview: ProjectRuntimeConsoleModel["requestMaterialPreview"];
  requestMaterialError: string | null;
  requestMaterialLoading: boolean;
  publicDriveUploadPreview: ProjectRuntimeConsoleModel["publicDriveUploadPreview"];
  publicDriveUploadError: string | null;
  publicDriveUploadLoading: boolean;
};
```

Render:

- `<section aria-label="Project Folder tasks">` for rows.
- task rows as buttons or focusable controls with `aria-current` for the current task and selected styling for the selected task.
- `<section aria-label="Selected Project Folder task">` for details.
- Only one detail panel visible at a time.
- Default selected task is the current task on initial render.
- Clicking `Request material`, `Application Form Section 2`, or `Public drive upload` changes the detail panel.
- If a selected row has `actionTarget`, clicking its action calls `onTaskAction(actionTarget)`.
- If a selected row has no approved action, render a concise non-actionable state explanation instead of a disabled fake workflow button.
- Request material metrics only inside Request material detail.
- Public-drive metrics/items only inside Public drive upload detail.

- [ ] **Step 4: Compose it from `PackagePreparationMode`**

Replace the horizontal readiness grid and separate panels with:

```tsx
<ProjectFolderTaskList
  tasks={projectFolderTasks}
  currentTaskKey={currentProjectFolderTaskKey}
  selectedTaskKey={selectedProjectFolderTaskKey}
  onSelectTask={setSelectedProjectFolderTaskKey}
  onTaskAction={handleProjectFolderTaskAction}
  requestMaterialPreview={requestMaterialPreview}
  requestMaterialError={requestMaterialError}
  requestMaterialLoading={requestMaterialLoading}
  publicDriveUploadPreview={publicDriveUploadPreview}
  publicDriveUploadError={publicDriveUploadError}
  publicDriveUploadLoading={publicDriveUploadLoading}
/>
```

`PackagePreparationMode` may keep its internal name for compatibility, but no user-facing copy may say Package.

- [ ] **Step 5: Pass selector results from layout**

In `ProjectWorkbenchLayout.tsx`:

- import `deriveProjectFolderTasks` and `selectCurrentProjectFolderTaskKey`;
- build `projectFolderTasks`;
- keep a local `selectedProjectFolderTaskKey` state in the Workbench layer or the Project Folder section component;
- when `currentProjectFolderTaskKey` changes because loaded readiness changes, initialize/reset selection only if the user has not manually selected a task in the current Project Folder session;
- route `onTaskAction` to the existing Workbench action handler using the task row's `actionTarget`;
- pass tasks/current key to `PackagePreparationMode`.

- [ ] **Step 6: Cover row selection and row action in tests**

Add tests that:

- render Project Folder with Request material and Public drive rows;
- assert the default detail is the current task;
- click `Public drive upload` and assert public-drive counts/items appear while request-material details disappear;
- click `Request material` and assert request-material details appear;
- click a row/detail action and assert the existing action handler receives the row's `actionTarget`.

- [ ] **Step 7: Run layout tests**

Run:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false
```

Expected:

- ProjectWorkbenchLayout tests pass after updating old readiness-grid assertions.

### Task 3: Compact next action and remove package-facing action copy

**Files:**

- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Add selector tests for user-facing wording**

Add tests:

```ts
it("uses Project Folder wording for readiness refresh actions", () => {
  const lifecycle = deriveProjectWorkbenchLifecycle({
    ...baseInput,
    hasLtr: true,
    hasActiveMatrix: true,
    folderReady: true,
    requestMaterialStatus: "collected",
    officialFolderCheckStatus: "ready",
    packageStatus: null,
  });

  expect(lifecycle.nextAction.title).toBe("Check Project Folder readiness");
  expect(lifecycle.nextAction.reason).not.toMatch(/package/i);
});
```

Assert that active Matrix Project Folder mode labels do not include `Package`.

- [ ] **Step 2: Update selector wording**

Replace user-facing strings:

- `Refresh project folder checks` remains acceptable if it references Project Folder.
- `Resolve project folder blockers` should become `Resolve Project Folder blockers`.
- Any `package` wording in user-facing title/reason/action label should become `Project Folder`.

Keep internal `packageStatus` input if needed.

- [ ] **Step 3: Compact the banner**

In CSS, adjust `.runtime-console-stage-banner` and `.runtime-console-next-action` so:

- it reads as a compact status/action strip,
- it does not dominate the first viewport,
- it still shows one primary action clearly.

Do not remove state/reason copy entirely.

- [ ] **Step 4: Run selector and layout tests**

Run:

```powershell
cd frontend; npm test -- --run projectWorkbenchLifecycleSelectors ProjectWorkbenchLayout --watch=false
```

Expected:

- Tests pass.

### Task 4: Add static guards and browser-smoke expectations

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Add TASK_320 static guard**

Add a new test:

```python
def test_task320_project_folder_single_task_ui_boundaries_are_wired() -> None:
    feature_root = FRONTEND_ROOT / "src" / "features" / "project-workbench"
    task_selector_source = (feature_root / "projectFolderTaskSelectors.ts").read_text(
        encoding="utf-8"
    )
    task_list_source = (feature_root / "ProjectFolderTaskList.tsx").read_text(
        encoding="utf-8"
    )
    task_detail_path = feature_root / "ProjectFolderTaskDetailPanel.tsx"
    task_detail_source = (
        task_detail_path.read_text(encoding="utf-8") if task_detail_path.exists() else ""
    )
    lifecycle_source = (feature_root / "ProjectWorkbenchLifecycleSections.tsx").read_text(
        encoding="utf-8"
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required in [
        "Local project folder",
        "Request material",
        "Confirmed Fee authority",
        "Required forms",
        "Application Form Section 2",
        "Submitted Material",
        "Public drive upload",
    ]:
        assert required in task_selector_source or required in task_list_source

    user_facing_project_folder_sources = "\n".join(
        [task_selector_source, task_list_source, task_detail_source]
    )
    for forbidden_copy in [
        "Workspace",
        ".connlab",
        "manifest",
        "SQLite",
        "Project package",
        "Package preview",
    ]:
        assert forbidden_copy not in user_facing_project_folder_sources

    assert "selectedTaskKey" in task_list_source
    assert "onSelectTask" in task_list_source
    assert "onTaskAction" in task_list_source
    assert "Project Folder preparation checklist" not in lifecycle_source
    assert "ProjectPackagePreviewPanel" not in lifecycle_source
    assert ".runtime-console-project-folder-tasks" in styles_source
    assert ".runtime-console-current-folder-task" in styles_source
```

Do not globally ban internal `packageStatus` or backend-compatible API names. The guard should focus on the new Project Folder selector/list/detail user-facing copy and composition boundaries.

- [ ] **Step 2: Run static guard**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or task320"
```

Expected:

- TASK_320 guard passes.

- [ ] **Step 3: Browser smoke**

After implementation, use the in-app Browser:

1. Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f`.
2. Confirm no page-level horizontal scrollbar at 1280px width.
3. Confirm Project Folder tab has the task list and one detail surface.
4. Confirm the default selected detail matches the current recommended task.
5. Click `Request material` and confirm its detail replaces the prior detail.
6. Click `Public drive upload` and confirm target path, counts, and item details are readable and long paths wrap.
7. Click `Application Form Section 2` and confirm it reads as a controlled form update, not a generic required file.
8. Open Execution tab and confirm Matrix/Step workspace remains there.

### Task 5: Final validation and task board update

**Files:**

- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Run validation commands**

Run:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchLayout projectWorkbenchLifecycleSelectors projectFolderTaskSelectors --watch=false
cd frontend; npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or task320 or public_drive or request_material or official_folder"
py -m pytest tests\unit\test_project_request_material_collection_service.py tests\unit\test_official_project_folder_check_service.py tests\unit\test_public_drive_upload_service.py -q
git diff --check
```

Expected:

- All tests pass.
- `git diff --check` has no whitespace errors. CRLF warnings are acceptable if they match existing repository behavior.

- [ ] **Step 2: Update task board only after implementation passes**

Update `docs/task_board.md`:

- mark TASK_320 complete,
- note frontend-only UI contraction,
- list validation results,
- state that no backend/file behavior changed,
- state that next task requires separate approval.

- [ ] **Step 3: Update plan index**

Update `docs/task_plan_index.md`:

- set TASK_320 as latest completed task file/plan after completion,
- keep TASK_317A as accepted planning prerequisite historical reference.

## Review Checklist Before Approval

Confirm before implementation:

- This task does not implement generated files.
- This task does not change upload/copy/repair behavior.
- This task does not rename backend routes or database concepts.
- This task only changes operator-facing Workbench UI and tests.
- The task-row model includes all TASK_317A rows.
- Request material and public-drive details become task details, not standalone panels.
- Confirmed Fee authority and Fee form remain separate.
- Application Form Section 2 remains its own controlled row.
- Browser smoke is required because the task changes operator flow and layout density.

## Approval Gate

This plan is for review. Do not implement TASK_320 until the user explicitly approves implementation.
