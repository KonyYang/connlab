# TASK_362B Matrix DWV and IR Condition Defaults Planner Evidence

Status: planned-only
Date: 2026-07-17
Role: Planner

## Gate

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled
foundation.

Current lane: `TASK_362B_MATRIX_DWV_IR_CONDITION_DEFAULTS`, planned-only.

Why allowed: `TASK_362A` is complete/accepted and the user approved this
narrow parser follow-up. No active implementation task is displaced.

## Evidence

- User-supplied specification wording establishes the two source-to-output
  mappings: DWV `1500VAC, 60 seconds` and IR `500VDC, 2 minutes`.
- The local specification confirms explicit `Test Voltage`, `Test Duration`,
  and `Electrification Time` wording.
- The current section extractor's generic condition-token fallback can select
  the DWV Requirement's leakage-current `1mA` token.
- The existing normalizer already preserves source voltage polarity and
  Requirement normalization, giving this lane a narrow, testable boundary.

## Scope Decision

The task is limited to source-labeled DWV/IR Condition extraction and focused
regressions. It excludes all Fee behavior even though TASK_362A separately
uses IR/DWV duration facts for fee-tier selection.

## Next Gate

Reviewer plan gate. No implementation is authorized.
