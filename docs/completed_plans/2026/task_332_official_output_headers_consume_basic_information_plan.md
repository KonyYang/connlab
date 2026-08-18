# TASK_332 Official Output Headers Consume Basic Information Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` or the project task execution protocol before implementation. This plan is review material only until the user explicitly approves TASK_332 implementation.

**Goal:** Make Project Folder formal output headers consistently use the latest confirmed Project Basic Information snapshot without reopening the same Office file for a second header pass.

**Architecture:** Keep Basic Information as the authority snapshot boundary, add a small output-identity mapper in the application layer, and pass mapped identity into each output generator before the Office gateway opens a file. Gateways write header fields during their existing generate/write session.

**Tech Stack:** Python 3.11, FastAPI application services, SQLite-backed Basic Information snapshots, Office/Excel/Word gateways, pytest.

## Current Phase / Task Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current completed task: `TASK_331_TEST_RECORD_AND_LTR_EXCEL_CONSUME_BASIC_INFORMATION`.
- Why TASK_332 is allowed: `docs/task_board.md` says TASK_331 is complete and the user explicitly requested the next plan for formal output generation consuming confirmed Basic Information.
- This document is a plan only. No implementation code is authorized until the user approves TASK_332.

## Current Code Evidence

The current code already has most of the required seams:

- `backend/application/project_basic_information_output.py`
  - Defines `ConfirmedBasicInformationSnapshot`, `context_signature`, and `ProjectBasicInformationSnapshotReader`.
- `backend/application/project_folder_required_forms_service.py`
  - Required Forms preview blocks without confirmed Basic Information.
  - Generate validates Basic Information version/hash against preview context.
  - Staging generator receives `ConfirmedBasicInformationSnapshot`.
- `backend/api/dependencies.py`
  - `_RequiredFormsStagingGenerator` passes `basic_information.values` into Fee and Customer Feedback generation.
- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
  - `ExportConfirmedMatrixFeeEvaluationCommand.basic_information_values` reaches the workbook writer.
- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
  - `generate_matrix_basic_fill()` opens Excel once, writes Basic Information identity, writes Matrix basic fill rows, saves once.
- `backend/application/customer_feedback_form_generation_service.py`
  - Builds Customer Feedback identity from Basic Information, but still falls back to project identity when no Basic Information values are provided.
- `backend/infrastructure/office/customer_feedback_workbook_gateway.py`
  - Copies template and uses openpyxl to fill only `ltr_number`, `requestor`, and `product_name` aliases; several Basic Information identity fields are currently ignored by the gateway.
- `backend/application/project_application_form_write_back_service.py`
  - Requires confirmed Basic Information and writes the copied Application Form Word document.
  - Some modeled fields still use fallback expressions such as `basic.get(...) or form/project`.
- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
  - Blocks without confirmed Basic Information when the reader is configured.
  - Builds Test Record header metadata from Basic Information and returns version/hash for API headers.

## User-Provided Reference Samples

The user supplied three production-style sample files for TASK_332 mapping review:

- Fee sample:
  `C:/Users/White/Desktop/AI information/Projects/DL-2025-11-073/DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test/DL-2025-11-073 Form for Testing Fee Evaluation.xls`
- Customer Feedback sample:
  `C:/Users/White/Desktop/AI information/Projects/DL-2025-11-073/DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test/DL-2025-11-073 Customer Feedback Form.xlsx`
- Application Form sample:
  `C:/Users/White/Desktop/AI information/Projects/DL-2025-11-073/DL-2025-11-073 Coolpower 3.40mm Pin Busbar To Socket Busbar Qualification Test/Submitted Material/Coolpower 3.40mm Busbar To Busbar qualification test  Request-20251111.docx`

These files are manual references only. Automated tests must not read from `C:/Users/White/Desktop/...`. During implementation, convert the observed layouts into minimal generated fixtures under `tests/fixtures/` or create equivalent workbook/docx files inside tests.

Observed sample header anchors:

- Fee sample, sheet `Testing Prices`:
  - Row 2: `LTR Number` -> `DL-2025-11-073`
  - Row 2: `Test Description` -> `Coolpower 3.40mm Busbar To Busbar Qualification Test`
  - Row 3: `Requestor` -> `MP Cao`
  - Row 3: `Site` -> `Dongguan`
- Customer Feedback sample, sheet `Customer Feedback Form`:
  - Row 7: `Customer Name` -> `MP Cao`
  - Row 7: `Telephone No.` -> `16763616869`
  - Row 7: `Site` -> `Dongguan`
  - Row 9: `Project Details (if applicable)` -> `Coolpower 3.40mm Busbar To Busbar Qualification Test`
  - Row 9: `Work Request No.` -> `DL-2025-11-073`
  - Row 11: `From Date (mm/dd/yy)` and `To Date (mm/dd/yy)`
  - Row 13: `GES Team` -> `DongGuan Product Test Lab`
- Application Form sample:
  - Requestor table includes `Requested By`, `Phone #`, `Date`, `Email`, `Business Unit`, `Mfg. Site`, `Project #`, `Results Format`, and requested completion date.
  - Product/sample table includes `Product Name`, `Part Number / Revision`, traceability, materials, plating, lubricant, housing, and quantity.
  - Test table includes `Tests to be Performed` and `Applicable Specifications`.
  - Additional form anchors include confidential/subcontract flags and report-copy recipients.

TASK_332 implementation should turn these observed labels into repository-owned tests. The Customer Feedback workbook in particular shows that simple "label cell + next column" logic is not enough for every field: `Site` and `Work Request No.` use wider offsets because of merged/blank cells. The gateway should support explicit placement rules first, then controlled label search only for fields that are safe to discover.

## Fixture Policy

- Do not make tests depend on user desktop paths or production customer files.
- Prefer generated fixtures in test code for simple `.xlsx`/`.docx` layouts.
- If binary fixtures are needed, store minimal sanitized files under `tests/fixtures/official_output_headers/`.
- The fixture must contain only the labels and cells needed for TASK_332 tests, not a full customer workbook.
- The fixture should encode the sample-specific hard cases:
  - Customer Feedback merged/blank-cell offset targets.
  - Application Form table labels.
  - Fee Form fixed header cells.

## Problem Statement

The product direction is correct: Project Basic Information is the operator-confirmed authority for formal output headers. The remaining risk is consistency:

- Fee Form is already close, but needs stronger regression coverage that the workbook header is written from Basic Information in the same Excel session as row generation.
- Customer Feedback receives Basic Information in the service, but the infrastructure gateway ignores many known fields because aliases only cover three keys.
- Application Form write-back uses Basic Information but still contains silent fallback expressions for fields already modeled by Basic Information.
- Test Record already uses Basic Information, but TASK_332 should preserve that behavior while the shared output identity mapper is introduced.
- Efficiency should be explicit: do not generate body first and then reopen the same file for headers.

## Scope

TASK_332 includes:

1. Shared formal output identity mapping from `ConfirmedBasicInformationSnapshot`.
2. Fee Evaluation workbook header mapping hardening and tests.
3. Customer Feedback workbook header mapping expansion and tests.
4. Application Form Word write-back mapping hardening and tests.
5. Test Record header regression tests to ensure the existing one-pass path remains intact.
6. Required Forms orchestration tests proving Basic Information context is passed once and validated.
7. Task board completion update after implementation.

TASK_332 excludes:

- UI changes.
- LTR sync UI/confirmation workflow.
- Report generation.
- Basic Information schema/API/persistence changes.
- Matrix/Fee Basic Information source providers.
- Project Folder one-click orchestration changes beyond current Required Forms path.
- New public-drive authority behavior.

## Design

### 1. Shared Output Identity Mapper

Create a focused mapper module:

`backend/application/project_basic_information_output_identity.py`

Responsibilities:

- Convert `ConfirmedBasicInformationSnapshot` into output-specific identity payloads.
- Provide one place to define business field names, labels, and fallback rules.
- Keep mapped fields explicit.

Suggested dataclasses:

```python
@dataclass(frozen=True, slots=True)
class FeeFormIdentity:
    dl_number: str
    product_description: str
    test_item: str
    requested_by: str
    location: str
    lab_performing_tests: str

@dataclass(frozen=True, slots=True)
class CustomerFeedbackIdentity:
    ltr_number: str
    product_name: str
    test_item: str
    requestor: str
    phone: str
    email: str
    project_leader: str
    lab: str
    received_date: str
    estimated_completion_date: str

@dataclass(frozen=True, slots=True)
class ApplicationFormWriteBackIdentity:
    fields: dict[str, str]

@dataclass(frozen=True, slots=True)
class TestRecordHeaderIdentity:
    lab_test_request_number: str
    product_description: str
    applicable_specification: str
```

Suggested functions:

```python
def fee_form_identity(snapshot: ConfirmedBasicInformationSnapshot) -> FeeFormIdentity: ...
def customer_feedback_identity(snapshot: ConfirmedBasicInformationSnapshot) -> CustomerFeedbackIdentity: ...
def application_form_identity(snapshot: ConfirmedBasicInformationSnapshot) -> ApplicationFormWriteBackIdentity: ...
def test_record_header_identity(snapshot: ConfirmedBasicInformationSnapshot) -> TestRecordHeaderIdentity: ...
```

Rule:

- For fields modeled in Basic Information, the mapper reads Basic Information only.
- Empty modeled fields remain empty unless the output explicitly treats them as required and blocks.
- Legacy Project/ApplicationForm fallback can only be used for fields not modeled in Basic Information or for controlled filename suffix compatibility already documented elsewhere.

### 2. Fee Evaluation Workbook

Current path:

`ProjectFolderRequiredFormsService` -> `_RequiredFormsStagingGenerator` -> `ConfirmedMatrixFeeEvaluationExportService.export()` -> `FeeEvaluationWorkbookGateway.generate_matrix_basic_fill()`

Implementation approach:

- Keep `generate_matrix_basic_fill()` as the single Excel open/save boundary.
- Replace ad hoc `dict[str, str]` Basic Information identity with mapper output or mapper-derived dict at the application boundary.
- `_write_basic_information_identity()` should continue writing before `_write_matrix_basic_fill()` inside the same workbook session.
- Add tests proving:
  - `basic_information_values` or mapped identity reaches the writer.
  - gateway writes `.Value` to the expected cells/labels, not only that `.Text` displays expected source values.
  - the fake Excel app opens one workbook and saves once for a matrix-basic Fee Form.
  - protected/merged/formula regions outside the intended header cells are not overwritten.

Expected no second pass:

```text
Open template workbook once
  -> write Basic Information header fields
  -> write Matrix/Fee rows
  -> save as target
Close workbook
```

### 3. Customer Feedback Workbook

Current path:

`ProjectFolderRequiredFormsService` -> `_RequiredFormsStagingGenerator` -> `CustomerFeedbackFormGenerationService.generate()` -> `CustomerFeedbackWorkbookGateway.generate()`

Implementation approach:

- Keep template copy + one workbook load/save operation.
- Expand `CustomerFeedbackWorkbookGateway` alias coverage to write known Customer Feedback fields:
  - `ltr_number`
  - `product_name`
  - `test_item`
  - `requestor`
  - `phone`
  - `email`
  - `project_leader`
  - `lab`
  - `received_date`
  - `estimated_completion_date`
- Add aliases matching likely template labels, for example:
  - `ltr_number`: `work request no`, `work request number`, `ltr number`, `dl number`
  - `product_name`: `project details`, `product description`, `product name`
  - `requestor`: `customer name`, `requestor`, `requester`, `requested by`
  - `phone`: `phone`, `telephone`, `tel`
  - `email`: `e-mail of requestor`, `email`, `e mail`, `requestor email`
  - `project_leader`: `project leader`, `engineer`, `owner`
  - `lab`: `lab performing the tests`, `lab`, `testing lab`
  - `received_date`: `date lab received samples`, `received date`
  - `estimated_completion_date`: `estimated completion date`, `completion date`
