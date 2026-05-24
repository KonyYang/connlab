# TASK_237 Matrix Editor Fixed Columns BG And Group Header Density Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_237_MATRIX_EDITOR_FIXED_COLUMNS_BG_AND_GROUP_HEADER_DENSITY`
- Allowed now: user explicitly requested this visual density/accessibility refinement.

## Goal

Improve matrix editability cues without changing behavior:

- clearer visual protection zone for left fixed columns
- easier column selection in group headers

## Minimal Change Design

1. Fixed columns background

- Target selector: `.matrix-editor-main-table th:nth-child(-n + 6), .matrix-editor-main-table td:nth-child(-n + 6)` (with selected-row exceptions preserved)
- Use subtle tint close to existing neutral palette; avoid strong contrast

2. Group header capsule density

- Reduce `.matrix-editor-group-name-input` vertical padding/min-height/font-size slightly
- Increase outer header cell vertical padding for `.matrix-editor-group-band` so click area outside input is larger

3. Keep interactions unchanged

- No changes to `onClick/selectGroup`, context menu, or input handlers

## File-Level Changes

1. `frontend/src/workbench.css`
- add/update selectors for fixed columns background
- tune group header cell/input spacing

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_237 static assertion for new style selectors/class rules

## Risks

- Row/column selected states could visually conflict with new background; keep selected-state rules higher priority.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task237 or matrix_editor"
```

## Out Of Scope

- interaction rule changes
- table width redistribution
- requirement/description parsing logic
