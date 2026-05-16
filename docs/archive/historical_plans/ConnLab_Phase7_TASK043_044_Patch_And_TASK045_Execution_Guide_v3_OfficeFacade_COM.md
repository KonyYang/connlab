# ConnLab Phase 7 TASK_043 / TASK_044 Patch And TASK_045 Execution Guide

> Revision: v3 鈥?adds OfficeFacade + Excel COM as the recommended local workbook-write implementation for TASK_045, with performance and architecture guardrails.

> Date: 2026-04-28  
> Purpose: give an AI coding agent a focused patch plan after `TASK_043` and `TASK_044` were already completed before the real `LTR_number.xls` details were fully understood.  
> Scope: patch completed work where necessary, then guide the next Excel write task.  
> v3 update: `TASK_045` should implement the local `.xls` write path through `OfficeFacade + Excel COM Gateway`, because the real workbook is legacy `.xls`, password-protected for modify access, and needs format-preserving sheet operations.  
> Recommended file location: `docs/tasks/phase7/TASK_043_044_PATCH_AND_TASK_045_GUIDE.md` or `tasks/TASK_043_044_PATCH_LTR_REAL_WORKBOOK_RULES.md`.

---

## 1. Operator Context

`TASK_043` and `TASK_044` are already completed in the current working repository.

However, they were completed before the real LTR workbook and detailed registration rules were fully provided. Do **not** rewrite them from scratch. The correct next step is a controlled patch:

```text
Patch TASK_043/TASK_044 behavior and contracts where needed
  -> preserve completed structure where possible
  -> add missing real-workbook rules
  -> prepare TASK_045 Excel write implementation
```

The real workbook is an `.xls` public-drive registration file. Users normally open it with a modify/read-write credential. Without the modify credential, the workbook opens as read-only. The public-drive path and modify credential must be soft-coded by configuration, not hard-coded in source. Use an operator-editable local config file so the actual deployment can change the path and password without code changes.

Do not hard-code the real workbook password in source code, tests, fixtures, logs, frontend state, or screenshots. If a config file contains the real password, keep that config file local/operator-managed and exclude it from Git.

---

## 2. Mandatory Read Order For AI Executor

Before coding, read:

1. `AGENTS.md`
2. `docs/task_board.md`
3. Current active task file
4. `docs/archive/historical_plans/ConnLab_Phase7_Real_LTR_Folder_Lifecycle_Plan.md`
5. This patch guide
6. Existing implementation of completed `TASK_043` and `TASK_044`

Then state:

```text
Current phase: <from docs/task_board.md>
Current active task: <from docs/task_board.md>
Patch intent: TASK_043/TASK_044 compatibility patch before TASK_045 Excel write
```

If `docs/task_board.md` does not allow this patch or TASK_045 preparation, stop and update the board first.

---

## 3. Real Workbook Facts To Reflect In Code

### 3.1 Workbook format and access model

- Workbook format is legacy Excel `.xls`.
- Do not assume `openpyxl` compatibility.
- For the local Windows desktop version, the recommended implementation is **`OfficeFacade + Excel COM` through `pywin32`**.
- `openpyxl` is not suitable for the authoritative write path because the workbook is `.xls`, not `.xlsx`.
- `xlrd/xlwt/xlutils` should not be used as the authoritative write path because this task needs modify-password handling, reliable read-only detection, workbook saving, format-preserving sheet copy, and public-drive Excel compatibility.
- UI and application services must not directly open Excel, manage Excel processes, call `win32com`, or handle the workbook password.
- Workbook write is disabled unless explicitly enabled by config/feature flag.

#### Recommended local adapter decision

Use this stack for `TASK_045`:

```text
UI / Presenter
  -> LTR application workflow service
  -> LTRWorkbookGateway interface
  -> ExcelComLTRWorkbookGateway
  -> OfficeFacade
  -> win32com / Excel COM
```

Do **not** use this dependency path:

```text
UI / Controller / Domain Service
  -> win32com.client.Dispatch("Excel.Application")
  -> Workbooks.Open(...)
  -> Cells(...).Value = ...
```

