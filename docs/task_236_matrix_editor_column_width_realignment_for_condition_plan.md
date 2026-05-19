# TASK_236 Matrix Editor Column Width Realignment For Condition Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_236_MATRIX_EDITOR_COLUMN_WIDTH_REALIGNMENT_FOR_CONDITION`
- Allowed now: user explicitly requested this UI density refinement.

## Goal

Adjust Matrix grid column width proportions for practical editing:

- shrink `Test Item`, `Section`, `Method`
- widen `Condition`

## Minimal Change Design

Only adjust width rules in `workbench.css` for `.matrix-editor-main-table` column selectors.

Current relevant mapping (nth-child):

1. row selector
2. Test Item
3. Section
4. Method
5. Condition
6. Requirement
7+ groups

Planned direction:

- Reduce `nth-child(2)`, `nth-child(3)`, `nth-child(4)`
- Increase `nth-child(5)`
- Keep `nth-child(6)` and group columns unchanged unless minor balance is necessary

## File-Level Changes

1. `frontend/src/workbench.css`
- update numeric widths in both duplicated matrix-table rule blocks (if present)

2. `tests/unit/test_frontend_shell_files.py`
- optional static check for updated width literals if existing tests rely on exact values

## Risks

- There are duplicated matrix width blocks in stylesheet; update both to avoid inconsistent behavior under media/layout branches.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task236 or matrix_editor"
```

## Out Of Scope

- any change to row/column interaction logic
- right-side Step preview logic
- backend/API/data changes
