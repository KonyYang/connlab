# Project Workbench Matrix Projection Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render the active confirmed Matrix in Project Workbench as a read-only row-by-group matrix projection with clickable step tokens.

**Architecture:** Frontend-only prototype that consumes the existing `fetchConfirmedMatrixTestRecordPreview(projectId)` API. A selector transforms confirmed preview groups into table rows and group columns; a Workbench component renders loading/not-ready/empty/error/ready states and a local read-only detail panel for selected tokens.

**Tech Stack:** React, TypeScript, Vitest, Testing Library, CSS in `frontend/src/workbench.css`, pytest static shell tests.

---

## Anti-Skip Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE`
- Allowed reason: TASK_261 to TASK_268 are complete, `docs/task_board.md` has no active implementation task before this planning step, and the user requested TASK_269 from the post-Phase-11 guideline.

## Scope Lock

Implement only a frontend read-only Matrix Projection prototype in Project Workbench:

- Use existing confirmed Matrix Test Record preview API.
- Transform preview groups into a matrix table.
- Render clickable token cells.
- Show a compact local read-only selected token detail panel.

Do not implement:

- Backend/API/schema changes.
- StepInstance persistence.
- LLCR runtime persistence.
- Evidence/image upload.
- Report engine.
- Test Record Word generation.
- AI recommendation.
- Permission/approval workflow.
- Matrix authority edits from Workbench.
- Multi-matrix merge.

## File Responsibilities

- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`
  - New pure selectors and types for deriving matrix rows, group columns, token cells, placeholder status tone, and selected-token detail from `ConfirmedMatrixTestRecordPreview`.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
  - New Workbench component that fetches confirmed Matrix preview, renders projection states, displays the matrix table, and shows selected token detail.

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
  - Component tests for ready projection, token click detail, not-ready, empty, and error states.

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Replace the bottom `TestRecordPreviewSmokePanel` mount with `ProjectWorkbenchMatrixProjectionPanel`.
  - Keep other runtime console structure unchanged.

- `frontend/src/workbench.css`
  - Add projection table, token status, legend, and detail panel styling near existing `runtime-console-test-record-preview` or matrix runtime styles.

- `tests/unit/test_frontend_shell_files.py`
  - Add static guardrails for TASK_269 wiring and scope boundaries.

- `tasks/TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE.md`
  - Update to complete only after approved implementation and validation pass.

- `docs/task_board.md`
  - Update status only after approved implementation and validation pass.

## UX Decisions

1. Source is active Confirmed Matrix only.
   - The component calls `fetchConfirmedMatrixTestRecordPreview(projectId)`.
   - It does not read Matrix draft or SourceMatrix directly.

2. Projection rows are derived by stable step context.
   - Row key uses `sequence`, `test_item`, `section`, `method`, `condition`, and `requirement`.
   - This avoids collapsing steps that share a token but differ in context.

3. Projection columns are preview groups.
   - Only selected confirmed groups appear because TASK_263 preview already uses active Confirmed Matrix.

4. Status colors are placeholders.
   - They reserve the status language but do not claim persisted execution state.
   - Use deterministic local mapping so tests are stable:
     - token sequence divisible by 6 -> `review`
     - divisible by 5 -> `retest`
     - divisible by 4 -> `failed`
     - divisible by 3 -> `passed`
     - divisible by 2 -> `in_progress`
     - otherwise -> `not_started`

5. Token detail is local and read-only.
   - TASK_270 will formalize Record Step Workspace.
   - TASK_269 detail panel must not show editable fields or generation actions.

## Task 1: Add Projection Selectors

**Files:**

- Create: `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`

- [ ] **Step 1: Create selector file**

Create `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`:

```ts
import {
  type ConfirmedMatrixTestRecordPreview,
  type ConfirmedMatrixTestRecordPreviewGroup,
  type ConfirmedMatrixTestRecordPreviewStep,
} from "../../api/client";

export type MatrixProjectionStatusTone =
  | "not_started"
  | "in_progress"
  | "passed"
  | "failed"
  | "review"
  | "retest";

export type MatrixProjectionGroupColumn = {
  groupKey: string;
  groupLabel: string;
  sampleQuantityExpression: string;
};

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

