# TASK_252B Plan - Matrix Editor Single-Card Import Flow

## 1. Task Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Previous task: `TASK_252A` complete
- New planned task: `TASK_252B_MATRIX_EDITOR_SINGLE_CARD_IMPORT_FLOW`
- Why allowed: user explicitly accepted this refinement direction

## 2. Goal

Simplify Matrix import from dual-entry + multi-action flow to single entry and explicit final apply actions.

## 3. Planned UX

1. Top action strip:
   - remove `Import Matrix`
   - keep `Choose .docx`
   - keep `Undo`
2. Import workspace:
   - always visible (single card)
   - source document shown as read-only selected filename
   - remove `Browse` inside field row
3. Actions:
   - remove `Preview`
   - remove `Apply import`
   - keep `Replace` and `Append` as commit actions
4. Parse behavior:
   - auto-preview immediately after file selection
   - correction inputs (`page`, `table on page`, `table text`) can trigger reparse via lightweight control (enter key or explicit `Reparse`)
   - selecting a file only prepares an import preview; it must not write to the Matrix grid
   - `Replace` and `Append` are disabled until the latest successful preview matches the current correction fields
5. Source identity:
   - selected source display must use the original filename from the file picker
   - source trace shown to the user must not expose backend temporary names such as `tmp*.docx`

## 4. Architecture Fit

- Frontend remains thin and uses typed API client.
- Existing backend `.docx` upload preview endpoint remains the parse source.
- No route directly handles Office logic.
- Import write remains explicit through current draft-creation path.
- The browser-only implementation will not launch Word or other OS applications. That belongs in a later desktop-shell/PyWebView task.

## 5. File-Level Change Plan

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `tasks/TASK_252B_MATRIX_EDITOR_SINGLE_CARD_IMPORT_FLOW.md`

## 6. Risks

1. Auto-preview race conditions during repeated file selection
   - mitigation: guard with existing loading state and latest selected file
2. Removing explicit preview button may hide parsing state
   - mitigation: show clear loading and parse status summary
3. Replace/Append accidental click
   - mitigation: disable when no successful preview payload
4. Upload response currently reports temporary backend filenames
   - mitigation: override user-facing source display with selected `File.name`, and consider API filename preservation if needed
5. Correction fields can become stale after auto-preview
   - mitigation: track preview selector key and disable commit when fields no longer match parsed result

## 7. Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252b or task252a or matrix_editor"
```

```powershell
cd frontend
npm run build
```

## 8. Stop Point

Do not implement until user explicitly approves `TASK_252B`.
