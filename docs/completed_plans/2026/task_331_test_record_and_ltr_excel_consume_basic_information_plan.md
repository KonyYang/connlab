# TASK_331 Test Record And LTR Excel Consume Basic Information Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

`TASK_330F_BASIC_INFORMATION_TWO_COLUMN_LAYOUT_AND_DATE_INPUTS` is complete. The user explicitly requested a new plan and task file for `TASK_331_TEST_RECORD_AND_LTR_EXCEL_CONSUME_BASIC_INFORMATION`.

This plan is allowed now because TASK_330A/B/C established Project Basic Information authority and made Project Folder Required forms consume the latest confirmed snapshot. TASK_331 continues that same output-consumption direction for two remaining consumers: Test Record Word draft headers and LTR workbook metadata synchronization.

## Goal

Make Test Record Word draft generation and post-registration LTR Excel metadata synchronization consume the latest confirmed Project Basic Information snapshot instead of assembling business identity fields from ad hoc Project/LTR/ApplicationForm sources.

## Product Decision

Project Basic Information is now the project-level authority snapshot for shared business identity fields used by generated outputs.

`TASK_331` should therefore apply this rule:

```text
Formal generated/synchronized business files read latest confirmed Basic Information.
Draft Basic Information is ignored.
If no confirmed snapshot exists, the operation blocks before mutating files.
```

## Important Boundary

LTR workbook handling must be split into two concepts:

1. Initial LTR number application/registration.
2. Post-registration LTR workbook metadata synchronization.

Initial LTR application may happen before Basic Information is confirmed, because Basic Information is often assembled after project intake and Workbench review. TASK_331 must not break New Project completion or require confirmed Basic Information before first LTR registration.

TASK_331 only adds/adjusts the post-registration sync path so existing LTR workbook row metadata can be refreshed from confirmed Basic Information.

## Existing Code Context

### Basic Information Output Reader

Existing file:

- `backend/application/project_basic_information_output.py`

Reusable types:

- `ConfirmedBasicInformationSnapshot`
- `ConfirmedBasicInformationReader`
- `ProjectBasicInformationSnapshotReader`

Snapshot fields available:

- `project_id`
- `version`
- `values`
- `source_signature`
- `source_signature_hash`
- `context_signature`
- `confirmed_at`
- `confirmed_by`

### Test Record Word Generation

Existing files:

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/infrastructure/office/test_record_document_gateway.py`
- `backend/api/routes_confirmed_matrix_test_record_generation.py`
- `backend/api/dependencies.py`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/unit/test_test_record_document_gateway.py`
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`

Current behavior:

- Generates a `.docx` Test Record draft from active ConfirmedMatrix preview.
- Resolves `lab_test_request_number`, `product_description`, and `applicable_specification` from LTR notes, Project fields, intake draft, or ApplicationForm.
- Does not require confirmed Basic Information.
- Does not include Basic Information version/hash in the generation result.

### LTR Workbook Write

Existing files:

- `backend/application/ltr_workbook_write_preview_service.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- `backend/api/routes_ltr_workbook.py`
- `backend/api/dependencies.py`
- `backend/infrastructure/office/ltr_workbook_gateway.py` or current LTR workbook transaction gateway implementation under `backend/infrastructure/office/`
- `tests/unit/test_ltr_workbook_write_commit_service.py`
- `tests/integration/test_ltr_workbook_write_commit_api.py`

Current behavior:

- Initial workbook commit writes or replaces an LTR registration row through a locked transaction.
- `CommitLtrWorkbookWriteCommand` takes row metadata such as `test_item`, `sample_description`, `location`, `test_type_in_sheet`, and `project_leader` from request/command input.
- Commit rejects projects that already have a registered local LTR.
- This service is not the right place to update an already registered row.

## Data Mapping

TASK_331 must preserve the authority meaning of confirmed Basic Information.

For fields already modeled in Basic Information, consumers must read only from the confirmed snapshot. They must not silently mix in Project/ApplicationForm/LTR fallback values after the operator has confirmed Basic Information. If a required modeled field is empty, the consumer returns a blocker or warning that tells the operator to update and confirm Basic Information.

Fallbacks are allowed only for fields not yet modeled in Basic Information, or for existing non-authority template discovery values such as workbook path, target row location, and active ConfirmedMatrix content.