`OfficeFacade` is responsible for Excel process lifecycle and common Office safety settings.  
`ExcelComLTRWorkbookGateway` is responsible for LTR workbook-specific operations.  
The LTR application service is responsible for orchestration and transaction policy.

### 3.2 Workbook sheets

Known annual registration sheets use year labels, for example:

```text
2020
2021
2022
2023
2024
2025
2026
```

There are also helper/special sheets such as filling requirements and Whisker lists. They are not normal LTR registration targets.

### 3.3 Main annual sheet columns

Annual sheets use this effective structure:

| Column | Meaning |
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

Core implementation assumptions:

- Header row is row 1.
- Data begins from row 2.
- LTR number is stored in column D.
- Real code should not rely only on hard-coded columns if a schema/header resolver already exists, but the above mapping is the baseline.

---

## 4. Correct LTR Number Rules

### 4.1 Normal number format

Normal LTR numbers follow:

```text
DL-YYYY-MM-NNN
```

Example:

```text
DL-2026-04-031
```

Invalid for new registration:

```text
W123
ABC
123
pure alphabetic values
pure numeric values
non-DL numbers without a valid DL base pattern
```

### 4.2 Associated number format

Associated LTR numbers are based on a valid base number plus suffix:

```text
DL-YYYY-MM-NNNA
DL-YYYY-MM-NNNB
```

Example:

```text
DL-2025-11-002A
```

The base number is:

```text
DL-2025-11-002
```

Suffix policy should be explicit. If the existing implementation only supports one uppercase letter, keep that policy unless the real workbook shows broader suffix needs. Do not accept arbitrary non-DL identifiers.

### 4.3 Suffix numbers occupy the base sequence

A suffix number occupies its base sequence for normal numbering.

Example existing workbook values:

```text
DL-2026-04-001
DL-2026-04-002
DL-2026-04-003A
DL-2026-04-004
DL-2026-04-005
```

The next normal number is:

```text
DL-2026-04-006
```

because `DL-2026-04-003A` occupies sequence `003`.

---

## 5. Correct Sheet Routing Rules

### 5.1 Normal registration target sheet

Normal registration writes only to the sheet matching the current computer/system year.

Example:

```text
Current system year: 2026
Target write sheet: 2026
Normal number prefix: DL-2026-<current month>-NNN
```

### 5.2 Associated registration target sheet

Associated registration also writes to the current system year sheet, even if the associated LTR number contains an older year.

Example:

```text
Current system year: 2026
Requested associated number: DL-2025-11-002A
Write target sheet: 2026
Base lookup sheet: 2025
```

### 5.3 Associated base lookup sheet

For associated number `DL-2025-11-002A`:

- parse base number: `DL-2025-11-002`;
- parse base year: `2025`;
- search sheet `2025` for the exact base number;
- search sheet `2025` for exact full number `DL-2025-11-002A`;
- list all same-family rows containing/belonging to stem `DL-2025-11-002`, for example:

```text
DL-2025-11-002
DL-2025-11-002A
DL-2025-11-002B
```

Display enough information for operator confirmation:

```text
DL number
Sheet
Row
Requested by
Project Type
Description P/N
Test Item
Project Leader
Remarks / PO
```

### 5.4 Global exact duplicate check

Before writing any associated number, perform a global exact duplicate check across all annual sheets.

If exact same LTR exists anywhere, block the write.

---

## 6. Revised TASK_043 Patch Requirements

`TASK_043` should represent readiness/preflight for data quality and association verification only. It must not reserve, preview, or commit a final normal LTR number.

### 6.1 Normal registration readiness only

Normal LTR registration does **not** need number preflight. Do not show, reserve, or store a candidate normal number before the write transaction.

Patch existing normal preview/check result to include only readiness information:

```text
registration_type = normal
target_write_year_sheet = current system year
number_preflight_required = false
number_preview_allowed = false
final_number_reserved = false
readiness_result
warnings
blockers
```

Important rule:

```text
Normal final number is calculated only inside TASK_045 after workbook lock and modify/write access are obtained.
```

