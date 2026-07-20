# TASK_366A Planner Discovery Evidence

## Routing

- Task: `TASK_366A_EXTERNAL_EXCEL_XLS_READ_COMPATIBILITY`
- Lane: `external-excel-xls-read-compatibility`
- Role: Planner
- Status: `implementation authorized / pending Developer implementation`
- Date: 2026-07-20
- Implementation authorization: none

## Current Phase / Active Task / Why Allowed

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- The prior board had no selected active product lane. The user explicitly requested
  this independent Discovery Gate and formal planned-only lane.
- TASK_365B accepted commit `a58c96a3...` is an ancestor of current HEAD
  `f82a942687a85d1ee1a02c490d630f19bb548d95`.
- The worktree contains many unrelated changes. This pass does not clean, revert,
  stage, commit, or absorb them.

## Evidence Read

- `AGENTS.md`, `docs/task_board.md`
- Planner Discovery, Parallel Execution, Lane Orchestration, and Role Registry protocols
- `PRODUCT.md`, `DESIGN.md`, architecture and frontend architecture rules
- Settings resource config and desktop picker bridge
- external resource validation and read services/routes
- `OfficeFacade`, `ExcelWorkbookGateway`, `OfficeLifecycleManager`, Office models/
  exports, and existing LTR COM boundaries
- focused resource, row-read, API, picker, structure-probe, and lifecycle tests

## Confirmed By User

- Standard record and Equipment calibration Settings resources need `.xls/.xlsx`.
- `.xlsx` remains unchanged; `.xls` uses controlled read-only Excel COM.
- Excel unavailable, corrupt file, and header mismatch must be diagnosable.
- No write/conversion/save-as/real public-drive access is allowed.
- LTR, Fee, Matrix, lifecycle, schema/database, remote push, and dirty cleanup are locked.

## Confirmed By Repository Evidence

- Picker filters currently expose `.xlsx` only for both named resources.
- Validation currently rejects `.xls` for both named resources.
- The row-read application/API contracts are already format-neutral.
- The `.xlsx` gateway is a read-only ZIP/XML implementation with established sheet/
  header diagnostics and no need for COM.
- The Office lifecycle already owns hidden Excel startup and deterministic close/quit/
  COM uninitialization, and supports `read_only=True`.
- No frontend DTO, registry schema, or database migration is required.

## Planner Decisions

1. Use one new bounded infrastructure gateway for `.xls` probe and tabular read.
2. Dispatch only `probe_excel_structure()` and `read_excel_tabular_rows()` by suffix
   inside `OfficeFacade`; preserve LTR `read_excel_workbook()` behavior.
3. Keep `excel_workbook_gateway.py` production behavior locked, proving parity by tests.
4. Reuse `ExcelStructureProbeResult` and `ExcelTabularReadResult`; no public API change.
5. Freeze read-only COM flags and exactly-once cleanup/no-save behavior.
6. Treat fake-COM lifecycle tests as mandatory and real Excel temp-file smoke as
   conditional host evidence, never as access to a real operator workbook.
7. Keep the lane serialized across its three shared composition files and package by
   exact whitelist/hunks in the existing dirty worktree.

## Reviewer B1/B2 Fix Decision

- B1 is confirmed by source inspection. `office_lifecycle.py` must be a narrow Future
  May Touch file because automation-settings can fail after DispatchEx but before a
  handle is returned, and Quit can currently prevent CoUninitialize.
- The only added lifecycle scope is setup/open/Close/restore/Quit/CoUninitialize
  cleanup, exactly-once ownership/idempotency, and primary-error precedence. LTR write,
  password, save, transaction, Word, Outlook, and all other Office behavior stay locked.
- B2 is frozen with independent pre-read limits: `65_536` rows, `256` columns, and
  `1_000_000` total cells. Equality passes; malformed or over-limit counts fail before
  either `UsedRange.Value` or `Value2` is touched.
- Mandatory fake-COM tests now cover each boundary/over-limit axis, settings failure,
  Quit failure, primary-plus-cleanup failure, exactly-once cleanup, and repeated close.

## Historical B3 Source-Of-Truth Reconciliation

- Reviewer plan re-gate passed after the B1/B2 docs-only corrections.
- The user explicitly approved Developer planning-first only.
- Developer completed the docs-only planning-first pass and recorded exact private
  error, injection, lifecycle, file, test, line-count, and package boundaries in the
  plan and Developer evidence.
- No product/test implementation was authorized or performed by that pass.
- At that checkpoint, the state was `ready for Reviewer implementation-readiness
  re-gate` and product implementation was not yet authorized. The final authorization
  section below supersedes that historical gate state.
- The technical contract, May Touch, locks, UsedRange limits, COM lifecycle/error
  policy, `.xlsx` preservation, and temp-only optional real-COM smoke are unchanged.

## Final Implementation Authorization Reconciliation

- Reviewer implementation-readiness re-gate passed.
- The user explicitly approved TASK_366A product implementation.
- Authorization is limited to the exact May Touch and focused tests in the reviewed
  task/plan. Every locked path and stop-and-re-gate condition remains active.
- The required behavior remains unchanged: `.xlsx` stays on the current gateway;
  `.xls` uses hidden read-only COM; errors remain typed/actionable; lifecycle cleanup
  is exactly-once/idempotent with primary-error precedence; UsedRange inclusive caps
  remain `65_536`/`256`/`1_000_000` before `Value`/`Value2`; fake-COM is mandatory and
  real-COM smoke remains temp-only and optional.
- This Planner pass changes governance only. Product/test implementation is delegated
  to the next legal Developer role.

## Not Yet Confirmed

- Private symbol names may follow repository conventions during planning-first. The
  UsedRange limits and observable cleanup/error behavior are no longer open decisions.
- Excel may not be installed on every CI host; the conditional smoke must report a
  skip reason while deterministic fake-COM tests remain required.

These are non-blocking and do not alter May Touch or acceptance semantics.

## Risks Controlled

- Accidental `.xlsx` COM fallback is prevented by suffix routing and regressions.
- File mutation is prevented by read-only open, no Save/SaveAs API, close(false), and
  no-write call assertions.
- Excel orphan processes are prevented by owned DispatchEx lifecycle and cleanup tests.
- Header/layout drift produces typed diagnostics rather than partial silent reads.
- Oversized UsedRange data fails boundedly instead of consuming unbounded memory.
- LTR and other Office automation remain outside the package.

## Discovery Validation

- Confirmed TASK_366A task/plan/evidence paths did not previously exist.
- Confirmed current HEAD and TASK_365B ancestor relationship.
- Confirmed current staging was empty before edits.
- Read-only repository inspection only; no product test or real file operation was
  needed for this governance pass.
- `git diff --check -- docs/task_board.md`: passed; existing LF/CRLF notice only.
- UTF-8 trailing-whitespace scan across all three new TASK_366A documents: clean.
- Final authorization document line counts: task `210`, Developer-refined plan `515`,
  and Planner evidence `151` before this final checkpoint. Product/test file
  limits remain the separate frozen implementation gate.
- Targeted product-candidate status scan: no TASK_366A product/test candidate changed.
- `git diff --cached --name-only`: empty; no staging, commit, or push occurred.
- B1/B2 stale-contract scan: no current pending-plan-gate wording, unfrozen range
  limit, or lifecycle-hardening omission remains in TASK_366A governance.

## Definition Of Ready

Definition of Ready and authorization gates are satisfied. The lane is executable only
within the exact reviewed scope and is pending Developer implementation. No blocker
remains.

## Next Legal Role

Developer implementation pass only.
