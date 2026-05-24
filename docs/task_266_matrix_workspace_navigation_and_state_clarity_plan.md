# Matrix Workspace Navigation And State Clarity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Matrix Workspace clearly show whether the operator is editing a draft, viewing the current active authority after confirmation, or editing a revision draft, while separating draft actions from authority actions.

**Architecture:** This is a frontend-only workflow clarity slice. Keep Matrix authority backend contracts unchanged, add only missing frontend client wiring for the already existing draft-confirm endpoint, and keep UI state derivation local to the Matrix Editor feature.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, CSS in `frontend/src/workbench.css`, pytest static shell tests.

---

## Anti-Skip Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY`
- Allowed reason: TASK_261 to TASK_265 are complete, `docs/task_board.md` marks TASK_266 as planned active, and the user approved moving from task-file creation into executable planning.

## Scope Lock

Implement only frontend workflow clarity:

- State banner for Draft / Active Authority / Revision Draft.
- Draft Actions and Authority Actions grouping.
- Consequence copy for key actions.
- Rename draft save action to `Save Draft`.
- Make `Change Selected Groups` a current-configuration concept, not an import concept.
- Preserve TASK_261 to TASK_265 smoke-flow behavior.

Do not implement:

- Backend Matrix Authority architecture refactor.
- Backend API/schema/database migration.
- Permission system.
- LLCR runtime persistence.
- Report engine.
- AI recommendation.
- Test Record Word generation.
- StepInstance, execution result persistence, or multi-matrix merge.

## File Responsibilities

- `frontend/src/api/client.ts`
  - Add frontend function for existing `POST /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}/confirm`.
  - Reuse existing `ConfirmProjectMatrixRevisionDraftInput` and `ConfirmedMatrixSnapshot` types.

- `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
  - New focused helper for banner/action copy and mode derivation.
  - Keeps string copy and state labels out of the large workspace component.

- `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
  - New small presentational component for current-state banner.

- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
  - New presentational component for Draft Actions and Authority Actions.
  - Receives disabled reasons and event handlers from `MatrixEditorWorkspace`.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Integrate the new banner and action groups.
  - Wire `Confirm As Active Matrix` to existing backend endpoint through the client.
  - Wire `Discard Draft Changes` by reloading the persisted draft.
  - Keep `Change Selected Groups` disabled with explicit copy in this task.
  - Wire `Change Source Matrix` to the existing document picker flow.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Update assertions for `Save Draft`.
  - Add coverage for banner mode, grouped actions, consequence copy, disabled group reselection, and existing import selection hiding behavior.

- `frontend/src/workbench.css`
  - Add compact layout styles for state banner and action groups.
  - Keep visual treatment quiet and dense, aligned with the existing Matrix Editor.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_266 static guardrails for labels, copy, component names, and no backend expansion.

## UX Decisions

1. Draft mode is derived when a persisted draft is loaded and `base_confirmed_matrix_id` is null.
   - Banner: `Editing Draft`
   - Copy: `Not active for downstream outputs`

2. Revision draft mode is derived when a persisted draft is loaded and `base_confirmed_matrix_id` is present, unless the current confirmation action already succeeded.
   - Banner: `Editing Revision Draft`
   - Copy: `Changes are not active until confirmed`

3. Active authority mode is shown after a successful `Confirm As Active Matrix` or `Confirm Revision` action in this screen.
   - Banner: `Current Active Matrix Authority`
   - Copy: `Used by Project Workbench and Test Record generation`

4. `Confirm As Active Matrix` uses the existing backend endpoint at `/api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}/confirm`.
   - This is a frontend client and UI wiring change only.

5. `Discard Draft Changes` reloads the current persisted draft with `getProjectMatrixDraft(projectId, projectMatrixDraftId)`.
   - If no persisted draft exists, it stays disabled.

6. `Change Selected Groups` is visible but disabled in TASK_266.
   - Consequence copy states that it will adjust current matrix authority configuration and is not a new import.
   - Full reselection behavior requires a later task with source snapshot/session rules.

7. `Change Source Matrix` invokes the existing source document picker.
    - It replaces the ambiguous standalone top-level `Import Matrix` action for normal editing mode.
    - Import dialog title can remain `Import Matrix` when a source document is actually being parsed.
    - If a persisted draft exists, user must pass an explicit confirmation prompt before source change proceeds.
    - Confirmation copy must warn that source change may invalidate current draft edits.

