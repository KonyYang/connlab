# TASK_281_TEST_RECORD_HEADER_METADATA_FILL

## Status

Complete.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Allowed Reason

TASK_280 is complete and the task board currently has no active implementation task. The user requested the next controlled Test Record generation task: automatically fill the Word template header fields from project/LTR/application-form authority data.

## Objective

Extend the TASK_280 template-backed Test Record Word generation so the generated `.docx` automatically fills the template header fields that correspond to the information confirmed during LTR registration:

- `Lab Test Request Number` <- registered LTR number.
- `Product Description` <- LTR registration `Sample Description`.
- `Applicable Specification` / `Applicable Specifications` <- confirmed applicable specification value from intake/application-form authority data.

`Estimated Completion Date` must remain blank because it is a handwritten/manual record field.

## Template Header Shape

The approved template contains header tables:

```text
Header table 0:
  cell 2: Lab Test Request Number / 实验室测试项目编号

Header table 1:
  cell 0: Product Description / 产品描述
  cell 1: value cell
  cell 2: Applicable Specification / 适用的规范
  cell 3: value cell
  cell 4: Estimated Completion Date / 预计完成日期
  cell 5: value cell
```

The implementation must locate fields by nearby label text, not by only assuming table index and cell position. Table/cell indexes may be used as a fallback after label matching.

## Scope

### In Scope

1. Add a backend metadata resolver for Test Record header fields.
2. Resolve registered LTR number from the project's registered `LtrRecord`.
3. Resolve Product Description from the `sample_description` value captured when applying the LTR number.
4. Resolve Applicable Specification from confirmed intake/application-form data, with deterministic fallback behavior.
5. Pass resolved header metadata from the application service into the Word gateway.
6. Fill the Word template header value cells without changing group/step table generation.
7. Leave Estimated Completion Date blank.
8. Add backend unit/integration tests for header metadata resolution and Word header filling.

### Out Of Scope

Do not implement in TASK_281:

- Estimated Completion Date auto-fill.
- Header/footer visual redesign.
- New template picker UI.
- Test execution persistence, StepInstance, evidence/images, report generation, fee calculation, AI, permissions, or multi-user behavior.
- Editing generated Word content inside ConnLab.
- Generating from unconfirmed Matrix editor state.
- Parsing Excel as runtime source.

## Data Source Decision

### Lab Test Request Number

Use the latest registered LTR for the project:

```text
LtrRecord.status == REGISTERED
```

If no registered LTR exists, leave the header value blank and keep generation non-blocking.

### Product Description

Primary source:

```text
LtrRecord.notes JSON -> sample_description
```

This is the value entered during `Apply LTR Number` / project setup confirmation, matching the user's requirement that Product Description comes from `Sample Description`.

Fallback:

```text
Project.product_name
```

### Applicable Specification

Primary source:

```text
confirmed intake draft requested_testing_json[*].applicable_specification
```

If multiple distinct values exist, join them with `; ` in source order.

Fallbacks:

1. Application form `requested_testing` only when a deterministic specification token can be extracted (for example `EIA-`, `GS-`, `QG-`, `IEC`, `ASTM`, `UL` pattern tokens).
2. Existing LTR readiness specification resolver behavior if available through existing repositories.
3. Blank when no deterministic source exists.

Do not invent placeholder text.
Do not use free-text heuristic inference that may map unrelated narrative text into header specification fields.

## Header Write Guard

Header fill must be value-only and style-preserving:

1. Do not overwrite label text cells for:
   - `Lab Test Request Number`
   - `Product Description`
   - `Applicable Specification`
   - `Estimated Completion Date`
2. Do not replace a full header cell with plain `cell.text = value` when the cell includes label text or mixed runs.
3. Preserve existing runs/paragraph formatting and only update value runs or append value text in designated value area.
4. `Estimated Completion Date` label remains intact and its value area remains blank.

## Expected Files

Backend:

- `backend/application/confirmed_matrix_test_record_document_generation_service.py`
- `backend/infrastructure/office/test_record_document_gateway.py`
- `backend/api/dependencies.py`
- `backend/infrastructure/storage/repositories/intake_package.py` only if a `list_by_confirmed_project` or equivalent lookup is needed.

Tests:

- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/unit/test_test_record_document_gateway.py`
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`

Task tracking:

- `tasks/TASK_281_TEST_RECORD_HEADER_METADATA_FILL.md`
- `docs/task_281_test_record_header_metadata_fill_plan.md`
- `docs/task_board.md`
- `docs/task_plan_index.md`

## Acceptance Criteria

1. Generated Word fills `Lab Test Request Number` with the registered LTR number.
2. Generated Word fills `Product Description` with the LTR registration `Sample Description` value.
3. Generated Word fills `Applicable Specification` with the confirmed applicable specification value.
4. Generated Word leaves `Estimated Completion Date` blank.
5. Header filling works on the approved template by label matching in header tables.
6. Header filling does not alter group/sample paragraphs.
7. Header filling does not alter step rows, step ordering, Test items, methods, conditions, remarks, or manual execution columns.
8. Missing LTR/sample/spec values do not crash generation; missing values leave the corresponding header cell blank.
9. Backend tests cover happy path and missing-value behavior.
10. Integration test verifies the downloaded `.docx` contains the filled header values.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for execution.

Reason:

- The task is a bounded backend Word-generation refinement with existing service, repository, and document-gateway boundaries.
- The main risk is Word header table manipulation and authority metadata source selection; both are manageable with targeted unit/integration tests.
- The task should be executed serially with `superpowers:executing-plans` because document output behavior needs careful checkpoint verification.

## Validation Plan

```powershell
py -m pytest tests\unit\test_test_record_document_gateway.py -q
py -m pytest tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
py -m pytest tests\integration\test_confirmed_matrix_test_record_generation_api.py -q
git diff --check
```

## Stop Rule

After implementing TASK_281, stop. Do not proceed to execution-data fields, equipment filling, image/evidence insertion, report generation, or fee calculation without a new approved task.
