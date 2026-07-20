# TASK_366B Reviewer Plan Gate

Date: 2026-07-20

Role: Reviewer

Lane: `standard-record-method-version-sync-and-sheet-configuration`

Status: `reviewer_blocked / Planner docs-only fix required`

Implementation authorization: none.

## Scope Reviewed

- `AGENTS.md`, task board, task, plan, and Planner discovery evidence.
- Accepted TASK_366A baseline and the current external-resource API/service/repository
  chain, Office facade/tabular gateways, Matrix draft/confirmed authority boundary, and
  current Matrix/Test Record projections.
- ConnLab product, design, and frontend architecture rules for the proposed Settings
  field and inline Matrix panel.

No product or test code was modified. No database, public-drive workbook, discovery
attachment, or other real operator file was accessed.

## Blocking Finding

### B1: `worksheet_name` blank/null semantics contradict the frozen request contract

The delegated contract freezes `null` and blank sheet input as resolving to the
effective default `认可标准`. However, the current task's Worksheet Configuration
Contract and plan section 4 specify that an explicit blank sheet name is rejected with
a typed validation error and no write. That leaves the observable Settings behavior
undetermined: clearing the new input could either reset to the default sheet or fail,
and the API/persistence/preview paths would implement different meanings.

This is not a presentation-only decision. The current upsert API requires a path and
does not have field-presence semantics for a second persisted field, so implementation
needs one exact distinction among omitted, explicit `null`, whitespace-only input, and
trimmed nonblank input before DTO, service, repository, UI blur handling, and test
expectations can be safely designed.

**Required Planner docs-only fix:** align task, plan, Planner evidence, and board
summary to one canonical normalization table that honors the frozen request contract:

- omitted field preserves an existing persisted value;
- legacy/persisted `NULL`, explicit `null`, and whitespace-only Standard-record input
  resolve to effective `认可标准`, with an explicit decision whether a reset stores
  `NULL` or the default text;
- trimmed nonblank valid input is persisted independently from the path;
- invalid control characters, length, and Excel-invalid characters remain typed
  no-write failures; and
- non-Standard resource types define whether omission is ignored and supplied values,
  including `null`, are rejected.

The fix must also freeze response semantics (`worksheet_name` effective value versus
stored nullable value) and cover clear/reset, legacy-null reload, omission-preserve,
and explicit-invalid API/UI cases. No schema, product, or test implementation is
authorized in this fix pass.

## Confirmed Plan Boundaries

- The proposed authority mapping is correct: sync may modify only the editable
  `ProjectMatrixDraftRow.method`; existing `Confirm Matrix` remains the sole
  publication action. Generic Test Record and TASK_360B remain confirmed projections
  and are not sync write targets.
- A separately persisted nullable sheet field and a draft-scoped source audit context
  are appropriately additive and avoid encoding business metadata into a path. The
  planned legacy-null compatibility and fail-closed migration shape checks are sound
  once B1 fixes the input/write semantics.
- The Chinese layout contract (configured sheet, title row 1, header row 2, required
  `文 件 编 号` at B2, data row 3+) correctly explains why first-nonempty-row behavior
  is insufficient. Keeping `.xlsx` default calls unchanged and extending `.xls`
  through the accepted TASK_366A read-only facade is the right parity boundary.
- Revision parsing, row-local candidate resolution, duplicate/ambiguity handling,
  downgrade blocking, preview zero-write, apply fingerprint recomputation, selected
  method-only mutation, and audit context are specific enough for a later review.
- The stated locks correctly exclude direct confirmed mutation, generic/specialized
  workbook behavior, Fee/LTR/project lifecycle, VBA and source writes, real files,
  and external residuals. The planned Settings and Matrix UI placement also matches
  the ConnLab product and frontend architecture rules.

## Validation Performed

- Read-only task/plan/evidence and source inspection only.
- Board confirms TASK_366B is the sole planned-only active lane, pending this Reviewer
  plan gate; no Developer route is currently legal.
- No product/test files were changed or staged by this review.

## Next Legal Route

Route only to **Planner docs-only fix pass** for B1. Do not route Developer
planning-first or implementation until the normalized worksheet input/persistence/API
contract is reconciled and passes a Reviewer plan re-gate.

## B1 Plan Re-Gate

Date: 2026-07-20

Status: `reviewer_pass`

The Planner's docs-only correction resolves the worksheet configuration ambiguity
without changing product scope:

- Standard-record field omission preserves an existing stored value; a new Standard
  row stores `NULL` and exposes effective `认可标准`.
- Explicit `null` and a string that trims to empty both reset the stored value to
  `NULL`, then return effective `认可标准`. A clear action is therefore deterministic
  and does not incorrectly fail validation.
- Trimmed nonblank valid values persist independently from the path. Invalid length,
  controls, and Excel-invalid characters remain typed no-write errors.
- Non-Standard resources ignore an omitted field but reject every supplied worksheet
  value, including `null` and blank. Responses are effective Standard values or
  `null` for other resource types.
