# TASK_262A Matrix Import Selection Mode And Action Clarity Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` (planned, awaiting approval)
- Why this task is allowed now:
  - `TASK_262_MATRIX_IMPORT_GROUP_SELECTION_VIEW` is complete.
  - User smoke testing identified import-selection UX confusion before the planned Test Record smoke path.
  - `docs/task_board.md` marks `TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY` as the current planned task awaiting explicit approval.

This document is a plan only. No implementation should start until user approval.

Model fit:

- Recommended model: `GPT-5.3-codex`, reasoning `medium`.
- Why: bounded frontend workflow correction, existing API client reuse, no backend schema/domain change, focused UI tests.

UI context required for implementation:

- `$impeccable` product register context from `PRODUCT.md` and `DESIGN.md`.
- `docs/02_ARCHITECTURE_RULES.md`.
- `docs/frontend_architecture_rules.md`.

## 1) Goal

Make Matrix import group selection understandable by moving it into the Matrix editing area as a temporary selection mode:

```text
Preview parsed Matrix
-> inline group selection mode
-> confirm selected groups
-> TASK_261 commit
-> normal selected-only Matrix Editor draft
```

The task should also prevent the top-right draft/revision actions from appearing as the next step while the user is still choosing imported groups.

## 2) Task Understanding

Input data:

- Existing `MatrixPreviewResponse`.
- Project id.
- Operator-selected group keys.

Output data:

- Returned `ProjectMatrixDraft` loaded into normal Matrix Editor mode.
- Clear selection-mode UI with Test Item context and group-column checkboxes.
- Clear disabled/future placeholder for Append Matrix.

Involved modules:

- `frontend/src/api/client.ts` only if small type reuse/copy adjustment is required.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`.
- `frontend/src/features/matrix-editor/MatrixImportGroupSelectionView.tsx`, likely replaced or repurposed.
- `frontend/src/features/matrix-editor/matrixImportSelectionSelectors.ts`.
- optional new `frontend/src/features/matrix-editor/MatrixImportSelectionMode.tsx`.
- `frontend/src/workbench.css`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`.
- `tests/unit/test_frontend_shell_files.py`.
- `tasks/TASK_262A_MATRIX_IMPORT_SELECTION_MODE_AND_ACTION_CLARITY.md`.
- `docs/task_board.md` after implementation completion.

Not allowed:

- backend changes
- parser changes
- multi-Matrix append/merge implementation
- Test Record preview
- confirmed authority creation from import selection
- report/fee/execution/evidence/future-scope work

## 3) Product Decisions From User Feedback

1. Multi-Matrix merge is category `C`: it can involve both rows/test items and group columns.
2. Multi-Matrix merge is rare and should be deferred until after Test Record smoke flow.
3. When implemented later, merge must preserve long-term lineage for every source row/group.
4. Current task should only reserve the Append Matrix entry and make clear it is not active yet.
5. Group selection should keep `Test Item` rows visible as context.
6. Selection mode should hide `Section`, `Method`, `Condition`, and `Requirement`.

## 4) UX Shape

Scene sentence:

An offline lab engineer has just parsed a Matrix from a DOCX file and needs to see enough of the table to choose which group columns belong to this project, without being pulled into full editing before the draft exists.

Design direction:

- Restrained product UI.
- Inline selection state inside Matrix Editor, not a separate administrative table.
- Familiar grid shape, but with edit affordances off.
- Group columns are the decision surface.
- Primary action is `Confirm selected groups`.

Selection mode layout:

```text
Toolbar/status:
  Source: <document name>
  Parsed groups: N, selected: M
  [Append Matrix] disabled/future
  [Confirm selected groups]

Grid:
  Test Item | Group 1 [x] | Group 2 [x] | Group 3 [ ]
  Visual    | token preview/light text | ...
  LLCR      | ...

Hidden in selection mode:
  Section, Method, Condition, Requirement
  right-side editing cards
  Save/Create revision/Confirm revision actions
```

## 5) File-Level Change Plan

1. Selection selectors
   - Extend `matrixImportSelectionSelectors.ts`.
   - Build a selection-mode view model from `MatrixPreviewResponse`:
     - source document label
     - rows with `test_item`
     - group columns with key/label/sample quantity
     - group token values for lightweight context if already available
     - selected count
     - disabled reason
   - Keep backend fallback group key behavior aligned with TASK_261.

2. Selection mode component
   - Add or repurpose a named component:
     - preferred: `MatrixImportSelectionMode.tsx`
     - or repurpose `MatrixImportGroupSelectionView.tsx` if the name remains accurate.
   - Props:
     - view model
     - selected keys
     - loading/status/error state
     - toggle group
     - confirm selected groups
     - cancel/back
     - append placeholder click/disabled reason
   - Render grid-like selection mode, not full editor controls.