## Task 1: Add Frontend Confirm-As-Active Client

**Files:**

- Modify: `frontend/src/api/client.ts`

- [ ] **Step 1: Add the client function**

Add this function near `confirmProjectMatrixRevisionDraft`:

```ts
export function confirmProjectMatrixDraft(
  projectId: string,
  projectMatrixDraftId: string,
  input: ConfirmProjectMatrixRevisionDraftInput
): Promise<ConfirmedMatrixSnapshot> {
  return requestJson<ConfirmedMatrixSnapshot>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-drafts/${encodeURIComponent(projectMatrixDraftId)}/confirm`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}
```

- [ ] **Step 2: Run a frontend type check through build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

If the build fails because of ordering or export conflicts, keep the function next to the revision confirm client and reuse existing exported types exactly.

## Task 2: Create Clarity Model Helpers

**Files:**

- Create: `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
- Test through: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Create the model helper file**

Create `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts` with:

```ts
export type MatrixWorkspaceMode = "draft" | "activeAuthority" | "revisionDraft";

export type MatrixWorkspaceBannerModel = {
  mode: MatrixWorkspaceMode;
  title: string;
  consequence: string;
  tone: "draft" | "authority" | "revision";
};

export type MatrixActionCopy = {
  saveDraft: string;
  discardDraftChanges: string;
  changeSelectedGroups: string;
  changeSourceMatrix: string;
  confirmAsActiveMatrix: string;
  createRevisionDraft: string;
  confirmRevision: string;
};

export const MATRIX_WORKSPACE_ACTION_COPY: MatrixActionCopy = {
  saveDraft: "Save current edits only. Downstream outputs keep using the active authority until confirmation.",
  discardDraftChanges: "Discard unsaved edits and reload the last saved draft.",
  changeSelectedGroups: "Adjust execution groups for this matrix configuration. This is not a new source import.",
  changeSourceMatrix: "Choose a different source matrix candidate. Existing draft edits may need review.",
  confirmAsActiveMatrix: "Publish this saved draft as the current authority used by Project Workbench and Test Record generation.",
  createRevisionDraft: "Start an editable copy from the active authority. The current active matrix remains in use.",
  confirmRevision: "Replace the active authority with this saved revision draft.",
};

export function buildMatrixWorkspaceBannerModel(input: {
  hasPersistedDraft: boolean;
  baseConfirmedMatrixId: string | null;
  activeAuthorityConfirmed: boolean;
}): MatrixWorkspaceBannerModel {
  if (input.activeAuthorityConfirmed) {
    return {
      mode: "activeAuthority",
      title: "Current Active Matrix Authority",
      consequence: "Used by Project Workbench and Test Record generation",
      tone: "authority",
    };
  }
  if (input.hasPersistedDraft && input.baseConfirmedMatrixId) {
    return {
      mode: "revisionDraft",
      title: "Editing Revision Draft",
      consequence: "Changes are not active until confirmed",
      tone: "revision",
    };
  }
  return {
    mode: "draft",
    title: "Editing Draft",
    consequence: "Not active for downstream outputs",
    tone: "draft",
  };
}
```

- [ ] **Step 2: Keep copy ASCII and exact**

Check that the file contains no em dash characters and no `Import Matrix` phrase inside `changeSelectedGroups`.

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task266 or matrix_editor"
```

Expected before adding TASK_266 static tests:

```text
existing matrix_editor checks pass
```

## Task 3: Add State Banner Component

**Files:**

- Create: `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Create banner component**

Create `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`:

```tsx
import { type ReactElement } from "react";
import { type MatrixWorkspaceBannerModel } from "./matrixWorkspaceClarityModel";

type MatrixWorkspaceStateBannerProps = {
  model: MatrixWorkspaceBannerModel;
};

export function MatrixWorkspaceStateBanner({
  model,
}: MatrixWorkspaceStateBannerProps): ReactElement {
  return (
    <section
      className={`matrix-workspace-state-banner matrix-workspace-state-banner-${model.tone}`}
      aria-label="Matrix workspace state"
    >
      <div>
        <span>Current State</span>
        <strong>{model.title}</strong>
      </div>
      <p>{model.consequence}</p>
    </section>
  );
}
```

