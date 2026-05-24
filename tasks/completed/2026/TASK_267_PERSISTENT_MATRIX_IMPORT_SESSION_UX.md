# TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX

## Status

Complete on 2026-05-24. Persistent Matrix import session UX is implemented and verified.

Executable plan reviewed and revised on 2026-05-24 to clarify test preview PDF token setup, selected-group-key restore order after commit, and CSS selector merge behavior.

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

`TASK_267_PERSISTENT_MATRIX_IMPORT_SESSION_UX` was the active task for this slice and is now complete.

## Why This Task Is Allowed Now

- `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete.
- `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete.
- `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` is complete.
- `TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING` is complete.
- `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND` is complete.
- `TASK_264_MATRIX_TO_TEST_RECORD_SMOKE_UI` is complete.
- `TASK_265_END_TO_END_SMOKE_VALIDATION_AND_BOARD_SYNC` is complete.
- `TASK_266_MATRIX_WORKSPACE_NAVIGATION_AND_STATE_CLARITY` is complete.
- `docs/task_board.md` currently has no active implementation task.
- `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md` lists TASK_267 as the next workflow refinement after TASK_266.
- The user explicitly requested TASK_267 task file and executable plan creation.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded frontend UX/state task.
- It requires careful reading of the current Matrix import preview, group selection, and draft editor state flow.
- It should add a small in-memory import-session model and navigation affordances without backend schema/API changes.
- Medium reasoning is enough if the worker keeps scope tight and verifies existing TASK_261 to TASK_266 behavior.
- The main risk is accidentally turning this into backend lineage persistence, multi-matrix merge, or source snapshot recovery after reload. Those are out of scope.

## Baseline Analysis

Current Matrix Workspace behavior:

- `MatrixEditorWorkspace.tsx` keeps import source file, preview payload, preview PDF token, locator fields, group selection keys, and import dialog state as local component state.
- `Change Source Matrix` already opens the source picker with an explicit confirmation when a persisted draft exists.
- `Change Selected Groups` exists as a TASK_266 Draft Action but remains disabled because persisted group reselection was not implemented.
- `MatrixImportSelectionMode.tsx` currently offers `Cancel`, disabled `Append Matrix (Future)`, and `Confirm selected groups`.
- From group selection, the user cannot explicitly return to the matrix candidate preview while preserving the import session.
- After selected groups are committed and the selected-only draft is loaded, the user does not have a clear live-session path back to the prior matrix preview or group selection.
- Existing TASK_261 commit API already supports committing a preview payload plus selected group keys; TASK_267 should keep using it.

## Objective

Make Matrix import behave like a persistent import session inside the current Matrix Workspace tab, so an operator can safely move between source preview, group selection, and draft editing without mentally starting over.

This task must not introduce a backend import-session model. Persistence means in-memory continuity for the current Matrix Workspace session.

## Required UX Outcome

The operator can:

- Return from group selection to matrix candidate preview without losing source preview context.
- Return from draft editing to the live matrix import session when that session is still available.
- Change the source matrix with clear draft-invalidation warnings.
- Cancel the current import session explicitly.
- Recover from choosing the wrong matrix table or wrong group set without treating group reselection as a new import.

## Scope

Allowed:

- Introduce a frontend-only Matrix import session model/helper.
- Preserve source file, source document name, preview payload, PDF token, locator fields, selected group keys, and last commit status in the current Matrix Workspace component state.
- Add `Back to matrix candidate selection` in group selection mode.
- Add `Cancel import session` in group selection mode.
- Enable `Change Selected Groups` from Draft Actions when a live import session is available.
- Keep `Change Selected Groups` disabled with clear copy when no live import session exists.
- Keep `Change Source Matrix` as a separate source replacement path with explicit warning.
- Let the operator re-open the existing import preview dialog from draft editing when the live import session exists.
- Keep existing `POST /api/projects/{project_id}/matrix-import/commit` behavior.
- Preserve TASK_266 state banner and action grouping.
- Add/update frontend component tests and static shell tests.

Forbidden:

- No backend import-session API.
- No backend lineage model/schema migration.
- No SourceMatrix repository/API expansion.
- No browser refresh/sessionStorage/localStorage recovery unless explicitly approved later.
- No multi-matrix merge/append implementation.
- No Test Record generation changes.
- No StepInstance, LLCR runtime persistence, report engine, fee engine, equipment matching, AI recommendation, permission system, or LAN behavior.
- No changes to TASK_261 commit API request/response contract.
- No Project Workbench authority editing.

## Design Requirements

- Follow `$impeccable` product UI guidance: calm, traceable, dense enough for lab work, no marketing layout.
- Follow `docs/02_ARCHITECTURE_RULES.md` and `docs/frontend_architecture_rules.md`.
- Keep Matrix authority editing in Matrix Workspace.
- Treat `Change Selected Groups` as modifying the current matrix authority configuration, not as `Import Matrix`.
- Use compact session copy rather than large instructional blocks.
- Preserve the existing PDF preview and locator fields as the matrix candidate preview surface.
- Make draft invalidation risk visible before source replacement.

## Candidate Impact Files

Expected:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`
- `frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Recommended new helper:

- `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`

Avoid modifying:

- backend application services
- backend API routes
- storage models/repositories
- database migrations
- Test Record preview backend
- Project Workbench smoke panel

## Acceptance Criteria

- Group selection mode has `Back to matrix candidate selection`.
- Group selection mode has `Cancel import session`.
- Back to matrix candidate selection reopens the existing source preview/PDF/locator context.
- Cancel import session clears the live import session and returns to normal editor state.
- Draft Actions `Change Selected Groups` is enabled only when a live import session exists.
- `Change Selected Groups` returns to selection mode using the existing preview payload and prior selected group keys.
- `Change Selected Groups` is disabled with clear copy when the source preview session is unavailable.
- `Change Source Matrix` remains separate and warns when changing source may invalidate draft edits.
- Existing import commit still calls TASK_261 API with preview payload plus selected group keys.
- Existing TASK_266 state banner/action grouping remains intact.
- TASK_261 to TASK_266 smoke-flow behavior remains unchanged.
- No backend files are modified.

## Validation

Minimum validation after approved implementation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task267 or task266 or matrix_editor"
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

- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task267 or task266 or matrix_editor"` passed (`36 passed, 72 deselected`).
- `cd frontend; npm test -- --run MatrixEditorWorkspace` passed (`12 passed`).
- `cd frontend; npm run build` passed.
- `py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q` passed (`1 passed`).

## Required Executable Plan Before Implementation

The executable plan for this task is:

```text
docs/task_267_persistent_matrix_import_session_ux_plan.md
```

No implementation code may be written before this task file and plan are reviewed and explicitly approved.

## Residual Risk Record

- TASK_267 deliberately preserves import context only inside the current Matrix Workspace runtime. It does not recover preview payload or source file after browser refresh, route remount, or app restart.
- A persisted draft loaded without a live import session cannot safely reconstruct the original preview payload without backend support. In that case, `Change Selected Groups` must stay disabled and explain that source preview context is unavailable.
- Candidate preview remains the existing PDF/locator/reparse surface, not a full candidate-management redesign.
- Multi-source append/merge remains future scope.
