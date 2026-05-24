# TASK_179 Section 2 Write Back To Application Form

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`
- Current active task in board at creation time: `none; TASK_178 complete`
- Why this task is allowed now: `TASK_177_SECTION2_COMPLETION_PREVIEW` is complete and `TASK_178_NEW_PROJECT_INTAKE_LOGIC_FIXES` is complete; the task board recommends `TASK_179_SECTION2_WRITE_BACK_TO_APPLICATION_FORM` as the next controlled task.
- Implementation gate: this task file and plan define the implementation scope; do not write implementation code until the user explicitly approves this task, for example `批准执行 TASK_179`.

---

## 1. Purpose

Write approved Section 2 preview values back to the original application form `.docx` through the Office infrastructure boundary.

The goal is controlled write-back, not a general Word editing tool.

---

## 2. Business Context

TASK_177 computes Section 2 values from Project-stage `ProjectTestPlanDraft` data. The current business workflow requires the original application/request form in the preserved email package to be completed and used in the approval package.

This task performs the first controlled write-back step:

1. operator confirms preview values;
2. ConnLab creates a backup of the target application form;
3. ConnLab writes only approved Section 2 fields;
4. ConnLab returns an audit-style result describing changed fields and backup path.

---

## 3. Scope

In scope:

- Add a Word infrastructure gateway method for Section 2 `.docx` write-back.
- Add an application service that:
  - verifies Project and Project test-plan draft ownership;
  - validates target application-form path;
  - computes or accepts approved Section 2 values from TASK_177 preview inputs;
  - creates a backup before write;
  - calls the Word gateway through `OfficeFacade`;
  - returns a structured write-back result.
- Add a typed API endpoint for write-back.
- Add tests for service/gateway/API behavior using temporary `.docx` fixtures.

Out of scope:

- No frontend/UI button.
- No `.doc` write-back.
- No PDF write-back.
- No test record generation.
- No fee evaluation generation.
- No report generation.
- No AI interpretation.
- No broad Word template engine.
- No writing public-drive files without an explicit target path supplied by the approved request.

---

## 4. Inputs

Expected API input:

```text
project_id
draft_id
target_application_form_path
received_date
lab
assigned_personnel
sample_condition
sample_preparation_days
test_group_scheduling_buffer_days
report_drafting_days
review_days
operator
```

The service may reuse `Section2CompletionPreviewService` to compute:

- estimated completion date;
- test demand summary;
- duration summary;
- warnings.

---

## 5. Outputs

Write-back result:

```text
project_id
draft_id
target_application_form_path
backup_path
changed_fields[]
unchanged_fields[]
warnings[]
written_at
operator
```

Changed field item:

```text
field_key
label
old_value
new_value
location
```

---

## 6. Business Rules

- Only `.docx` is supported in this task.
- The target file must exist before execution.
- A backup must be created before mutation.
- The write must be limited to Section 2 fields:
  - lab;
  - assigned personnel;
  - received date;
  - estimated completion date;
  - sample condition;
  - test demand / requested testing summary only if a matching Section 2 location exists.
- If a required Section 2 label/location cannot be found, the service must fail or return a blocker before write. Do not guess arbitrary cells.
- The application service must not import `docx` or `win32com`.
- The API route must stay thin and typed.
- The original application form file is mutated only after backup succeeds.

---

## 7. Expected Files

Backend:

- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/infrastructure/office/models.py`
- `backend/application/section2_write_back_service.py`
- `backend/api/routes_section2_write_back.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

Tests:

- `tests/unit/test_section2_write_back_service.py`
- `tests/unit/test_word_document_section2_write_gateway.py`
- `tests/integration/test_section2_write_back_api.py`

Docs:

- `docs/task_179_section2_write_back_plan.md`
- `docs/task_board.md`

---

## 8. Proposed API

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-write-back
```

Request:

```json
{
  "target_application_form_path": "D:\\\\...\\\\E-3718 request.docx",
  "received_date": "2026-05-12",
  "lab": "Connector Lab",
  "assigned_personnel": "White",
  "sample_condition": "Good condition",
  "sample_preparation_days": 1,
  "test_group_scheduling_buffer_days": 1,
  "report_drafting_days": 3,
  "review_days": 1,
  "operator": "White"
}
```

Response:

```json
{
  "project_id": "project-id",
  "draft_id": "draft-id",
  "target_application_form_path": "D:\\\\...\\\\E-3718 request.docx",
  "backup_path": "D:\\\\...\\\\E-3718 request.docx.bak-20260512-153000",
  "changed_fields": [],
  "unchanged_fields": [],
  "warnings": [],
  "written_at": "2026-05-12T15:30:00+08:00",
  "operator": "White"
}
```

---

## 9. Validation Plan

Targeted tests:

```powershell
py -m pytest tests\unit\test_section2_write_back_service.py tests\unit\test_word_document_section2_write_gateway.py tests\integration\test_section2_write_back_api.py -q
```

Regression:

```powershell
py -m pytest tests\unit\test_section2_completion_preview_service.py tests\integration\test_section2_completion_preview_api.py -q
```

Task board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 10. Acceptance Criteria

- Write-back can update known Section 2 fields in a `.docx` fixture.
- Backup is created before write.
- Missing target file is rejected.
- Non-`.docx` target is rejected.
- Missing Section 2 locations are rejected without mutating the target.
- API returns changed fields, backup path, warnings, and written timestamp.
- Application service does not import `docx` or `win32com`.
- No frontend/UI changes.
- No test record, fee, or report output.
- Targeted tests pass.

---

## 11. Stop Condition

After implementation and validation:

- update task board;
- record validation;
- stop;
- do not start the next task without explicit approval.

---

## 12. Completion Notes

Implemented:

- Added controlled `.docx` Section 2 write-back through the Office infrastructure boundary.
- Added Word gateway models for changed/unchanged Section 2 field results.
- Added `WordDocumentGateway.write_section2_fields()` and `OfficeFacade.write_word_section2_fields()`.
- Added `Section2WriteBackService` that:
  - reuses TASK_177 Section 2 preview calculation;
  - validates target `.docx`;
  - creates a backup before write;
  - writes only supported Section 2 fields;
  - returns changed fields, unchanged fields, warnings, backup path, written timestamp, and operator.
- Added `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-write-back`.

Preserved boundaries:

- No frontend/UI changes.
- No `.doc` or PDF write-back.
- No test record, fee evaluation, or report generation.
- Application service does not import `docx` or `win32com`.
- Word mutation stays behind `backend/infrastructure/office`.

Validation:

- `py -m pytest tests\unit\test_section2_write_back_service.py tests\unit\test_word_document_section2_write_gateway.py tests\integration\test_section2_write_back_api.py -q` passed, 8 passed.
- `py -m pytest tests\unit\test_section2_completion_preview_service.py tests\integration\test_section2_completion_preview_api.py -q` passed, 6 passed.
- `py -m pytest tests\unit\test_office_integration_boundary.py -q` passed, 7 passed.
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed, 17 passed.
