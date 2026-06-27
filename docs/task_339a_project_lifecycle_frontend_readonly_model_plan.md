# TASK_339A Project Lifecycle Frontend Readonly Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first frontend readonly behavior layer for TASK_337A Project lifecycle states and TASK_338 guarded write errors in existing project-facing surfaces.

**Architecture:** Consume the backend lifecycle overlay as typed frontend data, then centralize readonly decisions in a small lifecycle model helper before wiring existing screens. Keep pages as route composers and put business decisions in feature selectors/hooks. Do not implement the TASK_340 Unified Workbench Shell, Projects registry redesign, or backend changes.

**Tech Stack:** React, TypeScript, Vite, Vitest, Testing Library, FastAPI client DTOs in `frontend/src/api/client.ts`.

## Global Constraints

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current approved lane: `frontend-readonly-model` / `TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL`.
- Current role: Frontend Developer planning first.
- This document is planning only; frontend product code changes require explicit user approval of this plan.
- May create only `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md` during this planning turn.
- Do not change backend implementation, TASK_338 backend guards, Office gateway internals, Matrix/Fee business rules, Project Folder backend behavior, or public-drive authority semantics.
- Do not implement TASK_340 Unified Project Workbench Shell or redesign Projects registry lifecycle views.
- Do not implement StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope.
- Non-mutating preview/read actions classified safe by TASK_338 must remain available.
- Use `$impeccable` product-register guidance: calm, operational, state-first, business-readable UI copy; no decorative UI, no future-scope feature exposure.

---

## 1. Current Task Understanding

### Objective

Plan the frontend-only implementation for lifecycle readonly behavior after TASK_337A and TASK_338 are complete.

### Inputs

- TASK_337A lifecycle API:
  - `GET /api/projects/{project_id}/lifecycle`
  - `POST /api/projects/{project_id}/lifecycle/stop`
  - `POST /api/projects/{project_id}/lifecycle/resume`
  - `POST /api/projects/{project_id}/lifecycle/close-completed`
  - `POST /api/projects/{project_id}/lifecycle/close-administrative`
- TASK_337A lifecycle response fields:
  - `lifecycle_state: active | stopped | closed`
  - `closure_type: null | completed | administrative`
  - `readonly: boolean`
  - `allowed_actions: string[]`
  - `status_label`, `status`, timestamps, reasons, warnings, completion summary
- TASK_338 guarded write error:

```json
{
  "code": "project_lifecycle_readonly",
  "project_id": "P1",
  "lifecycle_state": "stopped",
  "closure_type": null,
  "message": "This project is stopped. Resume it before making changes.",
  "allowed_actions": ["resume", "close"]
}
```

### Outputs

- Typed frontend lifecycle DTOs and client functions.
- Shared frontend lifecycle readonly helper/selector/hook.
- Existing project-facing screens disable or suppress scoped write submissions for stopped and closed projects.
- TASK_338 readonly API errors render as business-readable guidance.
- Readonly preview/read actions remain available.
- Focused frontend tests and build validation.

### Required Input Closure

Integrator restored the missing required input files on 2026-06-27:

- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`

The required-input file gap is closed, but this plan still requires review after the Frontend Developer rereads those restored inputs. If the accepted contract changes any frontend readonly rule, this plan must be updated before implementation approval.

Frontend implementation remains blocked until this plan is reviewed and explicitly approved after the restored-input reread.

### Existing Frontend Reality

- `frontend/src/api/client.ts` has legacy `stopProject(...)` but does not yet expose TASK_337A lifecycle overlay client functions.
- `ProjectWorkbenchLayout` currently derives stopped behavior from `project.status === "cancelled"`.
- `ProjectBasicInformationWorkspace` autosaves draft changes and confirms without lifecycle readonly awareness.
- `MatrixEditorWorkspace`, Fee Evaluation, Required Forms, and LTR workbook actions have existing write paths that can hit TASK_338 backend guards.
- Existing feature folders should be preserved. This task should add lifecycle selectors/hooks rather than moving large UI surfaces.

## 2. Design Decisions

### 2.1 Lifecycle Data Source

Add typed DTOs and client functions in `frontend/src/api/client.ts`.

```ts
export type ProjectLifecycleState = "active" | "stopped" | "closed";
export type ProjectClosureType = "completed" | "administrative";

