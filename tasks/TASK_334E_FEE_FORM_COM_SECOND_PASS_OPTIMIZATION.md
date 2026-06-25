# TASK_334E Fee Form COM Second-Pass Optimization

## Goal

Reduce remaining Fee Form `.xls` COM time after TASK_334A by optimizing Matrix basic-fill edited-row writes, sparse comment handling, formula writes, and row insertion fallback visibility.

## Scope

In scope:

- Keep Fee Form `.xls` generation behavior unchanged.
- Optimize edited Matrix/basic rows to use range-style writes where practical.
- Keep comments sparse: blank Notes must not call Excel comment APIs.
- Preserve bulk row insertion order and cover Resize fallback with tests.
- Add timing/test evidence and update the task board after validation.

Out of scope:

- No `.xls` to `.xlsx` conversion.
- No Customer Feedback, Application Form, Test Record, LTR, Report, frontend progress UI, or Project Folder orchestration changes.
- No Fee Evaluation pricing/business-rule changes.
- No Basic Information schema/API changes.

## Validation

- `py -m pytest tests/unit/test_fee_evaluation_workbook_gateway.py tests/unit/test_fee_evaluation_sheet_ops.py -q`
- `py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_project_folder_required_forms_service.py -q`
- `py -m pytest tests/integration/test_project_folder_required_forms_api.py -q`
- Focused timing smoke where available; if real timing is not practical in the sandbox, document the limitation and preserve automated COM-call regression tests.
