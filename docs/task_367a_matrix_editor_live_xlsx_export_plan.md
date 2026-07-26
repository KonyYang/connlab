# TASK_367A Matrix Editor Live XLSX Export Plan

Date: 2026-07-26
Status: implementation authorized / pending controlled docs-only governance checkpoint
Task: `TASK_367A_MATRIX_EDITOR_LIVE_XLSX_EXPORT`
Lane: `matrix-editor-live-xlsx-export`
Implementation authorization: authorized; execution blocked pending governance checkpoint and clean-primary gate

## 1. Purpose

Add a compact Matrix Editor action that exports a click-time snapshot of the current unconfirmed
UI state as a macro-free `.xlsx`, using the observed Matrix workbook structure and without
mutating Matrix/session/project state or a source workbook.

## 2. Discovery Gate

### User-confirmed

- Add `导出 Matrix` beside `Import Matrix`.
- No Confirm Matrix prerequisite.
- Export only checked Groups, matching `Test record`.
- Preserve a blank-valued Fee row.
- Map Samples Quantity to `Sample size` and Test Days to `Time`.
- Match the read-only workbook at
  `D:\TestFlowManager\Projects\DL-2025-02-054 EK500 Connector Qualification Testing\matrix.xlsx`.
- Cover desktop and 514 px without overlap or overflow.
- Use the same browser Blob download mechanism as Test Record; do not add native Save As.
- Export `Time` exactly as Matrix Editor displays each checked Group's `Test Days`.
- Include only test rows that contain steps in at least one checked Group.

### Repository-confirmed

- `MatrixEditorWorkspace.tsx` owns current rows, Groups, samples, and schedule calculation.
- `buildMatrixEditorTestRecordDraftRequest()` already projects current UI state and checked
  Groups without Confirm Matrix.
- `showSelectedGroupsOnly` is rendering only.
- The current Blob download and API client parse `Content-Disposition`.
- Autosave/CAS is a persistence boundary. A read-only click snapshot needs no save generation or
  CAS token.
- Desktop path picking supports open/folder dialogs but not Save As.
- There is no Matrix XLSX export path.
- Oversized current surfaces are workspace 4093, workspace test 1934, client 4600, CSS 9455, and
  dependencies 2248 blank-inclusive lines.

### Reference-workbook-confirmed

Artifact-tool read-only inspection found one `Sheet`, range `A1:G5`, no formulas/drawings/merges,
the seven-column one-Group header, one example test row, and fixed `Sample size`, `Time`, `Fee`
rows. Header and A labels use gray `#CCCCCC`; cells use Calibri 11, centered/wrapped text, thin
borders, and row height 15.

The file was not saved, converted, copied, or modified. It is a design reference only.

### Planner inference

- The narrow architecture is an in-memory backend XLSX writer plus existing-style browser
  download.
- Native Save As adds a desktop bridge and materially expands scope.
- The generator should encode the observed layout rather than require the external workbook.
- New bounded projection/hook/button modules keep the 4093-line workspace to minimal wiring.
- New bounded API composition avoids `backend/api/dependencies.py`.

### User decision reconciliation

- Delivery is the existing browser Blob download path.
- For each checked Group, `Time` is exactly
  ```${formatPlanningDays(scheduleCalculation.groupDays[group.id] ?? 0)} d```.
  Integers have no decimals; non-integers have at most two decimals with trailing zeros removed;
  blank/no contributing Day values export as `0 d`.
- Backend treats `Time` as display text and does not parse, convert, round, or recompute it.
- Include only `isSampleRow === false` rows with a nonblank step cell in at least one checked
  Group after the existing selected-Group step-format/sequence gate passes.
- Unchecked Groups, sample/information rows, and rows unrelated to checked Groups are omitted.
- `Show selected groups only` remains view-only.

### Reviewer plan gate and User routing

- Reviewer plan gate passed on 2026-07-26.
- The User approved Developer docs-only planning-first.
- Product/test implementation, implementation worktree creation, staging, commit, and push are
  not authorized by that approval.

### Mandatory planning-first closure before implementation readiness

Developer planning-first must freeze:

1. exact request DTO field names/types/nesting and numeric caps for Groups, rows, cells, and
   strings; oversize and zero qualifying rows are typed `422` with no workbook bytes;
2. filename derivation from read-only `deriveProjectReference()` using latest LTR, `project_no`,
   then `TMP-<first 8 project-id characters uppercased>`, plus exact Windows-safe sanitization
   and the frozen timestamped suffix;
