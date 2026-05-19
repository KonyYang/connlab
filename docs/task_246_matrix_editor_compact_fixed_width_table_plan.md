# TASK_246 Matrix Editor Compact Fixed Width Table Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_246_MATRIX_EDITOR_COMPACT_FIXED_WIDTH_TABLE`
- Allowed now: user reported a smoke-test regression from TASK_245 and requested a bounded correction.

## Task Understanding

Goal:

- Matrix Editor should not force a large 1180px table when only one group column exists.
- The first six columns should use their configured fixed widths.
- The first visible group column should remain visible in the default one-group state.
- More groups should still extend horizontally and scroll, not shrink.

Input data:

- Existing Matrix Editor CSS from TASK_245.
- User smoke-test screenshot showing the first six columns over-expanded and hiding the group column.

Output data:

- CSS-only table width correction.
- No Matrix data or persistence changes.

Involved modules:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Not allowed:

- backend/API/domain/persistence changes
- Matrix save/load contract changes
- initial row/group seed changes
- row/group structural operation changes
- Step preview changes
- broad layout redesign

## Minimal Change Design

Current TASK_245 behavior:

- `.matrix-editor-main-table` uses:
  - `min-width: max(1180px, 100%)`
  - `width: max-content`
- Column rules have `width` and `min-width`.

Problem:

- The table-level 1180px minimum can distribute extra width across columns under fixed table layout, making the first six columns much wider than intended.
- With only one group column, the table does not need the 12-group baseline width.

Planned change:

1. Remove table-level `min-width: max(1180px, 100%)` from both Matrix table rule blocks.
2. Keep `width: max-content` so the table is sized by fixed columns.
3. Add `max-width` matching `width` and `min-width` for each fixed column group:
   - row selector: `38px`
   - `Test Item`: `124px`
   - `Section`: `48px`
   - `Method`: `88px`
   - `Condition`: `162px`
   - `Requirement`: `116px`
   - group columns: `44px`
4. Apply the same changes to both duplicated Matrix table width rule blocks in `workbench.css`.
5. Keep `.matrix-editor-main-table-wrap { overflow: auto; }` unchanged for many-group horizontal scrolling.

## File-Level Changes

1. `frontend/src/workbench.css`
- remove `min-width: max(1180px, 100%)`
- preserve `width: max-content`
- add `max-width` to fixed column rules
- update both duplicated Matrix table rule blocks consistently

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_246 static checks that:
  - no Matrix table block uses `min-width: max(1180px, 100%)`
  - fixed column groups include matching `width`, `min-width`, and `max-width`
  - group columns remain fixed at `44px`

3. `tasks/TASK_246_MATRIX_EDITOR_COMPACT_FIXED_WIDTH_TABLE.md`
- update status and validation after implementation.

4. `docs/task_board.md`
- mark TASK_246 complete after implementation and validation.

## Risks

- Removing the 1180px table minimum means a one-group table can be narrower than the full grid surface. This is intended because the user wants the first group column visible and the configured minimum width to act as fixed width.
- Many-group matrices still rely on the existing overflow wrapper for horizontal scrolling.
- `workbench.css` has duplicated Matrix table rules; both must be updated to avoid cascade drift.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task246 or matrix_editor"
```

## Review Checklist For Implementation

- Architecture: frontend CSS/static tests only.
- Scope: Matrix Editor table sizing correction only.
- UI: no redesign, no visual polish.
- Data: no Matrix row/group data model changes.
- Tests: targeted static test confirms the compact fixed-width behavior.

## Stop Point

After this plan is reviewed, implementation must wait for explicit user approval.
