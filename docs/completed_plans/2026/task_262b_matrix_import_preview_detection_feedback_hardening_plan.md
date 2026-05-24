# TASK_262B Matrix Import Preview Detection Feedback Hardening Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Active Task

TASK_262B_MATRIX_IMPORT_PREVIEW_DETECTION_FEEDBACK_HARDENING.

## Why Allowed

The user explicitly approved TASK_262B as a continuation of TASK_262/TASK_262A Matrix import preview behavior. The work is limited to Matrix preview detection and feedback correctness.

## Scope

- Keep Matrix import preview non-blocking when no valid Matrix is found.
- Prevent stale or false-positive Matrix preview state from driving group selection.
- Harden deterministic parser scoring against test record and revision record false positives.

## File-Level Changes

- `backend/modules/test_plan/product_spec_matrix_parser.py`
  - Add revision/history table rejection before Matrix candidate scoring.
  - Expand negative record header signals.
  - Penalize tables where the inferred first column is mostly numeric-only row IDs.
- `tests/unit/test_product_spec_matrix_parser.py`
  - Add a regression test for revision record tables that include `TEST GROUP` and `SAMPLE QTY` in description text.
- `docs/task_board.md`
  - Mark TASK_262B complete with validation summary.

## Risks

- Over-rejecting valid Matrix tables with compact numeric group headers.
  - Mitigation: keep numeric/alphanumeric group header support and retain existing acceptance test for numeric group headers with a sample tail and qualification context.
- Under-rejecting other non-Matrix administrative tables.
  - Mitigation: use explicit record-table signals and numeric first-column penalties without blocking manual fallback.

## Validation

- `py -m pytest tests\unit\test_product_spec_matrix_parser.py -q`
- `py -m pytest tests\integration\test_project_test_plan_preview_api.py -q`
