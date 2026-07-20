# TASK_366A External Excel XLS Read Compatibility Plan

## Status

`complete / accepted`

Reviewer plan and implementation re-gates passed, the user approved implementation,
and Developer, QA, and Integrator completed the exact frozen package. The accepted
local package remains limited to this plan's May Touch, lifecycle, range-limit, test,
and governance boundaries; remote push was not performed.

## 1. Discovery Decision

Create one serialized, bounded Settings/Office read-compatibility lane. No schema,
public DTO, frontend layout, LTR, or output-workbook lane is needed. The existing
resource registry already stores arbitrary paths and the existing row APIs are
format-neutral, so the implementation boundary is suffix dispatch plus a legacy `.xls`
read adapter.

## 2. Current State

### Confirmed by user

- Both named Settings resources accept `.xls` and `.xlsx`.
- `.xlsx` is unchanged; `.xls` uses read-only Excel COM.
- Errors must distinguish unavailable Excel, damaged files, and layout mismatch.
- No write, conversion, save-as, database, or unrelated workflow change is allowed.

### Confirmed by repository

- `path_picker_api._file_types()` limits non-LTR Excel files to `.xlsx`.
- `ExternalResourceService` rejects legacy `.xls` for Standard/Equipment resources.
- `ExternalExcelReadService` consumes only the format-neutral facade contract.
- `ExcelWorkbookGateway` is the accepted `.xlsx` ZIP/XML implementation.
- `OfficeLifecycleManager` provides an injectable owned Excel instance and cleanup.
- The existing routes translate read failures to HTTP 400 and missing registration to
  HTTP 404; response models do not expose workbook format.

### Planner inference

- A new gateway is safer than adding COM branches to the 435-line XLSX gateway.
- `OfficeFacade` is the narrow format router; this avoids changing application/API
  consumers and `backend/api/dependencies.py`.
- Existing lifecycle primitives can be reused without granting access to LTR writes.
- Cross-format behavior should be proven by contract tests, not by sharing mutable
  workbook internals between the ZIP/XML and COM implementations.

### Developer planning-first decisions

- Exact private class, error, injection, lifecycle, and test boundaries are frozen in
  sections 13-20 below.
- Real Excel availability remains environmental. Deterministic fake-COM tests are the
  mandatory implementation gate; a real-COM smoke remains conditional and temp-only.
- `pyproject.toml` intentionally remains unchanged. ConnLab's existing Office COM
  boundary treats pywin32 as an optional Windows runtime prerequisite and already
  raises `OfficeAutomationUnavailable` when absent. TASK_366A translates that absence
  into a `.xls`-specific typed read error; dependency/release packaging changes require
  a separate re-gate.

## 3. Architecture

```text
Settings path picker
  -> ExternalResourceService validation
  -> OfficeFacade suffix router
       .xlsx -> existing ExcelWorkbookGateway (unchanged)
       .xls  -> new ExcelComReadonlyTabularGateway

ExternalExcelReadService
  -> same OfficeFacade suffix router
  -> same ExcelTabularReadResult
  -> existing typed API response
```

The new gateway is infrastructure-only. Application services never import pywin32,
and API routes never touch COM.

## 4. XLSX Preservation Contract

- No production change to `excel_workbook_gateway.py`.
- No new fallback from `.xlsx` to COM, including damaged `.xlsx` files.
- Existing ZIP/XML errors, header normalization, sheet selection, row values, query
  behavior, and test fixtures remain unchanged.
- Existing `.xlsx` tests run as read-only regressions.

## 5. XLS COM Read Contract

### Open

1. Verify file existence and `.xls` suffix before COM initialization.
2. Call an injected `OfficeLifecycleManager.open_excel_workbook(..., read_only=True)`.
3. Require a dedicated hidden Excel instance with `UpdateLinks=0`, alerts/events/
   screen updating disabled, manual calculation where supported, `AddToMru=False`,
   and no password guessing.
4. Never call workbook `Save`, `SaveAs`, or any modifying method.

### Structure and rows

1. Enumerate worksheet names without changing active sheet state.
2. Match exact names and regex patterns with the same case-insensitive semantics as
   the XLSX path.
3. Read each matching worksheet's bounded UsedRange in one bulk operation using
   `Value`, falling back to `Value2` only for a read compatibility error.
4. Normalize the first non-empty row as the header row, map expected headers in their
   declared order, skip blank/header rows, and emit `__sheet_name`.