- [ ] **Step 2: Add compact banner styles**

Append near existing Matrix Editor styles in `frontend/src/workbench.css`:

```css
.matrix-workspace-state-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  border: 1px solid #cfd9e8;
  border-radius: 8px;
  background: #f5f8fc;
  color: #1d2f48;
}

.matrix-workspace-state-banner div {
  display: flex;
  align-items: baseline;
  gap: 10px;
  min-width: 0;
}

.matrix-workspace-state-banner span {
  color: #65758b;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.matrix-workspace-state-banner strong {
  font-size: 0.95rem;
}

.matrix-workspace-state-banner p {
  margin: 0;
  color: #43546c;
  font-size: 0.85rem;
}

.matrix-workspace-state-banner-authority {
  border-color: #bdd9cf;
  background: #eef9f4;
}

.matrix-workspace-state-banner-revision {
  border-color: #d8d0ee;
  background: #f5f2fb;
}
```

- [ ] **Step 3: Run build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 4: Add Action Groups Component

**Files:**

- Create: `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Create action groups component**

Create `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`:

```tsx
import { type ReactElement } from "react";
import { MATRIX_WORKSPACE_ACTION_COPY } from "./matrixWorkspaceClarityModel";

type MatrixActionButtonProps = {
  label: string;
  busyLabel?: string;
  consequence: string;
  disabled: boolean;
  disabledReason: string;
  isBusy?: boolean;
  primary?: boolean;
  onClick: () => void;
};

function MatrixActionButton({
  label,
  busyLabel,
  consequence,
  disabled,
  disabledReason,
  isBusy = false,
  primary = false,
  onClick,
}: MatrixActionButtonProps): ReactElement {
  return (
    <div className="matrix-workspace-action-item">
      <button
        className={primary ? "matrix-editor-primary-action" : undefined}
        type="button"
        disabled={disabled}
        title={disabled ? disabledReason : consequence}
        onClick={onClick}
      >
        {isBusy && busyLabel ? busyLabel : label}
      </button>
      <p>{consequence}</p>
    </div>
  );
}

type MatrixWorkspaceActionGroupsProps = {
  saveDraftDisabled: boolean;
  saveDraftDisabledReason: string;
  saveDraftBusy: boolean;
  discardDraftDisabled: boolean;
  discardDraftDisabledReason: string;
  confirmAsActiveDisabled: boolean;
  confirmAsActiveDisabledReason: string;
  confirmAsActiveBusy: boolean;
  createRevisionDisabled: boolean;
  createRevisionDisabledReason: string;
  createRevisionBusy: boolean;
  confirmRevisionDisabled: boolean;
  confirmRevisionDisabledReason: string;
  confirmRevisionBusy: boolean;
  showConfirmAsActive: boolean;
  showConfirmRevision: boolean;
  onSaveDraft: () => void;
  onDiscardDraftChanges: () => void;
  onChangeSourceMatrix: () => void;
  onConfirmAsActiveMatrix: () => void;
  onCreateRevisionDraft: () => void;
  onConfirmRevision: () => void;
};

