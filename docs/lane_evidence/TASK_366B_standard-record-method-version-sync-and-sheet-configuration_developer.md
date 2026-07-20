# TASK_366B Developer Implementation Evidence

Date: 2026-07-21

Role: Developer

Lane: `standard-record-method-version-sync-and-sheet-configuration`

Status: `ready_for_reviewer_implementation_re_gate`

Implementation authorization: completed within the reconciled TASK_366B boundary.

## Current Phase And Legal Basis

- Phase: Phase 11 controlled Project Workbench / Matrix foundation.
- Active task: `TASK_366B_STANDARD_RECORD_METHOD_VERSION_SYNC_AND_SHEET_CONFIGURATION`.
- Planner reconciliation records Reviewer implementation-readiness pass and explicit
  user approval for this Developer implementation pass.
- This pass changes only the exact TASK_366B May Touch package. It does not stage,
  commit, push, open an operator database, or read/write a public-drive workbook.

## Implementation Result

### Standard worksheet configuration

- Added nullable `external_resources.worksheet_name VARCHAR(31)` and preserved stored
  `NULL` as the compatibility representation for effective default `认可标准`.
- Pydantic field presence now distinguishes omission from explicit reset. Omission
  preserves the stored value; null/trim-empty resets; valid text trims and persists;
  invalid Excel sheet characters, controls, length, and any supplied non-Standard
  value return typed HTTP 400 before repository write.
- Settings renders one compact Standard-only sheet field. Path blur/browse saves omit
  `worksheet_name`; sheet blur/Enter supplies it; clear sends explicit null and the
  server response rehydrates the effective default.

### Additive compatibility migration

- Added a dedicated SQLite `BEGIN IMMEDIATE` migration for the worksheet and Matrix
  sync-context columns.
- The migration preflights every existing target column before DDL, permits compatible
  one-column partial states, creates all missing columns in one transaction, and
  performs transaction-visible final shape verification before commit.
- Wrong affinity/nullability/default/PK shape, lock acquisition failure, and injected
  final verification failure are typed `authority_corrupt` failures with rollback.
  A repeated compatible startup is idempotent.

### XLSX and legacy Excel catalog layout

- Added shared `ExcelTabularLayout` mapping and preserved `layout=None` behavior for
  every existing caller.
- Standard reads now require one trim/casefold-unique configured worksheet, row 2
  header `B2 = 文 件 编 号`, optional C/D headers, and data from row 3. Sparse XLSX cell
  references retain physical B/C/D positions and source row numbers.
- `.xlsx` continues through the existing XML gateway; `.xls` continues through the
  accepted hidden read-only COM gateway. TASK_366A size limits, cleanup, no-save, and
  error precedence remain unchanged.
- Equipment calibration retains its previous first-nonempty-header behavior.

### Method preview and method-only apply

- Added a bounded deterministic parser for exact EIA/ANSI-EIA 364 method cores,
  immediate A-Z revisions, optional catalog year, ambiguity, current/update/missing
  revision, and downgrade blocking.
- Exported and reused the existing canonical Matrix draft payload signature.
- Preview is zero-write and binds the editable draft, active confirmed lineage,
  configured Standard resource, catalog rows, target rows, and typed proposals into a
  preview fingerprint.
- Apply rebuilds and revalidates preview facts, accepts only distinct selectable row
  IDs, and uses a method-only root/row CAS. A nested savepoint makes a row conflict
  roll back root provenance and every earlier row update.
- The operation changes only selected draft row Methods plus root updated-at and the
  versioned `matrix-method-sync:v1` audit context. It never mutates confirmed Matrix,
  groups, cells, quantities, schedule, or non-Method row fields.
- Thin typed routes return no-write HTTP 400/404/409. The Matrix workspace enables the
  panel only for a current saved editable draft and reloads the existing Matrix session
  after success; Confirm Matrix remains the only publication path.

### Reviewer B1/B2 bounded fix

- `_build_preview()` now returns one private build result containing both the public
  preview and the exact editable root snapshot used to validate it. Apply carries that
  root directly into the method-only CAS instead of loading a newer root immediately
  before the write. A root update between preview rebuild and CAS therefore returns the
  existing typed conflict and leaves all Method rows unchanged.
- The catalog fingerprint now binds configured Standard resource ID, normalized path,
  effective worksheet name, and catalog rows. Switching resource configuration while
  preserving identical row content changes the rebuilt preview fingerprint and returns
  HTTP 409/no-write through the unchanged API contract.
- No DTO, route, client, worksheet normalization, XLSX/COM read behavior, or Confirm
  Matrix publication boundary changed in this fix.

### QA B3 bounded responsive fix

- Desktop keeps the existing semantic five-column Method sync table and selection
  behavior.
- At `max-width: 600px`, including the required 514px viewport, each semantic table
  row becomes one bounded grid: selection, test item, and status share the first line;
  Current and Proposed values remain in DOM order and stack below with visible labels.
- The narrow breakpoint overrides the desktop `min-width: 680px` with `min-width: 0`
  and changes the wrapper to `overflow-x: visible`, so the Method sync surface no
  longer requires horizontal scrolling. Long item, status, and Method text may wrap
  instead of widening the row.
- The action area becomes two stable equal-width columns at the same breakpoint.
  Existing button, checkbox, busy, disabled, and apply-selected behavior is unchanged.
- The component regression asserts row/cell responsive hooks, visible Current,
  Proposed, and Status labels, and stable Current-before-Proposed DOM order. A separate
  UTF-8 CSS contract scan verifies the breakpoint, no-horizontal-overflow overrides,
  and all three grid-area rows.

## TDD And Focused Validation

### Backend focused suite

Command:

```text
py -m pytest tests/unit/test_standard_record_sheet_configuration.py tests/unit/test_standard_record_method_sync_schema_migration.py tests/integration/test_standard_record_sheet_configuration_api.py tests/unit/test_excel_standard_record_layout_xlsx.py tests/unit/test_excel_standard_record_layout_com.py tests/unit/test_standard_record_catalog_read_service.py tests/unit/test_standard_method_version_parser.py tests/unit/test_matrix_method_version_sync_service.py tests/unit/test_project_matrix_draft_method_sync_repository.py tests/integration/test_matrix_method_version_sync_api.py tests/unit/test_external_excel_read_service.py tests/integration/test_external_excel_read_api.py tests/unit/test_excel_com_readonly_tabular_gateway.py tests/unit/test_office_lifecycle.py -q
```

Result after the B1/B2 fix: `68 passed`.

Key red/green nodes include:

- `test_standard_sheet_api_distinguishes_omission_reset_and_nonstandard`
- `test_migration_completes_one_column_partial_state`
- `test_malformed_existing_column_fails_before_any_ddl`
- `test_final_verification_failure_rolls_back_both_alters`
- `test_locked_writer_fails_closed_then_recovers`
- `test_xlsx_explicit_layout_preserves_sparse_b_column_and_row_number`
- `test_preview_is_zero_write_and_reports_safe_method_update`
- `test_apply_uses_verified_preview_root_version_for_cas`
- `test_apply_rejects_identical_catalog_rows_from_changed_source_context`
- `test_method_sync_row_conflict_rolls_back_root_and_other_rows`
- `test_preview_apply_and_stale_conflict_use_typed_api`

The API integration explicitly proves invalid empty selection HTTP 400/no-write,
missing project draft HTTP 404, stale signature HTTP 409, selected apply, and persisted
method-only result on disposable SQLite.

### Frontend focused and workspace regression

Command:

```text
npm test -- MatrixEditorWorkspace SettingsStandardRecordSheet MatrixMethodVersionSyncPanel useMatrixMethodVersionSync --run
```

Result after B3: `4 files / 49 tests passed`, including all 44 read-only existing
`MatrixEditorWorkspace` tests.

Covered behavior includes path-save omission, explicit sheet reset, selectable Method
proposal rendering, selected-only apply, authoritative session reload, existing
autosave/Cancel/Confirm Matrix, and Matrix Step quantity behavior.

### Compatibility regression note

The read-only Matrix session/confirmed authority/Test Record command produced
`33 passed, 1 failed`. The sole failure is
`tests/integration/test_matrix_editor_session_api.py::test_matrix_editor_session_autosave_restore_confirm_and_discard`
at an existing Fee rebase `preserved_count` assertion. The dirty worktree contains
external Fee pricing/default-fill changes outside every TASK_366B candidate path.
TASK_366B does not change Fee code, and this failure is recorded as an excluded external
residual rather than repaired across lane boundaries.

## Build And Static Validation

- `py -m py_compile` passed for every touched TASK_366B Python product/test module.
- `npm run build` passed. The existing Vite chunk-size warning remains the only warning.
- Exact `MatrixMethodVersionSyncPanel` responsive regression: `1 file / 2 tests passed`.
- Responsive CSS contract scan passed for `max-width: 600px`, `overflow-x: visible`,
  `min-width: 0`, and the selection/item/status plus Current/Proposed grid areas.
- B3 frontend physical lines: component `85`, focused test `118`; both remain bounded.
- Candidate tracked-path `git diff --check` passed; output contained only repository
  LF/CRLF conversion notices.
- Explicit UTF-8 scan: `44` candidate product/test paths, `0` trailing-whitespace lines.
- UTF-8 physical-line scan passed for every new/touched bounded Python module. Largest
  bounded files:
  - `project_matrix_draft.py`: 459
  - `excel_com_readonly_tabular_gateway.py`: 459
  - `excel_workbook_gateway.py`: 433
  - `matrix_method_version_sync_service.py`: 368
  - `test_matrix_method_version_sync_service.py`: 270
  - `external_resource_service.py`: 285
  - `excel_tabular_layout.py`: 218
- The XLSX gateway was mechanically split from 561 to 433 physical lines by moving
  shared layout/probe helpers into the 218-line shared module; behavior regressions pass.
- `git diff --cached --name-only`: empty.
- `git status --short -- data`: empty. No real database or real workbook path was
  opened or modified. All SQLite and workbook fixtures were disposable pytest paths.
- Forbidden-scope scan of new orchestration/route/UI/test files found no real DB,
  public-drive, TASK_360B, Generic Test Record writer, LTR, or direct confirmed Matrix
  mutation boundary.
- Optional browser smoke was not run because the approved test environment did not
  provide a disposable backend/browser fixture, and starting the normal app could
  access operator configuration. Component/workspace tests and production build cover
  the authorized frontend boundary without that risk.

## Package Isolation

- External TASK_362A, TASK_364B/C, TASK_365B, Fee/default-fill, parser, release/dist,
  Test Points UI, and other dirty-worktree residuals remain untouched and un-staged.
- Existing unrelated hunks in shared `client.ts`, `workbench.css`, and workspace files
  were preserved; TASK_366B additions are confined to their approved contiguous/hunk
  regions.
- No source workbook write, conversion, Save, public-drive access, schema rebuild,
  Generic Test Record change, TASK_360B output change, LTR/Fee/project lifecycle
  change, stage, commit, or push occurred.

## Blocker Summary

None within TASK_366B. The single excluded Fee regression is documented above and is
not a legal TASK_366B fix target.

## Next Legal Role

Reviewer focused implementation re-gate only. Do not route QA or Integrator before
Reviewer accepts this B1/B2/B3 candidate.
