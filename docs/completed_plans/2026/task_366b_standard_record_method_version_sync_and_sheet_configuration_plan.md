# TASK_366B Standard Record Method Version Sync And Sheet Configuration Plan

Status: `complete / accepted`

Current phase: Phase 11 controlled Project Workbench / Matrix foundation.

Current role boundary: Integrator closeout. Reviewer plan and implementation re-gates,
Developer implementation, QA B3 re-gate, and Integrator isolation are complete. This
closeout does not authorize a later lane.

## 1. Discovery Decision

The legacy macro's `ConfirmSpec!Test Method` is not a ConnLab workbook output owner.
Repository evidence places the editable Method on `ProjectMatrixDraftRow.method`,
publishes it as `ConfirmedMatrixRow.method`, and projects it into confirmed Test Record
preview/generation. Therefore TASK_366B updates an editable Matrix draft and leaves the
existing `Confirm Matrix` flow as the sole authority publication gate.

The Settings resource record currently contains path/active/validation only. A sheet
name cannot be encoded safely in the path. TASK_366B therefore proposes an additive
nullable `worksheet_name` column and an additive nullable Matrix draft sync-context
column. Neither schema change is authorized by this planned-only pass.

## 2. User Workflow

### Settings

1. In `File Locations`, the Standard record Excel row keeps the existing path and
   browse control.
2. Immediately after the path control, show a compact labeled input
   `Standard record sheet` with effective default `认可标准`.
3. Path or sheet blur/Enter sends one coherent resource update, then uses the existing
   validation action. Error text remains inline and business-readable.
4. Other resource rows do not show a sheet field.

### Matrix Editor

1. The operator opens an editable Matrix draft and saves pending edits.
2. A secondary `Check method versions` action opens an inline, non-modal panel near the
   Matrix actions.
3. Preview lists row/Test Item, current Method, matched catalog code, proposed Method,
   and status. Safe changes have native selection checkboxes; blocked/no-change rows
   are read-only.
4. `Apply selected to draft` revalidates source and target fingerprints, updates only
   draft Method values, then reloads the Matrix session.
5. The operator may continue editing. `Confirm Matrix` remains separate and publishes
   all Matrix changes through the existing authority lifecycle.

This is a dense operational table, not a modal, card grid, or new top-level workspace.
At 514 px it uses stacked current/proposed text per row without horizontal overflow.

## 3. Persistence And Migration

Create
`backend/infrastructure/storage/standard_record_method_sync_schema_migration.py`
as the sole compatibility bootstrap for these two additive columns:

| Table | Column | Canonical SQLite declaration | Meaning |
| --- | --- | --- | --- |
| `external_resources` | `worksheet_name` | `VARCHAR(31) NULL`, no default, non-PK | Stored override; `NULL` means effective `认可标准` only for Standard record resources. |
| `project_matrix_draft_records` | `method_sync_context_json` | `TEXT NULL`, no default, non-PK | Latest successful draft-method sync provenance; never part of confirmed authority. |

The SQLAlchemy models use `String(31), nullable=True` and `Text, nullable=True`.
Because the generic `Base.metadata.create_all()` currently creates these non-Profile
tables before dedicated migrations run, fresh databases receive the columns from ORM
DDL and the dedicated bootstrap read-verifies them. Existing databases receive only
the missing `ALTER TABLE ... ADD COLUMN` statements.

The migration sequence is exact:

1. Open the existing initialization connection and acquire `BEGIN IMMEDIATE`.
2. Read both table definitions with `PRAGMA table_info` before any DDL. A present
   column must match declared type/affinity, nullable state, non-PK state, and no
   persisted default. A wrong existing shape raises the task-local typed
   `StandardRecordMethodSyncSchemaError(code="authority_corrupt")`.
3. Only after every present object passes preflight, add all missing columns in table
   order. Do not create a table, rebuild a table, update data, or synthesize values.
4. Re-read both columns on the same connection, inside the same transaction, and
   compare the complete canonical shape. Verification failure rolls back every DDL.