- Add placement support for the supplied sample layout:
  - `Customer Name` value at row 7, column C.
  - `Telephone No.` value at row 7, column E.
  - `Site` value at row 7, column I.
  - `Project Details` value at row 9, column C.
  - `Work Request No.` value at row 9, column I.
  - `From Date` value at row 11, column C.
  - `To Date` value at row 11, column E.
  - `GES Team` value at row 13, column C.
- Preserve warnings for labels not found.
- Add gateway-level tests using a real temporary `.xlsx` workbook with label cells and assert the adjacent value cells are filled.

Hard placement rules:

| Field | Basic Information key | Placement rule | Missing label/cell result |
| --- | --- | --- | --- |
| Work Request No. | `dl_number` | Prefer fixed sample-compatible anchor row containing `Work Request No.` and write to the target value cell in that row; fallback label search may use configured offset. | Block if missing; workbook identity is invalid without DL/LTR number. |
| Project Details | `product_description` or `description_pn` | Prefer label `Project Details`; write to the project detail value cell. | Block if both Product Description and Description P/N cannot be placed. |
| Customer Name | `requested_by` | Prefer label `Customer Name`; write to requestor value cell. | Warning if missing. |
| Telephone No. | `phone` | Prefer label `Telephone No.` / `Phone`; write to phone value cell. | Warning if missing. |
| Site | `location` | Prefer label `Site`; write to sample-compatible site value cell, not simply the next column. | Warning if missing. |
| From Date | `date_lab_received_samples` | Prefer label `From Date`; write to date value cell using the workbook's existing date style when possible. | Warning if missing. |
| To Date | `estimated_completion_date` | Prefer label `To Date`; write to date value cell using the workbook's existing date style when possible. | Warning if missing. |
| GES Team | `lab_performing_tests` | Prefer label `GES Team`; write to team value cell. | Warning if missing. |

Search policy:

- Use fixed/known anchors for the sample-compatible Customer Feedback header.
- Use label search only within the header band, not the whole workbook.
- Do not write into formula cells.
- If a found label belongs to a merged range, resolve the target cell from the top-left label anchor and configured offset.
- Return warnings for optional fields that cannot be placed; return blockers for DL/LTR number and project detail fields.

Efficiency:

- The gateway currently copies the template then loads the copied workbook once with openpyxl. That is acceptable for `.xlsx`.
- Do not reopen the workbook in a later header update service.

### 4. Application Form Word Write-Back

Current path:

`ProjectApplicationFormWriteBackService.write_back()` -> `OfficeFacade.write_word_application_form_fields()` -> Word gateway.

Implementation approach:

- Replace `_fields(project, form, basic_information)` fallback-heavy mapping with mapper-guided Basic Information fields for modeled values.
- For modeled fields, use Basic Information values only:
  - `dl_number`
  - `project_number`
  - `project_type`
  - `description_pn`
  - `product_description`
  - `test_item`
  - `applicable_specifications`
  - `requested_by`
  - `phone`
  - `requestor_email`
  - `location`
  - `project_leader`
  - `business_unit`
  - `requested_completion_date`
  - `lab_performing_tests`
  - schedule/date fields
  - result/commercial/sample fields modeled by Basic Information
- Use legacy form/project fallback only for values not currently modeled by Basic Information and only when necessary to maintain existing Word field support.
- Keep `_ensure_safe_managed_target()` unchanged.
- Add tests proving that when Basic Information values intentionally differ from ApplicationForm/Project values, the Word write-back uses Basic Information.

Minimum mapping acceptance table:

| Basic Information key | Word label/table anchor | Required for write-back | Missing behavior |
| --- | --- | --- | --- |
| `requested_by` | `Requested By:` | Yes | Block; requestor identity is required. |
| `phone` | `Phone #:` | No | Skip with warning if label exists but value is empty. |
| `requestor_email` | `Email:` | No | Skip with warning if label exists but value is empty. |
| `business_unit` | `Business Unit:` | No | Skip if empty. |
| `location` | `Mfg. Site:` | No | Skip if empty. |
| `project_number` | `Project #:` | No | Skip if empty. |
| `results_format` | `Results Format:` | No | Skip if empty. |
| `requested_completion_date` | `Requested Testing Completion Date:` | No | Skip if empty. |
| `project_type` | `Project Type` | No | Skip if empty. |
| `test_sample_status` | `Test Sample Status` | No | Skip if empty. |
| `product_description` | `Product Name` / product table | Yes if `description_pn` is empty | Block if both product description and Description P/N are empty. |
| `description_pn` | `Part Number / Revision` or Description P/N target | Yes if `product_description` is empty | Block if both product description and Description P/N are empty. |
| `test_item` | `Tests to be Performed` | Yes | Block. |
| `applicable_specifications` | `Applicable Specifications` | No | Skip if empty. |
| `confidential` | `Confidential tests or samples?` | No | Skip if empty. |
| `sub_contract` | `Can testing be subcontracted?` | No | Skip if empty. |
| `send_report_copies_to` | `Send copies of test results/reports to:` | No | Skip if empty. |

Efficiency:

- Keep one Word write operation through `write_word_application_form_fields()`.
- Do not add a second Word pass for headers.

### 5. Test Record Header

Current path:

`ConfirmedMatrixTestRecordDocumentGenerationService.generate()` resolves Basic Information header metadata before calling the document writer.

Implementation approach:

- Keep current one-pass writer contract.
- If introducing `TestRecordHeaderIdentity`, adapt `_resolve_header_metadata()` to use it.
- Do not introduce a second Test Record header write-back service.
- Add regression coverage that:
  - missing confirmed Basic Information blocks generation when reader is configured;
  - header metadata comes from confirmed Basic Information;
  - output result still returns Basic Information version/hash for API headers;
  - writer is called once per generation.

### 6. Required Forms Orchestration

Current path already validates Basic Information context.

Implementation approach:

- Keep preview/generate stale-context validation.
- When the shared mapper is introduced, ensure all Required Forms staging outputs use the same `ConfirmedBasicInformationSnapshot` object that passed generate validation.
- Do not alter Project Folder conflict workflow.
- Add/update tests proving the generator receives mapped identity and does not call the Basic Information reader independently per output.

## File-Level Plan

### Create

- `backend/application/project_basic_information_output_identity.py`
  - Shared typed mappers for Fee Form, Customer Feedback, Application Form write-back, and Test Record header identity.
- `tests/unit/test_project_basic_information_output_identity.py`
  - Mapper unit tests for output-specific payloads and no silent fallback.

### Modify

- `backend/application/confirmed_matrix_fee_evaluation_export_service.py`
  - Accept mapper-derived identity while preserving compatibility with existing command payload if needed.
- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
  - Harden tests around `_write_basic_information_identity()` and one-pass workbook generation; implementation change only if tests reveal mapping gaps.
- `backend/application/customer_feedback_form_generation_service.py`
  - Use mapper-derived Customer Feedback identity for Basic Information values.
  - Avoid falling back to project identity when Required Forms has already supplied confirmed Basic Information.
- `backend/infrastructure/office/customer_feedback_workbook_gateway.py`
  - Expand alias matching and fill known header fields.
- `backend/application/project_application_form_write_back_service.py`
  - Move Basic Information mapping to shared mapper; remove silent fallback for modeled fields.
- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
  - Optionally use shared Test Record header mapper while keeping current writer contract.
- `backend/api/dependencies.py`
  - If command payloads become typed, adapt `_RequiredFormsStagingGenerator` to pass mapper-derived payloads.
- `docs/task_board.md`
  - Mark TASK_332 complete after implementation and validation.

### Tests To Modify/Add