export type ProjectLifecycleResponse = {
  project_id: string;
  lifecycle_state: ProjectLifecycleState;
  closure_type: ProjectClosureType | null;
  status_label: string;
  readonly: boolean;
  allowed_actions: string[];
  status: string;
  stopped_at?: string | null;
  stopped_reason?: string | null;
  closed_at?: string | null;
  closed_reason?: string | null;
  completion_summary?: Record<string, unknown> | null;
  warnings: string[];
};

export type ProjectLifecycleActionRequest = {
  reason?: string | null;
  operator?: string | null;
};

export type ProjectLifecycleCloseCompletedRequest = {
  close_note: string;
  operator?: string | null;
  manual_completion_confirmed: boolean;
  output_summary_acknowledged: boolean;
};

export type ProjectLifecycleCloseAdministrativeRequest = {
  reason: string;
  operator?: string | null;
};
```

Client functions:

```ts
export function getProjectLifecycle(projectId: string): Promise<ProjectLifecycleResponse>;
export function stopProjectLifecycle(
  projectId: string,
  input: ProjectLifecycleActionRequest
): Promise<ProjectLifecycleResponse>;
export function resumeProjectLifecycle(
  projectId: string,
  input: ProjectLifecycleActionRequest
): Promise<ProjectLifecycleResponse>;
export function closeProjectCompletedLifecycle(
  projectId: string,
  input: ProjectLifecycleCloseCompletedRequest
): Promise<ProjectLifecycleResponse>;
export function closeProjectAdministrativeLifecycle(
  projectId: string,
  input: ProjectLifecycleCloseAdministrativeRequest
): Promise<ProjectLifecycleResponse>;
```

Keep the existing legacy `stopProject(...)` client during this task for compatibility, but route new frontend lifecycle controls through the TASK_337A lifecycle API.

### 2.2 Readonly Error Type

Add frontend parsing for TASK_338 readonly details in `frontend/src/api/client.ts`.

```ts
export type ProjectLifecycleReadonlyErrorDetail = {
  code: "project_lifecycle_readonly";
  project_id: string;
  lifecycle_state: ProjectLifecycleState;
  closure_type: ProjectClosureType | null;
  message: string;
  allowed_actions: string[];
};

export function isProjectLifecycleReadonlyErrorDetail(
  detail: unknown
): detail is ProjectLifecycleReadonlyErrorDetail;
```

Do not change the generic `ApiRequestError` contract. Use `ApiRequestError.detail` plus the helper above in feature hooks.

### 2.3 Shared Frontend Readonly Model

Create `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`.

```ts
import type {
  ProjectLifecycleReadonlyErrorDetail,
  ProjectLifecycleResponse,
} from "../../api/client";

export type ProjectLifecycleReadonlyMode =
  | "active"
  | "stopped_readonly"
  | "closed_completed_readonly"
  | "closed_administrative_readonly"
  | "closed_readonly";

export type ProjectLifecycleReadonlyView = {
  mode: ProjectLifecycleReadonlyMode;
  readonly: boolean;
  title: string;
  message: string;
  allowedActions: string[];
  canResume: boolean;
  canClose: boolean;
  canWriteBusinessData: boolean;
  canUseReadonlyPreview: boolean;
};

export function deriveProjectLifecycleReadonlyView(
  lifecycle: ProjectLifecycleResponse | null
): ProjectLifecycleReadonlyView;

