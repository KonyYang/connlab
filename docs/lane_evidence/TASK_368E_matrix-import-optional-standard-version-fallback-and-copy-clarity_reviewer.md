# TASK_368E Reviewer Evidence

Date: 2026-08-01

Role: Reviewer

Status: `reviewer_blocked`

Next role: Developer

## Gate Authority And Inspected Package

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Active task: `TASK_368E_MATRIX_IMPORT_OPTIONAL_STANDARD_VERSION_FALLBACK_AND_COPY_CLARITY`.
- Why allowed: primary `docs/task_board.md` records TASK_368E as the sole WIP=1 token owner in
  `gate_running` / `Reviewer`; queue, paused task, Quick Fix, and parallel exception are null.
- Exact lane: `lane/task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`
  in `D:\PythonProject\connlab-worktrees\task-368e-matrix-import-optional-standard-version-fallback-and-copy-clarity`.
- Review base: `e226bf1e54db4de54eb2366e96895999ce54652d`.
- Implementation checkpoint: `9cd39e2dc5e8b50f23fd3e3202913a96019d4999`.
- Reviewed HEAD: `bb9734830b41c3a86c1cd5542d34a0832cd990d4`.
- Primary authority inspected read-only at `82fabf965c178843be689429c9f90be97787eabe`.
- Read before review: `AGENTS.md`, primary task board, TASK_368E task/plan, TASK_366B/C
  task/plan contracts, Developer evidence, review checklist, backend/frontend architecture
  rules, and `$impeccable` product/design context.
- Base ancestry, exact branch/HEAD, clean index/worktree, `git diff --check`, implementation
  `git show --check`, and the exact 18-path base..HEAD package were independently verified.
  There was no unexpected path, staged change, `data/**`, package/lockfile, Office gateway,
  persistence/schema, Confirm Matrix, or Standard Method versions change.

## Findings First

### Blocking B1 - cleanup integrity failures can be downgraded to Skip fallback

`backend/application/matrix_import_method_authority.py:390` walks through every exception's
`__cause__` / `__context__` and accepts `PermissionError` or an allowed Windows code without
first stopping on a known integrity wrapper. The existing legacy gateway raises
`LegacyExcelCleanupError` from the underlying cleanup exception at
`backend/infrastructure/office/excel_com_readonly_tabular_gateway.py:235`. Consequently a cleanup
failure whose cause is `PermissionError` (or an allowed Windows availability-code `OSError`) is
classified as `standard_version_file_unavailable`; explicit preserve then succeeds as
`source_preserved`.

Independent in-memory reproduction on reviewed HEAD:

```text
py -c "... LegacyExcelCleanupError ... __cause__=PermissionError(...) ... _availability_reason(...)"
-> standard_version_file_unavailable

py -c "... resolver failure=LegacyExcelCleanupError(caused by PermissionError) ...
        unavailable_action='preserve_imported_methods' ..."
-> source_preserved standard_version_unavailable
```

This violates the frozen task/plan rule that cleanup failure is an integrity condition: it must
remain typed `422`, zero-write, and must neither expose nor honor Skip. The current TASK_368E tests
cover bare corrupt/unknown errors but do not cover a known integrity wrapper containing an
otherwise allowlisted cause.

Minimal executable fix:

1. Make the availability classifier fail closed when the inspected chain reaches
   `LegacyExcelCleanupError` before considering its nested cause. Preserve the approved behavior
   for genuine file-open/read availability causes and `LegacyExcelComUnavailableError`.
2. Add bounded unit and API regressions proving both the default request and explicit
   `preserve_imported_methods` keep a cleanup wrapper with `PermissionError`/allowed Windows cause
   on `422` with zero source/draft writes and no action-required detail.
3. Re-run the existing positive allowlist, integrity matrix, compatibility, build, and line-count
   gates. `matrix_import_method_authority.py` is already exactly 499 physical lines, so the fix
   must preserve the `<500` hard limit without weakening the classifier.

### Non-blocking observations

- `matrix_import_method_authority.py` is exactly 499 physical UTF-8 lines and
  `matrix_import_commit_service.py` is 449. Both satisfy the hard limit, but the authority module
  has no maintenance margin and imports a private `_context_identity` across modules. This is not
  a separate scope blocker, but the bounded fix must not exceed the ceiling.
- Frontend review found the controlled 409 predicate, exact dialog/Settings copy, focus entry and
  Escape focus return, picker-cancel zero-write behavior, worksheet preservation, recoverable
  validation, Skip application/close behavior, and exact amber polite warning consistent with the
  task and `$impeccable` product context. Generic 409/422 errors do not open the Skip dialog.

## Independent Validation

Passing checks on reviewed HEAD:

- TASK_368E backend unit/API: `21 passed`.
- TASK_366B/C import authority, strict reuse, group selection, source persistence, saved-draft
  Method sync, and Confirm authority compatibility set: `61 passed`.
- Disposable XLSX, fake-COM XLS, Standard catalog, and external read compatibility: `8 passed`.
- Matrix session service: `16 passed, 1 failed`; the sole failure is the separately attributed
  legacy fake below.
- Focused/compatibility frontend: `8 files / 61 tests passed`, including the new choice/hook/
  workspace/Settings coverage plus existing Matrix Editor and Standard Method versions behavior.
- Disposable HEAD frontend mirror build: passed (`tsc -b` and Vite), with only the existing
  chunk-size advisory.
- `py -m py_compile` for all five changed Python product/test modules: passed.
- Exact line counts: authority `499`, commit service `449`, route `291`, new backend tests
  `288 / 250`, dialog/hook `96 / 113`, and new frontend tests `269 / 73 / 98`.
- `git diff --check`, base ancestry, implementation `show --check`, exact allowlist, staged-empty,
  `data/**`/package/lockfile status, and no workbook-save/real-data scan: passed.

The blocking reproduction itself passed as a diagnostic and proves the incorrect outcome:
`LegacyExcelCleanupError(PermissionError)` produced `source_preserved` instead of a fail-closed
error.

## Baseline Debt Attribution

- Reviewed HEAD full `tests/unit/test_frontend_shell_files.py`:
  `134 passed, 28 failed`.
- Disposable base snapshot of the same module:
  `132 passed, 30 failed`.
- Every one of the 28 HEAD failure nodes was already failing at the base. TASK_368E introduced no
  shell-test failure and made two prior base failures pass; the exact TASK_368E Settings assertions
  also pass. The remaining 28 are historical static-contract debt outside this package.
- `test_confirm_first_authority_initializes_default_fee_authority` fails identically at base and
  reviewed HEAD because `_RecordingMatrixImportCommitService` constructs the already-required
  `MatrixImportCommitResult` without `method_authority_sync`. This task did not change that test or
  constructor requirement; it is baseline-only debt, not a TASK_368E regression.

All baseline comparisons used temporary `git archive` snapshots and disposable runtime files;
temporary artifacts were removed. No real database, Excel/PDF/DOCX, public-drive path, workbook,
server, or operator resource was read or written.

## Conclusion And Handoff

`reviewer_blocked`.

The frontend, source-preservation, transaction, strict reuse, nullability, and configured-success
contracts otherwise passed the reviewed checks, but B1 leaves an explicitly forbidden integrity
bypass. Return only the bounded classifier/test fix to Developer, then perform a full Reviewer
re-gate. Do not advance to QA until this blocker is closed.
