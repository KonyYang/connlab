# TASK_130_EXTERNAL_EXCEL_STRUCTURE_PROBES

## Status

done

## Purpose

Add read-only external Excel structure probes before any lock, backup, or write gateway work.

## Scope

- Read external Excel files without writing.
- Validate workbook-level structure signals:
  - readable workbook
  - expected sheet names or sheet-name patterns
  - expected header names
  - expected date-like header fields where applicable
- Apply probes to registered external Excel resources:
  - `ltr_workbook`
  - `standard_record_excel`
  - `equipment_calibration_excel`
- Keep `.xls` write/COM work out of scope; legacy `.xls` may only receive non-mutating existence/readability handling available in current infrastructure.

## Out Of Scope

- Do not write to any public-drive Excel file.
- Do not implement lock files, backup execution, or short transactions.
- Do not implement LTR workbook write preview or commit.
- Do not add frontend UI.
- Do not implement Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py -q
py -m pytest tests\unit tests\integration -q
```

Completed:

- `py -m pytest tests\unit\test_excel_structure_probe.py tests\unit\test_external_resource_service.py tests\unit\test_ltr_workbook_snapshot_gateway.py -q`, result `17 passed`.
- `py -m pytest tests\unit tests\integration -q`, result `367 passed`.

## Stop Rule

Stop after implementation and update `docs/task_board.md`.