If the existing TASK_043 currently calculates an advisory next number from a read-only snapshot, remove it from normal user-facing flow. At most, keep it as internal debug output disabled by default. It must never appear as a candidate to confirm, reserve, or commit.

### 6.2 Associated registration preflight

Patch or add `AssociatedLTRPreflightResult` with:

```text
requested_associated_number
parsed_base_number
base_year_sheet
current_write_year_sheet
base_found
base_row_summary
family_rows
exact_duplicate_rows_from_snapshot
operator_confirmation_required
operator_confirmed
missing_base_warning
missing_base_continue_reason_required
missing_base_continue_reason
warnings
blockers
```

Preflight may perform read-only lookup and ask the operator to confirm association correctness.

Acceptable preflight outcomes:

```text
Base exists + no snapshot duplicate -> allow operator confirmation
Base exists + snapshot duplicate -> warning/block before commit depending current policy
Base missing -> require explicit warning and continue reason, or block if policy says so
Workbook unavailable -> allow local-only path only if configured
```

### 6.3 Do not hold workbook lock during operator confirmation

Preflight may show dialogs or frontend confirmation states. It must not hold a public-drive lock while waiting for operator input.

---

## 7. Revised TASK_044 Patch Requirements

`TASK_044` is local commit and audit/evidence. It should not assume external workbook write has already occurred unless the commit mode says so.

Patch requirements:

1. Local-only commit must be explicit in the record or evidence.
2. Store enough preflight snapshot/reference data for traceability.
3. Do not treat advisory normal numbers as final registered external workbook numbers.
4. For associated numbers, store operator association confirmation or missing-base continuation reason.
5. Project lifecycle should move to LTR registered only under the accepted local policy.
6. When external workbook write mode is enabled later, TASK_045 should be the source of final workbook row pointer and authoritative external registration result.

Recommended local record/evidence fields if available:

```text
commit_mode: local_only | workbook_synced
registration_type: normal | associated
ltr_number
workbook_status: not_attempted | pending_sync | synced | failed
preflight_snapshot_id / fingerprint
operator_confirmation_summary
missing_base_reason
created_by
created_at
```

If the current domain model is too small, do the minimal safe extension rather than a broad schema redesign.

---

## 8. OfficeFacade + Excel COM Implementation Guidance

`TASK_045` should explicitly use `OfficeFacade + Excel COM` for the local desktop `.xls` write path. This is not a temporary shortcut; it is the most compatible local solution for the current public-drive workbook. The important design rule is that COM is isolated behind infrastructure boundaries and optimized to avoid the slow patterns found in the legacy system.

### 8.1 Responsibility split

```text
OfficeFacade
  - create/reuse an Excel.Application instance when needed;
  - apply safe automation settings;
  - open workbook with configured path and modify password;
  - detect open/read-only failures;
  - save, close, and release COM resources;
  - guarantee cleanup in finally blocks.

ExcelComLTRWorkbookGateway
  - locate annual sheets;
  - read annual sheet snapshots;
  - read DL column / UsedRange in batch;
  - find exact duplicates and same-family rows;
  - create a missing current-year sheet when authorized;
  - clear concrete registration rows while preserving template formatting;
  - append one complete LTR registration row;
  - return workbook row pointers and evidence metadata.

LTRApplicationService / LTRRegistrationService
  - decide normal vs associated flow;
  - enforce readiness and operator confirmation rules;
  - acquire/release public-drive/application lock;
  - compute normal final number only after write access;
  - synchronize local record/evidence/lifecycle after workbook commit.
```

### 8.2 Required COM optimization rules

The old system was slow mainly because COM calls are expensive when used cell-by-cell or repeatedly. `TASK_045` must avoid these patterns.

Required rules:

1. Open the workbook **once** per registration transaction.
2. Do not open the workbook during normal readiness just to calculate a candidate normal number.
3. Use batch `Range(...).Value` reads for annual sheet data or at least for the DL column.
4. Use one `Range(...).Value` assignment to write the full registration row.
5. Avoid `Select()`, `Activate()`, and UI-driven Excel automation.
6. Set Excel automation options while the operation runs:

```python
excel.Visible = False
excel.DisplayAlerts = False
excel.ScreenUpdating = False
excel.EnableEvents = False
# xlCalculationManual = -4135
excel.Calculation = -4135
```

7. Always restore settings or close the dedicated Excel instance in `finally`.
8. Always check `workbook.ReadOnly` after opening. Passing a modify password does not guarantee write access if another user already holds the file.
9. Do not keep the public-drive workbook open between user actions.
10. Do not wait for operator confirmation while holding the workbook lock or an open writable workbook.

### 8.3 Recommended `OfficeFacade` shape

Use existing project naming if the codebase already has an `OfficeFacade`. Otherwise, implement the smallest adapter needed by `TASK_045`.

```python
class OfficeFacade:
    def open_excel_workbook(
        self,
        path: str,
        modify_password: str | None = None,
        read_only: bool = False,
    ) -> "ExcelWorkbookHandle":
        ...

class ExcelWorkbookHandle:
    @property
    def workbook(self): ...

    @property
    def excel_app(self): ...

    def save(self) -> None: ...

    def close(self, save_changes: bool = False) -> None: ...
```

Implementation notes:

- Prefer a dedicated hidden Excel instance for the operation.
- Do not attach to an operator's visible Excel session unless existing project policy requires it.
- Use `DispatchEx` if you need an isolated Excel instance.
- Use `Workbooks.Open` with the configured modify password. Depending on the wrapper signature, the parameter may need to be passed by keyword or positional COM argument. Validate this with an integration test on Windows.
- On every failure, close the workbook and quit the dedicated Excel instance.

### 8.4 Recommended `ExcelComLTRWorkbookGateway` shape

```python
class ExcelComLTRWorkbookGateway(LTRWorkbookGateway):
    def __init__(self, office: OfficeFacade, config: LTRWorkbookConfig):
        self._office = office
        self._config = config

    def open_write_session(self) -> LTRWorkbookWriteSession:
        handle = self._office.open_excel_workbook(
            path=self._config.path,
            modify_password=self._config.modify_password,
            read_only=False,
        )
        return ExcelComLTRWorkbookWriteSession(handle, self._config)
```

The write session should be context-manager friendly:

```python
with gateway.open_write_session() as session:
    session.assert_not_read_only()
    snapshot = session.read_annual_sheet(target_sheet)
    # calculate/write/save inside this context
```

### 8.5 Batch read/write examples

Avoid slow per-cell loops:

```python
# Avoid
for row in range(2, last_row + 1):
    dl = sheet.Cells(row, 4).Value
```

Prefer batch reads:

```python
# Example: read all visible business columns from row 2 to last row
values = sheet.Range(f"A2:Q{last_row}").Value
```

Avoid one COM call per column when writing:

```python
# Avoid
sheet.Cells(row, 1).Value = month
sheet.Cells(row, 2).Value = total
sheet.Cells(row, 3).Value = monthly_number
sheet.Cells(row, 4).Value = dl_number
```

Prefer one row assignment:

```python
row_values = [[
    month,
    total,
    monthly_number,
    dl_number,
    project_type,
    description_pn,
    test_item,
    test_type,
    requested_by,
    location,
    project_leader,
    test_result,
    failed_item,
    sample_deposition,
    subcontract,
    test_fee,
    remarks_po,
]]
sheet.Range(f"A{target_row}:Q{target_row}").Value = row_values
```

### 8.6 Performance acceptance criteria

`TASK_045` should not merely verify that Excel can be written. It should also prevent slow legacy patterns from returning.

Acceptance criteria:

- Scanning one annual sheet uses batch range reads, not per-cell `Cells(row, col)` loops over every row.
- Writing one registration row uses one row-range assignment.
- The workbook is opened at most once per registration transaction.
- The UI must not freeze while Excel is opening/writing. If the current architecture is PyQt, run the write use case through an existing worker/background mechanism or a command runner that does not block the main event loop.
- `Excel.exe` must not remain after success or failure unless the application intentionally manages a warm, hidden Excel instance.
- A normal workstation should usually complete open + scan target sheet + write one row + save within a practical operator workflow. Do not set a strict CI timing assertion, but log timings for open/read/calculate/write/save/close phases.

