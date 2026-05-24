# TASK_252CN_MATRIX_EDITOR_SECTION_SYMBOL_NOTE_EXTRACTION_RESTORE

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CN_MATRIX_EDITOR_SECTION_SYMBOL_NOTE_EXTRACTION_RESTORE`

## Why This Task Is Allowed Now

- User reported a concrete regression for `GS-12-1507 RA Coplanar Rev7 (3).docx`: section markers such as `6.5*` / `6.6*` are shown in `Item/Section Notes`, but the table-footer `*Simultaneously measure power contact resistance.` note body is not displayed.
- The task is a bounded parser note-extraction fix for existing Matrix preview behavior.
- `docs/task_board.md` shows no active task and requires explicit approval before opening the next controlled Matrix Editor task.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

## Objective

Restore extraction of standalone symbol marker notes (`*`, `#`) after the TASK_252CM scoped note-block changes, so section notes like `Section:6.5*` include the correct note body.

## Scope

Allowed:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `tests/unit/test_product_spec_matrix_parser.py`
- `tests/integration/test_project_test_plan_preview_api.py` if API regression coverage is needed
- task/plan/board documentation updates

Forbidden:

- frontend layout redesign
- new import formats
- runtime/domain/persistence changes

## Acceptance Criteria

1. `*Simultaneously measure power contact resistance.` is extracted even when it appears as a single standalone symbol note after a table.
2. Rows with section markers `6.5*` and `6.6*` produce `source_item_section_note` with the full symbol note body.
3. Existing A2 `(a)..(e)` scoped/backfilled note behavior remains valid.
4. Targeted parser/API tests pass.

## Validation

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```