5. Commit only after final verification. Lock acquisition failure is diagnostic and
   fail-closed; a fully compatible rerun performs no DDL or data write.

`backend/infrastructure/storage/database.py` receives one import and one call directly
after generic table creation and before services can read the new fields. Tests use
only disposable SQLite files and prove fresh, both legacy columns absent, either one
column absent, malformed existing shape, injected DDL/final-verification failure,
locked writer recovery, and idempotent second startup. No fixture opens, copies, or
mutates `data/connlab.sqlite3`.

`ExternalResource.worksheet_name` and
`ProjectMatrixDraftRecord.method_sync_context_json` are optional final dataclass
fields so unrelated constructors remain source-compatible. Repository mappings retain
stored `NULL`; the effective worksheet default belongs to application/API read
projection, not persistence or migration.

## 4. Settings API Contract

Extend `ExternalResourceUpsertRequest` with
`worksheet_name: str | None = None`. The route must inspect Pydantic v2
`request.model_fields_set`; a nullable field value alone is insufficient to distinguish
omission from reset. It maps the request into an application value object:

```python
@dataclass(frozen=True, slots=True)
class WorksheetNameUpdate:
    supplied: bool
    value: str | None = None
```

`ExternalResourceService.upsert_resource()` receives this object. The default is
`WorksheetNameUpdate(supplied=False)`, preserving every existing call. Validation and
normalization occur before constructing the replacement domain record or calling
`repository.upsert()`, which makes every validation failure no-write. A task-local
`ExternalResourceWorksheetNameError(ValueError)` maps to the route's existing typed
HTTP 400 style; it never leaks a database or COM exception.

The canonical input, persistence, and response contract is:

| Resource kind | Request field state | Persistence result | Response `worksheet_name` | Outcome |
| --- | --- | --- | --- | --- |
| Standard record | omitted | preserve existing stored value; for a new row store `NULL` | stored trimmed value or effective `认可标准` when stored `NULL` | success |
| Standard record | explicit `null` | store `NULL` | effective `认可标准` | reset success |
| Standard record | explicit string that trims to empty | store `NULL` | effective `认可标准` | reset success |
| Standard record | explicit trimmed valid nonblank string | store trimmed value independently from `path` | stored trimmed value | success |
| Standard record | control characters, more than 31 chars after trim, or `[ ] : * ? / \\` | no change | previous effective value if reloaded | typed 400/422 no-write |
| Non-Standard resource | omitted | ignore/preserve unrelated resource state | `null` | success |
| Non-Standard resource | any supplied value, including `null` or blank | no change | `null` if reloaded | typed 400/422 no-write |

The UI clear action must send explicit reset semantics (`null` or whitespace-only by
the chosen component convention) and display `认可标准` after the server response.
Legacy `NULL` reloads must display `认可标准` without backfill. Omission-preserve must be
tested separately from reset so an existing custom value is not silently lost.

`ExternalResourceResponse.worksheet_name` returns the effective Standard value and
`null` for other resource types. `frontend/src/api/client.ts` mirrors the optional
request and nullable response. `ExternalResourceService.validate_resource()` and
`ExternalExcelReadService.read_standard_records()` both resolve the effective value
through one pure `effective_standard_worksheet_name()` helper; they may not duplicate
defaulting rules. No new Settings endpoint is required.

The Settings client input is
`{path: string; active: boolean; worksheet_name?: string | null}`. Path browse/blur
saves omit `worksheet_name`, preserving a custom sheet. Only sheet blur/Enter supplies
the field: trim-empty sends `null`, otherwise it sends the user's string and relies on
server canonicalization. The response always rehydrates the local draft. The compact
`Standard record sheet` input appears only on the Standard record row, immediately
below/after the path control; it shares the row's inline validation region and loading
state. Other resource rows neither render nor submit the field. No modal, nested card,
new page, or save footer is introduced.

## 5. Workbook Layout Extension

