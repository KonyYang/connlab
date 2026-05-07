# TASK_105_NEW_PROJECT_EDITOR_TEXTAREA_SCROLLBAR_HOTFIX

## Status

done

## Purpose

Fix New Project application editor textarea behavior in the right-side function card area.

The `Description of Requested Testing` and `Additional Information` editing boxes should not expose vertical drag-resize scrollbars when content becomes multi-line. Their behavior should match the existing `Test Sample Information` table cell editor logic.

## Scope

- Frontend-only hotfix for New Project editor / Precheck shared editing surface.
- Keep existing business data and API behavior unchanged.
- Align textarea interaction behavior:
  - auto-grow with content
  - no vertical drag handle
  - no inner vertical scrollbar for normal multi-line editing

## Out Of Scope

- No workflow change.
- No backend change.
- No task-sequence advancement into `TASK_104`.

## Validation

Required:

```powershell
npm run build
```

Optional:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

## Stop Rule

After implementation and board update, stop without entering the next task.
