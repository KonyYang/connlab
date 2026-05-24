# TASK_226_MATRIX_EDITOR_ROW_SELECTOR_AND_SELECTION_HIGHLIGHT

## Status

Complete. Implemented and validated on 2026-05-18.

This is a Matrix Editor table interaction refinement following `TASK_225`.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_226_MATRIX_EDITOR_ROW_SELECTOR_AND_SELECTION_HIGHLIGHT`.

## Why This Task Is Allowed Now

`TASK_225` completed the right-click context menu pattern for group column operations. The user confirmed the column operation direction is basically acceptable and requested the same discoverable selection model for rows, using a narrow row-number selector column and row/column selection highlight. This is a bounded Matrix Editor grid interaction change.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The work is a focused frontend interaction refinement in the Matrix Editor grid.
- Existing row/group operation functions and context menu logic can be reused.
- No backend, API contract, domain model, persistence, or Workbench behavior is involved.
- Validation can be covered by frontend build and targeted static regression checks.

## Objective

Make row operations match the group column operation pattern:

1. Add a narrow leftmost row-number selector column for Matrix Editor data rows.
2. Clicking a row number selects that row and highlights the full row.
3. Right-clicking the selected row number opens the row operation context menu.
4. Clicking a group header selects that group column and highlights the full column.
5. Right-clicking the selected group header opens the group operation context menu.
6. Preserve current inline cell editing and structural protection rules.

## Scope

Allowed:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` targeted static assertions only
- task file and board update on completion

Forbidden:

- backend changes
- API contract changes
- matrix domain model changes
- persistence changes
- Workbench page changes
- unrelated visual redesign or polish
- adding popup workflows beyond the existing context menu

## Interaction Rules

### Row Selection

- Add a very narrow first column used only as a row selector.
- Header cell should be compact and not reintroduce an action rail.
- Data cells show row numbers `1`, `2`, `3`, etc.
- Left-clicking a row number:
  - sets `selectedRowId`
  - clears `selectedGroup`
  - closes any open context menu
  - highlights the whole selected row
- Right-clicking a row number:
  - selects that row
  - opens the existing row context menu at pointer position
- Row structural actions remain:
  - insert above
  - insert below
  - duplicate row
  - move up
  - move down
  - delete row

### Column Selection

- Left-clicking a group header:
  - sets `selectedGroup`
  - clears `selectedRowId`
  - closes any open context menu
  - highlights the whole selected group column
- Right-clicking a group header:
  - selects that group
  - opens the existing group context menu at pointer position
- Group structural actions remain:
  - insert left
  - insert right
  - duplicate group
  - move left
  - move right
  - delete group

### Protected Areas

- The fixed header row remains structurally protected.
- The five fixed definition columns remain structurally protected:
  - Test Item
  - Section
  - Method
  - Condition
  - Requirement
- The new row-number selector column is not an editable Matrix data column.
- Inline editing remains available in content cells, including group cells.

### Guard Rules

- Cannot delete the last test item row.
- Cannot delete the last group column.
- Move actions are disabled at boundaries.
- Invalid actions keep the existing status-strip protection message pattern.

## Implementation Boundary

Expected page changes:

- Extend the Matrix grid header with one compact row-selector header cell.
- Render one row-selector cell per data row before `Test Item`.
- Add explicit row select and group select handlers.
- Adjust row context menu trigger so the primary row trigger is the row-number selector.
- Keep context menu actions backed by existing row/group operation functions.
- Apply selected row/group class names based on `selectedRowId` and `selectedGroup`.

Expected stylesheet changes:

- Add compact row-selector column sizing.
- Shift existing column width selectors by one column.
- Add selected-row and selected-group background states.
- Keep group columns compact and do not add persistent action controls.

Expected tests:

- Static assertion that row selector cells and group header click selection are wired.
- Static assertion that selected row/group class names exist.
- Static assertion that old row action rail and group `...` controls remain absent.

## Acceptance Criteria

- Matrix Editor has a compact leftmost row-number selector column.
- Clicking a row number highlights the whole row.
- Right-clicking a row number opens row operations.
- Clicking a group header highlights the whole group column.
- Right-clicking a group header opens group operations.
- Inline editing still works in Test Item, fixed text columns, and group cells.
- No persistent row action buttons or group header `...` controls return.
- `npm run build` passes.
- Targeted static checks pass.

## Validation

Required:

```powershell
cd frontend
npm run build
```

Targeted check:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task226 or task225 or task224 or task223"
```

Result:

- `cd frontend; npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task226 or task225 or task224 or task223"` passed (`3 passed`, `71 deselected`).

## Completion Notes

- Added a compact leftmost row-number selector column.
- Clicking a row number selects and highlights the full row.
- Right-clicking a row number opens the row structural context menu.
- Clicking a group header selects and highlights the full group column.
- Right-clicking a group header opens the group structural context menu.
- Kept inline editing, minimum-structure guards, undo, and protected fixed-definition columns.
- No backend, API contract, domain model, persistence, or Workbench page changes were made.
