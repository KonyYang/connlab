# TASK_110_NEW_PROJECT_IMPORTED_FILENAME_VISIBILITY_AND_SAMPLE_TABLE_WIDTH_HOTFIX

## Status

done

## Purpose

Fix two New Project usability regressions:

- imported application form filename should remain visible beside `Application information`
- sample table should provide practical editing width on small screens

## Scope

- Frontend-only hotfix.
- Keep existing workflow/API behavior unchanged.
- Improve sample table with horizontal scrolling and sticky `Actions` column.

## Validation

```powershell
npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q
```
