# Persistent Matrix Import Session UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let operators move between matrix candidate preview, group selection, and draft editing without losing the current import context.

**Architecture:** This is a frontend-only in-memory session UX refinement. Keep existing TASK_261 commit API and backend persistence unchanged; add a small Matrix import session helper and wire navigation actions in the existing Matrix Editor feature.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, CSS in `frontend/src/workbench.css`, pytest static shell tests.

---

## Anti-Skip Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX`
- Allowed reason: TASK_261 to TASK_266 are complete, `docs/task_board.md` has no active implementation task, and the user requested TASK_267 task and plan creation from the post-Phase-11 guideline.

## Scope Lock

Implement only frontend in-memory Matrix import session UX:

- Preserve import preview context during one Matrix Workspace runtime session.
- Add navigation between candidate preview, group selection, and draft editor.
- Keep `Change Selected Groups` separate from `Change Source Matrix`.
- Keep TASK_261 commit API unchanged.

Do not implement:

- Backend import-session persistence.
- Database/schema/API changes.
- Reload/app restart recovery.
- Multi-matrix append/merge.
- Test Record generation, StepInstance, LLCR runtime persistence, report engine, AI recommendation, permissions, or LAN behavior.

## File Responsibilities

- `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
  - New helper for deriving live-session availability and action copy.
  - Centralizes the distinction between "session available" and "source preview unavailable".

- `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`
  - Add `Back to matrix candidate selection` and `Cancel import session` actions.
  - Keep `Confirm selected groups` unchanged.
  - Preserve disabled `Append Matrix (Future)`.

- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
  - Make `Change Selected Groups` enabled/disabled based on props supplied by `MatrixEditorWorkspace`.
  - Show disabled reason when live import session is unavailable.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Track and preserve the current in-memory import session.
  - Reopen import preview dialog from group selection and draft editing.
  - Clear import session only on explicit cancel or new source file selection.
  - Keep source-change confirmation guard from TASK_266.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Cover back-to-candidate navigation, cancel-session behavior, draft-to-group reselection, and disabled reselection when no live session exists.

- `frontend/src/workbench.css`
  - Add compact styling for any new session status or button layout tweaks.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_267 static guardrails.

## UX Decisions

1. "Persistent" means persistent within the current Matrix Workspace runtime.
   - It does not survive browser refresh or route remount.
   - It does not require `localStorage`, `sessionStorage`, or backend session APIs.

2. The current source preview dialog remains the matrix candidate preview surface.
   - It already contains PDF preview, page/table/keyword locator, reparse, Replace, and Append placeholder.
   - TASK_267 adds safe return paths to this surface.

3. `Change Selected Groups` is enabled only when `importPreview` exists.
   - It re-enters selection mode using the current preview payload.
   - It preserves the previously selected group keys when possible.

4. If a persisted draft is loaded without live `importPreview`, `Change Selected Groups` stays disabled.
   - Disabled reason: `Source preview session unavailable. Use Change Source Matrix to start a new source session.`

5. `Cancel import session` is explicit.
   - It clears file, preview payload, PDF token, locator fields, selection keys, import errors/messages, and selection mode.
   - It returns the user to normal editor state without deleting the current saved draft.

6. `Back to matrix candidate selection` from group selection reopens the existing preview dialog.
   - It must not clear `importPreview`, PDF token, locator fields, or selected group keys.

## Task 1: Add Import Session Helper

**Files:**

- Create: `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`

- [ ] **Step 1: Create helper**

Create `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`:

```ts
import { type MatrixPreviewResponse } from "../../api/client";

export type MatrixImportSessionActionState = {
  hasLivePreview: boolean;
  changeSelectedGroupsDisabled: boolean;
  changeSelectedGroupsDisabledReason: string;
};

export function buildMatrixImportSessionActionState(
  preview: MatrixPreviewResponse | null
): MatrixImportSessionActionState {
  const hasLivePreview = preview !== null;
  return {
    hasLivePreview,
    changeSelectedGroupsDisabled: !hasLivePreview,
    changeSelectedGroupsDisabledReason: hasLivePreview
      ? ""
      : "Source preview session unavailable. Use Change Source Matrix to start a new source session.",
  };
}

