# Matrix Editor Single Draft Publish Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert Matrix Editor into one user-facing draft editing and publish flow with compact header/actions and a single `Confirm As Active Matrix` publish action.

**Architecture:** Keep Matrix Editor as the frontend owner of draft editing state and auto-save coordination. Use existing Matrix draft and confirm APIs as the implementation detail behind one user-facing publish action. Do not introduce a new backend contract unless implementation proves the current APIs cannot satisfy the approved acceptance criteria.

**Tech Stack:** React, TypeScript, Vite/Vitest, FastAPI-backed typed client, pytest static guards.

---

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

`TASK_277_MATRIX_EDITOR_SINGLE_DRAFT_PUBLISH_FLOW` complete.

## Allowed Reason

TASK_276 was complete and `docs/task_board.md` marked `TASK_277_MATRIX_EDITOR_SINGLE_DRAFT_PUBLISH_FLOW` as the current active task after user approval. Implementation and validation are completed.

## Design Summary

Matrix Editor should present a single mental model:

```text
Edit Matrix draft -> auto-save -> Confirm As Active Matrix -> Workbench refreshes
```

Internal versioning remains available through existing APIs, but users should not see `Create Revision Draft`, `Confirm Revision`, `Draft Actions`, or `Authority Actions`.

When active authority exists, the editor may create/load an editable revision draft internally only when needed by editing/publish flow. This is not a user-facing action. If content is unchanged from the active authority baseline, confirm should not publish a redundant confirmed version.

## File Responsibilities

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Owns Matrix Editor state, auto-save, draft loading, unified confirm behavior, compact header composition, and action placement.
- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
  - Replace grouped action cards with a compact toolbar component or simplify this component into compact actions.
- `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
  - Remove from render path or reduce to a compact save-status-only surface if still needed.
- `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
  - Remove user-facing revision/draft consequence copy that is no longer rendered.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Cover unified confirm, auto-save-before-confirm, no-change publish guard, hidden revision action, and Workbench return.
- `frontend/src/workbench.css`
  - Compact Matrix Editor header/action styling.
- `tests/unit/test_frontend_shell_files.py`
  - Static guard against reintroducing user-facing revision/draft action concepts.

## Task 1: Add Regression Tests For Single Publish Flow

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add a test that hides internal revision actions**

Add or update a Matrix Editor render test so it asserts:

```ts
expect(screen.queryByRole("button", { name: "Create Revision Draft" })).toBeNull();
expect(screen.queryByRole("button", { name: "Confirm Revision" })).toBeNull();
expect(screen.queryByText("Draft Actions")).toBeNull();
expect(screen.queryByText("Authority Actions")).toBeNull();
expect(screen.queryByText("Current State")).toBeNull();
expect(screen.getByRole("button", { name: "Confirm As Active Matrix" })).toBeTruthy();
```

- [ ] **Step 2: Add a test that confirm flushes unsaved edits before publish**

Use the existing editable row setup. Change a Matrix field, keep `saveProjectMatrixDraft` pending, click `Confirm As Active Matrix`, and assert confirm waits for save:

```ts
fireEvent.change(screen.getByLabelText("Row 1 test item"), {
  target: { value: "Visual Examination Updated" },
});

await waitFor(() => {
  expect(apiMocks.saveProjectMatrixDraft).toHaveBeenCalledTimes(1);
});

fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));
expect(apiMocks.confirmProjectMatrixRevisionDraft).not.toHaveBeenCalled();
```

Then resolve the save promise and assert the correct confirm API is called.

- [ ] **Step 3: Add a test that a revision draft uses the revision confirm API behind the same button**

Given `buildRevisionDraft()` has `base_confirmed_matrix_id: "confirmed-1"`, click `Confirm As Active Matrix` and assert:

```ts
expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledWith(
  "P1",
  "draft-1",
  { confirmed_by: "connlab-operator" }
);
expect(apiMocks.confirmProjectMatrixDraft).not.toHaveBeenCalled();
expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
```

- [ ] **Step 4: Add a test that first authority uses first-confirm API behind the same button**

