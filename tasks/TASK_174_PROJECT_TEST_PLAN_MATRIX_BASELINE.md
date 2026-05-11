# TASK_174 Project Test Plan Matrix Baseline

> Status: proposed; awaiting explicit implementation approval
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 10F`
- Current active task in board at creation time: `none`
- Why this task is allowed now: user explicitly requested creation of the next controlled task after discussing project-management-stage structured test planning.
- Implementation gate: do not write implementation code until the user explicitly approves implementation, for example `批准执行 TASK_174`.

---

## 1. Purpose

Create the first controlled backend foundation for extracting a project test-plan Matrix baseline from product specification files.

This task introduces a read-only preview path that turns Matrix-like product specification content into structured planning data linked to a Project. It is the first step toward later Section 2 write-back, test record template generation, fee evaluation, customer feedback, status tracking, and incremental report data updates.

This task does not implement full Matrix management, test execution records, fee generation, or report generation.

---

## 2. Business Context

Current manual workflow:

1. Review email, application form, product specification, and historical similar projects.
2. Identify test groups and test steps.
3. Read test conditions, methods, reference standards, judgement criteria, and duration from product specification sections.
4. Estimate sample preparation, testing, report drafting, and review schedule.
5. Fill application form Section 2.
6. Prepare test record templates and fee evaluation form.
7. Later reuse the same information for customer feedback, test status, result sheets, and reports.

Target ConnLab direction:

- Keep files as business inputs and deliverables.
- Store structured Project-stage planning data in ConnLab.
- Generate or update downstream files from confirmed structured data with preview, backup, audit, and operator confirmation.

---

## 3. Boundary With New Project Data

`IntakeCase` and `ApplicationDraft` belong to the New Project stage.

`ProjectTestPlan` belongs to the Project Management stage.

Allowed one-way data flow:

```text
IntakePackage / IntakeCase / ApplicationDraft
  -> Confirmed Project
  -> ProjectTestPlan preview
  -> ProjectTestPlan reviewed draft in later task
```

Rules:

- `ProjectTestPlan` must attach to `Project`, not to `ApplicationDraft`.
- `ProjectTestPlan` may preserve `source_case_id`, `source_draft_id`, and source asset references for traceability.
- `ProjectTestPlan` must not mutate intake draft data.
- Later Section 2, test record, fee, status, and report flows must read Project-stage data, not live draft data.

---

## 4. Confirmed Calibration Inputs

Local samples provided by the user:

```text
Product spec sample 1:
D:\Source\2\PRODSPEC GS-12-1941 CoolPowerHD_Rev5.pdf

Product spec sample 2:
D:\Source\2\GS-12-2113 CoolPower HDF 3.40mm product specification_20251219_Rev7.doc

Product spec sample 3:
C:\Users\White\Desktop\AI information\2\PRODSPEC GS-12-2005 EnergyKlip 500A product specification_1.docx

Historical completed project folder:
D:\Source\2\DL-2024-12-050 EK200 Connector Qualification Testing

Application form template:
D:\Source\2\Template\E-3718_H Laboratory Test Request-Even.docx

Test record template:
D:\Source\2\Template\FDQF-E-036 Test Record Template-Even.docx

Fee evaluation template:
D:\Source\2\Template\DL-2025-11-073 Form for Testing Fee Evaluation.xls
```

Scheduling defaults:

- Sample preparation: 1 day.
- Report drafting: 3 days.
- Review: 1 day.
- Test group scheduling buffer: 1 day.

Observed `.docx` calibration fact:

- `PRODSPEC GS-12-2005 EnergyKlip 500A product specification_1.docx` opens with `python-docx`.
- It contains 26 tables.
- Table 21 is a strong Matrix target:
  - 23 rows;
  - 10 columns;
  - headers include `test Items`, `Section`, `test sequence`;
  - columns include `Group 1` through `Group 8`;
  - rows include `Examination of Product`, `Contact Resistance (Low Level)`, and section references such as `5.4`, `6.1`.

---

## 5. Scope

In scope:

- Add read-only backend capability to preview Matrix-like `.docx` product specification data.
- Detect Matrix candidate tables using stable headers such as `test Items`, `Section`, `test sequence`, and `Group N`.
- Extract test groups and ordered test steps from Matrix rows.
- Preserve source traceability:
  - source document path/name;
  - table index;
  - row index;
  - section reference.
- Return warnings/blockers instead of guessing unclear rows.
- Return source-format capability information for `.docx`, `.doc`, and `.pdf`.
- Add deterministic unit tests with synthetic `.docx` fixture data.
- Add a narrow integration/API smoke test.
- Document manual validation against the provided EnergyKlip 500A `.docx` sample.

Out of scope:

- No Section 2 writing.
- No original application form mutation.
- No test record template generation.
- No fee evaluation generation.
- No PDF table extraction.
- No `.doc` conversion or `.doc` parsing.
- No full ProjectTestPlan persistence schema unless explicitly approved as a follow-up.
- No Matrix UI.
- No report generation.
- No AI interpretation.
- No Outlook inbox auto-scan, email sending, LAN deployment, or permissions.

---

## 6. Data Contract

Initial preview DTOs should stay application-level and read-only.

```text
ProjectTestPlanMatrixPreview
  project_id: str | None
  source_document_path: str
  source_document_name: str
  source_format: str
  capability_status: supported | unsupported | deferred
  generated_at: str
  groups: list[TestGroupPreview]
  warnings: list[str]
  blockers: list[str]

TestGroupPreview
  group_key: str
  group_label: str
  steps: list[TestStepPreview]
  source_table_index: int
  extraction_status: extracted | partial | blocked