3. export disabled reasons for no Group, no qualifying row, busy, step-gate failure, and
   lifecycle read-only; lifecycle read-only uses `lifecycleReadonlyView.message`, sends no
   request, and autosave/CAS is not an enablement dependency;
4. bounded RED/GREEN nodes proving caps, zero-row `422`, filename fallback/sanitization, and
   lifecycle-readonly no-request behavior.

The exact contracts below close every mandatory readiness detail.

## 3. Target Data Flow

```text
Matrix Editor local state at click
  -> pure checked-Group export projection
  -> POST typed current-UI snapshot
  -> application validation/projection
  -> in-memory openpyxl writer
  -> XLSX bytes + Content-Disposition
  -> browser Blob download
```

No leg reads or writes Matrix persistence, Confirmed Matrix, project outputs, Settings, or
external workbooks.

## 3.1 Exact HTTP And DTO Contract

The future endpoint is:

```text
POST /api/projects/{project_id}/matrix-editor/live-xlsx-export
Content-Type: application/json
Response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

The TypeScript request types and Pydantic request models must use the same snake-case JSON
shape:

```text
MatrixEditorLiveXlsxExportRequest
  source: Literal["matrix_editor_current_ui_state"]
  project_reference: string
  groups: MatrixEditorLiveXlsxExportGroupRequest[]
  rows: MatrixEditorLiveXlsxExportRowRequest[]

MatrixEditorLiveXlsxExportGroupRequest
  group_id: string
  group_key: string
  group_label: string
  sample_size: string
  time_display: string

MatrixEditorLiveXlsxExportRowRequest
  row_id: string
  test_item: string
  section: string
  test_method: string
  condition: string
  requirement: string
  cells: MatrixEditorLiveXlsxExportCellRequest[]

MatrixEditorLiveXlsxExportCellRequest
  group_id: string
  step_text: string
```

`project_id` remains the route parameter and is not duplicated in the body. Notes and Fee values
are not request fields: Notes is an intentionally blank derived column and Fee is an
intentionally blank derived row. The frontend supplies `group_label` after the approved
trimmed-label/current-key fallback. Each row's `cells` must contain exactly one entry for every
request Group, in the same order. This rectangular list avoids dynamic JSON object keys and lets
the application reject missing, extra, reordered, or duplicate Group identities.

Exact structural limits, enforced again by the application before gateway invocation:

| Value | Contract |
|---|---:|
| Groups | `1..64` |
| qualifying export rows | `1..512` after semantic validation |
| Group cells | `sum(len(row.cells)) <= 16,384` |
| `source` | exact literal only |
| `project_reference` | trimmed nonempty, max 255 code points |
| `group_id`, `group_key`, `row_id`, cell `group_id` | trimmed nonempty, max 128 |
| `group_label` | trimmed nonempty, max 255 |
| `sample_size` | max 255; blank allowed |
| `time_display` | max 32; blank is not generated by the frontend but the backend does not parse it |
| `test_item`, `section`, `test_method`, `condition`, `requirement` | max 2,048 each; blank allowed |
| `step_text` | max 255; blank allowed |

Group ids, Group keys, and row ids must be unique. Every row must contain at least one
nonblank `step_text`; otherwise it is not a qualifying export row. An empty `rows` list, a row
without a selected-Group step, a non-rectangular cell list, duplicate identity, or any cap
violation is rejected before workbook construction.

Pydantic type failures retain FastAPI's standard typed `422`. Application shape/bounds failures
map to:

```json
{
  "detail": {
    "code": "matrix_editor_live_xlsx_export_blocked",
    "message": "Actionable validation message."
  }
}
```

with HTTP `422`. The application service completes every validation and constructs an immutable
projection before calling `gateway.render()`. Tests use a spy gateway and require zero calls and
zero response bytes for all rejected requests. An unexpected writer failure maps to HTTP `500`
with code `matrix_editor_live_xlsx_export_failed`; it never returns partial bytes or writes a
file.

The success response is raw XLSX bytes. `Content-Disposition` is:

```text
attachment; filename="Matrix-Draft.xlsx"; filename*=UTF-8''<percent-encoded-real-name>
```

The existing client prioritizes `filename*`, so non-ASCII project references remain intact while
the ASCII fallback is header-safe.

## 3.2 Project Reference And Filename Contract

The click projection imports the existing read-only `deriveProjectReference()` and calls it with:

```text
latestLtr = model.latestLtr
projectNo = model.project?.project_no
projectId = model.project?.project_id ?? route projectId
```

Its precedence remains exactly latest LTR, `project_no`, then
`TMP-<first 8 project-id characters uppercased>`. `projectIdentity.ts` remains locked and no
second fallback is introduced.

The backend owns the final filename and an injectable local clock. It sanitizes the supplied
project reference as one Windows filename segment:

1. trim surrounding Unicode whitespace;
2. replace each run of `< > : " / \ | ? *` or U+0000..U+001F with one `_`;
3. remove trailing spaces and periods;
4. prefix `_` when the remaining basename is a case-insensitive Windows device name
   (`CON`, `PRN`, `AUX`, `NUL`, `COM1..COM9`, or `LPT1..LPT9`);
