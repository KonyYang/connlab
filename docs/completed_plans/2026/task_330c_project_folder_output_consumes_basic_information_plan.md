# TASK_330C Project Folder Output Consumes Basic Information Plan

> For implementation agents: follow `docs/project_management/TASK_EXECUTION_SKILL.md` and do not write implementation code until this plan is approved. This plan intentionally excludes unrelated request-material API fixes and Fee Form performance caching so TASK_330C stays focused on Basic Information output consumption.

## Governance

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task ID: `TASK_330C_PROJECT_FOLDER_OUTPUT_CONSUMES_BASIC_INFORMATION`.
- Why this task is allowed now: `TASK_330A_PROJECT_BASIC_INFORMATION_AUTHORITY_DATA_API` and `TASK_330B_PROJECT_BASIC_INFORMATION_WORKBENCH_UI` are complete, and the task board names TASK_330C as the next explicit stop-point task.
- Current approval state: plan/task-file preparation only is approved. Implementation still requires separate explicit approval.
- Stop rule: implement only TASK_330C after approval, then stop. Do not proceed to LTR workbook writeback, report generation, StepInstance, AI, permissions, LAN/server, or multi-user scope.

## Real Code Baseline

Current relevant code paths:

- `backend/application/project_basic_information_service.py`
  - Defines `ProjectBasicInformationRecord` with `version`, `values`, and `source_signature`.
  - `source_signature` is a full JSON signature of source values, so output contexts must use a bounded hash rather than embedding the full string.
  - `ProjectBasicInformationRepositoryPort.get_latest_confirmed(project_id)` already exists.
- `backend/infrastructure/storage/repositories/project_basic_information.py`
  - Implements latest confirmed record lookup.
- `backend/application/project_folder_required_forms_service.py`
  - Required forms preview currently gates on Official folder, Matrix authority, Confirmed Fee authority, and Customer Feedback template.
  - Current source context is `matrix:<id>@<revision>|fee:<id>@<revision>|pricing:<edit_id>`.
  - Managed-output safety already compares stored target path, sha256, and source context.
  - The staging generator only receives `project_id`, `key`, and `target_name`.
- `backend/api/dependencies.py`
  - `_RequiredFormsStagingGenerator` delegates:
    - Test Record to `ConfirmedMatrixTestRecordDocumentGenerationService`,
    - Fee Form to `ConfirmedMatrixFeeEvaluationExportService`,
    - Customer Feedback Form to `CustomerFeedbackFormGenerationService`.
- `backend/application/project_application_form_write_back_service.py`
  - Copied application Word write-back currently builds fields from `Project` + `ApplicationForm`.
  - Output record context is currently `application-form:<form_id>`.

## Goal

Make Project Folder formal outputs consume the latest confirmed Project Basic Information snapshot.

This means:

- Required forms preview/generate must know which Basic Information version/signature is being used.
- Required forms output generators must receive confirmed Basic Information values.
- Application Word write-back must use confirmed Basic Information values.
- Refresh after Basic Information reconfirmation must reuse TASK_321 managed-output safety, never overwrite user-edited files.

## Non-Goals

- No UI changes to the Basic Information editor or summary card.
- No new Basic Information source providers from Matrix or Fee.
- No public-drive upload changes.
- No LTR workbook writeback.
- No report generation.
- No template-mapping UI.
- No request-material collect bug fix.
- No Fee Form COM performance cache or reuse optimization.

## Design

### 1. Add A Confirmed Basic Information Reader Boundary

Add an application-layer protocol to the output services that need the snapshot.

Recommended minimal type in `backend/application/project_basic_information_output.py`:

```python
from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class ConfirmedBasicInformationSnapshot:
    project_id: str
    version: int
    values: dict[str, str]
    source_signature: str
    confirmed_at: str | None
    confirmed_by: str | None

    @property
    def source_signature_hash(self) -> str:
        return sha256(self.source_signature.encode("utf-8")).hexdigest()

    @property
    def context_signature(self) -> str:
        return f"basic:{self.version}@{self.source_signature_hash}"
```