Create a bounded pure helper
`backend/infrastructure/office/excel_tabular_layout.py` and extend the two TASK_366A
tabular gateways plus `OfficeFacade` with one optional keyword-only value object:

```python
@dataclass(frozen=True, slots=True)
class ExcelTabularLayout:
    header_row_number: int
    required_header_columns: tuple[tuple[str, int], ...]
    optional_headers: tuple[str, ...] = ()
    include_row_number: bool = False
    require_unique_sheet_match: bool = False

layout: ExcelTabularLayout | None = None
```

Rules:

- `layout=None` retains the accepted first-non-empty-header behavior byte-for-byte for
  every existing `.xlsx` and `.xls` caller.
- `header_row_number` and header-column positions are one-based positive integers.
- Header-column positions are one-based and checked after the same whitespace/case
  normalization used by the gateway.
- Explicit-layout reads add internal `__row_number` metadata only for that mode;
  existing calls and DTOs remain unchanged.
- `require_unique_sheet_match=True` compares configured and workbook names with trim
  plus Unicode `casefold`; zero or more than one logical match is a typed error.
- Required headers must exist at their exact physical columns. Optional headers are
  included in result mappings only when present; their absence is not a read failure.
- The `.xlsx` explicit-layout path must use cell references (`A1`, `B2`, and so on) to
  preserve sparse physical positions. It may not compact XML cells before checking
  B2. The default path retains the existing compact behavior.
- The COM path already receives a rectangular UsedRange; it delegates the same
  normalized layout mapping without changing pre-read size limits or cleanup.
- All TASK_366A UsedRange limits, hidden read-only COM, cleanup precedence, and no-save
  rules remain unchanged.

The Standard record read call uses:

```text
sheet = configured/effective worksheet_name
header row = 2
B2 = 文 件 编 号
optional C2 = 文 件 名 称
optional D2 = 备注
data starts at row 3
```

Column B is required. C/D absence does not block method-version matching but is
represented as absent optional metadata; V1 does not fabricate values or warnings.
At least one nonblank B3+ code is required for a valid Standard resource.

The existing Standard-record API shape remains compatible: `standard_code` maps column
B, `test_item` maps column C, and `sample_description` maps column D. Equipment
calibration remains unchanged.

`ExternalExcelReadService` gains one private Standard catalog read boundary returning
effective worksheet name plus rows containing `standard_code`, optional C/D values,
`source_sheet`, and `source_row_number`. Both existing Standard-record API projection
and the method-sync service consume that boundary. Validation calls the same layout
through `OfficeFacade.probe_excel_structure()`. There is no second workbook read inside
one preview/apply operation, and no public DTO exposes `ExcelTabularLayout`.

## 6. Deterministic Parser

Create `standard_method_version_parser.py` as a pure module under 300 lines.

### Matrix method parser

- normalize Unicode hyphen variants and surrounding whitespace for matching only;
- find exactly one `364-NN` core, case-insensitive;
- recognize an existing revision only when one A-Z character is immediately adjacent
  to NN;
- retain exact original display text and spans for replacement;
- never infer a revision from unrelated words or year text.

### Catalog parser

- accept EIA or ANSI/EIA prefix, case-insensitive;
- normalize whitespace around slash/hyphens;
- capture core, immediate revision, and optional trailing four-digit year;
- retain source code and explicit worksheet row metadata;
- classify malformed/non-EIA cells instead of raising across the whole workbook.

### Candidate resolution

- group by normalized core;
- dedupe identical revision candidates;
- if one distinct revision remains, it is authoritative for proposal;
- if several distinct revisions remain, return `ambiguous` and no proposal;
- same revision duplicates select newest parsed year, then lexical source code, for
  deterministic diagnostics only;
- compare A-Z ordinal solely for `current`, `update_available`, or
  `downgrade_conflict`; V1 blocks downgrade.

The output formatter replaces/appends only the immediate revision token. It preserves
the input prefix, separators, surrounding text, and any existing year. Catalog year is
not imported because current ConnLab methods use forms such as `EIA-364-18B` without
catalog year; the year remains preview metadata.

