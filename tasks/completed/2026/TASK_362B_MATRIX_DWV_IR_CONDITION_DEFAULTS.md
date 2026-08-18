# TASK_362B Matrix DWV and IR Condition Defaults

## Status

Complete/accepted in the shared working tree after Developer, Reviewer, QA,
and Integrator hunk-isolation gates. No mixed-worktree commit was created.

## Phase / Lane

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Lane: `matrix-dwv-ir-condition-defaults`.

## Goal

Correct Matrix default extraction for two electrical test families from their
specification sections:

- `Dielectric Withstanding Voltage` / `DWV`: `1500VAC, 60 seconds` when the
  source states `Test Voltage - 1500 volts AC` and `Test Duration - 60 seconds`.
- `Insulation Resistance`: `500VDC, 2 minutes` when the source states
  `Test Voltage - 500 volts DC` and `Electrification Time - 2 minutes`.

The DWV leakage-current threshold (for example `>1mA`) remains a Requirement
fact and must not become the Condition.

## Confirmed Facts

- The existing DWV Requirement normalizer correctly retains the no-arc-over /
  leakage-current statement.
- Generic Condition token collection can select `1mA` before the normalizer
  sees an empty DWV Condition.
- Existing IR/DWV voltage normalization emits compact source-faithful values
  such as `500VDC` and `1500VAC`, but does not combine an explicit duration.
- `TASK_362A` is complete/accepted and the board has no active implementation
  task. The user explicitly requested this narrow follow-up.

## May Touch After Separate Implementation Approval

- `backend/modules/test_plan/spec_section_text_extractor.py`
- `backend/modules/test_plan/mcr_text_normalizer.py` only if a small shared
  electrical-condition helper is needed
- `tests/unit/test_spec_section_text_extractor.py`
- `tests/unit/test_mcr_text_normalizer.py`
- `tests/unit/test_product_spec_matrix_parser.py` only for a narrow end-to-end
  Matrix default regression
- TASK_362B task, plan, Planner evidence, and `docs/task_board.md`

## Must Not Touch

- Fee rules, pricing, defaults, exports, UI, or source workbook artifacts
- Matrix persistence, confirmation, API, frontend/client, and database schema
- Requirement semantics beyond preserving the existing DWV and IR behavior
- Any real specification document, database, workbook, project folder, or
  public-drive path
- TASK_361 authority lanes and all unrelated parser families

## Acceptance Criteria

1. DWV source voltage plus `Test Duration` emits `1500VAC, 60 seconds`.
2. IR source voltage plus `Electrification Time` emits `500VDC, 2 minutes`.
3. A DWV leakage-current threshold never becomes Condition when a source
   voltage is available.
4. Existing DWV/IR Requirement normalization remains unchanged.
5. Missing voltage or missing duration is handled deterministically without
   inventing a value, and unrelated test families do not change.
6. Focused normalizer/extractor/parser regressions pass without real-file I/O.

## Validation Gate

- Unit fixtures cover AC and DC voltage, `Test Duration`, `Electrification
  Time`, no-duration, leakage-current token rejection, and unrelated generic
  token behavior.
- A focused Matrix parser fixture proves the final Condition values.
- Run focused pytest, Python compile, diff/trailing-whitespace, and
  forbidden-scope/no-real-file scans.

## Merge Gate

Reviewer plan gate, explicit implementation approval, Developer implementation,
Reviewer implementation review, focused QA, and Integrator scope isolation are
required. Stop after the plan gate until the user explicitly approves coding.