export type MatrixProjectionRow = {
  rowKey: string;
  sequence: number;
  testItem: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  cellsByGroupKey: Record<string, MatrixProjectionTokenCell[]>;
};

export type MatrixProjectionViewModel = {
  confirmedMatrixId: string;
  groupColumns: MatrixProjectionGroupColumn[];
  rows: MatrixProjectionRow[];
  totalTokenCount: number;
};

function normalizeText(value: string | null | undefined): string {
  return (value ?? "").trim();
}

function buildRowKey(step: ConfirmedMatrixTestRecordPreviewStep): string {
  return [
    step.sequence,
    normalizeText(step.test_item),
    normalizeText(step.section),
    normalizeText(step.method),
    normalizeText(step.condition),
    normalizeText(step.requirement),
  ].join("::");
}

export function deriveMatrixProjectionStatusTone(sequence: number): MatrixProjectionStatusTone {
  if (sequence % 6 === 0) {
    return "review";
  }
  if (sequence % 5 === 0) {
    return "retest";
  }
  if (sequence % 4 === 0) {
    return "failed";
  }
  if (sequence % 3 === 0) {
    return "passed";
  }
  if (sequence % 2 === 0) {
    return "in_progress";
  }
  return "not_started";
}

function buildTokenCell(
  group: ConfirmedMatrixTestRecordPreviewGroup,
  step: ConfirmedMatrixTestRecordPreviewStep
): MatrixProjectionTokenCell {
  return {
    tokenReference: `${group.group_key}:${step.sequence}:${step.raw_token}`,
    groupKey: group.group_key,
    groupLabel: group.group_label,
    rawToken: step.raw_token,
    sequence: step.sequence,
    statusTone: deriveMatrixProjectionStatusTone(step.sequence),
    sampleQuantityExpression: group.sample_quantity_expression || "-",
    testItem: step.test_item,
    section: step.section,
    method: step.method,
    condition: step.condition,
    requirement: step.requirement,
  };
}

export function buildMatrixProjectionViewModel(
  preview: ConfirmedMatrixTestRecordPreview
): MatrixProjectionViewModel {
  const groupColumns = preview.groups.map((group) => ({
    groupKey: group.group_key,
    groupLabel: group.group_label,
    sampleQuantityExpression: group.sample_quantity_expression || "-",
  }));
  const rowsByKey = new Map<string, MatrixProjectionRow>();
  let totalTokenCount = 0;

  preview.groups.forEach((group) => {
    group.steps.forEach((step) => {
      const rowKey = buildRowKey(step);
      const existingRow = rowsByKey.get(rowKey);
      const row = existingRow ?? {
        rowKey,
        sequence: step.sequence,
        testItem: step.test_item,
        section: step.section,
        method: step.method,
        condition: step.condition,
        requirement: step.requirement,
        cellsByGroupKey: {},
      };
      const cell = buildTokenCell(group, step);
      row.cellsByGroupKey[group.group_key] = [
        ...(row.cellsByGroupKey[group.group_key] ?? []),
        cell,
      ];
      rowsByKey.set(rowKey, row);
      totalTokenCount += 1;
    });
  });

  return {
    confirmedMatrixId: preview.confirmed_matrix_id,
    groupColumns,
    rows: Array.from(rowsByKey.values()).sort((left, right) => left.sequence - right.sequence),
    totalTokenCount,
  };
}

export function findMatrixProjectionToken(
  viewModel: MatrixProjectionViewModel,
  tokenReference: string | null
): MatrixProjectionTokenCell | null {
  if (!tokenReference) {
    return null;
  }
  for (const row of viewModel.rows) {
    for (const cells of Object.values(row.cellsByGroupKey)) {
      const match = cells.find((cell) => cell.tokenReference === tokenReference);
      if (match) {
        return match;
      }
    }
  }
  return null;
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

## Task 2: Add Matrix Projection Panel

**Files:**

- Create: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`

- [ ] **Step 1: Create component**

Create `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`:

```tsx
import { useEffect, useMemo, useState, type ReactElement } from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixTestRecordPreview,
  type ConfirmedMatrixTestRecordPreview,
} from "../../api/client";
import {
  buildMatrixProjectionViewModel,
  findMatrixProjectionToken,
  type MatrixProjectionStatusTone,
} from "./projectWorkbenchMatrixProjectionSelectors";

