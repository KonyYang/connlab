# Record Step Workspace Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn a clicked Project Workbench Matrix projection token into a record-oriented, read-only Step Workspace panel.

**Architecture:** Keep TASK_263 to TASK_269 data flow unchanged. Reuse the existing `MatrixProjectionTokenCell` view model, extract the inline token detail from `ProjectWorkbenchMatrixProjectionPanel` into a focused `RecordStepWorkspacePanel`, and add only frontend tests/styles/static guards.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, existing ConnLab CSS in `frontend/src/workbench.css`, pytest static guard tests.

---

## Anti-Skip Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_270_RECORD_STEP_WORKSPACE_PANEL` (planned)
- Allowed reason: `TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE` is complete, the task board had no active implementation task, and the user requested TASK_270 planning from the post-Phase-11 Matrix-driven laboratory execution guideline.

Implementation must wait for explicit user approval after this plan is reviewed.

## Product / UI Context

ConnLab is a `product` UI. The operator is a lab engineer or coordinator using an offline Windows workstation in a daytime laboratory administration setting. The UI should stay calm, dense, traceable, and operational.

Design constraints:

- State before action.
- Matrix before output.
- Step before report.
- No playful copy.
- No enabled placeholder actions for persistence that does not exist yet.
- No marketing layout, decorative cards, glassmorphism, gradient text, or side-stripe accent cards.

## Scope Boundary

In scope:

- Frontend-only right-side Record Step Workspace panel.
- Read-only rendering of selected Matrix projection token context.
- Inactive placeholders for record draft, evidence/data, and review.
- Tests and static guards.

Out of scope:

- Backend/API/database changes.
- StepInstance persistence.
- LLCR runtime persistence.
- Evidence upload.
- Measurement forms.
- Test Record Word generation.
- Report engine.
- AI recommendation or review.
- Equipment assignment.
- Permission workflow.
- Matrix authority mutation from Project Workbench.

## File Structure

Create:

- `frontend/src/features/project-workbench/RecordStepWorkspacePanel.tsx`
  - Owns the record-oriented selected-token detail UI.
  - Accepts `MatrixProjectionTokenCell | null` and a precomputed status label.
  - Contains no API calls and no mutation actions.

- `frontend/src/features/project-workbench/RecordStepWorkspacePanel.test.tsx`
  - Verifies empty state, selected-token detail, and read-only placeholders.

Modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - Imports and renders `RecordStepWorkspacePanel`.
  - Removes inline `<aside className="runtime-console-matrix-token-detail">`.
  - Keeps fetching, view-model derivation, token click handling, and table rendering unchanged.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - Updates the token-click assertion from `Matrix token detail` to `Record Step Workspace`.
  - Adds a lightweight assertion that record placeholders appear after token selection.

- `frontend/src/workbench.css`
  - Adds styles near the existing matrix projection rules around `.runtime-console-matrix-token-detail`.
  - Reuses existing cool workbench palette and compact detail layout.

- `tests/unit/test_frontend_shell_files.py`
  - Adds `test_task270_record_step_workspace_panel_is_wired`.
  - Guards component creation, projection wiring, required copy, no direct fetch, and no backend file requirement.

- `tasks/TASK_270_RECORD_STEP_WORKSPACE_PANEL.md`
  - Mark complete only after implementation and validation.

- `docs/task_board.md`
  - Mark TASK_270 complete only after implementation and validation.

## Existing Data Contract

Use this existing type from `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`:

```ts
export type MatrixProjectionTokenCell = {
  tokenReference: string;
  groupKey: string;
  groupLabel: string;
  rawToken: string;
  sequence: number;
  statusTone: MatrixProjectionStatusTone;
  sampleQuantityExpression: string;
  testItem: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
};
```

No API DTO changes are allowed.

---

### Task 1: Add Record Step Workspace Component

**Files:**

- Create: `frontend/src/features/project-workbench/RecordStepWorkspacePanel.tsx`
- Test: `frontend/src/features/project-workbench/RecordStepWorkspacePanel.test.tsx`

- [ ] **Step 1: Write the failing component test**

Create `frontend/src/features/project-workbench/RecordStepWorkspacePanel.test.tsx`:

```tsx
import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { RecordStepWorkspacePanel } from "./RecordStepWorkspacePanel";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";

const selectedToken: MatrixProjectionTokenCell = {
  tokenReference: "Visual::6.1::EIA-364-18B::10x::No damage:g1:1:1",
  groupKey: "g1",
  groupLabel: "Group 1",
  rawToken: "1",
  sequence: 1,
  statusTone: "not_started",
  sampleQuantityExpression: "3",
  testItem: "Visual",
  section: "6.1",
  method: "EIA-364-18B",
  condition: "10x",
  requirement: "No damage",
};

describe("RecordStepWorkspacePanel", () => {
  it("shows an empty state before a matrix token is selected", () => {
    render(
      <RecordStepWorkspacePanel selectedToken={null} statusLabel="Not selected" />
    );

    const panel = screen.getByLabelText("Record Step Workspace");
    expect(within(panel).getByText("Record Step Workspace")).toBeTruthy();
    expect(
      within(panel).getByText("Select a matrix token to review record context.")
    ).toBeTruthy();
  });

  it("renders selected token context needed for Test Record preparation", () => {
    render(
      <RecordStepWorkspacePanel
        selectedToken={selectedToken}
        statusLabel="Not started"
      />
    );

    const panel = screen.getByLabelText("Record Step Workspace");
    for (const expectedText of [
      "Group 1",
      "1",
      "Not started",
      "3",
      "Visual",
      "6.1",
      "EIA-364-18B",
      "10x",
      "No damage",
    ]) {
      expect(within(panel).getByText(expectedText)).toBeTruthy();
    }
  });

  it("shows inactive record, evidence, and review placeholders", () => {
    render(
      <RecordStepWorkspacePanel
        selectedToken={selectedToken}
        statusLabel="Not started"
      />
    );

    const panel = screen.getByLabelText("Record Step Workspace");
    expect(within(panel).getByText("Record draft")).toBeTruthy();
    expect(within(panel).getByText("Evidence / data")).toBeTruthy();
    expect(within(panel).getByText("Review")).toBeTruthy();
    expect(within(panel).getAllByText("Placeholder")).toHaveLength(3);
    expect(within(panel).queryByRole("button")).toBeNull();
  });
});
```

- [ ] **Step 2: Run the component test and verify it fails**

Run:

```powershell
cd frontend
npm test -- --run RecordStepWorkspacePanel
```

Expected: FAIL because `RecordStepWorkspacePanel` does not exist.

- [ ] **Step 3: Implement the component**

Create `frontend/src/features/project-workbench/RecordStepWorkspacePanel.tsx`:

```tsx
import type { ReactElement } from "react";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";

type RecordStepWorkspacePanelProps = {
  selectedToken: MatrixProjectionTokenCell | null;
  statusLabel: string;
};

function displayValue(value: string): string {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : "-";
}

export function RecordStepWorkspacePanel({
  selectedToken,
  statusLabel,
}: RecordStepWorkspacePanelProps): ReactElement {
  return (
    <aside
      className="runtime-console-record-step-workspace"
      aria-label="Record Step Workspace"
    >
      <header className="runtime-console-record-step-workspace-header">
        <div>
          <p className="eyebrow">Read-only step context</p>
          <h4>Record Step Workspace</h4>
        </div>
        <span>Authority locked</span>
      </header>

      {selectedToken ? (
        <>
          <dl className="runtime-console-record-step-fields">
            <div>
              <dt>Group</dt>
              <dd>{displayValue(selectedToken.groupLabel)}</dd>
            </div>
            <div>
              <dt>Step token</dt>
              <dd>{displayValue(selectedToken.rawToken)}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{statusLabel}</dd>
            </div>
            <div>
              <dt>Sample quantity</dt>
              <dd>{displayValue(selectedToken.sampleQuantityExpression)}</dd>
            </div>
            <div>
              <dt>Test item</dt>
              <dd>{displayValue(selectedToken.testItem)}</dd>
            </div>
            <div>
              <dt>Section</dt>
              <dd>{displayValue(selectedToken.section)}</dd>
            </div>
            <div>
              <dt>Method</dt>
              <dd>{displayValue(selectedToken.method)}</dd>
            </div>
            <div>
              <dt>Condition</dt>
              <dd>{displayValue(selectedToken.condition)}</dd>
            </div>
            <div>
              <dt>Requirement</dt>
              <dd>{displayValue(selectedToken.requirement)}</dd>
            </div>
          </dl>

          <div className="runtime-console-record-step-placeholders">
            <section>
              <span>Placeholder</span>
              <h5>Record draft</h5>
              <p>Record generation is not active in this task.</p>
            </section>
            <section>
              <span>Placeholder</span>
              <h5>Evidence / data</h5>
              <p>Evidence and measured data are outside this read-only workspace task.</p>
            </section>
            <section>
              <span>Placeholder</span>
              <h5>Review</h5>
              <p>Review workflow is not active for this step yet.</p>
            </section>
          </div>
        </>
      ) : (
        <p className="runtime-console-record-step-empty">
          Select a matrix token to review record context.
        </p>
      )}
    </aside>
  );
}
```