export function preserveSelectedGroupKeys(input: {
  availableGroupKeys: string[];
  previousSelectedGroupKeys: string[];
}): string[] {
  const available = new Set(input.availableGroupKeys);
  const preserved = input.previousSelectedGroupKeys.filter((groupKey) => available.has(groupKey));
  return preserved.length > 0 ? preserved : input.availableGroupKeys;
}
```

- [ ] **Step 2: Build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 2: Extend MatrixImportSelectionMode Navigation

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`

- [ ] **Step 1: Add props**

Add two props to `MatrixImportSelectionModeProps`:

```ts
onBackToCandidateSelection: () => void;
onCancelSession: () => void;
```

Add them to the function parameters:

```ts
onBackToCandidateSelection,
onCancelSession,
```

- [ ] **Step 2: Replace single Cancel action with explicit navigation**

In `.matrix-editor-selection-mode-actions`, replace:

```tsx
<button type="button" className="matrix-editor-import-secondary-button" onClick={onCancel}>Cancel</button>
```

with:

```tsx
<button type="button" className="matrix-editor-import-secondary-button" onClick={onBackToCandidateSelection}>
  Back to matrix candidate selection
</button>
<button type="button" className="matrix-editor-import-secondary-button" onClick={onCancel}>
  Back to editor
</button>
<button type="button" className="matrix-editor-import-secondary-button" onClick={onCancelSession}>
  Cancel import session
</button>
```

- [ ] **Step 3: Build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 3: Wire Import Session In MatrixEditorWorkspace

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`

- [ ] **Step 1: Import helpers**

Add:

```ts
import {
  buildMatrixImportSessionActionState,
  preserveSelectedGroupKeys,
} from "./matrixImportSessionModel";
```

- [ ] **Step 2: Derive session action state**

Near existing `importSelectionViewModel` derivation, add:

```ts
const importSessionActionState = buildMatrixImportSessionActionState(importPreview);
```

- [ ] **Step 3: Add session reset helper**

Add near import handlers:

```ts
const clearImportSession = (): void => {
  setImportFile(null);
  setImportPreview(null);
  setImportPreviewPdfToken(null);
  setLocatorPage("");
  setLocatorTableOnPage("");
  setLocatorKeyword("");
  setImportError(null);
  setImportLookupMessage("");
  setImportLookupTone("idle");
  setGroupSelectionKeys([]);
  setGroupSelectionStatus("");
  setCommittingImport(false);
  setShowImportDialog(false);
  setShowImportSelectionMode(false);
};
```

- [ ] **Step 4: Add back-to-candidate handler**

Add:

```ts
const onBackToMatrixCandidateSelection = (): void => {
  setShowImportSelectionMode(false);
  setShowImportDialog(true);
  setGroupSelectionStatus("");
  setCommittingImport(false);
};
```

- [ ] **Step 5: Add change-selected-groups handler**

Add:

```ts
const onChangeSelectedGroups = (): void => {
  const selectionViewModel = buildMatrixImportSelectionViewModel(importPreview);
  if (!selectionViewModel || selectionViewModel.groups.length === 0) {
    setGroupSelectionStatus("Source preview session unavailable. Use Change Source Matrix to start a new source session.");
    return;
  }
  const availableGroupKeys = selectionViewModel.groups.map((group) => group.groupKey);
  setGroupSelectionKeys((previous) =>
    preserveSelectedGroupKeys({
      availableGroupKeys,
      previousSelectedGroupKeys: previous,
    })
  );
  setGroupSelectionStatus("");
  setShowImportDialog(false);
  setShowImportSelectionMode(true);
};
```

- [ ] **Step 6: Preserve selected group keys after commit**

Inside `onCommitImportedGroups`, insert the committed keys immediately after `setShowImportSelectionMode(false);`:

```ts
setGroupSelectionKeys(response.selected_group_keys_committed);
```

This does not change backend behavior. It keeps the UI session aligned with the committed selection.

The intended success block order is:

```ts
applyDraftSnapshotToEditor(response.project_matrix_draft);
setHasPersistedDraft(true);
setSaveState("idle");
setSaveMessage(response.commit_status === "reused" ? "Loaded existing draft from same group selection." : "Project draft created from selected groups.");
setShowImportSelectionMode(false);
setGroupSelectionKeys(response.selected_group_keys_committed);
setGroupSelectionStatus("");
setImportError(null);
```

- [ ] **Step 7: Pass enabled/disabled state to action groups**

In `MatrixWorkspaceActionGroups`, replace current TASK_266 values:

```tsx
changeSelectedGroupsDisabled={true}
changeSelectedGroupsDisabledReason="Group reselection for a persisted matrix requires a follow-up source lineage task."
onChangeSelectedGroups={() => undefined}
```

with:

```tsx
changeSelectedGroupsDisabled={importSessionActionState.changeSelectedGroupsDisabled}
changeSelectedGroupsDisabledReason={importSessionActionState.changeSelectedGroupsDisabledReason}
onChangeSelectedGroups={onChangeSelectedGroups}
```

- [ ] **Step 8: Pass new selection mode handlers**

Update `MatrixImportSelectionMode` usage:

```tsx
onBackToCandidateSelection={onBackToMatrixCandidateSelection}
onCancel={onCancelGroupSelection}
onCancelSession={clearImportSession}
```

- [ ] **Step 9: Update no-valid-matrix selection fallback actions**

In the no-valid-matrix fallback header, include:

```tsx
<button type="button" className="matrix-editor-import-secondary-button" onClick={onBackToMatrixCandidateSelection}>
  Back to matrix candidate selection
