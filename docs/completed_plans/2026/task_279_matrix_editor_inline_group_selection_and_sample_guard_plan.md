# TASK_279 Matrix Editor Inline Group Selection And Sample Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the separate Matrix group selection page with inline group inclusion controls in the Matrix Editor table, and block Matrix confirmation when checked groups have invalid sample quantity.

**Architecture:** Matrix Editor remains a temporary session UI. Source Matrix import creates the editable Matrix draft directly; inline group checkboxes control `is_selected` in the current editor state. Frontend pre-validation highlights invalid checked-group sample fields, while backend session and legacy revision confirmation share one selected-group sample quantity guard.

Import dialog scope lock in TASK_279:

- `Replace` is the only active import action.
- `Append` remains disabled/non-operational and must not call import/commit APIs.

**Tech Stack:** React + TypeScript + Vitest for frontend; FastAPI + Python application services + pytest for backend.

---

## Current Phase And Task Gate

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task before approval: TASK_279 is the active planned task on the board and is awaiting user approval.
- Allowed task after approval: `TASK_279_MATRIX_EDITOR_INLINE_GROUP_SELECTION_AND_SAMPLE_GUARD`.
- Allowed reason: TASK_278 is complete; this task is a controlled Matrix Editor follow-up based on smoke feedback and user-approved product direction.

Do not implement this plan until the user explicitly approves TASK_279 execution and `docs/task_board.md` marks TASK_279 as current planned/active.

## Step 1 - Task Understanding

### Goal

Make Matrix Editor group selection part of the editor table itself. Users should import a source Matrix into the editor, check or uncheck group columns inline, optionally hide unchecked groups and unused rows, then confirm the current editor content.

### Inputs

- Active Confirmed Matrix session seed from `GET /api/projects/{project_id}/matrix-editor/session`.
- Source Matrix preview payload from `Import Matrix`.
- Current Matrix Editor local state:
  - `groupColumns`
  - `editableRows`
  - `sampleValues`
  - `sampleMergeNotes`
  - `importPreview`
  - source lineage IDs

### Outputs

- Frontend confirm payload where `groups[*].is_selected` reflects header checkbox state.
- Backend confirmed Matrix containing only selected groups.
- Disabled `Confirm Matrix` when a selected group sample quantity is blank or has no digit.
- Red invalid styling on invalid selected group sample quantity inputs.

### Modules

- Matrix Editor UI and tests.
- Matrix Editor action toolbar.
- Matrix import/session model helpers.
- Backend Matrix Editor session confirmation service.
- Backend Matrix revision flow service.
- Static frontend guard tests.

### Not Allowed

- Do not implement StepInstance, image/evidence persistence, report/fee/Test Record generation, permissions, AI, or multi-user scope.
- Do not add new database tables.
- Do not expose old revision/draft concepts in UI.
- Do not keep the separate `Selected Groups` page as a visible route or modal.

## File Structure

### Frontend

- Modify `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Remove active `MatrixImportSelectionMode` flow.
  - Add inline group checkbox state updates.
  - Add selected-only filter state.
  - Add selected-group sample guard.
  - Import source Matrix directly into editor state after import confirmation.

- Modify `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
  - Remove `Selected Groups` button and props.
  - Keep `Import Matrix`, `Cancel`, `Confirm Matrix`.

- Modify or delete `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`
  - Remove from active UI flow.
  - Delete only if no imports remain and tests/static guards are updated.

- Modify `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
  - Remove `changeSelectedGroupsDisabled` model if no longer used.
  - Keep import-source availability helpers only if still needed by Import Matrix.

- Modify `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Replace `Selected Groups` tests with inline group checkbox/filter/sample guard tests.

- Modify `frontend/src/workbench.css`
  - Add group header checkbox styling.
  - Add selected-only filter styling.
  - Add invalid sample input styling using the existing red field language.

- Modify `tests/unit/test_frontend_shell_files.py`
  - Add TASK_279 static guard.
  - Remove/relax older static assertions that require `Selected Groups` or `MatrixImportSelectionMode`.

### Backend

- Create `backend/application/matrix_sample_quantity_guard.py`
  - Shared application helper for selected-group sample quantity validation.
  - This avoids duplicate rules between session confirm and legacy revision confirm.

