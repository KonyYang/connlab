# TASK_334E Fee Form COM Second-Pass Optimization Plan

## Summary

TASK_334E is a focused Fee Form `.xls` COM hot-path follow-up. It keeps the existing output contract and reduces avoidable worksheet round-trips in edited-row-heavy Matrix basic-fill exports.

## Implementation

- Add regression tests proving edited rows write the editable B:H segment through the existing range-style seam instead of separate cell assignments.
- Add row insertion fallback tests proving `Rows(row).Resize(count).Insert()` is used before the final row-by-row fallback.
- Change the Matrix basic-fill writer so edited rows write B:H in one row-range assignment and always set the I-column formula after row values.
- Preserve sparse comment behavior: blank Notes skip comment APIs; non-empty Notes write only target comments and clear/retry only if `AddComment` fails.
- Keep diagnostics internal/test-observable and avoid public API response changes.

## Validation

- Run targeted Fee Form and sheet-op unit tests.
- Run Required Forms and project-folder API regressions.
- If a real Office smoke is available, capture before/after `write_matrix_basic_fill` timing; otherwise record automated regression evidence and note that real timing requires Office/fixture availability.

## Boundaries

Do not change Fee pricing rules, Basic Information, Customer Feedback, Application Form, Test Record, LTR, Report, frontend UI, or project-folder orchestration.
