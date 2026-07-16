# TASK_362C Force and Mating Condition Requirement Defaults

## Status

Complete/accepted after explicit implementation approval, TDD implementation,
Reviewer implementation self-review, focused QA, and Integrator hunk-isolation
review.

## Goal

For Matrix Test Items whose normalized label contains `force`, or explicitly
represents both the mating and un-mating concepts, use the matching
specification section to extract Condition and Requirement facts. Preserve
explicit extracted values and apply the confirmed review placeholders only
when the matching value remains absent or unusable:

- Condition: `mm/min` when no numeric displacement/cross-head speed is found.
- Requirement: `N` when no meaningful Requirement can be extracted or retained.

Existing text such as `No damage` is meaningful and must not be replaced by
`N`.

## Confirmed Scope

- The rule applies to Mating/Un-mating Force, Normal Force, Terminal extraction
  force, Offset mating insertion force, Floater Displacement Force, other
  test-item labels containing `force`, and explicit mating/un-mating pair
  labels even when they omit the word `force`.
- A label containing only `mating` is not sufficient. Durability, mating-cycle,
  Reseating, and other non-Force families remain outside this task unless the
  Test Item explicitly represents both mating and un-mating.
- Numeric section facts remain source-faithful, for example `25.4 mm/min`,
  `>= 150 N`, or existing paired force limits.
- A residual label-only fragment such as `Cross Head Speed -` is not a usable
  speed result and must fall back to `mm/min`. Valid specialized composite
  output such as `10 times, mm/min` remains valid.
- The `mm/min` and `N` values are operator-review placeholders, not inferred
  measurements or acceptance limits.

## May Touch After Separate Implementation Approval

- `backend/modules/test_plan/spec_section_text_extractor.py`
- `backend/modules/test_plan/mcr_text_normalizer.py` only if a narrow
  Force-family label helper is needed
- focused unit/parser tests for the existing extraction path
- TASK_362C governance/evidence and `docs/task_board.md`

## Must Not Touch

- Fee rules/defaults/pricing, Matrix persistence/API/frontend, schema, real
  specification files, databases, workbooks, and project folders
- Existing non-Force parser families and Requirement wording that already
  contains a meaningful extracted value
- TASK_362B, TASK_361 authority lanes, generic Test Record, Report, LTR/public
  drive, and unrelated cleanup

## Acceptance Criteria

1. Every in-scope Force or explicit mating/un-mating pair family extracts
   explicit section speed and Requirement facts when available.
2. Missing or unusable in-scope speed, including a label-only speed fragment,
   yields exactly `mm/min`.
3. Missing in-scope Requirement yields exactly `N` after existing extraction
   and normalization have completed.
4. Existing meaningful Requirement text such as `No damage` is preserved.
5. Mating-only cycle/durability labels and unrelated non-Force families retain
   their current missing-value behavior.
6. Valid specialized composite Condition values such as `10 times, mm/min`
   remain intact.
7. Focused extractor/normalizer/parser tests pass without real-file I/O.

## Validation Gate

Cover current specialized Force branches, a generic Force label, a
mating/un-mating pair label without `force`, a mating-only non-Force control,
an empty section, a label-only speed fragment, valid composite output,
explicit numeric Requirement, existing `No damage`, and an unrelated
non-Force control. Run focused pytest, compile, diff/trailing, and scope scans.

## Merge Gate

Reviewer plan gate, explicit implementation approval, Developer, Reviewer, QA,
and Integrator hunk isolation are required. Stop after plan review until the
user explicitly approves coding.

## Completion Evidence

- Focused extractor, MCR normalizer, and Product Spec Matrix parser suite:
  `114 passed`.
- `py_compile` and scoped `git diff --check` passed.
- No real specification file, database, workbook, project folder, API, or
  frontend path was exercised or modified.
- The shared dirty worktree prevented a mixed commit; TASK_362C changes are
  recorded as isolated hunks only.
