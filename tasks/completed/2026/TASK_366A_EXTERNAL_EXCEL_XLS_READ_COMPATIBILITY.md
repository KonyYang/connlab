# TASK_366A External Excel XLS Read Compatibility

## Status

`complete / accepted`

Reviewer plan and implementation re-gates passed, the user approved implementation,
and Developer, QA, and Integrator completed the frozen TASK_366A package. The accepted
local commit records only the exact May Touch, lifecycle hardening, limits, focused
tests, and governance boundary below; remote push was not performed.

## Lane

`external-excel-xls-read-compatibility`

## Current Phase / Active Task / Role / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Active task: none. TASK_366A is complete/accepted; this closeout activates no new
  product lane.
- Role: Integrator controlled package closeout.
- Why allowed: Reviewer and QA gates passed after the explicitly approved implementation;
  this pass records the isolated local package only.
- Accepted baseline: TASK_365B commit
  `a58c96a371a541e97514f424b67d0341e5d01fa3` is an ancestor of the current HEAD.
  Existing worktree changes are external and remain untouched.

## Goal

Allow Settings to configure, validate, and read Standard record Excel and Equipment
calibration Excel resources in either `.xlsx` or legacy `.xls` format. Preserve the
current `.xlsx` ZIP/XML path exactly. Route `.xls` only through a ConnLab-owned hidden
Windows Excel COM read-only adapter with deterministic cleanup and actionable errors.

## Confirmed By User

- Standard record Excel and Equipment calibration Excel must accept `.xls` and `.xlsx`.
- Existing `.xlsx` behavior must not change.
- `.xls` must use Windows Excel/COM in read-only mode.
- Excel-unavailable, corrupt/unreadable, and header-mismatch failures must be clear.
- No write, conversion, Save, Save As, or mutation of an operator/public-drive file.
- LTR write, Fee export, Matrix, Project lifecycle, schema, and database are excluded.

## Confirmed By Repository Evidence

- `backend/desktop/path_picker_api.py` currently exposes `.xls` only for the LTR
  picker; all other Excel resources use an `.xlsx` filter.
- `ExternalResourceService._excel_failure()` currently rejects `.xls` for Standard
  record and Equipment calibration before structure probing.
- `ExternalExcelReadService` already supplies typed, read-only Standard record and
  Equipment calibration rows through `OfficeFacade.read_excel_tabular_rows()`.
- `ExcelWorkbookGateway` is an `.xlsx`-only ZIP/XML reader and already provides the
  accepted sheet/header selection and error semantics.
- `OfficeLifecycleManager` already owns hidden `DispatchEx`, COM initialization,
  `UpdateLinks=0`, `ReadOnly`, `AddToMru=False`, `SaveChanges=False`, `Quit`, and
  `CoUninitialize` behavior.
- Existing API responses and Settings resource DTOs are format-neutral; no frontend
  DTO or schema change is required.

## Frozen Design Contract

1. `OfficeFacade.probe_excel_structure()` and `read_excel_tabular_rows()` dispatch by
   suffix: `.xlsx` to the unchanged `ExcelWorkbookGateway`, `.xls` to one new bounded
   COM read-only tabular gateway, and all other suffixes to a typed unsupported error.
2. `read_excel_workbook()` and every LTR-specific read/write path remain unchanged.
3. The `.xls` adapter opens a dedicated hidden Excel instance with links/events/
   alerts disabled, opens with `ReadOnly=True`, and never calls Save or Save As.
4. Worksheet matching, header normalization, first non-empty header row, row mapping,
   blank filtering, and `__sheet_name` output must be behaviorally equivalent to the
   current `.xlsx` contract.
5. COM cells are read in bounded worksheet ranges. Values become deterministic text:
   blank remains blank, text is trimmed, date/datetime values use ISO text, and numeric
   values use invariant text without inventing business formatting.
6. All worksheet/range references are released before the workbook handle closes.
   Every success and failure path calls `Close(SaveChanges=False)`, `Quit`, and
   `CoUninitialize` exactly once for the owned instance.
7. Settings validation persists INVALID with a diagnostic reason; read APIs return
   the existing typed HTTP 400 boundary for unreadable/invalid workbooks.
8. Before any COM `UsedRange.Value` or `Value2` access, the `.xls` adapter must
   independently enforce all three V1 limits:
   - maximum rows: `65_536`;
   - maximum columns: `256`;
   - maximum total cells (`rows * columns`): `1_000_000`.
   Equality is allowed. A malformed, negative, non-integral, or over-limit count fails
   with a typed range diagnostic. These limits apply only to the new `.xls` adapter
   and do not change `.xlsx` behavior.

## Error Contract

- Unsupported extension: `Expected an Excel file (.xlsx or .xls): <path>`.
- Excel/pywin32 unavailable: diagnostic states that legacy `.xls` reading requires
  Microsoft Excel COM on Windows and suggests installing/repairing Excel/pywin32.
- Open/corrupt/protected failure: diagnostic states that the `.xls` workbook could
  not be opened read-only and includes a bounded Excel error summary.
- Sheet mismatch: `No worksheet matched the expected sheet rules.`
- Validation header mismatch: existing `Missing required headers: ...` and missing
  date-header diagnostics remain available.
- Row read header mismatch: `Expected headers were not found.`
- Cleanup failures must not turn into a write attempt; the primary read/open error is
  retained with cleanup context where safe.

## May Touch

Product candidates:

- `backend/infrastructure/office/excel_com_readonly_tabular_gateway.py` (new, bounded)
- `backend/infrastructure/office/office_facade.py` (suffix dispatch and injection only)
- `backend/infrastructure/office/__init__.py` (new gateway/error export only if needed)
- `backend/infrastructure/office/office_lifecycle.py` (narrow lifecycle hardening only:
  setup/open/Close/restore/Quit/CoUninitialize cleanup, exactly-once ownership, and
  primary-error precedence; no other Office behavior)
- `backend/application/external_resource_service.py` (accept/probe `.xls` for only the
  two named resource types)
- `backend/desktop/path_picker_api.py` (picker filter for only the two named resources)

Focused test candidates:

- `tests/unit/test_excel_com_readonly_tabular_gateway.py` (new, bounded)
- `tests/unit/test_office_lifecycle.py` (focused lifecycle-hardening additions only)
- `tests/unit/test_external_resource_service.py`
- `tests/unit/test_external_excel_read_service.py`
- `tests/integration/test_external_excel_read_api.py`
- `tests/unit/test_desktop_path_picker_api.py`

Governance:

- this task, its plan/evidence, and the exact TASK_366A board hunks

## Must Not Touch

- current `.xlsx` parser behavior or XLSX fixture semantics
- `backend/application/external_excel_read_service.py` and external Excel API DTOs/
  routes unless Reviewer proves a typed error translation is impossible without a
  separately reviewed narrow change
- Settings React layout/copy/API client
- LTR workbook adapters, transactions, registration, notes, or write authority
- Fee export/pricing, Matrix, Project lifecycle, folder actions, Report/Test Record
- schema, migrations, repositories, SQLite data, or configuration persistence shape
- any real operator/public-drive workbook or folder

## Locked Paths

- `backend/infrastructure/office/excel_workbook_gateway.py` production behavior
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
- `backend/infrastructure/office/ltr_workbook_*`
- Fee/workbook output gateways and `backend/modules/fee_evaluation/**`
- Matrix/Project lifecycle/storage/migrations
- `frontend/**`, except read-only regression execution
- `data/**`, `dist_release/**`, `.agents/**`, `docs/project_management/**`
- unrelated dirty residuals, staging, commits, and remote push

## Acceptance Criteria

1. The native picker offers `.xlsx;*.xls` for both named Settings resources.
2. Existing valid `.xlsx` validation and row reads remain byte-path compatible and
   pass all current tests unchanged.
3. A valid Standard record `.xls` validates and returns mapped rows and sheet names.
4. A valid Equipment calibration `.xls` validates and returns mapped rows, including
   a deterministic calibration date string.
5. Missing Excel/pywin32, corrupt/open failure, no matching sheet, and missing headers
   produce distinct actionable diagnostics with no unhandled 500.
6. Success, structure failure, row-read failure, and open failure release the owned COM
   lifecycle exactly once and never invoke Save/SaveAs or writable open.
7. An automation-settings failure after `DispatchEx` still attempts owned `Quit` and
   always calls `CoUninitialize` once. A `Quit` failure cannot skip uninitialization.
8. Open/read/header failures remain the primary public error even when cleanup also
   fails; cleanup context may be attached without replacing the primary diagnosis.
9. Handle cleanup is idempotent: repeated close attempts do not repeat Close, restore,
   Quit, or CoUninitialize for the same owned session.
10. `.xls` UsedRange accepts each exact limit and blocks rows `65_537`, columns `257`,
    and total cells `1_000_001+` before either `Value` or `Value2` is accessed.
11. Query filtering and API response DTOs remain unchanged across formats.
12. No LTR/Fee/Matrix/schema/database/frontend/real-file diff exists. The only shared
    lifecycle production change is the reviewed cleanup hardening above.

## Validation Gate Draft

```powershell
py -m pytest tests/unit/test_excel_com_readonly_tabular_gateway.py -q
py -m pytest tests/unit/test_external_resource_service.py tests/unit/test_external_excel_read_service.py tests/unit/test_desktop_path_picker_api.py -q
py -m pytest tests/integration/test_external_excel_read_api.py -q
py -m pytest tests/unit/test_excel_structure_probe.py tests/unit/test_office_lifecycle.py -q
py -m py_compile backend/infrastructure/office/excel_com_readonly_tabular_gateway.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/office_lifecycle.py backend/application/external_resource_service.py backend/desktop/path_picker_api.py
git diff --check
```

Also require UTF-8 trailing-whitespace, exact whitelist, no-write-token, no-real-path,
line-count, and empty-staging scans. A Windows host smoke may create a disposable `.xls`
under a temporary directory and read it through real Excel COM; it is optional when
Excel is unavailable and must never point at an operator/public-drive file.

## Merge Gate Draft

Planner Discovery/planned-only -> Reviewer plan gate -> explicit user approval for
Developer planning-first -> Developer docs-only planning-first -> Planner
reconciliation -> Reviewer implementation-readiness -> explicit user implementation
approval -> Developer -> Reviewer -> QA Windows/disposable smoke -> Integrator exact
package isolation. No gate may be inferred from this planned task.

## Definition Of Ready

Definition of Ready is satisfied: plan/readiness gates passed, the implementation
contract and exact file/test boundaries are frozen, and the user explicitly approved
product implementation. No blocker remains for the bounded Developer pass.

## Next Legal Role

User/Orchestrator route decision only. No new product lane is activated automatically.
