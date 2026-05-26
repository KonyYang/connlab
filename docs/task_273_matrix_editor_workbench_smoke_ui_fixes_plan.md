# Matrix Editor Workbench Smoke UI Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Matrix Editor to Project Workbench smoke-tested flow understandable by replacing manual save/discard actions with auto-save, clarifying revision actions, enabling group changes in revision drafts, and removing the old Workbench group-card Matrix overview.

**Architecture:** Keep the change frontend-first and reuse existing APIs. Matrix Editor owns auto-save orchestration around `saveProjectMatrixDraft`; authority confirmation continues through existing confirm APIs. Project Workbench removes the old runtime overview and promotes the ConfirmedMatrix projection as the single primary Matrix surface.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, CSS, existing FastAPI endpoints through `frontend/src/api/client.ts`, pytest static guards.

---

## Anti-Skip Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES` (planned)
- Allowed reason: `TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY` is complete, the task board has no active implementation task, and user smoke testing identified UI blockers in the current Matrix Editor to Workbench flow.

Implementation must wait for explicit user approval after this plan is reviewed.

## Required Project Protocol

Before implementation, use:

- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product context

## Product / UI Context

ConnLab is a `product` UI. The physical scene is a lab coordinator on a daytime Windows workstation, revising a Matrix and expecting the Project Workbench to show the confirmed authority immediately after confirmation.

Design direction:

- State before action.
- Workflow before tools.
- Matrix before output.
- Fewer primary buttons.
- One primary Matrix surface in Workbench.

## Scope Boundary

In scope:

- Frontend auto-save behavior for Matrix draft edits using existing save API.
- Matrix Editor action cleanup and workflow copy.
- Revision-draft group selection without forcing new source import.
- Confirm revision success navigation back to Workbench.
- Workbench old Matrix overview removal.
- Workbench confirmed projection refresh validation.
- Frontend tests, static guards, docs/task state updates.

Out of scope:

- Backend database/schema changes.
- New backend APIs unless an existing API is proven insufficient during implementation review.
- StepInstance, execution persistence, evidence upload, image management.
- Report, fee, AI, equipment, permission, approval workflow.
- Full Workbench redesign or real execution lifecycle actions.

## Existing Baseline

Observed implementation facts:

- Matrix Editor currently exposes `Save Draft`, `Discard Draft Changes`, `Change Selected Groups`, `Change Source Matrix`, `Confirm As Active Matrix`, `Create Revision Draft`, and `Confirm Revision`.
- `Save Draft` uses existing `saveProjectMatrixDraft`.
- `Change Selected Groups` currently depends on `importPreview`; when source preview session is unavailable, it tells the user to use `Change Source Matrix`.
- First confirmation uses `confirmProjectMatrixDraft`.
- Revision confirmation uses `confirmProjectMatrixRevisionDraft`.
- Workbench currently renders both the old group-card `ProjectWorkbenchMatrixOverview` surface and the new `ProjectWorkbenchMatrixProjectionPanel`.

## File Structure

Modify:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Add debounced auto-save.
  - Gate confirm actions on save state.
  - Support group selection from current draft/revision groups.
  - Navigate to Workbench after successful revision confirmation.

- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
  - Remove primary `Save Draft` and `Discard Draft Changes` buttons.
  - Keep lower-priority revert affordance only when needed.
  - Clarify first confirm versus revision confirm actions.

- `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
  - Update action copy and mode copy.
  - Add auto-save status copy if useful.

- `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
  - Show current mode and save status.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Cover auto-save, save failure blocking confirm, revision flow, group selection without fresh source import, and confirm navigation.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Remove old `ProjectWorkbenchMatrixOverview` rendering and import.
  - Promote `ProjectWorkbenchMatrixProjectionPanel` as the primary Matrix surface.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - Adjust layout if needed after old overview removal.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - Ensure projection remains primary and loads after navigation/refresh.

- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.test.tsx`
  - Preserve TASK_272 history behavior after Workbench layout changes.

- `frontend/src/workbench.css`
  - Remove or reduce styles only tied to the old group-card overview if unused.
  - Add auto-save status and revised Workbench layout styles.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_273 static guard for removed old overview, no primary Save/Discard buttons, auto-save status copy, and no backend scope expansion.

- `docs/task_board.md`, `docs/task_plan_index.md`, `tasks/TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES.md`
  - Update after implementation and validation.

Likely no backend files should change.

---

### Task 1: Add Matrix Editor Auto-Save Tests

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Write failing tests for auto-save status**

Add tests that render Matrix Editor with a persisted draft, edit a matrix cell, and assert:

- `Unsaved changes` appears immediately.
- `Saving...` appears while `saveProjectMatrixDraft` is pending.
- `Saved` appears after the save resolves.
- `Save Draft` is not visible as a primary action.
- `Discard Draft Changes` is not visible as a primary action.

- [ ] **Step 2: Write failing test for save failure blocking confirmation**

Mock `saveProjectMatrixDraft` rejection after an edit and assert:

- `Save failed. Retry before confirming.` appears.
- `Confirm As Active Matrix` or `Confirm Revision` is disabled.
- the disabled reason is visible through existing disabled affordance or nearby status copy.

### Task 2: Implement Matrix Editor Auto-Save

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
- Modify: `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`

- [ ] **Step 1: Replace manual-save-first state with auto-save status**

Keep existing baseline signature logic, but make the primary save flow automatic:

```ts
type AutoSaveState = "idle" | "dirty" | "saving" | "saved" | "error";
```

Map to UI copy:

```ts
const AUTO_SAVE_COPY: Record<AutoSaveState, string> = {
  idle: "Saved",
  dirty: "Unsaved changes",
  saving: "Saving...",
  saved: "Saved",
  error: "Save failed. Retry before confirming.",
};
```

- [ ] **Step 2: Add debounced save effect**

When `hasUnsavedChanges` becomes true and draft is persisted, debounce a call to existing `onSaveDraft` behavior. Use a cleanup timeout so rapid edits do not save on every keystroke.

- [ ] **Step 3: Block confirm while saving or failed**

Confirm availability must require:

- no validation errors
- persisted draft exists
- auto-save state is not `dirty`, `saving`, or `error`

### Task 3: Simplify Matrix Editor Action Groups

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- Modify: `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Remove primary Save/Discard buttons**

