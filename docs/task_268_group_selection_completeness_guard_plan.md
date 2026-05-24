# Group Selection Completeness Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Matrix Group Selection mode actively guard against missing groups and missing steps before creating the selected-only draft.

**Architecture:** This is a frontend-only refinement inside the existing Matrix Editor feature. Derive completeness metadata from `MatrixPreviewResponse` in selectors, render a compact selection summary in `MatrixImportSelectionMode`, and keep the TASK_261 commit API unchanged.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, CSS in `frontend/src/workbench.css`, pytest static shell tests.

---

## Anti-Skip Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD`
- Allowed reason: TASK_261 to TASK_267 are complete, `docs/task_board.md` has no active implementation task before this planning step, and the user requested TASK_268 from the post-Phase-11 guideline.

## Scope Lock

Implement only the selection completeness guard:

- Add selected group and step summary.
- Show sample quantity expressions in group selection.
- Add a visible zero-selection blocker.
- Add confirmation summary before commit.

Do not implement:

- Backend changes, API changes, schema migration, repository changes, reload recovery, multi-matrix merge, Project Workbench projection, StepInstance, LLCR runtime persistence, report engine, fee engine, AI recommendation, permissions, or Test Record Word generation.

## File Responsibilities

- `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`
  - Extend the view model with selected-summary helpers that remain pure and testable through component tests.
  - Keep derivation based only on `MatrixPreviewResponse`, selected group keys, and existing group metadata.

- `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`
  - Render selected count, selected step count, sample quantity per group, and confirmation summary.
  - Keep Test Item rows as the table body context.
  - Keep Section / Method / Condition / Requirement hidden.

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Cover selected group count, selected step count, sample quantity visibility, summary update after toggling, and zero-selection blocker.

- `frontend/src/workbench.css`
  - Add compact, operational styling for the completeness summary and sample quantity labels.

- `tests/unit/test_frontend_shell_files.py`
  - Add static guardrails for TASK_268 copy and selectors.

- `tasks/TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD.md`
  - Update to complete only after approved implementation and validation pass.

- `docs/task_board.md`
  - Update status only after approved implementation and validation pass.

## UX Decisions

1. Selection mode remains matrix-native.
   - Rows continue to show Test Item context.
   - Group columns remain the primary selection surface.

2. Sample quantity belongs in group context.
   - Render under each group label in the selection header.
   - Render selected sample quantities again in the confirmation summary.

3. Step count is a guard, not a new authority.
   - Use `group.steps.length` when available.
   - If steps are not available, show `Steps: not available`.
   - Treat `stepCount: 0` as an explicitly empty steps array, and `stepCount: null` as "not available".

4. Zero selected groups is a blocker.
   - Keep `Confirm selected groups` disabled.
   - Show an explicit blocker line near the summary.

5. Confirmation summary is inline, not a modal.
   - Avoid adding a modal confirmation step.
   - Keep the workflow fast but harder to misunderstand.

## Task 1: Extend Selection View Model

**Files:**

- Modify: `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`

- [ ] **Step 1: Add summary type**

First update `MatrixImportSelectableGroup.stepCount` from `number` to `number | null`:

```ts
stepCount: number | null;
```

Then update `buildMatrixImportSelectableGroups` so missing or non-array `steps` becomes `null`, while an explicitly empty steps array remains `0`:

```ts
stepCount: Array.isArray(group.steps) ? group.steps.length : null,
```

Add below `MatrixImportSelectionViewModel`:

```ts
export type MatrixImportSelectionSummary = {
  selectedGroupCount: number;
  totalGroupCount: number;
  selectedStepCount: number | null;
  hasStepCounts: boolean;
  selectedGroupLabels: string[];
  selectedSampleQuantities: Array<{
    groupKey: string;
    groupLabel: string;
    sampleQuantityExpression: string;
  }>;
};
```

- [ ] **Step 2: Add sample quantity formatter**

Add:

```ts
export function formatMatrixImportSampleQuantity(value: string | null): string {
  const normalized = (value ?? "").trim();
  return normalized.length > 0 ? normalized : "Not specified";
}
```

- [ ] **Step 3: Add summary builder**

Add:

```ts
export function buildMatrixImportSelectionSummary(input: {
  groups: MatrixImportSelectableGroup[];
  selectedGroupKeys: string[];
}): MatrixImportSelectionSummary {
  const selectedKeys = new Set(input.selectedGroupKeys);
  const selectedGroups = input.groups.filter((group) => selectedKeys.has(group.groupKey));
  const hasStepCounts = selectedGroups.every((group) => group.stepCount !== null);
  const selectedStepCount = hasStepCounts
    ? selectedGroups.reduce((total, group) => total + (group.stepCount ?? 0), 0)
    : null;

  return {
    selectedGroupCount: selectedGroups.length,
    totalGroupCount: input.groups.length,
    selectedStepCount,
    hasStepCounts,
    selectedGroupLabels: selectedGroups.map((group) => group.groupLabel),
    selectedSampleQuantities: selectedGroups.map((group) => ({
      groupKey: group.groupKey,
      groupLabel: group.groupLabel,
      sampleQuantityExpression: formatMatrixImportSampleQuantity(group.sampleQuantityExpression),
    })),
  };
}
```

