# TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW

## Status

Planned. Awaiting user approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is planned only.

## Why This Task Is Allowed Now

- `TASK_261_MATRIX_IMPORT_GROUP_SELECTION_COMMIT` is complete.
- `docs/task_board.md` has no active implementation task.
- `docs/matrix_authority_to_test_record_smoke_flow_plan.md` recommends `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` after the backend import commit boundary.
- The next workflow need is an operator-facing Group Selection View that calls the TASK_261 commit API before Matrix editing begins.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded frontend workflow slice with typed API wiring, deterministic UI state, and focused frontend/static tests.
- It builds on existing Matrix Editor import preview behavior and the TASK_261 backend commit API.
- It does not require backend persistence changes, Office parser expansion, Test Record preview, runtime execution persistence, report generation, or Matrix Editor visual redesign.

## Required UI Context

This is a frontend/UI task. Implementation must load `$impeccable` context before editing UI code and follow:

- `PRODUCT.md`
- `DESIGN.md`
- `$impeccable` product register guidance
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Design posture:

- ConnLab is a restrained product UI for offline lab operators.
- Group Selection is a workflow gate, not a second Matrix editor.
- The view must show state, blocker, and next action without exposing future-scope features.

## Objective

Add a Group Selection View after Matrix import preview confirmation and before Matrix Editor editing state:

```text
Import Matrix
-> Matrix Preview
-> Group Selection
-> TASK_261 commit API
-> selected-only ProjectMatrixDraft
-> Matrix Editor editing state
```

This task makes the selected-group projection visible and operator-controlled while preserving full Source Matrix lineage through the backend.

## Scope

Allowed:

- Add frontend API client DTOs and function for `POST /api/projects/{project_id}/matrix-import/commit`.
- Add a named Matrix Editor feature component for group selection, preferably `frontend/src/features/matrix-editor/MatrixImportGroupSelectionView.tsx`.
- Add selector/helper logic for extracting selectable groups from the existing Matrix preview payload, preferably in `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`.
- Wire existing Matrix import preview confirmation so it opens Group Selection View instead of immediately applying imported rows/groups to the editor.
- Require at least one selected group before commit.
- Call the TASK_261 commit API with `preview_payload` and selected group keys.
- Load the returned selected-only `ProjectMatrixDraft` into existing Matrix Editor state using the current draft mapping path.
- Show operational loading, error, empty, disabled, and reused/created success states.
- Add/update focused frontend tests and static shell tests.
- Update `docs/task_board.md` after implementation completion.

Forbidden:

- Backend API, persistence, repository, database, or parser changes.
- `preview_token` implementation.
- Test Record preview generation. That belongs to `TASK_263`.
- Runtime execution, StepInstance, execution result persistence, evidence/image records, report, fee, duration, equipment, AI review, LAN, permissions, or deployment work.
- Confirmed Matrix creation from the import flow.
- Matrix Editor layout redesign or broad visual refactor.
- Displaying Test Item, Method, Condition, Requirement, execution rows, report data, or step preview inside the Group Selection View.
- Treating unselected groups as hidden editable draft groups.

## Contract Boundary

Input state:

- Existing Matrix import preview payload from the current Matrix Editor import preview flow.
- Existing route project id.
- Operator-selected group keys.

Frontend API request:

- `source_document_path`
- `source_document_name`
- `source_format`
- `preview_payload`
- `selected_group_keys`

Frontend API response:

- `source_import_id`
- `source_snapshot_id`
- `selected_group_keys_committed`
- `commit_status`
- `project_matrix_draft`

Error handling:

- `404`: project not found.
- `409`: deterministic commit conflict.
- `422`: empty/unknown/duplicate selected keys or malformed preview payload.

## UI Rules

Display only:

- group label/key
- sample quantity expression if available
- optional sample note if already present in preview group payload
- checkbox selection state
- compact step count only if it is cheaply derivable from preview group steps without showing step details

Do not display:

- Test Item
- Section
- Method
- Condition
- Requirement
- Matrix cell values
- Step preview
- Test Record, Report, Fee, Equipment, AI, or execution actions

Interaction rules:

- Default selection may select all parsed groups if the preview has groups.
- Operator can deselect groups, but confirm is disabled when none remain selected.
- Confirm button text should communicate draft creation, not final authority confirmation.
- Cancel returns to import preview/editor state without creating Source Matrix or ProjectMatrixDraft.
- Successful commit applies the returned `ProjectMatrixDraft` and enters normal Matrix Editor editing state with selected groups only.
- Repeated same-input commit may return `commit_status=reused`; UI should treat this as a successful load, not an error.

## Architecture Rules

- Route page remains thin; do not move workflow logic into route pages.
- API calls stay in `frontend/src/api/client.ts`.
- Group-selection derivation and disabled reasons should live in feature selectors/helpers, not scattered JSX conditions.
- The new view should be a feature component composed by `MatrixEditorWorkspace`.
- Keep changes scoped to Matrix Editor import workflow.
- Do not introduce a new global route or app shell.

## Acceptance Criteria

- Group Selection View appears after import preview confirmation, not before parsing.
- The view lists groups only and does not render Matrix row/detail columns.
- At least one group must be selected before confirm.
- Confirm calls TASK_261 commit API with `preview_payload` and selected group keys.
- A `created` response loads the returned selected-only `ProjectMatrixDraft` into Matrix Editor.
- A `reused` response loads the returned draft and is shown as a successful reuse state.
- Matrix Editor displays selected groups only after commit.
- Existing draft save/revision/confirm behavior remains unchanged for loaded drafts.
- Existing Matrix preview APIs remain unchanged.
- No backend code changes are introduced.
- No Test Record, Report, Fee, execution, evidence, or Confirmed Matrix scope is introduced.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task262 or matrix_editor"
```

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

```powershell
cd frontend; npm run build
```

## Residual Risk Record

- `MatrixEditorWorkspace.tsx` is already large. Keep new UI in a named feature component and selector module where practical.
- Current backend commit API accepts `preview_payload` mode only; frontend must not imply server-side preview token support.
- The Group Selection View is a gate before editing, not a reusable Matrix library selection system.
- Future group reselection from persisted Source Matrix lineage remains out of scope.