- Task, plan, Planner evidence, and board consistently preserve the correct Matrix
  draft-only apply boundary, Confirm Matrix publication gate, read-only `.xlsx`/`.xls`
  source behavior, deterministic parser/match policy, and future scope locks.

The implementation test matrix now explicitly includes reset, legacy-null effective
default, omission-preserve, invalid no-write, and non-Standard field cases in addition
to the existing authority, parity, stale preview/apply, and package-isolation checks.

### Re-Gate Validation

- Read-only inspection of the corrected board, task, plan, and Planner evidence.
- Stale blank-rejection wording scan is clean across active TASK_366B governance.
- Governance diff check has only the repository's existing board LF/CRLF notice;
  evidence trailing whitespace is clean and no candidate product or test path was
  modified or staged by this review.

## Next Legal Route

Recommend only **User approval for Developer planning-first**. TASK_366B remains
planned-only; do not route Developer implementation directly.

## Implementation-Readiness Gate

Date: 2026-07-20

Status: `reviewer_pass`

The reconciled plan is implementation-ready while product implementation remains
unauthorized.

### Readiness Confirmed

- `WorksheetNameUpdate(supplied, value)` backed by Pydantic field presence provides a
  concrete omission-versus-reset boundary. The task, plan, board, and role evidence
  consistently freeze stored `NULL` plus effective `认可标准`, typed invalid no-write,
  and non-Standard rejection behavior.
- The additive `VARCHAR(31) NULL` and `TEXT NULL` migration has an implementable
  complete-preflight, one-transaction, final-read-verify, rollback, legacy-partial,
  and idempotency contract. It neither backfills nor touches an operator database.
- The proposed `ExcelTabularLayout` keeps existing `.xlsx`/`.xls` calls on their
  accepted default path while explicitly supporting the Chinese title/header/data
  layout, sparse B-column position, single configured sheet, and private row metadata.
  TASK_366A's COM lifecycle, read-only, and resource-limit rules remain intact.
- Preview reuses the one exported canonical saved-draft signature. Apply uses the
  exact root/row CAS contract and expected old Method predicates, so it cannot call
  destructive `replace_snapshot()` or overwrite non-Method draft state. Stale/source/
  target failures map to the specified `400`/`404`/`409` no-write outcomes.
- The Matrix authority chain remains correct: only editable draft `method` changes;
  existing Confirm Matrix publishes; Generic Test Record and TASK_360B remain
  confirmed read-only consumers. The Settings and Matrix UI split also follows the
  local API-client, feature-hook, and scoped-style rules.
- May Touch, read-only regression dependencies, bounded new test modules, large-file
  hunk restrictions, browser checks, and lock exclusions are sufficiently exact for a
  serialized implementation package.

### Non-Blocking Audit Note

The plan's inherited gateway counts (`435` XLSX / `366` COM) are conservative stale
figures. Read-only UTF-8 physical counts are currently `383` and `309`, respectively;
both are below the hard limit and the plan's shared-helper requirement remains the more
restrictive safe budget. This does not change the implementation contract.

### Validation

- Read-only review of task, plan, Planner/Developer/reconciliation evidence, board,
  accepted Office gateways, external-resource API chain, and Matrix draft repository/
  session signature behavior.
- Targeted governance trailing-whitespace scans are clean. Board/role state consistently
  records Reviewer implementation-readiness as current and implementation as
  unauthorized.
- Governance diff check has only the repository's existing LF/CRLF notice. No product,
  test, database, public-drive, or attachment path was accessed or modified; index is
  empty.

## Next Legal Route

Recommend only **User product implementation approval followed by Planner final
source-of-truth reconciliation**. Do not route Developer implementation directly.

## Implementation Gate

Date: 2026-07-20

Status: `reviewer_blocked / Developer bounded fix required`

## Findings

### B1: Apply CAS can claim a draft version that was not fingerprint-validated

[`matrix_method_version_sync_service.py`](D:\PythonProject\connlab\backend\application\matrix_method_version_sync_service.py:166)
loads the draft a second time after `_build_preview()` has validated the request
signature and preview fingerprint. The repository CAS at
[line 213](D:\PythonProject\connlab\backend\application\matrix_method_version_sync_service.py:213)
uses that second load's `updated_at`, rather than the draft version used to build the
validated preview. If that second lookup observes a newer draft whose selected row's
old Method happens to be unchanged, the CAS can apply the stale proposal to the newer
root instead of returning the required `409`.

**Required bounded fix:** carry the preview's exact draft id, `updated_at`, editable
status, and base-confirmed lineage as private facts, and pass those facts to the root
CAS. Do not reload a newer draft to establish CAS expectations. Add a focused service
or repository regression that switches the store/root between preview construction and
CAS, proves zero row/context write and typed conflict, and preserves the successful
same-version path.

### B2: Catalog/preview fingerprint omits configured source identity

[`matrix_method_version_sync_service.py`](D:\PythonProject\connlab\backend\application\matrix_method_version_sync_service.py:272)
hashes only catalog row values. The resulting preview fingerprint at
[line 286](D:\PythonProject\connlab\backend\application\matrix_method_version_sync_service.py:286)
therefore omits `resource_id`, normalized resource path, and effective worksheet name,
despite the frozen contract requiring those source-context facts. Reconfiguring the
Standard resource to a different path/sheet with identical catalog rows can retain the
same fingerprint and allow apply without the promised stale rejection or distinct
audit provenance.