| Output field | Basic Information key | Missing behavior |
| --- | --- | --- |
| DL/LTR number | `dl_number` | Block if empty for Test Record or LTR sync. The latest registered local LTR is used only to find the existing workbook row, not to fill the output value. |
| Product / sample description | `product_description`, then `description_pn` | Block if both are empty. |
| Test item | `test_item` | Block if empty for LTR sync; Test Record still uses ConfirmedMatrix rows for step-level test items. |
| Applicable specification | `applicable_specifications` | If empty, Test Record may use existing intake/application specification extraction as an explicit not-yet-modeled fallback and include a warning in service tests. |
| Project type | `project_type` | Block if empty for LTR sync. |
| Requested by | `requested_by` | Use empty value only if workbook column allows empty; do not fallback to Project/ApplicationForm. |
| Mfg. Site / location | `location` | Block if empty for LTR sync. |
| Test type | `test_type` | Block if empty for LTR sync. |
| Project leader | `project_leader` | Block if empty for LTR sync. |
| Test result | `test_result` | Use Basic Information value or empty. |
| Failed item | `failed_item` | Use Basic Information value or empty. |
| Sample deposition | `sample_deposition` | Use Basic Information value or empty. |
| Sub-contract | `sub_contract` | Use Basic Information value or empty. |
| Test fee | `test_fee` | Use Basic Information value or empty. |
| Remarks (PO) | `remarks_po` | Use Basic Information value or empty. |

## Design

### 1. Test Record Header Consumption

Modify `ConfirmedMatrixTestRecordDocumentGenerationService` to accept an optional `ConfirmedBasicInformationReader`.

When the reader is provided:

1. `generate()` reads latest confirmed Basic Information before building the document.
2. If no confirmed snapshot exists, raise `ConfirmedMatrixTestRecordDocumentGenerationError` with:

   ```text
   Confirm Basic Information before generating Test Record.
   ```

3. Header metadata is built from confirmed Basic Information values:
   - `lab_test_request_number`: `dl_number`
   - `product_description`: `product_description` or `description_pn`
   - `applicable_specification`: `applicable_specifications`, falling back to existing specification extraction only when empty
4. `product_description` passed to the writer matches the Basic Information product description.
5. The application generation result includes:
   - `confirmed_basic_information_version`
   - `confirmed_basic_information_source_signature_hash`
6. The existing API download endpoint keeps returning `FileResponse`. It must not switch to a JSON envelope. The route exposes Basic Information context through response headers:
   - `X-ConnLab-Basic-Information-Version`
   - `X-ConnLab-Basic-Information-Source-Hash`

The existing writer boundary should remain the only Word mutation boundary. Do not make API routes or services manipulate `.docx` internals directly.

### 2. Test Record Gateway Header Fill

Keep using `TestRecordHeaderMetadata`.

If `TestRecordHeaderMetadata` already covers the required fields, only service-level metadata construction and tests need changes. If the template needs more header values later, extend the dataclass narrowly in the application layer and update `TestRecordDocumentGateway._fill_header_metadata()` tests.

TASK_331 should not implement Report headers, execution result tables, StepInstance persistence, or a full TestRecord aggregate.

### 3. LTR Workbook Metadata Sync

Add a new post-registration service instead of changing initial LTR application:

- `backend/application/ltr_workbook_basic_information_sync_service.py`

Responsibilities:

1. Read latest registered local LTR for the project.
2. Read latest confirmed Basic Information.
3. Open the workbook through the existing transaction/session gateway in a no-save preview mode or short read-only lookup mode.
4. Find the existing workbook row with `session.find_ltr_number(registered_ltr.ltr_number, sheet_names)`.
5. Build a workbook row preview for that exact existing row using Basic Information values.
6. Report the target workbook row only from `find_ltr_number()`. Do not reuse `LtrWorkbookWritePreviewService._target_row()` because that value estimates an append row and is not valid for existing-row sync.
7. Commit opens the workbook again, calls `find_ltr_number()` again, and writes the same existing row only if found.
8. If the row cannot be found during preview or commit, block with an actionable error.
9. Never allocate a new LTR number.
10. Never append a new row.
11. Never create a local LTR record.
12. Validate expected Basic Information version/hash on commit to prevent stale preview writes.
13. Use the existing LTR workbook transaction gateway for lock, backup, password, save, and Excel COM release behavior.

