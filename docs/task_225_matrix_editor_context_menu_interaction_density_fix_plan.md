# TASK_225 Matrix Editor Context Menu Interaction Density Fix Plan

## Goal

Address the usability regression from `TASK_224` by reclaiming horizontal space in Matrix Editor and moving structural actions to right-click context menus.

## User Feedback Mapping

Observed issues:

- `Row` control column consumes too much width.
- Group header `...` action controls consume width and reduce group visibility.
- Matrix editing surface is narrow, especially with many group columns.

Requested direction:

- Prefer right-click context menu interaction for structural operations.
- Keep table area compact.
- Optional compact row marker is acceptable if needed for row targeting.

## Proposed Hotfix Design

1. Remove row action rail and row action buttons from table cells.
2. Remove group header inline action controls and `details` menus.
3. Introduce custom context menu state in page-level local state:
   - menu visibility
   - anchor position (`x`,`y`)
   - target kind (`row` or `group`)
   - target id/index
4. Bind `onContextMenu`:
   - body row cells -> row menu
   - group header cells -> group menu
5. Reuse `TASK_224` structural handlers and guard messaging.
6. Keep top-level `Add test item` / `Add group` / `Undo`.
7. Keep contextual status strip for guard reasons and selection message.

## Menu Content

Row menu:

- Insert above
- Insert below
- Duplicate row
- Move up
- Move down
- Delete row

Group menu:

- Insert left
- Insert right
- Duplicate group
- Move left
- Move right
- Delete group

Disabled items:

- show disabled style in menu
- clicking disabled item does nothing
- status strip shows existing guard reason

## Guard Rules (Preserve Existing)

- Cannot delete last row.
- Cannot delete last group.
- Cannot move first row up.
- Cannot move last row down.
- Cannot move first group left.
- Cannot move last group right.
- Fixed first five columns cannot receive structural group operations.

## CSS Changes

- Remove/disable styles for:
  - `.matrix-editor-row-controls`
  - `.matrix-editor-row-menu`
  - `.matrix-editor-group-head`
  - `.matrix-editor-group-menu`
- Add styles for compact floating context menu:
  - menu container
  - menu items
  - disabled items
  - backdrop/close behavior if needed

## Implementation Boundary

Allowed files:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Not allowed:

- backend/API/domain changes
- broader Matrix redesign
- Workbench changes

## Risk Notes

- Browser native context menu must be prevented only where custom menu is needed.
- Menu placement near viewport edges must avoid clipping (basic clamp logic).
- Must preserve inline editing focus behavior when right-clicking.

## Validation

Automated:

```powershell
cd frontend
npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task225 or task224 or task223"
```

Manual smoke:

1. Right-click any test-item row cell and confirm row menu appears.
2. Right-click any group header and confirm group menu appears.
3. Confirm no always-visible row action column.
4. Confirm no always-visible group `...` control.
5. Confirm guard behavior for last row/group delete.
6. Confirm group visibility improves due to reclaimed width.

## Model Fit

`GPT-5.3-codex` medium is appropriate for this hotfix because it is a focused React state/event and CSS adjustment with existing logic reuse.
