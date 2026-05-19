# TASK_247 Matrix Editor Group Name Wrap Within Fixed Width Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_247_MATRIX_EDITOR_GROUP_NAME_WRAP_WITHIN_FIXED_WIDTH`
- Allowed now: user reported a smoke-test issue in Matrix Editor group header display after fixed-width column tasks.

## Task Understanding

Goal:

- Keep group columns narrow and fixed.
- Let group header names such as `11,12` wrap inside the existing group name input when they cannot fit on one line.
- Do not increase group column width.

Input data:

- Existing Matrix Editor CSS.
- Current group name input styling:
  - `white-space: nowrap`
  - `overflow: hidden`
  - `text-overflow: ellipsis`

Output data:

- CSS-only display behavior for group name input.
- No Matrix data or validation rule changes.

Involved modules:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Not allowed:

- backend/API/domain/persistence changes
- changing group column width
- changing group name validation rules
- changing group structural operations
- changing initial Matrix seed data
- broad visual redesign

## Minimal Change Design

Current issue:

- `.matrix-editor-group-name-input` forces a single line with `white-space: nowrap`.
- Long names or comma-separated short names cannot wrap, so they either clip or render awkwardly inside the 44px fixed group column.

Planned change:

1. Keep group column fixed width from TASK_246:
   - `width/min-width/max-width: 44px`
2. Change only `.matrix-editor-group-name-input` text wrapping:
   - remove or override `white-space: nowrap`
   - use `white-space: normal`
   - use `overflow-wrap: anywhere`
   - use `word-break: break-word` if needed for compact tokens
   - remove or neutralize `text-overflow: ellipsis`
3. Keep focus, empty, duplicate, border, font, padding, and validation colors unchanged.
4. Do not make the group header input wider.

## File-Level Changes

1. `frontend/src/workbench.css`
- adjust `.matrix-editor-group-name-input` wrapping rules only
- preserve the fixed group column width rules

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_247 static checks for:
  - group column fixed width still at `44px`
  - group name input uses wrapping
  - group name input no longer uses nowrap/ellipsis behavior

3. `tasks/TASK_247_MATRIX_EDITOR_GROUP_NAME_WRAP_WITHIN_FIXED_WIDTH.md`
- update status and validation after implementation.

4. `docs/task_board.md`
- mark TASK_247 complete after implementation and validation.

## Risks

- Wrapped group names can increase header row height. This is acceptable because the user requested wrapping instead of wider columns.
- CSS static tests cannot prove exact visual line breaks, but they can prevent the known no-wrap/ellipsis regression.
- Browser text wrapping around punctuation can vary slightly; `overflow-wrap: anywhere` is the conservative choice for fixed 44px columns.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task247 or matrix_editor"
```

## Review Checklist For Implementation

- Architecture: frontend CSS/static tests only.
- Scope: Matrix Editor group header input wrapping only.
- UI: no column width increase.
- Data: no Matrix row/group data model changes.
- Tests: targeted static test confirms wrap rules and fixed width preservation.

## Stop Point

After this plan is reviewed, implementation must wait for explicit user approval.