Use a draft fixture with `base_confirmed_matrix_id: null` and no active workbench authority. Click `Confirm As Active Matrix` and assert:

```ts
expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledWith(
  "P1",
  "draft-1",
  { confirmed_by: "connlab-operator" }
);
expect(apiMocks.confirmProjectMatrixRevisionDraft).not.toHaveBeenCalled();
expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
```

- [ ] **Step 5: Add a no-change guard test**

Render a revision draft without editing. Assert the confirm button is disabled or has a disabled reason equivalent to:

```text
No Matrix changes to publish.
```

Expected: no confirm API is called.

- [ ] **Step 6: Run the focused test and confirm it fails before implementation**

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace
```

Expected before implementation: at least the hidden action and unified confirm tests fail.

## Task 2: Introduce Unified Publish State Helpers

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`

- [ ] **Step 1: Add internal status types**

Keep user-facing language simple:

```ts
type MatrixPublishState = "idle" | "saving" | "publishing" | "success" | "error";
type MatrixPublishMode = "first_authority" | "revision_authority";
```

- [ ] **Step 2: Track active authority baseline signature**

Add state near existing save baseline state:

```ts
const [activeAuthorityBaselineSignature, setActiveAuthorityBaselineSignature] =
  useState<string | null>(null);
```

When loading or internally creating a revision draft from active authority, capture:

```ts
setActiveAuthorityBaselineSignature(JSON.stringify(buildDraftSavePayload(nextRows, nextGroups, nextSamples)));
```

For first-authority drafts with no active baseline:

```ts
setActiveAuthorityBaselineSignature(null);
```

- [ ] **Step 3: Derive publish mode and no-change state**

Add derived values:

```ts
const publishMode: MatrixPublishMode =
  projectMatrixDraftBaseConfirmedMatrixId ? "revision_authority" : "first_authority";
const hasNoAuthorityChanges =
  activeAuthorityBaselineSignature !== null &&
  postSaveSignature === activeAuthorityBaselineSignature;
```

`postSaveSignature` must be recomputed from the latest saved/normalized draft snapshot after `saveCurrentDraftNow()` resolves, so no-change checks do not rely on stale pre-save payload.

- [ ] **Step 4: Replace separate confirm state naming**

Keep existing state if the smaller edit is safer, but render only one user-facing publish action. If renaming is practical, replace separate `confirmRevisionMessage` / `confirmActiveMessage` with one publish message:

```ts
const [publishState, setPublishState] = useState<MatrixPublishState>("idle");
const [publishMessage, setPublishMessage] = useState("");
```

## Task 3: Flush Current Draft Before Confirm

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`

- [ ] **Step 1: Add an immediate save helper**

Implement inside `MatrixEditorWorkspace` so it can access current payload and setters:

```ts
const saveCurrentDraftNow = async (): Promise<ProjectMatrixDraft | null> => {
  if (!projectId.trim() || !projectMatrixDraftId) {
    return null;
  }
  if (autoSaveTimerRef.current !== null) {
    window.clearTimeout(autoSaveTimerRef.current);
    autoSaveTimerRef.current = null;
  }
  if (!hasUnsavedChanges && saveState !== "error") {
    return null;
  }
  setSaveState("saving");
  const saved = await saveProjectMatrixDraft(
    projectId,
    projectMatrixDraftId,
    currentSavePayload
  );
  setHasPersistedDraft(true);
  applyDraftSnapshotToEditor(saved);
  setSaveState("saved");
  return saved;
};
```

- [ ] **Step 2: Use the helper from publish**

In unified confirm, call:

```ts
await saveCurrentDraftNow();
```

before deciding the confirm endpoint.

- [ ] **Step 2.1: Recompute signature after forced save**

Immediately after `saveCurrentDraftNow()` succeeds, derive `postSaveSignature` from the returned saved snapshot (or from editor snapshot after `applyDraftSnapshotToEditor(saved)`) and use that value for no-change publish guard.

- [ ] **Step 3: Preserve save failure behavior**

If immediate save fails:

```ts
setSaveState("error");
setPublishState("error");
setPublishMessage(parseRequestError(error, "Save failed. Confirm was not published."));
return;
```

## Task 4: Replace Split Confirm Buttons With One Publish Action

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`