- [ ] **Step 4: Build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 2: Render Completeness Summary In Selection Mode

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`

- [ ] **Step 1: Import summary helpers**

Update imports:

```ts
import {
  buildMatrixImportSelectionSummary,
  formatMatrixImportSampleQuantity,
  type MatrixImportSelectionViewModel,
} from "./matrixImportSelectionSelectors";
```

- [ ] **Step 2: Build summary inside component**

Add after `visibleStatusMessage`:

```ts
const summary = buildMatrixImportSelectionSummary({
  groups: viewModel.groups,
  selectedGroupKeys,
});
const selectedGroupList = summary.selectedGroupLabels.length > 0
  ? summary.selectedGroupLabels.join(", ")
  : "None selected";
const selectedStepText = summary.hasStepCounts && summary.selectedStepCount !== null
  ? `${summary.selectedStepCount}`
  : "not available";
```

- [ ] **Step 3: Replace header meta line**

Replace:

```tsx
<p>{`Source: ${viewModel.sourceDocumentName} | Groups: ${viewModel.groups.length}, Selected: ${selectedGroupKeys.length}`}</p>
```

with:

```tsx
<p>{`Source: ${viewModel.sourceDocumentName}`}</p>
<p>{`Selected groups: ${summary.selectedGroupCount} / ${summary.totalGroupCount} | Selected steps: ${selectedStepText}`}</p>
```

- [ ] **Step 4: Add confirmation summary block**

Add after the optional status message:

```tsx
<aside className="matrix-editor-selection-summary" aria-label="Selected group summary">
  <div>
    <strong>Selected groups</strong>
    <span>{selectedGroupList}</span>
  </div>
  <div>
    <strong>Selected step count</strong>
    <span>{selectedStepText}</span>
  </div>
  <div>
    <strong>Sample quantities</strong>
    <span>
      {summary.selectedSampleQuantities.length > 0
        ? summary.selectedSampleQuantities
            .map((entry) => `${entry.groupLabel}: ${entry.sampleQuantityExpression}`)
            .join("; ")
        : "Select at least one group to review sample quantities."}
    </span>
  </div>
  {summary.selectedGroupCount === 0 ? (
    <p className="matrix-editor-selection-blocker">Select at least one group before creating the draft.</p>
  ) : null}
</aside>
```

- [ ] **Step 5: Show sample quantity in each group header**

Inside the group header label, replace:

```tsx
<span>{group.groupLabel}</span>
```

with:

```tsx
<span className="matrix-editor-selection-group-label">
  <span>{group.groupLabel}</span>
  <small>{`Samples: ${formatMatrixImportSampleQuantity(group.sampleQuantityExpression)}`}</small>
</span>
```

- [ ] **Step 6: Build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 3: Add Selection Summary Styling

**Files:**

- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Add summary styles near existing selection-mode rules**

Add near the existing `.matrix-editor-selection-mode`, `.matrix-editor-selection-mode-actions`, and `.matrix-editor-selection-table` styles in `frontend/src/workbench.css` so all selection-mode styling stays together:

```css
.matrix-editor-selection-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 12px 0;
  padding: 12px;
  border: 1px solid #d8e0ea;
  border-radius: 10px;
  background: #fbfdff;
}