- [ ] **Step 4: Run the component test and verify it passes**

Run:

```powershell
cd frontend
npm test -- --run RecordStepWorkspacePanel
```

Expected: PASS with 3 tests.

---

### Task 2: Wire The Panel Into Matrix Projection

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`

- [ ] **Step 1: Update the existing projection test expectation**

In `ProjectWorkbenchMatrixProjectionPanel.test.tsx`, update the first test after token click from:

```tsx
const detail = screen.getByLabelText("Matrix token detail");
expect(detail).toBeTruthy();
expect(within(detail).getByText("Visual")).toBeTruthy();
expect(within(detail).getByText("No damage")).toBeTruthy();
```

to:

```tsx
const detail = screen.getByLabelText("Record Step Workspace");
expect(detail).toBeTruthy();
expect(within(detail).getByText("Visual")).toBeTruthy();
expect(within(detail).getByText("No damage")).toBeTruthy();
expect(within(detail).getByText("Record draft")).toBeTruthy();
expect(within(detail).getByText("Evidence / data")).toBeTruthy();
expect(within(detail).getByText("Review")).toBeTruthy();
```

- [ ] **Step 2: Run the projection test and verify it fails**

Run:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Expected: FAIL because the projection still renders `Matrix token detail`.

- [ ] **Step 3: Replace inline aside with the new component**

In `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`, add import:

```tsx
import { RecordStepWorkspacePanel } from "./RecordStepWorkspacePanel";
```

Then replace the inline `<aside className="runtime-console-matrix-token-detail" ...>` block with:

```tsx
<RecordStepWorkspacePanel
  selectedToken={selectedToken}
  statusLabel={
    selectedToken ? STATUS_LABELS[selectedToken.statusTone] : "Not selected"
  }
/>
```

Do not change:

- `fetchConfirmedMatrixTestRecordPreview`
- `buildMatrixProjectionViewModel`
- `findMatrixProjectionToken`
- `selectedTokenReference`
- token button click handling
- row/group rendering

- [ ] **Step 4: Run the projection test and verify it passes**

Run:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Expected: PASS with the existing projection tests.

---

### Task 3: Add Record Workspace Styles

**Files:**

- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Add styles near existing token detail rules**

In `frontend/src/workbench.css`, place the new styles near the existing `.runtime-console-matrix-token-detail` section around the matrix projection rules:

```css
.runtime-console-record-step-workspace {
  display: grid;
  align-content: start;
  gap: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-canvas);
  padding: 12px;
  min-width: 0;
}

.runtime-console-record-step-workspace-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.runtime-console-record-step-workspace-header h4,
.runtime-console-record-step-workspace-header p,
.runtime-console-record-step-empty {
  margin: 0;
}

.runtime-console-record-step-workspace-header > span,
.runtime-console-record-step-placeholders span,
.runtime-console-record-step-empty {
  color: var(--color-ink-muted);
  font-size: 12px;
}

.runtime-console-record-step-workspace-header > span,
.runtime-console-record-step-placeholders span {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  padding: 3px 6px;
  font-weight: 700;
}

.runtime-console-record-step-fields {
  display: grid;
  gap: 8px;
  margin: 0;
}

.runtime-console-record-step-fields div {
  display: grid;
  gap: 2px;
}

.runtime-console-record-step-fields dt {
  color: var(--color-ink-muted);
  font-size: 11px;
  font-weight: 700;
}

.runtime-console-record-step-fields dd {
  margin: 0;
  color: var(--color-ink);
  overflow-wrap: anywhere;
}

.runtime-console-record-step-placeholders {
  display: grid;
  gap: 8px;
}

.runtime-console-record-step-placeholders section {
  display: grid;
  gap: 4px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  padding: 9px;
}

