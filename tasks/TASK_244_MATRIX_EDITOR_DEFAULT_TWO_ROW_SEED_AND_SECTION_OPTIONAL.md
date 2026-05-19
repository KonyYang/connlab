# TASK_244_MATRIX_EDITOR_DEFAULT_TWO_ROW_SEED_AND_SECTION_OPTIONAL

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_244_MATRIX_EDITOR_DEFAULT_TWO_ROW_SEED_AND_SECTION_OPTIONAL`.

## Why This Task Is Allowed Now

User reviewed the TASK_243 minimal one-row initialization and requested a bounded Matrix Editor initialization correction:

- default to at least two editable rows
- seed the first row with a common Visual Examination step
- keep the second row blank
- treat `Section` as optional, so blank Section cells should not show required-field red highlight

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only default-state and validation-cue adjustment.
- Bounded to Matrix Editor local draft initialization and required-field display.
- No backend/API/domain/persistence changes.
- Existing static frontend test pattern can cover the behavior.

## Objective

Change Matrix Editor initial grid data so a fresh Matrix Editor shows:

1. one populated first test item row
2. one blank second test item row
3. one group column
4. first row group step value `1`
5. blank `Section` cells without red required-field highlighting

## Initial Seed Values

Initial group column:

- `id`: `group-1`
- `name`: `G1`

Initial row 1:

- `Test Item`: `Visual Examination`
- `Section`: blank
- `Method`: `EIA-364-18B`
- `Condition`: `10x min magnification`
- `Requirement`: `No detrimental condition`
- `G1`: `1`

Initial row 2:

- all base fields blank
- `G1`: blank

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- Matrix save/load contract changes
- layout redesign
- group/row structural operation changes
- Step preview rule changes

## Acceptance Criteria

- Initial `groupColumns` contains exactly one group.
- Initial `editableRows` contains exactly two rows.
- First initial row matches the specified Visual Examination seed values.
- Second initial row is blank.
- First row group step value is `1`; second row group step value is blank.
- `Section` blank cells do not receive `is-empty-required`.
- `Test Item`, `Method`, `Condition`, and `Requirement` blank cells keep existing required-field highlighting.
- Existing missing-step cue remains on row `No.` for rows with all blank group steps.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task244 or matrix_editor"
```

Result: passed (`21 passed`, `69 deselected`).