5. keep at most 120 code points, then remove trailing spaces/periods again;
6. use deterministic `Project` if nothing remains.

The exact filename is:

```text
<safe project reference> Matrix Draft <local YYYYMMDDHHmmss>.xlsx
```

The 120-code-point segment limit keeps the final Windows component comfortably below 255
characters. Sanitization changes only the download filename; it does not mutate the request,
project identity, Matrix state, or workbook cells.

## 3.3 Export Availability Contract

The pure frontend projection module also owns a small availability function. Its first matching
reason wins:

1. lifecycle read-only: exact `lifecycleReadonlyView.message`;
2. hook busy: `Matrix export is in progress.`;
3. no checked Group: `Select at least one Group to export.`;
4. selected-Group step-format/sequence failure: the existing `stepTokenErrorMessage`, or
   `Fix Matrix step numbering before exporting.` when the detailed message is empty;
5. no qualifying non-sample row: `Add at least one step to a selected Group before exporting.`;
6. otherwise no disabled reason.

The native button is disabled whenever a reason exists and exposes that reason through its
title/adjacent status contract. The click handler rechecks availability before building the
snapshot, so a lifecycle transition cannot dispatch a request. The lifecycle test passes an
actual `lifecycleReadonlyView.message` value and proves the export client is not called.

`saveState`, `savedEditorDraftId`, autosave timers, saved signatures, draft generations, and CAS
tokens are deliberately absent from availability inputs. Busy prevents double activation;
after success or failure, a retry captures a new current-render snapshot.

## 4. Snapshot And Concurrency Contract

- The frontend builds the payload synchronously from the current render when the command starts.
- It contains checked Groups in current order, current row/cell text, current sample expressions,
  and the exact current checked-Group `Test Days` display strings.
- The row projection reuses the existing selected-Group step validity gate, then includes only
  non-sample rows with a nonblank step cell in at least one checked Group. It does not implement
  a second step parser.
- It does not wait for the 800 ms autosave or call a save endpoint.
- The server treats the payload as immutable.
- A later edit or autosave cannot alter the output.
- Because this is zero-write, source fingerprint, draft generation, saved signature, confirmed
  revision, and CAS are not preconditions.
- Double-click is prevented by local busy state; retry takes a new snapshot.

## 5. Workbook Layout Contract

For `N` checked Groups:

```text
A Test Item
B Section
C Test Method
D Condition
E Requirement
F.. checked Group labels
last Notes
```

After data rows: `Sample size`, `Time`, `Fee`.

- `Sample size` uses each checked Group's current sample expression.
- `Time` is the exact current page display string
  ```${formatPlanningDays(scheduleCalculation.groupDays[group.id] ?? 0)} d```; examples include
  `0 d`, `2 d`, and `2.5 d`.
- The backend writes `Time` as supplied display text and does not parse or recompute Day values.

Formatting follows the observed reference:

- one `Sheet`;
- header and A labels gray `#CCCCCC`;
- white value cells;
- Calibri 11, center alignment, wrap text, thin borders;
- widths A 20, B 8, D/E 20, other columns default;
- row height 15;
- no formulas, macros, merges, drawings, links, hidden sheets, or defined names.

All non-label Fee cells are `None`, not `0`, `""`, formulas, or cached values.

## 6. Error Contract

- no checked Group: typed `422`, no download;
- invalid source discriminator, duplicate Group identity, oversized payload, or malformed shape:
  typed `422`, no output;
- selected-Group step-format or sequence errors keep the command unavailable under the existing
  Matrix Editor gate, matching Test Record; the export backend has no Day parser;
- workbook failure: actionable typed error, no partial download;
- frontend uses concise status/error copy and re-enables retry;
- lifecycle read-only behavior stays aligned with existing target actions unless explicitly
  re-scoped.

