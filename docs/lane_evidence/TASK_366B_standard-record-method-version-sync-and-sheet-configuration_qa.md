# TASK_366B QA Evidence - Standard Record Method Version Sync And Sheet Configuration

**Date:** 2026-07-21
**Role:** QA / Smoke Owner
**Lane:** `standard-record-method-version-sync-and-sheet-configuration`
**Result:** `qa_pass` after B3 QA re-gate

## Scope and Safety

- QA performed read-only validation plus disposable pytest fixtures only. Backend test runs used `--basetemp` roots under `tmp/`.
- No real SQLite database, user attachment, public-drive workbook, source workbook, LTR file, generic Test Record file, or specialized workbook was opened or written.
- No product/test source, task board, staging area, commit, package, or push was modified by QA.
- The active board/task wording still includes an earlier Developer-pending state, but the 2026-07-21 Reviewer B1/B2 re-gate explicitly routed this active TASK_366B lane to QA. QA did not alter governance files.

## Validation Run

1. Disposable backend, Office, resource, API, migration, parser, preview/apply, and TASK_366A regression suite:

   ```powershell
   py -m pytest -p no:cacheprovider --basetemp=tmp\task_366b_qa_backend `
     tests/unit/test_standard_record_sheet_configuration.py `
     tests/unit/test_standard_record_method_sync_schema_migration.py `
     tests/integration/test_standard_record_sheet_configuration_api.py `
     tests/unit/test_excel_standard_record_layout_xlsx.py `
     tests/unit/test_excel_standard_record_layout_com.py `
     tests/unit/test_standard_record_catalog_read_service.py `
     tests/unit/test_standard_method_version_parser.py `
     tests/unit/test_matrix_method_version_sync_service.py `
     tests/unit/test_project_matrix_draft_method_sync_repository.py `
     tests/integration/test_matrix_method_version_sync_api.py `
     tests/unit/test_external_excel_read_service.py `
     tests/integration/test_external_excel_read_api.py `
     tests/unit/test_excel_com_readonly_tabular_gateway.py `
     tests/unit/test_office_lifecycle.py -q
   ```

   Result: **68 passed** in 29.27s.

   Coverage includes Standard worksheet field omission/reset/default and non-Standard rejection, additive migration fail-closed cases, Chinese catalog layout parity for disposable `.xlsx` and fake-COM `.xls`, read-only Office lifecycle/resource regressions, preview zero-write, selected-only method apply, typed `400`/`404`/`409`, root/row CAS, and B1/B2 TOCTOU/source-switch conflicts.

2. Focused frontend Settings/Matrix tests:

   ```powershell
   cd frontend
   npm test -- MatrixEditorWorkspace SettingsStandardRecordSheet MatrixMethodVersionSyncPanel useMatrixMethodVersionSync --run
   ```

   Result: **4 files / 48 tests passed**. The suite covers Settings path-save omission, explicit sheet clear/reset, safe proposal presentation, selected-only apply, session reload, and existing Matrix cancel/confirm behavior.

3. Build and compilation:

   ```powershell
   cd frontend
   npm run build
   ```

   Result: passed. `tsc -b` and Vite completed; only the existing Vite chunk-size warning was emitted.

   ```powershell
   py -m py_compile <all TASK_366B touched backend product modules>
   ```

   Result: passed (no output).

## Static and Package Checks

- Candidate `git diff --check`: no whitespace error; only existing LF/CRLF notices.
- UTF-8 trailing-whitespace scan across the TASK_366B candidate paths: no matches.
- Staged file count: `0`; `git status --short -- data`: empty.
- Expected TASK_366B new files are untracked in the dirty worktree; all are within the approved product/test boundary. The active candidate also includes approved narrow hunks in shared Office, Settings, Matrix, API, and storage files.
- No candidate real public-drive or real database path was used by QA. External Fee, parser, packaging/release, and other dirty-worktree residuals remain excluded.

## Blocking Finding

### B3 - 514px Method-sync table does not implement the approved responsive contract

**Expected:** The approved plan states that at 514px the Method sync surface uses “stacked current/proposed text per row without horizontal overflow” ([plan](D:\PythonProject\connlab\docs\task_366b_standard_record_method_version_sync_and_sheet_configuration_plan.md:52)) and reiterates that the sync table stacks current/proposed values while the status stays adjacent to its row ([plan](D:\PythonProject\connlab\docs\task_366b_standard_record_method_version_sync_and_sheet_configuration_plan.md:516)).

**Observed:**

