# TASK_132_LTR_WORKBOOK_WRITE_PREVIEW

## Status

done

## Purpose

Map confirmed New Project data and setup confirmation values into a no-write LTR workbook row preview.

## Scope

- Add a backend application service that previews the LTR workbook write mapping.
- Build the same A:Q column values used by the Excel COM row writer.
- Return workbook path, target sheet, target row if known, and per-column preview values.
- Accept explicit New Project setup confirmation values:
  - LTR number
  - plan date
  - Test Item
  - Sample Description
  - Location
  - Test Type in sheet
  - Project Leader
- Use confirmed Project/ApplicationForm/SampleInfo records as supporting source data.
- Do not open, lock, back up, save, or mutate the external workbook.

## Out Of Scope

- Do not implement LTR workbook write commit.
- Do not connect this preview to the New Project button.
- Do not add frontend UI.
- Do not write public-drive Excel files.
- Do not implement Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_ltr_workbook_write_preview_service.py -q
py -m pytest tests\unit tests\integration -q
```

Completed:

- `py -m pytest tests\unit\test_ltr_workbook_write_preview_service.py tests\integration\test_ltr_workbook_write_preview_api.py tests\unit\test_ltr_workbook_transaction_gateway.py tests\unit\test_excel_com_ltr_workbook_gateway.py -q`, result `14 passed`.
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q`, result `17 passed`.
- `py -m pytest tests\unit tests\integration -q`, result `376 passed`.
- `git diff --check`, result passed with CRLF working-copy warnings only.

## Stop Rule

Stop after implementation, review checklist, validation, and `docs/task_board.md` update.
