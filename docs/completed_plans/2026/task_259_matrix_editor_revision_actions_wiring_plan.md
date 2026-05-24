# TASK_259 Matrix Editor Revision Actions Wiring Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_259_MATRIX_EDITOR_REVISION_ACTIONS_WIRING`
- Why this task is allowed now:
  - `TASK_258` completed backend revision draft creation and confirm-revision APIs.
  - `docs/task_board.md` recommends a controlled frontend wiring task for Matrix revision actions.
  - Matrix Editor already has persisted draft loading and save wiring from `TASK_256`.

This document is a plan only. No implementation should start until user approval.

## 1) Product/UI Context

`$impeccable` register: `product`.

Physical scene: a lab coordinator is working on a Windows workstation during daytime project preparation, reviewing Matrix authority state and making a controlled revision without needing to understand backend terminology.

UI strategy:

- restrained ConnLab workbench UI
- inline action/status controls, not modal-first
- clear state before action
- disabled reasons visible when action is blocked
- no future-scope controls

## 2) Task Goal

Expose the TASK_258 backend revision flow in Matrix Editor with minimal frontend wiring:

1. Create revision draft from active confirmed Matrix.
2. Load the returned revision draft into the current Matrix Editor grid.
3. Continue editing through existing Save.
4. Confirm the revision draft when it is persisted, clean, and valid.

MVP operator identity rule: Confirm Revision must send `confirmed_by: "connlab-operator"`. This is a fixed frontend fallback until a later approved auth/session task provides a real operator identity.

## 3) File-Level Change Plan

1. API client
   - Update `ProjectMatrixDraftRecord.source_import_id` to `string | null`.
   - Add `base_confirmed_matrix_id` to draft record DTO.
   - Add confirmed Matrix response DTOs if not already present in frontend client.
   - Add:
     - `createMatrixRevisionDraft(projectId)`
     - `confirmProjectMatrixRevisionDraft(projectId, projectMatrixDraftId, input)`
   - Define confirm-revision input as at least `{ confirmed_by: string; superseded_reason?: string | null }`.
   - The Matrix Editor implementation must call confirm-revision with `confirmed_by: "connlab-operator"`.

2. Matrix Editor state
   - Track current draft lineage:
     - `projectMatrixDraftId`
     - `projectMatrixDraftUpdatedAt`
     - `projectMatrixDraftBaseConfirmedMatrixId`
     - current draft kind inferred from `base_confirmed_matrix_id`
   - Keep existing Save payload and unsaved detection.
   - On create revision success, reuse existing `buildMatrixFromProjectMatrixDraft` and reset baseline signature.
   - Add local helper/selector functions for revision action state instead of scattering compound conditions through JSX. Keep them in the same file unless a small feature selector file is clearly lower risk.

3. Matrix Editor controls
   - Add restrained action control for `Create revision draft`.
   - Add restrained action control for `Confirm revision`.
   - Keep `Save` as the draft-edit persistence action.
   - Disable Confirm Revision when:
     - no persisted draft id
     - not a revision draft
     - unsaved changes exist
     - Matrix validation errors exist
     - a create/save/confirm request is running

4. Status and copy
   - Use business-readable copy:
     - `Revision draft loaded`
     - `Save changes before confirming revision`
     - `Current draft is not a revision draft`
     - `Revision confirmed`
   - Do not expose raw route names, stack traces, SQL, or backend enum names.

5. Tests
   - Extend `tests/unit/test_frontend_shell_files.py`.
   - Check API client symbols and endpoint strings.
   - Check Matrix Editor imports and action handlers.
   - Check disabled reason strings and no raw `fetch()` outside client.
   - Preserve TASK_256 save assertions.
   - Add at least one behavior-level frontend test with mocked API covering revision draft dirty-state gating: unsaved changes disable Confirm Revision; successful Save clears dirty state and enables Confirm Revision for a revision draft.

6. Documentation
   - Mark task complete in `tasks/TASK_259_MATRIX_EDITOR_REVISION_ACTIONS_WIRING.md`.
   - Update `docs/task_board.md` with status, deliverables, validation results, and next recommended action.

## 4) UX State Rules

Revision draft creation:

- Enabled only when not currently saving/creating/confirming.
- If backend returns 404 or 409, show a concise business-readable message.
- On success, load the returned draft and clear unsaved state.

Save:

- Existing Save remains unchanged.
- Save must continue to persist row/group/cell/sample quantity data.
- Save must preserve `base_confirmed_matrix_id` through backend response and frontend state.

Confirm Revision:

- Requires current draft to have `base_confirmed_matrix_id`.
- Requires no unsaved changes.
- Requires no Matrix validation errors.
- On success, show confirmed revision status.
- On success, keep the current revision draft view loaded. Do not switch the page into a read-only active confirmed authority view in this task.
- Do not silently create a revision draft during confirm.
- Always send `confirmed_by: "connlab-operator"` in this MVP slice. Do not prompt for an operator name and do not infer a real user identity that the app does not yet own.

## 5) API Error Mapping

Frontend should display stable operator messages:

- 404: active confirmed Matrix or draft not found
- 409: revision draft already exists or draft is stale
- 422: revision draft is not confirmable
- unexpected: action failed, retry after checking saved state

This task should not alter backend error contracts.

## 6) Out Of Scope

- Backend changes.
- Revision history browser.
- Active confirmed authority read-model UI.
- Runtime Console refresh.
- Step execution or StepInstance persistence.
- Report, fee, duration, equipment, Approval Package generation.
- Confirmed Step Output.
- Parser/import preview changes.
- Frontend architecture rewrite or component split beyond the minimum needed.
- Login/session/operator identity work.

## 7) Validation Plan

Frontend static wiring:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task259 or task256"
```

Behavior-level frontend test with mocked API:

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

Frontend build:

```powershell
cd frontend; npm run build
```

Manual smoke after approval and implementation:

1. Open Matrix Editor for a project with an active confirmed Matrix.
2. Create revision draft.
3. Confirm the draft loads into the grid and Save state is clean.
4. Make one edit and verify Confirm Revision is disabled until Save succeeds.
5. Save.
6. Confirm Revision and verify success message.

## 8) Review Checklist

- API calls remain centralized in `frontend/src/api/client.ts`.
- Matrix Editor does not directly call backend routes with raw `fetch()`.
- Confirm Revision cannot run on source-import drafts.
- Confirm Revision cannot run with unsaved changes.
- Confirm Revision sends the required `confirmed_by` request field using the fixed MVP value.
- No backend/runtime/report scope is introduced.
- UI copy is operational and non-technical.
- Existing Save behavior remains intact.
