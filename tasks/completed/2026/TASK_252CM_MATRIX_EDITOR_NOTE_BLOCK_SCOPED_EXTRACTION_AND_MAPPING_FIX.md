# TASK_252CM_MATRIX_EDITOR_NOTE_BLOCK_SCOPED_EXTRACTION_AND_MAPPING_FIX

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CM_MATRIX_EDITOR_NOTE_BLOCK_SCOPED_EXTRACTION_AND_MAPPING_FIX`

## Why This Task Is Allowed Now

- User provided a concrete regression case on `GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`: extracted Step Notes content is clearly mismatched with the document’s actual `(a)..(e)` note block.
- Root cause is a bounded parser extraction scope issue (note source overreach / wrong origin association), plus downstream mapping side effects.
- Scope remains controlled to parser + matrix preview mapping validation without runtime domain expansion.

## Model Fit Assessment

`GPT-5.3-codex` with `high` reasoning is suitable.

## Objective

1. Restrict marker-note extraction to the matrix-table-adjacent note block instead of unconstrained paragraph-wide matching.
2. Ensure `(a)..(e)` in A2-like documents map to the correct step/sample tokens.
3. Prevent unrelated paragraph fragments (for example other requirement text) from being treated as marker-note definitions.

## Scope

Allowed:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/application/project_test_plan_matrix_preview_service.py` (only if required for parser input scope metadata)
- parser/API tests for note extraction and mapping correctness
- task/plan/board documentation updates

Forbidden:

- new format support (`.doc`, `.pdf`, OCR)
- frontend layout redesign
- persistence/runtime model changes

## Acceptance Criteria

1. For A2 note block examples, extracted notes match bottom note-list text exactly by marker (`a..e`).
2. Step notes for `3(a)` and `10(c)` show correct A2 note text, not unrelated requirement text.
3. Sample notes for `5+5(d)` and `5+(5e)` map to `(d)` / `(e)` note text.
4. No regression for previous marker variants (`(a)`, `a)`, `（a）`, `a.`, `Note (a):`, `*`, `#`, `(5e)`).
5. Targeted tests pass.

## Validation

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```
