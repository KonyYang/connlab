# TASK_283F Implementation Plan - Step Requirement to Test Record Remark Binding

## 1. Task Identity

- Task: `TASK_283F_STEP_REQUIREMENT_TO_TEST_RECORD_REMARK_BINDING`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Plan status: Draft for review (no implementation yet)
- Execution mode: `superpowers:executing-plans` (serial, minimal-risk)

## 2. Why This Task Is Allowed Now

`TASK_283A/B/E` stabilized deterministic MCR extraction and normalization. `TASK_283D` finalized Matrix Editor UX behavior. A remaining functional gap exists between step-level requirement intent and Test Record generated `Remark` output. This task is the controlled consumer-binding closure for that gap.

## 3. Objective

Ensure generated Test Record `Remark` is step-aware and deterministic, matching step-level requirement mapping for LLCR multi-step rows.

## 4. Scope Control

### In Scope

1. Backend step-requirement mapping logic in preview/generation path.
2. Deterministic LLCR split mapping for multi-step output.
3. Deterministic partial LLCR handling (initial-only without delta).
4. Word generation consumption of mapped step requirement.
5. Unit + integration test coverage for mapping and generated output.

### Out Of Scope

1. No StepInstance/domain expansion.
2. No new workflow or UI feature.
3. No AI extraction changes.
4. No report-engine redesign outside existing Test Record gateway path.

## 5. Design

1. Keep row-level `requirement` as authority source text.
2. Add backend helper that computes per-step requirement value from:
   - row requirement text.
   - final step order in one group.
3. Final step order contract:
   - collect all LLCR steps in group.
   - sort by `sequence` ascending.
   - if same `sequence`, stable tie-break by `raw_token`.
4. Integrate helper where `ConfirmedMatrixTestRecordPreviewStep` is built so downstream consumers receive step-ready requirement.
5. Keep family behavior deterministic and minimal:
   - LLCR only in V1 for split mapping.
   - non-target families keep existing behavior.

## 6. File-Level Change Plan

1. `backend/application/confirmed_matrix_test_record_preview_service.py`
2. `backend/modules/test_plan/*` helper module or local helper function for step requirement split (smallest maintainable placement).
3. `backend/application/confirmed_matrix_test_record_document_generation_service.py` (assert writer receives mapped step requirement values through preview payload).
4. `backend/infrastructure/office/test_record_document_gateway.py` (verify usage path; no format redesign expected).
5. Tests:
   - `tests/unit/test_confirmed_matrix_test_record_preview_service.py`
   - `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
   - `tests/unit/test_test_record_document_gateway.py`
   - targeted integration if required by contract validation.

## 7. LLCR Mapping Contract (V1)

Input example:

`Initial <= 0.25 mOhm; ΔR <= 0.17 mOhm`

Per-step output:

1. first LLCR step in final sorted order: `<= 0.25 mOhm`
2. subsequent LLCR steps: `ΔR <= 0.17 mOhm`

Normalization tolerance:

1. accept `R<=` and normalize to `ΔR <=` for follow-up.
2. if split cannot be determined, fallback to original row requirement unchanged.

Partial LLCR rule (initial-only):

1. if initial can be extracted but delta cannot:
   - initial step uses `<= <initial value>`.
   - follow-up steps keep original row requirement unchanged.
2. this rule is mandatory and test-locked.

## 8. Risks and Mitigation

1. Risk: mismatch between frontend preview behavior and backend generation behavior.
   - Mitigation: make backend mapping canonical and verify with tests that assert exact generated remark values.
2. Risk: over-applying LLCR logic to unrelated rows.
   - Mitigation: strict family detection guard and non-family passthrough.
3. Risk: order-dependent misassignment when tokens are not entered in ascending order (for example `5,2`).
   - Mitigation: explicit final-order contract + dedicated test.

## 9. Validation Commands

1. `py -m pytest tests/unit/test_confirmed_matrix_test_record_preview_service.py -q`
2. `py -m pytest tests/unit/test_confirmed_matrix_test_record_document_generation_service.py -q`
3. `py -m pytest tests/unit/test_test_record_document_gateway.py -q`
4. `py -m pytest tests/integration/test_confirmed_matrix_test_record_generation_api.py -q`
5. `py -m pytest tests/integration/test_matrix_to_test_record_smoke_flow_api.py -q`
6. `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task283 or matrix_editor"`
7. `git diff --check`

## 10. Completion Criteria

1. Generated Test Record `Remark` reflects step-level LLCR split mapping.
2. Partial LLCR (initial-only) behavior is deterministic and test-covered.
3. Existing generation flow and template fill format remain stable.
4. Regression tests pass.

