# TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY

## Status

Complete. Implemented and validated on 2026-05-23.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` has been completed.

## Why This Task Is Allowed Now

- `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete.
- User smoke testing found that the current Group Selection modal is too detached from the Matrix context and that the Matrix Editor action buttons are confusing during import selection.
- `docs/task_board.md` marks `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` as the current planned task awaiting explicit approval.
- This task is a controlled UX correction before `TASK_263_CONFIRMED_MATRIX_TEST_RECORD_PREVIEW_BACKEND`, so the Test Record smoke flow starts from a clearer Matrix import/selection experience.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded frontend workflow and UI-state correction.
- It reuses existing Matrix import preview, TASK_261 commit API client, and Matrix Editor draft loading behavior.
- It explicitly excludes backend lineage changes, multi-source merge implementation, Test Record preview, execution persistence, report generation, and broad Matrix Editor redesign.

## Required UI Context

This is a frontend/UI task. Implementation must load `$impeccable` context before editing UI code and follow:

- `PRODUCT.md`
- `DESIGN.md`
- `$impeccable` product register guidance
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`

Design posture:

- ConnLab is a restrained product UI for offline lab operators.
- Group selection should feel like selecting columns from the parsed Matrix, not like a separate administrative list.
- Action buttons must reflect lifecycle state: import selection first, editable draft actions after selection is committed.

## Objective

Replace the detached Group Selection modal with an inline Matrix selection mode:

```text
Import Matrix
-> Preview parsed Matrix
-> Matrix Selection Mode
   - Test Item visible as context
   - group columns selectable with checkbox headers
   - Section / Method / Condition / Requirement hidden
   - edit cards and draft/revision actions hidden or disabled
-> Confirm selected groups
-> TASK_261 commit API
-> selected-only ProjectMatrixDraft
-> normal Matrix Editor editing mode
```

This task also clarifies top-right action buttons so `Save`, `Create revision draft`, and `Confirm revision` do not appear as available actions during import selection mode.

## User-Confirmed Product Decisions

- Multi-Matrix merge is rare and should not be implemented now.
- Future merge must preserve long-term lineage for every source row/group, so it needs a later backend/data-design task.
- Current task should preserve a visible `Append Matrix` / merge-oriented entry as a future placeholder, but it must not perform merge behavior.
- Group Selection mode should keep `Test Item` rows visible as background context.
- Group Selection mode should hide `Section`, `Method`, `Condition`, and `Requirement`.

## Scope

Allowed:

- Replace or bypass the TASK_262 standalone Group Selection modal with an inline Matrix selection mode inside Matrix Editor.
- Add/adjust feature selectors for selection-mode view models.
- Render imported preview rows with `Test Item` and group columns only.
- Render a checkbox at each group column header, defaulting all groups selected.
- Require at least one group selected before confirming selection.
- Confirm selected groups through the existing TASK_261 commit API client.
- Load the returned selected-only `ProjectMatrixDraft` into normal Matrix Editor editing mode.
- Hide or disable draft/revision action buttons while selection mode is active.
- Restore or add `Append Matrix` as a visible reserved action, clearly disabled or marked as future scope.
- Add clear operator copy explaining that multi-Matrix append requires source-lineage support and is not active yet.
- Add/update focused frontend behavior tests and static shell tests.
- Update `docs/task_board.md` after implementation completion.

Forbidden:

- Backend API, persistence, repository, database, or parser changes.
- Implementing multi-Matrix append/merge.
- Storing multiple Source Matrix lineages on one draft.
- Test Record preview. That belongs to `TASK_263`.
- Runtime execution, StepInstance, execution result persistence, evidence/image records, report, fee, duration, equipment, AI review, LAN, permissions, or deployment work.
- Confirmed Matrix creation from import selection mode.
- Broad Matrix Editor layout redesign beyond selection-mode visibility/action clarity.
- Displaying `Section`, `Method`, `Condition`, or `Requirement` in selection mode.
- Enabling right-side Group/Step editing cards in selection mode.

## UI Rules

Selection mode must show:

- source document name
- concise import/selection status
- `Test Item` rows as background context
- group columns with labels/keys
- group-level sample quantity where practical
- checkbox in each group header
- selected count and blocker/disabled reason
- primary action: `Confirm selected groups`
- secondary action: cancel/back to import preview/editor
- reserved `Append Matrix` action as disabled/future if shown

Selection mode must not show:

- `Section`
- `Method`
- `Condition`
- `Requirement`
- Step preview cards
- editable group/step cards
- Save / Create revision draft / Confirm revision as active controls
- Test Record, Report, Fee, Equipment, AI, or execution actions

Normal editing mode:

- starts only after TASK_261 commit returns a `ProjectMatrixDraft`
- shows selected groups only
- restores normal Matrix Editor fields and right-side editing areas
- restores normal draft/revision actions according to existing guards

## Architecture Rules

- Keep API calls in `frontend/src/api/client.ts`.
- Keep selection-mode derivation in feature selectors/helpers where practical.
- Prefer a named feature component for inline selection mode instead of expanding a large JSX block directly in `MatrixEditorWorkspace.tsx`.
- Do not create a new route page.
- Do not move route or API responsibility into display components.
- Keep CSS scoped to Matrix Editor selection-mode classes.

## Acceptance Criteria

- Import preview no longer leads to a detached Group Selection list as the primary operator experience.
- After preview, Matrix Editor enters an inline selection mode.
- Selection mode shows `Test Item` and group columns only.
- Selection mode hides `Section`, `Method`, `Condition`, `Requirement`.
- Group headers include checkboxes and default to selected.
- Confirm is disabled with a visible reason when no groups are selected.
- Confirm calls TASK_261 commit API with selected group keys.
- Commit `created` and `reused` responses both load the returned selected-only draft.
- Normal edit mode begins only after successful commit.
- Save / Create revision draft / Confirm revision are hidden or disabled during selection mode.
- A reserved Append Matrix entry exists but is not functional and is clearly marked as future/disabled.
- Existing save/revision/confirm behavior remains unchanged after a draft is loaded.
- No backend files are modified.
- No Test Record/report/fee/execution/future-scope behavior is introduced.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task262a or matrix_editor"
```

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

```powershell
cd frontend; npm run build
```

## Residual Risk Record

- Existing `MatrixEditorWorkspace.tsx` is large; this task should prefer a named selection-mode component and selector updates rather than adding a large inline JSX block.
- Append/Merge Matrix is intentionally deferred because long-term source lineage is required.
- This task improves import/selection clarity before Test Record preview; it does not make Test Record flow available.
