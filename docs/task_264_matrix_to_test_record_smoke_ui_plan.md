# TASK_264 Matrix To Test Record Smoke UI Plan

## Protocol Status

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI`
- Why allowed now: `docs/task_board.md` marks TASK_264 as planned active after TASK_263 completion.
- Implementation status: planning only.
- Approval gate: implementation remains blocked until user explicitly approves this plan.

## Goal

Add a frontend-only, read-only smoke panel in Project Workbench that consumes TASK_263 API:

```text
GET /api/projects/{project_id}/confirmed-matrix/test-record-preview
```

The panel must prove:

1. Selected confirmed groups propagate into Test Record preview.
2. Sample quantity expression is visible per group.
3. Unselected groups are not shown.

## Scope Lock

Implement:

- API client types + fetch function for TASK_263 endpoint.
- One named Workbench feature component:
  - `TestRecordPreviewSmokePanel`
- Narrow composition into existing Workbench layout.
- Loading/ready/empty/404/error state handling.
- Focused frontend tests and static guard updates.

Do not implement:

- Backend/API/schema changes.
- Matrix import/edit/confirm flow changes.
- Fee/report/equipment feature changes.
- Execution inputs, result inputs, StepInstance, evidence upload.
- File generation (.docx/.pdf/.xlsx).
- Broad Workbench redesign.

## Existing Code Facts

From current codebase:

- Workbench route shell:
  - `frontend/src/pages/ProjectWorkbenchPage.tsx`
- Main Workbench composition:
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Runtime model selection:
  - `selectProjectRuntimeConsoleModel(...)`
- Existing API client has no TASK_263 frontend symbols yet:
  - `frontend/src/api/client.ts`

Current Workbench layout already includes legacy/mock surfaces (including fee-like sections). TASK_264 will not remove them; it will add a narrow read-only smoke panel without new fee/report/equipment actions.

## Placement Decision

Placement:

- Add `TestRecordPreviewSmokePanel` inside `ProjectWorkbenchLayout`, in downstream consumer area, as a dedicated read-only section.

Reason:

- Keeps Matrix authority editing separate from downstream derived preview.
- Avoids embedding in Matrix Editor grid or import selection flow.
- Smallest change with predictable blast radius.

## API Client Contract

File:

- `frontend/src/api/client.ts`

Add:

- `ConfirmedMatrixTestRecordPreviewStatus = "ready" | "empty"`
- `ConfirmedMatrixTestRecordPreviewStep`
- `ConfirmedMatrixTestRecordPreviewGroup`
- `ConfirmedMatrixTestRecordPreview`
- `fetchConfirmedMatrixTestRecordPreview(projectId: string): Promise<ConfirmedMatrixTestRecordPreview>`

Request/response rules:

- No request body.
- Uses `GET /api/projects/{project_id}/confirmed-matrix/test-record-preview`.
- Treat `404` as not-ready (no active confirmed authority), not hard crash.

## UI State Model

File:

- New: `frontend/src/features/project-workbench/TestRecordPreviewSmokePanel.tsx`

Props:

- `projectId: string`

Internal state:

- `idle/loading`
- `ready` (API success + `preview_status === "ready"`)
- `empty` (API success + `preview_status === "empty"`)
- `not_ready` (HTTP 404)
- `error` (other failures)

Render rules:

- Title: `Test Record Preview`
- Subtext: read-only from confirmed authority.
- `ready`: show groups in response order; each group shows:
  - `group_label` + `group_key`
  - `sample_quantity_expression`
  - `step_count`
  - compact step rows with:
    - `sequence`, `raw_token`, `test_item`, `section`, `method`, `condition`, `requirement`
- `empty`: show business-readable message that authority exists but no previewable steps.
- `not_ready`: show business-readable message to confirm Matrix authority first.
- `error`: show concise generic error message.

Interaction rules:

- No edit/save/confirm buttons.
- No input fields.
- Optional read-only refresh button is allowed only if it re-fetches same endpoint and adds no workflow branching.

## File-Level Changes

Create:

- `frontend/src/features/project-workbench/TestRecordPreviewSmokePanel.tsx`

Modify:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Optional test file (if needed by current test setup):

- `frontend/src/features/project-workbench/TestRecordPreviewSmokePanel.test.tsx`

## Testing Strategy

Static guard updates:

- Ensure new component file exists.
- Ensure client has new types/function.
- Ensure layout composes new panel.
- Ensure panel is read-only (no edit/confirm/report/fee/equipment action labels in component source).

Component behavior tests (if added):

- `ready`: renders selected group(s), sample quantity, step rows.
- `empty`: renders empty authority message.
- `404`: renders not-ready message.
- Verify absent group label from mock payload is not rendered.

## Validation Commands

Minimum:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task264 or test_record_preview or project_workbench"
```

Frontend tests:

```powershell
cd frontend; npm test -- --run TestRecordPreviewSmokePanel
```

If no dedicated component test is created, use:

```powershell
cd frontend; npm test -- --run ProjectWorkbench
```

Build:

```powershell
cd frontend; npm run build
```

Backend contract safety:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_test_record_preview_api.py -q
```

## Risks And Fallbacks

Risk: Workbench layout is large and mixed with runtime/mock content.

Fallback:

- Add a small isolated feature component and inject it in one stable section without refactoring surrounding surfaces.

Risk: API 404 handling might be treated as generic error.

Fallback:

- In client/panel mapping, branch 404 into explicit `not_ready` UI state.

Risk: Overreach into fee/report/equipment due to existing sections in page.

Fallback:

- Restrict TASK_264 acceptance to the new panel behavior only; do not alter unrelated sections.

## Acceptance Checklist

- [ ] `fetchConfirmedMatrixTestRecordPreview` exists in `client.ts` with typed DTOs.
- [ ] Workbench composes `TestRecordPreviewSmokePanel`.
- [ ] Panel shows loading, ready, empty, not-ready(404), and generic error.
- [ ] Ready state displays group label/key, sample quantity, step count, compact steps.
- [ ] Unselected group labels from fixture/mock do not render.
- [ ] Panel has no edit/save/confirm/report/fee/equipment actions.
- [ ] No backend files changed.
- [ ] `tests/unit/test_frontend_shell_files.py` updated and passing.
- [ ] Frontend build passes.

## Next Step After Approval

Implement TASK_264 exactly per this plan, then update:

- `tasks/TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI.md`
- `docs/task_board.md`

only after validation passes.
