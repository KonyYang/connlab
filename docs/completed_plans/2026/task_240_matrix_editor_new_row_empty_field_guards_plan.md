# TASK_240 Matrix Editor New Row Empty Field Guards Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_240_MATRIX_EDITOR_NEW_ROW_EMPTY_FIELD_GUARDS`
- Allowed now: user requested explicit validation cues for empty row content.

## Goal

Improve row authoring feedback by highlighting missing mandatory base fields and missing group step definitions.

## Minimal Design

1. Base 5 fields empty-state class

- In row rendering, for each base field textarea:
  - if `trim() === ""` append class `is-empty-required`
- Apply red border/background style in CSS.

2. All-group-empty row cue

- Compute `rowHasNoGroupSteps` per row:
  - all `row.groups[group.id]` trimmed empty
- Apply class on each group step input for that row:
  - `is-row-step-empty`
- Keep stronger existing invalid class precedence (`is-invalid`) for format/sequence errors.

3. Status strip message behavior

- Keep existing message logic unchanged in this task (avoid scope expansion).

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- add row-level empty checks
- append class names on base fields and group cells

2. `frontend/src/workbench.css`
- add styles:
  - `.matrix-editor-inline-textarea.is-empty-required`
  - `.matrix-editor-inline-input.is-row-step-empty`

3. `tests/unit/test_frontend_shell_files.py`
- add TASK_240 static checks for new classes/wiring.

## Risks

- Empty-row cue could visually conflict with selected-row highlight; keep warning style subtle but visible.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task240 or matrix_editor"
```

## Out Of Scope

- backend validation/persistence enforcement
- new status-strip message redesign
