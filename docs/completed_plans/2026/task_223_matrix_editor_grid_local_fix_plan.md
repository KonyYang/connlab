# TASK_223 Matrix Editor Grid Local Fix Plan

## Scope

This plan is for a local Matrix Editor grid/table hotfix only. It does not redesign Matrix Editor and does not touch Project Workbench.

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task: none. `TASK_222` is complete, and this `TASK_223` hotfix is allowed because the user explicitly requested a bounded Matrix Editor table-area correction.

## Located Files

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
  - Owns the current Matrix Editor route page and renders the Matrix Grid table directly.
  - Current table has two header rows, the first `#` column, static body cells, and generated group tokens.
- `frontend/src/workbench.css`
  - Owns `.matrix-editor-main-table*` sizing, density, column width, and cell token styling.
  - Contains multiple Matrix table selector blocks, so implementation must update the effective table selectors carefully after removing the `#` column.
- `tests/unit/test_frontend_shell_files.py`
  - Candidate location for focused static guard assertions if the current frontend static checks cover Matrix Editor structure.

## Current Problem Summary

The Matrix Editor table currently:

- renders a left `#` sequence column in both header rows and body rows
- renders an extra grouped header row above the actual column labels
- gives text columns enough width that group columns are pushed out of view
- renders body cells as static text, including group cells

The attached Workbench Matrix Overview reference uses a denser balance where group columns remain visible and text columns wrap instead of dominating the viewport.

## Proposed Minimal Implementation

1. In `ProjectMatrixEditorPage.tsx`, add local editable matrix state initialized from `MATRIX_ROWS`.
2. Remove the `#` header cells and row-number body cell.
3. Replace the two-row header with one formal header row containing:
   - `Test Item`
   - `Section`
   - `Method`
   - `Condition`
   - `Requirement`
   - `G1` through `G12`
4. Represent group cell values in local state, initialized with the current placeholder token logic so the visual sample remains populated.
5. Render body cells through a tiny inline editable cell helper inside the same file, scoped to Matrix Editor only.
6. Update CSS column selectors after the column index shift:
   - text columns become child indexes 1, 3, 4, and 5 depending on field
   - group columns start at child index 6
7. Set compact widths and wrapping behavior:
   - keep `Section` and `Method` compact
   - reduce `Test Item`, `Condition`, and `Requirement` from the current effective widths
   - give group columns fixed/minimum compact width and centered text
   - use `white-space: normal`, `overflow-wrap: anywhere`, and stable `table-layout`/width rules as needed

## Editable Behavior

Interpretation of the user request:

- Header cells are not editable.
- Data-row cells are editable for `Test Item`, `Section`, `Method`, `Condition`, `Requirement`, and group columns.
- Editing is local frontend state only.
- No persistence, save API, backend contract, validation workflow, popup, or modal is added.

## File-Level Changes

Planned implementation files after approval:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
  - import `useState`
  - introduce editable row/group state
  - remove `#` column
  - collapse table headers to one row
  - add scoped inline editable cell rendering
- `frontend/src/workbench.css`
  - adjust Matrix Editor table width rules and nth-child selectors
  - add inline editor styling scoped under `.matrix-editor-main-table`
  - ensure body text wraps and group columns remain compact
- `tests/unit/test_frontend_shell_files.py`
  - optional focused static assertions for `TASK_223` if existing test style supports it
- `docs/task_board.md`
  - update only after approved implementation and validation

## Risks

- CSS has duplicate Matrix table blocks, so a later selector may override earlier changes. Implementation must update the effective selectors, not only the first matching block.
- Removing the `#` column shifts `nth-child` indexes. Width and group-column selectors must be adjusted together.
- Basic inline edit is intentionally not persisted. This must be clear in completion notes to avoid implying backend save behavior.
- If existing static tests encode the old two-header or `#` column structure, they must be updated only for this specific table behavior.

## Validation Plan

Automated:

```powershell
cd frontend
npm run build
```

If static assertions are added or updated:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task223 or task222 or task221"
```

Manual:

- Open Matrix Editor.
- Verify no `#` header/body column.
- Verify one header row only.
- Verify text columns wrap and do not dominate the first viewport.
- Verify group columns `G1/G2/G3...` are more visible.
- Edit a text body cell and a group body cell inline.
- Confirm Project Workbench Matrix Overview is unchanged.

## Model Fit

`GPT-5.3-codex` with `medium` reasoning is suitable.

This is a bounded frontend hotfix with localized JSX/CSS changes, simple local state, and no backend/API/domain work. The main difficulty is careful selector/index handling after the removed column, which is appropriate for `medium` reasoning.