New command/result types:

```python
@dataclass(frozen=True, slots=True)
class PreviewLtrWorkbookBasicInformationSyncCommand:
    project_id: str

@dataclass(frozen=True, slots=True)
class CommitLtrWorkbookBasicInformationSyncCommand:
    project_id: str
    operator_confirmed: bool
    preview_acknowledged: bool
    expected_confirmed_basic_information_version: int
    expected_confirmed_basic_information_source_signature_hash: str

@dataclass(frozen=True, slots=True)
class LtrWorkbookBasicInformationSyncPreview:
    project_id: str
    ltr_number: str
    workbook_path: Path | None
    target_sheet: str
    target_row: int | None
    row_data: LtrWorkbookRowData
    columns: tuple[LtrWorkbookWriteColumnPreview, ...]
    confirmed_basic_information_version: int
    confirmed_basic_information_source_signature_hash: str
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class LtrWorkbookBasicInformationSyncResult:
    project_id: str
    ltr_number: str
    workbook_path: Path
    backup_path: Path
    sheet_name: str
    row_number: int
    confirmed_basic_information_version: int
    confirmed_basic_information_source_signature_hash: str
```

### 4. LTR Sync API

Add a typed API route module:

- `backend/api/routes_ltr_workbook_basic_information_sync.py`

Endpoints:

```text
GET /api/projects/{project_id}/ltr-workbook/basic-information-sync/preview
POST /api/projects/{project_id}/ltr-workbook/basic-information-sync/commit
```

Preview response:

- status `ready` when the existing row can be found and Basic Information is confirmed.
- status `blocked` when:
  - no local registered LTR exists,
  - no confirmed Basic Information exists,
  - workbook path/snapshot is unavailable,
  - workbook row cannot be found,
  - required workbook fields are missing.

Commit response:

- returns workbook path, backup path, sheet, row, LTR number, and Basic Information context.

TASK_331 does not attach this backend sync API to Project Folder `Update project folder` and does not implement the frontend preview/commit workflow. The reserved `Update LTR` entry belongs in the Workbench `Project Basic Information` card and is gated by confirmed Basic Information; a later `TASK_332` or separate UI/orchestration task should wire that entry to preview, operator confirmation, commit, and success/error feedback.

HTTP behavior:

- Missing project or registered LTR: `404`.
- Missing Basic Information or required field blockers: `400`.
- Workbook lock timeout: `409`.
- Stale Basic Information preview: `409`.
- Excel/workbook write errors: `400` with actionable detail.

### 5. Dependency Wiring

Modify `backend/api/dependencies.py`:

- Inject `ProjectBasicInformationSnapshotReader(ProjectBasicInformationRepository(session))` into:
  - `ConfirmedMatrixTestRecordDocumentGenerationService`
  - `LtrWorkbookBasicInformationSyncService`
- Register the new LTR sync service dependency.

Modify `backend/api/main.py`:

- Include the new router.

### 6. Tests

Add or update tests before implementation.

Test Record tests:

- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
  - missing confirmed Basic Information blocks before writer call.
  - confirmed Basic Information values populate header metadata.
  - result includes Basic Information version/hash.
  - applicable specifications read Basic Information when present; when empty, existing intake/application extraction is treated as the explicit not-yet-modeled fallback and is covered by warning-oriented tests.
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`
  - API returns `400` when Basic Information is unconfirmed.
  - API returns Basic Information version/hash when generation succeeds.

LTR sync tests:

- `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
  - preview blocks without local registered LTR.
  - preview blocks without confirmed Basic Information.
  - preview builds row data from Basic Information values.
  - commit rejects stale Basic Information version/hash.
  - preview uses workbook `find_ltr_number()` row lookup, not append-row estimation.
  - commit writes only existing workbook row and never appends.
  - commit rejects when target row cannot be found.
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`
  - preview returns typed Basic Information context.
  - commit requires operator confirmation and preview acknowledgement.
  - commit maps lock timeout to `409`.

Regression tests:

- `tests/integration/test_ltr_workbook_write_commit_api.py`
  - existing initial LTR application path still does not require confirmed Basic Information.
- `tests/unit/test_project_folder_required_forms_service.py`
  - existing 330C consumers still pass.

## File-Level Change List

Create:

- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `backend/api/routes_ltr_workbook_basic_information_sync.py`
- `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
- `tests/integration/test_ltr_workbook_basic_information_sync_api.py`
- `tasks/TASK_331_TEST_RECORD_AND_LTR_EXCEL_CONSUME_BASIC_INFORMATION.md`