### 8.7 Optional later optimization: warm Excel instance

For Phase 7, prefer safety and correctness over aggressive caching. The default should be:

```text
open Excel -> open workbook -> register one LTR -> save -> close workbook -> quit/release Excel
```

A later optimization may pre-warm a hidden `Excel.Application` instance, but it must **not** keep the public-drive workbook open before the user starts an LTR registration transaction. Holding the workbook open early can block other users and defeats the public-drive collaboration model.

### 8.8 Future server replacement boundary

This COM gateway is for the local Windows desktop version only. Future server/online mode should replace it with a database-backed registry gateway:

```text
Local Phase 7:
  LTRWorkbookGateway -> ExcelComLTRWorkbookGateway -> OfficeFacade -> Excel COM

Future server mode:
  LTRRegistryGateway -> DatabaseLTRRegistryGateway -> DB transaction + unique constraint + audit log
```

Server mode should not use Office COM for online registration. Excel should become an export/sync artifact, not the primary concurrent registry.

---

## 9. TASK_045 Excel Write Execution Plan

TASK_045 should be the first task that can write the real workbook, and only when config enables it. For the local Windows `.xls` workbook, implement the write path through `ExcelComLTRWorkbookGateway` and `OfficeFacade`, not through direct `win32com` calls in services or UI code.

### 8.1 Configuration contract

Add or verify a config section like:

```toml
[ltr_workbook]
path = "\\\\server-or-nas\\shared\\LTR_number.xls"
mode = "excel_com"
write_enabled = false
lock_dir = "\\\\server-or-nas\\shared\\.connlab_locks"
lock_timeout_seconds = 120
backup_dir = "D:/ConnLabBackups/LTR"
modify_password = "<operator-local password>"
require_operator_confirmation_for_year_sheet_bootstrap = true
allow_system_assisted_create_year_sheet = true
template_sheet_name = ""
sheet_bootstrap_clear_start_row = 2
```

Rules:

- `path` is configurable.
- `write_enabled` defaults to false.
- `path` and `modify_password` both come from configuration.
- the config file containing the real password must be local/operator-managed and excluded from Git.
- provide a committed example config with placeholders only, for example `modify_password = ""`.
- do not log the password or expose it to UI state.

### 8.2 Normal workbook commit sequence

Authoritative sequence:

```text
Receive confirmed normal registration request
  -> validate local readiness
  -> acquire public-drive/application lock
  -> open workbook with modify/write credential through gateway
  -> assert workbook is not read-only
  -> resolve current system year sheet
  -> if current year sheet missing, follow new-year bootstrap flow
  -> re-read target sheet after write access is obtained
  -> scan DL column in current year target sheet for current YYYY-MM
  -> calculate final next number inside this write session
  -> write row to workbook
  -> save workbook
  -> close workbook and release Excel resources
  -> release lock
  -> sync local LtrRecord/evidence/lifecycle
  -> return final committed LTR number and workbook row pointer
```

Never compute or reserve the final normal number before write access.

### 8.3 Associated workbook commit sequence

Authoritative sequence:

```text
Receive confirmed associated registration request
  -> validate local readiness and association confirmation
  -> acquire public-drive/application lock
  -> open workbook with modify/write credential through gateway
  -> assert workbook is not read-only
  -> resolve current system year write sheet
  -> if current year sheet missing, follow new-year bootstrap flow
  -> re-read workbook after write access is obtained
  -> globally check exact duplicate associated number across annual sheets
  -> if duplicate exists: abort write and return collision rows
  -> optionally re-read base/family rows from base-year sheet for evidence/warnings
  -> write associated number row to current system year sheet
  -> save workbook
  -> close workbook and release Excel resources
  -> release lock
  -> sync local LtrRecord/evidence/lifecycle
  -> return committed result
```

Default policy:

```text
If exact duplicate exists at commit time -> block write.
If no exact duplicate exists -> write directly.
If family rows changed since preflight -> record warning/evidence, do not wait for second operator confirmation while holding lock.
```

### 8.4 New-year sheet bootstrap sequence

This is conditional. It runs only if the current system year sheet is missing.

Preflight stage:

```text
Detect current year sheet missing
  -> show operator proposed bootstrap plan
  -> operator authorizes or cancels
  -> store bootstrap intent if authorized
```

Commit stage:

```text
Acquire lock + write access
  -> re-check sheet list
  -> if current year sheet exists now: skip bootstrap
  -> if still missing and bootstrap intent authorized:
       copy configured template sheet or previous-year sheet
       rename copied sheet to current year
       clear concrete registration data from row 2 downward
       preserve header, column widths, formatting, formulas, validation, filters where possible
       re-read new sheet
  -> continue registration in same write transaction
```

Do not create the sheet silently without prior operator authorization.

---

## 10. Suggested DTO / Service Contract Patches

Use existing class/module names if they already exist. Do not duplicate abstractions.

### 10.1 Number parser / rules

Needed functions or equivalent methods:

```python
parse_ltr_number(value) -> ParsedLTRNumber
is_valid_new_ltr_number(value) -> bool
derive_base_number(value) -> str
extract_sequence(value) -> int
extract_family_stem(value) -> str
calculate_next_normal_number(existing_numbers, year, month) -> str
```

Expected behavior:

```text
DL-2026-04-003A -> sequence 3, family stem DL-2026-04-003
DL-2026-04-003  -> sequence 3, family stem DL-2026-04-003
ABC             -> invalid
123             -> invalid
```

### 10.2 Workbook gateway interface

Suggested interface shape:

```python
class LTRWorkbookGateway:
    def read_snapshot(self) -> LTRWorkbookSnapshot: ...
    def open_write_session(self) -> LTRWorkbookWriteSession: ...

class LTRWorkbookWriteSession:
    def assert_not_read_only(self) -> None: ...
    def list_sheets(self) -> list[str]: ...
    def copy_year_sheet(self, template_sheet: str, target_sheet: str, clear_start_row: int) -> None: ...
    def read_annual_sheet(self, sheet_name: str) -> AnnualSheetSnapshot: ...
    def find_family_rows(self, sheet_name: str, family_stem: str) -> list[LTRWorkbookRow]: ...
    def find_exact_duplicates(self, ltr_number: str, annual_sheets_only: bool = True) -> list[LTRWorkbookRow]: ...
    def append_registration_row(self, sheet_name: str, row_data: LTRWorkbookRowData) -> LTRWorkbookRowPointer: ...
    def save(self) -> None: ...
    def close(self) -> None: ...
```

Application services depend on this interface, not Excel COM directly.

Infrastructure implementation for Phase 7 should be named clearly, for example `ExcelComLTRWorkbookGateway`, and must depend on `OfficeFacade` rather than constructing `win32com` objects in the gateway constructor or application services.

### 10.3 Preflight result models

Normal:

```text
NormalLTRReadinessResult
- project_id
- target_write_year_sheet
- readiness
- number_preflight_required = false
- number_preview_allowed = false
- final_number_reserved = false
- warnings
- blockers
```

Associated:

```text
AssociatedLTRPreflightResult
- project_id
- requested_associated_number
- parsed_base_number
- base_year_sheet
- current_write_year_sheet
- base_found
- base_row_summary
- family_rows
- exact_duplicate_rows_from_snapshot
- operator_confirmation_required
- operator_confirmed
- missing_base_continue_reason
- warnings
- blockers
```

Commit:

```text
LTRWorkbookCommitResult
- success
- registration_type
- final_ltr_number
- target_sheet
- target_row
- workbook_fingerprint_before
- workbook_fingerprint_after
- duplicate_collision_rows
- warnings
- evidence_id
```

---

## 11. Test Plan For Patch And TASK_045

Add or patch tests before implementing risky write behavior.

### 11.1 Number parser tests

