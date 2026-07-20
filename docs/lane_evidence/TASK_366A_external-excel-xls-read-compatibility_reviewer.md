# TASK_366A Reviewer Plan Gate

Date: 2026-07-20

Status: `reviewer_blocked / implementation B4 required`

## Scope Reviewed

- `AGENTS.md`, task board, TASK_366A task, plan, and Planner evidence.
- Current Settings picker, external-resource validation, external Excel row-read/API
  chain, `OfficeFacade`, XLSX gateway, and Office lifecycle implementation.
- Existing external-resource, tabular-read/API, picker, XLSX-structure, and Office
  lifecycle tests.

The board correctly marks TASK_366A as planned-only. No product or test code was
modified, no operator/public-drive workbook was opened, and the pre-existing dirty
worktree remains excluded.

## Findings

### B1: Existing COM lifecycle cannot meet the promised cleanup contract without a narrow lifecycle hardening

The plan requires every post-initialization path to release `Workbook.Close(False)`,
Excel `Quit`, and `CoUninitialize` exactly once, while retaining the primary read/open
failure. The current reusable primitive does not provide that guarantee:

- [`office_lifecycle.py`](D:\PythonProject\connlab\backend\infrastructure\office\office_lifecycle.py:68)
  invokes `_apply_excel_automation_settings()` outside the cleanup `try`; a settings
  assignment failure after `DispatchEx` leaks the owned Excel instance and COM
  initialization.
- [`office_lifecycle.py`](D:\PythonProject\connlab\backend\infrastructure\office\office_lifecycle.py:26)
  calls `Quit()` before `CoUninitialize()` without a nested `finally`; a `Quit()` failure
  skips COM uninitialization. A cleanup exception can also replace the earlier gateway
  read/header diagnosis unless the gateway and handle define primary-error precedence.

TASK_366A currently locks `office_lifecycle.py` out of May Touch while relying on it for
the new `.xls` path. A gateway-only fix cannot clean an exception that occurs before a
handle is returned.

**Required Planner docs-only fix:** authorize one bounded lifecycle hardening hunk in
`backend/infrastructure/office/office_lifecycle.py` and focused additions to
`tests/unit/test_office_lifecycle.py`. Freeze the cleanup order and error precedence:
after successful `CoInitialize`, every later setup/open failure must attempt owned
`Quit` and always attempt `CoUninitialize`; after a successful open, `close(False)` must
attempt Close, restoration, Quit, and CoUninitialize once even if an earlier cleanup
call raises. The original open/read/header failure remains the public diagnostic with
cleanup context attached only when safe. This must remain isolated from LTR write paths.

### B2: UsedRange safety limit is not an executable contract

The plan requires a bounded UsedRange but leaves the rows/columns/cell cap for a future
Reviewer decision. Neither the task nor plan fixes numeric limits or whether each bound
is independently enforced. That prevents deterministic fake-COM oversize tests and
leaves an avoidable resource-exhaustion decision to implementation.

**Required Planner docs-only fix:** freeze exact maximum rows, columns, and/or total
cells; state the check occurs before reading `Value`/`Value2`; and list boundary and
over-limit fake-COM cases in the mandatory test matrix. The cap must be shared by the
probe/read contract only and must not alter `.xlsx` behavior.

## Confirmed Correct Boundaries

- The real chain supports the proposed narrow format-router design: Settings validation
  currently rejects `.xls` only for Standard record and Equipment calibration, while
  `ExternalExcelReadService` and its API DTOs already consume format-neutral tabular
  results.
- Keeping `ExcelWorkbookGateway` unchanged and dispatching only probe/tabular calls is
  the right `.xlsx` non-regression boundary. LTR's `read_excel_workbook()` remains
  excluded.
- The proposed hidden `DispatchEx`, `UpdateLinks=0`, `ReadOnly=True`, `AddToMru=False`,
  no-save/no-conversion rule, deterministic error categories, mandatory fake-COM tests,
  and temp-directory-only optional real-COM smoke all match the requested scope.
- Frontend, Settings React/API client, LTR writes, Fee/export, Matrix/project lifecycle,
  schema/database, real files, release output, staging, and unrelated residuals remain
  locked.

## Validation Performed

- Read-only source and test inspection only.
- TASK_366A governance `git diff --check`: passed with only the repository's existing
  LF/CRLF notice.
- UTF-8 trailing-whitespace scans for board/task/plan/Planner evidence: clean.
- Staging is empty. Existing modified/untracked product and release paths are external
  residuals and were not absorbed.

## Next Legal Route

Route only to **Planner docs-only fix pass** for B1 and B2. Do not route Developer
planning-first or implementation until the plan is re-gated and later user approvals
are recorded.

## B1/B2 Plan Re-Gate

Date: 2026-07-20

Status: `reviewer_pass`

