# TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE

Status: complete
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Workstream: Post-Phase-11 Matrix-driven Laboratory Execution workflow refinement
Last Updated: 2026-05-25

## Current Execution Context

Current task status:

```text
TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE
```

Allowed reason:

- `TASK_261` to `TASK_268` are complete.
- `docs/task_board.md` currently has no active implementation task before this planning step.
- `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md` recommends TASK_269 after Group Selection completeness guard.
- The user explicitly requested this TASK_269 task file and executable plan.

Implementation and validation are complete.

## Objective

Replace the Workbench group-card smoke-preview mental model with a read-only Matrix table projection prototype.

The operator should see the active confirmed Matrix as:

```text
Rows: Test item / section step definitions
Columns: selected groups
Cells: clickable step tokens
```

This improves Matrix to Test Record continuity by making Project Workbench feel like a laboratory execution cockpit driven by the confirmed Matrix authority.

## Baseline

Completed baseline:

- `TASK_263` exposes `GET /api/projects/{project_id}/confirmed-matrix/test-record-preview`.
- `TASK_264` added `TestRecordPreviewSmokePanel`, which displays confirmed Matrix preview as group cards/tables.
- `TASK_265` validates the smoke chain from Matrix import commit to confirmed Test Record preview.
- `TASK_266` to `TASK_268` improved Matrix Workspace navigation, import session continuity, and group selection completeness.

Current Workbench gap:

- The Workbench still emphasizes smoke group cards and runtime placeholder surfaces.
- The user cannot scan the active confirmed Matrix in its native row-by-group shape.
- Step tokens are not yet presented as matrix cells that can drive a downstream record workspace.

## Scope

In scope:

- Frontend-only Project Workbench projection prototype.
- Use existing `fetchConfirmedMatrixTestRecordPreview(projectId)` API and DTOs.
- Transform confirmed preview groups into a read-only matrix projection table.
- Render rows by stable step context: sequence, test item, section, method, condition, requirement.
- Render columns by selected confirmed groups.
- Render non-empty cells as clickable step token buttons.
- Add placeholder status colors with reserved meanings:
  - gray = not started
  - blue = in progress
  - green = completed/pass
  - red = failed
  - yellow = review required
  - purple = reopened/retest
- Open a compact read-only detail panel when a matrix token is clicked.
- Keep authority editing out of Workbench.
- Add component tests and static shell guardrails.

Out of scope:

- No backend API changes.
- No database/schema migration.
- No StepInstance persistence.
- No LLCR runtime persistence.
- No structured execution data persistence.
- No report engine.
- No Test Record Word generation.
- No evidence/image upload implementation.
- No AI recommendation.
- No permission or approval workflow.
- No multi-matrix merge/append implementation.
- No authority mutation from Project Workbench.

## UX Requirements

The projection must be:

- Read-only authority view.
- Matrix-native, not a detached list of group cards.
- Dense but readable on the ConnLab Workbench surface.
- Clear about loading, not-ready, empty, and error states.
- Explicit that the source is the active Confirmed Matrix.
- Able to select a step token and show a useful detail panel.

The detail panel in this task is a prototype only. It may show:

- Group.
- Step token.
- Test item.
- Section.
- Method.
- Condition.
- Requirement / remarks.
- Sample quantity.
- Placeholder status.

The detail panel must not expose editable execution fields, file upload, evidence persistence, generated Word record actions, or authority edit actions.

## Expected Impact Files

Expected frontend changes:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Expected documentation changes after approved implementation:

- `tasks/TASK_269_PROJECT_WORKBENCH_MATRIX_PROJECTION_PROTOTYPE.md`
- `docs/task_269_project_workbench_matrix_projection_prototype_plan.md`
- `docs/task_board.md`

Avoid modifying:

- backend application services
- backend API routes
- storage models/repositories
- database migrations
- Matrix Workspace editing behavior
- TASK_261 import commit API
- TASK_263 confirmed Matrix preview API

## Acceptance Criteria

- Project Workbench renders a Matrix Projection prototype from active Confirmed Matrix preview data.
- Projection rows are grouped by test item / section / method / condition / requirement.
- Projection columns are selected confirmed groups only.
- Non-empty projection cells render clickable step token buttons.
- Clicking a token opens a read-only step detail panel.
- Placeholder status colors are present and documented in UI copy or class names.
- Not-ready, empty, loading, and error states remain explicit.
- Projection is read-only and does not mutate Matrix authority.
- Existing Matrix Workspace and TASK_261 to TASK_268 smoke-flow behavior remain unchanged.
- No backend files are modified.

## Validation

Minimum validation after approved implementation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task269 or task264 or project_workbench"
```

```powershell
cd frontend; npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

```powershell
cd frontend; npm run build
```

Smoke-flow regression safety:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded frontend projection and UX prototype.
- It consumes an existing typed read-only API and does not require backend design.
- The main work is deriving a table view from existing DTOs, preserving UI boundaries, and writing focused component/static tests.
- Medium reasoning is enough if the worker keeps the prototype read-only and avoids pulling TASK_270 or TASK_271 scope forward.

## Required Executable Plan Before Implementation

Executable plan:

```text
docs/task_269_project_workbench_matrix_projection_prototype_plan.md
```

Do not implement before the user explicitly approves the plan.

## Residual Risks

- `ConfirmedMatrixTestRecordPreview` is grouped by group first, so the frontend must derive row identity from step context. This is acceptable for a prototype but may later need a backend row identity if row ordering or duplicate test item names become ambiguous.
- Placeholder status colors are not persisted execution truth. They must remain clearly prototype-derived until a future task implements execution state.
- This task introduces a useful token detail panel, but the full Record Step Workspace is reserved for `TASK_270`.

## Completion Notes

- Delivered frontend-only Project Workbench Matrix projection prototype using existing confirmed preview API.
- Replaced bottom Workbench panel mount from `TestRecordPreviewSmokePanel` to `ProjectWorkbenchMatrixProjectionPanel`.
- Added selector-based row-by-group projection derivation and local read-only token detail panel.
- Added projection table/status/detail styles and responsive behavior.
- Added component tests and static shell guardrails for TASK_269.
- Updated TASK_264 static guard to remain compatible after TASK_269 panel replacement.

## Validation Results

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task269 or task264 or project_workbench"
```

Result: `3 passed, 107 deselected`

```powershell
cd frontend; npm test -- --run ProjectWorkbenchMatrixProjectionPanel
```

Result: `4 passed`

```powershell
cd frontend; npm run build
```

Result: passed

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Result: `1 passed`

```powershell
git diff --name-only -- backend
```

Result: no output (backend untouched)