## 7. Preview Service And DTO

Create `matrix_method_version_sync_service.py` with repository/reader ports. It must
load one project-scoped editable draft, reject superseded/stale lineage, load the
configured active Standard resource, and use the catalog reader once per operation.
The existing private `_build_signature_from_project_draft()` in
`matrix_editor_session_service.py` is renamed/exported as
`build_project_matrix_draft_payload_signature()` and all current callers are updated
mechanically. The sync service must reuse that function; no second saved-payload
signature algorithm is permitted.

Preview request:

```text
project_matrix_draft_id
expected_saved_payload_signature
```

Preview response includes:

```text
project_id, project_matrix_draft_id, base_confirmed_matrix_id
resource_id, resource_path, worksheet_name
catalog_fingerprint, target_fingerprint, preview_fingerprint, generated_at
rows[]: draft_row_id, row_order, test_item, current_method, method_core,
        matched_standard_code, catalog_revision, catalog_year,
        proposed_method, status, reason, selectable
summary counts
```

Fingerprints use canonical UTF-8 JSON and SHA-256:

- catalog: resource id/path/effective sheet plus ordered parsed source rows;
- target: draft id/base confirmed id/updated_at plus ordered row ids and methods;
- preview: version tag plus catalog and target fingerprints and ordered proposals.

Preview is read-only and performs no draft, Matrix, resource, or workbook write.
The service verifies `expected_saved_payload_signature` against the exported canonical
draft signature before catalog parsing. Not found/project mismatch is typed 404;
missing editable draft, stale base-confirmed lineage, or signature mismatch is typed
409; invalid source configuration/catalog is typed 400. Row status is one of
`current`, `update_available`, `revision_missing`, `downgrade_conflict`, `ambiguous`,
`no_method_core`, `multiple_method_cores`, `catalog_missing`, or `catalog_malformed`.
Only `update_available` and `revision_missing` are selectable.

## 8. Apply Contract

Apply request adds:

```text
preview_fingerprint
selected_draft_row_ids[]
applied_by
```

Within one API-session SQLite transaction:

1. reload the exact draft and source resource;
2. read the catalog once and rebuild the preview;
3. reject mismatch as typed HTTP 409 before mutation;
4. reject duplicate, unknown, unselectable, downgrade, ambiguous, or unchanged row ids;
5. build the exact post-apply ordered Method set, its fingerprint, and the canonical
   audit JSON in memory without writing;
6. call a new repository command that conditionally claims the root by
   `project_matrix_draft_id`, prior `updated_at`, editable status, and base-confirmed
   lineage, then updates only selected row `method` columns using row id plus expected
   old value predicates;
7. require exactly one root and one row update per selection; any zero/unexpected row
   count raises the same typed 409 and rolls back the entire transaction;
8. set root `updated_at` and the precomputed `method_sync_context_json` in the same
   root CAS, reload the aggregate, verify the persisted post-apply Method fingerprint,
   calculate the canonical saved-payload signature, and return it through the existing
   API-session commit boundary.

The repository must not call the existing `replace_snapshot()`: that method deletes
and recreates groups, rows, cells, and Step quantities and is too broad for this
method-only command. The new repository operation preserves row ids and every
non-method column and never touches groups, cells, Step quantities, scheduling fields,
or confirmed tables.

The audit JSON schema is versioned `matrix-method-sync:v1` and contains sorted keys:
`resource_id`, normalized resource path, effective worksheet, catalog/target/preview
fingerprints, `applied_by`, UTC `applied_at`, pre-apply saved signature, selected rows
(`draft_row_id`, `row_order`, old/new method, source row/code), and
`post_apply_method_fingerprint`. It contains no workbook contents beyond selected
catalog codes and no operator credentials.

No operation creates or confirms a Matrix. If no editable draft exists, the UI directs
the operator to open/create one through existing Matrix revision behavior. Existing
autosave, Cancel, stale-signature, and Confirm Matrix contracts remain authoritative.