Modify:

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/api/routes_confirmed_matrix_test_record_generation.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`
- `tests/integration/test_ltr_workbook_write_commit_api.py`
- `docs/task_board.md`

Expected no changes:

- No frontend UI files.
- No Basic Information schema/API/persistence files.
- No Project Folder Required forms behavior except regression tests.
- No Report generation files.
- No StepInstance/execution persistence files.

## Acceptance Criteria

1. Test Record Word draft generation blocks when confirmed Basic Information is missing.
2. Test Record Word draft generation fills header metadata from latest confirmed Basic Information.
3. Test Record generation keeps the `.docx` `FileResponse` behavior and returns Basic Information version/hash through `X-ConnLab-Basic-Information-Version` and `X-ConnLab-Basic-Information-Source-Hash` headers.
4. Existing ConfirmedMatrix authority requirements for Test Record generation remain intact.
5. New LTR workbook Basic Information sync preview reads latest confirmed Basic Information and latest registered local LTR.
6. New LTR workbook Basic Information sync preview and commit both locate the target row through workbook `find_ltr_number()` and block if the existing row is missing.
7. LTR sync never allocates, appends, or registers a new LTR.
8. LTR sync commit rejects stale Basic Information preview context.
9. Initial LTR workbook write/registration still works without confirmed Basic Information.
10. No Report, StepInstance, execution persistence, frontend UI, or Basic Information schema change is introduced.

## Validation Commands

Backend:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/unit/test_test_record_document_gateway.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py -q
py -m pytest tests/integration/test_ltr_workbook_write_commit_api.py tests/unit/test_ltr_workbook_write_commit_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

Frontend:

```powershell
cd frontend
npm test -- --run ProjectBasicInformation ProjectWorkbenchLayout --watch=false
npm run build
```

Static diff:

```powershell
git diff --check
```

## Manual Smoke

Use a test project first.

1. Confirm Basic Information for a test project.
2. Confirm Matrix for the same project.
3. Generate Test Record Word draft.
4. Verify the document header shows confirmed Basic Information values.
5. Preview LTR workbook Basic Information sync.
6. Verify the preview targets the existing registered LTR row and shows Basic Information-derived row values.
7. Commit sync only against a copied workbook or configured safe workbook path.
8. Verify Excel is released and the backup path is returned.
9. Reconfirm Basic Information with a changed field.
10. Verify old preview commit is rejected as stale.

## Risks

- LTR workbook is public-drive authority. Mitigation: sync must use existing transaction lock/backup gateway and update only an existing row.
- Test Record template header mapping may be format-sensitive. Mitigation: keep mutation inside `TestRecordDocumentGateway` and cover `_fill_header_metadata()` with focused tests.
- Existing initial LTR registration occurs before Basic Information confirmation. Mitigation: do not change existing initial write-commit blocker rules.
- Operators may expect LTR sync inside Project Folder update. Mitigation: keep API/backend sync ready in TASK_331; UI placement or one-click orchestration can be a later task if desired.

## Out Of Scope

- No Report generation or Report header fill.
- No Basic Information source-provider additions from Matrix/Fee.
- No Basic Information schema, required-field, or UI changes.
- No Project Folder Required forms semantic changes.
- No managed-output record system for Test Record or LTR workbook beyond returning Basic Information context. Because the existing Test Record output filename is deterministic, TASK_331 must still prevent silent user-file overwrite by blocking when the target Test Record file already exists and no managed-output/fingerprint safety record proves it is safe to replace, or by generating a unique draft filename.
- No public-drive upload redesign.
- No LTR sync frontend preview/commit workflow, confirmation dialog, success feedback, or one-click workflow placement.
- Workbench may expose the reserved `Update LTR` entry in the `Project Basic Information` card, gated by confirmed Basic Information; wiring the entry to the backend sync API is deferred to a later approved task.
- No StepInstance, execution persistence, evidence/image management, AI review, permissions, LAN/server, or multi-user behavior.
