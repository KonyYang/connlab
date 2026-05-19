# TASK_245 Matrix Editor Fixed Column Widths Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_245_MATRIX_EDITOR_FIXED_COLUMN_WIDTHS`
- Allowed now: user requested this specific Matrix Editor table width correction after TASK_244 completion.

## Task Understanding

Goal:

- Matrix Editor table columns should not shrink when group count grows.
- The left Matrix definition columns and every group column should keep a predictable width.
- When there are more groups than fit in the main viewport, horizontal scrolling is acceptable and preferred over compressed cells.

Input data:

- Existing Matrix Editor table CSS.
- Existing group add/duplicate/insert operations that can increase group column count.

Output data:

- CSS-only sizing behavior for Matrix Editor table columns.
- No Matrix data or persistence changes.

Involved modules:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Not allowed:

- backend/API/domain/persistence changes
- Matrix save/load contract changes
- row/group operation changes
- initial seed data changes
- Step preview behavior changes
- broad layout redesign

## Minimal Change Design

Current state:

- `.matrix-editor-main-table` uses `table-layout: fixed`.
- Column selectors already define `width` values.
- The same width rules exist in two CSS blocks and must stay consistent.
- With only `width`, browser table layout can still compress cells when the table is constrained.

Planned change:

1. Add `min-width` matching the existing `width` for each Matrix table column group:
   - row selector: `38px`
   - `Test Item`: `124px`
   - `Section`: `48px`
   - `Method`: `88px`
   - `Condition`: `162px`
   - `Requirement`: `116px`
   - group columns: `44px`
2. Keep the same values as the current acceptable 12-group baseline.
3. Apply the same `min-width` additions to both duplicated Matrix table width rule blocks in `workbench.css`.
4. If needed, add a table-level `min-width: max-content` or equivalent only inside `.matrix-editor-main-table`, so overflow stays local to the existing table surface.
5. Do not alter colors, fonts, validation styles, row selection, group selection, or context menus.

## File-Level Changes

1. `frontend/src/workbench.css`
- add `min-width` beside existing column `width` rules
- preserve existing column width values
- keep duplicated Matrix table rule blocks consistent

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_245 static checks for fixed width/min-width pairs on left and group columns
- keep existing Matrix Editor tests intact

3. `tasks/TASK_245_MATRIX_EDITOR_FIXED_COLUMN_WIDTHS.md`
- update status and validation after implementation

4. `docs/task_board.md`
- mark TASK_245 complete after implementation and validation

## Risks

- More fixed-width columns will require horizontal scrolling when group count is high. That is intentional for this task because preserving readable group cells is preferred over proportional shrink.
- The table width rules are duplicated in `workbench.css`; implementation must update both blocks or later CSS order could override earlier expectations.
- This task does not make group widths responsive by viewport size. It locks the current accepted 12-group baseline.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task245 or matrix_editor"
```

## Review Checklist For Implementation

- Architecture: frontend CSS/static tests only.
- Scope: Matrix Editor table sizing only.
- UI: no redesign, no visual polish.
- Data: no Matrix row/group data model changes.
- Tests: targeted static test confirms fixed width/min-width behavior.

## Stop Point

After this plan is reviewed, implementation must wait for explicit user approval.
