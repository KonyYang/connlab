# TASK_252CO_MATRIX_EDITOR_SAMPLES_INLINE_AND_NOTES_LABEL_MINIFY

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CO_MATRIX_EDITOR_SAMPLES_INLINE_AND_NOTES_LABEL_MINIFY`

## Why This Task Is Allowed Now

- User explicitly requested a bounded UI refinement in Matrix Editor Step preview:
  - `Samples` label and input on one line
  - simplify `Samples Notes` heading to `Notes` or remove it
- This is a narrow frontend-only change without domain/runtime expansion.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

## Objective

1. Keep `Samples` label and samples input in one horizontal row.
2. Simplify sample-note heading from `Samples Notes` to `Notes`; if no heading is preferred by layout, remove heading text.
3. Preserve existing sample note body content and marker mapping behavior.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task/plan/board documentation updates

Forbidden:

- parser/API/backend changes
- unrelated Matrix Editor behavior changes

## Acceptance Criteria

1. `Samples` and input render on one line in Step preview card.
2. Sample note title is simplified (`Notes`) or omitted, with note content still visible.
3. Existing step/item note cards remain unchanged.
4. Frontend static checks and build pass.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252co or matrix_editor"
```

```powershell
cd frontend
npm run build
```
