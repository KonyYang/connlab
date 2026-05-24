# TASK_180 Test Record And Fee Input Dataset Preview

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`
- Current active task in board at creation time: `none; TASK_179 complete`
- Why this task is allowed now: `TASK_179_SECTION2_WRITE_BACK_TO_APPLICATION_FORM` is complete, and the task board recommends `TASK_180_TEST_RECORD_AND_FEE_INPUT_DATASET_PREVIEW` as the next controlled task.
- Implementation gate: approved by user and implemented in this task.

---

## 1. Purpose

Create a read-only structured input dataset preview for later test record template generation and fee evaluation form generation.

This task does not generate or modify Word/Excel files. It only turns the reviewed Project test-plan draft into stable JSON-style datasets that downstream document-generation tasks can consume.

---

## 2. Business Context

After Section 2 preview/write-back, the approval package still needs:

- test record templates;
- fee evaluation inputs.

The current manual process repeatedly copies test groups, steps, methods, conditions, standards, durations, sample quantities, and project metadata into multiple files. ConnLab should first create a structured intermediate dataset so later template generation does not re-parse specifications or manually reconstruct the same data.

---

## 3. Scope

In scope:

- Add a backend application service that reads a Project-scoped `ProjectTestPlanDraft`.
- Produce a test-record input dataset preview:
  - project identity;
  - source document traceability;
  - test groups;
  - test steps;
  - method/condition/reference/judgement fields where available;
  - duration hints where available;
  - warnings for missing fields.
- Produce a fee-evaluation input dataset preview:
  - project identity;
  - groups and step counts;
  - duration summary;
  - fee line candidates with missing-price warnings;
  - no calculated price unless an explicit price source is provided in future tasks.
- Add a read-only API endpoint.
- Add unit and integration tests.

Out of scope:

- No test record `.docx` generation.
- No fee evaluation `.xls` generation.
- No template write-back.
- No Office COM automation.
- No Excel/Word mutation.
- No price database.
- No frontend/UI changes.
- No report generation.
- No customer feedback form generation.

---

## 4. Inputs

Expected input:

```text
project_id
draft_id
include_fee_dataset: bool = true
include_test_record_dataset: bool = true
```

Data source:

- persisted `ProjectTestPlanDraft.payload_json`

Optional later sources, not implemented in this task:

- sample records;
- standard/equipment Excel read models;
- price table;
- historical duration/fee data.

---

## 5. Outputs

Preview response:

```text
project_id
draft_id
source_document_name
test_record_dataset
fee_dataset
warnings[]
```

Test record dataset:

```text
groups[]
  group_key
  group_label
  source_table_index
  steps[]
    sequence
    test_item
    condition_summary
    method_summary
    reference_standard
    judgement_criteria
    duration_hint
    source_section
    source_table_index
    source_row_index
    warnings[]
```

Fee dataset:

```text
summary
  group_count
  step_count
  explicit_duration_days
line_items[]
  group_label
  sequence
  description
  duration_hint
  quantity_basis
  pricing_status
  warnings[]
```

---

## 6. Business Rules

- The service must read Project-stage `ProjectTestPlanDraft`, not New Project draft data.
- Cross-project drafts must be rejected.
- Superseded drafts must be rejected.
- Missing method/condition/reference/judgement fields should produce warnings, not invented values.
- Fee preview must not invent prices.
- Dataset preview must be deterministic and JSON serializable.
- No Office files are written.

---

## 7. Expected Files

Backend:

- `backend/application/test_record_fee_dataset_preview_service.py`
- `backend/api/routes_test_record_fee_dataset_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`

Tests:

- `tests/unit/test_test_record_fee_dataset_preview_service.py`
- `tests/integration/test_test_record_fee_dataset_preview_api.py`

Docs:

- `docs/task_180_test_record_fee_dataset_preview_plan.md`
- `docs/task_board.md`

---

## 8. Proposed API

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-dataset-preview
```

Request:

```json
{
  "include_test_record_dataset": true,
  "include_fee_dataset": true
}
```

Response:

```json
{
  "project_id": "project-id",
  "draft_id": "draft-id",
  "source_document_name": "spec.docx",
  "test_record_dataset": {
    "groups": []
  },
  "fee_dataset": {
    "summary": {
      "group_count": 0,
      "step_count": 0,
      "explicit_duration_days": 0
    },
    "line_items": []
  },
  "warnings": []
}
```

---

## 9. Validation Plan

Targeted tests:

```powershell
py -m pytest tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q
```

Regression:

```powershell
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
```

Task board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 10. Acceptance Criteria

- Dataset preview can be generated for an existing Project test-plan draft.
- Unknown Project IDs are rejected.
- Unknown/cross-project draft IDs are rejected.
- Superseded drafts are rejected.
- Test-record dataset preserves group/step/source traceability.
- Fee dataset provides line candidates and missing-price warnings without calculating price.
- Missing method/condition/reference/judgement fields produce warnings.
- No Office files are written.
- No templates are generated.
- Targeted tests pass.
- `docs/task_board.md` is updated after implementation and validation.

---

## 11. Stop Condition

After implementation and validation:

- update task board;
- record validation;
- stop;
- do not start document generation without explicit approval.
---

## 12. Completion Notes

- Added read-only backend dataset preview from Project-stage `ProjectTestPlanDraft` data.
- Added typed API endpoint `POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-dataset-preview`.
- Test record dataset preserves group, step, source table/row/section, method, condition, reference, judgement, duration hints, and per-step warnings.
- Fee dataset provides group/step summary, explicit duration total, line-item candidates, and missing-price warnings without calculating price.
- Missing Project, missing/cross-project draft, superseded draft, and disabled-both-datasets cases are rejected.
- No Office files are written; no templates are generated; no frontend changes are included.

Validation completed:

```powershell
py -m pytest tests\unit\test_test_record_fee_dataset_preview_service.py tests\integration\test_test_record_fee_dataset_preview_api.py -q
py -m pytest tests\unit\test_project_test_plan_draft_service.py tests\integration\test_project_test_plan_draft_api.py -q
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Result:

- TASK_180 targeted tests: `7 passed`.
- Project test-plan draft regression: `7 passed`.
- Task-board guard regression: `17 passed`.

Stop condition:

- Stop after TASK_180 completion.
- Do not start test record template or fee form generation without explicit approval of the next task.

