# TASK_163 Project Registry Cancelled Visibility Filter Plan

> Status: proposed
> Created: 2026-05-10
> Phase: Phase 10F - Real public-drive LTR workbook operational closure

---

## 1. Current State

`TASK_162` soft-cancelled historical no-LTR Project residues and wrote audit records. The Project Registry frontend still renders every row returned by `listProjects()`, so cancelled records remain visible and still affect metrics, search results, and pagination counts.

Current relevant file:

- `frontend/src/pages/ProjectListPage.tsx`

Current behavior:

- `rows` stores all Projects.
- `metrics = buildMetrics(rows)` uses all Projects.
- `filteredRows = filterRows(rows, deferredSearch)` searches all Projects.
- Pagination uses `filteredRows`.
- `cancelled` Projects have progress `0` but still appear as normal registry rows.

---

## 2. UX Decision

Use a restrained product-table control, not a new page and not a card-heavy cleanup surface.

Physical scene: a lab coordinator is checking the daily Project Registry on a Windows workstation after cleanup; cancelled records are audit history, not the normal work queue.

Design:

- Add a small checkbox/toggle in the registry toolbar: `Show cancelled`.
- Default unchecked.
- When unchecked, hide `project.status === "cancelled"` before search and pagination.
- When checked, include cancelled rows.
- Show a compact count label such as `25 cancelled hidden` when applicable.

This keeps the registry operational while preserving traceability.

---

## 3. Implementation Plan

### 3.1 Frontend State And Selectors

File: `frontend/src/pages/ProjectListPage.tsx`

Add:

- `showCancelled` state, default `false`.
- helper `visibleRowsForScope(rows, showCancelled)`.
- helper `cancelledRowCount(rows)`.

Change:

- Build metrics from scoped visible rows, not raw rows.
- Search scoped visible rows.
- Reset pagination when `showCancelled` changes.
- Empty state says:
  - no rows in database: existing `No projects yet`
  - rows exist but all visible rows hidden due to cancelled filter: message tells operator to enable `Show cancelled`
  - search no match: existing search guidance remains.

### 3.2 Toolbar Control

File: `frontend/src/pages/ProjectListPage.tsx`

Add one compact checkbox/toggle near search and refresh:

- Label: `Show cancelled`
- Uses normal form control semantics.
- Avoid modal, extra page, or disabled fake filter button.

### 3.3 Styling

File: `frontend/src/project-dashboard.css`

Add small styles for:

- `.registry-scope-toggle`
- `.registry-scope-note`

Keep the visual vocabulary consistent with existing toolbar buttons and search controls.

### 3.4 Tests

File: `tests/unit/test_frontend_shell_files.py`

Add or extend a static frontend test to assert:

- `showCancelled` state exists.
- `visibleRowsForScope` or equivalent helper exists.
- `Show cancelled` appears in the page source.
- metrics/search use scoped rows rather than all rows.

Validation:

- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_dashboard or task163"`
- `npm run build` from `frontend`

---

## 4. Risks

- The backend still returns cancelled Projects. This is intentional for now because TASK_163 is a UI visibility task, not an API contract change.
- Opening a cancelled Project remains allowed. This is intentional for traceability until a later task defines read-only cancelled-workbench behavior.
- Metrics will become "visible scope" metrics, not all-time database metrics. This is intentional for daily registry usability, and the hidden-count label preserves awareness.

---

## 5. Acceptance

The task is complete when Project Registry no longer shows cancelled Projects by default, the operator can reveal them explicitly, and build/static validation passes.
