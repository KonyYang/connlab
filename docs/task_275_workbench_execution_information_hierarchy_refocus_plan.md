# Workbench Execution Information Hierarchy Refocus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Project Workbench first-screen information match lab execution needs by reducing duplicate status UI, simplifying the Matrix table, and moving setup/output concepts into a compact materials area.

**Architecture:** Frontend-only. Reuse the existing Workbench layout, ConfirmedMatrix preview API, projection selectors, and mock/placeholder Step Workspace data. Do not introduce new DTOs or backend behavior.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, CSS, existing FastAPI client functions, pytest static guards.

---

## Anti-Skip Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_275_WORKBENCH_EXECUTION_INFORMATION_HIERARCHY_REFOCUS` (planned)
- Allowed reason: `TASK_274_WORKBENCH_STEP_WORKSPACE_REFOCUS` is complete, the task board has no active implementation task, and user smoke testing clarified the next Workbench hierarchy correction.

Implementation must wait for explicit user approval after this plan is reviewed.

## Required Project Protocol

Before implementation, use:

- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product context

## Product / UI Context

ConnLab is a `product` UI. The physical scene is a lab engineer checking a project during daily execution. The user needs group progress, failed items, Matrix steps, and output material readiness. They do not need repeated project-created/LTR-created facts or detailed audit cards on the first screen.

Design direction:

- Group progress before test-item totals.
- Matrix table before dashboard cards.
- Setup supports execution.
- Step before report.
- Four visible execution states only on the first screen.

## Scope Boundary

In scope:

- Header simplification.
- Setup/output-material section replacement.
- Matrix local action placement.
- Matrix table structure changes.
- Status legend reduction to four categories.
- Bottom Matrix rows for sample sizes and placeholders.
- Recent activity and fee card simplification.
- Frontend tests, CSS, static guards, task state docs.

Out of scope:

- Backend changes.
- New API endpoints or DTOs.
- StepInstance or execution persistence.
- Real completion-date calculation.
- Real fee calculation.
- Real output generation or image upload activation.
- Report, fee, AI, equipment, permission, approval workflow implementation.

## Existing Baseline

Observed implementation facts:

- `ProjectWorkbenchLayout` owns header, metrics, readiness cards, filter bar, main Matrix area, right Step Workspace, and bottom cards.
- `ProjectWorkbenchMatrixProjectionPanel` renders the ConfirmedMatrix-derived Matrix projection table.
- `projectWorkbenchMatrixProjectionSelectors.ts` builds group columns, rows, token cells, sample quantity expressions, and status tones.
- Current visible states include more than the desired four categories: not started, in progress, pass, failed, review, retest.
- Current Matrix header displays group sample quantity in each group column.
- Current table includes `Seq` and `Section`.
- Bottom layout includes Recent Activity and Fee Estimate cards.

## File Structure

Modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Simplify header.
  - Replace readiness strip with output-material section.
  - Move Matrix action into Matrix toolbar.
  - Remove Step Workspace `Matrix` and `Record` controls.
  - Hide persistent Recent Activity card.
  - Simplify Fee Estimate card.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - Remove `Seq` and `Section` columns.
  - Remove sample quantity from group headers.
  - Add bottom rows for sample sizes, estimated completion date, and status.
  - Limit displayed status legend to four categories.

- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`
  - Add a first-screen status tone mapping helper if needed.
  - Preserve existing raw status data for future detailed views.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - Assert simplified columns, bottom rows, and four-state legend.

- `frontend/src/workbench.css`
  - Adjust header, setup/output area, Matrix bottom rows, and simplified bottom section styles.

- `tests/unit/test_frontend_shell_files.py`
  - Add TASK_275 static guards.

- `tasks/TASK_275_WORKBENCH_EXECUTION_INFORMATION_HIERARCHY_REFOCUS.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

No backend files should be modified.

---

