# Workbench Step Workspace Refocus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refocus Project Workbench on the existing right-side Step Workspace as the future execution workspace, while simplifying the left Matrix projection and removing redundant main-page audit and Word generation controls.

**Architecture:** Frontend-only. Keep all backend capabilities from TASK_271 and TASK_272 intact. Project Workbench layout remains the composition root. `ProjectWorkbenchMatrixProjectionPanel` becomes a lean read-only Matrix table surface. The existing right-side `Step Workspace` remains the visible step context.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, CSS, existing FastAPI client types, pytest static guards.

---

## Anti-Skip Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS` (planned)
- Allowed reason: `TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES` is complete, the task board sets `TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS` as the current active planned task (awaiting approval), and user smoke testing clarified the Workbench product direction.

Implementation must wait for explicit user approval after this plan is reviewed.

## Required Project Protocol

Before implementation, use:

- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product context

## Product / UI Context

ConnLab is a `product` UI. The physical scene is a lab engineer on an offline Windows workstation using the Workbench to move from Matrix authority into step execution. The interface should prioritize the selected step and its future execution data surface over audit history and document generation buttons.

Design direction:

- Workflow before tools.
- Step before report.
- Matrix before output.
- State before action.
- Avoid duplicate headings, nested cards, and future-feature clutter.

## Scope Boundary

In scope:

- Remove read-only `Record Step Workspace` from the Matrix projection panel.
- Keep existing right-side `Step Workspace`.
- Simplify projection panel headings and framing.
- Hide `Authority Change History` from the main Workbench page.
- Hide `Generate Test Record Draft` from the main Matrix projection page area.
- Preserve backend/API/service capabilities for future placement.
- Update frontend tests and static guards.
- Update task state docs after implementation.

Out of scope:

- Backend changes.
- New API endpoints.
- StepInstance or execution persistence.
- Evidence/image upload.
- Real Record action implementation.
- Report, fee, AI, equipment, permission, approval workflow.
- Full Workbench redesign.

## Existing Baseline

Observed implementation facts:

- `ProjectWorkbenchLayout` renders the existing right-side `runtime-console-step-workspace`.
- `ProjectWorkbenchMatrixProjectionPanel` currently renders:
  - nested `Confirmed Matrix Projection / Matrix execution projection` heading
  - `Generate Test Record Draft`
  - `AuthorityChangeHistoryPanel`
  - projection table
  - read-only `RecordStepWorkspacePanel`
- The browser shows both the existing right-side `Step Workspace` and the new read-only `Record Step Workspace`.
- User explicitly prefers the existing right-side `Step Workspace` as the future execution workspace direction.

## File Structure

Modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - Remove `RecordStepWorkspacePanel` import and rendering.
  - Remove `AuthorityChangeHistoryPanel` rendering from the main projection.
  - Remove `TestRecordDraftGenerationButton` rendering from the main projection.
  - Simplify duplicate heading structure.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - Update expectations to assert projection table remains visible.
  - Assert `Record Step Workspace`, `Authority Change History`, and `Generate Test Record Draft` are not visible in the main panel.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Keep existing right-side Step Workspace.
  - Adjust outer toolbar copy only if needed to prevent duplicate headings.
  - Do not activate future Step Workspace buttons.

- `frontend/src/workbench.css`
  - Remove or orphan-proof styles for removed main-panel elements if they are only used there.
  - Adjust projection layout width after removing read-only panel.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_274 static guards:
    - Workbench projection panel must not render `RecordStepWorkspacePanel`.
    - Workbench projection panel must not render `AuthorityChangeHistoryPanel`.
    - Workbench projection panel must not render `TestRecordDraftGenerationButton`.
    - Right-side `runtime-console-step-workspace` remains present in `ProjectWorkbenchLayout`.
    - No backend files are required for TASK_274.

- `docs/task_board.md`
- `docs/task_plan_index.md`
- `tasks/TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS.md`

Likely preserve:

- `frontend/src/features/project-workbench/RecordStepWorkspacePanel.tsx`
- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.tsx`
- `frontend/src/features/project-workbench/TestRecordDraftGenerationButton.tsx`

Those components can remain for future secondary placement or tests unless static analysis proves they are now dead and removal is explicitly approved.

---

### Task 1: Update Projection Panel Tests

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`

- [ ] **Step 1: Assert removed main-page controls are absent**

Add or update tests so the ready Workbench projection does not show:

- `Record Step Workspace`
- `Authority Change History`
- `Generate Test Record Draft`