export function deriveReadonlyApiErrorMessage(
  detail: ProjectLifecycleReadonlyErrorDetail
): string;
```

Readonly mode rules:

| Backend state | Frontend mode | Business write controls | Read/preview controls |
|---|---|---|---|
| `active` | `active` | enabled by existing business rules | enabled by existing business rules |
| `stopped` | `stopped_readonly` | disabled | available if non-mutating |
| `closed` + `completed` | `closed_completed_readonly` | disabled | available if non-mutating |
| `closed` + `administrative` | `closed_administrative_readonly` | disabled | available if non-mutating |
| `closed` + null | `closed_readonly` | disabled | available if non-mutating |

### 2.4 UX Copy

Business-readable copy:

```ts
const READONLY_COPY = {
  stopped: {
    title: "Project stopped",
    message: "This project is paused. Review and preview actions remain available; editing resumes after the project is resumed.",
  },
  closedCompleted: {
    title: "Project closed as completed",
    message: "This project is archived as completed. Project data is read-only.",
  },
  closedAdministrative: {
    title: "Project closed administratively",
    message: "This project is archived administratively. Project data is read-only.",
  },
  closed: {
    title: "Project closed",
    message: "This project is archived. Project data is read-only.",
  },
};
```

Do not expose raw enum names such as `closed_completed` in UI labels.

### 2.5 Surfaces Covered In First Slice

Plan implementation covers existing surfaces corresponding to TASK_338 guarded paths:

- Project Workbench action shell:
  - replace legacy stopped detection with lifecycle readonly view
  - keep lifecycle management controls focused on existing Workbench, without TASK_340 shell changes
  - disable or block Matrix Editor, Fee Evaluation, Basic Information, Required Forms generate, folder create, request material collect, repair, public-drive upload when lifecycle readonly
  - keep readonly refresh/preview actions available
- Basic Information:
  - load lifecycle alongside Basic Information
  - stop autosave scheduling when readonly
  - render fields read-only or disabled
  - disable Confirm with visible readonly reason
- Matrix Editor:
  - load lifecycle before write controls
  - disable editable cells, group inclusion, import commit, autosave, discard, confirm, and draft-generation write actions when readonly
  - keep session load and display available
- Fee Evaluation:
  - load lifecycle in page context
  - disable pricing draft edits/autosave/discard, confirm fee version, and file generation writes when readonly
  - keep current draft/fee preview display available
- Project Folder Required Forms / LTR sync actions that appear through Workbench runtime model:
  - disable generate/commit/upload style writes in readonly mode
  - keep refresh, preview, and read-only open available

If an action is unclear, treat it as write-blocked only when it calls a TASK_338 guarded endpoint or an existing project folder/public-drive mutation. Do not hide or block pure read/preview actions broadly.

### 2.6 Error Handling Strategy

Feature hooks must catch `ApiRequestError` and inspect `detail` with `isProjectLifecycleReadonlyErrorDetail(...)`.

```ts
if (error instanceof ApiRequestError && isProjectLifecycleReadonlyErrorDetail(error.detail)) {
  setError(deriveReadonlyApiErrorMessage(error.detail));
  setLifecycleReadonlyDetail(error.detail);
  return;
}
```

Business-readable fallback messages:

- Stopped: `This project is stopped. Resume it before making changes.`
- Closed completed: `This project is closed as completed and is read-only.`
- Closed administrative: `This project is closed administratively and is read-only.`

Do not render raw backend JSON.

## 3. File Structure

### Create After Plan Approval

- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
  - Shared lifecycle readonly selectors, copy, and error-message mapping.

- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts`
  - Pure tests for active/stopped/closed modes and API error details.

### Modify After Plan Approval

- `frontend/src/api/client.ts`
  - Add lifecycle DTOs, action clients, and readonly-error type guard.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Load/use lifecycle readonly state passed from model.
  - Replace legacy `project.status === "cancelled"` readonly checks in Workbench rendering.
  - Disable write action handlers when readonly.

- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - Fetch `getProjectLifecycle(projectId)` with runtime model data.
  - Expose lifecycle response, loading, error, and refresh helper.
  - Normalize TASK_338 readonly errors from required forms, folder, public-drive, and related write actions.

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - Accept lifecycle readonly input and derive stopped/closed readonly modes from TASK_337A lifecycle fields.

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
  - Add stopped, closed completed, and closed administrative selector tests.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - Assert write actions disabled for readonly lifecycle states and read/preview actions remain available.