.runtime-console-record-step-placeholders h5,
.runtime-console-record-step-placeholders p {
  margin: 0;
}

.runtime-console-record-step-placeholders h5 {
  color: var(--color-ink);
  font-size: 12px;
}

.runtime-console-record-step-placeholders p {
  color: var(--color-ink-muted);
  font-size: 12px;
  line-height: 1.4;
}
```

- [ ] **Step 2: Run frontend tests affected by styles and rendering**

Run:

```powershell
cd frontend
npm test -- --run RecordStepWorkspacePanel
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Expected: both pass.

---

### Task 4: Add Static Guard

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_270 guard test**

Append near the existing TASK_269 guard:

```python
def test_task270_record_step_workspace_panel_is_wired() -> None:
    projection_source = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "project-workbench"
        / "ProjectWorkbenchMatrixProjectionPanel.tsx"
    ).read_text(encoding="utf-8")
    workspace_source = (
        FRONTEND_ROOT
        / "src"
        / "features"
        / "project-workbench"
        / "RecordStepWorkspacePanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )
    workspace_source_lower = workspace_source.lower()

    assert "RecordStepWorkspacePanel" in projection_source
    assert "Record Step Workspace" in workspace_source
    for required_copy in [
        "Read-only step context",
        "Authority locked",
        "Sample quantity",
        "Record draft",
        "Evidence / data",
        "Review",
        "Placeholder",
        "Select a matrix token to review record context.",
    ]:
        assert required_copy in workspace_source
    for forbidden_copy in [
        "save",
        "generate",
        "upload",
        "approve",
    ]:
        assert forbidden_copy not in workspace_source_lower
    assert "<button" not in workspace_source
    assert "fetch(" not in workspace_source
    assert "fetchConfirmedMatrixTestRecordPreview" not in workspace_source
    assert "runtime-console-record-step-workspace" in styles_source
```

- [ ] **Step 2: Run the guard and verify it passes**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task270 or task269 or project_workbench"
```

Expected: PASS.

---

### Task 5: Full Verification

**Files:**

- No code changes unless verification exposes a defect.

- [ ] **Step 1: Run targeted frontend tests**

Run:

```powershell
cd frontend
npm test -- --run RecordStepWorkspacePanel
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Expected: all targeted tests pass.

- [ ] **Step 2: Run frontend build**

Run:

```powershell
cd frontend
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Run Python static guards**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task270 or task269 or project_workbench"
```

Expected: pass.

- [ ] **Step 4: Run smoke flow regression**

Run:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Verify backend remains untouched**

Run:

```powershell
git diff --name-only -- backend
```

Expected: no output.

- [ ] **Step 6: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no errors. Existing CRLF warnings are acceptable if they match repository baseline.

---

### Task 6: Update Task State After Implementation

**Files:**

- Modify: `tasks/TASK_270_RECORD_STEP_WORKSPACE_PANEL.md`
- Modify: `docs/task_board.md`

- [ ] **Step 1: Mark the task file complete**

In `tasks/TASK_270_RECORD_STEP_WORKSPACE_PANEL.md`, update:

```md
## Status

Planned. Awaiting user approval before implementation.
```

to:

```md
## Status

Complete.
```

Add an implementation summary with validation results from Task 5.

- [ ] **Step 2: Mark the board complete**

In `docs/task_board.md`, update:

```md
> Current Active Task: TASK_270_RECORD_STEP_WORKSPACE_PANEL (planned; executable plan created, awaiting user approval before implementation).
```

to:

```md
> Current Active Task: none (`TASK_270_RECORD_STEP_WORKSPACE_PANEL` complete; awaiting next approved task).
```

Add a completion note stating that TASK_270 added a frontend-only read-only Record Step Workspace panel and did not introduce backend/API/database/StepInstance/execution persistence/Test Record Word generation scope.

---

## Self-Review Checklist

- [ ] The plan implements all TASK_270 guideline scope items.
- [ ] The plan keeps Project Workbench read-only with respect to Matrix authority.
- [ ] The plan does not introduce backend/API/database changes.
- [ ] The panel has no enabled edit/upload/generate/review actions.
- [ ] The copy stays operational and avoids future-feature overclaiming.
- [ ] Tests cover empty, selected, and placeholder states.
- [ ] Static guard prevents accidental direct API calls inside the detail component.

## Approval Gate

Stop here. Do not implement until the user explicitly approves TASK_270 execution.
