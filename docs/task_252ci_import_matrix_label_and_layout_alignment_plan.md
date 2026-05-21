# TASK_252CI Plan - Import Matrix Label And Layout Alignment

## Goal

Restore top action wording/layout to match accepted TASK_252A/252B UX intent:

- primary entry text: `Import Matrix`
- action strip keeps only import + undo
- keep current file-picker and preview/apply behavior unchanged

## File Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- rename `Choose .docx` button label to `Import Matrix`
- keep hidden file input trigger
- ensure no extra top-right placeholder controls

2. `frontend/src/workbench.css` (only if needed)
- minor spacing tweaks to match compact action strip

3. `tests/unit/test_frontend_shell_files.py` (optional)
- update/add static assertion for `Import Matrix` label when needed

## Risks

- low risk; UI text/layout-only

## Validation

- `cd frontend && npm run build`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or task252"`
