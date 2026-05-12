# TASK_177 Section 2 Completion Preview Plan

> Status: proposed for review
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 1. Goal

Build a read-only Section 2 preview from `ProjectTestPlanDraft` data.

The task must answer: if the operator approved the current Project test-plan draft, what values would ConnLab propose for application form Section 2 before any Word file is modified?

---

## 2. Inputs

- `project_id`
- `draft_id`
- `received_date`
- optional lab values:
  - `lab`
  - `assigned_personnel`
  - `sample_condition`
- scheduling buffers:
  - `sample_preparation_days`
  - `test_group_scheduling_buffer_days`
  - `report_drafting_days`
  - `review_days`
- persisted `ProjectTestPlanDraft.payload`

Default business buffers can match the current user-provided baseline:

- sample preparation: 1 day
- test group scheduling: 1 day
- report drafting: 3 days
- review: 1 day

---

## 3. Outputs

Return a typed preview object:

- project and draft identity;
- source document name;
- received date;
- estimated completion date;
- lab;
- assigned personnel;
- sample condition;
- test demand summary;
- duration summary;
- warnings.

No file is created or changed.

---

## 4. Design

### Application Service

Add `Section2CompletionPreviewService`.

Responsibilities:

- load the Project-scoped draft via existing draft store/repository;
- reject missing, cross-project, or superseded drafts;
- extract group and step labels from `payload`;
- build a compact test demand summary;
- calculate total preview duration in calendar days;
- return warnings for missing explicit test durations.

### Duration Rule

First version:

```text
total_estimated_days =
  sample_preparation_days
  + test_group_scheduling_buffer_days
  + explicit_test_duration_days
  + report_drafting_days
  + review_days
```

`explicit_test_duration_days` is `0` unless the draft payload contains deterministic duration fields from previous extraction. Missing explicit durations must create a warning.

### API

Add:

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-preview
```

The route stays thin and calls the application service only.

---

## 5. File-Level Changes

Expected implementation files:

- `backend/application/section2_completion_preview_service.py`
- `backend/api/routes_section2_completion_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_section2_completion_preview_service.py`
- `tests/integration/test_section2_completion_preview_api.py`

Documentation and control files:

- `tasks/TASK_177_SECTION2_COMPLETION_PREVIEW.md`
- `docs/task_board.md`
- phase scope guard tests, only if needed for the new task-board state.

---

## 6. Risks

- Product-spec Matrix rows often reference narrative sections; explicit duration may be unavailable.
- Calendar-day addition is simpler than the lab's real workday scheduling.
- If this task tries to write Word files, it would skip the required preview/approval boundary.
- If it reads New Project draft data directly, it would violate the Project Management data boundary established in TASK_175.

---

## 7. Validation

Targeted:

```powershell
py -m pytest tests\unit\test_section2_completion_preview_service.py tests\integration\test_section2_completion_preview_api.py -q
```

Regression:

```powershell
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
```

Static task-board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 8. Approval Gate

This plan is only the executable design. Implementation starts only after explicit approval, for example:

```text
批准执行 TASK_177
```