Reader protocol:

```python
class ConfirmedBasicInformationReader(Protocol):
    def get_latest_confirmed(
        self,
        project_id: str,
    ) -> ConfirmedBasicInformationSnapshot | None:
        ...
```

Dependency wiring can adapt `ProjectBasicInformationRepository.get_latest_confirmed(...)` into this reader. The repository domain record should not leak into every output service if a small snapshot type keeps the output contract cleaner.

### 2. Gate Required Forms On Confirmed Basic Information

Modify `ProjectFolderRequiredFormsService` constructor to accept `basic_information_reader`.

In `preview(project_id)`:

1. keep existing Official folder, folder-check, Matrix, Fee, and Customer Feedback template gates;
2. read latest confirmed Basic Information;
3. if missing, return blocked preview with one actionable blocker:

```text
Confirm Basic Information before generating Project Folder outputs.
```

4. include the snapshot in source context and preview metadata.

Extend `RequiredFormsPreview` with:

```python
confirmed_basic_information_version: int | None
confirmed_basic_information_source_signature_hash: str | None
```

Update source context:

```text
matrix:<id>@<revision>|fee:<id>@<revision>|pricing:<edit_id>|basic:<version>@<source_signature_hash>
```

Do not store the full Basic Information source-signature JSON in `ProjectOutputRecord.source_context_signature`; that database field is bounded and intended for compact freshness tokens.

### 3. Validate Basic Information Context During Generate

Extend `GenerateRequiredFormsCommand` with:

```python
expected_confirmed_basic_information_version: int
expected_confirmed_basic_information_source_signature_hash: str
```

Update `_validate_context(...)` so generation rejects stale previews when:

- another Basic Information version was confirmed after preview;
- source signature changed;
- expected targets no longer match current generate/update targets;
- existing Matrix/Fee/template checks fail as today.

This keeps Basic Information reconfirmation from racing with `Update project folder`.

### 4. Pass Snapshot To Staging Generators

Extend the `RequiredFormsStagingGenerator` protocol:

```python
def generate(
    self,
    *,
    project_id: str,
    key: str,
    target_name: str,
    basic_information: ConfirmedBasicInformationSnapshot,
) -> Path:
    ...
```

Use the snapshot for:

- `fee_form`: write at least these confirmed Basic Information fields through the existing Fee export/gateway boundary:
  - `dl_number`,
  - `product_description`,
  - `test_item`,
  - `requested_by`,
  - `location`,
  - `lab_performing_tests`.
- `customer_feedback_form`: write at least these confirmed Basic Information fields through the existing Customer Feedback generation boundary:
  - `dl_number`,
  - `product_description`,
  - `test_item`,
  - `requested_by`,
  - `phone`,
  - `requestor_email`,
  - `project_leader`,
  - `lab_performing_tests`,
  - `date_lab_received_samples`,
  - `estimated_completion_date`.
- `test_record`: no Basic Information data change unless the current Test Record generator already supports identity fill safely. Still include Basic Information in output context so the file can be refreshed when formal source context changes.

Office writes must stay behind existing infrastructure/application gateways. No route or UI may write Excel/Word directly.

### 5. Consume Snapshot In Application Word Write-Back

Modify `ProjectApplicationFormWriteBackService` to accept `basic_information_reader`.

Behavior:

- if no confirmed Basic Information snapshot exists, raise an actionable blocker before Word mutation;
- locate the copied Application Form in `Submitted Material` as today;
- build known Word fields from Basic Information values first;
- keep a narrow fallback only for fields not present in Basic Information if that preserves existing behavior and does not overwrite explicit Basic Information values.

Recommended field mapping:

```text
ltr_number                 <- dl_number
project_number             <- project_number
project_type               <- project_type
description_pn             <- description_pn
product_description        <- product_description
test_item                  <- test_item
applicable_specifications  <- applicable_specifications
requested_by               <- requested_by
requester                  <- requested_by
phone                      <- phone
email                      <- requestor_email
location                   <- location
project_leader             <- project_leader
lab                        <- lab_performing_tests
sample_condition           <- condition_of_samples_when_received
received_date              <- date_lab_received_samples
estimated_completion_date  <- estimated_completion_date
start_test_date            <- start_test_date
finish_test_date           <- finish_test_date
report_date                <- report_date
test_fee                   <- test_fee
remarks_po                 <- remarks_po
```