3. Matrix Editor workflow
   - Update `MatrixEditorWorkspace.tsx`.
   - After import preview confirmation, set `selectionMode` state instead of showing detached group list.
   - Hide/disable top-right Save/Create revision/Confirm revision while selection mode is active.
   - Hide right-side editing cards while selection mode is active.
   - Confirm selected groups calls existing `commitMatrixImport`.
   - On success, apply returned draft and leave selection mode.
   - On cancel, return to import preview/editor without creating a draft.

4. Append Matrix placeholder
   - Restore or add a visible `Append Matrix` action near import controls.
   - Keep it disabled or clearly marked future.
   - Copy should explain: `Append Matrix requires multi-source lineage and is not active in this task.`
   - Do not call commit API or mutate editor state from this placeholder.

5. Styling
   - Update `frontend/src/workbench.css` with scoped selection-mode classes.
   - Avoid nested cards, decorative side stripes, gradient text, and decorative motion.
   - Keep table/grid dimensions stable and readable on a 14-inch laptop.

6. Tests
   - Update `MatrixEditorWorkspace.test.tsx`:
     - import preview enters selection mode
     - `Test Item` is visible
     - `Section`, `Method`, `Condition`, `Requirement` are absent in selection mode
     - group header checkboxes default selected
     - confirm disabled with visible reason when all groups deselected
     - commit success exits selection mode and loads returned draft
     - draft/revision buttons are hidden or disabled during selection mode
   - Update `tests/unit/test_frontend_shell_files.py`:
     - symbols/classes exist
     - forbidden columns are not rendered by selection-mode component
     - Append Matrix placeholder is present but disabled/future
     - no backend files are part of TASK_262A

7. Documentation
   - Mark TASK_262A complete only after implementation and validation.
   - Update `docs/task_board.md` with deliverables, validation, and next recommended task.

## 6) Data Flow

```text
MatrixPreviewResponse
-> selection-mode view model
-> selected group key state
-> commitMatrixImport(projectId, preview_payload, selected_group_keys)
-> ProjectMatrixDraft
-> existing applyDraftSnapshotToEditor()
-> normal Matrix Editor edit mode
```

Append placeholder flow:

```text
Append Matrix click/hover
-> disabled/future message only
-> no data mutation
```

## 7) Out Of Scope

- Multi-Matrix merge behavior.
- Multi-source SourceMatrix/Draft lineage schema.
- Backend support for multiple Source Matrix imports per draft.
- Group reselection from existing Source Matrix lineage.
- Test Record preview.
- First-authority confirmation UX redesign, unless limited to hiding draft/revision actions during import selection mode.
- Runtime execution, StepInstance, evidence, images, report, fee, duration, equipment, AI review, LAN, permissions, deployment.

## 8) Implementation Steps

1. Extend selection selectors to produce inline selection-mode rows/groups.
2. Add/repurpose named selection-mode component.
3. Wire Matrix Editor import preview into selection mode.
4. Hide/disable draft/revision action area during selection mode.
5. Add disabled Append Matrix placeholder.
6. Confirm selected groups through existing TASK_261 API client and load returned draft.
7. Add scoped styles.
8. Add/update tests.
9. Run validation commands.
10. Update task file and task board after implementation passes.

## 9) Validation Plan

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task262a or matrix_editor"
```

```powershell
cd frontend; npm test -- --run MatrixEditorWorkspace
```

```powershell
cd frontend; npm run build
```

## 10) Risks

- If too much JSX is added to `MatrixEditorWorkspace.tsx`, the existing large-file risk worsens. Keep selection mode in a named component.
- If Append Matrix looks active, users may expect rare merge behavior now. It must read as reserved/future.
- Selection mode should show enough context to choose groups but not become full Matrix editing.
- Hiding draft/revision actions during selection mode solves current confusion, but broader first-authority vs revision wording may still need a later dedicated task.

## 11) Review Checklist

- Selection mode is inline in Matrix Editor, not a detached group-only modal.
- `Test Item` is visible as context.
- `Section`, `Method`, `Condition`, and `Requirement` are hidden in selection mode.
- Group header checkboxes default selected.
- Confirm selected groups is disabled with visible reason when none selected.
- TASK_261 commit API remains the only commit boundary.
- Normal edit mode starts only after returned draft is loaded.
- Save/Create revision/Confirm revision are not active during selection mode.
- Append Matrix is present only as disabled/future placeholder.
- No backend files are modified.
- No Test Record/report/fee/execution/future-scope behavior is introduced.
