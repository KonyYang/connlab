# Matrix Editor Temporary Session Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current Matrix Editor draft/revision workflow with a temporary editing session model. The user sees `Cancel` and `Confirm Matrix`; backend draft/revision mechanics remain internal.

**Architecture:** Add a narrow Matrix Editor session read/publish boundary if existing APIs cannot cleanly express this workflow. Frontend owns local editing interaction. Backend remains authoritative for active authority, source snapshot lineage, and confirm validation. No new persistence table is planned.

**Tech Stack:** FastAPI, SQLAlchemy repositories, Pydantic DTOs, React + TypeScript, Vitest, pytest.

---

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

`TASK_278_MATRIX_EDITOR_TEMPORARY_SESSION_FLOW` completed implementation baseline (Phase 11).

## Allowed Reason

TASK_277 is complete and `docs/task_board.md` has no active implementation task. The user explicitly requested a dedicated follow-up task to collapse visible revision draft semantics into an internal temporary session model.

## Product Model

Matrix Editor should have this user-facing model:

```text
Edit current Workbench Matrix -> Cancel or Confirm Matrix
```

The system model behind it:

```text
Temporary Matrix Editor Session
  based_on: current active ConfirmedMatrix
  source: full SourceMatrix snapshot behind that authority or newly parsed Word Matrix
  selected_groups: editable subset of source groups
  visible_rows/cells: editable Matrix content
```

Important constraints:

- There is no user-visible saved draft restore flow.
- Closing, canceling, or leaving mid-edit does not make the next entry resume those edits.
- The next entry starts from Workbench's current active Matrix and its full source snapshot.
- `Change selected Groups` must use the full source snapshot, not only currently published groups.
- If the full source snapshot behind an active Matrix cannot be loaded, the editor opens the current active selected Matrix content, disables `Change selected Groups`, and tells the user: `Original source Matrix is unavailable. Use Change Source Matrix to reselect groups.`
- No-change confirm has one fixed protocol: HTTP 200 with `publish_status: "no_change"` and message `No Matrix changes to confirm.`
- `revision draft` remains an internal implementation detail only.

## File Responsibilities

- `backend/application/matrix_editor_session_service.py`
  - Build Matrix Editor seed DTO from active authority plus full source snapshot.
  - Confirm session payload into new active authority through existing domain mechanics.
  - Translate stale active-authority conflicts into business-readable errors.
- `backend/api/routes_matrix_editor_session.py`
  - Thin typed routes for session seed and confirm.
- `backend/api/dependencies.py`, `backend/api/main.py`
  - Wire the new route/service if the plan's API path is implemented.
- `backend/infrastructure/storage/repositories/source_matrix_import.py`
  - Provide source snapshot lookup by source snapshot id if missing.
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`
  - Remain internal lineage storage only if confirm uses draft records.
- `frontend/src/api/client.ts`
  - Add typed Matrix Editor session DTOs and request helpers.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - Load editor seed instead of newest persisted draft.
  - Own temporary local editor state.
  - Route `Cancel` and `Confirm Matrix`.
  - Use session source snapshot for group selection.
- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
  - Separate editing tools from completion actions.
- `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
  - Keep source preview/session state local and non-resumable.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
  - Cover temporary session, cancel discard, confirm, source-backed group selection, missing-source fallback, no-active group-selection disabled state, and stale-message translation.
- `frontend/src/workbench.css`
  - Place `Cancel`/`Confirm Matrix` as completion actions.
- `tests/unit/test_frontend_shell_files.py`
  - Static guards for no raw revision/stale wording and no default draft resume.

## Task 1: Define Backend Session Contract

**Files:**

- Add: `backend/application/matrix_editor_session_service.py`
- Add or modify: `backend/api/routes_matrix_editor_session.py`
- Modify: `backend/api/dependencies.py`
- Modify: `backend/api/main.py`
- Modify only if needed: source Matrix repository
- Add: `tests/unit/test_matrix_editor_session_service.py`
- Add: `tests/integration/test_matrix_editor_session_api.py`

- [ ] **Step 1: Add tests for active-authority editor seed**

Create a service test that seeds:

- active ConfirmedMatrix with selected groups
- source snapshot with additional unselected groups

Assert the editor seed returns:

- active authority id/revision
- visible rows/cells from active authority
- source groups from full source snapshot
- selected group keys matching active authority groups

- [ ] **Step 2: Add tests for no-active editor seed**

Assert a project without active Matrix returns a clear empty/import-first seed shape or a typed not-ready response, depending on selected API contract.

- [ ] **Step 3: Add tests for active-authority seed with missing source snapshot**

Seed an active ConfirmedMatrix whose `source_snapshot_id` cannot be resolved. Assert the session seed:

- still returns active authority visible rows/cells and selected groups
- marks `source_status` or equivalent as unavailable
- returns a user-facing message exactly equivalent to:

```text
Original source Matrix is unavailable. Use Change Source Matrix to reselect groups.
```

The frontend must use this state to disable `Change selected Groups`.

- [ ] **Step 4: Add source snapshot lookup support if missing**

If repositories cannot fetch a `SourceMatrixSnapshot` by `snapshot_id`, add a narrow repository method such as:

```python
def get_snapshot(self, snapshot_id: str) -> SourceMatrixSnapshot | None:
    ...
```

Do not expose storage models directly.

- [ ] **Step 5: Implement session seed service**

Suggested output DTO shape:

```python
MatrixEditorSessionSeed(
    project_id=str,
    active_confirmed_matrix_id=str | None,
    active_confirmed_revision=int | None,
    source_snapshot_id=str | None,
    source_groups=tuple[...],
    source_rows=tuple[...],
    source_cells=tuple[...],
    selected_group_keys=tuple[str, ...],
    editor_rows=tuple[...],
    editor_cells=tuple[...],
    source_status="available" | "unavailable" | "not_required",
    source_unavailable_message=str | None,
)
```

- [ ] **Step 6: Add confirm-session tests**

Cover:

- unchanged session returns HTTP 200 with `publish_status: "no_change"` and message `No Matrix changes to confirm.`
- changed session creates a new active authority
- stale active authority returns business message equivalent to:

```text
Matrix was updated. Reload the latest Matrix to continue.
```

- [ ] **Step 7: Implement confirm-session service**

Preferred behavior:

- accept current active authority id/revision expected by the session
- validate active authority is still current
- validate selected groups/sample quantities/token content
- return `publish_status: "no_change"` for unchanged content instead of raising an error
- internally create any required draft/lineage records only during confirm
- confirm into a new active authority
- return the confirmed snapshot or a compact publish response

Do not create user-visible draft restore semantics.

- [ ] **Step 8: Add typed API routes**

Suggested routes:

```text
GET  /api/projects/{project_id}/matrix-editor/session
POST /api/projects/{project_id}/matrix-editor/session/confirm
```

Route bodies remain thin and call application services.

The confirm route response must use a stable discriminated shape:

```json
{
  "publish_status": "published | no_change",
  "message": "No Matrix changes to confirm.",
  "confirmed_matrix": null
}
```

For stale active authority, return a typed non-200 response with a stable code such as `active_matrix_changed`; the frontend must display `Matrix was updated. Reload the latest Matrix to continue.`

## Task 2: Convert Matrix Editor To Temporary Local Session

**Files:**

- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

- [ ] **Step 1: Add frontend session DTOs and client helpers**

Add typed helpers for:

```ts
fetchMatrixEditorSession(projectId)
confirmMatrixEditorSession(projectId, payload)
```

- [ ] **Step 2: Replace initial draft loading**

Matrix Editor initial load should use the session seed endpoint, not `listProjectMatrixDrafts` newest-first behavior.

Expected:

- active authority exists -> initialize from active authority content
- full source snapshot exists -> keep it as group selection source
- active authority exists but source snapshot missing -> initialize from active authority content, disable group selection, show source-unavailable guidance
- no active authority -> empty/import-first editor session

- [ ] **Step 3: Remove default persisted draft resume semantics**

The editor must not default to:

- latest persisted project matrix draft
- existing revision draft from older active authority
- unconfirmed source import draft from a prior page visit

Existing API helpers may remain for compatibility if no longer used by initial load.

- [ ] **Step 4: Keep session state local**

Local edits, imported source preview, selected groups, and cell changes live in Matrix Editor state until confirm.

Visible copy should avoid "Saved" if it implies persisted recoverability. Prefer compact copy such as:

```text
Editing
Changes not confirmed
Ready to confirm
```

Use final exact copy during implementation based on existing style.

- [ ] **Step 5: Update `Change selected Groups`**

Ensure group selection choices come from the session full source groups.

Regression condition:

- Active Matrix publishes groups 1, 2, and 5
- Source Matrix contains groups 1 through 12
- `Change selected Groups` shows all 12 choices

Also add a missing-source test:

- active authority exists
- source status is unavailable
- `Change selected Groups` is disabled
- the guidance text is visible

Also add a no-active/no-source test:

- no active authority
- no source seed exists
- `Change selected Groups` is disabled until import/source exists

- [ ] **Step 6: Update `Change Source Matrix`**

After Word preview/selection:

- replace the current local source snapshot/preview
- update group choices from the new source
- do not create a resumable default draft
- do not navigate away

If current backend import commit must persist source lineage before confirm, keep it internal and do not use it as next default load.