### Task 1: Update Matrix Projection Tests

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`

- [ ] **Step 1: Add assertion for removed columns**

In the ready-state test, assert the table no longer has `Seq` or `Section` column headers:

```ts
expect(screen.queryByRole("columnheader", { name: "Seq" })).toBeNull();
expect(screen.queryByRole("columnheader", { name: "Section" })).toBeNull();
```

- [ ] **Step 2: Add assertion for simplified group headers**

Assert group headers show only group labels and do not include `Samples:`:

```ts
expect(screen.getByRole("columnheader", { name: "Group 1" })).toBeTruthy();
expect(screen.getByRole("columnheader", { name: "Group 2" })).toBeTruthy();
expect(screen.queryByText("Samples: 3")).toBeNull();
expect(screen.queryByText("Samples: 5")).toBeNull();
```

- [ ] **Step 3: Add assertion for bottom rows**

Assert bottom rows display sample sizes and placeholders:

```ts
// Ensure `within` is imported from "@testing-library/react" in this test file.
const sampleSizesRow = screen.getByText("Sample sizes").closest("tr");
expect(sampleSizesRow).toBeTruthy();
expect(screen.getByText("Sample sizes")).toBeTruthy();
expect(screen.getByText("Estimated completion date")).toBeTruthy();
expect(screen.getByText("Status")).toBeTruthy();
expect(within(sampleSizesRow as HTMLElement).getByText("3")).toBeTruthy();
expect(within(sampleSizesRow as HTMLElement).getByText("5")).toBeTruthy();
expect(screen.getAllByText("Not scheduled")).toHaveLength(2);
expect(screen.getAllByText("Pending execution data")).toHaveLength(2);
```

- [ ] **Step 4: Add assertion for four-state legend**

Assert visible legend contains only:

```ts
expect(screen.getByText("Not started")).toBeTruthy();
expect(screen.getByText("In progress")).toBeTruthy();
expect(screen.getByText("Pass")).toBeTruthy();
expect(screen.getByText("Failed")).toBeTruthy();
expect(screen.queryByText("Review required")).toBeNull();
expect(screen.queryByText("Reopened / retest")).toBeNull();
```

### Task 2: Simplify Matrix Projection Rendering

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- Modify: `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`

- [ ] **Step 1: Add first-screen status mapping helper**

If the selector currently exposes `review` or `retest`, add a helper that maps first-screen status to:

```ts
export type MatrixProjectionVisibleStatusTone =
  | "not_started"
  | "in_progress"
  | "passed"
  | "failed";

export function toVisibleMatrixProjectionStatusTone(
  tone: MatrixProjectionStatusTone
): MatrixProjectionVisibleStatusTone {
  if (tone === "failed") {
    return "failed";
  }
  if (tone === "passed") {
    return "passed";
  }
  if (tone === "not_started") {
    return "not_started";
  }
  return "in_progress";
}
```

- [ ] **Step 2: Replace legend labels**

Use the visible status label map:

```ts
const VISIBLE_STATUS_LABELS: Record<MatrixProjectionVisibleStatusTone, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  passed: "Pass",
  failed: "Failed",
};
```

- [ ] **Step 3: Remove `Seq` and `Section` columns**

Render only:

```tsx
<th>Test item</th>
{viewModel.groupColumns.map((group) => (
  <th key={group.groupKey}>{group.groupLabel}</th>
))}
```

- [ ] **Step 4: Remove sample quantity from group headers**

Do not render `Samples:` in header cells.

- [ ] **Step 5: Add bottom rows**

Inside the table body after normal rows, render:

```tsx
<tr className="runtime-console-matrix-meta-row">
  <th scope="row">Sample sizes</th>
  {viewModel.groupColumns.map((group) => (
    <td key={`sample:${group.groupKey}`}>{group.sampleQuantityExpression || "-"}</td>
  ))}
</tr>
<tr className="runtime-console-matrix-meta-row">
  <th scope="row">Estimated completion date</th>
  {viewModel.groupColumns.map((group) => (
    <td key={`eta:${group.groupKey}`}>Not scheduled</td>
  ))}
</tr>
<tr className="runtime-console-matrix-meta-row">
  <th scope="row">Status</th>
  {viewModel.groupColumns.map((group) => (
    <td key={`status:${group.groupKey}`}>Pending execution data</td>
  ))}
</tr>
```

### Task 3: Simplify Workbench Header And Actions

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

- [ ] **Step 1: Remove status badge from title**

Stop rendering `ProjectStatusBadge` next to the Workbench project title. Keep imports clean.

- [ ] **Step 2: Compose compact identity**

Render title/subtitle with project identity and product/test description:

```tsx
<h2>{project.product_name}</h2>
<div className="runtime-console-project-meta">
  <span>{latestLtr ?? `Temporary project ${project.project_id.slice(0, 8)}`}</span>
  <span>{project.business_unit || "Business unit not set"}</span>
  <span>{project.requestor}</span>
