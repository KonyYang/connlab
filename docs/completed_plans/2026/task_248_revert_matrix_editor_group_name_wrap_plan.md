# TASK_248 Revert Matrix Editor Group Name Wrap Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP`
- Allowed now: user explicitly requested reverting the most recent TASK_247 change.

## Task Understanding

Goal:

- Undo the group header name wrapping introduced by TASK_247.
- Restore the previous single-line clipped group name input behavior.
- Do not touch TASK_246 fixed-width table sizing.

Input data:

- Current Matrix Editor CSS after TASK_247.
- Existing static tests, including TASK_247 assertions.

Output data:

- CSS rollback for `.matrix-editor-group-name-input`.
- Updated static tests reflecting rollback behavior.

Involved modules:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Not allowed:

- backend/API/domain/persistence changes
- group column width changes
- TASK_246 column width rollback
- Matrix data or validation rule changes
- row/group structural operation changes

## Minimal Change Design

Current TASK_247 behavior:

```css
white-space: normal;
overflow-wrap: anywhere;
word-break: break-word;
```

Rollback target:

```css
white-space: nowrap;
overflow: hidden;
text-overflow: ellipsis;
```

Planned change:

1. Replace group name input wrapping rules with the previous single-line clipping rules.
2. Keep all fixed column width rules intact:
   - group columns remain `width/min-width/max-width: 44px`
3. Update TASK_247 test coverage into TASK_248 rollback coverage:
   - assert nowrap/hidden/ellipsis are present in the group input block
   - assert wrapping-specific rules are absent from the group input block
   - keep group column width assertions intact

## File-Level Changes

1. `frontend/src/workbench.css`
- rollback only `.matrix-editor-group-name-input` wrapping lines

2. `tests/unit/test_frontend_shell_files.py`
- remove or replace TASK_247 wrapping assertion
- add TASK_248 rollback assertion

3. `tasks/TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP.md`
- update status and validation after implementation.

4. `docs/task_board.md`
- mark TASK_248 complete after implementation and validation.

## Risks

- This restores the prior clipping/ellipsis behavior, so long names may still be visually truncated. That is intentional because the TASK_247 wrap effect was rejected.
- This task does not introduce an alternative display strategy for longer group names. A future task can evaluate a better design if needed.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task248 or matrix_editor"
```

## Review Checklist For Implementation

- Architecture: frontend CSS/static tests only.
- Scope: rollback TASK_247 only.
- UI: no new visual behavior beyond restoring prior single-line group name input.
- Data: no Matrix data model changes.
- Tests: targeted static test confirms rollback.

## Stop Point

After this plan is reviewed, implementation must wait for explicit user approval.