5. Convert values deterministically: `None -> ""`, strings trimmed, date/datetime to
   ISO, booleans to stable text, integral numerics without `.0`, other finite numerics
   invariantly. Non-finite or unrepresentable values fail with a row/sheet diagnostic.
6. Keep a conservative maximum UsedRange rows/columns or total cells. Oversized ranges
   fail clearly instead of exhausting memory. V1 freezes three independent checks,
   all before either `Value` or `Value2` is accessed:
   - `MAX_XLS_USED_RANGE_ROWS = 65_536`;
   - `MAX_XLS_USED_RANGE_COLUMNS = 256`;
   - `MAX_XLS_USED_RANGE_CELLS = 1_000_000`.
   Equality is accepted. Rows/columns must be non-negative integral counts. The product
   is checked without first materializing cell data. A fake COM range that exceeds any
   one limit must prove neither value property was touched. These caps apply only to
   `.xls`; the `.xlsx` gateway remains unchanged.

### Cleanup

- Hold the workbook handle in one `try/finally` boundary.
- Release range, worksheet, collection, and temporary COM references before close.
- Call `handle.close(save_changes=False)` once on every path after successful open.
- The handle owns `Workbook.Close(False)`, setting restoration, Excel `Quit`, and
  `CoUninitialize` exactly once.
- Open failure delegates cleanup to `OfficeLifecycleManager`; the gateway does not
  attempt a second close/quit/uninitialize.
- Cleanup failure is reported without attempting a save and must not hide an earlier
  corrupt/header/read diagnosis.

### Lifecycle hardening required by B1

`OfficeLifecycleManager` is now a narrow Future May Touch dependency because a gateway
cannot clean a failure that occurs before a handle is returned. The only authorized
future lifecycle behavior is:

1. Once `CoInitialize` succeeds, exactly one later path owns `CoUninitialize`.
2. Dispatch failure always uninitializes COM once.
3. Automation-settings failure after `DispatchEx` attempts owned Excel `Quit` and
   still uninitializes once even when `Quit` fails.
4. Workbook-open failure attempts workbook close when a workbook exists, settings
   restoration when state was captured, Excel `Quit`, and COM uninitialization. Every
   later cleanup step is attempted with nested `finally` semantics.
5. A returned handle's first `close(False)` attempts Workbook Close, settings restore,
   Quit, and CoUninitialize once. The handle records closed ownership before cleanup so
   a repeated close is a no-op and cannot double-release COM.
6. If setup/open/read/header processing has a primary exception and cleanup also
   fails, the primary exception remains the public error; bounded cleanup context is
   chained or attached. If cleanup is the only failure, the first deterministic
   cleanup failure is raised only after all remaining cleanup steps were attempted.
7. This hardening must preserve existing open parameters and must not alter LTR write,
   password, save, workbook transaction, Word, Outlook, or other Office semantics.

## 6. Error Mapping

| Condition | Validation behavior | Read API behavior |
|---|---|---|
| unsupported suffix | INVALID with expected `.xlsx or .xls` | HTTP 400 typed detail |
| Excel/pywin32 unavailable | INVALID with install/repair diagnostic | HTTP 400 typed detail |
| corrupt/protected/open failure | INVALID with read-only open diagnostic | HTTP 400 typed detail |
| no matching worksheet | INVALID with existing sheet-rule message | HTTP 400 same message |
| missing required/date header | INVALID with named missing headers | HTTP 400 expected-header message |
| oversized/invalid cell data | INVALID with sheet/range diagnostic | HTTP 400 typed detail |

Do not expose raw COM tracebacks. Preserve a bounded exception summary and chain the
original exception for logs/tests.

## 7. File-Level Sequence

1. Add `tests/unit/test_excel_com_readonly_tabular_gateway.py` with fake workbook,
   worksheet, range, handle, lifecycle, and release counters. Begin with success,
   unavailable/open/read/header failures, oversize, and cleanup/no-write tests.
2. Add focused failing lifecycle tests in `tests/unit/test_office_lifecycle.py`, then
   harden only `backend/infrastructure/office/office_lifecycle.py` for the B1 contract.
3. Add `backend/infrastructure/office/excel_com_readonly_tabular_gateway.py`, target
   under 300 lines and hard limit under 500.
4. Update `office_facade.py` only to inject the legacy gateway and dispatch probe/read
   calls by suffix. Keep `read_excel_workbook()` untouched.
5. Update `ExternalResourceService` to accept `.xls` only for Standard record and
   Equipment calibration and probe it through the facade.
