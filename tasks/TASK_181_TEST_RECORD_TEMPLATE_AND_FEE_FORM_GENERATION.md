# TASK_181 Test Record Template And Fee Form Generation

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`.
- Current active task in board at creation time: `none; TASK_180 complete`.
- Why this task is allowed now: `TASK_180_TEST_RECORD_AND_FEE_INPUT_DATASET_PREVIEW` is complete and the task board recommends `TASK_181_TEST_RECORD_TEMPLATE_AND_FEE_FORM_GENERATION` as the next controlled task.
- Implementation gate: approved by user and implemented in this task.
- Model note: this task is suitable for `gpt-5.3-codex` because it is implementation-heavy, test-heavy, and bounded by existing backend/Office infrastructure boundaries.

---

## 1. Purpose

Generate the first controlled approval-package documents from the structured `ProjectTestPlanDraft`/TASK_180 dataset path:

- test record template document;
- fee evaluation form document/workbook.

The purpose is not to make a final report generator. It is to turn the already-reviewed test-plan dataset into operator-reviewable Office files that can be placed in the project folder and submitted for project startup approval.

---

## 2. Business Context

After Section 2 write-back and dataset preview, the approval package still requires files that are currently prepared manually:

- completed application request form;
- test record template;
- fee evaluation form.

TASK_181 addresses only the second and third items. The completed application request form is already covered by TASK_179.

---

## 3. Scope

In scope:

- Add a backend application service that uses the TASK_180 dataset preview as its data source.
- Add template/input path validation for test record and fee evaluation templates.
- Generate a test record `.docx` output through the Office infrastructure boundary.
- Generate a fee evaluation output through the Office infrastructure boundary.
- For legacy `.xls` fee templates, keep all Excel write behavior behind an infrastructure gateway; application/API code must not call COM directly.
- Return a typed result with output paths, generated sections/sheets, warnings, and skipped fields.
- Add a backend API endpoint.
- Add unit and integration tests using temporary files and fake gateway seams where real Office COM is not available.

Out of scope:

- No frontend/UI changes.
- No report generation.
- No customer feedback form generation.
- No test status dashboard.
- No pricing database or automatic price calculation.
- No direct COM calls from application or API layers.
- No mutation of product specifications, application drafts, Matrix drafts, or New Project intake data.
- No overwrite of existing generated files unless the task explicitly implements a safe conflict strategy.

---

## 4. Inputs

Expected command/API input:

```text
project_id
draft_id
test_record_template_path
fee_evaluation_template_path
output_dir
overwrite: bool = false
include_test_record: bool = true
include_fee_evaluation: bool = true
```

Primary structured data source:

- Project-stage `ProjectTestPlanDraft.payload_json` via TASK_180 dataset preview service.

Templates:

- Test record template: expected `.docx`.
- Fee evaluation template: expected `.xls` or `.xlsx`; `.xls` requires Excel COM gateway availability.

---

## 5. Outputs

Generation result:

```text
project_id
draft_id
test_record_output_path
fee_evaluation_output_path
generated_files[]
warnings[]
```

Generated file entry:

```text
kind
source_template_path
output_path
status
warnings[]
```

---

## 6. Business Rules

- Generation must be based on Project-stage test-plan draft data, not New Project draft data.
- Superseded drafts must be rejected through the TASK_180 dataset preview path.
- Missing method/condition/reference/judgement/duration fields must remain visible as warnings; do not invent values.
- Fee generation must not invent prices.
- Existing output files must block generation when `overwrite=false`.
- Office writes must stay behind infrastructure gateways.
- The service must be testable without requiring local Microsoft Office.

---

## 7. Expected Files

Backend/application:

- `backend/application/test_record_fee_document_generation_service.py`

Backend/infrastructure Office:

- `backend/infrastructure/office/test_record_document_gateway.py`
- `backend/infrastructure/office/fee_evaluation_workbook_gateway.py`
- `backend/infrastructure/office/models.py`
- `backend/infrastructure/office/__init__.py`

Backend/API:

- `backend/api/routes_test_record_fee_document_generation.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

Tests:

- `tests/unit/test_test_record_fee_document_generation_service.py`
- `tests/unit/test_test_record_document_gateway.py`
- `tests/unit/test_fee_evaluation_workbook_gateway.py`
- `tests/integration/test_test_record_fee_document_generation_api.py`

Docs:

- `docs/task_181_test_record_template_fee_form_generation_plan.md`
- `docs/task_board.md`

---

## 8. Proposed API

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-documents/generate
```

Request:

```json
{
  "test_record_template_path": "D:/Source/2/Template/FDQF-E-036 Test Record Template-Even.docx",
  "fee_evaluation_template_path": "D:/Source/2/Template/DL-2025-11-073 Form for Testing Fee Evaluation.xls",
  "output_dir": "D:/Project/DL-XXXX/Submitted Material",
  "overwrite": false,
  "include_test_record": true,
  "include_fee_evaluation": true
}
```

Response:

```json
{
  "project_id": "project-id",
  "draft_id": "draft-id",
  "generated_files": [],
  "warnings": []
}
```

---

## 9. Validation Plan

Targeted tests:

```powershell
py -m pytest tests\unit\test_test_record_fee_document_generation_service.py tests\unit\test_test_record_document_gateway.py tests\unit\test_fee_evaluation_workbook_gateway.py tests\integration\test_test_record_fee_document_generation_api.py -q
```

Regression:

```powershell
py -m pytest tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
```

Task board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 10. Acceptance Criteria

- Test record document generation can create a `.docx` output from a template and TASK_180 dataset.
- Fee evaluation generation can create an output from a supported template path through an infrastructure gateway.
- Legacy `.xls` handling is isolated behind an Office gateway and can be skipped or reported as unavailable when COM support is unavailable.
- Existing output files are not overwritten by default.
- Missing dataset fields produce warnings, not fabricated content.
- No Office writes occur in API route bodies or application service internals.
- No frontend code is changed.
- Targeted tests pass.
- `docs/task_board.md` is updated after implementation and validation.

---

## 11. Stop Condition

After implementation and validation:

- update task board;
- record validation;
- stop;
- do not start frontend wiring, report generation, customer feedback form generation, or status dashboard work without explicit approval.

---

## 12. Completion Notes

- Added backend generation service using TASK_180 dataset preview as the only structured source.
- Added API endpoint: `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-documents/generate`.
- Added Office infrastructure gateways:
  - test record `.docx` generation through `python-docx`.
  - fee workbook generation through Excel COM gateway boundary.
- Added controlled behavior for unavailable fee-generation COM runtime:
  - return `skipped_unavailable` for fee output entry instead of cross-layer failure.
- Added strict validation for include flags, template existence/type, output directory, and overwrite conflicts.
- No frontend/UI changes.

Validation completed:

```powershell
py -m pytest tests\unit\test_test_record_fee_document_generation_service.py tests\unit\test_test_record_document_gateway.py tests\unit\test_fee_evaluation_workbook_gateway.py tests\integration\test_test_record_fee_document_generation_api.py -q
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Result:

- TASK_181 targeted tests: `9 passed`.
- Draft + TASK_180 regression: `14 passed`.
- Task-board guard regression: `17 passed`.

Stop condition:

- Stop after TASK_181 completion.
- Do not start next controlled task without explicit user approval.
