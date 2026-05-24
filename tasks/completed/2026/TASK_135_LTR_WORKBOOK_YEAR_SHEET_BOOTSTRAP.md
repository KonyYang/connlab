# TASK_135_LTR_WORKBOOK_YEAR_SHEET_BOOTSTRAP

## Status

done

## Purpose

Add a controlled bootstrap path for missing annual LTR workbook sheets so write commit can proceed safely on a new year without silent sheet creation.

## Scope

- Add infrastructure capability to copy a configured template year sheet into a missing target year sheet inside the locked short transaction.
- Add controlled cleanup of configured data rows in the newly copied year sheet while preserving workbook structure and headers.
- Add explicit operator confirmation gate for year-sheet bootstrap in workbook write commit flow.
- Keep bootstrap behavior within existing lock/backup/short transaction boundaries.
- Keep existing duplicate checks and number rules intact.

## Out Of Scope

- Do not add a full year-sheet management UI.
- Do not silently bootstrap without explicit operator confirmation.
- Do not change unrelated LTR numbering business rules.
- Do not implement Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q
py -m pytest tests\unit tests\integration -q
```

Completed:

- `py -m pytest tests\unit\test_ltr_workbook_write_commit_service.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py tests\integration\test_ltr_workbook_write_commit_api.py -q`, result `23 passed`.
- `py -m pytest tests\unit tests\integration -q`, result `392 passed`.

## Stop Rule

Stop after implementation, review checklist, validation, and `docs/task_board.md` update.