export function MatrixWorkspaceActionGroups({
  saveDraftDisabled,
  saveDraftDisabledReason,
  saveDraftBusy,
  discardDraftDisabled,
  discardDraftDisabledReason,
  confirmAsActiveDisabled,
  confirmAsActiveDisabledReason,
  confirmAsActiveBusy,
  createRevisionDisabled,
  createRevisionDisabledReason,
  createRevisionBusy,
  confirmRevisionDisabled,
  confirmRevisionDisabledReason,
  confirmRevisionBusy,
  showConfirmAsActive,
  showConfirmRevision,
  onSaveDraft,
  onDiscardDraftChanges,
  onChangeSourceMatrix,
  onConfirmAsActiveMatrix,
  onCreateRevisionDraft,
  onConfirmRevision,
}: MatrixWorkspaceActionGroupsProps): ReactElement {
  return (
    <section className="matrix-workspace-action-groups" aria-label="Matrix workspace actions">
      <div className="matrix-workspace-action-group" aria-label="Draft Actions">
        <h3>Draft Actions</h3>
        <MatrixActionButton
          label="Save Draft"
          busyLabel="Saving..."
          consequence={MATRIX_WORKSPACE_ACTION_COPY.saveDraft}
          disabled={saveDraftDisabled}
          disabledReason={saveDraftDisabledReason}
          isBusy={saveDraftBusy}
          onClick={onSaveDraft}
        />
        <MatrixActionButton
          label="Discard Draft Changes"
          consequence={MATRIX_WORKSPACE_ACTION_COPY.discardDraftChanges}
          disabled={discardDraftDisabled}
          disabledReason={discardDraftDisabledReason}
          onClick={onDiscardDraftChanges}
        />
        <MatrixActionButton
          label="Change Selected Groups"
          consequence={MATRIX_WORKSPACE_ACTION_COPY.changeSelectedGroups}
          disabled={true}
          disabledReason="Group reselection for a persisted matrix requires a follow-up source lineage task."
          onClick={() => undefined}
        />
        <MatrixActionButton
          label="Change Source Matrix"
          consequence={MATRIX_WORKSPACE_ACTION_COPY.changeSourceMatrix}
          disabled={false}
          disabledReason=""
          onClick={onChangeSourceMatrix}
        />
      </div>

      <div className="matrix-workspace-action-group" aria-label="Authority Actions">
        <h3>Authority Actions</h3>
        {showConfirmAsActive ? (
          <MatrixActionButton
            label="Confirm As Active Matrix"
            busyLabel="Confirming..."
            consequence={MATRIX_WORKSPACE_ACTION_COPY.confirmAsActiveMatrix}
            disabled={confirmAsActiveDisabled}
            disabledReason={confirmAsActiveDisabledReason}
            isBusy={confirmAsActiveBusy}
            primary
            onClick={onConfirmAsActiveMatrix}
          />
        ) : null}
        <MatrixActionButton
          label="Create Revision Draft"
          busyLabel="Creating..."
          consequence={MATRIX_WORKSPACE_ACTION_COPY.createRevisionDraft}
          disabled={createRevisionDisabled}
          disabledReason={createRevisionDisabledReason}
          isBusy={createRevisionBusy}
          onClick={onCreateRevisionDraft}
        />
        {showConfirmRevision ? (
          <MatrixActionButton
            label="Confirm Revision"
            busyLabel="Confirming..."
            consequence={MATRIX_WORKSPACE_ACTION_COPY.confirmRevision}
            disabled={confirmRevisionDisabled}
            disabledReason={confirmRevisionDisabledReason}
            isBusy={confirmRevisionBusy}
            primary
            onClick={onConfirmRevision}
          />
        ) : null}
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Add action group CSS**

Append near Matrix Editor action styles in `frontend/src/workbench.css`:

```css
.matrix-workspace-action-groups {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.matrix-workspace-action-group {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 12px;
  border: 1px solid #d6dfeb;
  border-radius: 8px;
  background: #f8fafc;
}

.matrix-workspace-action-group h3 {
  grid-column: 1 / -1;
  margin: 0;
  color: #32435a;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
}

.matrix-workspace-action-item {
  min-width: 0;
}

.matrix-workspace-action-item button {
  width: 100%;
}

.matrix-workspace-action-item p {
  margin: 5px 0 0;
  color: #68788d;
  font-size: 0.74rem;
  line-height: 1.35;
}
```

- [ ] **Step 3: Run build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 5: Integrate Banner And Action Groups In MatrixEditorWorkspace

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`

- [ ] **Step 1: Import new client and components**

Update imports:

```ts
import {
  commitMatrixImport,
  confirmProjectMatrixDraft,
  confirmProjectMatrixRevisionDraft,
  createMatrixRevisionDraft,
  getProjectMatrixDraft,
  listProjectMatrixDrafts,
  matrixPreviewPdfUrl,
  previewProjectTestPlanMatrixFromUpload,
  saveProjectMatrixDraft,
  type ConfirmedMatrixSnapshot,
  type MatrixPreviewResponse,
  type MatrixImportCommitResponse,
  type ProjectMatrixDraft,
  type ProjectMatrixDraftSaveRequest,
} from "../../api/client";
import { MatrixWorkspaceActionGroups } from "./MatrixWorkspaceActionGroups";
import { MatrixWorkspaceStateBanner } from "./MatrixWorkspaceStateBanner";
import { buildMatrixWorkspaceBannerModel } from "./matrixWorkspaceClarityModel";
```

- [ ] **Step 2: Add confirm-as-active state**

Add state near existing revision action state:

```ts
const [confirmActiveState, setConfirmActiveState] = useState<MatrixRevisionActionState>("idle");
const [confirmActiveMessage, setConfirmActiveMessage] = useState<string>("");
const [activeAuthorityConfirmed, setActiveAuthorityConfirmed] = useState(false);
```

Update `applyDraftSnapshotToEditor` to reset active confirmation when a draft is loaded:

```ts
setActiveAuthorityConfirmed(false);
setConfirmActiveState("idle");
setConfirmActiveMessage("");
```

- [ ] **Step 3: Add banner model and disabled reasons**

Add near existing guard derivations:

```ts
const workspaceBannerModel = buildMatrixWorkspaceBannerModel({
  hasPersistedDraft,
  baseConfirmedMatrixId: projectMatrixDraftBaseConfirmedMatrixId,
  activeAuthorityConfirmed,
});
const isRevisionDraft = projectMatrixDraftBaseConfirmedMatrixId !== null && !activeAuthorityConfirmed;
const isActiveAuthorityView = activeAuthorityConfirmed;
const isAnyMatrixActionBusy =
  saveState === "saving" ||
  createRevisionState === "loading" ||
  confirmRevisionState === "loading" ||
  confirmActiveState === "loading";
const saveDraftDisabledReason =
  !hasPersistedDraft || projectMatrixDraftId === null
    ? "No persisted draft target."
    : isAnyMatrixActionBusy
      ? "Action in progress."
      : hasMatrixValidationError
        ? groupNameErrorMessage || stepTokenErrorMessage
        : hasUnsavedChanges
          ? ""
          : "No unsaved changes.";
const discardDraftDisabledReason =
  !hasPersistedDraft || projectMatrixDraftId === null
    ? "No persisted draft target."
    : !hasUnsavedChanges
      ? "No unsaved changes."
      : isAnyMatrixActionBusy
        ? "Action in progress."
        : "";
const confirmAsActiveDisabledReason =
  !hasPersistedDraft || projectMatrixDraftId === null
    ? "No persisted matrix draft target."
    : isRevisionDraft
      ? "Use Confirm Revision for a revision draft."
      : isActiveAuthorityView
        ? "This matrix is already active."
        : hasUnsavedChanges
          ? "Save changes before confirming as active."
          : hasMatrixValidationError
            ? groupNameErrorMessage || stepTokenErrorMessage
            : isAnyMatrixActionBusy
              ? "Action in progress."
              : "";
const canConfirmAsActiveMatrix = confirmAsActiveDisabledReason.length === 0;
```

- [ ] **Step 4: Add discard handler**

Add near `onSaveDraft`:

```ts
const onDiscardDraftChanges = async (): Promise<void> => {
  if (!projectMatrixDraftId) {
    setSaveState("error");
    setSaveMessage("No persisted matrix draft target.");
    return;
  }
  setSaveState("saving");
  setSaveMessage("Reloading saved draft...");
  try {
    const draft = await getProjectMatrixDraft(projectId, projectMatrixDraftId);
    applyDraftSnapshotToEditor(draft);
    setSaveState("idle");
    setSaveMessage("Draft changes discarded.");
  } catch (error) {
    setSaveState("error");
    setSaveMessage(parseRequestError(error, "Discard draft changes failed."));
  }
};
```

- [ ] **Step 5: Add confirm-as-active handler**

Add near `onConfirmRevision`:

```ts
const onConfirmAsActiveMatrix = async (): Promise<void> => {
  if (!canConfirmAsActiveMatrix || !projectMatrixDraftId) {
    if (confirmAsActiveDisabledReason) {
      setConfirmActiveMessage(confirmAsActiveDisabledReason);
    }
    return;
  }
  setConfirmActiveState("loading");
  setConfirmActiveMessage("Confirming active matrix...");
  try {
    const confirmed = await confirmProjectMatrixDraft(projectId, projectMatrixDraftId, {
      confirmed_by: MVP_REVISION_CONFIRMED_BY,
    });
    setConfirmActiveState("success");
    setActiveAuthorityConfirmed(true);
    setConfirmActiveMessage(buildRevisionConfirmedMessage(confirmed));
  } catch (error) {
    setConfirmActiveState("error");
    setConfirmActiveMessage(parseRequestError(error, "Confirm active matrix failed."));
  }
};
```

- [ ] **Step 6: Update revision confirmation success to set active authority mode**

Inside existing `onConfirmRevision`, after successful confirmation:

```ts
setActiveAuthorityConfirmed(true);
```

- [ ] **Step 7: Replace the flat target action block**

Replace the current non-selection `matrix-editor-target-actions` button trio with a compact status marker only:

```tsx
{showImportSelectionMode ? (
  <div className="matrix-editor-target-actions">
    <span className="matrix-editor-selection-mode-pill">Import selection in progress</span>
  </div>
) : null}
```

Then render below the target header and above save/status messages:

```tsx
<MatrixWorkspaceStateBanner model={workspaceBannerModel} />
{!showImportSelectionMode ? (
  <MatrixWorkspaceActionGroups
    saveDraftDisabled={!canSave}
    saveDraftDisabledReason={saveDraftDisabledReason}
    saveDraftBusy={saveState === "saving"}
    discardDraftDisabled={!hasUnsavedChanges || discardDraftDisabledReason.length > 0}
    discardDraftDisabledReason={discardDraftDisabledReason}
    confirmAsActiveDisabled={!canConfirmAsActiveMatrix}
    confirmAsActiveDisabledReason={confirmAsActiveDisabledReason}
    confirmAsActiveBusy={confirmActiveState === "loading"}
    createRevisionDisabled={!canCreateRevisionDraftWithGuards}
    createRevisionDisabledReason={createRevisionDisabledReason || "Create revision is currently unavailable."}
    createRevisionBusy={createRevisionState === "loading"}
    confirmRevisionDisabled={!confirmRevisionGuard.canConfirm}
    confirmRevisionDisabledReason={confirmRevisionGuard.reason}
    confirmRevisionBusy={confirmRevisionState === "loading"}
    showConfirmAsActive={!isRevisionDraft}
    showConfirmRevision={isRevisionDraft}
    onSaveDraft={() => void onSaveDraft()}
    onDiscardDraftChanges={() => void onDiscardDraftChanges()}
    onChangeSourceMatrix={() => void onChangeSourceMatrix()}
    onConfirmAsActiveMatrix={() => void onConfirmAsActiveMatrix()}
    onCreateRevisionDraft={() => void onCreateRevisionDraft()}
    onConfirmRevision={() => void onConfirmRevision()}
  />
) : null}
```

- [ ] **Step 8: Include confirm active messages in status area**

Update status rendering:

```tsx
{(createRevisionMessage || confirmRevisionMessage || confirmActiveMessage) && (
  <section className="matrix-editor-save-status">
    {confirmRevisionMessage || confirmActiveMessage || createRevisionMessage}
  </section>
)}
```

- [ ] **Step 9: Remove the normal-mode standalone import button**

Delete this standalone button from the normal-mode action bar:

```tsx
<button className="matrix-editor-import-primary-button" type="button" onClick={openChooseDocx}>{importingPreview ? "Parsing..." : "Import Matrix"}</button>
```

Keep the hidden file input, `Append Matrix (Future)`, undo, and import dialog behavior intact.

- [ ] **Step 9A: Add source-change confirmation guard**

Add a dedicated handler:

```ts
const onChangeSourceMatrix = (): void => {
  if (hasPersistedDraft) {
    const warning = hasUnsavedChanges
      ? "Changing the source matrix may invalidate current draft edits. Unsaved edits will be lost. Continue?"
      : "Changing the source matrix may invalidate current draft edits. Continue?";
    if (!window.confirm(warning)) {
      return;
    }
  }
  openChooseDocx();
};
```

Use this handler in `MatrixWorkspaceActionGroups` instead of binding `openChooseDocx` directly.

- [ ] **Step 10: Run build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 6: Update React Tests

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add API mock**

Add `confirmProjectMatrixDraft` to `apiMocks` and mocked client export.

```ts
confirmProjectMatrixDraft: vi.fn(),
```

In `beforeEach`, add:

```ts
apiMocks.confirmProjectMatrixDraft.mockResolvedValue({
  version: {
    confirmed_matrix_id: "confirmed-1",
    project_id: "P1",
    project_matrix_draft_id: "draft-1",
    source_import_id: "source-1",
    source_snapshot_id: "snapshot-1",
    confirmed_revision: 1,
    is_active_authority: true,
    status: "active",
    confirmed_by: "connlab-operator",
    confirmed_at: "2026-05-23T00:02:00Z",
    superseded_by_confirmed_matrix_id: null,
    superseded_at: null,
    superseded_reason: null,
  },
  groups: [],
  rows: [],
  cells: [],
});
```

- [ ] **Step 2: Update existing save button assertions**

Replace queries for:

```ts
screen.getByRole("button", { name: "Save" })
```

with:

```ts
screen.getByRole("button", { name: "Save Draft" })
```

- [ ] **Step 3: Update revision action label assertions**

Replace:

```ts
screen.getByRole("button", { name: "Create revision draft" })
screen.getByRole("button", { name: "Confirm revision" })
```

with:

```ts
screen.getByRole("button", { name: "Create Revision Draft" })
screen.getByRole("button", { name: "Confirm Revision" })
```

- [ ] **Step 4: Add banner and action grouping test**

Add a test:

```ts
it("shows revision draft state and separates draft and authority actions", async () => {
  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

  await waitFor(() => {
    expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
  });

  expect(screen.getByLabelText("Matrix workspace state").textContent).toContain("Editing Revision Draft");
  expect(screen.getByText("Changes are not active until confirmed")).toBeTruthy();
  expect(screen.getByLabelText("Draft Actions")).toBeTruthy();
  expect(screen.getByLabelText("Authority Actions")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Save Draft" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Discard Draft Changes" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Change Selected Groups" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Change Source Matrix" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Create Revision Draft" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Confirm Revision" })).toBeTruthy();
  expect(screen.getByText("Adjust execution groups for this matrix configuration. This is not a new source import.")).toBeTruthy();
});
```

- [ ] **Step 5: Add confirm-as-active test for non-revision draft**

Create a non-revision draft fixture by returning `base_confirmed_matrix_id: null`, then add:

```ts
it("confirms a normal draft as active authority", async () => {
  apiMocks.listProjectMatrixDrafts.mockResolvedValueOnce([
    {
      project_matrix_draft_id: "draft-1",
      project_id: "P1",
      source_import_id: null,
      source_snapshot_id: "snapshot-1",
      base_confirmed_matrix_id: null,
      status: "draft",
      created_at: "2026-05-23T00:00:00Z",
      updated_at: "2026-05-23T00:00:00Z",
    },
  ]);
  apiMocks.getProjectMatrixDraft.mockResolvedValueOnce({
    ...buildRevisionDraft(),
    record: {
      ...buildRevisionDraft().record,
      base_confirmed_matrix_id: null,
    },
  });

  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

  await waitFor(() => {
    expect(screen.getByText("Editing Draft")).toBeTruthy();
  });

  fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));

  await waitFor(() => {
    expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(1);
    expect(screen.getByText("Current Active Matrix Authority")).toBeTruthy();
    expect(screen.getByText("Used by Project Workbench and Test Record generation")).toBeTruthy();
  });
});
```

- [ ] **Step 6: Preserve import selection mode hiding**

Update existing import-selection test to assert:

```ts
expect(screen.queryByRole("button", { name: "Save Draft" })).toBeNull();
expect(screen.queryByLabelText("Draft Actions")).toBeNull();
expect(screen.queryByLabelText("Authority Actions")).toBeNull();
```

- [ ] **Step 7: Run focused tests**

Run:

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

Expected:

```text
all MatrixEditorWorkspace tests pass
```

## Task 7: Add Static Frontend Guardrails

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_266 static test**

Add:

```python
def test_task266_matrix_workspace_navigation_and_state_clarity_is_wired() -> None:
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    action_groups_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixWorkspaceActionGroups.tsx"
    ).read_text(encoding="utf-8")
    banner_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixWorkspaceStateBanner.tsx"
    ).read_text(encoding="utf-8")
    clarity_model_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "matrixWorkspaceClarityModel.ts"
    ).read_text(encoding="utf-8")
    api_client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(encoding="utf-8")
    workbench_css = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    for required in [
        "MatrixWorkspaceStateBanner",
        "MatrixWorkspaceActionGroups",
        "buildMatrixWorkspaceBannerModel",
        "confirmProjectMatrixDraft",
    ]:
        assert required in matrix_editor_source or required in api_client_source

    for required_copy in [
        "Editing Draft",
        "Not active for downstream outputs",
        "Current Active Matrix Authority",
        "Used by Project Workbench and Test Record generation",
        "Editing Revision Draft",
        "Changes are not active until confirmed",
        "Save Draft",
        "Discard Draft Changes",
        "Change Selected Groups",
        "Change Source Matrix",
        "Confirm As Active Matrix",
        "Create Revision Draft",
        "Confirm Revision",
    ]:
        assert (
            required_copy in matrix_editor_source
            or required_copy in action_groups_source
            or required_copy in banner_source
            or required_copy in clarity_model_source
        )

    assert "This is not a new source import" in clarity_model_source
    assert "Draft Actions" in action_groups_source
    assert "Authority Actions" in action_groups_source
    assert "matrix-workspace-state-banner" in workbench_css
    assert "matrix-workspace-action-groups" in workbench_css