6. Update the native Settings picker filters for only those two resource types.
7. Add service/API/picker contract tests and rerun the unchanged XLSX suites.
8. Run optional real Excel smoke against a generated temporary `.xls`, record file
   hash/metadata before and after read, and delete only the controlled temp artifact.

## 8. Test Matrix

Mandatory deterministic tests:

- Standard `.xls` structure and tabular rows.
- Equipment `.xls` structure, rows, and date text.
- sheet regex and header normalization parity with `.xlsx`.
- missing Excel/pywin32, DispatchEx failure, corrupt/open failure.
- no matching sheet, required/date header missing, malformed/oversized range.
- exact row boundary `65_536` accepted and `65_537` blocked before `Value/Value2`.
- exact column boundary `256` accepted and `257` blocked before `Value/Value2`.
- exact cell boundary `1_000_000` accepted (for example `4_000 x 250`) and an
  independently over-limit product blocked (for example `4_001 x 250`).
- automation-settings failure after DispatchEx: Quit attempted and CoUninitialize once.
- Quit failure: CoUninitialize still once; no double cleanup.
- open/read/header primary error plus cleanup error: primary error preserved with
  cleanup context, all cleanup attempts exactly once.
- repeated handle close: Close/restore/Quit/CoUninitialize are not repeated.
- query filtering and existing response DTOs.
- picker filters for Standard/Equipment include both extensions while other resource
  filters remain unchanged.
- lifecycle counts on success and every post-open failure; no `Save`/`SaveAs` call.
- `.xlsx` exact regression, including proof that a damaged `.xlsx` does not invoke COM.

Conditional Windows smoke:

- create a disposable `.xls` in pytest/temp space using a dedicated Excel instance;
- close creation session, read through the product facade, verify rows and unchanged
  hash/size/mtime across the read session;
- skip with an explicit environment reason when Excel is unavailable;
- never copy/open an operator workbook.

## 9. May Touch / Locks

The exact May Touch and Locked Paths are frozen in the task file. In particular:

- no `backend/api/dependencies.py`, route DTO, frontend API client, or Settings React
  change is planned;
- no XLSX gateway production change is planned;
- no LTR COM gateway/transaction/write path is eligible;
- no database/schema/config-storage change is eligible.
- `office_lifecycle.py` is eligible only for the B1 cleanup/ownership/error-precedence
  hardening above; every unrelated Office behavior remains locked.

If Developer planning-first finds one of those changes necessary, stop and return to
Planner/Reviewer before implementation authorization.

## 10. Parallelism and Package Isolation

- This lane is serialized with any task touching `office_facade.py`,
  `external_resource_service.py`, or `path_picker_api.py`.
- It may be reviewed in parallel with unrelated product lanes, but implementation must
  use hunk/file isolation in the dirty worktree.
- Recommended future branch: `codex/task-366a-external-excel-xls-read-compatibility`.
- Only the exact product/tests/governance whitelist may be staged by Integrator.

## 11. Validation and Merge Gates

Validation commands and acceptance cases are listed in the task file. Reviewer must
also inspect no-write tokens, COM ownership, line counts, XLSX non-dispatch, external
dirty residual exclusion, and empty staging.

Merge requires Developer evidence, independent Reviewer pass, QA deterministic suite,
conditional Windows COM smoke evidence or a documented environment skip, explicit
user acceptance, and Integrator exact package isolation. No remote push is implied.

## 12. Definition Of Ready

Definition of Ready is satisfied. Developer planning-first and Reviewer
implementation-readiness are complete, and the user explicitly approved product
implementation. The exact interfaces, file sequence, lifecycle ownership, range
validation, error translation, dependency strategy, tests, rollback, and package
isolation are authorized without expansion.

## 13. Exact Future Interfaces

Create `backend/infrastructure/office/excel_com_readonly_tabular_gateway.py` with these
private/public-to-infrastructure symbols:

```python
MAX_XLS_USED_RANGE_ROWS = 65_536
MAX_XLS_USED_RANGE_COLUMNS = 256
MAX_XLS_USED_RANGE_CELLS = 1_000_000

class ExternalExcelTabularGatewayError(ValueError): ...
class UnsupportedExternalExcelTabularFormatError(ExternalExcelTabularGatewayError): ...
class LegacyExcelComUnavailableError(ExternalExcelTabularGatewayError): ...
class LegacyExcelReadOnlyOpenError(ExternalExcelTabularGatewayError): ...
class LegacyExcelRangeError(ExternalExcelTabularGatewayError): ...
class LegacyExcelReadError(ExternalExcelTabularGatewayError): ...
class LegacyExcelCleanupError(ExternalExcelTabularGatewayError): ...

class ExcelReadonlyLifecyclePort(Protocol):
    def open_excel_workbook(
        self, path: Path, modify_password: str | None = None,
        read_only: bool = False,
    ) -> ExcelWorkbookHandle: ...

class ExcelComReadonlyTabularGateway:
    def __init__(self, lifecycle: ExcelReadonlyLifecyclePort) -> None: ...
    def probe_structure(...) -> ExcelStructureProbeResult: ...
    def read_tabular_rows(...) -> ExcelTabularReadResult: ...
```

Every gateway error inherits `ValueError`. This is required because the existing
external Excel routes already map `ValueError` to HTTP 400 and must remain unchanged.
`LegacyExcelComUnavailableError` wraps `OfficeAutomationUnavailable`; other open COM
failures become `LegacyExcelReadOnlyOpenError`. Range and bulk-cell failures remain
distinct. Exception summaries collapse whitespace, cap output at 240 characters, and
chain the original exception without exposing a traceback in API detail.

`OfficeFacade.__init__()` gains only:

```python
legacy_excel_gateway: ExcelComReadonlyTabularGateway | None = None
```

It resolves `_lifecycle` first, then constructs the default legacy gateway with that
same lifecycle. A private `_tabular_gateway(Path)` returns the existing gateway for
`.xlsx`, the COM gateway for `.xls`, and raises
`UnsupportedExternalExcelTabularFormatError` with
`Expected an Excel file (.xlsx or .xls): <path>` otherwise. Only
`probe_excel_structure()` and `read_excel_tabular_rows()` call this router.
`read_excel_workbook()` and `open_excel_workbook()` are unchanged.

No `backend/infrastructure/office/__init__.py` export is needed: the facade and focused
tests import the gateway module directly. No models, API DTO, dependency provider, or
application read-service signature changes are permitted.

## 14. COM Read Algorithm

The new gateway must perform one operation per owned workbook session:

1. Check `Path.is_file()` and exact case-insensitive `.xls` suffix before opening COM.
2. Call `open_excel_workbook(path, read_only=True, modify_password=None)`.
3. Access `Workbook.Worksheets` by one-based `Count`/`Item(index)`; do not select or
   activate sheets and do not depend on COM enumeration state.
4. Match exact sheet names case-insensitively and regex patterns with
   `re.fullmatch(..., IGNORECASE)`, matching current XLSX behavior.
5. For each matched sheet, capture `UsedRange`, then read `Rows.Count` and
   `Columns.Count`. Counts must be non-boolean integers and non-negative.
6. Independently reject rows above 65,536, columns above 256, or product above
   1,000,000 before either `.Value` or `.Value2` is accessed. A zero dimension yields
   an empty matrix without touching either value property.
7. Read `.Value` once. Fall back to `.Value2` only when `.Value` raises a COM read
   exception; malformed returned shape does not trigger a second read.
8. Canonicalize scalar/one-row/one-column/two-dimensional COM results to an exact
   `tuple[tuple[object, ...], ...]`; dimension mismatch is a typed read error.
9. Release bulk value, range, worksheet, and worksheet-collection references before
   calling `handle.close(save_changes=False)`.

Cell text conversion is exact:

- `None -> ""`; strings are trimmed;
- `datetime -> value.isoformat(timespec="seconds")` and `date -> value.isoformat()`;
- booleans become `TRUE` or `FALSE`;
- integers use decimal text; finite float/Decimal values use invariant non-scientific
  decimal text with redundant fractional zeroes removed;
- NaN, infinity, or unsupported COM value objects raise `LegacyExcelReadError` with
  sheet and one-based row/column context.

Header and row handling intentionally duplicates the locked XLSX contract rather than
refactoring the 435-line XLSX gateway: first non-empty row, whitespace/case header
normalization, union-of-observed-headers probe semantics, per-sheet canonical header
index mapping, blank/header-row skipping, declared header order, and `__sheet_name`.
Probe returns the existing invalid result/messages; tabular read raises exactly
`No worksheet matched the expected sheet rules.` or
`Expected headers were not found.`.

## 15. Lifecycle Ownership And Error Precedence

`backend/infrastructure/office/office_lifecycle.py` receives only the following
hardening:

- add `OfficeAutomationCleanupError(RuntimeError)` and an internal cleanup collector;
- add an internal non-init `_closed` flag to `ExcelWorkbookHandle`;
- `close(False)` marks ownership closed before cleanup, then attempts Workbook Close,
  settings restoration, Excel Quit, and CoUninitialize in that order; all later steps
  run even after an earlier failure; a repeated close is a no-op, including after the
  first close raised;
- preserve `save()` and every existing open parameter/password behavior;
- capture previous Excel settings before applying them, so a Visible/DisplayAlerts/
  ScreenUpdating/EnableEvents assignment failure can still attempt restoration;
- after successful `CoInitialize`, DispatchEx, settings, and Workbooks.Open failures
  all use one cleanup owner. Workbook Close is attempted only if a workbook exists,
  Quit only if Excel exists, and CoUninitialize exactly once;
- primary setup/open exceptions are re-raised with a bounded cleanup note after every
  cleanup attempt. Cleanup-only handle failure raises the first
  `OfficeAutomationCleanupError` after all cleanup attempts.

The existing tolerated Calculation assignment remains tolerated and is not converted
to setup failure. `_restore_excel_settings()` may continue its best-effort per-setting
behavior. The new gateway preserves a read/open/header/range primary exception when
`close(False)` also fails by attaching a bounded `Cleanup warning:` note. If reading
succeeded and close alone fails, it raises `LegacyExcelCleanupError`. No gateway path
calls `save()`, `Workbook.Save`, or `SaveAs`.

Because this handle also serves accepted LTR sessions, focused regressions must prove
the existing `UpdateLinks=0`, password/write-reservation, read-only, AddToMru, and
SaveChanges parameters are unchanged. No LTR gateway/session source is editable.

## 16. Application And Picker Changes

`ExternalResourceService._excel_failure()` changes only the Standard record and
Equipment calibration branch from `.xlsx` to `{.xlsx, .xls}`. Both suffixes call the
same `_probe_excel_resource()`; LTR's existing `.xls` size-only compatibility branch
is unchanged. Unsupported Standard/Equipment suffixes use the task's exact
`.xlsx or .xls` message. Existing exception capture persists INVALID with
`Excel file is not readable: <typed reason>`.

`backend/desktop/path_picker_api.py::_file_types()` explicitly treats
`standard_record_excel`, `equipment_calibration_excel`, and `ltr_workbook` as
`Excel workbooks (*.xlsx;*.xls)`. Application form and default filters remain
unchanged. The separate tkinter `WindowsPathPicker` is read-only in this lane: the
actual Settings page calls the PyWebView desktop bridge and has no API picker fallback.
Changing the unused API-picker route requires a separate scope decision.

## 17. Exact TDD Sequence

1. Add lifecycle red tests for settings failure after DispatchEx, Dispatch failure,
   open failure, Quit failure, Close failure, primary-plus-cleanup precedence, and
   repeated close. Implement only the lifecycle hardening in section 15.
2. Add the bounded fake-COM gateway module tests. Start with Standard and Equipment
   success, sheet regex/header parity, deterministic date/number text, Value2 fallback,
   and proof that open is `read_only=True` with no save calls. Implement the gateway.
3. Add parameterized dimension tests. Exact 65,536x1, 1x256, and 4,000x250 fake ranges
   must reach the value accessor without allocating the declared matrix; 65,537x1,
   1x257, 4,001x250, bool, float, and negative counts must fail with both access
   counters at zero.
4. Add open/unavailable/read/header/cleanup tests, including primary error preservation
   and exact once-only Close/Quit/CoUninitialize counters.
5. Add OfficeFacade injection/suffix tests in the new gateway test module: `.xlsx`
   invokes only the accepted gateway, `.xls` invokes only COM, damaged `.xlsx` never
   falls back, and other suffixes raise the exact typed format error.
6. Replace the two legacy-rejection expectations in
   `test_external_resource_service.py` with parameterized Standard/Equipment `.xls`
   probe success/error assertions while retaining real `.xlsx` regressions.
7. Add fake-facade `.xls` Standard/Equipment row mapping and query tests to
   `test_external_excel_read_service.py`; add HTTP 200 and each typed HTTP 400 category
   to `test_external_excel_read_api.py` through dependency/service injection only.
8. Add picker-filter assertions for both named resources and unchanged unrelated
   filters to `test_desktop_path_picker_api.py`.
9. Run XLSX structure/row regressions and read-only LTR lifecycle regressions before
   package review.

