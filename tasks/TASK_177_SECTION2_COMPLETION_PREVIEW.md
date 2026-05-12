# TASK_177 Section 2 Completion Preview

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`
- Current active task in board at creation time: `none; TASK_176 complete`
- Why this task is allowed now: `TASK_176_PROJECT_FOLDER_EVIDENCE_CLASSIFICATION_FOR_APPROVAL_PACKAGE` is complete, and the task board recommends `TASK_177_SECTION2_COMPLETION_PREVIEW` as the next controlled task.
- Implementation gate: this task file and plan define the implementation scope; do not write implementation code until the user explicitly approves this task, for example `批准执行 TASK_177`.

---

## 1. Purpose

Create a read-only Section 2 completion preview from Project-stage planning data.

This task computes the values that should later fill application form Section 2, but it must not write to Word files. The output is an operator-reviewable preview that can be inspected before a future write-back task.

---

## 2. Business Context

After TASK_174 and TASK_175, ConnLab can extract a product specification Matrix preview and persist a Project test-plan draft. TASK_177 uses that structured draft plus controlled scheduling defaults to preview Section 2 values:

- lab;
- assigned personnel;
- received date;
- estimated completion date;
- sample condition;
- requested testing / test demand summary;
- planning notes and warnings.

The preview becomes the safe bridge before `TASK_179_SECTION2_WRITE_BACK_TO_APPLICATION_FORM`.

---

## 3. Scope

In scope:

- Add an application service that reads a Project test-plan draft snapshot and computes Section 2 preview data.
- Support explicit scheduling buffers:
  - sample preparation days;
  - test group scheduling buffer days;
  - report drafting days;
  - review days.
- Compute estimated completion date from a provided received date and duration inputs.
- Produce a compact test demand summary from draft groups and steps.
- Return warnings when duration data is missing or cannot be trusted.
- Add a read-only API endpoint for Section 2 preview.
- Add unit and integration tests.

Out of scope:

- No Word write-back.
- No Office COM automation.
- No mutation of the original application form.
- No test record generation.
- No fee evaluation generation.
- No report generation.
- No frontend/UI changes.
- No PDF or `.doc` parsing.
- No historical project duration learning model.
- No working-day holiday calendar unless explicitly added in a future task.

---

## 4. Input Data

Primary input:

- `project_id`
- `draft_id`
- `received_date`
- optional operator-provided Section 2 values:
  - `lab`
  - `assigned_personnel`
  - `sample_condition`
- scheduling defaults:
  - `sample_preparation_days`
  - `test_group_scheduling_buffer_days`
  - `report_drafting_days`
  - `review_days`

Draft source:

- persisted `ProjectTestPlanDraft.payload`

---

## 5. Output Data

Preview response:

```text
Section2CompletionPreview
  project_id
  draft_id
  source_document_name
  received_date
  estimated_completion_date
  lab
  assigned_personnel
  sample_condition
  test_demand_summary
  duration_summary
  warnings[]
```

Duration summary:

```text
sample_preparation_days
test_group_scheduling_buffer_days
explicit_test_duration_days
report_drafting_days
review_days
total_estimated_days
duration_basis
```

---

## 6. Business Rules

- The service must read Project-stage `ProjectTestPlanDraft`, not New Project `ApplicationDraft`.
- Cross-project draft access must be rejected.
- Superseded drafts should not be used for Section 2 preview unless future tasks explicitly allow a historical preview mode.
- If no explicit test duration can be derived from draft payload, the preview may still compute using operator/default buffers and must emit a warning.
- Estimated completion date is a preview value only.
- Calendar logic for this task is simple calendar-day addition; working-day calendar support is deferred.
- All source uncertainties must appear as warnings, not hidden assumptions.

---

## 7. Expected Files

Backend:

- `backend/application/section2_completion_preview_service.py`
- `backend/api/routes_section2_completion_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

Tests:

- `tests/unit/test_section2_completion_preview_service.py`
- `tests/integration/test_section2_completion_preview_api.py`

Docs:

- `docs/task_177_section2_completion_preview_plan.md`
- `docs/task_board.md`

---

## 8. Proposed API

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-preview
```

Request:

```json
{
  "received_date": "2026-05-12",
  "lab": "Connector Lab",
  "assigned_personnel": "White",
  "sample_condition": "Good condition",
  "sample_preparation_days": 1,
  "test_group_scheduling_buffer_days": 1,
  "report_drafting_days": 3,
  "review_days": 1
}
```

Response:

```json
{
  "project_id": "project-id",
  "draft_id": "draft-id",
  "source_document_name": "PRODSPEC ... .docx",
  "received_date": "2026-05-12",
  "estimated_completion_date": "2026-05-18",
  "lab": "Connector Lab",
  "assigned_personnel": "White",
  "sample_condition": "Good condition",
  "test_demand_summary": "Group 1: Examination of Product; Group 2: Contact Resistance...",
  "duration_summary": {
    "sample_preparation_days": 1,
    "test_group_scheduling_buffer_days": 1,
    "explicit_test_duration_days": 0,
    "report_drafting_days": 3,
    "review_days": 1,
    "total_estimated_days": 6,
    "duration_basis": "calendar_days_preview"
  },
  "warnings": []
}
```

---

## 9. Validation Plan

Targeted tests:

```powershell
py -m pytest tests\unit\test_section2_completion_preview_service.py tests\integration\test_section2_completion_preview_api.py -q
```

Related regression:

```powershell
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
```

Task board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 10. Acceptance Criteria

- Section 2 preview can be computed for an existing Project test-plan draft.
- The API rejects unknown projects, unknown drafts, cross-project drafts, and superseded drafts.
- Estimated completion date is computed from received date plus preview duration components.
- Test demand summary is derived from draft groups/steps without reparsing source files.
- Missing explicit duration data produces a warning instead of guessed test duration.
- No New Project draft data is mutated.
- No Office file is written.
- No application form Section 2 write-back is performed.
- Targeted tests pass.
- `docs/task_board.md` is updated after implementation and validation.

---

## 11. Stop Condition

After implementation and validation:

- update task board;
- record validation;
- stop;
- do not start `TASK_178` without explicit approval.

---

## 12. Completion Notes

Implemented:

- Added a read-only `Section2CompletionPreviewService` that computes Section 2 preview values from Project-stage `ProjectTestPlanDraft` data.
- Added calendar-day duration calculation from:
  - sample preparation days;
  - test group scheduling buffer days;
  - explicit test duration days already present in draft payload;
  - report drafting days;
  - review days.
- Added warning behavior when no explicit test duration is available in the draft payload.
- Added compact test demand summary generation from draft groups and steps.
- Added `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-preview`.
- Rejected unknown projects, unknown/cross-project drafts, superseded drafts, and invalid negative duration buffers.

Preserved boundaries:

- No Word write-back.
- No Office COM automation.
- No original application form mutation.
- No New Project draft mutation.
- No test record, fee evaluation, or report generation.

Validation:

- `py -m pytest tests\unit\test_section2_completion_preview_service.py tests\integration\test_section2_completion_preview_api.py -q` passed, 6 passed.
- `py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q` passed, 7 passed.
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed, 17 passed.
