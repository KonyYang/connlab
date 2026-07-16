# TASK_362B Matrix DWV and IR Condition Defaults Plan

## Discovery Gate

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package
controlled foundation.

Current active task/lane: no active implementation task; `TASK_362A` is
complete/accepted. `TASK_362B` is planned-only.

Why planning is allowed: the user explicitly approved the narrow DWV/IR
default-extraction follow-up after the board recorded `TASK_362A` complete.

### Confirmed By User

- DWV must extract `1500VAC, 60 seconds` from a `Test Voltage` AC statement
  and a `Test Duration` statement.
- IR must extract `500VDC, 2 minutes` from a `Test Voltage` DC statement and
  an `Electrification Time` statement.
- DWV leakage current belongs to Requirement, not Condition.

### Confirmed By Repository Evidence

- `spec_section_text_extractor._extract_condition` falls through to generic
  token collection for DWV and IR; that collection can return `1mA`.
- `mcr_text_normalizer._extract_test_voltage_condition` already recognizes
  source voltage and preserves AC/DC as compact `VAC`/`VDC`, but only runs
  when the preceding Condition is empty and does not capture duration.
- Existing DWV and IR Requirement normalization is independent and has focused
  regression coverage.

### Inferred By Planner

- Family-specific extraction belongs before generic token collection in the
  section extractor, so a source voltage wins over an incidental Requirement
  current threshold.
- A single private helper can construct a compact electrical Condition from
  source voltage plus the family-specific duration label.

### Not Yet Confirmed

- No additional voltage formats or duration units beyond the explicit source
  wording are approved. They remain unsupported rather than guessed.

### Risk And Decision

The main risk is accidentally turning this into generic electrical parsing and
changing unrelated Matrix rows. The plan remains narrow: only DWV and IR use
the helper, only explicit labeled source fields qualify, and missing fields
produce no invented values. Evidence is sufficient for a planned-only lane;
no blocking question remains.

## Design

### Inputs And Outputs

| Family | Required source facts | Condition output |
|---|---|---|
| DWV | `Test Voltage` with value and AC/DC; `Test Duration` with seconds/minutes | `<value>VAC/VDC, <duration>` |
| IR | `Test Voltage` with value and AC/DC; `Electrification Time` with seconds/minutes | `<value>VAC/VDC, <duration>` |

Explicit labeled source fields are required. If voltage is unavailable, the
helper returns no family-specific Condition. If duration is unavailable, the
approved implementation decision is to return the explicit voltage only rather
than inventing a duration; tests must document that fallback.

### File-Level Changes

1. `backend/modules/test_plan/spec_section_text_extractor.py`
   - Detect normalized DWV and IR test-item labels before generic condition
     token fallback.
   - Add one private helper that extracts explicitly labeled test voltage and
     family-specific duration, normalizes `AC`/`DC` to `VAC`/`VDC`, and joins
     both values with `, `.
   - Recognize ordinary document label separators (colon and dash variants)
     without broad free-text voltage guessing.

2. `backend/modules/test_plan/mcr_text_normalizer.py`
   - Keep existing Requirement normalization intact.
   - Narrowly align its blank-condition voltage fallback with the new source
     format only if required for direct-normalizer callers. Do not duplicate
     conflicting duration logic.

3. Focused tests
   - Add DWV AC plus Test Duration regression, proving `1mA` is not Condition.
   - Add IR DC plus Electrification Time regression.
   - Add missing-duration and unrelated-family regressions.
   - Add a Matrix parser-level fixture only if the unit tests do not exercise
     the public default path end to end.

## Non-Goals

- No Fee default, pricing, or duration-tier behavior changes.
- No generic voltage parser, UI behavior, Matrix persistence, API, or schema
  changes.
- No reads from the real DOCX during automated tests.

## Validation

Run the focused extractor/normalizer/parser tests, `py_compile` for changed
Python files, `git diff --check`, and scope scans. Use only inline fixtures and
temporary test inputs. Confirm the change does not alter the existing DWV
Requirement text or IR Requirement formatting.

## Approval Boundary

This document authorizes no product code. A separate explicit user approval is
required before Developer implementation.
