# TASK_182 Approval Package Generation And Project Folder Placement

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`.
- Current active task in board at creation time: `none; TASK_181 complete`.
- Why this task is allowed now: `TASK_181_TEST_RECORD_TEMPLATE_AND_FEE_FORM_GENERATION` is complete and the next business need is to assemble generated approval-package files into the Project folder structure.
- Implementation gate: approved by user and implemented in this task.

---

## 1. Purpose

Create a controlled backend workflow to preview and then place the project startup approval package into the Project folder.

The approval package is the handoff set for supervisor review before project startup. It should combine existing generated/received materials without re-parsing product specifications or re-inventing document data.

---

## 2. Business Context

The manual approval package currently includes:

- completed application request form;
- generated test record template;
- generated fee evaluation form;
- original e-mail evidence;
- customer submitted materials, including product specifications and supporting documents.

Earlier tasks created the required building blocks:

- `TASK_176`: evidence placement classification rules;
- `TASK_179`: Section 2 application-form write-back;
- `TASK_180`: structured test record and fee dataset preview;
- `TASK_181`: test record and fee document generation.

TASK_182 should assemble these into a coherent approval package placement operation.

---

## 3. Scope

In scope:

- Add a backend application service for approval-package placement preview.
- Add a controlled execution path to copy selected approval package files into the Project folder.
- Reuse existing project folder/evidence placement rules where possible.
- Validate that the target Project folder exists.
- Validate required package inputs:
  - completed application form path;
  - generated test record output path;
  - generated fee evaluation output path when available;
  - evidence/source files to place.
- Return a typed result with planned items, copied items, skipped items, warnings, and blockers.
- Add a backend API endpoint for preview and execution.
- Add unit and integration tests.

Out of scope:

- No new Office generation.
- No pricing calculation.
- No report generation.
- No customer feedback form generation.
- No frontend/UI changes.
- No automatic public-drive upload beyond copying into the configured Project folder path.
- No overwrite of existing files unless this task explicitly implements a safe conflict strategy.

---

## 4. Inputs

Expected command/API input:

```text
project_id
project_folder_path
completed_application_form_path
test_record_output_path
fee_evaluation_output_path: optional
evidence_source_paths[]
execute: bool = false
overwrite: bool = false
```

Data sources:

- existing file paths from TASK_179 and TASK_181 outputs;
- user/operator selected evidence paths;
- existing evidence placement classification rules.

---

## 5. Outputs

Preview/execution result:

```text
project_id
project_folder_path
mode
items[]
warnings[]
blockers[]
```

Item:

```text
source_path
target_relative_path
target_path
classification
status
warnings[]
```

---

## 6. Business Rules

- Preview must be available before execution.
- Execution must copy files only after the preview is blocker-free.
- Existing files must block by default when `overwrite=false`.
- Application form, test record, fee evaluation, product specifications, and supporting submitted materials should go under `Submitted Material`.
- E-mail evidence should go under `E-mail`.
- Classification should reuse TASK_176 rules where possible.
- The service must not mutate Office document contents.
- The service must not mutate New Project intake data or ProjectTestPlanDraft payloads.

---

## 7. Expected Files

Backend/application:

- `backend/application/approval_package_service.py`

Backend/API:

- `backend/api/routes_approval_package.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

Tests:

- `tests/unit/test_approval_package_service.py`
- `tests/integration/test_approval_package_api.py`

Docs:

- `docs/task_182_approval_package_generation_and_project_folder_placement_plan.md`
- `docs/task_board.md`

---

## 8. Proposed API

```text
POST /api/projects/{project_id}/approval-package/preview
POST /api/projects/{project_id}/approval-package/execute
```

Request:

```json
{
  "project_folder_path": "D:/Projects/DL-2026-05-001",
  "completed_application_form_path": "D:/Projects/DL-2026-05-001/Submitted Material/request.docx",
  "test_record_output_path": "D:/Projects/DL-2026-05-001/Submitted Material/test_record.docx",
  "fee_evaluation_output_path": "D:/Projects/DL-2026-05-001/Submitted Material/fee.xls",
  "evidence_source_paths": [],
  "overwrite": false
}
```

---

## 9. Validation Plan

Targeted tests:

```powershell
py -m pytest tests\unit\test_approval_package_service.py tests\integration\test_approval_package_api.py -q
```

Regression:

```powershell
py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py -q
py -m pytest tests\unit\test_test_record_fee_document_generation_service.py tests\integration\test_test_record_fee_document_generation_api.py -q
```

Task board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 10. Acceptance Criteria

- Approval package placement can be previewed without copying files.
- Execution copies files only when preview has no blockers.
- Existing target files are blocked by default.
- E-mail files are placed under `E-mail`.
- Application form, generated test record, generated fee evaluation, and submitted materials are placed under `Submitted Material`.
- No Office file content is modified.
- No frontend code is changed.
- Targeted tests pass.
- `docs/task_board.md` is updated after implementation and validation.

---

## 11. Stop Condition

After implementation and validation:

- update task board;
- record validation;
- stop;
- do not start frontend wiring, status dashboards, report generation, or customer feedback form generation without explicit approval.

---

## 12. Completion Notes

- Added backend approval package service with preview and execute operations.
- Added API endpoints:
  - `POST /api/projects/{project_id}/approval-package/preview`
  - `POST /api/projects/{project_id}/approval-package/execute`
- Added deterministic placement logic:
  - application form, test record, fee evaluation -> `Submitted Material`
  - `.msg` evidence -> `E-mail`
  - other evidence -> `Submitted Material`
- Added overwrite protection and conflict blocking during preview and execute.
- Added lifecycle guard integration:
  - preview uses `EVIDENCE_PREVIEW`
  - execute uses `EVIDENCE_PLACE`
- No Office content editing and no frontend changes.

Validation completed:

```powershell
py -m pytest tests\unit\test_approval_package_service.py tests\integration\test_approval_package_api.py -q
py -m pytest tests\unit\test_evidence_placement_service.py tests\integration\test_evidence_placement_api.py tests\unit\test_test_record_fee_document_generation_service.py tests\integration\test_test_record_fee_document_generation_api.py -q
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Result:

- TASK_182 targeted tests: `5 passed`.
- Evidence + TASK_181 regression: `11 passed`.
- Task-board guard regression: `17 passed`.

Stop condition:

- Stop after TASK_182 completion.
- Do not start the next controlled task without explicit approval.
