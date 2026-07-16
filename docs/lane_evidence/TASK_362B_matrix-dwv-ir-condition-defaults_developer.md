# TASK_362B Matrix DWV and IR Condition Defaults Developer Evidence

Status: implementation_complete_pending_reviewer
Date: 2026-07-17
Role: Developer

## Scope

Implemented only the planned Matrix section-extraction behavior:

- DWV now reads explicit `Test Voltage` plus `Test Duration` before generic
  condition-token fallback.
- IR now reads explicit `Test Voltage` plus `Electrification Time` before
  generic condition-token fallback.
- The helper emits compact `VAC`/`VDC` plus source duration, preserves an
  explicit voltage when duration is absent, and recognizes the observed DOCX
  table separator through the ASCII regex escape `\\u6bcf`.

No Fee, UI, API, schema, persistence, real-file, or unrelated parser behavior
was changed.

## TDD Evidence

1. Updated the focused DWV/IR extractor regression to expect the requested
   voltage-plus-duration values. The test failed as expected: IR returned
   `2 minutes` and DWV returned `1mA`.
2. Added the family-specific extraction branch and helper.
3. Re-ran the focused regression: `2 passed`.
4. Added regressions for the observed document separator, voltage-only fallback,
   and preserving DWV leakage current in Requirement.

## Validation

`py -m pytest tests\\unit\\test_spec_section_text_extractor.py tests\\unit\\test_mcr_text_normalizer.py tests\\unit\\test_product_spec_matrix_parser.py -q`

Result: `104 passed`.

## Handoff

Reviewer implementation gate is required next. Existing unrelated working-tree
changes, including the prior voltage-only normalizer fallback, are not claimed
by this evidence and must remain isolated during package review.
