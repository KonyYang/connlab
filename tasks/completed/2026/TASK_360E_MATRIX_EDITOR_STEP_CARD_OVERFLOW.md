# TASK_360E Matrix Editor Step Card Overflow

Status: complete
Lane: `matrix-editor-step-card-overflow`
Owner Role: Developer
Created: 2026-07-11

## Purpose

Keep the Group, Step quantity setup, and Samples cards inside the shared Group Step Workspace width.

## Scope

- Add shrink constraints to the Matrix Editor workspace and its child cards.
- Use fixed table layout for the Group step output and quantity table.
- Allow quantity default fields and Samples input to shrink/wrap inside the parent.
- Do not change React behavior, API calls, Matrix data, or persistence.

## Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py::test_matrix_editor_step_cards_stay_within_shared_workspace_width tests\unit\test_frontend_shell_files.py::test_task222_matrix_editor_pixel_tuning_preserves_definition_studio_priority -q`: passed, `2 passed`.
- `npm run build`: passed; existing Vite chunk-size warning remains.
- `MatrixEditorWorkspace.test.tsx`: 44 passed, 1 pre-existing Contact Plan preview-button state failure unrelated to CSS.
- Browser bounds verification was unavailable because the in-app browser tab was released during refresh.