```

- [ ] **Step 2: Record backend no-touch guard**

Do not add a git-dependent pytest check for changed files. Use the final `git diff --name-only` review step in Task 8 to verify TASK_266 did not introduce backend changes.

- [ ] **Step 3: Run static tests**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task266 or matrix_editor"
```

Expected:

```text
TASK_266 and Matrix Editor static checks pass
```

## Task 8: Final Verification And Documentation Sync

**Files:**

- Modify after passing validation: `tasks/TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY.md`
- Modify after passing validation: `docs/task_board.md`

- [ ] **Step 1: Run full TASK_266 verification**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task266 or matrix_editor"
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

Expected changed implementation files for TASK_266 are limited to:

```text
docs/task_266_matrix_workspace_navigation_and_state_clarity_plan.md
docs/task_board.md
tasks/TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY.md
frontend/src/api/client.ts
frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx
frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx
frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx
frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts
frontend/src/workbench.css
tests/unit/test_frontend_shell_files.py
```

If unrelated pre-existing files are already dirty, do not revert them. Only verify TASK_266 did not introduce backend changes.

- [ ] **Step 3: Update task file to complete**

After validation passes, update `tasks/TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY.md`:

```markdown
## Status

Complete on 2026-05-24. Matrix Workspace navigation, state banner, action grouping, and consequence copy are implemented and verified.
```