The route module owns only Pydantic conversion and typed mapping. `preview` accepts no
actor and is zero-write. `apply` requires nonblank `applied_by`, a nonempty deduplicated
selection bounded by the number of draft rows, and the three fingerprints/tokens. The
frontend always reloads the Matrix session after success and discards the prior preview;
on 409 it keeps the panel visible with an explicit `Reload Matrix and check again`
action, never auto-applies stale proposals.

## 9. Audit And Downstream Boundary

The durable audit is bounded to:

- old/new draft Method values in `method_sync_context_json`;
- source resource id, effective sheet, catalog fingerprint, actor, and timestamp;
- the existing confirmed Matrix version's `project_matrix_draft_id` link;
- immutable old and new `ConfirmedMatrixRow.method` values after confirmation.

If later manual edits change the draft Method fingerprint, audit readers can identify
the sync context as modified-after-sync. This task does not add an audit UI or change
confirmed Matrix schema.

Generic Test Record continues to read active confirmed Matrix rows. Before Matrix
confirmation it stays unchanged; after confirmation it naturally reflects the new
Method values. TASK_360B/TASK_361D workbooks, Fee, Report, and other outputs are locked.

## 10. File-Level TDD Sequence

1. `tests/unit/test_standard_record_method_sync_schema_migration.py`: write red tests
   for fresh/read-verify, both partial states, wrong shape, rollback, lock recovery,
   and idempotency. Implement the new migration, then add only the ORM/dataclass/
   repository field mappings and the one `database.py` import/call.
2. `tests/unit/test_standard_record_sheet_configuration.py` and
   `tests/integration/test_standard_record_sheet_configuration_api.py`: freeze the
   complete omission/null/blank/valid/invalid/non-Standard matrix and repository
   no-write behavior. Implement `WorksheetNameUpdate`, the effective-value helper,
   route field-presence conversion, and response/client types.
3. `tests/unit/test_excel_standard_record_layout_xlsx.py` and
   `tests/unit/test_excel_standard_record_layout_com.py`: red-test title row, sparse
   B2 position, optional C/D, unique configured sheet, row metadata, default-call
   parity, COM limits, and no-save cleanup. Implement `ExcelTabularLayout`, then add
   only optional delegation parameters to the facade/gateways.
4. `tests/unit/test_standard_record_catalog_read_service.py` and
   `tests/integration/test_external_excel_standard_layout_api.py`: prove validation
   and read share the effective sheet/layout, require a nonblank B3+ code, preserve
   public Standard row shape, and leave Equipment behavior unchanged.
5. `tests/unit/test_standard_method_version_parser.py`: implement the pure parser only
   after all positive, negative, duplicate, ambiguous, year, downgrade, multiple-core,
   and row-state-reset tests are red.
6. `tests/unit/test_matrix_method_version_sync_service.py`: implement preview and
   apply orchestration after zero-write, exact signature reuse, source/target
   fingerprints, selected-only update, root/row CAS conflicts, audit JSON, and full
   non-method preservation tests are red.
7. `tests/integration/test_matrix_method_version_sync_api.py`: use temporary SQLite
   and disposable `.xlsx`/fake catalog boundaries to prove typed 400/404/409, preview
   zero-write, apply transaction rollback, post-apply signature, and no confirmed
   Matrix mutation.
8. Create bounded Settings tests
   `frontend/src/features/settings/SettingsStandardRecordSheet.test.tsx`; implement the
   compact field and typed client request while leaving existing oversized/shared
   tests read-only.
9. Create `MatrixMethodVersionSyncPanel.test.tsx` and
   `useMatrixMethodVersionSync.test.tsx`; implement declarative panel/hook, then add one
   import/model/composition hunk to `MatrixEditorWorkspace.tsx`. The hook owns async
   preview/apply/error/stale/reload state; the panel owns no raw API call.
10. Run read-only existing Matrix session, confirmed authority, Generic Test Record,
    External Resource, Equipment, TASK_366A gateway/lifecycle, and frontend workspace
    regressions proving the publication and compatibility boundaries.