.matrix-editor-selection-summary div {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.matrix-editor-selection-summary strong {
  font-size: 12px;
  color: #172033;
}

.matrix-editor-selection-summary span {
  font-size: 13px;
  color: #647084;
  overflow-wrap: anywhere;
}

.matrix-editor-selection-blocker {
  grid-column: 1 / -1;
  margin: 0;
  color: #c2413a;
  font-weight: 700;
}

.matrix-editor-selection-group-label {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.matrix-editor-selection-group-label small {
  color: #647084;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.2;
}
```

- [ ] **Step 2: Add responsive fallback**

Add near existing Matrix Editor responsive rules, or below the summary styles:

```css
@media (max-width: 900px) {
  .matrix-editor-selection-summary {
    grid-template-columns: 1fr;
  }
}
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

## Task 4: Update React Tests

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add test for selected counts and sample quantities**

Add a test that enters selection mode from import preview and asserts:

```ts
expect(screen.getByText("Selected groups: 2 / 2 | Selected steps: 3")).toBeTruthy();
expect(screen.getByText("Samples: 5")).toBeTruthy();
expect(screen.getByText("Samples: 3")).toBeTruthy();
expect(screen.getByLabelText("Selected group summary")).toBeTruthy();
expect(screen.getByText("Group A: 5; Group B: 3")).toBeTruthy();
```

Use preview mock groups with:

```ts
groups: [
  {
    group_key: "g1",
    group_label: "Group A",
    source_table_index: 0,
    extraction_status: "ok",
    sample_quantity_expression: "5",
    sample_note: null,
    steps: [
      { sequence: 1, raw_token: "1", test_item: "Step 1" },
      { sequence: 2, raw_token: "2", test_item: "Step 2" },
    ],
  },
  {
    group_key: "g2",
    group_label: "Group B",
    source_table_index: 0,
    extraction_status: "ok",
    sample_quantity_expression: "3",
    sample_note: null,
    steps: [
      { sequence: 3, raw_token: "3", test_item: "Step 3" },
    ],
  },
],
```

Use `sequence`, `raw_token`, and `test_item` because `MatrixPreviewStep` in `frontend/src/api/client.ts` requires those fields. Do not use `step_token`; that field is not part of the current frontend DTO.

- [ ] **Step 2: Add test for summary update after deselecting one group**

In the same or a separate test:

```ts
fireEvent.click(screen.getByLabelText("Select Group B"));
expect(screen.getByText("Selected groups: 1 / 2 | Selected steps: 2")).toBeTruthy();
expect(screen.getByText("Group A: 5")).toBeTruthy();
expect(screen.queryByText("Group A: 5; Group B: 3")).toBeNull();
```

- [ ] **Step 3: Add test for zero-selection blocker**

Add or extend a test:

```ts
fireEvent.click(screen.getByLabelText("Select Group A"));
fireEvent.click(screen.getByLabelText("Select Group B"));

expect(screen.getByText("Select at least one group before creating the draft.")).toBeTruthy();
const confirmButton = screen.getByRole("button", { name: "Confirm selected groups" });
expect(confirmButton).toBeDisabled();
```

- [ ] **Step 4: Run Matrix Editor tests**

Run:

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

Expected:

```text
all MatrixEditorWorkspace tests pass
```

## Task 5: Add Static Guardrails

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_268 static test**

Add:

```python
def test_task268_group_selection_completeness_guard_is_wired() -> None:
    selection_mode_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixImportSelectionMode.tsx"
    ).read_text(encoding="utf-8")
    selector_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "matrixImportSelectionSelectors.ts"
    ).read_text(encoding="utf-8")
    css_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    assert "buildMatrixImportSelectionSummary" in selector_source
    assert "formatMatrixImportSampleQuantity" in selector_source
    assert "Selected groups:" in selection_mode_source
    assert "Selected step count" in selection_mode_source
    assert "Sample quantities" in selection_mode_source
    assert "Select at least one group before creating the draft." in selection_mode_source
    assert "matrix-editor-selection-summary" in css_source
    assert "matrix-editor-selection-blocker" in css_source
```

- [ ] **Step 2: Run static tests**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task268 or task267 or matrix_editor"
```

Expected:

```text
TASK_268 and existing Matrix Editor checks pass
```

## Task 6: Regression Verification And Docs Sync

**Files:**

- Modify after validation: `tasks/TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD.md`
- Modify after validation: `docs/task_board.md`

- [ ] **Step 1: Run full verification**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task268 or task267 or matrix_editor"
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

- [ ] **Step 2: Confirm backend remains untouched**

Run:

```powershell
git diff --name-only
```

Expected TASK_268 implementation files are limited to:

```text
docs/task_268_group_selection_completeness_guard_plan.md
docs/task_board.md
tasks/TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD.md
frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts
frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx
frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
frontend/src/workbench.css
tests/unit/test_frontend_shell_files.py
```

- [ ] **Step 3: Update task file after implementation**

After validation passes, update:

```markdown
Status: complete
Last Updated: 2026-05-24
```

Add validation results and completion notes to `tasks/TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD.md`.

- [ ] **Step 4: Update task board after implementation**

Update `docs/task_board.md`:

```markdown
> Status: ... + TASK_268 complete
> Last Updated: 2026-05-24
> Current Active Task: none (`TASK_268_GROUP_SELECTION_COMPLETENESS_GUARD` complete; awaiting next approved task).
```

Add a TASK_268 completion note with deliverables, validation commands, and scope boundary.

## Review Checklist Before Implementation

- [ ] Task remains frontend-only.
- [ ] No backend files are modified.
- [ ] Group selection remains matrix-native, not a detached list.
- [ ] Test Item rows remain visible.
- [ ] Section / Method / Condition / Requirement remain hidden.
- [ ] Zero selected groups is visibly blocked.
- [ ] Sample quantities are visible before commit.
- [ ] TASK_261 commit API remains unchanged.
- [ ] TASK_267 navigation remains intact.

## Execution Handoff

After this plan is approved, implement with `superpowers:executing-plans` in this session. Execute task by task, run verification commands at the listed checkpoints, update task docs only after validation passes, and stop after TASK_268 completion. Do not proceed to TASK_269 or any follow-up task.
