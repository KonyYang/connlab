# TASK_226 Matrix Editor Row Selector And Selection Highlight Plan

## Phase And Task Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_226_MATRIX_EDITOR_ROW_SELECTOR_AND_SELECTION_HIGHLIGHT`
- Allowed now because: `TASK_225` is complete, and the user requested a bounded follow-up to make row operations follow the same selected-target and right-click menu pattern as group columns.

## Task Goal

Improve Matrix Editor row and group operation targeting without expanding workflow scope:

- Add a compact row-number selector column.
- Let users click a row number to select and highlight a row.
- Let users right-click the selected row number to open row operations.
- Let users click a group header to select and highlight a group column.
- Let users right-click the selected group header to open group operations.

This task is not a UI redesign. It is a local Matrix grid interaction refinement.

## Inputs

- Existing Matrix Editor frontend state:
  - `editableRows`
  - `groupColumns`
  - `selectedRowId`
  - `selectedGroup`
  - `contextMenu`
- Existing row/group structural operation functions from `TASK_224` and `TASK_225`.
- Existing inline editing mechanism in `MatrixAutoGrowTextarea`.

## Outputs

- Matrix Editor grid with a compact row-number selector column.
- Clear selected row and selected group column state.
- Row and group context menus opened from selected structural target surfaces.
- Updated static frontend regression checks.

## In Scope

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task status and task board updates after implementation

## Out Of Scope

- Backend changes
- API changes
- Domain model changes
- Persistence changes
- Workbench page changes
- Complex modal workflows
- Keyboard shortcut system
- Multi-row or multi-column selection
- Visual redesign beyond selected-state and row-selector styling needed for the interaction

## Interaction Design

### Row Operations

Use a narrow first column as a row-selector surface. It exists because rows do not have a natural header target like group columns.

- Header: compact non-action header cell, for example `No.` or an unobtrusive row marker.
- Data rows: display `1`, `2`, `3`, etc.
- Left-click row number: select row and highlight the entire row.
- Right-click row number: select row and open row context menu.
- Right-clicking ordinary data cells may be kept as a convenience only if it does not interfere with inline editing, but the primary row operation trigger is the row number.

### Group Operations

Use the existing group header as the structural target.

- Left-click group header: select the column and highlight all cells in that group.
- Right-click group header: select the column and open group context menu.
- No visible `...` menu button should return.

### Highlight Behavior

- Row selection: apply a selected-row class to the `<tr>` so all row cells show selected state.
- Group selection: apply selected-group class to the group header and all cells under the selected group.
- Row and group selection are mutually exclusive:
  - selecting a row clears selected group
  - selecting a group clears selected row
- Clicking normal editable cells should preserve editing behavior and should not unexpectedly open structural menus.

## Implementation Notes

### `ProjectMatrixEditorPage.tsx`

Expected minimal changes:

1. Add `selectRow(rowId)` and `selectGroup(group)` handlers.
2. Update `openRowContextMenu` so it can be called from the row-number selector and selects by row index/id.
3. Add a first `<th>` for the row selector.
4. Add a first `<td>` per row with row number and click/context-menu handlers.
5. Add selected class names:
   - selected row on `<tr>`
   - selected group header on `<th>`
   - selected group cells on group `<td>`
6. Keep existing row/group operation functions unchanged unless minor indexing adjustment is needed after adding the selector column.

### `workbench.css`

Expected minimal changes:

1. Add compact row selector width, approximately `32px` to `38px`.
2. Shift the existing fixed-column width selectors by one column:
   - row selector becomes column 1
   - Test Item becomes column 2
   - Section becomes column 3
   - Method becomes column 4
   - Condition becomes column 5
   - Requirement becomes column 6
   - groups start at column 7
3. Add selected row/group background rules using existing cool workbench selection tones.
4. Keep group columns compact and preserve text wrapping.

### Tests

Update `tests/unit/test_frontend_shell_files.py` with a focused `TASK_226` static test:

- row selector class and row number rendering are present
- row selector click and context menu handlers are present
- group header click selection and context menu handlers are present
- selected row/group class names are present
- old persistent action controls remain absent

## Risks

- Adding a row-number column reduces horizontal room. Mitigation: keep it compact and non-action-only, unlike the previous wide Row action column.
- CSS `nth-child` selectors must shift correctly after inserting the selector column.
- Group column selected state must not make editable group cells hard to read.
- Row selection must not break inline editing focus.

## Validation Plan

Run:

```powershell
cd frontend
npm run build
```

Run:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task226 or task225 or task224 or task223"
```

Manual smoke expectation:

1. Open Matrix Editor.
2. Click row number `2`: row 2 highlights.
3. Right-click row number `2`: row menu opens for row 2.
4. Click group header `G2`: G2 column highlights.
5. Right-click group header `G2`: group menu opens for G2.
6. Edit Test Item or a group cell: inline editing remains stable.

## Review Boundary

Implementation should start only after explicit user approval.
