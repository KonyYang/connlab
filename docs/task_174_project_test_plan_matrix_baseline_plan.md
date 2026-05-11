# TASK_174 Project Test Plan Matrix Baseline Plan

> Status: proposed for discussion
> Created: 2026-05-11
> Updated: 2026-05-12
> Phase: proposed Phase 11 - Project planning data foundation before downstream document automation
> Current board state at proposal time: Phase 10F, active task `none`

---

## 1. Why This Task Is The Next Important Task

The next business pain is not just project folder creation. The folder is only the container. The real repeated manual work starts before and after folder creation:

- confirm test groups;
- confirm each group step sequence;
- confirm each step condition, method, reference standard, and judgement criteria;
- estimate duration and completion date;
- fill application form Section 2;
- prepare test record tables and fee estimate files;
- later reuse the same information for customer feedback, status tracking, live test data sheets, and report drafts.

If ConnLab only creates folders now, it will reproduce the current manual model inside a better folder. The next controlled task should first create a structured project test-plan baseline from real submitted material, especially product specification Matrix tables.

This task is still not full Matrix implementation, report generation, or AI review. It is a narrow baseline and extraction task that proves ConnLab can preserve the planning data needed by later automation.

---

## 2. Current Code Reality

Observed repository state:

- Project creation, intake, application-form parsing, LTR workbook authority, configured resource settings, and project folder generation already exist.
- `FolderService` can preview and generate a folder from a configured template.
- Folder generation currently copies the application form into a request-like folder, but does not understand test planning content.
- Application form parsing already extracts requested-testing rows and Section 2 lab fields, but Section 2 is not yet generated/updated from a structured test plan.
- External Excel read models exist for standard/equipment resources, but product specification Matrix extraction is not implemented.
- Matrix, Test Record, Report Generation, AI review, and customer feedback automation remain future scope unless explicitly opened.

---

## 3. Proposed Task Goal

Create a read-only project test-plan Matrix baseline service using real submitted materials.

The first task should answer:

1. Can ConnLab identify candidate product specification documents from a project package/folder?
2. Can ConnLab extract or at least preview Matrix-like tables from a real `.docx` product specification?
3. Can ConnLab represent test groups, steps, references, and missing-detail gaps as structured records/DTOs?
4. Can the operator review the extracted baseline before any downstream file or form is modified?

Confirmed business decisions from user discussion:

- The supplied CoolPower product specification sample may be used as a local calibration sample.
- Product specifications can be `.doc`, `.docx`, or `.pdf`, with `.docx` and `.pdf` most common.
- Matrix table headers are generally stable.
- Test group identity is normally based on group name.
- Duration is primarily derived from method/standard content, then adjusted by sample preparation time, report drafting/review time, historical project timing, and engineer judgement.
- Section 2 should eventually be written back into the original application form file because the original email package is preserved.
- Management approval package requires:
  - completed application/request form;
  - test record templates;
  - fee estimate form.
- Email evidence belongs in the generated project folder `E-mail`.
- Customer/specification/supporting documents belong in the generated project folder `Submitted Material`.

Best architectural conclusion:

- ConnLab should not make Word/PDF/Excel files the source of truth.
- ConnLab should also not ignore the file-centric reality of the current workflow.
- The durable source of truth should be a structured `ProjectTestPlan` draft linked to the original files and source locations.
- Existing files remain the operator-facing and management-facing deliverables.
- Every file update should be generated from the structured plan with preview, source traceability, and operator confirmation.

---

## 4. Scope

In scope:

- Add a narrow read-only parser/probe for product specification `.docx` files.
- Add explicit unsupported/deferred handling for `.doc` and `.pdf` product specifications.
- Detect Matrix-like tables from Word document snapshots.
- Extract candidate rows into a structured preview:
  - test group;
  - step/order;
  - test item or operation;
  - condition summary;
  - method/reference section;
  - judgement/acceptance summary when visible;
  - source document path;
  - source table index;
  - source row index;
  - confidence or extraction status.