- parse `DL-2026-04-031` as normal.
- parse `DL-2025-11-002A` as associated.
- derive base `DL-2025-11-002` from `DL-2025-11-002A`.
- reject pure letters and pure numbers.
- reject non-DL format as new registration input.

### 11.2 Sequence allocation tests

Given existing:

```text
DL-2026-04-001
DL-2026-04-002
DL-2026-04-003A
DL-2026-04-004
DL-2026-04-005
```

Expected next normal:

```text
DL-2026-04-006
```

### 11.3 Normal readiness tests

- normal readiness/preflight does not produce advisory or candidate number.
- response has `number_preflight_required=false`.
- response has `number_preview_allowed=false`.
- response has `final_number_reserved=false`.
- UI/API response must not imply any number is available before commit.

### 11.4 Associated preflight tests

- `DL-2025-11-002A` uses base lookup sheet `2025`.
- write target sheet remains current system year, e.g. `2026`.
- family rows are returned for operator confirmation.
- missing base requires warning and continuation reason or block by policy.
- exact duplicate in snapshot is reported.

### 11.5 TASK_045 write transaction tests using fake gateway

- final normal number is calculated only after fake write session opens.
- normal readiness/preflight does not produce or expose a candidate number.
- if fake workbook changes between preflight and commit, commit uses latest write-session data.
- gateway read-only mode blocks write.
- duplicate associated number detected at commit blocks write.
- no duplicate associated number writes to current system year sheet.
- public-drive lock is released on success and failure.
- Excel session/gateway close is called on success and failure.

### 11.6 New-year bootstrap tests

- missing current year sheet triggers preflight authorization requirement.
- no operator authorization -> commit blocks sheet creation.
- if sheet is created by someone else before commit, bootstrap is skipped.
- if still missing and authorized, sheet is copied from template/previous year and concrete rows are cleared.
- registration continues in same write transaction after sheet creation.

### 11.7 OfficeFacade / Excel COM gateway tests

Use unit tests with a fake `OfficeFacade` first. Add Windows-only integration tests separately if the project already supports integration-test markers.

Unit/fake tests:

- `ExcelComLTRWorkbookGateway` calls `OfficeFacade.open_excel_workbook(...)` with configured path and modify password.
- write session checks `workbook.ReadOnly` and blocks when true.
- sheet scan uses a range-read adapter method rather than per-cell loops.
- row append uses a row-range write adapter method.
- `save()` is called only after successful validation and row append.
- `close()` is called on success and failure.
- public-drive/application lock is released on success and failure.

Optional Windows integration tests, guarded by config and skipped by default:

- can open a copied test `.xls` with modify password.
- detects read-only mode when workbook is unavailable for writing.
- can copy previous-year sheet to a new year sheet in a disposable workbook copy.
- can write one row and save without leaving Excel.exe behind.

### 11.8 Configuration tests

- workbook path comes from config.
- workbook modify password comes from config.
- committed example config contains only placeholder or empty password.
- real local config is excluded from Git.
- password value is not logged.
- `write_enabled=false` blocks real write path.

---

## 12. Implementation Guardrails

### 12.1 Do not do these

- Do not hard-code public-drive path.
- Do not hard-code workbook password.
- Do not store workbook password in source code or Git-tracked config.
- Do not calculate or display candidate normal LTR numbers before write access.
- Do not write associated numbers to the base-year sheet when current system year differs.
- Do not let UI directly call Excel COM.
- Do not let application/domain services directly call `win32com`.
- Do not implement annual-sheet scans with per-cell COM loops.
- Do not write row values one cell at a time when a row range assignment is possible.
- Do not hold workbook lock while waiting for operator confirmation.
- Do not silently create a new annual sheet.
- Do not treat read-only workbook access as write success.

### 12.2 Required architecture boundary

Expected dependency direction:

```text
UI / API route
  -> Application workflow service
  -> Domain rules / readiness rules
  -> LTR workbook gateway interface
  -> Infrastructure Excel adapter
```

Forbidden dependency direction:

```text
UI / API route
  -> Excel COM / workbook password / public drive path
```

---

