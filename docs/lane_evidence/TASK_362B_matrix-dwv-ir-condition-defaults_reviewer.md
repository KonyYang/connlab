# TASK_362B Matrix DWV and IR Condition Defaults Reviewer Evidence

Status: reviewer_pass
Date: 2026-07-17
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, parser behavior, real specification
file, database, workbook, API, or frontend change was made by this review.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package
controlled foundation.

Current task: `TASK_362B_MATRIX_DWV_IR_CONDITION_DEFAULTS`, planned-only.

Why allowed: `TASK_362A` is complete/accepted and the board records TASK_362B
as the current planned lane.

## Findings

The plan correctly isolates the defect to a family-ordering problem: generic
Condition token collection can choose DWV Requirement text `1mA` before the
normalizer's blank-condition voltage fallback is available. A family-specific
DWV/IR extraction branch before that fallback is the narrowest correction.

The two exact requested mappings are explicit and testable:

- DWV: source-labeled AC test voltage plus `Test Duration` ->
  `1500VAC, 60 seconds`.
- IR: source-labeled DC test voltage plus `Electrification Time` ->
  `500VDC, 2 minutes`.

The plan keeps Requirement normalization, Fee duration behavior, Matrix
persistence, API/client, UI, and real-file access out of scope. It also states
the missing-field rule rather than defaulting an unproven voltage or duration.

## Decision

`reviewer_pass`

Recommended next action: explicit user approval for Developer implementation.

Blocking summary: none.
