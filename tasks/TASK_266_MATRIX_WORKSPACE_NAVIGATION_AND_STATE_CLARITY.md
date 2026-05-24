# TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY

## Status

Complete on 2026-05-24. Matrix Workspace navigation, state banner, action grouping, consequence copy, and source-change confirmation guard are implemented and verified.

## Current Phase

Board phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Workstream:

```text
Post-Phase-11 Matrix-driven Laboratory Execution workflow refinement
```

## Current Active Task

`TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY` was the active task for this slice and is now complete.

## Why This Task Is Allowed Now

- `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete.
- `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete.
- `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` is complete.
- `TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING` is complete.
- `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND` is complete.
- `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI` is complete.
- `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC` is complete.
- `docs/task_board.md` currently has no active implementation task.
- `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md` identifies Matrix Workspace navigation/state clarity as the next UX refinement after the smoke flow.
- The user explicitly requested creation of this TASK_266 task file.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded frontend workflow-clarity task.
- The main work is reading current Matrix Editor state/action logic, then restructuring labels, grouping, copy, and tests without changing backend contracts.
- Medium reasoning is enough if the worker follows `AGENTS.md`, `$impeccable`, `docs/02_ARCHITECTURE_RULES.md`, and `docs/frontend_architecture_rules.md`, and keeps the change limited to Matrix Workspace UI semantics.
- The main risk is scope creep into backend authority redesign, group reselection persistence, multi-matrix merge, or Test Record generation. Those are explicitly out of scope.

## Baseline Analysis

Current frontend state from the existing Matrix Workspace implementation:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` currently renders `Save`, `Create revision draft`, and `Confirm revision` together in the same top action area when import selection mode is not active.
- The same component already hides draft/revision actions while `showImportSelectionMode` is true.
- `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx` already implements inline group selection mode with Test Item rows and group checkbox headers, hiding Section / Method / Condition / Requirement during selection.
- The import toolbar still has `Import Matrix` plus a disabled `Append Matrix (Future)` placeholder.
- Existing tests in `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx` assert current labels such as `Save`, `Create revision draft`, and `Confirm revision`, so TASK_266 must update tests alongside UI copy.
- `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md` requires the user to understand whether they are editing Draft, Confirmed Authority, or Revision Draft, and requires `Change Selected Groups` to be presented as authority-configuration editing rather than a new import.

## Objective

Improve Matrix Workspace navigation, status messaging, and action semantics so an operator can immediately tell which matrix state they are working with and what each action will affect.

The task must preserve the completed TASK_261 to TASK_265 smoke flow and must not restructure backend Matrix Authority architecture.

## Required UX Outcome

The Matrix Workspace must clearly communicate these states:

1. `Editing Draft`
   - Consequence: `Not active for downstream outputs`.
2. `Current Active Matrix Authority`
   - Consequence: `Used by Project Workbench and Test Record generation`.
3. `Editing Revision Draft`
   - Consequence: `Changes are not active until confirmed`.

The action area must separate at least these groups:

Draft Actions:

- `Save Draft`
- `Discard Draft Changes`
- `Change Selected Groups`
- `Change Source Matrix`

Authority Actions:

- `Confirm As Active Matrix`
- `Create Revision Draft`
- `Confirm Revision`

Each key action must include consequence copy that explains the result of clicking it.

## Scope

Allowed:

- Add a Matrix Workspace state banner for draft, active authority, and revision draft contexts.
- Rename `Save` to `Save Draft` where it saves only the current Project Matrix Draft.
- Split Matrix Workspace action controls into `Draft Actions` and `Authority Actions`.
- Add concise consequence copy for save, discard, group-selection change, source change, confirm-active, create-revision, and confirm-revision actions.
- Add `Change Selected Groups` as an authority-configuration action, not as `Import Matrix`.
- Add `Change Source Matrix` as a separate source-change entry point.
- In import selection mode, keep a visible compact state banner so current workspace state is always explicit.
- Require explicit confirmation before `Change Source Matrix` when a draft exists (especially with unsaved edits), and show draft-invalidation risk copy.
- Keep unsupported actions disabled or clearly marked as not active in this task when the required backend/session behavior does not yet exist.
- Preserve current import preview and inline group-selection flow behavior.
- Preserve current draft save, revision draft creation, and revision confirmation behavior.
- Add or update React component tests for the new labels, grouping, state banner, and disabled/active semantics.
- Add or update static frontend shell tests for TASK_266 guardrails.
- Update task and board status after approved implementation and validation.

Forbidden:

- No backend Matrix Authority architecture refactor.
- No backend API contract changes unless a separately approved follow-up task requires them.
- No database schema changes.
- No permission system.
- No LLCR runtime persistence.
- No report engine.
- No AI recommendation.
- No Test Record Word generation.
- No StepInstance or execution result persistence.
- No multi-matrix merge implementation.
- No long-term row/group source lineage implementation beyond existing persisted lineage.
- No replacement of TASK_261 to TASK_265 smoke-flow behavior.
- No Project Workbench ownership shift; Matrix authority editing remains in Matrix Workspace.

## Design Requirements

- Follow `$impeccable` product UI guidance: calm, traceable, operator-focused, and not marketing-like.
- Follow `docs/02_ARCHITECTURE_RULES.md` and `docs/frontend_architecture_rules.md`.
- Keep Matrix Workspace as the editing surface; Project Workbench remains a downstream consumer.
- Avoid making `Change Selected Groups` look like a fresh import. The label and consequence copy must describe changing the current matrix authority configuration.
- Keep `Import Matrix` only for choosing/parsing a source document or source candidate.
- During import selection mode, keep draft/authority action groups hidden or inactive, as TASK_262A established.
- Avoid card nesting and avoid adding large explanatory blocks that crowd the grid. Use compact banners, grouped action sections, and short consequence copy.
- Do not introduce a new frontend state-management dependency.

## Candidate Impact Files

Expected:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Optional, if it reduces `MatrixEditorWorkspace.tsx` growth:

- new `frontend/src/features/matrix-editor/MatrixWorkspaceStateBanner.tsx`
- new `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- new `frontend/src/features/matrix-editor/matrixWorkspaceStateSelectors.ts`