</div>
```

- [ ] **Step 3: Remove top Refresh and Edit Matrix Definition**

Remove topbar buttons for `Refresh` and `Edit Matrix Definition`.

- [ ] **Step 4: Add Matrix local action in Matrix toolbar**

In the Matrix toolbar, add:

```tsx
<button type="button" onClick={onOpenMatrixEditor}>Matrix</button>
```

Keep it near the Matrix projection heading.

### Task 4: Replace Readiness Strip With Setup / Output Materials

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Replace readiness heading**

Change the strip title from project readiness to:

```tsx
<p className="eyebrow">Project setup / output materials</p>
<strong>Preparation</strong>
```

- [ ] **Step 2: Remove repeated readiness items**

Do not render `Created project`, `LTR Number registered`, or `Matrix Authority` as strip cards.

- [ ] **Step 3: Render output-material items**

Render compact items:

```tsx
const outputItems = [
  { title: "Project folder", value: "Not recorded" },
  { title: "Source materials", value: "Available after folder creation" },
  { title: "Test Record", value: "Ready after Matrix confirmation" },
  { title: "Fee estimate", value: "Estimated total only" },
  { title: "Sample images", value: "Future evidence input" },
  { title: "Approval package", value: "Future output package" },
];
```

Use existing `RuntimeReadinessItem` if the component remains visually compact enough, or add a local compact renderer in the same file.

- [ ] **Step 4: Remove unclear `Open Setup Manager`**

Do not render `Open Setup Manager` in this task.

### Task 5: Clean Step Workspace Actions

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

- [ ] **Step 1: Remove `Matrix` button from Step Workspace**

The Matrix action now lives near the Matrix section, so remove the Step Workspace `Matrix` button.

- [ ] **Step 2: Remove `Record` button from Step Workspace**

The future Record entry belongs in setup/output materials, so remove the Step Workspace `Record` button.

- [ ] **Step 3: Keep `Image` disabled if still shown**

If `Image` remains in Step Workspace, keep:

```tsx
<button type="button" disabled title="Planned future action in Step Workspace.">
  Image
</button>
```

### Task 6: Simplify Bottom Cards

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Hide persistent Recent Activity card**

Remove `RecentActivitySurface` from the default `runtime-console-bottom` section.

- [ ] **Step 2: Add secondary history affordance if needed**

If a small affordance is needed, render a disabled or placeholder button in the setup/output area:

```tsx
<button type="button" disabled title="Activity history will open from this entry in a later task.">
  View activity history
</button>
```

- [ ] **Step 3: Simplify Fee Estimate card**

Render only total estimated fee:

```tsx
<article className="runtime-console-fee-total">
  <span>Total estimated fee</span>
  <strong>Pending estimate</strong>
</article>
```

Do not render spent or remaining values.

### Task 7: Add Static Guards

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_275 guard**

Assert:

```python
layout_source_lower = layout_source.lower()
assert "ltr number registered" not in layout_source_lower
assert "refresh" not in layout_source_lower
assert "edit matrix definition" not in layout_source_lower
assert "created project" not in layout_source_lower
assert "matrix authority" not in layout_source_lower
assert "open setup manager" not in layout_source_lower
assert "recent activity" not in layout_source_lower
assert "spent" not in layout_source_lower
assert "remaining" not in layout_source_lower
```

- [ ] **Step 2: Guard Matrix table simplification**

Assert:

```python
assert "<th>Seq</th>" not in projection_source
assert "<th>Section</th>" not in projection_source
assert "Samples:" not in projection_source
assert "Sample sizes" in projection_source
assert "Estimated completion date" in projection_source
assert "Pending execution data" in projection_source
```

- [ ] **Step 3: Guard four visible statuses**

Assert the projection panel does not render `Review required` or `Reopened / retest` in the first-screen legend, using lower-case source checks for resilience.

### Task 8: Verify

**Commands:**

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task275 or task274 or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --name-only -- backend
git diff --check
```

- [ ] **Step 1: Run projection tests**
- [ ] **Step 2: Run frontend build**
- [ ] **Step 3: Run static guards**
- [ ] **Step 4: Run integration smoke test**
- [ ] **Step 5: Confirm backend diff is empty**
- [ ] **Step 6: Run diff check**

### Task 9: Browser Smoke

**Target:**

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
```

- [ ] **Step 1: Open Workbench**

Confirm:

- no `LTR Number Registered` badge in title
- no top `Refresh`
- no top `Edit Matrix Definition`
- Matrix action is near Matrix projection
- setup/output area is compact and output-focused
- Matrix table has no `Seq` or `Section`
- group headers have no sample quantity
- bottom rows show `Sample sizes`, `Estimated completion date`, `Status`
- legend has four states only
- Recent Activity is not a persistent bottom card
- Fee estimate shows total only

### Task 10: Update Task State

**Files:**

- Modify: `tasks/TASK_275_WORKBENCH_EXECUTION_INFORMATION_HIERARCHY_REFOCUS.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Mark task complete only after validation**

Do not update completion state before commands pass or failures are documented.

- [ ] **Step 2: Stop**

Do not enter the next task.

---

## Review Checklist

Before final response, confirm:

- [ ] No backend/API/domain/storage files changed.
- [ ] Workbench header is simplified.
- [ ] Setup/output area replaces readiness repetition.
- [ ] Matrix table is simplified and has bottom metadata rows.
- [ ] Four visible Matrix statuses only.
- [ ] Recent Activity and Fee Estimate are reduced.
- [ ] No future workflows were made active.
- [ ] Tests, build, static guards, backend diff, and browser smoke are reported.