- [ ] **Step 2: Preserve Matrix projection table expectations**

Keep assertions that the Matrix projection table and token cells remain visible and selectable.

- [ ] **Step 3: Preserve loading/error/not-ready states**

Ensure the panel still renders clear states when projection data is loading, empty, not ready, or failed.

### Task 2: Simplify `ProjectWorkbenchMatrixProjectionPanel`

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`

- [ ] **Step 1: Remove read-only step panel composition**

Remove the import and rendering of `RecordStepWorkspacePanel`.

- [ ] **Step 2: Remove main projection audit history**

Remove `AuthorityChangeHistoryPanel` from the main projection layout. Do not delete its API client, component, or backend service.

- [ ] **Step 3: Remove main projection Word generation button**

Remove `TestRecordDraftGenerationButton` from the main projection layout. Do not delete backend generation capability.

- [ ] **Step 4: Flatten duplicate heading structure**

Keep one clear `Matrix execution projection` title at the Workbench Matrix region level. The panel body should focus on summary, legend, and table.

### Task 3: Keep Right-Side Step Workspace As The Main Step Context

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` if present or create a focused test if local patterns support it

- [ ] **Step 1: Preserve existing right-side Step Workspace**

Confirm `runtime-console-step-workspace` remains rendered.

- [ ] **Step 2: Keep future actions non-operational**

Do not wire `Image`, `Record`, `Edit step`, `Import data`, `Generate record`, or `Save` to new behavior in this task.

- [ ] **Step 3: Keep token selection wiring unchanged**

If existing Matrix token selection updates the right-side Step Workspace, preserve it. If it does not, do not introduce new backend behavior.

### Task 4: Adjust Styles

**Files:**

- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Remove nested-panel visual clutter**

Adjust classes used by `ProjectWorkbenchMatrixProjectionPanel` so the left projection reads as one Matrix surface.

- [ ] **Step 2: Expand table affordance after removing read-only panel**

Ensure the Matrix table has enough horizontal room and does not leave an empty right column where `RecordStepWorkspacePanel` used to be.

- [ ] **Step 3: Preserve dense product UI**

Keep the Workbench restrained, operational, and table-first.

### Task 5: Add Static Guards

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_274 guard**

Guard against reintroducing removed main-page elements in `ProjectWorkbenchMatrixProjectionPanel.tsx`:

- `RecordStepWorkspacePanel`
- `AuthorityChangeHistoryPanel`
- `TestRecordDraftGenerationButton`

- [ ] **Step 2: Guard right-side Step Workspace preservation**

Assert `ProjectWorkbenchLayout.tsx` still contains `runtime-console-step-workspace`.

- [ ] **Step 3: Guard frontend-only scope**

Assert implementation changes do not touch backend paths:

- `git diff --name-only -- backend` returns no output.
- Add/update static guard assertions that TASK_274 frontend slice does not require backend file edits.

### Task 6: Verify

**Commands:**

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm test -- --run AuthorityChangeHistoryPanel
npm test -- --run TestRecordDraftGenerationButton
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task274 or task273 or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

- [ ] **Step 1: Run frontend tests**
- [ ] **Step 2: Run static guard tests**
- [ ] **Step 3: Run smoke integration test**
- [ ] **Step 4: Run build**
- [ ] **Step 5: Run diff check**

### Task 7: Browser Smoke

**Target:**

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
```

- [ ] **Step 1: Open Workbench**

Confirm:

- right-side `Step Workspace` remains visible
- left Matrix table remains visible
- no read-only `Record Step Workspace`
- no `Authority Change History`
- no `Generate Test Record Draft`

- [ ] **Step 2: Capture screenshot if browser tooling is available**

Use the in-app browser if available.

### Task 8: Update Task State

**Files:**

- Modify: `tasks/TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Mark TASK_274 complete only after validation**

Do not update completion state before verification commands pass or failures are explicitly documented.

- [ ] **Step 2: Stop**

Do not enter the next task.

---

## Review Checklist

Before final response, confirm:

- [ ] `docs/project_management/TASK_REVIEW_CHECKLIST.md` has been considered.
- [ ] No backend/API/domain/storage files changed.
- [ ] Workbench keeps old right-side Step Workspace.
- [ ] New read-only Record Step Workspace is gone from main Workbench.
- [ ] Authority History is hidden from main Workbench.
- [ ] Test Record draft generation button is hidden from main Workbench projection.
- [ ] No future execution actions were made active.
- [ ] Tests and build results are reported.