- [ ] **Step 1: Replace `onConfirmRevision` and `onConfirmAsActiveMatrix` render wiring with one handler**

Add:

```ts
const onConfirmAsActiveMatrix = async (): Promise<void> => {
  if (!canPublishActiveMatrix || !projectMatrixDraftId) {
    setPublishState("error");
    setPublishMessage(publishDisabledReason || "Confirm is unavailable.");
    return;
  }
  setPublishState("saving");
  try {
    await saveCurrentDraftNow();
  } catch (error) {
    setSaveState("error");
    setPublishState("error");
    setPublishMessage(parseRequestError(error, "Save failed. Confirm was not published."));
    return;
  }

  const savedDraft = await saveCurrentDraftNow();
  const signatureAfterSave = buildSignatureFromSavedDraft(savedDraft ?? currentDraftSnapshot);
  if (
    activeAuthorityBaselineSignature !== null &&
    signatureAfterSave === activeAuthorityBaselineSignature
  ) {
    setPublishState("error");
    setPublishMessage("No Matrix changes to publish.");
    return;
  }

  setPublishState("publishing");
  try {
    if (publishMode === "revision_authority") {
      await confirmProjectMatrixRevisionDraft(projectId, projectMatrixDraftId, {
        confirmed_by: MVP_REVISION_CONFIRMED_BY,
      });
    } else {
      await confirmProjectMatrixDraft(projectId, projectMatrixDraftId, {
        confirmed_by: MVP_REVISION_CONFIRMED_BY,
      });
    }
    setPublishState("success");
    onBackToWorkbench();
  } catch (error) {
    setPublishState("error");
    setPublishMessage(parseRequestError(error, "Confirm failed."));
  }
};
```

- [ ] **Step 2: Remove visible `Create Revision Draft` and `Confirm Revision` actions**

Do not render these labels:

```text
Create Revision Draft
Confirm Revision
```

Keep `createMatrixRevisionDraft` available internally if needed on load.

- [ ] **Step 3: Replace `MatrixWorkspaceActionGroups` UI**

Render one compact toolbar:

```tsx
<section className="matrix-workspace-toolbar" aria-label="Matrix editor actions">
  {revertDraftVisible ? <button type="button" disabled={revertDraftDisabled}>Undo</button> : null}
  <button type="button" disabled={changeSelectedGroupsDisabled}>Change groups</button>
  <button type="button" onClick={onChangeSourceMatrix}>Import Matrix</button>
  <button className="matrix-editor-primary-action" type="button" disabled={confirmDisabled}>
    {confirmBusy ? "Confirming..." : "Confirm As Active Matrix"}
  </button>
</section>
```

No consequence paragraphs under buttons.

## Task 5: Load Active Matrix As Internal Editable Draft

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`

- [ ] **Step 1: Keep current draft loading first**

Continue to call:

```ts
const summaries = await listProjectMatrixDrafts(projectId);
```

If an editable draft exists, load it as today.

- [ ] **Step 2: If no editable draft exists but Workbench has active authority, defer revision draft creation until needed**

Use existing active authority signal:

```ts
const hasActiveAuthorityFromWorkbench =
  model.runtimeAuthoritySync?.projectionMatrixReference != null;
```

When `summaries.length === 0 && hasActiveAuthorityFromWorkbench`, do not eagerly create a revision draft on first page load. Instead, create it lazily on first edit intent or first confirm intent via a shared `ensureEditableDraft()` helper:

```ts
const ensureEditableDraft = async (): Promise<ProjectMatrixDraft> => {
  if (projectMatrixDraftId) {
    return currentDraftSnapshot;
  }
  const draft = await createMatrixRevisionDraft(projectId);
  applyDraftSnapshotToEditor(draft);
  setHasPersistedDraft(true);
  setSaveState("saved");
  return draft;
};
```

Do not display `Create Revision Draft` to the user.

- [ ] **Step 3: If no active authority and no draft exists, keep editable initial matrix**

Use the existing `buildInitialMatrixRows()` and `buildInitialGroupColumns()` path.

## Task 6: Compact Matrix Editor Header And Remove State Banner

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Header content**

Render:

```tsx
<button type="button" onClick={onBackToWorkbench}>Back to Workbench</button>
<h2>Matrix Editor</h2>
<p className="matrix-editor-project-identity">
  {projectIdentity} · {model.project.product_name} · {testDescription}
