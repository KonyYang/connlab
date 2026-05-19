# TASK_228 Matrix Editor Column Header Direct Context Menu Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_228_MATRIX_EDITOR_COLUMN_HEADER_DIRECT_CONTEXT_MENU`
- Allowed now: user explicitly approved replacing A/B/C row with direct header interaction.

## Goal

Reduce visual noise and ambiguity in Matrix grid while preserving column operations:

1. Remove A/B/C column index row.
2. Use group header itself for select + context menu.
3. Keep editable group names and existing guarded structural operations.

## Design Decision

Use “header-as-handle” pattern:

- Group header container receives:
  - `onClick` => select column
  - `onContextMenu` => open column menu
- Group name input remains editable.
- Input-level event handling prevents accidental menu pop while editing text.

This keeps one operation surface per column and avoids extra pseudo-label rows.

## File-Level Changes

1. `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- Remove the second header row (`A/B/C...` row).
- Keep single header row with editable group-name inputs.
- Bind selection and right-click to group header wrapper.
- Ensure input events do not block typing and do not misfire context menu.
- Keep selected-column highlight behavior.

2. `frontend/src/workbench.css`
- Remove/retire index-row style usage (`.matrix-editor-group-index`) if unused.
- Keep and tune group-header selected styles if needed for clarity.

3. `tests/unit/test_frontend_shell_files.py`
- Update `TASK_227` related expectations to not require index row.
- Add/adjust `TASK_228` assertions:
  - no `toColumnLabel(groupIndex)` rendered in header row
  - group header click/context-menu hooks present
  - editable group header input still present

## Risks

- Click and right-click bindings can conflict with input text editing if event boundaries are not scoped.
- Header interaction should remain predictable when group name is empty.
- Must not regress existing context menu guard behaviors.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task228 or task227 or task226"
```

## Out Of Scope

- Keyboard shortcut additions.
- API/persistence of group names.
- Workbench or non-grid UI changes.
