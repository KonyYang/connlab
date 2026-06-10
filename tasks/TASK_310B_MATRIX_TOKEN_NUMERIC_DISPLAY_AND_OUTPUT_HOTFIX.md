# TASK_310B_MATRIX_TOKEN_NUMERIC_DISPLAY_AND_OUTPUT_HOTFIX

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed Now

The user reported a Workbench Matrix projection issue: tokens such as `3(a)` and `4(b)` are displayed on Workbench buttons and can then propagate into generated Test Record / Test Report style derived outputs.

This is a bounded Matrix token hotfix after TASK_310A. It does not implement TASK_311 Customer Feedback generation or any future StepInstance/report-execution scope.

## Root Cause

Confirmed Matrix consumers parse cell values through `backend.modules.test_plan.matrix_step_sequence_validation.parse_step_tokens`.

The parser currently returns:

- `sequence`: numeric step number
- `suffix_note`: suffix such as `(a)` or `(b)`
- `raw_token`: the original token text such as `3(a)`

Several downstream consumers display or export `raw_token` directly:

- Workbench Matrix projection buttons use `step.raw_token`.
- Confirmed Matrix Test Record preview exposes `step.raw_token`.
- Test Record document generation eventually prefers `raw_token` over `sequence`.
- Fee draft / Fee template consumers use parsed token raw text.

So suffix remarks remain visible even though they are no longer meaningful in the Workbench and derived-output phase.

## Goal

For confirmed Matrix / derived-output consumers, display and export pure numeric step tokens:

- `3(a)` -> `3`
- `4(b)` -> `4`
- `4（1）` -> `4`
- `6#` -> `6`
- `10*` -> `10`

Keep the parsed suffix in `suffix_note` where internal differentiation is still needed. Do not reintroduce suffixes into Workbench buttons or generated document step labels.

## In Scope

- Add backend parser tests proving parsed `raw_token` used by confirmed-output consumers is numeric-only while `suffix_note` is preserved.
- Add Workbench projection tests proving button/cell labels use numeric-only tokens for suffixed steps.
- Add Test Record preview/document or derived-output tests proving generated/exported step token values are numeric-only for suffixed tokens.
- Update the minimal backend/shared parser or confirmed-output mapping needed to make the above true.
- Update task board after validation.

## Out Of Scope

- No source Matrix import parser behavior change unless required by confirmed-output normalization.
- No Matrix Editor source-note extraction redesign.
- No Matrix save/confirm API contract change.
- No database migration.
- No Customer Feedback implementation.
- No Report-generation expansion beyond existing Test Record-related derived-output guards.
- No StepInstance, evidence/image, AI review, permission, multi-user, LAN/server, or public-drive publishing scope.

## Acceptance Criteria

- Workbench Matrix projection buttons display `3`, not `3(a)`.
- Confirmed Matrix Test Record preview returns numeric-only `raw_token` for suffixed step tokens.
- Test Record document generation receives numeric-only step tokens for suffixed confirmed Matrix steps.
- Suffix data remains available as `suffix_note` internally where parser consumers need stable differentiation.
- Existing sorting and token reference uniqueness remain stable enough for repeated same-number tokens with different suffixes.
- Existing TASK_310A separator behavior remains passing.

## Required Validation

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

## Stop Point

After this hotfix is implemented and validated, stop. Do not proceed to TASK_311 or any other task without its own approved task scope.

## Completion Notes

Implemented on 2026-06-11 after explicit user approval.

- Shared confirmed-output token parsing now normalizes parsed `raw_token` to the numeric sequence text while preserving `suffix_note`.
- Workbench Matrix projection displays `step.sequence` as the visible token label, so historical/API values like `3(a)` still render as `3`.
- Test Record document generation defensively formats step labels from numeric `sequence` first, preventing suffix remarks from appearing in generated step labels.
- Existing TASK_310A Chinese comma / whitespace separator behavior remains covered.

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