The action group should no longer render:

- `Save Draft`
- `Discard Draft Changes`

- [ ] **Step 2: Add low-priority revert affordance only when useful**

Render `Revert to last saved draft` only when there are unsaved changes or save failure. It should not sit as an equal primary workflow action.

- [ ] **Step 3: Update copy**

Keep primary actions focused on:

- `Change Selected Groups`
- `Change Source Matrix`
- `Confirm As Active Matrix` for first confirmation only
- `Create Revision Draft`
- `Confirm Revision`

### Task 4: Fix Change Selected Groups For Revision Drafts

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Write failing test**

Set up a persisted revision draft with groups loaded from API and no current `importPreview`. Click `Change Selected Groups` and assert selection mode opens from the current draft groups.

- [ ] **Step 2: Implement draft-derived group selection source**

When `importPreview` is unavailable but current editor groups exist, build selection view state from the current matrix editor groups and rows instead of requiring `Change Source Matrix`.

- [ ] **Step 3: Preserve source import behavior**

When a fresh source import session exists, keep using the existing import selection model so TASK_261/TASK_262 behavior remains intact.

### Task 5: Clarify Confirm Actions And Navigation

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Write failing tests**

Cover:

- existing active authority state hides or disables `Confirm As Active Matrix`.
- revision draft shows `Confirm Revision`.
- confirming revision calls `confirmProjectMatrixRevisionDraft`.
- successful revision confirmation calls `onBackToWorkbench`.

- [ ] **Step 2: Implement first-confirm versus revision-confirm visibility**

Rules:

- If no active authority exists and current draft has no `base_confirmed_matrix_id`, show `Confirm As Active Matrix`.
- If active authority exists and no revision draft is loaded, make `Create Revision Draft` the primary next action.
- If revision draft is loaded, show `Confirm Revision`.

- [ ] **Step 3: Navigate after successful revision confirmation**

After `confirmProjectMatrixRevisionDraft` resolves:

- update success state briefly if needed
- call `onBackToWorkbench`
- trigger one explicit Workbench reload path so projection/history APIs re-fetch current active authority

Add test assertion that Workbench-facing fetches run again after revision confirmation return.

Do not invent a new route or API.

### Task 6: Remove Old Workbench Matrix Overview

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Remove old overview render path**

Remove import and rendering of `ProjectWorkbenchMatrixOverview` from Workbench layout.

- [ ] **Step 2: Promote confirmed projection**

Render `ProjectWorkbenchMatrixProjectionPanel` as the primary Matrix work surface.
It must own `loading`, `not_ready`, `empty`, `error`, and `ready` display states after old overview removal.

- [ ] **Step 3: Keep right-side step context**

Keep the projection component's `RecordStepWorkspacePanel` tied to selected tokens.

- [ ] **Step 4: Update tests**

Assert:

- old `Runtime execution map` / group-card overview is absent.
- `Matrix execution projection` is present.
- `Generate Test Record Draft` is present when projection is ready.
- `Authority Change History` remains present.
- no blank primary Matrix region appears in `loading/not_ready/error` states.

### Task 7: Add Static Guards

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_273 guard**

Guard:

- `ProjectWorkbenchLayout.tsx` no longer imports `ProjectWorkbenchMatrixOverview`.
- Workbench still imports or renders `ProjectWorkbenchMatrixProjectionPanel`.
- Matrix action group does not contain primary labels `Save Draft` or `Discard Draft Changes`.
- Auto-save copy exists.
- No backend files are expected in TASK_273 plan.
- Forbidden future scope words are not introduced as active action copy in edited Matrix Editor and Workbench files.

### Task 8: Run Validation And Update Task State

**Files:**

- Modify: `tasks/TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Run frontend tests**

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm test -- --run AuthorityChangeHistoryPanel
npm run build
```

- [ ] **Step 2: Run static and smoke tests**

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task273 or task272 or matrix_editor or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

- [ ] **Step 3: Manual smoke path**

Validate:

```text
Matrix import -> group selection -> confirm initial authority -> Workbench projection visible
Workbench -> Matrix Editor -> Create Revision Draft -> Change Selected Groups -> auto-save -> Confirm Revision -> Workbench
Workbench refresh -> updated projection and authority history visible
```

- [ ] **Step 4: Update board and task**

Mark TASK_273 complete only after validation passes. Do not activate the next task in the same implementation turn.

## Review Checklist

- [ ] Auto-save status is visible and blocks confirm on failure.
- [ ] Main action area no longer overloads users with Save/Discard.
- [ ] Revision path is clear for already confirmed Matrix authority.
- [ ] Workbench has only one primary Matrix authority projection surface.
- [ ] No backend schema/API/domain changes were introduced.
- [ ] No StepInstance/execution persistence/report/fee/AI/equipment/permission/approval scope was introduced.
