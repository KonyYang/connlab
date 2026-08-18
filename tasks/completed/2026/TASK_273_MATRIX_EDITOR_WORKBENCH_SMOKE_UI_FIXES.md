# TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES

## Status

Complete. Implemented and validated on 2026-05-26.

## Current Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current product direction: `Matrix-driven Laboratory Execution Phase`
- Current task status: `TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES` complete
- Allowed reason: `TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY` is complete, `docs/task_board.md` has no active implementation task, and user smoke testing found Matrix Editor / Workbench UI issues that block the Matrix to Test Record continuity workflow from being understandable to a new user.

## Source Inputs

Primary source:

- User smoke-test feedback after TASK_266 through TASK_272.

Relevant guideline:

- `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`

Relevant project rules:

- `$impeccable` product register.
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

## Objective

Make the current Matrix Editor to Project Workbench flow understandable and usable after smoke testing:

```text
Create or load Matrix draft -> edit groups / matrix -> auto-save draft -> confirm authority or revision -> return to Workbench -> see refreshed Matrix execution projection.
```

This task is a UI / frontend workflow hardening slice. It must not add new backend domain models, StepInstance persistence, execution-data capture, permission/approval workflow, report engine, fee engine, AI features, or equipment workflow.

## User Problems

1. `Change Source Matrix` shows a technically correct warning, but the copy does not explain source-session replacement clearly.
2. `Save Draft` and `Discard Draft Changes` create too much cognitive load. Users expect Matrix edits to be retained automatically.
3. `Change Selected Groups` is unavailable after returning to a confirmed Matrix unless the user imports a new source Matrix, which makes revision editing feel broken.
4. `Confirm As Active Matrix` is confusing when an active authority already exists. Users need a clear first-confirm versus revision-confirm path.
5. Confirming a revision should return the user to Workbench and refresh the authority projection.
6. Workbench still shows the old group-card Matrix Overview, while the new `Matrix execution projection` is the actual direction.
7. Refreshing Workbench does not show projection changes when no revision was actually confirmed, and the UI does not explain why.

## Scope

In scope:

- Convert Matrix Editor draft persistence to a frontend auto-save experience using the existing `saveProjectMatrixDraft` API.
- Remove `Save Draft` and `Discard Draft Changes` from the main Matrix Editor action groups.
- Add compact save status copy:
  - `Saving...`
  - `Saved`
  - `Unsaved changes`
  - `Save failed. Retry before confirming.`
- Keep a low-priority `Revert to last saved draft` affordance only when it is actually useful.
- Gate confirm actions on a clean saved draft.
- Clarify first confirmation versus revision confirmation:
  - first draft: `Confirm As Active Matrix`
  - existing authority: `Create Revision Draft`, then `Confirm Revision`
- Disable or hide `Confirm As Active Matrix` when an active authority already exists.
- Make `Change Selected Groups` work from the current persisted draft or revision draft without requiring a new source import.
- Keep `Change Source Matrix` available but improve the warning copy and action labels.
- After successful `Confirm Revision`, return to Workbench and ensure Workbench reloads current active ConfirmedMatrix projection and authority history.
- Remove the old Workbench group-card `Matrix Overview / Runtime execution map`.
- Promote `Matrix execution projection` as the Workbench primary Matrix surface with the right-side Record Step Workspace.
- Add or update frontend tests and static guards.
- Update task and board status after implementation.

Out of scope:

- Backend schema changes.
- New Matrix import APIs.
- New ConfirmedMatrix authority APIs.
- Version conflict or multi-user collaborative editing.
- StepInstance or execution persistence.
- Evidence upload or image management.
- Report engine.
- Fee engine.
- AI review or recommendation.
- Equipment assignment.
- Permission or approval workflow.
- Full Workbench redesign beyond removing the old overview and improving the confirmed projection flow.
- Implementing real execution status transitions.

## Expected File Changes

