# TASK_227 Matrix Editor Editable Group Header And Column Index Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_227_MATRIX_EDITOR_EDITABLE_GROUP_HEADER_AND_COLUMN_INDEX`
- Allowed now: user explicitly requested this Matrix grid refinement after `TASK_226`.

## Goal

Improve Matrix Editor column targeting and naming:

1. Business-editable group names (no fixed `G1/G2/...` display).
2. Excel-like column index letters (`A/B/C...`) as stable selection surface.
3. Keep right-click column structure operations.
4. Keep existing row-number selection and row operations.

## Key Design (Minimal Change)

1. Data split for each group column:
- `id`: internal stable id for operations (non-editable)
- `name`: user-editable display name (can be empty)

2. Visual structure:
- Header row 1: fixed definition headers + editable group name inputs.
- Header row 2: fixed area blank/marker + column index cells `A/B/C...` used for column select/right-click.

3. Interactions:
- Click index letter cell => select whole column and highlight.
- Right-click index letter cell => open existing column context menu.
- Edit group name in header input inline.
- Add group: new column `name=""`, `id` auto-generated internally.

## File-Level Changes

1. `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- Refactor `groupColumns: string[]` to object array with stable `id` + editable `name`.
- Update row group-value keying from old string key to new group `id`.
- Add header inline input for editable group name.
- Add column index row rendering and selection/right-click hooks.
- Ensure existing column ops work by `id`.

2. `frontend/src/workbench.css`
- Add styles for editable group-name input and index row cells.
- Keep compact widths and existing row selector behavior.
- Preserve selected-column highlight.

3. `tests/unit/test_frontend_shell_files.py`
- Add/adjust static checks for:
  - editable group header input
  - index-letter row
  - column right-click hook on index cells
  - new group default empty name behavior marker in source

## Risks

- Mapping migration from `string[]` groups to object groups may break existing operations if keying is inconsistent.
- Need to keep context menu behavior tied to stable `id`, not editable display name.
- Header input focus must not conflict with selection/right-click behavior.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task227 or task226 or task225"
```

## Out of Scope

- Backend persistence for edited group names.
- API/schema/domain updates.
- Batch operations redesign.
- Non-table UI changes.