- `tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py`
- `tests/unit/test_fee_evaluation_workbook_gateway.py`
- `tests/unit/test_customer_feedback_form_generation_service.py`
- `tests/unit/test_customer_feedback_workbook_gateway.py`
- `tests/unit/test_project_application_form_write_back_service.py`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/unit/test_project_folder_required_forms_service.py`
- `tests/integration/test_project_folder_required_forms_api.py`

## Implementation Tasks

### Task 1: Add Shared Basic Information Output Identity Mapper

- [ ] Write `tests/unit/test_project_basic_information_output_identity.py`.
- [ ] Create `backend/application/project_basic_information_output_identity.py`.
- [ ] Cover Fee, Customer Feedback, Application Form, and Test Record payloads.
- [ ] Verify missing optional values stay empty rather than falling back.
- [ ] Verify generated fixtures, not user desktop files, drive mapper/gateway tests.

Validation:

```powershell
py -m pytest tests/unit/test_project_basic_information_output_identity.py -q
```

### Task 2: Harden Fee Form Header Consumption

- [ ] Add/adjust service tests proving Fee Form receives mapper-derived identity.
- [ ] Add gateway test proving header cells are written in the same matrix-basic workbook generation call.
- [ ] Implement only the minimal mapping/gateway changes needed to pass tests.

Validation:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
```

### Task 3: Expand Customer Feedback Header Filling

- [ ] Add workbook gateway tests using a temporary `.xlsx` with all expected label aliases.
- [ ] Expand alias map and fill logic for phone, email, project leader, lab, received date, estimated completion date, and test item.
- [ ] Add service tests proving Basic Information identity beats project values when supplied.
- [ ] Preserve not-found warnings for template labels that do not exist.

Validation:

```powershell
py -m pytest tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_customer_feedback_workbook_gateway.py -q
```

### Task 4: Harden Application Form Word Write-Back Mapping

- [ ] Add tests where Project/ApplicationForm values intentionally conflict with Basic Information values.
- [ ] Move mapping through the shared output identity mapper.
- [ ] Preserve managed-output fingerprint checks.
- [ ] Keep one Word gateway call.

Validation:

```powershell
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
```

### Task 5: Preserve Test Record One-Pass Basic Information Header Behavior

- [ ] Add/update tests verifying writer call count is one.
- [ ] If useful, adapt header metadata resolution to use `test_record_header_identity()`.
- [ ] Keep `.docx` download API headers unchanged.

Validation:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
```

### Task 6: Required Forms End-To-End Regression

- [ ] Add/update Required Forms service tests showing one confirmed Basic Information context is used for Fee, Customer Feedback, and Test Record staging.
- [ ] Preserve stale Basic Information version/hash rejection.
- [ ] Preserve unmanaged/user-modified output conflict behavior.

Validation:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
```

### Task 7: Documentation And Board Closure

- [ ] Update `docs/task_board.md` with completion notes.
- [ ] Include validation command results.
- [ ] Stop after TASK_332; do not start Report generation or UI orchestration.

## Risk Controls

- Customer Feedback templates may use labels not covered by aliases. Tests should cover known labels and warnings should remain visible for misses.
- `.xls` Fee Form requires Excel COM; unit tests should use fake COM objects where possible and keep real COM smoke optional.
- Application Form Word templates may vary; write-back should remain label-driven through the existing Word gateway.
- Basic Information missing optional fields should not produce mixed-source output. Critical missing fields should block only when the output cannot be meaningfully generated.

## Review Checklist For TASK_332

- [ ] Does every formal output consume confirmed Basic Information for modeled fields?
- [ ] Does any output silently fall back to Project/ApplicationForm/LTR for a modeled field?
- [ ] Does any implementation open the same file once for content and again for header?
- [ ] Are managed-output fingerprint rules preserved?
- [ ] Are no UI, Report, LTR workflow, Basic Information schema/API, Matrix/Fee provider, or StepInstance changes included?

## Required Verification Commands

```powershell
py -m pytest tests/unit/test_project_basic_information_output_identity.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
py -m pytest tests/unit/test_customer_feedback_form_generation_service.py tests/unit/test_customer_feedback_workbook_gateway.py -q
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
git diff --check
```

## Stop Point

When TASK_332 is complete, stop and wait for separate approval before:

- Report header generation.
- LTR sync UI/confirmation workflow.
- Project Folder one-click orchestration changes.
- Basic Information schema/source-provider expansion.
