# TASK_366A Developer Evidence

Date: 2026-07-20

Role: Developer

Status: `ready_for_reviewer_implementation_re_gate`

TASK_ID: `TASK_366A_EXTERNAL_EXCEL_XLS_READ_COMPATIBILITY`

Lane: `external-excel-xls-read-compatibility`

## Phase And Authorization

Current phase is Phase 11. Reviewer implementation-readiness passed, the user approved
product implementation, and Planner reconciliation authorized this bounded Developer
pass. Implementation remained inside TASK_366A exact May Touch.

## Real Code Facts Reconciled

- Settings currently calls the PyWebView `DesktopPathPickerApi`; its Standard and
  Equipment filters are `.xlsx`-only. The separate tkinter/API picker is not used by
  the current Settings browse handler and remains read-only in this lane.
- `ExternalResourceService` rejects `.xls` before probing for the two named resources.
  The format-neutral `ExternalExcelReadService` already calls
  `OfficeFacade.read_excel_tabular_rows()` and needs no change.
- Existing routes map `ValueError` to HTTP 400. New COM gateway errors therefore must
  inherit `ValueError`; allowing raw `OfficeAutomationUnavailable(RuntimeError)` to
  escape would produce an unhandled 500.
- `OfficeFacade` currently owns one XLSX gateway and one lifecycle manager. It is the
  correct suffix router and can construct the legacy gateway with that same lifecycle;
  dependencies/providers do not need modification.
- `ExcelWorkbookGateway` is 435 lines and contains accepted `.xlsx` sheet/header/row
  behavior. It remains locked; parity is implemented and tested in the new gateway,
  not by refactoring shared helpers out of the XLSX module.
- `OfficeLifecycleManager` currently applies automation settings outside its open
  cleanup boundary, and `ExcelWorkbookHandle.close()` can skip CoUninitialize when
  Quit raises. Narrow exactly-once/nested-cleanup hardening is required and sufficient.
- `pyproject.toml` does not declare pywin32. Existing ConnLab COM boundaries use
  runtime imports and actionable unavailable errors. TASK_366A preserves that strategy;
  dependency/release changes require a separate gate.

## Frozen Implementation Boundary

- New `ExcelComReadonlyTabularGateway` handles only `.xls` probe/tabular read through
  an injected lifecycle port; it imports no pywin32 directly.
- `OfficeFacade` dispatches only probe/tabular methods: `.xlsx` unchanged, `.xls` COM,
  other suffix typed unsupported. `read_excel_workbook()` and LTR paths are unchanged.
- All new infrastructure errors are `ValueError` subclasses with bounded messages, so
  Settings validation persists INVALID and existing APIs return HTTP 400.
- UsedRange independently validates integral non-negative rows, columns, and product
  against inclusive 65,536 / 256 / 1,000,000 limits before Value/Value2 access.
- Gateway cleanup releases local COM references before idempotent `close(False)`.
  Lifecycle cleanup always attempts Close/restore/Quit/CoUninitialize exactly once and
  retains the primary setup/open/read/header error when cleanup also fails.
- Cell, sheet, header, mapping, query, and response semantics are frozen in the plan.
  No save, conversion, fallback from damaged `.xlsx`, or operator-file access exists.

## Exact May Touch

Future implementation is limited to the new gateway, narrow facade/lifecycle/resource/
desktop-picker hunks, six focused test modules, and TASK_366A governance listed in
sections 18-19 of the plan. `office/__init__.py`, models, XLSX gateway, application
read service, routes, dependencies, WindowsPathPicker, pyproject, frontend, LTR,
schema/database, outputs, and unrelated residuals are read-only.

## Validation And Package Plan

- TDD starts with lifecycle and fake-COM failures before product changes.
- Mandatory tests cover Standard/Equipment success, parity, errors, no-write,
  Value2 fallback, exact/over-limit ranges, primary-error precedence, and idempotent
  cleanup. XLSX and read-only LTR lifecycle regressions remain required.
- New/touched Python files stay below 500 physical UTF-8 lines; the gateway targets
  300 lines and its test remains a bounded module below 500.
- Static checks cover py_compile, diff/trailing whitespace, exact whitelist, added
  write tokens, real/public paths, line counts, locked scope, and staging isolation.
- Optional real Excel smoke may use only a newly created temp `.xls`, with hash/size/
  mtime unchanged across product read; missing Excel/pywin32 is an explicit skip.

## Planning-First Validation

- Read AGENTS, task board, TASK_366A task/plan/Planner/Reviewer evidence, picker,
  validation/read services, routes/provider, facade, XLSX gateway/models, lifecycle,
  LTR consumers, pyproject, and focused tests.
- Current HEAD: `f82a942687a85d1ee1a02c490d630f19bb548d95`.
- Target product/test paths were clean; only the pre-existing untracked TASK_366A plan
  was present. Staging was empty.
- This pass changed only the TASK_366A plan and this Developer evidence. It did not run
  product tests, access an operator/public-drive workbook, or modify product/test/
  schema/database/frontend/API/dependency files.