Avoid modifying:

- backend application services
- backend API routes
- storage models/repositories
- database migrations
- Test Record preview backend
- Project Workbench Test Record smoke panel unless a static copy reference must be kept consistent

## Consequence Copy Requirements

Use wording equivalent to these meanings:

- `Save Draft`: saves current draft edits only; downstream outputs keep using the active authority until confirmation.
- `Discard Draft Changes`: discards unsaved draft edits and returns to the last saved/loaded draft state, or remains disabled if no discard path exists in this task.
- `Change Selected Groups`: changes which groups are part of the current matrix authority configuration; it is not a new source import.
- `Change Source Matrix`: chooses a different source matrix candidate/document; existing draft edits may need review.
- `Confirm As Active Matrix`: publishes this saved draft as the current authority used by Project Workbench and Test Record generation.
- `Create Revision Draft`: starts an editable copy from the active authority; the active authority remains in use.
- `Confirm Revision`: replaces the active authority with the saved revision draft.

## Acceptance Criteria

- Matrix Workspace shows a visible current-state banner in normal editing contexts.
- The banner differentiates Draft, Active Authority, and Revision Draft semantics.
- `Save` is no longer the visible label for the draft save action; it is expressed as `Save Draft`.
- Draft-related actions and authority-related actions are visually and semantically separated.
- `Save Draft`, `Confirm As Active Matrix`, `Create Revision Draft`, and `Confirm Revision` each have consequence copy.
- `Change Selected Groups` appears as a current-authority-configuration action and is not named or described as `Import Matrix`.
- `Change Source Matrix` is distinct from `Change Selected Groups`.
- `Change Source Matrix` triggers an explicit risk confirmation when a draft already exists.
- Import selection mode still hides or disables draft/authority action groups.
- Import selection mode still shows a visible compact state banner (state clarity is never hidden).
- Existing save, create revision draft, and confirm revision behavior remains unchanged.
- TASK_261 to TASK_265 smoke-flow contracts remain unchanged.
- No backend files are modified.

## Validation

Minimum frontend validation after approved implementation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task266 or matrix_editor"
```

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

```powershell
cd frontend; npm run build
```

Smoke-flow regression safety:

```powershell
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

Validation result on 2026-05-24:

- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task266 or matrix_editor"` passed (`35 passed, 72 deselected`).
- `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`9 passed`).
- `cd frontend; npm run build` passed.
- `py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`).

## Required Executable Plan Before Implementation

The executable plan for this task must be created as:

```text
docs/task_266_matrix_workspace_navigation_and_state_clarity_plan.md
```

No implementation code may be written before this task file and the executable plan are reviewed and explicitly approved.

## Residual Risk Record

- Current frontend state may not have a complete active-authority viewing mode. The executable plan must inspect the loaded draft/revision state carefully and define the least risky banner derivation without backend changes.
- `Discard Draft Changes`, `Change Selected Groups`, and `Change Source Matrix` may require future backend/session behavior for full functionality. TASK_266 may present them as disabled or clearly scoped entry points if full behavior is not available without changing backend contracts.
- The action grouping must improve clarity without turning the Matrix Editor header into a dense command console.
- This task improves workflow clarity only; it does not solve multi-source merge, source lineage expansion, persistent reselection sessions, or downstream Test Record generation.
