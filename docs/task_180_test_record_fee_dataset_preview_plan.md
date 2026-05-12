# TASK_180 Test Record And Fee Dataset Preview Plan

> Status: proposed for review
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 1. Goal

Create read-only structured datasets for two downstream approval-package artifacts:

- test record template generation;
- fee evaluation form generation.

The task must stop at dataset preview. No Word or Excel output is generated in this task.

---

## 2. Design

### Application Service

Add `TestRecordFeeDatasetPreviewService`.

Responsibilities:

- verify Project exists;
- load Project-scoped `ProjectTestPlanDraft`;
- reject superseded draft;
- parse draft payload JSON;
- project groups/steps into a test-record dataset;
- project groups/steps into fee line candidates;
- add warnings for missing method/condition/reference/judgement/duration/price data.

### API

Add:

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/record-fee-dataset-preview
```

The route stays typed and thin.

### Data Shape

Use plain dataclasses in application layer first. Do not add persistence or normalized Matrix tables in this task.

---

## 3. File-Level Changes

Expected implementation files:

- `backend/application/test_record_fee_dataset_preview_service.py`
- `backend/api/routes_test_record_fee_dataset_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_test_record_fee_dataset_preview_service.py`
- `tests/integration/test_test_record_fee_dataset_preview_api.py`

Control files:

- `tasks/TASK_180_TEST_RECORD_AND_FEE_INPUT_DATASET_PREVIEW.md`
- `docs/task_board.md`
- phase guard tests, only to allow the new board state.

---

## 4. Risks

- Real fee evaluation needs a price source, which is not available yet. This task must not invent prices.
- Test record template layout is not implemented yet, so the dataset should stay template-neutral.
- Draft payload is still JSON snapshot data; field names may vary across future parsers. Missing values should become warnings.
- If this task starts writing `.docx` or `.xls`, it skips the required dataset preview boundary.

---

## 5. Validation

Targeted:

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

## 6. Approval Gate

This plan is only the executable design. Implementation starts only after explicit approval, for example:

```text
批准执行 TASK_180
```
