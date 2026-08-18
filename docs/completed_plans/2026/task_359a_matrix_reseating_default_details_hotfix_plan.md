# TASK_359A Matrix Reseating Default Details Hotfix Plan

Status: complete
Date: 2026-07-10
Task: `TASK_359A_MATRIX_RESEATING_DEFAULT_DETAILS_HOTFIX`

## Current Phase / Active Task / Why Allowed

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task: `TASK_358A_MATRIX_EDITOR_QUANTITY_DEFAULTS_SIMPLIFICATION` is complete/accepted. The task board now requires an Orchestrator/User routing decision for the next lane.

Why allowed: the user explicitly requested a narrow backend default-fill hotfix for the Matrix `Reseating` row after confirming TASK_358A is complete.

## Goal

Add backend-owned default details for Matrix rows where `Test Item` is `Reseating` and `Section` is `7.8`:

- `Method`: `<Basic Information.applicable_specifications> 7.8`
- `Condition`: `Manual 3 cycles`
- `Requirement`: `No damage`

This should behave like existing Matrix detail defaults for other Test Items. It must not be a frontend hardcode or manual browser edit.

## Existing Evidence

- `backend/modules/test_plan/spec_section_text_extractor.py` extracts or fills row-level `method`, `condition`, and `requirement`.
- `ProjectTestPlanMatrixPreviewService` already receives `project_id`; it now reads the Basic Information preview snapshot and passes `applicable_specifications` through the parser path.
- `tests/unit/test_spec_section_text_extractor.py` already covers test-item family defaults for similar Matrix detail behavior.
- Current browser evidence shows Row 13 `Reseating`, Section `7.8`, with blank Method/Condition and Requirement `No damage`.

## Design

Implementation should follow TDD:

1. Add a failing unit test in `tests/unit/test_spec_section_text_extractor.py`.
2. The test should call `extract_row_details(section="7.8", section_text=..., test_item="Reseating", applicable_specifications="EIA-364-37")`.
3. Expected output:
   - method `EIA-364-37 7.8`
   - condition `Manual 3 cycles`
   - requirement `No damage`
   - status `matched`
4. Add the smallest backend default rule in `spec_section_text_extractor.py`, scoped to normalized `Reseating` and section `7.8`, composing the Method from the Basic Information value.

No API response/schema or frontend change is planned.

## Risks

- A broad string match for `seat` could affect unrelated Test Items. The rule must match `reseating` narrowly.
- A broad section match could apply to other sections. The rule should require section `7.8`.
- Existing extracted explicit details should not be overwritten unless they are blank; this hotfix targets missing default content only.

## Validation

- `py -m pytest tests\unit\test_spec_section_text_extractor.py tests\unit\test_product_spec_matrix_parser.py -q`: passed, `36 passed`.
- `py -m pytest tests\integration\test_project_test_plan_preview_api.py -q`: passed, `9 passed`.
- `py -m compileall -q backend\application\project_test_plan_matrix_preview_service.py backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py backend\modules\test_plan\spec_section_text_extractor.py`: passed.
- If the local server is restarted or the Matrix is reparsed later, verify the Matrix Editor row displays the Basic Information specification followed by `7.8`.

## Stop Point

Stop after this hotfix. Do not enter the next task.