- Return blockers/warnings for unclear rows instead of guessing.
- Add backend API for previewing a product-spec Matrix baseline from a registered file path or project asset.
- Add tests using synthetic `.docx` fixtures and, if approved, a sanitized real-sample fixture.
- Document the manual validation checklist against the supplied CoolPower example.

Out of scope:

- No automatic Section 2 writing in this task.
- No test record generation in this task.
- No fee estimate generation in this task.
- No report generation or live report updating in this task.
- No AI interpretation in this task.
- No Outlook inbox auto-scan, email sending, LAN deployment, or permissions.
- No mutation of public-drive files.
- No automatic `.doc` to `.docx` conversion in this task.
- No PDF table extraction in this first task unless a deterministic text/table extraction seam already exists.

---

## 5. Data Model Draft

Initial DTOs can remain application-level preview models before database persistence:

```text
ProjectTestPlanPreview
  project_id
  source_document_path
  source_document_name
  generated_at
  groups[]
  warnings[]
  blockers[]

TestGroupPreview
  group_key
  group_label
  steps[]
  source_table_index
  extraction_status

TestStepPreview
  sequence
  step_label
  test_item
  condition_summary
  method_summary
  reference_standard
  judgement_criteria
  estimated_duration_hint
  duration_source
  duration_status
  source_section
  source_table_index
  source_row_index
  warnings[]
```

Database persistence should be deferred unless the preview proves stable. If persistence is needed in the same task, store only a draft snapshot JSON linked to project and source asset, not final normalized Matrix tables.

Recommended eventual normalized model after preview proves stable:

```text
ProjectTestPlan
  project_test_plan_id
  project_id
  source_asset_id
  source_document_path
  status: draft | reviewed | approved | superseded
  version
  created_at
  updated_at

ProjectTestGroup
  group_id
  project_test_plan_id
  group_label
  sequence
  sample_count
  status

ProjectTestStep
  step_id
  group_id
  sequence
  test_item
  condition_summary
  method_summary
  reference_standard
  judgement_criteria
  estimated_duration_hours
  duration_basis
  source_trace
  status
```

Do not implement the normalized persistence model in TASK_174 unless the task is explicitly expanded. TASK_174 should keep the first step small: read-only preview, stable DTOs, and source traceability.

---

## 6. Architecture Design

Recommended boundaries:

- `backend/infrastructure/office/word_document_gateway.py`
  - already provides neutral Word snapshots;
  - should not contain business Matrix logic.
- `backend/application/project_test_plan_matrix_preview_service.py`
  - orchestrates project/source loading and calls parser/probe.
- `backend/modules/test_plan/product_spec_matrix_parser.py`
  - deterministic parser for Matrix-like Word tables.
- `backend/modules/test_plan/duration_hint_parser.py`
  - narrow helper to detect explicit duration text when present.
  - returns hints and source text only; does not invent duration.
- `backend/api/routes_project_test_plan.py`
  - thin typed preview API.
- `tests/unit/test_product_spec_matrix_parser.py`
  - parser behavior.
- `tests/integration/test_project_test_plan_preview_api.py`
  - API smoke and error cases.

Layer rule:

- Domain/application should not directly use Word COM.
- Parser can consume `WordDocumentSnapshot` or `.docx` through an OfficeFacade boundary, but Word-specific IO should remain in infrastructure.
- PDF and legacy `.doc` support should enter through infrastructure gateways later:
  - `.docx`: python-docx first.
  - `.doc`: Microsoft Word COM conversion/read gateway behind OfficeFacade.
  - `.pdf`: separate PDF text/table gateway after sample evaluation.

---

## 7. Proposed API

Option A, project asset based:

```text
POST /api/projects/{project_id}/test-plan/matrix-preview
```

Request:

```json
{
  "source_asset_id": "asset-id"
}
```