Register `SECTION2_WRITE_BACK` output with context:

```text
application-form:<form_id>|basic:<version>@<source_signature_hash>
```

### 6. Preserve Managed-Output Safety

Do not weaken existing TASK_321 semantics.

Required forms refresh rules:

- if target does not exist, generate;
- if target exists without a ConnLab output record, conflict for Test Record and write-back outputs;
- if existing Fee/Customer Feedback behavior currently treats present unmanaged files as current, review during implementation and keep or tighten only with tests and explicit acceptance;
- if target has a ConnLab record but sha256 changed, conflict;
- if target has matching sha256 but different source context, update;
- if target has matching sha256 and matching source context, skip/current.

Word write-back refresh rules:

- Word write-back mutates the copied Application Form, so it must not silently overwrite a user-edited file unless the existing write-back service has an explicit managed fingerprint check.
- If the current service lacks pre-write fingerprint protection for `SECTION2_WRITE_BACK`, add the minimum safe check using the latest output record before writing:
  - matching path,
  - matching stored sha256,
  - managed/system-generated status/source where available,
  - then write and register the new sha256/context;
  - otherwise block.

### 7. API Surface

No new route is required.

Existing routes may gain typed response/request fields:

- `GET /api/projects/{project_id}/project-folder/required-forms/preview`
- `POST /api/projects/{project_id}/project-folder/required-forms/generate`
- `POST /api/projects/{project_id}/project-folder/application-form/write-back`

If exposed, new fields should be business-readable and optional-compatible:

```json
{
  "confirmed_basic_information_version": 2,
  "confirmed_basic_information_source_signature_hash": "..."
}
```

Frontend DTO/client changes are in scope for this task because the existing Workbench generate request must echo preview context for stale-preview validation. Do not add new Basic Information UI in TASK_330C.

## File-Level Change Plan

Expected backend files:

- `backend/application/project_basic_information_output.py`
  - new snapshot dataclass and reader adapter/protocol if not kept inside service modules.
- `backend/application/project_folder_required_forms_service.py`
  - add Basic Information reader,
  - block preview when missing,
  - extend preview/command context,
  - pass snapshot to generator,
  - include Basic Information in `source_context_signature`.
- `backend/application/project_application_form_write_back_service.py`
  - add Basic Information reader,
  - block when missing,
  - map Basic Information fields,
  - include Basic Information context,
  - add/keep safe managed-output checks before mutation.
- `backend/api/dependencies.py`
  - wire Basic Information repository/adapter into required forms and write-back services,
  - pass snapshot into `_RequiredFormsStagingGenerator`.
- `backend/api/routes_project_folder_required_forms.py`
  - expose and echo Basic Information version/hash for stale-preview validation.
- `backend/api/routes_project_application_form_write_back.py`
  - update typed response only if new context/blocker needs to be exposed.
- `frontend/src/api/client.ts`
  - add Basic Information version/hash fields to Required forms preview/generate DTOs.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - pass Basic Information version/hash from preview to generate request.

Expected tests:

- `tests/unit/test_project_folder_required_forms_service.py`
- `tests/unit/test_project_application_form_write_back_service.py`
- `tests/integration/test_project_folder_required_forms_api.py`
- `tests/integration/test_official_project_workspace_api.py`
- frontend tests only if DTO echo fields change.

## Test Plan

### Unit Tests

Add or update tests for:

- Required forms preview blocks when Basic Information has no confirmed snapshot.
- Required forms preview includes `basic:<version>@<source_signature>` in source context.
- Required forms generate rejects stale preview when Basic Information version changed.
- Required forms generate passes Basic Information snapshot to Fee and Customer Feedback staging generator.
- Fee Form generation writes the minimum required Basic Information fields: `dl_number`, `product_description`, `test_item`, `requested_by`, `location`, and `lab_performing_tests`.
- Customer Feedback generation writes the minimum required Basic Information fields: `dl_number`, `product_description`, `test_item`, `requested_by`, `phone`, `requestor_email`, `project_leader`, `lab_performing_tests`, `date_lab_received_samples`, and `estimated_completion_date`.
- Customer Feedback filename suffix uses Basic Information `project_leader` when present and falls back to the current ApplicationForm assigned-personnel behavior only when it is empty.
- Existing managed output with unchanged sha256 but changed Basic Information context updates.
- Existing managed output with changed sha256 blocks.
- Application Word write-back blocks without confirmed Basic Information.
- Application Word write-back maps confirmed Basic Information values ahead of Project/ApplicationForm fallback.
- Application Word write-back records `application-form:<id>|basic:<version>@<source_signature>`.
- Application Word write-back blocks user-edited managed targets before mutation when a prior managed record exists and disk sha256 differs.

### API Tests

Add or update tests for:

- Required forms preview response reports blocker for missing Basic Information.
- Required forms preview/generate round trip succeeds with Basic Information context.
- Required forms generate stale Basic Information context returns conflict/stale-preview error.
- Workbench Required forms generate request echoes Basic Information version/hash from preview.
- Application form write-back returns blocker/missing-state error when Basic Information is not confirmed.
- Nonexistent project behavior stays unchanged.

### Manual Smoke

Use a temporary or disposable project where possible:

1. Confirm Basic Information.
2. Click `Generate project folder` or `Update project folder`.
3. Verify:
   - Fee Form exists in the Official project folder root,
   - Customer Feedback Form exists in the Official project folder root,
   - copied Application Word document exists in `Submitted Material`,
   - all three use confirmed Basic Information values where mapped.
4. Reconfirm Basic Information with a changed value.
5. Click `Update project folder`.
6. Verify managed outputs refresh only when unchanged on disk.
7. Manually edit a generated output and click `Update project folder`.
8. Verify ConnLab blocks instead of overwriting.

## Validation Commands

After implementation:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
py -m pytest tests/integration/test_official_project_workspace_api.py -q
```

If dependency wiring or DB/service behavior changes broadly:

```powershell
py -m pytest tests/integration/test_api_default_dependencies.py -q
py -m pytest tests/unit/test_database.py -q
```

Frontend request/response DTOs are expected to change for Required forms stale-preview validation:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors --watch=false
npm run build
```

## Risks

- Basic Information field names must remain stable. If field labels change in UI, output mapping should still use backend keys.
- Application Word write-back mutates an existing copied document; without strict fingerprint checks it can overwrite user edits. This plan requires adding the missing check if current code lacks it.
- Fee Form export currently uses an existing Matrix/Fee path. Passing Basic Information must be done through a narrow extension, not by duplicating Office write logic in the required-forms service.
- Customer Feedback file naming currently uses application form assigned personnel. TASK_330C must switch the suffix source to confirmed Basic Information `project_leader` when present, and may fall back to the current source only when `project_leader` is empty.
- Blocking formal outputs when Basic Information is unconfirmed may affect existing projects. The user path is already available through TASK_330B: open `Basic Information`, confirm, return to Workbench, then generate/update Project Folder outputs.

## Acceptance Criteria

- TASK_330C implementation does not touch Basic Information source assembly, UI editor behavior, LTR workbook, report generation, public-drive upload, StepInstance, AI, permissions, LAN/server, or multi-user scope.
- Project Folder formal outputs consume latest confirmed Basic Information snapshot.
- Missing confirmed Basic Information blocks formal output generation/write-back before mutation.
- Basic Information version/source signature is part of required output context.
- Required output context uses a bounded Basic Information source-signature hash, not the full JSON source signature.
- Customer Feedback filename suffix uses confirmed Basic Information `project_leader` when available.
- Reconfirmed Basic Information causes safe managed refresh behavior.
- User-modified/unmanaged files are not overwritten.
- Tests cover preview, generate, write-back, stale context, and fingerprint safety.