## Task 3: Refactor Visible Actions And Copy

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- Modify: `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
- Modify: `frontend/src/workbench.css`
- Modify: `tests/unit/test_frontend_shell_files.py`

- [ ] **Step 1: Rename publish button**

Replace visible `Confirm As Active Matrix` with:

```text
Confirm Matrix
```

- [ ] **Step 2: Replace back link with Cancel**

Render a real secondary button:

```text
Cancel
```

It should not look like a text link.

- [ ] **Step 3: Group completion actions**

Place `Cancel` and `Confirm Matrix` together, separated from edit tools such as:

- Undo
- Change selected Groups
- Change Source Matrix

Preferred placement: right side or bottom-right action area, depending on existing layout constraints.

- [ ] **Step 4: Add discard confirmation**

When local changes exist and user clicks `Cancel`, use business-readable copy:

```text
Discard current Matrix edits and return to Workbench?
```

Do not mention draft/revision.

- [ ] **Step 5: Translate stale conflict**

Any backend stale active-authority conflict should display:

```text
Matrix was updated. Reload the latest Matrix to continue.
```

Do not show raw backend text containing `Revision draft is stale`.

- [ ] **Step 6: Static guards**

Add/update guards to reject user-facing occurrences in Matrix Editor UI:

- `Confirm As Active Matrix`
- `revision draft`
- `Create Revision Draft`
- `Confirm Revision`
- `Revision draft is stale relative to current active confirmed matrix`

Allow these terms only in tests/docs where explicitly scoped.

## Task 4: Confirm Flow And Workbench Refresh

**Files:**

- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Existing Workbench files only if refresh/remount currently fails

- [ ] **Step 1: Add no-change test**

If user enters and confirms without changing anything:

- no new active authority is created
- confirm-session API returns `publish_status: "no_change"`
- user sees `No Matrix changes to confirm.`
- frontend test must not accept no-change as 409 or 422

- [ ] **Step 2: Add changed-session publish test**

Edit a cell or group selection, click `Confirm Matrix`, assert:

- confirm-session API called with expected active authority id/revision
- successful response calls `onBackToWorkbench`

- [ ] **Step 3: Add cancel discard test**

Edit a cell, click `Cancel`, confirm discard, assert:

- no confirm API called
- no save/resume API called
- `onBackToWorkbench` called

- [ ] **Step 4: Add next-entry reset test**

Simulate:

- enter editor
- edit
- cancel
- render editor again

Assert second render initializes from active session seed, not the canceled edit.

- [ ] **Step 5: Preserve right-side Group Step Workspace behavior**

Add or keep tests proving TASK_278 does not redesign the right-side Group Step Workspace:

- selected group/step context updates from the temporary editor session
- existing note/sample/step output surfaces remain present
- no StepInstance, image/evidence persistence, result persistence, or report behavior is introduced

- [ ] **Step 5: Manual Workbench refresh smoke**

Verify in browser:

- confirm returns to Workbench
- Workbench Matrix projection reflects newly active authority

## Task 5: Documentation And Board Sync

**Files:**

- Modify: `tasks/TASK_278_MATRIX_EDITOR_TEMPORARY_SESSION_FLOW.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

- [ ] **Step 1: Update task completion notes**

Summarize:

- temporary editor session model
- Cancel discard semantics
- full source snapshot group selection
- Confirm Matrix publish behavior

- [ ] **Step 2: Update task board**

Set TASK_278 complete only after implementation and validation.

- [ ] **Step 3: Update plan index**

Move current active plan to none after completion and set latest completed plan to TASK_278.

## Validation Checklist

Run:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace
npm run build
```

Run:

```powershell
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\integration\test_matrix_editor_session_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task278 or task277 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
py -m pytest tests\integration\test_confirmed_matrix_authority_api.py -q
git diff --check
```

Manual browser smoke:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f
```

Expected browser results:

- Matrix Editor shows `Cancel` and `Confirm Matrix`
- no user-facing revision/draft wording
- `Change selected Groups` lists all source groups
- missing source snapshot disables `Change selected Groups` and shows source-unavailable guidance
- no active/no source seed disables `Change selected Groups`
- cancel discards edits and next entry reloads Workbench Active Matrix
- confirm publishes and returns to Workbench
- no-change confirm returns `publish_status: "no_change"` and shows `No Matrix changes to confirm.`
- stale active authority is shown as reload-latest guidance

## Risks

- Existing Matrix draft persistence is currently used as both editing state and authority lineage. TASK_278 must separate user-facing session semantics from internal lineage records without deleting historical compatibility.
- Source snapshot lookup by active authority may require a small backend read model because ConfirmedMatrix only carries selected groups while group selection needs full source groups.
- Removing persistent auto-save may require copy changes so users do not believe unconfirmed edits are recoverable after leaving.
- Import commit behavior may currently persist draft/source state earlier than the desired temporary session model. If this cannot be fully deferred in one task, implementation must keep persisted records internal and ensure next entry ignores unconfirmed records.

## Non-Goals

- No saved draft restore UI.
- No historical version picker.
- No StepInstance/execution persistence.
- No image/evidence/report/fee/AI workflow.
- No permissions or multi-user locking.
- No database table unless implementation review proves it unavoidable and user approves the revised plan.