</p>
<span className="matrix-editor-save-status">{AUTO_SAVE_STATUS_COPY[saveState]}</span>
```

Do not foreground:

```text
LTR Registered
BU
Requester
Groups
Steps
Items
Current State
Editing Draft
Draft Save Status
```

- [ ] **Step 2: Remove `MatrixWorkspaceStateBanner` from render path**

Remove:

```tsx
<MatrixWorkspaceStateBanner ... />
```

or keep the component file unused if removing it would expand scope.

- [ ] **Step 3: CSS compacting**

Add/adjust classes so the top area fits within one compact band:

```css
.matrix-editor-target-header {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
}

.matrix-editor-project-identity {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

## Task 7: Static Guards

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_277 static test**

Add a test that reads Matrix Editor files and asserts removed copy is absent:

```py
def test_task277_matrix_editor_single_draft_publish_flow_is_wired() -> None:
    workspace = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "matrix-editor"
        / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    actions = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "matrix-editor"
        / "MatrixWorkspaceActionGroups.tsx"
    ).read_text(encoding="utf-8")

    combined = workspace + "\n" + actions
    assert "Create Revision Draft" not in combined
    assert "Confirm Revision" not in combined
    assert "Draft Actions" not in combined
    assert "Authority Actions" not in combined
    assert "Current State" not in workspace
    assert "Confirm As Active Matrix" in combined
    assert "Back to Workbench" in workspace
```

Do not assert callback invocation by source-string matching in static guard. Verify actual return behavior in `MatrixEditorWorkspace.test.tsx` interaction tests.

- [ ] **Step 2: Run the guard**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task277 or matrix_editor"
```

Expected after implementation: all selected tests pass.

## Task 8: Browser Smoke

**Files:**

- No code files. Manual validation step.

- [ ] **Step 1: Open Matrix Editor**

Open:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/matrix-editor
```

Expected:

- compact header
- no `Create Revision Draft`
- no `Draft Actions`
- no `Authority Actions`
- no large state banner
- one `Confirm As Active Matrix`

- [ ] **Step 2: Confirm Workbench return**

Edit a Matrix cell, wait for `Saved`, click `Confirm As Active Matrix`.

Expected:

- route changes to `/projects/{project_id}`
- Workbench Matrix projection reloads
- no stale Matrix projection from the previous authority remains visible after reload

## Task 9: Final Validation

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace
npm run build
```

Then from repository root:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task277 or task276 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --name-only -- backend
git diff --check
```

Expected:

- Matrix Editor tests pass.
- Static guards pass.
- Build passes.
- Smoke integration passes.
- `git diff --name-only -- backend` has no output unless a backend contract gap was explicitly approved.
- `git diff --check` has no blocking whitespace errors.

## Risks And Controls

1. Internal auto-created revision draft may surprise future maintainers.
   - Control: keep the behavior local and tested; do not show it as a user action.
2. No-change detection can be imperfect if backend changes draft normalization.
   - Control: compare the same `buildDraftSavePayload` signature used by auto-save.
3. Confirm-after-save can race with debounced auto-save.
   - Control: clear pending auto-save timer in `saveCurrentDraftNow`.
4. Workbench may not refresh if route remount is insufficient.
   - Control: browser smoke must verify projection changes after confirm; if it fails, add a frontend refresh key or route-level reload in the approved implementation.

## Completion Updates

After implementation only:

- update `tasks/TASK_277_MATRIX_EDITOR_SINGLE_DRAFT_PUBLISH_FLOW.md` to Complete
- update `docs/task_board.md`
- update `docs/task_plan_index.md`
- include validation results and any backend contract limitations
