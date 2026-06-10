# TASK_310B Matrix Token Numeric Display And Output Hotfix Plan

Status: Complete. Implemented after explicit user approval.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_311_CUSTOMER_FEEDBACK_FORM_GENERATION` is planned and awaiting explicit approval on the board. This TASK_310B plan is a separate proposed hotfix and must not start TASK_311 implementation.

## Why This Task Is Allowed Now

The user identified a current Workbench/derived-output defect: suffixed Matrix tokens such as `3(a)` are visible on Workbench token buttons and may propagate into generated Test Record / Test Report style outputs. The intended behavior is to show and output pure numeric step labels in this phase.

## Step 1: Task Understanding

Goal:

- Remove suffix notes from confirmed Matrix step token display/output labels.

Input:

- Confirmed Matrix cell token text such as `3(a)`, `4(b)`, `4（1）`, `6#`, `10*`.

Output:

- Workbench and derived-output token labels such as `3`, `4`, `6`, `10`.

Modules involved:

- `backend/modules/test_plan/matrix_step_sequence_validation.py`
- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/modules/runtime_projection/token_projection_builder.py`
- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_template_basic_fill_service.py`
- `backend/infrastructure/office/test_record_document_gateway.py` or document-generation service tests
- `frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`

Not allowed:

- No source Matrix parser redesign.
- No database or API contract migration.
- No TASK_311 Customer Feedback implementation.
- No future execution/report system expansion.

## Step 2: Root-Cause Evidence

Confirmed-output consumers use `parse_step_tokens`, which preserves suffix in `raw_token`:

```text
3(a) -> raw_token="3(a)", sequence=3, suffix_note="(a)"
```

Workbench Matrix projection builds button display from `cell.rawToken`, which comes from `step.raw_token`.

The Test Record document gateway also prefers `raw_token` when formatting a step label.

## Step 3: Design

Use numeric-only display/output token labels for confirmed-output consumers while preserving suffix metadata:

```text
3(a) -> raw_token="3", sequence=3, suffix_note="(a)"
4(b) -> raw_token="4", sequence=4, suffix_note="(b)"
6#   -> raw_token="6", sequence=6, suffix_note="#"
```

Preferred implementation:

- Normalize `ParsedStepToken.raw_token` in the shared confirmed-output parser to `str(sequence)`.
- Keep `suffix_note` unchanged.
- Keep token reference uniqueness based on `sequence_number + suffix_note`, so internal repeated-token differentiation remains possible.

Why this is safer than only changing the Workbench button:

- Workbench, Test Record preview, Test Record document generation, Fee draft, and Fee template all consume parsed token raw text.
- Fixing only UI would leave generated outputs with suffixes.

## Step 4: File-Level Plan

1. Tests first:
   - Update `tests/unit/test_matrix_step_sequence_validation.py` to assert numeric-only raw token with preserved suffix.
   - Update `tests/unit/test_confirmed_matrix_test_record_preview_service.py` to assert `3(a)` becomes preview raw token `3`.
   - Update runtime projection tests to assert Workbench-facing token raw value is `3`.
   - Update ProjectWorkbench Matrix projection panel test to assert rendered button `3`, not `3(a)`.
   - Add or adjust Test Record generation tests if gateway/service currently receives suffixed raw token.

2. Implementation:
   - Update shared parser or confirmed-output mapper minimally.
   - Do not alter source Matrix import parser unless a failing test proves it is the same confirmed-output path.

3. Documentation:
   - Update `docs/task_board.md` and this plan after validation.

## Step 5: Validation Commands

```powershell
py -m pytest tests\unit\test_matrix_step_sequence_validation.py tests\unit\test_confirmed_matrix_runtime_projection_service.py tests\unit\test_confirmed_matrix_test_record_preview_service.py tests\unit\test_confirmed_matrix_test_record_document_generation_service.py -q
```

```powershell
py -m pytest tests\unit\test_confirmed_matrix_fee_draft_service.py tests\unit\test_confirmed_matrix_fee_template_basic_fill_service.py -q
```

```powershell
cd frontend
npm test -- --run ProjectWorkbenchMatrixProjectionPanel --watch=false
```

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or project_workbench or task310"
```

## Risks

- Some existing tests assert raw token preservation. Those tests must be reviewed carefully to distinguish source-import/parser note extraction from confirmed-output display semantics.
- Repeated step numbers with different suffixes may render as repeated identical numeric buttons. This matches the requested display behavior, but token references must remain internally distinct using `suffix_note`.
- Existing source note matching in Matrix Editor should not be changed by this hotfix.

## Approval Request

Approve `TASK_310B_MATRIX_TOKEN_NUMERIC_DISPLAY_AND_OUTPUT_HOTFIX` to implement the numeric-only token display/output behavior.

## Completion Notes

Implemented on 2026-06-11.

- `parse_step_tokens` now emits numeric-only `raw_token` values while preserving suffix metadata in `suffix_note`.
- Workbench Matrix projection now renders numeric labels from `sequence`, so suffixed legacy/API tokens display as `3`, not `3(a)`.
- Test Record Word generation now prefers numeric `sequence` for step labels and strips suffixes from legacy raw-token fallback values.
- Scope boundary held: no TASK_311 Customer Feedback implementation, no database/API contract migration, no StepInstance/report-execution expansion.

## Validation Summary

```text
py -m pytest tests\unit\test_matrix_step_sequence_validation.py tests\unit\test_confirmed_matrix_runtime_projection_service.py tests\unit\test_confirmed_matrix_test_record_preview_service.py tests\unit\test_confirmed_matrix_test_record_document_generation_service.py tests\unit\test_test_record_document_gateway.py -q
35 passed

py -m pytest tests\unit\test_confirmed_matrix_fee_draft_service.py tests\unit\test_confirmed_matrix_fee_template_basic_fill_service.py -q
13 passed

cd frontend; npm test -- --run ProjectWorkbenchMatrixProjectionPanel --watch=false
8 passed

cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false
23 passed

py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor or project_workbench or task310"
44 passed, 90 deselected

cd frontend; npm run build
passed
```
