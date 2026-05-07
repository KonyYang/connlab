# TASK_134_NEW_PROJECT_LTR_WORKBOOK_COMMIT_UI_INTEGRATION

## Status

done

## Purpose

Connect the confirmed LTR workbook write commit backend to the New Project completion workflow without bypassing preview acknowledgement, operator confirmation, or the existing folder creation boundary.

## Scope

- Add frontend API client types and method for `POST /api/projects/{project_id}/ltr-workbook/write-commit`.
- Integrate workbook write commit into the New Project `Apply LTR Number and Create Folder` action after project confirmation and before folder generation.
- Use the existing New Project setup confirmation values for:
  - LTR number choice / specified input
  - Test Item
  - Sample Description
  - Location
  - Test Type in sheet
  - Project Leader
- Require an explicit operator acknowledgement in the UI before the external workbook write is committed.
- Surface workbook write success, replacement/append action, target sheet/row, and backup path in operational copy.
- Surface backend validation errors as actionable New Project completion messages.
- Preserve the existing folder preview/generation flow and use the committed LTR number as the folder DL number.

## Out Of Scope

- Do not implement a full LTR workbook row preview UI.
- Do not silently create missing annual workbook sheets.
- Do not change the backend workbook commit contract except for narrow fixes required by this integration.
- Do not implement Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

Completed:

- `py -m pytest tests\integration\test_new_project_completion_api.py tests\integration\test_ltr_workbook_write_commit_api.py tests\unit\test_frontend_shell_files.py -q`, result `56 passed`.
- `npm run build`, result passed.
- `py -m pytest tests\unit tests\integration -q`, result `389 passed`.

## Stop Rule

Stop after implementation, review checklist, validation, and `docs/task_board.md` update.