No implementation test may require local Excel. Fake lifecycle/COM is mandatory.

## 18. Exact Future May Touch

Product:

- create `backend/infrastructure/office/excel_com_readonly_tabular_gateway.py`;
- modify `backend/infrastructure/office/office_facade.py` only for injection/router;
- modify `backend/infrastructure/office/office_lifecycle.py` only for section 15;
- modify `backend/application/external_resource_service.py` only for the two resource
  suffix/probe branch;
- modify `backend/desktop/path_picker_api.py` only for the two picker types.

Tests:

- create `tests/unit/test_excel_com_readonly_tabular_gateway.py`;
- focused additions to `tests/unit/test_office_lifecycle.py`;
- focused changes to `tests/unit/test_external_resource_service.py`;
- focused additions to `tests/unit/test_external_excel_read_service.py`;
- focused additions to `tests/integration/test_external_excel_read_api.py`;
- focused additions to `tests/unit/test_desktop_path_picker_api.py`.

Governance is limited to TASK_366A task/plan/evidence/board at later authorized gates.
`office/__init__.py`, `models.py`, `excel_workbook_gateway.py`,
`external_excel_read_service.py`, routes, dependencies, WindowsPathPicker,
`pyproject.toml`, frontend, LTR gateways, and every other task path are explicitly
read-only. Any discovered need to edit them stops implementation for re-gate.

## 19. Line Count And Validation Gates

Current physical UTF-8 lines: facade 223, lifecycle 127, resource service 211, desktop
picker 107, locked XLSX gateway 435; lifecycle test 127, resource test 318, read-service
test 167, API test 168, picker test 83, XLSX probe test 132.

Future limits:

- new gateway target <=300 and hard limit <500;
- new gateway test hard limit <500;
- every touched Python file remains <500, with resource-service tests targeted <450;
- use `Path.read_text(encoding="utf-8").splitlines()` so blank lines are counted.

Mandatory commands:

```powershell
py -m pytest tests/unit/test_excel_com_readonly_tabular_gateway.py -q
py -m pytest tests/unit/test_office_lifecycle.py -q
py -m pytest tests/unit/test_external_resource_service.py tests/unit/test_external_excel_read_service.py tests/unit/test_desktop_path_picker_api.py -q
py -m pytest tests/integration/test_external_excel_read_api.py -q
py -m pytest tests/unit/test_excel_structure_probe.py tests/unit/test_office_integration_boundary.py tests/unit/test_ltr_workbook_compatibility_service.py -q
py -m py_compile backend/infrastructure/office/excel_com_readonly_tabular_gateway.py backend/infrastructure/office/office_facade.py backend/infrastructure/office/office_lifecycle.py backend/application/external_resource_service.py backend/desktop/path_picker_api.py
git diff --check
```

Static gates inspect only candidate additions for `.Save(` or `.SaveAs(`, writable
open, output/copy/delete calls, public-drive literals, direct pywin32 imports outside
infrastructure, forbidden paths, UTF-8 trailing whitespace, physical line counts,
exact whitelist, empty TASK_366A staging, and no `data/**`/`dist_release/**` mutation.
Existing `ExcelWorkbookHandle.save()` is not removed or counted as a new write path.

## 20. Windows Smoke, Rollback, And Package Isolation

Fake-COM tests are release-blocking. A Windows/Excel smoke is optional and occurs only
after deterministic tests pass. It may create one `.xls` under pytest/temp space with
a dedicated Excel instance and `FileFormat=56`, close the creator, record SHA-256,
size, and mtime, read through the product facade, assert rows and unchanged metadata,
then delete only that controlled temp artifact. Missing Excel/pywin32 produces an
explicit skip reason. No operator/public-drive path may be copied or opened.

Rollback is file/hunk-local: removing the facade `.xls` branch leaves `.xlsx` exactly
as before; removing the picker/resource suffix hunks returns validation/UI selection
to `.xlsx`; the new gateway then has no caller. Lifecycle hardening is packaged only
if its own tests and LTR read-only regressions pass and is independently revertible.
Never package a partial router without lifecycle tests.

The current target product/test paths are clean at planning-first time; the plan file
is untracked and the shared worktree contains unrelated residuals. Integrator must use
the exact section-18 whitelist and hunk-stage shared files. No whole-worktree staging,
commit, push, or residual cleanup is part of TASK_366A.

## 21. Next Legal Role

User/Orchestrator route decision only. No scope expansion or new product lane is
authorized by this closeout.
