# TASK_235 Matrix Editor Requirement Split Colon Variant Support Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_235_MATRIX_EDITOR_REQUIREMENT_SPLIT_COLON_VARIANT_SUPPORT`
- Allowed now: user supplied additional real requirement format and approved opening this controlled task.

## Goal

Refine the TASK_234 requirement split parser to support multi-clause colon variant blocks while keeping conservative fallback behavior.

## Parser Update Design

Current limitation:

- semicolon split approach can break when both initial and after blocks each contain multiple semicolon-separated clauses.

Planned approach:

1. Normalize whitespace/newlines.
2. Find first `Initial` marker.
3. Find first `After` / `After test` marker position.
4. `initialPart` = text from `Initial` marker to before `After` marker (trim trailing separators).
5. `followPart` = text after `After...:` label to end (trim leading/trailing separators).
6. If either part is empty, return `null` and keep original requirement.

This keeps full blocks intact:

- `Initial:Mating <= 150N; Un-mating >= 20N;`
- `Mating <= 200N; Un-mating >= 40N;`

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- replace/extend split helper with marker-position parser
- preserve integration points in existing family loop

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_235 static assertions for marker-position split implementation and colon variant handling markers

## Risks

- Loose marker matching may catch unrelated prose; mitigate with explicit `Initial` and `After` gate checks and conservative fallback.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task235 or task234 or matrix_editor"
```

## Out Of Scope

- backend authority dictionary/parser
- multi-language requirement grammar
- persistence/API behavior