- Modify `backend/application/matrix_editor_session_service.py`
  - Call shared sample guard before no-change comparison and publishing.
  - Raise `MatrixEditorSessionError` with business-readable message when selected group sample text is invalid.

- Modify `backend/application/matrix_revision_flow_service.py`
  - Replace inline nonblank selected sample check with shared digit-containing guard.

- Modify backend tests:
  - `tests/unit/test_matrix_editor_session_service.py`
  - `tests/unit/test_matrix_revision_flow_service.py`
  - `tests/integration/test_matrix_editor_session_api.py`

## Data And Function Design

### Shared Backend Guard

Create `backend/application/matrix_sample_quantity_guard.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol


class SampleQuantityGroup(Protocol):
    group_label: str
    group_key: str
    is_selected: bool
    sample_quantity_expression: str | None


@dataclass(frozen=True, slots=True)
class SampleQuantityViolation:
    group_label: str
    group_key: str


_DIGIT_PATTERN = re.compile(r"\d")


def find_selected_sample_quantity_violations(
    groups: tuple[SampleQuantityGroup, ...],
) -> tuple[SampleQuantityViolation, ...]:
    violations: list[SampleQuantityViolation] = []
    for group in groups:
        if not bool(group.is_selected):
            continue
        expression = (group.sample_quantity_expression or "").strip()
        if not expression or _DIGIT_PATTERN.search(expression) is None:
            violations.append(
                SampleQuantityViolation(
                    group_label=group.group_label.strip() or group.group_key.strip(),
                    group_key=group.group_key.strip(),
                )
            )
    return tuple(violations)


def format_sample_quantity_violation_message(
    violations: tuple[SampleQuantityViolation, ...],
) -> str:
    labels = ", ".join(item.group_label for item in violations)
    return f"Sample quantity is required for selected groups: {labels}."
```

### Frontend Guard

Add local helper in `MatrixEditorWorkspace.tsx`:

```ts
function sampleQuantityHasDigit(value: string | null | undefined): boolean {
  return /\d/.test((value ?? "").trim());
}

function buildInvalidSelectedSampleGroupIds(
  groups: GroupColumn[],
  samples: Record<string, string>
): Set<string> {
  return new Set(
    groups
      .filter((group) => group.isSelected)
      .filter((group) => !sampleQuantityHasDigit(samples[group.id]))
      .map((group) => group.id)
  );
}
```

### Inline Group Toggle

Add local handler in `MatrixEditorWorkspace.tsx`:

```ts
const toggleGroupIncluded = (groupId: string, included: boolean): void => {
  markUnsaved();
  setGroupColumns((previous) =>
    previous.map((group) =>
      group.id === groupId ? { ...group, isSelected: included } : group
    )
  );
  setSelectedGroupId(groupId);
  setSelectedRowId(null);
};
```

### Selected-Only Filter

Add state:

```ts
const [showSelectedGroupsOnly, setShowSelectedGroupsOnly] = useState(false);
```

Derived values:

```ts
const visibleGroupColumns = showSelectedGroupsOnly
  ? groupColumns.filter((group) => group.isSelected)
  : groupColumns;

const visibleEditableRows = showSelectedGroupsOnly
  ? editableRows.filter((row) =>
      visibleGroupColumns.some((group) => (row.groups[group.id] ?? "").trim().length > 0)
    )
  : editableRows;
```

Implementation must preserve row indexes for labels. Use the original `editableRows` index when rendering visible rows:

```ts
const visibleRows = editableRows
  .map((row, rowIndex) => ({ row, rowIndex }))
  .filter(({ row }) => {
    if (!showSelectedGroupsOnly) {
      return true;
    }
    return visibleGroupColumns.some(
      (group) => (row.groups[group.id] ?? "").trim().length > 0
    );
  });
```

## Implementation Tasks

### Task 1: Backend Shared Sample Quantity Guard

**Files:**

- Create: `backend/application/matrix_sample_quantity_guard.py`
- Modify: `tests/unit/test_matrix_editor_session_service.py`
- Modify: `tests/unit/test_matrix_revision_flow_service.py`