### B1 Lifecycle Boundary

The revised task and plan now permit only a narrow future hardening of
`backend/infrastructure/office/office_lifecycle.py`, together with focused additions to
`tests/unit/test_office_lifecycle.py`. The allowed behavior is limited to COM ownership,
idempotent cleanup, nested-finally release ordering, and primary-error precedence.
It expressly preserves existing open parameters and locks LTR write/password/transaction
behavior, Word, Outlook, and all other Office behavior.

The required fake-COM coverage is now explicit for automation-settings failure after
`DispatchEx`, `Quit` failure, primary read/header error plus cleanup error, success and
post-open failure counts, and repeated handle close. This closes the previously
unreachable lifecycle failure paths without widening the lane into LTR automation.

### B2 UsedRange Boundary

The `.xls` gateway now has a precise, `.xlsx`-independent pre-read contract:

- `65_536` rows, `256` columns, and `1_000_000` cells are each inclusive maxima;
- malformed, non-integral, negative, or over-limit dimensions fail before `Value` or
  `Value2` is touched; and
- mandatory fake-COM cases prove every exact boundary and independently over-limit axis.

This makes the resource bound deterministic and testable without allocating a large
workbook or accessing an operator file.

### Re-Gate Validation

- Read-only review of the updated task, plan, Planner evidence, and existing lifecycle
  implementation.
- TASK_366A governance `git diff --check`: passed with only the existing repository
  LF/CRLF notice.
- UTF-8 trailing-whitespace scans: clean.
- No TASK_366A product/test candidate is present; staging remains empty. Existing dirty
  paths remain external residuals.

### Next Legal Route

Recommend **User approval for Developer planning-first** only. TASK_366A remains
planned-only and product implementation remains unauthorized; do not route Developer
implementation directly.

## Implementation-Readiness Gate

Date: 2026-07-20

Status: `reviewer_blocked / source-of-truth reconciliation required`

## Finding

### B3: Board and governing task state still describe the already-completed plan gate

The Developer evidence and updated plan correctly report
`developer_planning_first_complete / pending Reviewer implementation-readiness`.
However, the current task board, TASK_366A task, and Planner evidence still state
`pending Reviewer plan re-gate` and direct the next role to Reviewer plan re-gate. This
is a governing state conflict, not merely historical narration: the board is the
execution source of truth and still forbids Developer planning-first, which has already
occurred under the recorded user approval.

**Required Planner docs-only reconciliation:** update only the TASK_366A board row and
active-task summary, task status/role/next-route fields, and Planner evidence to record
the completed plan re-gate and Developer planning-first pass, then set the current state
to `ready for Reviewer implementation-readiness / implementation unauthorized`. Do not
approve product implementation or modify code/tests while reconciling.

## Readiness Work Confirmed Pending Reconciliation

- The exact new gateway/facade/lifecycle/resource/picker file sequence is sufficient
  to preserve `.xlsx`, isolate `.xls` COM routing, and leave the row service, routes,
  DTOs, dependencies, models, WindowsPathPicker, `pyproject.toml`, frontend, and LTR
  sources read-only.
- The planned `ValueError` hierarchy is sufficient for the existing HTTP 400 boundary;
  the optional pywin32 runtime remains correctly handled without a dependency change.
- Lifecycle ownership, primary-error precedence, read-only/no-save behavior, and the
  inclusive `65_536` / `256` / `1_000_000` pre-Value/Value2 checks are concrete and
  backed by mandatory fake-COM cases plus a temp-only optional real-COM smoke.
- The plan's physical-line facts were independently verified with its declared
  `Path.read_text(encoding="utf-8").splitlines()` method: facade `223`, lifecycle `127`,
  resource service `211`, desktop picker `107`, XLSX gateway `435`, and all listed test
  files match the recorded baseline and remain below their future limits.

## Validation

- Read-only code/evidence inspection only; no product or test path changed.
- Candidate product/test paths remain clean; Developer planning-first changed only its
  evidence and the TASK_366A plan. Staging remains empty and real/public-drive files
  were not accessed.

## Next Legal Route

Route only to **Planner docs-only source-of-truth reconciliation**. After that, rerun
this Reviewer implementation-readiness gate; product implementation remains
unauthorized until the later explicit user approval and final reconciliation.

## B3 Reconciliation And Implementation-Readiness Re-Gate

Date: 2026-07-20

Status: `reviewer_pass`

The TASK_366A board entry, task status/current-role fields, Planner evidence, plan, and
new reconciliation evidence now consistently record: Reviewer plan re-gate passed,
user-approved Developer planning-first completed, Reviewer implementation-readiness is
the current gate, and product implementation remains unauthorized. The prior
pending-plan-gate language is retained only as historical evidence.

The previously reviewed technical contract remains implementation-ready without scope
expansion:

- `.xlsx` remains on the unchanged ZIP/XML gateway; only `.xls` probe/tabular calls
  route to the hidden read-only COM gateway through `OfficeFacade`.
- All new `.xls` errors inherit `ValueError`, preserving validation diagnostics and the
  existing HTTP 400 route boundary; pywin32 stays an optional runtime dependency.
- The lifecycle hardening, exact-once/idempotent cleanup, primary-error precedence,
  no-save rule, and inclusive pre-read UsedRange caps (`65_536` rows, `256` columns,
  `1_000_000` cells) are explicit and covered by mandatory fake-COM cases.
- The only conditional host smoke creates and reads a disposable temp `.xls`; no real
  operator/public-drive workbook is eligible. All named product, LTR, API/DTO,
  frontend, schema/database, and residual locks remain intact.

Validation was governance-only: TASK_366A diff/trailing checks passed with only the
existing LF/CRLF notice, no candidate product/test path is changed, and staging remains
empty.

## Next Legal Route

Recommend only **User product implementation approval, followed by Planner final
source-of-truth reconciliation**. Do not route Developer implementation directly.

## Implementation Gate

Date: 2026-07-20

Status: `reviewer_blocked`

### B4: `.Value` fallback is broader than the approved COM-compatibility contract

[`excel_com_readonly_tabular_gateway.py`](D:\PythonProject\connlab\backend\infrastructure\office\excel_com_readonly_tabular_gateway.py:234)
catches every `Exception` from `UsedRange.Value` and then reads `Value2`. The frozen
contract permits the second read only for a COM read-compatibility failure. As written,
a programming bug or unrelated runtime failure is silently retried through `Value2`,
which can mask the primary diagnosis and violates the declared no-second-read behavior
for non-COM failures. The current test labels a generic `RuntimeError` as the compatible
fallback case, so it cannot distinguish the two paths.

**Required bounded Developer fix:** add a narrow COM-read compatibility classifier that
does not introduce a direct pywin32 dependency; use it to decide whether `Value2` may
be read. Add regressions proving a recognized compatibility error takes the `Value2`
path, while an arbitrary non-COM `Value` exception becomes `LegacyExcelReadError`,
leaves `Value2` untouched, and retains the normal close/primary-error semantics. Keep
the change confined to the new gateway and its focused test module.

### Validation Reproduced

- Declared nine-module focused suite: `72 passed`.
- `py_compile` for all five authorized product modules: passed.
- Candidate `git diff --check`: passed with only repository LF/CRLF notices.
- All candidate Python files are below the 500-line hard limit; staging is empty.

The route boundary, `.xlsx` non-dispatch, read-only open, lifecycle cleanup,
ValueError-to-HTTP-400 mapping, range prechecks, picker scope, and locked-path checks
otherwise conform to TASK_366A.

## Next Legal Route

Route only to **Developer bounded fix pass** for B4. Do not route QA or Integrator.

## B4 Implementation Re-Gate

Date: 2026-07-20

Status: `reviewer_pass`

The bounded B4 change closes the earlier fallback overreach without widening the
lane:

- `_is_com_read_compatibility_error()` recognizes only a runtime exception whose
  type is exactly named `com_error` from the `pywintypes` module. The gateway does
  not import `pywin32` or `pywintypes`, so the optional Windows COM dependency remains
  runtime-only.
- A recognized COM compatibility failure is the sole path that reads
  `UsedRange.Value2`. An arbitrary `RuntimeError` from `Value` is immediately wrapped
  as `LegacyExcelReadError`; its regression proves `Value2` remains untouched.
- The regression with both an arbitrary read failure and a close failure preserves the
  read diagnosis as the public exception and attaches the cleanup failure as context.
  This retains the lifecycle primary-error contract.
- No product path outside the new gateway and its focused test gained B4 behavior.
  The broader TASK_366A candidate remains confined to the already-authorized
  facade/lifecycle/resource/picker and focused test boundary; `.xlsx`, LTR, routes,
  DTOs, frontend, settings persistence, and real/public-drive files remain untouched.

### Validation Reproduced

- Nine focused modules: `74 passed`.
- `py_compile` for the five authorized production modules: passed.
- Candidate diff checks and UTF-8 trailing-whitespace checks: clean apart from the
  repository's pre-existing LF/CRLF notices.
- The checked-out UTF-8 physical counts are gateway `309` and focused gateway test
  `346`, both below the hard limit. This corrects the Developer evidence's stale
  `366` / `427` count narration without affecting the implementation result.
- `git diff --cached --quiet` returned zero; no candidate path is staged. No real
  database, public-drive path, or workbook was accessed during this review.

## Next Legal Route

Route only to **QA gate**. QA should run the deterministic fake-COM checks and, where
Windows Excel is available, the planned disposable temp-directory-only real-COM smoke.
Do not route Integrator from this gate.
