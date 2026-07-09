# TASK_359A Matrix Reseating Default Details Hotfix

Status: complete
Lane: `matrix-reseating-default-details-hotfix`
Owner Role: Developer
Created: 2026-07-09

## Purpose

Add the same backend-owned Matrix row detail default behavior used by other Test Items for `Reseating`.

## User Goal

When Matrix detail extraction encounters a row with:

```text
Test Item: Reseating
Section: 7.8
```

ConnLab should default the missing row details to:

```text
Method: `<Basic Information.applicable_specifications> 7.8`
Condition: Manual 3 cycles
Requirement: No damage
```

The behavior should come from the backend Matrix detail extraction/default-fill path, not from manual frontend editing.

## Scope

- Add a backend unit test for `Reseating` default details.
- Update the existing Matrix row detail extraction/default-fill path only as needed.
- Read the current project's Basic Information `applicable_specifications` value for Matrix preview defaults.
- Keep the change deterministic and test-item/section scoped.

## May Touch

- `backend/modules/test_plan/spec_section_text_extractor.py`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/dependencies.py`
- `tests/unit/test_spec_section_text_extractor.py`
- `tests/unit/test_product_spec_matrix_parser.py`
- `tasks/TASK_359A_MATRIX_RESEATING_DEFAULT_DETAILS_HOTFIX.md`
- `docs/task_359a_matrix_reseating_default_details_hotfix_plan.md`
- `docs/task_board.md`

## Must Not Touch

- Matrix parser table selection/import flow.
- Matrix Editor frontend behavior.
- Matrix Step quantity defaults or TASK_358A implementation.
- Fee Evaluation, Test Record, Report, LTR, Folder, release, packaging, settings, public-drive, or real workbook/folder behavior.
- Schema, migrations, persistence models, or API contracts.
- `.agents/**` or `docs/project_management/**`.

## Validation

- `py -m pytest tests\unit\test_spec_section_text_extractor.py -q`
- `py -m pytest tests\unit\test_product_spec_matrix_parser.py -q`
- `py -m pytest tests\integration\test_project_test_plan_preview_api.py -q`
- Optional browser smoke after restart/reparse: import or reparse a Matrix containing `Reseating` section `7.8` and verify Method/Condition/Requirement defaults.