</button>
<button type="button" className="matrix-editor-import-secondary-button" onClick={onCancelGroupSelection}>
  Back to editor
</button>
<button type="button" className="matrix-editor-import-secondary-button" onClick={clearImportSession}>
  Cancel import session
</button>
```

- [ ] **Step 10: Build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 4: Add Session Copy And Styling

**Files:**

- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Merge selection action wrapping into the existing selector**

Find the existing selector in `frontend/src/workbench.css`:

```css
.matrix-editor-selection-mode-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
```

Replace it with:

```css
.matrix-editor-selection-mode-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.matrix-editor-selection-mode-actions button {
  white-space: normal;
  min-height: 34px;
}
```

- [ ] **Step 2: Build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 5: Update React Tests

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add test for group selection back navigation**

Add a test that:

1. Uploads a file.
2. Opens Replace.
3. Clicks `Back to matrix candidate selection`.
4. Asserts `Word PDF Preview`, `Page`, `Table on page`, and `Reparse` are visible again.
5. Clicks `Replace` again.
6. Asserts selected group checkboxes are still available.

Test body:

```ts
it("returns from group selection to matrix candidate preview without losing source context", async () => {
  apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce({
    project_id: "P1",
    source_document_path: "C:/specs/spec.docx",
    source_document_name: "spec.docx",
    source_format: ".docx",
    capability_status: "ok",
    generated_at: "2026-05-23T00:00:00Z",
    selected_table_index: 0,
    selected_page_number: 2,
    selected_page_table_index: 1,
    candidate_tables: [],
    preview_pdf_token: "pdf-token-test-267",
    rows: [
      {
        source_row_index: 1,
        test_item: "Visual Examination",
        source_section: "6.1",
        group_tokens: { "Group A": "1", "Group B": "2" },
        is_sample_row: false,
      },
    ],
    groups: [
      {
        group_key: "g1",
        group_label: "Group A",
        source_table_index: 0,
        extraction_status: "ok",
        sample_quantity_expression: "5",
        sample_note: null,
        steps: [],
      },
      {
        group_key: "g2",
        group_label: "Group B",
        source_table_index: 0,
        extraction_status: "ok",
        sample_quantity_expression: "3",
        sample_note: null,
        steps: [],
      },
    ],
    warnings: [],
    blockers: [],
  });

  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
  await waitFor(() => {
    expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
  });

  const input = document.querySelector("input[type='file']") as HTMLInputElement;
  const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
  fireEvent.change(input, { target: { files: [file] } });

  await waitFor(() => {
    expect(screen.getByRole("button", { name: "Replace" })).toBeTruthy();
  });

  fireEvent.click(screen.getByRole("button", { name: "Replace" }));
  await waitFor(() => {
    expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
  });

  fireEvent.click(screen.getByRole("button", { name: "Back to matrix candidate selection" }));
  await waitFor(() => {
    expect(screen.getByTitle("Word PDF Preview")).toBeTruthy();
    expect(screen.getByLabelText("Page")).toBeTruthy();
    expect(screen.getByLabelText("Table on page")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Reparse" })).toBeTruthy();
  });

  fireEvent.click(screen.getByRole("button", { name: "Replace" }));
  await waitFor(() => {
    expect(screen.getByLabelText("Select Group A")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Add test for draft Change Selected Groups**

Add a test that:

1. Uploads source.
2. Commits selected groups.
3. Returns to editor.
4. Clicks `Change Selected Groups`.
5. Asserts selection mode opens without another upload.

Use existing commit test setup and assert `apiMocks.previewProjectTestPlanMatrixFromUpload` call count remains unchanged after clicking `Change Selected Groups`.

- [ ] **Step 3: Add test for cancel import session**

Add a test that:

1. Enters selection mode from an uploaded source.
2. Clicks `Cancel import session`.
3. Asserts selection mode is gone.
4. Asserts `Change Selected Groups` is disabled and has title `Source preview session unavailable. Use Change Source Matrix to start a new source session.`

- [ ] **Step 4: Run tests**

Run:

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

Expected:

```text
all MatrixEditorWorkspace tests pass
```

## Task 6: Add Static Guardrails

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_267 static test**

Add:

```python
def test_task267_persistent_matrix_import_session_ux_is_wired() -> None:
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    selection_mode_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixImportSelectionMode.tsx"
    ).read_text(encoding="utf-8")
    action_groups_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixWorkspaceActionGroups.tsx"
    ).read_text(encoding="utf-8")
    session_model_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "matrixImportSessionModel.ts"
    ).read_text(encoding="utf-8")

    for required in [
        "Back to matrix candidate selection",
        "Cancel import session",
        "onBackToMatrixCandidateSelection",
        "clearImportSession",
        "buildMatrixImportSessionActionState",
        "preserveSelectedGroupKeys",
    ]:
        assert required in matrix_editor_source or required in selection_mode_source or required in session_model_source

    assert "Source preview session unavailable. Use Change Source Matrix to start a new source session." in session_model_source
    assert "Change Selected Groups" in action_groups_source
    assert "commitMatrixImport" in matrix_editor_source
```

- [ ] **Step 2: Run static tests**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task267 or task266 or matrix_editor"
```

Expected:

```text
TASK_267 and existing Matrix Editor checks pass
```

## Task 7: Final Verification And Documentation Sync

**Files:**

- Modify after passing validation: `tasks/TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX.md`
- Modify after passing validation: `docs/task_board.md`

- [ ] **Step 1: Run verification**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task267 or task266 or matrix_editor"
```

Expected:

```text
passes
```

Run:

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

Expected:

```text
passes
```

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
passes
```

Run:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 2: Confirm no backend files changed**

Run:

```powershell
git diff --name-only
```

Expected TASK_267 implementation files are limited to:

```text
docs/task_267_persistent_matrix_import_session_ux_plan.md
docs/task_board.md
tasks/TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX.md
frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx
frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx
frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx
frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
frontend/src/features/matrix-editor/matrixImportSessionModel.ts
frontend/src/workbench.css
tests/unit/test_frontend_shell_files.py
```

- [ ] **Step 3: Update task file to complete**

After validation passes, update status:

```markdown
## Status

Complete on 2026-05-24. Persistent Matrix import session UX is implemented and verified.
```

Add validation results under the Validation section.

- [ ] **Step 4: Update task board**

Update `docs/task_board.md`:

```markdown
> Status: ... + TASK_267 complete
> Last Updated: 2026-05-24
> Current Active Task: none (`TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX` complete; awaiting next approved task).
```

Add a TASK_267 completion note with deliverables, validation commands, and scope boundary.

## Review Checklist Before Implementation

- [ ] Task remains frontend-only.
- [ ] No backend files are modified.
- [ ] `Change Selected Groups` is not presented as `Import Matrix`.
- [ ] `Back to matrix candidate selection` preserves current source preview/PDF/locator context.
- [ ] `Cancel import session` clears only the import session, not the saved draft.
- [ ] TASK_261 commit API remains unchanged.
- [ ] TASK_266 state banner and action grouping remain visible and working.

## Execution Handoff

After this plan is approved, implement with `superpowers:executing-plans` in this session. Execute task by task, run each verification command at the checkpoint where it is listed, and stop after TASK_267 completion. Do not proceed to TASK_268 or any follow-up task.