- `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
  - Fetch lifecycle with Basic Information.
  - Prevent autosave/confirm when readonly.
  - Map TASK_338 readonly errors to UI copy.

- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
  - Render readonly banner.
  - Pass read-only state to field renderers.
  - Disable Confirm with visible reason.

- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
  - Assert readonly fields, no autosave write, disabled confirm, and active behavior preservation.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Fetch lifecycle and derive readonly state.
  - Disable editing, autosave, import commit, discard, confirm, and generated write actions.
  - Keep Matrix session display available.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Assert stopped/closed readonly disables write controls and active mode remains editable.

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
  - Fetch lifecycle in page context.
  - Disable pricing draft edits/autosave/discard, confirm, and file generation writes when readonly.
  - Preserve read-only preview.

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
  - Assert readonly disables write actions and maps TASK_338 readonly error.

- `frontend/src/workbench.css`
  - Add minimal readonly banner/disabled reason classes if existing alert classes are insufficient.
  - No broad visual redesign.

### Do Not Modify

- Backend files.
- Office gateway files.
- TASK_338 backend guard implementation.
- Projects registry page redesign.
- TASK_340 Workbench shell plan or implementation files.

## 4. Implementation Tasks

### Task 1: API Lifecycle DTOs And Readonly Error Helper

**Files:**

- Modify: `frontend/src/api/client.ts`
- Test: `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts`

**Interfaces:**

- Produces lifecycle DTOs and client functions from section 2.1.
- Produces `isProjectLifecycleReadonlyErrorDetail(...)`.

- [ ] Add lifecycle DTO types to `frontend/src/api/client.ts`.
- [ ] Add `ProjectLifecycleReadonlyErrorDetail` and `isProjectLifecycleReadonlyErrorDetail(...)`.
- [ ] Add `getProjectLifecycle`, `stopProjectLifecycle`, `resumeProjectLifecycle`, `closeProjectCompletedLifecycle`, and `closeProjectAdministrativeLifecycle`.
- [ ] Run:

```powershell
cd frontend
npm test -- --run src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts
```

Expected during this task: type-level tests compile after Task 2 creates the test file.

### Task 2: Shared Readonly Model

**Files:**

- Create: `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
- Create: `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts`

**Interfaces:**

- Consumes `ProjectLifecycleResponse` and `ProjectLifecycleReadonlyErrorDetail`.
- Produces `deriveProjectLifecycleReadonlyView(...)` and `deriveReadonlyApiErrorMessage(...)`.

- [ ] Write tests:

```ts
import { describe, expect, it } from "vitest";
import {
  deriveProjectLifecycleReadonlyView,
  deriveReadonlyApiErrorMessage,
} from "./projectLifecycleReadonlyModel";

describe("project lifecycle readonly model", () => {
  it("keeps active projects writable", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "active",
      closure_type: null,
      status_label: "Active",
      readonly: false,
      allowed_actions: [],
      status: "ltr_registered",
      warnings: [],
    });

    expect(view.mode).toBe("active");
    expect(view.canWriteBusinessData).toBe(true);
  });

  it("marks stopped projects readonly with resume guidance", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "stopped",
      closure_type: null,
      status_label: "Stopped",
      readonly: true,
      allowed_actions: ["resume", "close"],
      status: "cancelled",
      warnings: [],
    });

    expect(view.mode).toBe("stopped_readonly");
    expect(view.canResume).toBe(true);
    expect(view.canWriteBusinessData).toBe(false);
    expect(view.message).toContain("paused");
  });

  it("marks completed close as archived readonly", () => {
    const view = deriveProjectLifecycleReadonlyView({
      project_id: "P1",
      lifecycle_state: "closed",
      closure_type: "completed",
      status_label: "Closed",
      readonly: true,
      allowed_actions: [],
      status: "closed",
      warnings: [],
    });

    expect(view.mode).toBe("closed_completed_readonly");
    expect(view.canResume).toBe(false);
    expect(view.title).toBe("Project closed as completed");
  });

  it("maps TASK_338 readonly detail to business copy", () => {
    expect(
      deriveReadonlyApiErrorMessage({
        code: "project_lifecycle_readonly",
        project_id: "P1",
        lifecycle_state: "closed",
        closure_type: "administrative",
        message: "This project is closed administratively and is readonly.",
        allowed_actions: [],
      })
    ).toBe("This project is closed administratively and is read-only.");
  });
});
```

- [ ] Implement readonly model and copy exactly enough for tests.
- [ ] Run:

```powershell
cd frontend
npm test -- --run src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts
```

Expected: tests pass.

### Task 3: Project Workbench Lifecycle Consumption

**Files:**

- Modify: `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- Modify: `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- Modify: `frontend/src/workbench.css` only if existing alert classes cannot express readonly banner/disabled reason.

**Interfaces:**

- Consumes `getProjectLifecycle(projectId)`.
- Produces lifecycle readonly view in runtime model.

- [ ] Extend `ProjectRuntimeConsoleModel` with:

```ts
lifecycle: ProjectLifecycleResponse | null;
lifecycleLoading: boolean;
lifecycleError: string | null;
refreshLifecycle: () => Promise<void>;
```

- [ ] Update `deriveProjectWorkbenchLifecycle(...)` input:

```ts
lifecycleReadonlyView: ProjectLifecycleReadonlyView;
```

- [ ] Replace `isCancelled: project.status === "cancelled"` with lifecycle overlay state.
- [ ] Disable Workbench write action handlers when `readonlyView.canWriteBusinessData === false`.
- [ ] Keep these read/preview actions available:
  - refresh package preview
  - refresh required forms preview
  - refresh official folder check
  - refresh public-drive preview
  - Matrix/session display navigation when it is read-only safe
- [ ] Add tests:
  - stopped project shows `Project stopped` and disables folder/create/generate/upload style actions
  - closed completed project shows archive copy and no Resume action
  - active project still exposes current write actions under existing business rules
- [ ] Run:

```powershell
cd frontend
npm test -- --run src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
```

Expected: tests pass.

### Task 4: Basic Information Readonly Behavior

**Files:**

- Modify: `frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts`
- Modify: `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- Modify: `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`

**Interfaces:**

- Consumes `getProjectLifecycle(projectId)`.
- Consumes readonly model from Task 2.

- [ ] Load lifecycle with existing Basic Information data.
- [ ] Add to model:

```ts
readonlyView: ProjectLifecycleReadonlyView;
readonlyReason: string | null;
```

- [ ] In `updateValue`, return without changing state when readonly.
- [ ] In autosave effect, skip scheduling and cancel pending timer when readonly.
- [ ] In `confirm`, return with readonly guidance when readonly.
- [ ] Pass read-only state into field renderers:
  - textareas use `readOnly`
  - inputs use `readOnly`
  - selects and radios use `disabled`
- [ ] Add readonly banner above the field grid.
- [ ] Add tests:
  - stopped lifecycle renders fields read-only and does not call draft save on edit
  - closed completed lifecycle disables Confirm with archived copy
  - active lifecycle preserves current editable behavior
  - TASK_338 readonly API detail maps to business-readable alert
- [ ] Run:

```powershell
cd frontend
npm test -- --run src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx
```

Expected: tests pass.

### Task 5: Matrix Editor Readonly Behavior

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

**Interfaces:**

- Consumes `getProjectLifecycle(projectId)`.
- Uses readonly model from Task 2.

- [ ] Load lifecycle during Matrix Editor initialization.
- [ ] Derive a local `isReadonly` from lifecycle readonly view.
- [ ] Disable or make read-only:
  - editable grid cells
  - group include checkboxes
  - group/sample text inputs
  - source import commit buttons
  - autosave, discard, and confirm actions
  - Matrix editor test-record draft generation actions if present
- [ ] Keep session load, Matrix display, filters, row selection, group selection, and step preview available.
- [ ] Add a compact readonly banner near the editor header.
- [ ] Add tests:
  - stopped lifecycle disables editable controls and confirm
  - closed administrative lifecycle disables import commit/write actions
  - active lifecycle remains editable
- [ ] Run:

```powershell
cd frontend
npm test -- --run src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
```

Expected: tests pass.

### Task 6: Fee Evaluation Readonly Behavior

**Files:**

- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- Modify: `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

**Interfaces:**

- Consumes `getProjectLifecycle(projectId)`.
- Uses readonly model from Task 2.

- [ ] Load lifecycle in `FeeEvaluationReviewExportPage` context.
- [ ] Disable pricing draft edits and autosave when readonly.
- [ ] Disable discard pricing draft, confirm fee version, and generated file write actions when readonly.
- [ ] Keep fee draft loading and preview table display available.
- [ ] Catch TASK_338 readonly errors from save/discard/confirm/generate calls and show business-readable copy.
- [ ] Add tests:
  - stopped lifecycle disables pricing edit and save path
  - closed completed lifecycle disables confirm/export write actions
  - active lifecycle preserves current editing and save behavior
- [ ] Run:

```powershell
cd frontend
npm test -- --run src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

Expected: tests pass.

### Task 7: Final Frontend Validation And Evidence

**Files:**

- Modify after implementation approval only: `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`

- [ ] Run focused frontend tests:

```powershell
cd frontend
npm test -- --run src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.test.tsx src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx
```

- [ ] Run frontend build:

```powershell
cd frontend
npm run build
```

- [ ] Run whitespace check:

```powershell
git diff --check -- frontend/src/api/client.ts frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-basic-information/useProjectBasicInformationModel.ts frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md
```

- [ ] Confirm forbidden surfaces unchanged:

```powershell
git status --short -- backend backend/infrastructure/office backend/infrastructure/files
```

Expected:

- No backend files changed by Frontend Developer implementation.
- No Office gateway or file infrastructure changes.
- TASK_340 Workbench shell implementation remains untouched.

## 5. Risks And Mitigations

### Risk: Frontend guesses lifecycle from legacy `status`

Mitigation:

- Add typed lifecycle client and use TASK_337A `lifecycle_state` / `closure_type`.
- Keep legacy `status === "cancelled"` only as temporary fallback if lifecycle fetch fails, and surface a warning in developer evidence if fallback is used.

### Risk: Autosave writes still fire after readonly state loads

Mitigation:

- Basic Information, Matrix Editor, and Fee Evaluation hooks must cancel pending autosave timers when readonly becomes true.
- Tests assert write client mocks are not called for readonly states.

### Risk: Read/preview actions are hidden too broadly

Mitigation:

- Readonly model separates `canWriteBusinessData` from `canUseReadonlyPreview`.
- Tests assert preview/refresh/display controls remain available.

### Risk: TASK_339A becomes Workbench Shell implementation

Mitigation:

- Do not add new navigation, IA, route shells, or TASK_340 layout.
- Keep changes within existing pages/features and small shared lifecycle model.

### Risk: API readonly errors appear as raw backend text

Mitigation:

- Use `isProjectLifecycleReadonlyErrorDetail(...)` and `deriveReadonlyApiErrorMessage(...)`.
- Feature hooks show stable business copy.

## 6. Acceptance Criteria

TASK_339A implementation is ready for review when:

- Frontend consumes TASK_337A lifecycle API with typed DTOs.
- Existing project-facing surfaces use shared readonly model instead of legacy `cancelled` status as primary lifecycle authority.
- Active projects preserve current write behavior.
- Stopped projects show paused readonly guidance and block scoped write submissions.
- Closed completed and closed administrative projects show archived readonly guidance and block scoped write submissions.
- Resume is not presented for closed states.
- TASK_338 `project_lifecycle_readonly` API errors surface as business-readable guidance.
- Non-mutating preview/read actions remain available where TASK_338 classifies them safe.
- Focused frontend tests pass.
- `npm run build` passes.
- No backend, Office gateway, Project Folder backend behavior, TASK_338 guard, TASK_340 shell, Projects registry redesign, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope is introduced.

## 7. Plan-Only Validation

Before implementation approval, validate only this plan file:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path docs\task_339a_project_lifecycle_frontend_readonly_model_plan.md
Select-String -Path docs\task_339a_project_lifecycle_frontend_readonly_model_plan.md -Pattern 'ProjectLifecycleResponse' -Encoding UTF8
Select-String -Path docs\task_339a_project_lifecycle_frontend_readonly_model_plan.md -Pattern 'project_lifecycle_readonly' -Encoding UTF8
Select-String -Path docs\task_339a_project_lifecycle_frontend_readonly_model_plan.md -Pattern 'Basic Information' -Encoding UTF8
Select-String -Path docs\task_339a_project_lifecycle_frontend_readonly_model_plan.md -Pattern 'Matrix Editor' -Encoding UTF8
Select-String -Path docs\task_339a_project_lifecycle_frontend_readonly_model_plan.md -Pattern 'Fee Evaluation' -Encoding UTF8
rg -n "[ \t]$" docs\task_339a_project_lifecycle_frontend_readonly_model_plan.md
git diff --check -- docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md
```

Expected:

- Plan file exists.
- Lifecycle DTO, readonly error, selected surfaces, and validation commands are present.
- Trailing whitespace scan returns no matches.
- `git diff --check` reports no whitespace errors.

## 8. Stop Point

Stop after creating `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`.

Do not write frontend product code, implement TASK_339A, start TASK_340 implementation, or enter backend/Workbench implementation lanes until this plan is explicitly reviewed and approved after the restored-input reread.
