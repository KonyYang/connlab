# TASK_235_MATRIX_EDITOR_REQUIREMENT_SPLIT_COLON_VARIANT_SUPPORT

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_235_MATRIX_EDITOR_REQUIREMENT_SPLIT_COLON_VARIANT_SUPPORT`.

## Why This Task Is Allowed Now

User provided an additional real requirement format:

`Initial:Mating ...; Un-mating ...; After test:Mating ...; Un-mating ...;`

Current split helper in TASK_234 may not reliably preserve full multi-clause initial and after segments for this colon-heavy variant.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only parser refinement in existing Step preview rule layer.
- Deterministic string parsing and conservative fallback.
- No backend/API/domain/persistence change.

## Objective

Extend requirement split parser so it handles multi-clause colon variant:

1. Capture full `Initial` block until `After...` marker.
2. Capture full `After` block content after removing the `After...:` prefix.
3. For repeated special-family steps:
   - first -> full `Initial` block
   - remaining -> full `After` block content
4. Keep fallback-to-original behavior when parser confidence is low.
5. Keep manual requirement override precedence.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- matrix model changes
- report/test-record logic changes

## Acceptance Criteria

- Parser supports examples like:
  - `Initial:Mating <= 150N; Un-mating >= 20N; After test:Mating <= 200N; Un-mating >= 40N;`
- First matching step default requirement gets full initial block.
- Remaining matching steps default requirement get full after block (without `After test:` label).
- Existing TASK_234 and TASK_233 behaviors remain intact.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task235 or task234 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task235 or task234 or task233 or matrix_editor"` passed (`14 passed`, `69 deselected`).
