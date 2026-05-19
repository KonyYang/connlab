# TASK_229B Matrix Editor Page To Feature Decomposition Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_229B_MATRIX_EDITOR_PAGE_TO_FEATURE_DECOMPOSITION`
- Allowed now: approved architecture-risk closure after TASK_229A.

## Goal

Decompose oversized Matrix Editor route page into feature modules without changing behavior.

## Current Problem

- `frontend/src/pages/ProjectMatrixEditorPage.tsx` mixes:
  - static config data
  - runtime state and action handlers
  - menu/selection logic
  - full grid + side panels JSX
- This violates route-page boundary guidance in `docs/frontend_architecture_rules.md`.

## Minimal Decomposition

1. Feature config module
- `frontend/src/features/matrix-editor/matrixEditorConfig.ts`
- move static constants (sample rows, template cards, reference rows, metrics)

2. Feature state hook
- `frontend/src/features/matrix-editor/useMatrixEditorDraftModel.ts`
- own row/group state, validators, selection, context menu state, mutation actions

3. Feature view components
- `frontend/src/features/matrix-editor/MatrixEditorGrid.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorContextMenu.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorStepWorkspace.tsx`
- optional supporting surface component split if needed

4. Route page
- keep route params + `useProjectRuntimeConsoleModel` integration
- compose feature components and pass model props
- avoid owning detailed matrix mutation logic

## File-Level Change Plan

- Add:
  - `frontend/src/features/matrix-editor/matrixEditorConfig.ts`
  - `frontend/src/features/matrix-editor/useMatrixEditorDraftModel.ts`
  - `frontend/src/features/matrix-editor/MatrixEditorGrid.tsx`
  - `frontend/src/features/matrix-editor/MatrixEditorContextMenu.tsx`
  - `frontend/src/features/matrix-editor/MatrixEditorStepWorkspace.tsx`
- Refactor:
  - `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- Adjust static tests:
  - `tests/unit/test_frontend_shell_files.py`

## Behavior Lock (Must Preserve)

- editable cells and auto-grow behavior
- row selector + row context menu operations
- group header selection + context menu operations
- group-name validation: required + unique (case-insensitive)
- error messaging in status strip
- existing undo behavior

## Risks

- prop threading complexity between hook and components
- accidental behavior drift during extraction
- static tests may need selector/string expectation updates

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task229 or task228 or task227"
```

## Out Of Scope

- new Matrix draft API
- Workbench IA changes
- visual redesign