Response:

```json
{
  "project_id": "project-id",
  "source_document_name": "GS-12-2113 ... Rev7.doc",
  "groups": [],
  "warnings": [],
  "blockers": []
}
```

Option B, local path based for baseline calibration only:

```text
POST /api/test-plan/matrix-preview-from-path
```

Request:

```json
{
  "source_path": "C:\\Users\\White\\Desktop\\Projects\\..."
}
```

Recommendation:

- Use path-based preview only for controlled local calibration if the file is not yet a registered ConnLab asset.
- Long term, use project asset IDs so the app stays project-centered.

---

## 8. Operator Workflow After This Task

Target workflow after TASK_174:

1. Project has LTR and folder.
2. Submitted material includes application form, email, product specification, and related attachments.
3. Operator selects or confirms the product specification file.
4. ConnLab previews extracted Matrix baseline.
5. Operator sees:
   - test groups;
   - steps;
   - referenced sections;
   - unknown/missing rows;
   - information still requiring manual confirmation.
6. No generated forms are written yet.

This gives a safe bridge from current manual work to later automation.

Longer-term operator workflow target:

1. Import email/package and application form.
2. Apply LTR.
3. Create project folder from template.
4. Place source email under `E-mail` and customer/specification files under `Submitted Material`.
5. Select product specification.
6. Preview Matrix extraction and duration hints.
7. Confirm/edit Project Test Plan.
8. Preview Section 2 updates to the original application form.
9. Write Section 2 back to the application form only after confirmation.
10. Generate or update test record templates and fee estimate form from the confirmed plan.
11. Later, use the same plan as the backbone for status tracking, test data sheets, and incremental report updates.

---

## 9. Follow-Up Task Sequence

Recommended sequence after TASK_174:

1. `TASK_175_PROJECT_TEST_PLAN_REVIEW_AND_DRAFT_PERSISTENCE`
   - let operator edit/confirm extracted groups and steps;
   - persist a draft project test plan snapshot.

2. `TASK_176_PROJECT_FOLDER_EVIDENCE_CLASSIFICATION_FOR_APPROVAL_PACKAGE`
   - ensure email evidence goes to `E-mail`;
   - ensure customer/product specification files go to `Submitted Material`;
   - preserve traceability between assets and generated folder paths.

3. `TASK_177_SECTION2_COMPLETION_PREVIEW`
   - compute Section 2 values from confirmed test plan:
     - lab;
     - assigned personnel;
     - received date;
     - estimated completion date;
     - sample condition;
     - test demand summary.
   - preview only; no Word write yet.

4. `TASK_178_SECTION2_WRITE_BACK_TO_APPLICATION_FORM`
   - write approved Section 2 fields back into the original application form file through the Office boundary.
   - create backup before write.
   - store audit record of fields changed and target file path.

5. `TASK_179_TEST_RECORD_AND_FEE_INPUT_DATASET_PREVIEW`
   - create structured datasets for test record and fee estimation templates.
   - still preview first; document writing remains separate.

6. `TASK_180_TEST_RECORD_TEMPLATE_AND_FEE_FORM_GENERATION`
   - generate approval-package files from confirmed plan and templates.
   - still no report generation.

7. `TASK_181_REPORT_LIVE_DATASET_BASELINE`
   - define report dataset schema so future reports update incrementally from project/test-plan/test-result data.
   - no final report generation yet.

---

## 10. Required User Inputs Before Implementation

Already confirmed:

- CoolPower sample can be used.
- Product specs are mixed `.doc` / `.docx` / `.pdf`, with `.docx` and `.pdf` most common.
- Matrix headers are mostly stable.
- Test group names are the main group identity.
- Duration is based on method/standard plus preparation/report/review/historical/manual adjustments.
- Section 2 should write back to the original application form.
- Approval package requires completed application/request form, test record templates, and fee estimate form.
- Emails and customer documents are stored in project folder evidence locations.

