# TASK_366C QA Evidence - Import Matrix Replace Method Authority Sync

**Date:** 2026-07-21
**Role:** QA / Smoke Owner
**Lane:** `import-matrix-replace-method-authority-sync`
**Result:** `qa_pass`

## Scope and Safety

- QA used only disposable pytest SQLite/XLSX/fake resources. The complete backend run
  used `--basetemp=tmp\task_366c_qa_backend`.
- No real database, user attachment, public-drive workbook, LTR file, source workbook,
  generic Test Record, specialized workbook, or output artifact was accessed or
  modified.
- No product/test code, board, staging area, package, commit, or push was modified by
  QA.
- At QA time, the board retained an earlier Reviewer-fixture-pending phrase while the
  explicit Reviewer implementation pass routed this active TASK_366C lane to QA. QA did
  not change governance files. The subsequent Planner post-QA source-of-truth
  reconciliation supersedes that governance residual and keeps the QA result unchanged.

## Validation Commands and Results

1. Disposable import authority/API/replay regression suite:

   ```powershell
   py -m pytest -p no:cacheprovider --basetemp=tmp\task_366c_qa_backend `
     tests/unit/test_matrix_import_commit_service.py `
     tests/unit/test_matrix_import_method_authority.py `
     tests/integration/test_matrix_import_method_authority_commit_api.py `
     tests/integration/test_matrix_import_group_selection_commit_api.py `
     tests/integration/test_project_test_plan_source_matrix_import_persistence_api.py `
     tests/unit/test_standard_method_version_parser.py `
     tests/unit/test_matrix_method_version_sync_service.py `
     tests/integration/test_matrix_method_version_sync_api.py -q
   ```

   Result: **28 passed** in 13.43s.

   The suite covers safe EIA-364 revision replacement, row-level safe/unsafe outcomes,
   missing/duplicate source identity, catalog/source mismatch, selected-only import,
   strict same-context reuse, changed resource/path/catalog/context conflicts,
   all-table source-authority zero-write, and post-draft persistence rollback.

2. Matrix Editor returned-draft regression:

   ```powershell
   cd frontend
   npm test -- MatrixEditorWorkspace --run
   ```

   Result: **1 file / 44 tests passed**. The Replace regression asserts the returned
   authoritative draft is applied immediately and the inline result reports
   `Matrix replaced. 1 Method updated; 2 rows need review.`

3. Frontend production build:

   ```powershell
   cd frontend
   npm run build
   ```

   Result: passed, including `tsc -b`; only the existing Vite chunk-size warning was
   emitted.

4. Python compilation:

   ```powershell
   py -m py_compile backend/application/source_matrix_import_persistence_service.py backend/application/source_matrix_import_builder.py backend/application/matrix_import_commit_service.py backend/application/matrix_import_draft_builder.py backend/application/matrix_import_method_authority.py backend/api/routes_matrix_import_commit.py backend/api/dependencies.py tests/unit/test_matrix_import_commit_service.py tests/unit/test_matrix_import_method_authority.py tests/integration/test_matrix_import_method_authority_commit_api.py tests/integration/test_matrix_import_group_selection_commit_api.py
   ```

   Result: passed (no output).

## Authority and UI Observations

- The commit flow prepares source/draft facts, resolves one current Standard
  resource/path/effective-sheet/catalog authority, derives proposals/fingerprints, and
  only then performs strict replay comparison or enters nested persistence. Current
  resource/catalog failure occurs before persistence; reuse is read-verified rather
  than the old early return.
- Safe unique EIA-364 candidates update only the editable returned draft. No-match,
  ambiguity, downgrade, stale resource/path/sheet/catalog/context, manually changed
  Method, or incomplete persisted aggregate remain typed no-write outcomes under the
  focused tests.
- Matrix Editor calls `applyDraftSnapshotToEditor()` with the returned
  `project_matrix_draft`, consumes `method_authority_sync`, and renders its concise
  result through `role=status` and `aria-live=polite`. This preserves Replace as the
  inline entry point without a separate saved-draft Method Apply action.
- Confirm Matrix remains outside Replace; the authority source is read-only. No
  confirmed Matrix direct mutation or Standard workbook save/convert/write appeared in
  production candidate additions.

## Fixture and Static Checks

- The only `workbook.save(...)` added in candidate scanning is the authorized test-only
  setup hunk in `test_matrix_import_group_selection_commit_api.py`. It creates
  `standard-records.xlsx` under pytest `tmp_path`, registers it through the existing
  External Resource API, and leaves the node's original `201 created` / `201 reused`
  assertions unchanged.
- Candidate `git diff --check`: no whitespace error; only existing LF/CRLF notices.
- UTF-8 trailing-whitespace scan: no matches. Staging count: `0`; `data/` status:
  empty.
- Bounded candidate line counts are under 500: authority module 448, source builder
  409, API test 358, commit-service test 337, commit service 320, route 257.
- External Fee/default-fill, parser, release/packaging, prior task governance, and
  other dirty-worktree residuals were observed but excluded.

## Browser / Narrow-Viewport Residual

No live browser smoke was run. There is no disposable local API/server fixture for the
real Matrix Editor route, and starting the normal application could read operator
configuration. The in-app Browser previously rejected local-file fixture navigation
under its URL safety policy; QA did not bypass that control. This is non-blocking here
because the source/actual Matrix Editor regression covers returned-draft and inline
summary consumption, and the production build passes. A future browser fixture lane
can add visual screenshots without reopening this authority implementation.

## Gate Decision

**QA gate: pass.** Recommend **Integrator packaging/readiness** for the isolated
TASK_366C candidate. Integrator must stage only the frozen TASK_366C hunks and exclude
all external residuals.