## 11. Exact May Touch And Package Isolation

### Backend product

- `backend/domain/models.py`: append nullable `worksheet_name` only.
- `backend/domain/project_matrix_draft_models.py`: append nullable sync context only.
- `backend/infrastructure/storage/models.py`: one `String(31)` column.
- `backend/infrastructure/storage/models_project_matrix_draft.py`: one `Text` column.
- `backend/infrastructure/storage/repositories/external_resources.py`: field mapping.
- `backend/infrastructure/storage/repositories/project_matrix_draft.py`: context mapping
  plus one method-only CAS operation; existing `replace_snapshot()` behavior unchanged.
- new `backend/infrastructure/storage/standard_record_method_sync_schema_migration.py`.
- `backend/infrastructure/storage/database.py`: one import/call cluster only.
- new `backend/infrastructure/office/excel_tabular_layout.py`.
- `backend/infrastructure/office/excel_workbook_gateway.py` and
  `excel_com_readonly_tabular_gateway.py`: optional explicit-layout delegation only.
- `backend/infrastructure/office/office_facade.py`: optional layout passthrough only.
- `backend/application/external_resource_service.py`: worksheet command/default/
  validation and Standard probe arguments.
- `backend/application/external_excel_read_service.py`: private Standard catalog read
  projection; Equipment path unchanged.
- new `backend/modules/test_plan/standard_method_version_parser.py`.
- new `backend/application/matrix_method_version_sync_service.py`.
- `backend/application/matrix_editor_session_service.py`: mechanically export/rename
  the existing canonical draft-signature helper and update its current call sites only.
- `backend/api/routes_external_resources.py`: request field-presence/response mapping.
- new `backend/api/routes_matrix_method_version_sync.py`.
- `backend/api/dependencies.py`: one service provider cluster only.
- `backend/api/main.py`: one route registration only.

`backend/api/routes_external_excel_resources.py`,
`backend/api/routes_matrix_editor_session.py`, and
`backend/application/project_matrix_draft_persistence_service.py` are read-only
regression dependencies. The refined design does not thread sync context through the
Matrix session DTO and does not use full-snapshot replacement.

### Frontend product

- `frontend/src/api/client.ts`: contiguous worksheet and sync DTO/client additions.
- `frontend/src/pages/SettingsPage.tsx`: pass optional worksheet update and rehydrate.
- `frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`: Standard-only
  compact field.