## 13. Suggested Task Board Update

If the board currently says TASK_043 and TASK_044 are done, add a small patch task before TASK_045:

```markdown
### TASK_044A_LTR_REAL_WORKBOOK_RULE_PATCH

Status: pending

Goal:
Patch completed TASK_043/TASK_044 to reflect real LTR workbook rules before implementing Excel write.

Scope:
- normal LTR does not perform number preflight or candidate-number preview;
- associated preflight must parse base number, lookup base-year sheet, list family rows, and collect operator confirmation;
- local commit must not treat advisory number as authoritative workbook registration;
- config-file policy for workbook path and modify password must be documented and enforced before TASK_045.

Exit Criteria:
- parser/rule tests pass;
- preflight DTO tests pass;
- local commit traceability tests pass;
- no real workbook write occurs;
- docs/task_board.md points next to TASK_045.
```

Then activate:

```markdown
### TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC

Status: pending after TASK_044A

Goal:
Implement external workbook write through `OfficeFacade + ExcelComLTRWorkbookGateway` using transaction-safe final number allocation and batch COM operations.
```

---

## 14. Acceptance Checklist

The patch is complete only when all items below are true:

- [ ] `TASK_043` normal readiness does not calculate, preview, or reserve candidate numbers.
- [ ] `TASK_043` associated preflight supports base lookup, family-row listing, duplicate warning, and operator confirmation.
- [ ] `TASK_044` local commit records preflight/evidence and does not pretend local-only is external workbook sync.
- [ ] Normal final number allocation exists only in TASK_045 write session.
- [ ] Associated duplicate exact check is repeated in TASK_045 write session.
- [ ] Current system year sheet is the write target for both normal and associated registration.
- [ ] Associated base lookup uses the base number's year sheet.
- [ ] New-year sheet bootstrap is conditional and operator-authorized.
- [ ] Workbook path and lock path are configurable.
- [ ] Workbook modify password is loaded from local/operator-managed configuration, not hard-coded.
- [ ] UI/API does not directly open or write Excel.
- [ ] `TASK_045` uses `OfficeFacade + ExcelComLTRWorkbookGateway` for local `.xls` writing.
- [ ] Annual sheet reads and row writes avoid slow per-cell COM loops.
- [ ] Excel workbook open/save/close is guaranteed through cleanup/finally behavior.
- [ ] `Excel.exe` process cleanup is verified or explicitly managed.
- [ ] Tests cover the real workbook rules above.
- [ ] `docs/task_board.md` is updated with status and next task.

---

## 15. Recommended AI Prompt To Execute This Patch

Use this prompt with the AI coding agent:

```text
Read AGENTS.md first, then docs/task_board.md, then the active task file, then docs/archive/historical_plans/ConnLab_Phase7_Real_LTR_Folder_Lifecycle_Plan.md, then this patch guide.

TASK_043 and TASK_044 are already completed, but they were completed before the real LTR workbook rules were fully clarified. Do not rewrite them wholesale. Patch them minimally and safely.

Implement or adjust the code so that:
1. normal LTR readiness never calculates, previews, or reserves a candidate/final number;
2. associated LTR preflight parses the base number, checks the base-year sheet, lists same-family rows, and collects operator confirmation;
3. local-only commit is traceable and not confused with external workbook sync;
4. TASK_045 computes the final normal number only inside a write session after lock and modify access;
5. TASK_045 uses OfficeFacade + ExcelComLTRWorkbookGateway for the local `.xls` write path;
6. Excel COM calls are isolated in infrastructure and optimized with batch reads/writes;
7. workbook path and modify password are configuration-driven;
8. no UI code directly opens Excel or handles the password.

Add or update tests for parser rules, sequence rules, associated preflight, local commit traceability, configuration boundaries, OfficeFacade/Excel COM gateway behavior, and the upcoming TASK_045 fake-gateway transaction behavior.

Do not write the real LTR workbook in this patch unless docs/task_board.md explicitly activates TASK_045 and write_enabled is true.

After finishing, update docs/task_board.md with the patch result and set the next recommended task to TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC.
```