No error path saves a draft, publishes Matrix, registers output, or writes a file.

The availability reason ordering and exact copy are frozen in section 3.3. The backend remains
authoritative for request caps and semantic shape even when a crafted client bypasses the
frontend gate.

## 7. File-Level Design

### Frontend

1. `matrixEditorXlsxExportProjection.ts`: structural input types and pure checked-Group
   row/sample/display-time/Fee projection using the existing gate-backed row scope.
2. `useMatrixEditorXlsxExport.ts`: request lifecycle, Blob URL, filename, revoke, busy/error.
3. `MatrixEditorXlsxExportButton.tsx`: accessible command/status only.
4. `MatrixEditorWorkspace.tsx`: imports, current-state inputs, adjacent component wiring only.
5. `client.ts`: typed request and `requestBlobResponse` wrapper only.
6. `workbench.css`: optional exact responsive hunk only if controlled smoke proves necessary.

### Backend

1. `matrix_editor_live_xlsx_export_service.py`: validate source/bounds/identities and return an
   immutable workbook projection.
2. `matrix_editor_live_xlsx_workbook_gateway.py`: create a fresh workbook in `BytesIO`, apply the
   frozen layout, and return bytes.
3. `routes_matrix_editor_live_xlsx_export.py`: typed DTO, error mapping, XLSX media type, safe
   `Content-Disposition`.
4. `dependencies_matrix_editor_live_xlsx_export.py`: bounded stateless composition.
5. `main.py`: exact route registration.

## 8. Exact Scope And Budgets

| Path | Ownership | Budget |
|---|---|---:|
| `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` | exact wiring | minimal hunk, no inline business logic |
| `frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.ts` | new pure projection | <=220 |
| `frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.ts` | new hook | <=180 |
| `frontend/src/features/matrix-editor/MatrixEditorXlsxExportButton.tsx` | new command UI | <=100 |
| `frontend/src/api/client.ts` | exact DTO/download hunk | no whole-file stage |
| `frontend/src/workbench.css` | optional exact responsive hunk | <=20 additions |
| `backend/api/main.py` | exact router hunk | final <250 |
| `backend/api/routes_matrix_editor_live_xlsx_export.py` | new route/DTO | <=220 |
| `backend/api/dependencies_matrix_editor_live_xlsx_export.py` | new composition | <=100 |
| `backend/application/matrix_editor_live_xlsx_export_service.py` | new projection | <=300 |
| `backend/infrastructure/office/matrix_editor_live_xlsx_workbook_gateway.py` | new writer | <=300 |
| six new bounded test modules | exact feature coverage | each <=350; tighter budgets in task |

All Python candidates must remain below 500 blank-inclusive lines. Existing oversized frontend
files are mixed and exact-hunk only. The 1934-line workspace test is read-only.

## 9. Test-First Plan

### RED

- `test_projection_uses_ltr_then_project_no_then_tmp_reference` fails because the projection and
  exact `deriveProjectReference()` wiring do not exist;
- `test_projection_keeps_checked_groups_and_only_qualifying_non_sample_rows` fails because the
  selected rectangular snapshot does not exist;
- `test_projection_preserves_exact_sample_and_time_display_text` fails because current sample
  and page-formatted Time text are not projected;
- `test_service_rejects_group_row_cell_and_string_caps_before_gateway` fails because limits and
  the pre-gateway validation boundary do not exist;
- `test_service_rejects_zero_or_nonqualifying_rows_before_gateway` fails because zero-row
  semantic validation does not exist;
- `test_service_rejects_duplicate_or_nonrectangular_identities_before_gateway` fails because
  identity/shape validation does not exist;
- `test_service_builds_windows_safe_timestamped_filename` fails because sanitization and the
  injected clock do not exist;
- `test_workbook_gateway_writes_reference_layout_and_true_blank_fee_cells` fails because the
  in-memory writer does not exist;
- `test_live_xlsx_api_returns_typed_422_without_gateway_for_empty_and_oversize_payloads` fails
  because the route and typed error mapping do not exist;
- `test_live_xlsx_api_returns_bytes_and_utf8_content_disposition_without_writes` fails because
  the byte response does not exist;
- `test_export_hook_downloads_one_click_snapshot_and_revokes_blob_url` and
  `test_export_hook_keeps_busy_error_and_retry_state` fail because the hook does not exist;
- `test_export_button_uses_lifecycle_reason_and_dispatches_no_request` and
  `test_export_button_combines_busy_group_step_and_row_gates` fail because the command and
  disabled-reason contract do not exist.