TestStepPreview
  sequence: int
  test_item: str
  source_section: str | None
  condition_summary: str | None
  method_summary: str | None
  reference_standard: str | None
  judgement_criteria: str | None
  estimated_duration_hint: str | None
  duration_source: str | None
  duration_status: found | missing | deferred
  source_table_index: int
  source_row_index: int
  warnings: list[str]
```

Notes:

- TASK_174 may leave condition/method/standard/judgement/duration fields as `None` or `deferred` when only the Matrix table references sections.
- Later tasks can resolve section narrative details after Matrix group/step extraction is stable.
- Do not create normalized `ProjectTestPlan` persistence in TASK_174 unless explicitly approved.

---

## 7. Architecture Plan

Expected files:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
  - deterministic Matrix table parser.
  - consumes neutral table rows, not API or repository objects.

- `backend/modules/test_plan/duration_hint_parser.py`
  - detects explicit duration text when present.
  - returns only source-backed hints.
  - does not invent estimates.

- `backend/application/project_test_plan_matrix_preview_service.py`
  - validates source path or asset reference.
  - calls Office gateway/snapshot reader.
  - maps parser output into preview DTO.

- `backend/api/routes_project_test_plan.py`
  - thin typed FastAPI route.

- `backend/api/main.py`
  - include the new route.

- `tests/unit/test_product_spec_matrix_parser.py`
  - parser happy path, missing matrix, ambiguous rows.

- `tests/integration/test_project_test_plan_preview_api.py`
  - API smoke and unsupported format handling.

Layering rules:

- API calls application service only.
- Application service may orchestrate source validation and OfficeFacade/gateway usage.
- Infrastructure reads Word/PDF/Office files.
- Parser module contains business parsing rules but no filesystem writes.
- Domain remains free of Office and API dependencies.

---

## 8. Proposed API

Preferred local calibration API:

```text
POST /api/test-plan/matrix-preview-from-path
```

Request:

```json
{
  "source_path": "C:\\Users\\White\\Desktop\\AI information\\2\\PRODSPEC GS-12-2005 EnergyKlip 500A product specification_1.docx",
  "project_id": null
}
```

Response:

```json
{
  "project_id": null,
  "source_document_name": "PRODSPEC GS-12-2005 EnergyKlip 500A product specification_1.docx",
  "source_format": ".docx",
  "capability_status": "supported",
  "groups": [],
  "warnings": [],
  "blockers": []
}
```

Future project-asset API, not required unless implementation finds it already cheap and safe:

```text
POST /api/projects/{project_id}/test-plan/matrix-preview
```

Request:

```json
{
  "source_asset_id": "asset-id"
}
```

---

## 9. Parsing Rules For First Version

Matrix candidate table:

- Must contain a row with test item header similar to `test Items`.
- Must contain `Section`.
- Must contain group columns matching `Group <number>`.
- Must contain at least one body row with a test item and one group sequence cell.

Step expansion:

- For each Matrix row, read each group column.
- Split sequence cell by comma.
- For every sequence number, create a `TestStepPreview`.
- Sort each group by sequence ascending.
- Preserve duplicate sequence warnings instead of silently discarding.

Example:

```text
Contact Resistance (Low Level) | 6.1 | Group 1 = 2,5,8
```

Becomes:

```text
Group 1:
  sequence 2 -> Contact Resistance (Low Level), section 6.1
  sequence 5 -> Contact Resistance (Low Level), section 6.1
  sequence 8 -> Contact Resistance (Low Level), section 6.1
```

---

## 10. Validation Plan

Automated tests:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py -q
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
```

Recommended broader backend smoke:

```powershell
py -m pytest tests\unit tests\integration -q
```

Manual validation:

1. Run preview against:
   `C:\Users\White\Desktop\AI information\2\PRODSPEC GS-12-2005 EnergyKlip 500A product specification_1.docx`
2. Confirm Matrix table 21 is selected.
3. Confirm `Group 1` through `Group 8` are extracted.
4. Confirm known rows such as `Examination of Product` and `Contact Resistance (Low Level)` appear under expected groups and sequence numbers.
5. Run preview against `.doc` and `.pdf` samples and confirm they return clear unsupported/deferred capability responses, not crashes.

---

## 11. Acceptance Criteria

- `.docx` Matrix preview extracts groups and ordered steps from a Matrix-like table.
- Parser preserves source document, table index, row index, group label, sequence number, and section reference.
- Unsupported `.doc` and `.pdf` inputs return clear capability blockers.
- No source files are modified.
- No Section 2, test record, fee, or report files are generated or modified.
- Tests cover happy path, missing Matrix table, malformed sequence cells, duplicate sequence warnings, and unsupported formats.
- `docs/task_board.md` is updated after implementation and validation.

---

## 12. Follow-Up Sequence

Recommended next controlled tasks after TASK_174:

1. `TASK_175_PROJECT_TEST_PLAN_REVIEW_AND_DRAFT_PERSISTENCE`
2. `TASK_176_PROJECT_FOLDER_EVIDENCE_CLASSIFICATION_FOR_APPROVAL_PACKAGE`
3. `TASK_177_SECTION2_COMPLETION_PREVIEW`
4. `TASK_178_SECTION2_WRITE_BACK_TO_APPLICATION_FORM`
5. `TASK_179_TEST_RECORD_AND_FEE_INPUT_DATASET_PREVIEW`
6. `TASK_180_TEST_RECORD_TEMPLATE_AND_FEE_FORM_GENERATION`
7. `TASK_181_REPORT_LIVE_DATASET_BASELINE`

---

## 13. Approval Gate

This task file defines the controlled implementation scope.

Do not implement until the user explicitly approves with wording equivalent to:

```text
批准执行 TASK_174
```