1. `MatrixMethodVersionSyncPanel` always renders one five-column semantic table, with separate `Current`, `Catalog`, and `Status` cells and no responsive row labels or alternative mobile markup ([panel](D:\PythonProject\connlab\frontend\src\features\matrix-editor\MatrixMethodVersionSyncPanel.tsx:51)).
2. Its CSS enforces `min-width: 680px` and resolves narrow widths through `overflow-x: auto` ([CSS](D:\PythonProject\connlab\frontend\src\workbench.css:9326)).
3. The only `<600px` Method-sync rules change the header/action flex layout; they do not stack table rows/current/proposed/status ([CSS](D:\PythonProject\connlab\frontend\src\workbench.css:9352)).

**Impact:** At the required 514px viewport, a preview with rows remains a horizontally scrollable 680px table. It does not present the current/proposed pair as one readable row with its status adjacent, as required by the frozen plan. The focused component tests and build do not exercise this responsive contract.

**Minimal reproduction:** Render any non-empty Method-version preview, set the viewport to 514px, and inspect the sync table. The fixed 680px minimum requires horizontal scrolling rather than the approved stacked row layout.

**Required owner and bounded fix:** **Developer fix pass** limited to the approved `MatrixMethodVersionSyncPanel.tsx` and `workbench.css` responsive-hunk scope. Implement the approved narrow-row presentation at 514px while preserving desktop semantic table behavior, row selection labels, busy/disabled rules, and selected-only apply. Add a focused responsive/component regression before returning to QA.

## Browser Note

No live browser smoke was run: the local application is not configured with a disposable API/server fixture, and starting the normal application could use operator configuration. This is not the blocker. The responsive failure is directly reproducible from the rendered DOM and all matching CSS rules above.

## Gate Decision

**Historical QA gate:** blocked before B3 corrective implementation.

## B3 QA Re-Gate - 2026-07-21

**Result:** `qa_pass`

### B3 Correction Verification

- `MatrixMethodVersionSyncPanel` retains its desktop five-column semantic table. At `max-width: 600px`, each actual table row now has the approved grid sequence: `Use`, `Test item`, and `Status` on the first line, then `Current`, then `Proposed`. Current/proposed cells retain DOM order and carry `data-label` values used by the narrow layout.
- The narrow rule sets the panel table to `min-width: 0`, removes forced horizontal scrolling from the wrapper, uses `minmax(0, ...)`, and applies `overflow-wrap: anywhere` to long item/status/current/proposed content. Header actions use a two-column grid at the same breakpoint.
- Native checkbox inputs retain row-specific accessible labels. The panel retains semantic native buttons, so Tab, Space, and Enter use browser-native focus and activation behavior; no custom key handler was introduced. The focused component test continues to prove row selection and selected-only Apply callback behavior.

### Re-Gate Commands and Results

```powershell
py -m pytest -p no:cacheprovider --basetemp=tmp\task_366b_qa_regate_backend tests/unit/test_matrix_method_version_sync_service.py -q
```

Result: **5 passed** in 1.73s. The earlier QA disposable 68-test backend/Office/API suite remains applicable because B3 is presentation-only.

```powershell
cd frontend
npm test -- MatrixEditorWorkspace SettingsStandardRecordSheet MatrixMethodVersionSyncPanel useMatrixMethodVersionSync --run
```

Result: **4 files / 49 tests passed**. This includes the new B3 DOM/class/data-label assertion, safe row selection, selected-only apply, Settings reset/default behavior, and existing Matrix workspace regressions.

```powershell
cd frontend
npm run build
```

Result: passed, including `tsc -b`; only the existing Vite chunk-size warning remains.

### Re-Gate Static Checks

- Focused `git diff --check` and UTF-8 trailing-whitespace scan: clean, apart from existing LF/CRLF notices.
- B3 candidate scope is limited to `MatrixMethodVersionSyncPanel.tsx`, its focused test, and the exact responsive `workbench.css` hunk. No API/route/backend/Confirm Matrix, real-file, or public-drive token was added in that hunk.
- Index remains empty; `data/` remains clean. No real database, attachment, workbook, or public-drive path was accessed.

### Controlled Browser Attempt / Residual

QA created a disposable `tmp/task366b_qa_browser/` static harness that referenced the current panel DOM and current `workbench.css`. The in-app Browser rejected local-file navigation under its URL safety policy. QA did not bypass that policy, did not start the normal application because it could read operator configuration, and removed the temporary harness (`HARNESS_CLEANED=True`). Therefore no screenshot or live console artifact exists.

This is a non-blocking tooling residual, not a product failure: the exact current DOM/CSS establishes the required 514px grid/no-horizontal-scroll behavior, and the actual component/workspace suite and production build pass.

**QA re-gate: pass.** B3 is closed. Recommend **Integrator packaging/readiness** for the isolated TASK_366B candidate; keep all external Fee and dirty-worktree residuals excluded.
