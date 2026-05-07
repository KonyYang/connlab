# TASK_128_EXTERNAL_RESOURCE_REGISTRY_AND_VALIDATION

## Status

done

## Purpose

Add a backend registry and validation API for external resources that ConnLab will use in later controlled tasks.

## Scope

- Add SQLite-backed external resource records.
- Support these resource types:
  - `ltr_workbook`
  - `application_form_template`
  - `project_folder_template`
  - `standard_record_excel`
  - `equipment_calibration_excel`
- Store path, active state, validation status, last validation time, and failure reason.
- Validate path existence and expected file/directory type.
- Validate Word and Excel resources through existing Office infrastructure boundaries where available.
- Validate project folder template as a directory and ensure it is usable as a folder template.
- Expose thin FastAPI endpoints for listing, upserting, and validating resources.

## Out Of Scope

- Do not write to public-drive Excel files.
- Do not implement LTR workbook password, lock timeout, or backup directory policy.
- Do not implement external Excel structure probes.
- Do not implement workbook lock/write transaction gateway.
- Do not implement frontend management UI.
- Do not implement Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Validation

Required:

```powershell
py -m pytest tests\unit\test_external_resource_service.py tests\integration\test_external_resource_api.py -q
py -m pytest tests\unit tests\integration -q
```

Completed:

- `py -m pytest tests\unit\test_external_resource_service.py tests\integration\test_external_resource_api.py -q`, result `9 passed`.
- `py -m pytest tests\unit tests\integration -q`, result `359 passed`.

## Stop Rule

Stop after implementation and update `docs/task_board.md`.