## Implementation Result

- Added `ExcelComReadonlyTabularGateway` for `.xls` probe and tabular reads through an
  injected `OfficeLifecycleManager`. It opens one hidden Excel instance read-only,
  never calls Save/SaveAs, validates UsedRange before Value/Value2, and returns the
  existing `ExcelStructureProbeResult` / `ExcelTabularReadResult` contracts.
- Kept `.xlsx` on the accepted ZIP/XML gateway. `OfficeFacade` now performs exact
  `.xlsx` / `.xls` dispatch only for probe/tabular methods; generic workbook/LTR paths
  are unchanged and damaged `.xlsx` cannot fall back to COM.
- Added typed `ValueError` subclasses for COM unavailable, read-only open, range,
  read, cleanup, and unsupported-format failures. Existing API routes therefore retain
  their HTTP 400 contract without DTO, route, dependency, or client changes.
- Hardened Excel COM lifecycle ownership: settings are captured before mutation;
  Dispatch/settings/open failures unwind owned resources; handle close always attempts
  Close(False), restore, Quit, and CoUninitialize; close is idempotent even after a
  cleanup failure; a primary operation error retains precedence over cleanup errors.
- Enabled Standard record and Equipment calibration `.xls` validation/probing and
  desktop picker filters. The existing LTR `.xls` compatibility branch is unchanged.

## TDD Evidence

- Lifecycle RED: `test_office_lifecycle.py` initially failed collection because
  `OfficeAutomationCleanupError` did not exist. GREEN: 6 passed, including settings,
  Dispatch, open, Close, Quit, primary-error, and repeated-close ownership paths.
- Gateway RED: `test_excel_com_readonly_tabular_gateway.py` initially failed because
  the gateway module did not exist. GREEN: 19 passed with fake COM only.
- Application RED: Standard/Equipment `.xls` validation and picker tests failed under
  the previous `.xlsx`-only branches. GREEN after the two narrow product changes.
- Fake-COM coverage includes read-only open arguments, Close(False), Value2 fallback,
  deterministic values, exact sheet/header diagnostics, COM unavailable/damaged open,
  cleanup precedence, and UsedRange boundaries. Inclusive 65,536 rows, 256 columns,
  and 1,000,000 cells reach Value; each over-limit/invalid count is blocked before
  both Value and Value2.

## Final Validation

- Full focused command across nine modules after the B4 fix:
  `74 passed in 11.50s`.
- Earlier grouped runs: gateway/lifecycle `24 passed`; resource/read/API/picker
  `32 passed`; accepted XLSX/Office/LTR regressions `15 passed`.
- `py -m py_compile` passed for all five touched/new product modules.
- Tracked candidate `git diff --check` passed; untracked gateway/test/plan/evidence
  no-index checks had no whitespace error. Git emitted only existing LF/CRLF notices.
- UTF-8 trailing-whitespace scan passed.
- Physical UTF-8 lines, including blanks: gateway 366; facade 241; lifecycle 182;
  resource service 211; picker 111; gateway test 427; lifecycle test 285; resource
  test 321; read-service test 208; API test 245; picker test 101. All are below 500.
- Forbidden write/path token scan passed: no gateway Save/SaveAs, copy/delete,
  public-drive, real database, or data-path operation.
- Candidate status contains only the five authorized product files, six authorized
  test files, and TASK_366A plan/evidence. Staging is empty.
- Locked backend/API/models/XLSX/WindowsPathPicker/pyproject paths have no candidate
  diff. The status scan showed unrelated pre-existing frontend diffs and untracked
  `dist_release` artifacts; this lane did not modify, stage, clean, or attribute them.
- Optional real-COM smoke was not run: fake COM is the mandatory deterministic gate,
  and avoiding local Excel automation also guarantees no operator/public-drive file
  access. No real workbook, real database, or release artifact was opened or changed.

## Blockers

None.

## Next Legal Role

Reviewer implementation re-gate only. Do not route QA or Integrator yet.

## B4 Bounded Fix Pass

Reviewer found that the initial `UsedRange.Value` handler caught every `Exception`
and always attempted `Value2`. The bounded fix adds a runtime-safe private classifier
that recognizes only the pywin32 `pywintypes.com_error` type by its runtime module and
class name; the gateway still has no direct or optional import of pywin32.

- A recognized COM read-compatibility error may use the existing Value2 fallback.
- Any other Value exception is immediately wrapped as `LegacyExcelReadError`; Value2
  is not accessed.
- If that primary read failure coincides with close/cleanup failure, the read error
  remains primary and receives the existing bounded cleanup note.
- RED proof: the two new arbitrary-error tests failed because Value2 hid the primary
  error and cleanup became public. GREEN proof: focused gateway module `21 passed`.
- Final nine-module rerun after the fix: `74 passed in 11.50s`; all py_compile,
  diff/trailing, physical-line, locked-scope, no-real-path, no-direct-pywin32, and
  staging-empty checks passed.

Status is `ready_for_reviewer_implementation_re_gate`; next role is Reviewer
implementation re-gate only.