- `frontend/src/features/settings/settingsSelectors.ts`: effective worksheet row value.
- new `frontend/src/features/matrix-editor/MatrixMethodVersionSyncPanel.tsx`.
- new `frontend/src/features/matrix-editor/useMatrixMethodVersionSync.ts`.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`: import, hook inputs,
  panel placement, and existing session reload callback only.
- `frontend/src/workbench.css`: selectors specific to the Settings field and sync panel.

### Focused tests and governance

Only the bounded new test modules listed in section 10 plus narrowly necessary
existing TASK_366A/default-layout regression assertions may change. Existing oversized
files such as `test_project_matrix_draft_repository.py` (780),
`test_project_matrix_draft_persistence_service.py` (509),
`test_matrix_editor_session_service.py` (1339),
`test_matrix_editor_session_api.py` (1107), and
`MatrixEditorWorkspace.test.tsx` (1911) are read-only regression dependencies.
Governance changes are limited to TASK_366B task/plan/evidence and the exact board hunk
only after a future authorized implementation gate.

All new Python/TypeScript modules stay below 500 physical UTF-8 lines; product helpers
target below 300. Existing oversized product files receive only the narrow hunks above:
`database.py`, `models.py`, `api/dependencies.py`,
`matrix_editor_session_service.py`, `MatrixEditorWorkspace.tsx`, and `client.ts`.
`excel_workbook_gateway.py` is currently 435 lines and the COM gateway 366 lines, so
shared layout logic must live in the new helper and both gateway files must remain
below 500 after implementation.

## 12. Validation Gate

Future mandatory validation:

- parser unit suite covering all positive/negative/version-state cases;
- migration/repository/API Settings suite on new, legacy, repeated, malformed temporary
  SQLite databases, including worksheet reset, legacy-null effective default,
  omission-preserve, invalid no-write, and non-Standard supplied-field rejection;
- `.xlsx` disposable fixture and fake-COM `.xls` parity suite with title/header/data
  rows and exact B-column validation;
- full TASK_366A fake-COM, Office lifecycle, XLSX, Equipment, and no-write regressions;
- sync service/API tests for zero-write preview, stale 409, selected-only apply,
  audit context, and no partial write;
- Matrix session/confirmed authority/Test Record regressions;
- focused frontend Settings and Matrix panel tests. Settings tests must cover
  clear/reset to `认可标准`, omission-preserve on save/update, invalid sheet names, and
  non-Standard resource field rejection/visibility;
- `npm run build`, Python compile, UTF-8 line counts, diff/trailing, forbidden token,
  exact whitelist, staging-empty, and no-real-mutation scans;
- optional browser smoke at desktop and 514 px using disposable API data only.

The implementation evidence must record exact pytest/vitest node paths, not only suite
totals. Physical line count uses
`Path.read_text(encoding="utf-8").splitlines()` so blank lines are retained. Static
checks include `py -m py_compile` for every touched Python product/test module,
`npm run build`, `git diff --check`, an explicit UTF-8 trailing-whitespace scan, an
exact changed-path whitelist, forbidden-scope token/path scan, `git diff --cached`
empty, and a no-real-data/path scan proving no access or mutation under `data/**`,
public-drive paths, discovery attachments, or generated workbook roots.

Browser smoke uses disposable API state only:

- desktop: Standard row displays path then `Standard record sheet`; custom save,
  clear/reset, reload, and inline invalid state are legible;
- 514 px: no horizontal page overflow; the sync table stacks current/proposed method,
  status remains adjacent to its row, and actions remain reachable without a bottom
  dock obstruction;
- keyboard: sheet input Enter saves, row selection is labeled, stale reload action is
  focusable, and apply remains disabled until at least one safe proposal is selected;
- console remains clean. No smoke opens a real workbook.

No deterministic test opens the discovery attachment or a public-drive workbook. Real
Excel COM is not required beyond the already accepted TASK_366A behavior; if repeated,
it is temp-only and read-only.

## 13. Merge Gate And Rollback

Merge requires Developer evidence, independent Reviewer pass, QA package/browser
evidence, explicit user acceptance, and Integrator hunk isolation. Backend/schema,
frontend, and shared Office changes are serialized in one lane; no parallel product
implementation is proposed.

Rollback removes route/UI/service callers while leaving nullable columns harmless.
Existing accepted Matrix Method values remain valid. No rollback rewrites or deletes
resource, draft, confirmed Matrix, or workbook data. `.xlsx` and `.xls` default calls
continue through their TASK_366A behavior.

The package boundary excludes every pre-existing dirty path. Integrator staging must
use an explicit TASK_366B whitelist and inspect oversized-file hunks individually.
Neither Developer nor Reviewer stages, commits, pushes, or cleans external residuals.

## 14. Definition Of Ready

The accepted package preserves the planned authority ownership, physical schema shapes,
field-presence semantics, explicit Excel layout, parser/candidate rules, shared saved
signature, method-only CAS apply, typed API behavior, UI/model boundaries, exact May
Touch, bounded tests, rollback, and package isolation are implementation-ready for
independent review.

The accepted implementation is limited to the frozen TASK_366B scope: worksheet-name
field-presence/reset/default behavior, additive migration, explicit `.xlsx`/COM Chinese
catalog layout, canonical saved signature, method-only root+row CAS, typed no-write
`400/404/409`, preview zero-write, selected apply to editable Matrix draft, existing
Confirm Matrix publication, focused bounded tests, and existing May Touch/locks.

## 15. Next Legal Role

User/Orchestrator only. No follow-on product lane is activated by this closeout.