- [ ] **Step 1: Add failing backend unit tests**

Add to `tests/unit/test_matrix_editor_session_service.py`:

```python
def test_confirm_session_rejects_selected_group_sample_without_digit() -> None:
    active = _build_active_snapshot()
    service = _service(active=active, source_snapshot=None)
    command = MatrixEditorSessionConfirmCommand(
        project_id="P1",
        expected_active_confirmed_matrix_id="cmv-1",
        expected_active_confirmed_revision=1,
        source_document_path=None,
        source_document_name=None,
        source_format=None,
        source_import_id="smi-1",
        source_snapshot_id="sms-1",
        confirmed_by="operator",
        groups=(
            MatrixEditorSessionGroup(
                draft_group_id="dg-1",
                source_group_snapshot_id="sg-1",
                group_order=1,
                group_key="g1",
                group_label="1",
                is_selected=True,
                sample_quantity_expression="sample only",
                sample_note=None,
            ),
        ),
        rows=(
            MatrixEditorSessionRow(
                draft_row_id="dr-1",
                source_row_snapshot_id="sr-1",
                row_order=1,
                test_item="Visual Examination",
                source_section="1.1",
                method="EIA-364-18B",
                condition="10x min magnification",
                requirement="No detrimental condition",
                is_sample_row=False,
            ),
        ),
        cells=(
            MatrixEditorSessionCell(
                draft_row_id="dr-1",
                draft_group_id="dg-1",
                cell_value="1",
            ),
        ),
    )

    with pytest.raises(MatrixEditorSessionError) as exc:
        service.confirm_session(command)

    assert "Sample quantity is required for selected groups: 1." in str(exc.value)
```

Add to `tests/unit/test_matrix_revision_flow_service.py` a focused test using existing fixtures in that file:

```python
def test_confirm_revision_rejects_selected_group_sample_without_digit() -> None:
    service, stores = _service()
    revision_draft = service.create_revision_draft(
        CreateMatrixRevisionDraftCommand(project_id="P1")
    )
    modified_groups = list(revision_draft.groups)
    modified_groups[0] = modified_groups[0].__class__(
        draft_group_id=modified_groups[0].draft_group_id,
        project_matrix_draft_id=modified_groups[0].project_matrix_draft_id,
        source_group_snapshot_id=modified_groups[0].source_group_snapshot_id,
        group_order=modified_groups[0].group_order,
        group_key=modified_groups[0].group_key,
        group_label=modified_groups[0].group_label,
        is_selected=True,
        sample_quantity_expression="sample only",
        sample_note=modified_groups[0].sample_note,
    )
    revision_draft = revision_draft.__class__(
        record=revision_draft.record,
        groups=tuple(modified_groups),
        rows=revision_draft.rows,
        cells=revision_draft.cells,
    )
    stores.draft_store.snapshot_by_id[
        revision_draft.record.project_matrix_draft_id
    ] = revision_draft

    with pytest.raises(MatrixRevisionFlowError) as exc:
        service.confirm_revision_draft(
            ConfirmMatrixRevisionDraftCommand(
                project_id="P1",
                project_matrix_draft_id=revision_draft.record.project_matrix_draft_id,
                confirmed_by="operator",
            )
        )

    assert "Sample quantity is required for selected groups: G1." in str(exc.value)
```

When implementing, replace this sketch with concrete fixture calls already present in `test_matrix_revision_flow_service.py`.

- [ ] **Step 2: Run backend tests and verify failure**

Run:

```powershell
py -m pytest tests\unit\test_matrix_editor_session_service.py tests\unit\test_matrix_revision_flow_service.py -q
```

Expected: failing tests because shared guard is not implemented/called yet.

- [ ] **Step 3: Create shared guard**

Create `backend/application/matrix_sample_quantity_guard.py` with the exact guard shown in **Data And Function Design**.

- [ ] **Step 4: Wire guard into Matrix Editor session confirm**

In `backend/application/matrix_editor_session_service.py`, import:

```python
from backend.application.matrix_sample_quantity_guard import (
    find_selected_sample_quantity_violations,
    format_sample_quantity_violation_message,
)
```

In `confirm_session`, after selected group existence and before `_has_any_step_tokens`, add:

```python
sample_violations = find_selected_sample_quantity_violations(command.groups)
if sample_violations:
    raise MatrixEditorSessionError(
        format_sample_quantity_violation_message(sample_violations)
    )
```

- [ ] **Step 5: Wire guard into legacy revision flow**

In `backend/application/matrix_revision_flow_service.py`, replace the inline selected-group sample nonblank check:

```python
if not (group.sample_quantity_expression or "").strip():
    raise MatrixRevisionFlowError(
        "Selected groups must have nonblank sample quantity expression."
    )
```

with:

```python
sample_violations = find_selected_sample_quantity_violations(selected_groups)
if sample_violations:
    raise MatrixRevisionFlowError(
        format_sample_quantity_violation_message(sample_violations)
    )
```

- [ ] **Step 6: Run backend tests**

Run:

```powershell
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\unit\test_matrix_revision_flow_service.py -q
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
```

Expected: all pass.

### Task 2: Remove Selected Groups Toolbar Action And Page Flow

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify or delete: `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`
- Modify: `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
- Test: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add failing frontend toolbar test**

In `MatrixEditorWorkspace.test.tsx`, replace the old `Selected Groups` availability tests with:

```ts
it("does not expose a separate Selected Groups action", async () => {
  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

  await screen.findByRole("button", { name: "Confirm Matrix" });

  expect(screen.queryByRole("button", { name: "Selected Groups" })).toBeNull();
  expect(screen.getByRole("button", { name: "Import Matrix" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Cancel" })).toBeTruthy();
});
```

- [ ] **Step 2: Run frontend test and verify failure**

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
```

Expected: fail because `Selected Groups` is still rendered.

- [ ] **Step 3: Remove toolbar props and button**

In `MatrixWorkspaceActionGroups.tsx`, remove:

```ts
changeSelectedGroupsDisabled: boolean;
changeSelectedGroupsDisabledReason: string;
onChangeSelectedGroups: () => void;
```

Remove the `Selected Groups` button. Keep only:

```tsx
<button type="button" onClick={onChangeSourceMatrix}>
  Import Matrix
</button>
```

Keep import dialog `Append` as disabled placeholder only:

```tsx
<button type="button" disabled title="Append Matrix is out of scope in TASK_279.">
  Append
</button>
```

- [ ] **Step 4: Remove active selection-mode render path**

In `MatrixEditorWorkspace.tsx`:

- remove `MatrixImportSelectionMode` import
- remove `showImportSelectionMode` rendering branches
- remove `onChangeSelectedGroups`
- remove `onCommitImportedGroups`
- remove `groupSelectionKeys`, `groupSelectionStatus`, `groupSelectionViewModel`, and `groupSelectionOrigin` state if no longer referenced
- keep `Import Matrix` dialog and preview/reparse behavior

- [ ] **Step 5: Keep build green while import direct-apply is still pending**

Temporarily wire import confirmation to an explicit helper stub:

```ts
const applyImportedMatrixDirectly = async (): Promise<void> => {
  throw new Error("TASK_279 direct import implementation missing");
};
```

Do not leave this stub after Task 3.

### Task 3: Import Matrix Directly Into Editor

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add failing import direct-apply test**

In `MatrixEditorWorkspace.test.tsx`, add:

```ts
it("imports parsed source matrix directly into the editor table", async () => {
  apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce({
    project_id: "P1",
    source_document_path: "D:/source.docx",
    source_document_name: "source.docx",
    source_format: ".docx",
    capability_status: "supported",
    generated_at: "2026-05-28T00:00:00Z",
    selected_table_index: 0,
    selected_page_number: 1,
    selected_page_table_index: 1,
    candidate_tables: [],
    preview_pdf_token: null,
    rows: [
      {
        source_row_index: 1,
        test_item: "Visual Examination",
        source_section: "1.1",
        group_tokens: { "1": "1", "2": "2", g1: "1", g2: "2" },
        is_sample_row: false,
      },
    ],
    groups: [
      {
        group_key: "g1",
        group_label: "1",
        source_table_index: 0,
        extraction_status: "loaded",
        sample_size: null,
        sample_quantity_expression: "5",
        sample_note: null,
        steps: [],
      },
      {
        group_key: "g2",
        group_label: "2",
        source_table_index: 0,
        extraction_status: "loaded",
        sample_size: null,
        sample_quantity_expression: "6",
        sample_note: null,
        steps: [],
      },
    ],
    warnings: [],
    blockers: [],
  });
  apiMocks.commitMatrixImport.mockResolvedValueOnce({
    commit_status: "created",
    source_import_id: "smi-new",
    source_snapshot_id: "sms-new",
    selected_group_keys_committed: ["g1", "g2"],
    project_matrix_draft: {
      groups: [
        {
          draft_group_id: "group-1",
          source_group_snapshot_id: "sg-1",
          group_order: 1,
          group_key: "g1",
          group_label: "1",
          is_selected: true,
          sample_quantity_expression: "5",
          sample_note: null,
        },
        {
          draft_group_id: "group-2",
          source_group_snapshot_id: "sg-2",
          group_order: 2,
          group_key: "g2",
          group_label: "2",
          is_selected: true,
          sample_quantity_expression: "6",
          sample_note: null,
        },
      ],
      rows: [
        {
          draft_row_id: "row-1",
          source_row_snapshot_id: "sr-1",
          row_order: 1,
          test_item: "Visual Examination",
          source_section: "1.1",
          method: null,
          condition: null,
          requirement: null,
          is_sample_row: false,
        },
      ],
      cells: [
        { draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1" },
        { draft_row_id: "row-1", draft_group_id: "group-2", cell_value: "2" },
      ],
    },
  });

  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

  await screen.findByRole("button", { name: "Import Matrix" });
  fireEvent.click(screen.getByRole("button", { name: "Import Matrix" }));
  const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
  fireEvent.change(input, {
    target: {
      files: [
        new File(["docx"], "source.docx", {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }),
      ],
    },
  });

  await screen.findByText("Import Matrix");
  fireEvent.click(screen.getAllByRole("button", { name: "Replace" })[0]);

  await waitFor(() => {
    expect(apiMocks.commitMatrixImport).toHaveBeenCalledWith("P1", expect.objectContaining({
      selected_group_keys: ["g1", "g2"],
    }));
  });
  expect(screen.queryByText("Import Selection Mode")).toBeNull();
  expect(screen.getByLabelText("Include group 1")).toBeTruthy();
  expect(screen.getByLabelText("Include group 2")).toBeTruthy();
  expect((screen.getByLabelText("Row 1 1") as HTMLTextAreaElement).value).toBe("1");
  expect((screen.getByLabelText("Row 1 2") as HTMLTextAreaElement).value).toBe("2");
});
```

- [ ] **Step 2: Implement direct import helper**

In `MatrixEditorWorkspace.tsx`, implement:

```ts
const applyImportedMatrixDirectly = async (): Promise<void> => {
  const selectionFromPreview = buildMatrixImportSelectionViewModel(importPreview);
  if (!importPreview || !selectionFromPreview || selectionFromPreview.groups.length === 0) {
    setImportError("No valid matrix found from import.");
    return;
  }
  setCommittingImport(true);
  try {
    const selectedGroupKeys = selectionFromPreview.groups.map((group) => group.groupKey);
    const response = await commitMatrixImport(projectId, {
      source_document_path: importPreview.source_document_path,
      source_document_name: importPreview.source_document_name,
      source_format: importPreview.source_format,
      preview_payload: importPreview,
      selected_group_keys: selectedGroupKeys,
    });
    applyDraftSnapshotToEditor(buildSessionDraftFromProjectMatrixDraft(response.project_matrix_draft));
    setImportPreview(importPreview);
    setSessionSourceImportId(response.source_import_id);
    setSessionSourceSnapshotId(response.source_snapshot_id);
    setSaveState("saved");
    setImportError(null);
    setShowImportDialog(false);
  } catch (error) {
    setImportError(parseRequestError(error, "Failed to import Matrix."));
  } finally {
    setCommittingImport(false);
  }
};
```

Replace the import dialog `Replace` action to call `applyImportedMatrixDirectly`.

Do not enable `Append` in this task. Add/keep a test assertion that `Append` is disabled and cannot trigger `commitMatrixImport`.

- [ ] **Step 3: Run import direct-apply test**

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
```

Expected: pass.

### Task 4: Inline Group Checkboxes And Selected-Only Filter

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/workbench.css`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add failing inline checkbox test**

Add:

```ts
it("toggles group inclusion inline without deleting group data", async () => {
  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

  const include1 = await screen.findByLabelText("Include group 1");
  expect((include1 as HTMLInputElement).checked).toBe(true);

  fireEvent.click(include1);

  expect((include1 as HTMLInputElement).checked).toBe(false);
  expect((screen.getByLabelText("Row 1 1") as HTMLTextAreaElement).value).toBe("1");
  fireEvent.click(include1);
  expect((include1 as HTMLInputElement).checked).toBe(true);
});
```

- [ ] **Step 2: Add failing selected-only filter test**

Add:

```ts
it("hides unchecked groups and unused rows when selected-only filter is enabled", async () => {
  apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce(
    buildSessionSeed({
      sourcePreviewPayload: {
        project_id: "P1",
        source_document_path: "D:/spec.docx",
        source_document_name: "spec.docx",
        source_format: ".docx",
        capability_status: "supported",
        generated_at: "2026-05-28T00:00:00Z",
        selected_table_index: 0,
        selected_page_number: 1,
        selected_page_table_index: 1,
        candidate_tables: [],
        preview_pdf_token: null,
        rows: [],
        groups: [],
        warnings: [],
        blockers: [],
      },
      editorDraft: {
        groups: [
          {
            draft_group_id: "group-1",
            source_group_snapshot_id: "sg-1",
            group_order: 1,
            group_key: "g1",
            group_label: "1",
            is_selected: true,
            sample_quantity_expression: "5",
            sample_note: null,
          },
          {
            draft_group_id: "group-2",
            source_group_snapshot_id: "sg-2",
            group_order: 2,
            group_key: "g2",
            group_label: "2",
            is_selected: true,
            sample_quantity_expression: "5",
            sample_note: null,
          },
        ],
        rows: [
          {
            draft_row_id: "row-1",
            source_row_snapshot_id: "sr-1",
            row_order: 1,
            test_item: "Used Item",
            source_section: "1.1",
            method: "M",
            condition: "C",
            requirement: "R",
            is_sample_row: false,
          },
          {
            draft_row_id: "row-2",
            source_row_snapshot_id: "sr-2",
            row_order: 2,
            test_item: "Only Unchecked Item",
            source_section: "1.2",
            method: "M",
            condition: "C",
            requirement: "R",
            is_sample_row: false,
          },
        ],
        cells: [
          { draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1" },
          { draft_row_id: "row-2", draft_group_id: "group-2", cell_value: "2" },
        ],
      },
    })
  );

  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

  fireEvent.click(await screen.findByLabelText("Include group 2"));
  fireEvent.click(screen.getByLabelText("Show selected groups only"));

  expect(screen.queryByLabelText("Row 1 2")).toBeNull();
  expect(screen.queryByLabelText("Row 2 test item")).toBeNull();

  fireEvent.click(screen.getByLabelText("Show selected groups only"));
  expect(screen.getByLabelText("Row 2 test item")).toBeTruthy();
  expect((screen.getByLabelText("Row 2 2") as HTMLTextAreaElement).value).toBe("2");
});
```

- [ ] **Step 3: Implement inline checkbox rendering**

In the group header `<th>`, render:

```tsx
<label className="matrix-editor-group-include-control" onClick={(event) => event.stopPropagation()}>
  <input
    type="checkbox"
    checked={group.isSelected}
    aria-label={`Include group ${group.name || "group"}`}
    onChange={(event) => toggleGroupIncluded(group.id, event.target.checked)}
  />
  <span aria-hidden="true" />
</label>
```

Keep the existing group name input beside it.

- [ ] **Step 4: Implement selected-only filter**

Add a compact checkbox control above the table:

```tsx
<label className="matrix-editor-filter-toggle">
  <input
    type="checkbox"
    checked={showSelectedGroupsOnly}
    aria-label="Show selected groups only"
    onChange={(event) => setShowSelectedGroupsOnly(event.target.checked)}
  />
  <span>Selected groups only</span>
</label>
```

Use `visibleGroupColumns` and `visibleRows` for rendering table headers, cells, and sample row. Do not mutate `groupColumns` or `editableRows` when filtering.

- [ ] **Step 5: Add CSS**

Add:

```css
.matrix-editor-group-header-content {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 4px;
  align-items: center;
}

.matrix-editor-group-include-control {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.matrix-editor-filter-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-ink-muted);
  font-size: 12px;
  font-weight: 700;
}
```

- [ ] **Step 6: Run frontend tests**

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
```

Expected: pass.

### Task 5: Frontend Selected Sample Guard

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/workbench.css`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add failing sample guard test**

Add:

```ts
it("blocks Confirm Matrix when a selected group sample quantity has no number", async () => {
  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

  const sample1 = await screen.findByLabelText("Samples 1");
  fireEvent.change(sample1, { target: { value: "sample only" } });

  expect(screen.getByRole("button", { name: "Confirm Matrix" })).toBeDisabled();
  expect(sample1.className).toContain("is-invalid");

  fireEvent.click(screen.getByLabelText("Include group 1"));

  expect(screen.getByRole("button", { name: "Confirm Matrix" })).not.toBeDisabled();
});
```

- [ ] **Step 2: Implement invalid sample group detection**

Add helpers shown in **Frontend Guard**.

Add:

```ts
const invalidSelectedSampleGroupIds = buildInvalidSelectedSampleGroupIds(
  groupColumns,
  sampleValues
);
const hasSelectedSampleQuantityError = invalidSelectedSampleGroupIds.size > 0;
```

Add to `publishDisabledReason` before no-change:

```ts
: hasSelectedSampleQuantityError
  ? "Selected group sample quantity is incomplete."
```

Do not pass this reason into a tooltip for `Confirm Matrix`.

Do not surface this guard via top status copy. When disabled by selected-sample guard, `onConfirmMatrix` must return without setting `confirmActiveMessage`.

- [ ] **Step 3: Apply red invalid styling to sample inputs**

For sample quantity textareas:

```tsx
className={`matrix-editor-sample-textarea${
  invalidSelectedSampleGroupIds.has(group.id) ? " is-invalid" : ""
}`}
```

For selected group notes card sample input, apply the same invalid class when selected group is invalid.

- [ ] **Step 4: Adjust `Confirm Matrix` button title behavior**

In `MatrixWorkspaceActionGroups.tsx`, remove sample-guard tooltip behavior. The simplest acceptable result is no `title` on `Confirm Matrix`:

```tsx
<button
  className="matrix-editor-primary-action"
  type="button"
  disabled={publishDisabled}
  onClick={onPublishActiveMatrix}
>
  {publishBusy ? "Confirming..." : "Confirm Matrix"}
</button>
```

- [ ] **Step 5: Add CSS if existing `.is-invalid` does not cover sample fields**

Add:

```css
.matrix-editor-sample-textarea.is-invalid,
.matrix-editor-samples-inline-input.is-invalid {
  border-color: var(--color-danger);
  background: #fff1f1;
}
```

- [ ] **Step 6: Run frontend tests**

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
```

Expected: pass.

### Task 6: Static Guards And Cleanup

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`
- Modify: `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx` if deleting
- Modify: `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts` if no longer used

- [ ] **Step 1: Add TASK_279 static guard**

Add:

```python
def test_task279_inline_group_selection_and_sample_guard_is_wired() -> None:
    workspace_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    action_groups_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixWorkspaceActionGroups.tsx"
    ).read_text(encoding="utf-8")
    css_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    assert "Selected Groups" not in action_groups_source
    assert "onChangeSelectedGroups" not in action_groups_source
    assert "MatrixImportSelectionMode" not in workspace_source
    assert "Include group" in workspace_source
    assert "Show selected groups only" in workspace_source
    assert "buildInvalidSelectedSampleGroupIds" in workspace_source
    assert "sampleQuantityHasDigit" in workspace_source
    assert "matrix-editor-group-include-control" in css_source
    assert "matrix-editor-filter-toggle" in css_source
```

- [ ] **Step 2: Update older static tests**

Adjust older task guards that currently require:

- `Selected Groups`
- `MatrixImportSelectionMode`
- `Confirm selected groups`
- `matrix-editor-selection-summary`

Replace those requirements with TASK_279-compatible assertions.

- [ ] **Step 3: Remove unused component if safe**

Run:

```powershell
rg "MatrixImportSelectionMode|buildMatrixImportSelectionSummary|buildDefaultSelectedGroupKeys" frontend\src
```

If no runtime imports remain, delete `MatrixImportSelectionMode.tsx` and remove unused selector exports. If older static tests still document historical behavior, update them rather than keeping dead UI code.

- [ ] **Step 4: Run static tests**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task279 or task278 or matrix_editor"
```

Expected: pass.

### Task 7: End-To-End Verification And Board Sync

**Files:**

- Modify: `tasks/TASK_279_MATRIX_EDITOR_INLINE_GROUP_SELECTION_AND_SAMPLE_GUARD.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Run full targeted validation**

Run:

```powershell
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\unit\test_matrix_revision_flow_service.py -q
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
npm test -- --run ProjectWorkbenchMatrixProjectionPanel --watch=false
npm run build
cd ..
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task279 or task278 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

Expected:

- all listed tests pass
- `git diff --check` has no blocking whitespace errors; CRLF warnings are acceptable if consistent with current repo behavior

- [ ] **Step 2: Manual browser smoke**

Use in-app browser:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/matrix-editor
```

Check:

- toolbar has no `Selected Groups`
- import source Matrix directly loads editor table
- group header checkbox can uncheck/recheck a group
- selected-only filter hides unchecked group and unused rows
- invalid selected sample quantity disables `Confirm Matrix`
- unchecking the invalid group removes the publish blocker
- valid confirm returns to Workbench and projection shows selected groups only

- [ ] **Step 3: Update task status**

Update `tasks/TASK_279_MATRIX_EDITOR_INLINE_GROUP_SELECTION_AND_SAMPLE_GUARD.md`:

```markdown
## Status

Complete.
```

Add validation notes under a completion section.

- [ ] **Step 4: Update task board**

Update `docs/task_board.md`:

- add `TASK_279 complete` to status line
- set `Current Active Task: none`
- add completion note and validation summary

- [ ] **Step 5: Update plan index**

Update `docs/task_plan_index.md`:

```text
Status: no active planned task plan
Current active planned task plan:
none
Latest completed task plan history:
docs/task_279_matrix_editor_inline_group_selection_and_sample_guard_plan.md
```

## Risk Controls

- Keep `showSelectedGroupsOnly` as display-only state; never delete hidden rows/groups.
- Keep source lineage IDs intact after import.
- Do not reintroduce the old group selection page.
- Do not make sample guard rely on tooltip or hidden message; red fields and disabled confirm are the user-facing cues.
- Backend must remain the final guard even if frontend validation misses an edge case.

## Self-Review

### Spec Coverage

- Inline group checkbox selection: covered in Tasks 4 and 6.
- Removal of `Selected Groups` page/action: covered in Tasks 2 and 6.
- Direct import to editor table: covered in Task 3.
- Selected-only filter: covered in Task 4.
- Sample quantity digit guard: covered in Tasks 1 and 5.
- Old/new path validation alignment: covered in Task 1.
- No tooltip/top warning for sample guard: covered in Task 5.

### Placeholder Scan

No implementation step depends on unresolved placeholders. Test snippets use existing fixture helper names that are present in the current repository.

### Type Consistency

- Frontend group inclusion stays on existing `GroupColumn.isSelected`.
- Confirm payload continues to use existing `groups[*].is_selected`.
- Backend guard consumes existing application group objects through a structural protocol.

## Execution Handoff

Plan complete and saved to `docs/task_279_matrix_editor_inline_group_selection_and_sample_guard_plan.md`.

Recommended execution mode:

1. Inline Execution with `superpowers:executing-plans` - recommended for this repo because the task touches tightly coupled Matrix Editor state and backend validation.
2. Subagent-driven execution is not recommended here because the frontend state changes and backend guard must be reviewed together after each slice.

Wait for explicit user approval before implementation.
