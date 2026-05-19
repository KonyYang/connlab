# TASK_230 Matrix Editor Step Token Validation Guards Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_230_MATRIX_EDITOR_STEP_TOKEN_VALIDATION_GUARDS`
- Allowed now: user explicitly requested this Matrix Editor grid behavior/validation refinement.

## Goal

Implement constrained step-token editing guards in matrix group cells:

1. Default empty values are blank.
2. Token syntax limited to `number[,number...]`.
3. Group-level token set must be strictly continuous from 1 and unique.
4. Violations produce clear inline and status-strip feedback.

## Minimal Design

1. Cell value default
- Replace current default `"-"` with `""` for all group step cells.

2. Token parsing rules
- Normalize each cell by trimming.
- Allowed tokens: `^\d+(,\d+)*$` for non-empty values.
- Empty is allowed.
- Parse non-empty token lists into integers.

3. Group-level validation
- For each group column:
  - collect all numbers from all rows
  - detect duplicates
  - sort unique numbers, require first value `1`
  - require each next value increments by `1`
- Produce:
  - per-cell format error ids
  - per-group sequence error ids
  - user-facing error summary text

4. UI feedback
- Cell invalid class for:
  - bad format
  - group sequence violation (for cells in that group that have values)
- Status strip priority:
  - group-name error (existing)
  - step-token format/sequence errors
  - last message/default text

## Files

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
  - add validation selectors/helpers
  - update default value builders
  - wire invalid classes and status message
- `frontend/src/workbench.css`
  - ensure invalid cell visual style exists and is high-visibility
- `tests/unit/test_frontend_shell_files.py`
  - add/adjust static assertions for token guard logic markers

## Risks

- Over-validating empty cells should be avoided.
- Group-level error highlighting should not block regular text editing interactions.
- Parsing must be deterministic and fast for larger matrices.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task230 or matrix_editor or task229"
```

## Out Of Scope

- Backend persistence of validation result.
- Non-numeric token formats (ranges, suffixes, parentheses).
