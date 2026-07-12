# Matrix Editor Step Card Overflow Implementation Plan

**Goal:** Keep all Group Step Workspace child cards within their shared parent width.

**Architecture:** Preserve the existing Matrix Editor DOM and business behavior. Add CSS shrink constraints to the workspace, its cards, tables, and inline controls so content wraps inside the existing grid area.

## Changes

- `frontend/src/workbench.css`: add `min-width: 0` to the workspace and cards; use fixed table layout; make quantity defaults and Samples controls shrinkable.
- `tests/unit/test_frontend_shell_files.py`: add a static regression assertion for the width constraints.

## Validation

- Run the focused Python frontend shell assertions.
- Run `npm run build`.
- Run MatrixEditorWorkspace tests and report any unrelated baseline failures separately.
