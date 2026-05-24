# Phase 7 LTR Workbook Snapshot Layout

Date: 2026-04-28

## Scope

This document covers the read-only snapshot baseline from `TASK_041` and the
controlled local Excel COM boundary introduced in `TASK_045`.

It records workbook structure and gateway behavior implemented under
`backend/infrastructure/office/`. It does not implement UI behavior or write to
the real public workbook during tests.

## Gateway Boundary

| Item | Current behavior |
|---|---|
| Gateway | `backend.infrastructure.office.ExcelWorkbookGateway` |
| Read method | `read_ltr_workbook_snapshot(path)` |
| Write methods | none |
| Caller path policy | caller supplies the path; code and tests do not hard-code the real backup workbook |
| Password policy | no password is read or stored by this snapshot task; later `.xls` adapter/write tasks must accept password from configuration or caller input, not from hard-coded code |
| `.xlsx` support | read-only package inspection using standard library ZIP/XML parsing |
| `.xls` support | detected as legacy format and rejected with `UnsupportedLtrWorkbookError` until a later adapter task |
| Unsupported extension | rejected with `UnsupportedLtrWorkbookError` |
| Missing file | `FileNotFoundError` |
| Corrupt/unreadable `.xlsx` | `UnreadableLtrWorkbookError` |

## TASK_045 Local Excel COM Boundary

| Item | Current behavior |
|---|---|
| Gateway | `backend.infrastructure.office.ExcelComLTRWorkbookGateway` |
| Office entry point | `OfficeFacade.open_excel_workbook(...)` |
| COM lifecycle | `OfficeLifecycleManager.open_excel_workbook(...)` |
| Default write mode | disabled |
| Password policy | workbook modify password comes from local config or environment; no password is hard-coded |
| Read-only detection | write session checks `workbook.ReadOnly` and blocks when true |
| Normal number allocation | final normal DL is calculated inside an open write session after batch reading target sheet data |
| Batch read rule | annual sheet data is read through `Range("A2:Q{last_row}").Value` |
| Batch write rule | registration row is written through one `Range("A{row}:Q{row}").Value` assignment |

## Real Decrypted Workbook Probe

Local reference file:

```text
C:\Users\White\Desktop\AI information\LTR_number_解密版.xls
```

Probe date: 2026-04-28

Probe mode: Excel COM read-only open; no save, no write.

Observed sheets:

```text
2020, 2021, 2022, 2023, 2024, 2025, 2026,
Filling requirements, 2021 Whisker, 2022&2023 Whisker List
```

Annual sheet structure:

| Column | Header / meaning |
|---|---|
| A | Month |
| B | Total |
| C | Monthly Number |
| D | DL |
| E | Project Type |
| F | Description P/N |
| G | Test Item |
| H | Test Type |
| I | Requested by |
| J | Location |
| K | Project Leader |
| L | Test Result |
| M | Failed item |
| N | Sample deposition |
| O | Sub-contract |
| P | Test Fee |
| Q | Remarks (PO) |

## Snapshot Fields

| Field | Meaning |
|---|---|
| `workbook_path` | Input workbook path |
| `workbook_format` | `.xlsx`, `.xls`, or unsupported classification |
| `size_bytes` | File size |
| `modified_time` | File modified timestamp |
| `sheet_names` | Workbook sheet names from the manifest |
| `readable_sheet_names` | Sheets successfully read by the gateway |
| `sheet_strategy` | `year_sheets`, `year_month_sheets`, or `flat_or_unknown` |
| `existing_ltr_numbers` | Supported LTR number strings found in cell text |
| `unsupported_reason` | Reserved for future non-throwing unsupported snapshots |

## Validation Fixture

The committed tests create a temporary minimal `.xlsx` package in `tmp_path`. The fixture includes:

- one year-named worksheet;
- base DL number;
- suffix DL number;
- W-prefix number;
- invalid text that must be ignored.

No test writes to `D:\Source\Office Auto\TestDocument\LTR_number.xls`.

## Known Limits

- Legacy `.xls` read-only package parsing is still unsupported by `ExcelWorkbookGateway`; local desktop write support is isolated in `ExcelComLTRWorkbookGateway` through Office COM.
- The real LTR workbook may require a password, currently expected by the operator to default to `DGLAB`; this value must remain configurable and must not be hard-coded in code or tests.
- Later workbook adapter/write tasks should automatically open the workbook with the configured password when applying for a new LTR number, and should return an actionable error for missing or invalid password.
- The gateway scans cell text for existing LTR numbers; it does not yet infer target row, writable columns, or full workbook layout.
- Workbook write is implemented only as a feature-gated local COM gateway boundary; tests use fake OfficeFacade objects and do not write the real workbook.