Likely modify:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
- `frontend/src/features/matrix-editor/matrixWorkspaceClarityModel.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `tasks/TASK_273_MATRIX_EDITOR_WORKBENCH_SMOKE_UI_FIXES.md`

Likely no backend files should be modified.

## UI / UX Requirements

- ConnLab register: `product`.
- Physical scene: a lab coordinator on an offline Windows workstation is preparing or revising a Matrix and needs a calm, low-ambiguity path back to the Project Workbench.
- State before action:
  - show whether the draft is saving, saved, failed, or blocked.
  - show whether the user is editing initial draft, active authority, or revision draft.
- Workflow before tools:
  - do not show unnecessary save/discard buttons as primary workflow actions.
  - do not keep two competing Matrix overview surfaces in Workbench.
- Copy must be operational and non-technical.
- Avoid generic dashboard decoration.
- Do not expose unimplemented Report, Fee, AI, equipment, permission, approval, or execution-data actions as active features.

## Behavioral Requirements

### Matrix Editor Auto-Save

- Matrix edits should auto-save through existing `saveProjectMatrixDraft`.
- Auto-save should debounce user edits to avoid saving on every keystroke.
- Confirm actions must be disabled while saving or after save failure.
- Save failure must be visible and actionable.
- A low-priority `Revert to last saved draft` may remain, but it must not sit beside primary workflow actions.

### Group Selection

- `Change Selected Groups` must not require a fresh source import when the user is editing a persisted draft or revision draft.
- If no group-selection source can be derived, the UI must explain the blocker and point to the correct next action.
- Revision workflow should support:

```text
Create Revision Draft -> Change Selected Groups -> auto-save -> Confirm Revision
```

### Authority Confirmation

- When no active authority exists, user can confirm the initial saved draft with `Confirm As Active Matrix`.
- When active authority already exists, user should create a revision draft and confirm it with `Confirm Revision`.
- `Confirm As Active Matrix` should not look like the right action for changing an already confirmed Matrix.
- After successful `Confirm Revision`, return to Workbench and force one Workbench data reload so Matrix execution projection and Authority History are re-fetched from current active ConfirmedMatrix authority.

### Workbench Matrix Surface

- Remove the old group-card `Matrix Overview / Runtime execution map`.
- Keep `Confirmed Matrix Projection / Matrix execution projection` as the primary Matrix surface.
- Keep Record Step Workspace connected to selected matrix tokens.
- Keep Authority History and `Generate Test Record Draft`.
- Ensure Workbench reload or navigation after confirm uses current active ConfirmedMatrix data.
- After old overview removal, the primary Matrix region must always be owned by `ProjectWorkbenchMatrixProjectionPanel`, including `loading`, `not_ready`, `empty`, `error`, and `ready` states, to avoid blank or duplicated status regions.

## Acceptance Criteria

- Matrix Editor no longer presents `Save Draft` and `Discard Draft Changes` as primary buttons.
- Matrix Editor shows auto-save state clearly.
- Confirm actions are blocked while saving or when save failed.
- `Change Selected Groups` works for a revision draft without requiring `Change Source Matrix`.
- `Change Source Matrix` warning clearly says it replaces the source session and may discard unsaved edits.
- Existing authority revision path is clear:

```text
Create Revision Draft -> edit -> auto-save -> Confirm Revision -> Workbench
```

- Successful `Confirm Revision` returns to Workbench.
- Workbench refreshed after revision confirm shows the updated active Matrix projection, with explicit reload/re-fetch behavior verified in tests.
- Workbench no longer shows the old group-card Matrix Overview.
- `Matrix execution projection` remains the primary read-only authority surface.
- No backend schema/API/domain changes are introduced.
- No StepInstance, execution persistence, report, fee, AI, equipment, permission, approval, or generation-ledger scope is introduced.
- Relevant frontend tests, static guards, and build pass.

## Validation Plan

Required commands after implementation:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm test -- --run AuthorityChangeHistoryPanel
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task273 or task272 or matrix_editor or project_workbench"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

Manual smoke validation:

```text
Matrix import -> group selection -> confirm initial authority -> Workbench projection visible
Workbench -> Matrix Editor -> Create Revision Draft -> Change Selected Groups -> auto-save -> Confirm Revision -> Workbench
Workbench refresh -> updated projection and authority history visible
```

## Risks

- Auto-save can hide failure if status is too quiet. The UI must block confirmation on save failure.
- Removing explicit save/discard may surprise users who expect a form-submit model. The status copy must make save state visible.
- `Change Selected Groups` may need a frontend derivation path from persisted draft groups. Keep this frontend-only unless an existing API is insufficient and the plan is explicitly revised.
- Removing old Workbench overview could reveal layout gaps because some surrounding panels were composed around it.
- Workbench refresh may still depend on route-level state. Implementation must verify navigation and hard refresh.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task.

Reason:

- The task is a bounded frontend workflow and UI hardening slice using existing APIs.
- It requires careful state management and tests, but does not require backend schema migration, Office automation, report design, or multi-user workflow modeling.
- Medium or high reasoning is appropriate because Matrix Editor has several interacting states.

Recommended mode:

- `GPT-5.3-codex` with medium or high reasoning.
- Use `superpowers:executing-plans` for implementation after user approval.
