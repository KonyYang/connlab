# TASK_277_MATRIX_EDITOR_SINGLE_DRAFT_PUBLISH_FLOW

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_276 was complete and TASK_277 was approved as the current active task for execution. Implementation is now finished within approved frontend scope.

## Objective

Refocus Matrix Editor into a single draft editing and publish flow.

Users should not need to understand `draft`, `revision draft`, or `authority action` internals. They should see one editable Matrix surface, automatic saving, one Undo action, import/change controls, and one publish action:

```text
Confirm As Active Matrix
```

Confirming should publish the current saved editor state as the active authority, then return to Workbench so the Matrix projection refreshes from the newly active authority.

## User Feedback Source

This task is based on Matrix Editor smoke feedback:

- The page is always in draft editing mode; auto-save should be the normal behavior.
- The edit area should default to the Matrix shown in Workbench when an active Matrix exists.
- If there is no active Matrix, users can edit from scratch or import a document.
- Import from other projects and historical versions is useful but should not make the first task too complex.
- `Create Revision Draft` is an internal implementation concept and should not be exposed as a primary user action.
- `Confirm As Active Matrix` should save the current editor state, create/publish a new version only when the content differs, return to Workbench, and refresh the Workbench projection.
- `Back to Workbench` means return without publishing.
- The header and action zones are currently too large and repetitive.
- `Current State Editing Draft`, `Draft Actions`, `Authority Actions`, action consequence copy, and redundant save/authority notices consume space without helping the operator.

## Scope

### In Scope

Frontend-first Matrix Editor workflow and UI refactor:

1. Replace the exposed draft/revision mental model with a single user-facing editing flow.
2. Remove user-facing `Create Revision Draft`.
3. Keep one publish action:
   - `Confirm As Active Matrix`
4. Make `Confirm As Active Matrix` internally choose the correct existing API:
   - first authority: `confirmProjectMatrixDraft`
   - revision authority: `confirmProjectMatrixRevisionDraft`
5. Before confirming, flush the latest editor payload through `saveProjectMatrixDraft` when there are unsaved edits.
6. If a project already has an active Matrix and no editable draft is loaded, ensure an editable revision draft internally using existing APIs only when needed for editing/publish (lazy creation), instead of asking the user to click `Create Revision Draft`.
7. Prevent no-change publish when the editor content is unchanged from the active authority baseline.
   - Use a frontend baseline signature if existing APIs do not provide a dedicated no-change response.
   - Evaluate no-change against the latest saved/normalized draft snapshot used for publish, not only pre-save in-memory payload.
8. After successful confirm, call `onBackToWorkbench()` so Workbench remounts/reloads the active Matrix projection.
9. Keep auto-save and one `Undo` action.
10. Keep document import and selected-group adjustment as editor tools.
11. Compress the header to:
    - page label: `Matrix Editor`
    - `Back to Workbench`
    - one project identity line: `LTR or temporary project id · product description · test description`
    - compact save state: `Saved`, `Saving...`, `Unsaved changes`, or `Save failed`
12. Remove or collapse:
    - `Project workbench` shell label in Matrix Editor context if it appears as page title
    - `Current State Editing Draft`
    - `Draft Actions`
    - `Authority Actions`
    - action consequence paragraphs under buttons
    - redundant saved/active-authority explanatory banners
    - top metric blocks such as `Groups`, `Steps`, `Items` if they are not part of the editing grid itself
13. Move action buttons into a compact Matrix toolbar near the existing `Undo` row.
14. Preserve the current Matrix grid editing behavior, import preview behavior, group selection behavior, validation guards, and auto-save guard behavior unless explicitly modified by this task.

### Out Of Scope

Do not implement in TASK_277:

- cross-project Matrix import
- historical version picker UI
- full backend unified publish API
- backend schema changes
- permission/approval workflow
- StepInstance or test execution persistence
- Test Record generation behavior
- report, fee, image, evidence, or AI behavior
- broad Matrix grid editing redesign
- destructive cleanup of draft history

If existing APIs cannot safely satisfy a true unified publish contract, TASK_277 should implement the frontend single-flow shell with current APIs and document the backend follow-up separately.

## Expected Files

Likely implementation files:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
- `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Task tracking files:

- `tasks/TASK_277_MATRIX_EDITOR_SINGLE_DRAFT_PUBLISH_FLOW.md`
- `docs/task_277_matrix_editor_single_draft_publish_flow_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## Acceptance Criteria

1. Matrix Editor no longer exposes `Create Revision Draft`.
2. Matrix Editor no longer shows `Draft Actions` or `Authority Actions` headings.
3. Matrix Editor no longer renders action consequence paragraphs under each action button.
4. Matrix Editor no longer renders the large `Current State` / `Editing Draft` banner.
5. Matrix Editor header is compact and uses `Matrix Editor` as the page context.
6. Matrix Editor header includes one LTR/temp-id-first project identity line and does not foreground BU/requester metadata.
7. Matrix Editor has one visible publish button: `Confirm As Active Matrix`.
8. `Confirm As Active Matrix` flushes unsaved edits before publishing.
9. `Confirm As Active Matrix` publishes either first authority or revision authority through the correct existing API.
10. `Confirm As Active Matrix` does not create a new confirmed version when current editor content matches the active authority baseline.
11. Successful confirm returns to Workbench.
12. Workbench projection refreshes to the newly active Matrix after return.
13. `Back to Workbench` returns without publishing.
14. Auto-save status remains visible but compact.
15. `Undo` remains available as the single local rollback action.
16. Document import and selected-group adjustment remain reachable as compact Matrix toolbar actions.
17. No backend files are changed unless the approved plan explicitly identifies an unavoidable backend contract gap.

## Validation Plan

Run frontend component tests:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace
npm run build
```

Run static and smoke guards from repository root:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task277 or task276 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --name-only -- backend
git diff --check
```

Manual browser smoke:

```text
http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/matrix-editor
```

Check:

- no visible `Create Revision Draft`
- no `Draft Actions` / `Authority Actions`
- no large `Current State` banner
- compact header and compact toolbar
- edit a Matrix cell, wait for auto-save, confirm, return to Workbench
- Workbench Matrix projection reflects the confirmed Matrix
- Back to Workbench returns without publishing

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is mostly a frontend workflow and information-architecture refactor with existing APIs and existing tests.
- It requires careful state-flow control around auto-save and confirm, but the relevant code is localized in Matrix Editor feature files.
- The main risk is accidentally changing persistence semantics; this can be controlled with targeted tests and an explicit no-backend-change guard.

## Completion Notes

Implemented as a frontend-only workflow refactor:

- Unified one-button publish flow (`Confirm As Active Matrix`) while keeping existing first-confirm/revision-confirm API routing internally.
- Removed user-facing `Create Revision Draft`, `Confirm Revision`, `Draft Actions`, `Authority Actions`, and large `Current State` banner.
- Compacted header and moved Matrix actions into a compact toolbar near `Undo`.
- Added/updated interaction tests and static guards for TASK_277 behavior.
- Updated legacy static guards (`TASK_221/243/244/259`) to remain compatible with the new TASK_277 flow while preserving prior scope assertions.

Validation summary:

- `cd frontend && npm test -- --run MatrixEditorWorkspace` passed (`4 passed`)
- `cd frontend && npm run build` passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task277 or task276 or matrix_editor"` passed (`37 passed`)
- `py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`)
- `git diff --name-only -- backend` returned no output
- `git diff --check` passed with CRLF working-copy warnings only

Scope boundary held: no backend/API/domain/storage changes.