Still needed before implementation:

1. One or more real product specification samples besides CoolPower if layouts vary by product family.
2. One finished historical project folder that includes:
   - final application form with Section 2 filled;
   - test record templates;
   - fee estimate form;
   - product specification;
   - any manually prepared Matrix/test plan file if it exists.
3. The current blank templates for:
   - application form;
   - test record templates;
   - fee estimate form.
4. A short list of common test group names and aliases, for example whether `Group 1`, `Test Group 1`, `Sequence 1`, or customer-specific names appear.
5. Examples of method/standard text where duration is explicitly described.
6. Your preferred time-estimation defaults:
   - sample preparation buffer;
   - report drafting buffer;
   - reviewer approval buffer;
   - working-day calendar assumptions.
7. Whether project duration should use parallel-group scheduling or simple sum of all step durations.

Provided local calibration package on 2026-05-12:

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

Provided scheduling defaults:

- sample preparation: 1 day;
- report drafting: 3 days;
- review: 1 day;
- test group scheduling buffer: 1 day.

Initial file inventory observations:

- All provided paths exist locally.
- The completed historical project has the target folder categories expected by the business flow:
  - `E-mail`;
  - `Submitted Material`;
  - `Photos`;
  - `Test results`.
- The historical project includes management/delivery artifacts:
  - customer feedback workbook;
  - qualification report Word/PDF files;
  - testing fee evaluation `.xls`;
  - submitted request `.docx`;
  - submitted product specification `.doc`;
  - raw result workbooks and equipment/test PDFs.
- The supplied second specification is legacy `.doc`, not `.docx`; TASK_174 should not pretend it can be parsed through python-docx.
- The first specification is PDF; deterministic PDF table extraction should be evaluated as a separate gateway after the `.docx`/`.doc` strategy is clear.
- The supplied third specification is `.docx`, opens with python-docx, and contains 26 Word tables.
- In the third specification, table 21 is a strong first Matrix calibration target:
  - 23 rows;
  - 10 columns;
  - header includes `test Items`, `Section`, `test sequence`;
  - group columns are `Group 1` through `Group 8`;
  - example rows include `Examination of Product`, `Contact Resistance (Low Level)`, and section references such as `5.4`, `6.1`.

Revised implementation implication:

- TASK_174 should include a source-format capability report.
- TASK_174 can now use the EnergyKlip 500A `.docx` sample as the primary real Matrix extraction calibration file.
- TASK_174 can still report the `.doc` and `.pdf` samples as unsupported/deferred or format-gateway candidates.
- Automated tests should still use synthetic `.docx` fixtures, with manual validation against the real EnergyKlip 500A `.docx` sample.

---

## 11. Risks

- Real product specification files may be `.doc`, not `.docx`; python-docx cannot parse `.doc`.
- Real product specification files may be PDF; deterministic PDF table extraction needs separate calibration.
- Matrix table layouts may vary by product family or revision.
- Reference sections may point to narrative paragraphs rather than fully containing method/criteria in the Matrix row.
- Duration estimation may require a separate method-duration knowledge base; guessing duration from text would be unsafe.
- If ConnLab writes Section 2 too early, corrections can become costly. Preview and human confirmation should come first.
- Writing back to the original application form is operationally correct, but requires backup/audit and field-level preview to avoid corrupting the original evidence package.

---

## 12. Acceptance Criteria For TASK_174

- A real or synthetic product specification Matrix-like `.docx` can be parsed into structured preview groups and steps.
- Unclear rows are reported as warnings/blockers, not silently accepted.
- The parser preserves source traceability: table index, row index, section/reference text.
- The preview API is read-only.
- Tests cover at least:
  - happy path group/step extraction;
  - missing Matrix table;
  - ambiguous/missing method or judgement fields;
  - unsupported file type or missing source.
- Task board is updated only after implementation and validation, not during this proposal step.