**Required bounded fix:** include canonical resource id, normalized path, effective
worksheet name, and ordered parsed source rows in the catalog/source fingerprint used
by preview and apply. Add a regression where the configured resource changes but row
content is identical; apply must return typed `409` with no draft/context write. Keep
catalog data read-only and do not add a second provider read.

## Validation Reproduced

- Declared backend/Office/External Excel suite: `66 passed`.
- `py_compile` for reviewed authorized backend modules: passed.
- Matrix/Settings frontend suite: `4 files / 48 tests passed`.
- `npm run build`: passed with only the existing Vite chunk-size warning.
- Candidate scope inspection confirms worksheet normalization, Chinese `.xlsx`/`.xls`
  layout, method-only repository update, Confirm Matrix publication boundary, and
  locked Generic Test Record/TASK_360B/LTR/Fee paths otherwise conform to the lane.
- The declared read-only Matrix/Test Record run still has its separate external Fee
  `preserved_count` residual; it is neither caused by nor a legal fix target of
  TASK_366B.

## Next Legal Route

Route only to **Developer bounded fix pass** for B1 and B2. Do not route QA or
Integrator until the preview-source and CAS stale-protection regressions pass.

## B1/B2 Implementation Re-Gate

Date: 2026-07-21

Status: `reviewer_pass`

The bounded fix closes both stale-protection findings without expanding the product
contract:

- `_build_preview()` now returns a private build result that retains the exact editable
  draft root used for signature, lineage, catalog, and preview validation. Apply passes
  that root's `updated_at`, status, and confirmed lineage into the method-only CAS;
  it no longer reloads a newer root to establish CAS expectations. The new TOCTOU
  regression simulates a root update immediately before CAS and proves typed conflict,
  zero successful apply, and unchanged Method rows.
- The catalog fingerprint now hashes source `resource_id`, canonical path, effective
  worksheet name, and ordered catalog rows. The identical-row source-switch regression
  changes resource configuration, retains the same rows, and correctly receives a
  preview conflict with no apply write.
- Public DTO/API/client behavior, worksheet normalization, `.xlsx`/COM read routes,
  Generic Test Record/TASK_360B isolation, and Confirm Matrix publication remain
  unchanged by this pass.

### Validation Reproduced

- Exact B1/B2 service module: `5 passed`.
- Complete declared TASK_366B backend/Office suite: `68 passed`.
- `py_compile` for the fixed service/test: passed.
- Fixed service and its bounded test are `326` and `230` UTF-8 physical lines;
  trailing whitespace is clean, candidate diff check has only existing LF/CRLF notices,
  and the index is empty.
- The previously rerun frontend Matrix/Settings suite remains `4 files / 48 tests`
  passing; no frontend file changed in this bounded pass.

The unrelated Fee `preserved_count` failure remains an excluded external residual and
is not a TASK_366B action item.

## Next Legal Route

Route only to **QA gate**. QA should exercise the disposable SQLite/API flow and the
declared desktop/514px browser smoke where the controlled fixture is available. Do not
route Integrator from this gate.

## QA B3 Focused Implementation Re-Gate

Date: 2026-07-21

Status: `reviewer_pass`

The B3 responsive correction is bounded to the Method-preview presentation layer:

- Desktop retains the existing five-column semantic table. At `max-width: 600px`, the
  table body rows become a stable three-column grid with `Use`, `Test item`, and
  `Status` on the first row; `Current` then `Proposed` follow in DOM order below it.
- The retained table header stays available to assistive technology, while the two
  stacked value cells expose their visual labels through their existing `data-label`
  attributes. The native checkbox keeps its row-specific accessible name.
- The mobile table has `min-width: 0`, its wrapper no longer forces horizontal
  scrolling, and item/status/current/proposed content uses `minmax(0, ...)` and
  `overflow-wrap: anywhere`. The header actions form a two-column responsive grid, so
  both controls remain reachable at the declared 514px target.
- The candidate is limited to the panel's responsive CSS and its focused component
  assertion. There is no backend, API, client, authority, worksheet, or Confirm Matrix
  behavior change. The unrelated Fee residual remains excluded.

### Validation Reproduced

- `npm test -- MatrixMethodVersionSyncPanel --run`: `1 file / 2 tests passed`.
- `npm test -- MatrixEditorWorkspace SettingsStandardRecordSheet
  MatrixMethodVersionSyncPanel useMatrixMethodVersionSync --run`: `4 files / 49 tests
  passed`.
- `npm run build`: passed; only the existing Vite chunk-size warning was emitted.
- Focused diff check and trailing-whitespace scan are clean apart from the existing
  LF/CRLF working-copy notice. The panel and focused test remain below the Python/TS
  lane size limits.

## Next Legal Route

Route only to **QA re-gate** for the controlled 514px/desktop visual and console
re-smoke. Do not route Integrator from this focused Reviewer gate.
