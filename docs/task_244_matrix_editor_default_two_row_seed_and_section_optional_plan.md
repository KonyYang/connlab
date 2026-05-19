# TASK_244 Matrix Editor Default Two-Row Seed And Section Optional Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_244_MATRIX_EDITOR_DEFAULT_TWO_ROW_SEED_AND_SECTION_OPTIONAL`
- Allowed now: user requested this specific Matrix Editor initialization correction after TASK_243 completion.

## Task Understanding

Goal:

- A fresh Matrix Editor should start with a practical two-row starter grid:
  - first row contains the standard Visual Examination starter values from the screenshot
  - second row remains blank for the next test item
  - one group column remains available
- `Section` is optional and should not show required-field red highlight when blank.

Input data:

- Static frontend initial Matrix Editor seed values.
- Existing Matrix Editor local draft state and required-field display logic.

Output data:

- Frontend-only initial editable rows and display cues.
- No persisted Matrix draft contract changes.

Involved modules:

- Matrix Editor feature workspace.
- Existing frontend static test file.

Not allowed:

- backend/API/domain/persistence changes
- Matrix save/load contract changes
- layout redesign
- Step preview rule changes
- structural row/group operation changes

## Minimal Change Design

Current initialization after TASK_243:

- `buildInitialGroupColumns()` returns one group column.
- `buildInitialMatrixRows()` returns one blank row.
- render logic marks `Section` blank as `is-empty-required`.

Planned change:

1. Keep `buildInitialGroupColumns()` as one `G1` group.
2. Update `buildInitialMatrixRows()` to return two rows:
   - row 1 seeded with:
     - `item`: `Visual Examination`
     - `section`: ``
     - `method`: `EIA-364-18B`
     - `condition`: `10x min magnification`
     - `requirement`: `No detrimental condition`
     - `groups`: `{ "group-1": "1" }`
   - row 2 blank with `{ "group-1": "" }`
3. Keep `buildEmptyRow()` unchanged so added/inserted rows still start blank.
4. Remove required highlight from blank `Section` rendering only.
5. Keep required highlights for `Test Item`, `Method`, `Condition`, and `Requirement`.
6. Keep row `No.` missing-step warning behavior unchanged.

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- update `HEADER_METRICS` item/step count if still static
- update `buildInitialMatrixRows()`
- remove `is-empty-required` class assignment from the `Section` cell editor

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_244 checks for:
  - two initial rows
  - first-row Visual Examination seed values
  - first-row group step `1`
  - second-row blank group step
  - Section no longer uses `is-empty-required`
  - other required fields still use `is-empty-required`

3. `tasks/TASK_244_MATRIX_EDITOR_DEFAULT_TWO_ROW_SEED_AND_SECTION_OPTIONAL.md`
- update status and validation after implementation.

4. `docs/task_board.md`
- mark TASK_244 as complete after implementation and validation.

## Risks

- Header metrics are currently static. If left at `Items: 1` and `Steps: 0`, they would contradict the new initial grid. This task should adjust the static metrics to `Items: 2` and `Steps: 1` unless implementation finds they are already derived.
- The initial first row is a convenience starter value, not a persisted backend template. It should remain local frontend seed behavior until a future task defines structured Matrix templates.
- `Section` optionality is a display-validation change only. It does not introduce backend validation rules.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task244 or matrix_editor"
```

## Review Checklist For Implementation

- Architecture: frontend-only, no API/backend/domain changes.
- Scope: only current TASK_244 behavior.
- UI: no layout redesign or visual polish.
- Data: no Matrix domain model or persistence change.
- Tests: static frontend test added or updated for the seed and optional Section behavior.

## Stop Point

After this plan is reviewed, implementation must wait for explicit user approval.