type PreviewState = "loading" | "ready" | "empty" | "not_ready" | "error";

type ProjectWorkbenchMatrixProjectionPanelProps = {
  projectId: string;
};

const STATUS_LABELS: Record<MatrixProjectionStatusTone, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  passed: "Completed / pass",
  failed: "Failed",
  review: "Review required",
  retest: "Reopened / retest",
};

export function ProjectWorkbenchMatrixProjectionPanel({
  projectId,
}: ProjectWorkbenchMatrixProjectionPanelProps): ReactElement {
  const [state, setState] = useState<PreviewState>("loading");
  const [preview, setPreview] = useState<ConfirmedMatrixTestRecordPreview | null>(null);
  const [selectedTokenReference, setSelectedTokenReference] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setState("loading");
    setPreview(null);
    setSelectedTokenReference(null);
    void fetchConfirmedMatrixTestRecordPreview(projectId)
      .then((response) => {
        if (!active) {
          return;
        }
        setPreview(response);
        setState(response.preview_status === "empty" ? "empty" : "ready");
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        if (error instanceof ApiRequestError && error.status === 404) {
          setState("not_ready");
          return;
        }
        console.error("Failed to load confirmed Matrix projection.", error);
        setState("error");
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const viewModel = useMemo(
    () => (preview && preview.preview_status === "ready" ? buildMatrixProjectionViewModel(preview) : null),
    [preview]
  );
  const selectedToken = useMemo(
    () => (viewModel ? findMatrixProjectionToken(viewModel, selectedTokenReference) : null),
    [selectedTokenReference, viewModel]
  );

  return (
    <section className="runtime-console-matrix-projection" aria-label="Matrix Projection">
      <header className="runtime-console-matrix-projection-header">
        <div>
          <p className="eyebrow">Confirmed Matrix Projection</p>
          <h3>Matrix execution projection</h3>
        </div>
        <span>Read-only authority view</span>
      </header>

      {state === "loading" ? <p className="fine-print">Loading Matrix projection...</p> : null}
      {state === "not_ready" ? (
        <p className="runtime-console-matrix-projection-empty">
          No active confirmed matrix yet. Confirm Matrix authority first.
        </p>
      ) : null}
      {state === "empty" ? (
        <p className="runtime-console-matrix-projection-empty">
          Active confirmed matrix found, but no previewable Matrix tokens are available.
        </p>
      ) : null}
      {state === "error" ? (
        <p className="error">Unable to load Matrix projection. Try again after confirming Matrix authority.</p>
      ) : null}

      {state === "ready" && viewModel ? (
        <div className="runtime-console-matrix-projection-layout">
          <div className="runtime-console-matrix-projection-main">
            <div className="runtime-console-matrix-projection-summary">
              <span>Confirmed: {viewModel.confirmedMatrixId}</span>
              <span>Groups: {viewModel.groupColumns.length}</span>
              <span>Rows: {viewModel.rows.length}</span>
              <span>Tokens: {viewModel.totalTokenCount}</span>
            </div>
            <div className="runtime-console-matrix-projection-legend" aria-label="Status color legend">
              {Object.entries(STATUS_LABELS).map(([tone, label]) => (
                <span className={`runtime-console-matrix-token-status-${tone}`} key={tone}>
                  {label}
                </span>
              ))}
            </div>
            <div className="runtime-console-matrix-projection-table-wrap">
              <table className="runtime-console-matrix-projection-table">
                <thead>
                  <tr>
                    <th>Seq</th>
                    <th>Test item</th>
                    <th>Section</th>
                    {viewModel.groupColumns.map((group) => (
                      <th key={group.groupKey}>
                        <span>{group.groupLabel}</span>
                        <small>{`Samples: ${group.sampleQuantityExpression}`}</small>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {viewModel.rows.map((row) => (
                    <tr key={row.rowKey}>
                      <td>{row.sequence}</td>
                      <td>{row.testItem}</td>
                      <td>{row.section}</td>
                      {viewModel.groupColumns.map((group) => {
                        const cells = row.cellsByGroupKey[group.groupKey] ?? [];
                        return (
                          <td key={`${row.rowKey}:${group.groupKey}`}>
                            {cells.length > 0 ? (
                              <div className="runtime-console-matrix-token-stack">
                                {cells.map((cell) => (
                                  <button
                                    className={`runtime-console-matrix-token runtime-console-matrix-token-status-${cell.statusTone}${
                                      selectedTokenReference === cell.tokenReference ? " is-selected" : ""
                                    }`}
                                    key={cell.tokenReference}
                                    type="button"
                                    onClick={() => setSelectedTokenReference(cell.tokenReference)}
                                  >
                                    {cell.rawToken}
                                  </button>
                                ))}
                              </div>
                            ) : (
                              <span className="runtime-console-matrix-empty-cell">-</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <aside className="runtime-console-matrix-token-detail" aria-label="Matrix token detail">
            <h4>Selected matrix token</h4>
            {selectedToken ? (
              <dl>
                <div><dt>Group</dt><dd>{selectedToken.groupLabel}</dd></div>
                <div><dt>Token</dt><dd>{selectedToken.rawToken}</dd></div>
                <div><dt>Status</dt><dd>{STATUS_LABELS[selectedToken.statusTone]}</dd></div>
                <div><dt>Samples</dt><dd>{selectedToken.sampleQuantityExpression}</dd></div>
                <div><dt>Test item</dt><dd>{selectedToken.testItem}</dd></div>
                <div><dt>Section</dt><dd>{selectedToken.section}</dd></div>
                <div><dt>Method</dt><dd>{selectedToken.method || "-"}</dd></div>
                <div><dt>Condition</dt><dd>{selectedToken.condition || "-"}</dd></div>
                <div><dt>Requirement</dt><dd>{selectedToken.requirement || "-"}</dd></div>
              </dl>
            ) : (
              <p>Select a matrix token to inspect its read-only record context.</p>
            )}
          </aside>
        </div>
      ) : null}
    </section>
  );
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

## Task 3: Wire Projection Panel Into Workbench

**Files:**

- Modify: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

- [ ] **Step 1: Replace smoke panel import**

Replace:

```ts
import { TestRecordPreviewSmokePanel } from "./TestRecordPreviewSmokePanel";
```

with:

```ts
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";
```

- [ ] **Step 2: Replace bottom panel mount**

In `.runtime-console-bottom`, replace:

```tsx
<TestRecordPreviewSmokePanel projectId={project.project_id} />
```

with:

```tsx
<ProjectWorkbenchMatrixProjectionPanel projectId={project.project_id} />
```

Keep `TestRecordPreviewSmokePanel.tsx` in the repository for TASK_264 historical tests unless a later task explicitly removes it.

- [ ] **Step 3: Build**

Run:

```powershell
cd frontend; npm run build
```

Expected:

```text
build passes
```

## Task 4: Add Projection Styles

**Files:**

- Modify: `frontend/src/workbench.css`

- [ ] **Step 1: Add CSS near existing runtime console projection or test-record preview styles**

Add:

```css
.runtime-console-matrix-projection {
  display: grid;
  gap: 12px;
  min-width: 0;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-surface);
  padding: 14px;
}

.runtime-console-matrix-projection-header,
.runtime-console-matrix-projection-summary,
.runtime-console-matrix-projection-legend {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.runtime-console-matrix-projection-header h3,
.runtime-console-matrix-projection-header p {
  margin: 0;
}

.runtime-console-matrix-projection-header > span,
.runtime-console-matrix-projection-summary span {
  color: var(--color-ink-muted);
  font-size: 12px;
}

.runtime-console-matrix-projection-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 280px);
  gap: 12px;
  min-width: 0;
}

.runtime-console-matrix-projection-main {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.runtime-console-matrix-projection-table-wrap {
  overflow: auto;
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.runtime-console-matrix-projection-table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  font-size: 12px;
}

.runtime-console-matrix-projection-table th,
.runtime-console-matrix-projection-table td {
  border-bottom: 1px solid var(--color-border);
  border-right: 1px solid var(--color-border);
  padding: 7px 8px;
  vertical-align: top;
}

.runtime-console-matrix-projection-table th {
  background: var(--color-surface-muted);
  color: var(--color-ink);
  text-align: left;
  white-space: nowrap;
}

.runtime-console-matrix-projection-table th small {
  display: block;
  color: var(--color-ink-muted);
  font-weight: 600;
  white-space: normal;
}

.runtime-console-matrix-token-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.runtime-console-matrix-token,
.runtime-console-matrix-projection-legend span {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 3px 6px;
  font-size: 11px;
  font-weight: 700;
}

.runtime-console-matrix-token {
  cursor: pointer;
}

.runtime-console-matrix-token.is-selected {
  outline: 2px solid var(--color-primary);
  outline-offset: 1px;
}

.runtime-console-matrix-token-status-not_started {
  background: #eef2f7;
  color: #647084;
}

.runtime-console-matrix-token-status-in_progress {
  background: #e7f0fb;
  color: #1f66d1;
}

.runtime-console-matrix-token-status-passed {
  background: #eef9f4;
  color: #2f8f68;
}

.runtime-console-matrix-token-status-failed {
  background: #fff0ef;
  color: #c2413a;
}

.runtime-console-matrix-token-status-review {
  background: #fff7e8;
  color: #9a641c;
}

.runtime-console-matrix-token-status-retest {
  background: #f1edff;
  color: #6f54b8;
}

.runtime-console-matrix-empty-cell,
.runtime-console-matrix-projection-empty {
  color: var(--color-ink-muted);
}

.runtime-console-matrix-token-detail {
  display: grid;
  align-content: start;
  gap: 10px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-canvas);
  padding: 12px;
}

.runtime-console-matrix-token-detail h4,
.runtime-console-matrix-token-detail p {
  margin: 0;
}

.runtime-console-matrix-token-detail dl {
  display: grid;
  gap: 8px;
  margin: 0;
}

.runtime-console-matrix-token-detail div {
  display: grid;
  gap: 2px;
}

.runtime-console-matrix-token-detail dt {
  color: var(--color-ink-muted);
  font-size: 11px;
  font-weight: 700;
}

.runtime-console-matrix-token-detail dd {
  margin: 0;
  color: var(--color-ink);
  overflow-wrap: anywhere;
}

@media (max-width: 1100px) {
  .runtime-console-matrix-projection-layout {
    grid-template-columns: 1fr;
  }
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

## Task 5: Add Component Tests

**Files:**

- Create: `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`

- [ ] **Step 1: Create test file**

Create `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`:

```tsx
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ApiRequestError } from "../../api/client";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";

const apiMocks = vi.hoisted(() => ({
  fetchConfirmedMatrixTestRecordPreview: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    fetchConfirmedMatrixTestRecordPreview: apiMocks.fetchConfirmedMatrixTestRecordPreview,
  };
});

describe("ProjectWorkbenchMatrixProjectionPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders confirmed groups as matrix columns and step tokens as clickable cells", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockResolvedValue({
      project_id: "P1",
      confirmed_matrix_id: "cm-1",
      preview_status: "ready",
      groups: [
        {
          group_key: "g1",
          group_label: "Group 1",
          sample_quantity_expression: "3",
          step_count: 1,
          steps: [
            {
              sequence: 1,
              raw_token: "1",
              test_item: "Visual",
              section: "6.1",
              method: "EIA-364-18B",
              condition: "10x",
              requirement: "No damage",
            },
          ],
        },
        {
          group_key: "g2",
          group_label: "Group 2",
          sample_quantity_expression: "5",
          step_count: 1,
          steps: [
            {
              sequence: 1,
              raw_token: "1",
              test_item: "Visual",
              section: "6.1",
              method: "EIA-364-18B",
              condition: "10x",
              requirement: "No damage",
            },
          ],
        },
      ],
    });

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    await waitFor(() => {
      expect(apiMocks.fetchConfirmedMatrixTestRecordPreview).toHaveBeenCalledWith("P1");
    });
    expect(await screen.findByText("Matrix execution projection")).toBeTruthy();
    expect(screen.getByText("Confirmed: cm-1")).toBeTruthy();
    expect(screen.getByText("Group 1")).toBeTruthy();
    expect(screen.getByText("Group 2")).toBeTruthy();
    expect(screen.getByText("Samples: 3")).toBeTruthy();
    expect(screen.getByText("Samples: 5")).toBeTruthy();

    const tokens = screen.getAllByRole("button", { name: "1" });
    fireEvent.click(tokens[0]);
    expect(screen.getByLabelText("Matrix token detail")).toBeTruthy();
    expect(screen.getByText("Visual")).toBeTruthy();
    expect(screen.getByText("No damage")).toBeTruthy();
  });

  it("renders not-ready state for missing active confirmed matrix", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockRejectedValue(
      new ApiRequestError("Not Found", 404, null)
    );

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("No active confirmed matrix yet. Confirm Matrix authority first.")
    ).toBeTruthy();
  });

  it("renders empty state for active matrix with no previewable tokens", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockResolvedValue({
      project_id: "P1",
      confirmed_matrix_id: "cm-1",
      preview_status: "empty",
      groups: [],
    });

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("Active confirmed matrix found, but no previewable Matrix tokens are available.")
    ).toBeTruthy();
  });

  it("renders error state for unexpected API failure", async () => {
    apiMocks.fetchConfirmedMatrixTestRecordPreview.mockRejectedValue(new Error("boom"));

    render(<ProjectWorkbenchMatrixProjectionPanel projectId="P1" />);

    expect(
      await screen.findByText("Unable to load Matrix projection. Try again after confirming Matrix authority.")
    ).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run component tests**

Run:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Expected:

```text
ProjectWorkbenchMatrixProjectionPanel tests pass
```

## Task 6: Add Static Guardrails

**Files:**

- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Add TASK_269 static test**

Add near the TASK_268/TASK_264 static tests:

```python
def test_task269_project_workbench_matrix_projection_prototype_is_wired() -> None:
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    projection_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixProjectionPanel.tsx"
    ).read_text(encoding="utf-8")
    selector_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "projectWorkbenchMatrixProjectionSelectors.ts"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    assert "ProjectWorkbenchMatrixProjectionPanel" in layout_source
    assert "<ProjectWorkbenchMatrixProjectionPanel projectId={project.project_id} />" in layout_source
    assert "<TestRecordPreviewSmokePanel projectId={project.project_id} />" not in layout_source
    assert "fetchConfirmedMatrixTestRecordPreview" in projection_source
    assert "Matrix execution projection" in projection_source
    assert "Read-only authority view" in projection_source
    assert "Matrix token detail" in projection_source
    assert "buildMatrixProjectionViewModel" in selector_source
    assert "deriveMatrixProjectionStatusTone" in selector_source
    assert "runtime-console-matrix-projection-table" in styles_source
    assert "runtime-console-matrix-token-status-not_started" in styles_source
    assert "runtime-console-matrix-token-status-retest" in styles_source
```

- [ ] **Step 2: Run static tests**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task269 or task264 or project_workbench"
```

Expected:

```text
TASK_269 and relevant Workbench checks pass
```

## Task 7: Regression Verification And Docs Sync

**Files:**

- Modify after validation: `tasks/TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE.md`
- Modify after validation: `docs/task_board.md`

- [ ] **Step 1: Run full verification**

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task269 or task264 or project_workbench"
```

Expected:

```text
passes
```

Run:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchMatrixProjectionPanel
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
git diff --name-only -- backend
```

Expected:

```text
no output
```

- [ ] **Step 3: Update task file after implementation**

After validation passes, update:

```markdown
Status: complete
Last Updated: 2026-05-24
```

Add validation results and completion notes to `tasks/TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE.md`.

- [ ] **Step 4: Update task board after implementation**

Update `docs/task_board.md`:

```markdown
> Status: ... + TASK_269 complete
> Last Updated: 2026-05-24
> Current Active Task: none (`TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE` complete; awaiting next approved task).
```

Add a TASK_269 completion note with deliverables, validation commands, and scope boundary.

## Review Checklist Before Implementation

- [ ] Task remains frontend-only.
- [ ] No backend files are modified.
- [ ] Projection uses active Confirmed Matrix preview only.
- [ ] Workbench projection is read-only.
- [ ] Matrix authority edits remain in Matrix Workspace.
- [ ] No StepInstance or execution persistence is introduced.
- [ ] Token detail panel remains read-only and local to the prototype.
- [ ] TASK_270 Record Step Workspace is not implemented early.
- [ ] TASK_271 Test Record Word generation is not implemented early.

## Execution Handoff

After this plan is approved, implement with `superpowers:executing-plans` in this session. Execute task by task, run verification commands at the listed checkpoints, update task docs only after validation passes, and stop after TASK_269 completion. Do not proceed to TASK_270 or any follow-up task.