### GREEN

Implement only frozen modules and minimal wiring. Validate checked-Group ordering, live unsaved
values, only checked-Group rows containing steps, exact `Test Days` display strings including
`0 d`, dynamic Group columns, exact styles, blank Fee cells, no file/DB/session/confirm write,
download lifecycle, retry behavior, all numeric/string caps, zero gateway calls on `422`, and
the exact lifecycle-readonly no-request gate.

### Regression

```text
cd frontend
npm test -- --run matrixEditorXlsxExport MatrixEditorWorkspace --watch=false
npm run build
```

```text
py -m pytest tests/unit/test_matrix_editor_live_xlsx_export_service.py tests/unit/test_matrix_editor_live_xlsx_workbook_gateway.py tests/integration/test_matrix_editor_live_xlsx_export_api.py -q
py -m pytest tests/integration/test_matrix_editor_test_record_generation_api.py tests/integration/test_matrix_editor_session_api.py -q
py -m py_compile <exact new backend modules>
```

The existing Matrix Editor workspace test is rerun read-only; no assertion migration is allowed.

Exact test ownership and tighter blank-inclusive budgets:

| Test module | Required scope | Budget |
|---|---|---:|
| `tests/unit/test_matrix_editor_live_xlsx_export_service.py` | caps, identities, filename, pre-gateway rejection | <=300 |
| `tests/unit/test_matrix_editor_live_xlsx_workbook_gateway.py` | bytes, layout, styles, true blank Fee, forbidden workbook features | <=300 |
| `tests/integration/test_matrix_editor_live_xlsx_export_api.py` | success headers/bytes, typed 422, spy gateway, no writes | <=350 |
| `matrixEditorXlsxExportProjection.test.ts` | selected scope, exact text, project reference, local cap errors | <=280 |
| `useMatrixEditorXlsxExport.test.tsx` | click snapshot, one request, Blob lifecycle, busy/retry | <=250 |
| `MatrixEditorXlsxExportButton.test.tsx` | native command, exact disabled reasons, lifecycle no-request | <=220 |

The backend tests use only `BytesIO`, an injected fixed clock, and fake/spy gateways. API tests
override the bounded route dependency and snapshot DB/file/output directories before and after.
They do not initialize or read the operator database.

## 10. Browser / QA Gate

Use a controlled disposable API/UI harness, not operator project data:

- desktop and effective 514 px;
- button directly beside Import Matrix;
- Tab focus, Enter/Space exactly once, busy disabled, retry after failure;
- long identity/source names and three actions without overlap or horizontal overflow;
- checked/unchecked Groups prove selected-only output;
- rows without a step in any checked Group are absent while view filtering does not change scope;
- integer, fractional, and no-contributing-Day cases preserve the page text exactly;
- filename/media type/workbook content inspected;
- no console error and no save/confirm request caused by export.

## 11. Locked Paths

Locked:

- Matrix persistence, autosave, CAS, source lineage, revision, Confirm Matrix, import;
- Test Record product paths;
- schema/database/migrations;
- Settings, external resource configuration, desktop path picker, PyWebView, and native Save As;
- Fee, Point Profile, Measurement Plan, LTR, project output, parser, release packaging;
- real DB/files/workbooks and all external residuals.

## 12. Worktree And Gate Sequence

Developer planning-first, Planner reconciliation, Reviewer implementation-readiness, and
explicit User product/test implementation approval are complete:

1. assemble a controlled local docs-only governance checkpoint;
2. verify the primary worktree and index are clean;
3. only then create/reuse `lane/task-367a-matrix-editor-live-xlsx-export`;
4. create sibling worktree
   `D:\PythonProject\connlab-task-367a-matrix-editor-live-xlsx-export`;
5. Developer implements TDD and creates a clean lane checkpoint;
6. Reviewer reviews base-to-lane HEAD;
7. QA validates the reviewed clean commit in a disposable harness;
8. Integrator accepts an exact whitelist and records residual ownership.

No implementation worktree is created now.

## 13. Rollback

Delete only the new bounded modules/tests and remove exact route/client/workspace/CSS wiring.
There is no data or artifact cleanup.

## 14. Stop Point

Reviewer implementation-readiness passed and the User authorized product/test implementation.
Route only the controlled docs-only governance checkpoint package gate. Product/test edits,
implementation worktree creation, QA, and product integration remain blocked until that local
checkpoint makes the primary worktree/index clean. Remote push remains unauthorized.
