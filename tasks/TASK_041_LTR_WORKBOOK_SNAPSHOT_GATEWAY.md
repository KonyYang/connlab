# TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY

## Status

done

## Goal

Read LTR workbook metadata and existing numbers through an infrastructure gateway without writing.

## Scope

- Add a read-only LTR workbook snapshot gateway under `backend/infrastructure/office/`.
- Accept workbook path as input; do not hard-code the real local backup path in code or tests.
- Detect workbook format such as `.xls`, `.xlsx`, or unsupported.
- Report sheet strategy, readable sheets, existing LTR numbers where possible, and file metadata.
- Return explicit errors for missing file, unsupported format, and unreadable workbook cases.
- Add tests using generated or temporary workbook fixtures where safe.

## Out Of Scope

- Workbook write.
- LTR registration preview.
- LTR local commit.
- Readiness service or API.
- Frontend changes.
- Folder evidence placement.
- Lifecycle guards.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- Writing to `D:\Source\Office Auto\TestDocument\LTR_number.xls`.

## Inputs

- `backend/infrastructure/office/excel_workbook_gateway.py`
- `backend/modules/ltr/ltr_number_rules.py`
- Configurable workbook path supplied by caller/test
- Phase 7 plan workbook rules

## Outputs

- Read-only LTR workbook snapshot model/gateway.
- Tests for supported fixture reads and explicit unsupported/missing file errors.
- Task board update after completion.

## Acceptance Criteria

- No API/UI/application service opens Excel directly.
- Gateway reports workbook format as `.xls`, `.xlsx`, or unsupported.
- Gateway identifies sheet strategy or reports unsupported layout.
- Gateway lists existing monthly numbers where possible.
- File lock, missing file, and unsupported adapter errors are explicit.
- No write operation exists in this task.
- No tests write to the real workbook path.

## Validation

- Run focused workbook snapshot gateway tests.
- Run related Office boundary tests if shared Office gateway code is touched.