Also add a short validation summary under the task file's validation section with the exact commands and pass results.

- [ ] **Step 4: Update task board**

Update `docs/task_board.md`:

```markdown
> Status: ... + TASK_266 complete
> Last Updated: 2026-05-24
> Current Active Task: none (`TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY` complete; awaiting next approved task).
```

Add a TASK_266 completion note:

```markdown
- `TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY` is complete. Matrix Workspace now shows explicit Draft / Active Authority / Revision Draft state, separates Draft Actions from Authority Actions, and adds consequence copy for key operations while preserving TASK_261-TASK_265 smoke-flow behavior.
- Deliverables: `frontend/src/api/client.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`, `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`, `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/workbench.css`, `tests/unit/test_frontend_shell_files.py`, `tasks/TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY.md`, and `docs/task_266_matrix_workspace_navigation_and_state_clarity_plan.md`.
- Validation: record the exact passing commands.
- Scope boundary held: no backend authority refactor, API/schema change, permission system, LLCR runtime persistence, report engine, AI recommendation, Test Record Word generation, StepInstance, or multi-matrix merge implementation was introduced.
```

## Review Checklist Before Implementation

- [ ] The plan changes only frontend workflow clarity plus frontend API client wiring to an existing endpoint.
- [ ] `Change Selected Groups` is not described as `Import Matrix`.
- [ ] `Change Selected Groups` remains disabled in TASK_266 unless a later approved task implements persisted reselection.
- [ ] `Change Source Matrix` is the source replacement entry point.
- [ ] `Save Draft`, `Confirm As Active Matrix`, `Create Revision Draft`, and `Confirm Revision` have visible consequence copy.
- [ ] Import selection mode still hides Draft Actions and Authority Actions.
- [ ] No backend files are part of the implementation tasks.

## Execution Handoff

After this plan is approved, implement with `superpowers:executing-plans` in this session. Execute task by task, run each verification command at the checkpoint where it is listed, and stop after TASK_266 completion. Do not proceed to TASK_267 or any follow-up task.
