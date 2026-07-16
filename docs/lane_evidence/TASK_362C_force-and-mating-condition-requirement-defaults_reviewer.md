# TASK_362C Force and Mating Defaults Reviewer Evidence

Status: reviewer_pass
Date: 2026-07-17
Role: Reviewer

## Gate

Reviewer plan gate only. No product code, parser behavior, test implementation,
real specification file, database, workbook, API, or frontend change was made
by this review.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package
controlled foundation.

Current task: `TASK_362C_FORCE_AND_MATING_CONDITION_REQUIREMENT_DEFAULTS`,
planned-only.

Why allowed: `TASK_362B` is complete/accepted and the board records TASK_362C
as the current planned lane.

## Findings And Corrections

1. The original `force` / `mating` substring predicate was too broad. A
   mating-only durability or cycle label could be misclassified. The reviewed
   plan now requires either a `force` token or an explicit pair of mating and
   un-mating concepts, evaluated from the Test Item label only.
2. The original empty-value test was too weak. Existing generic collection can
   return a non-empty label-only fragment such as `Cross Head Speed -` without
   extracting a numeric speed. The reviewed plan now requires a usable numeric
   speed or a valid specialized composite; otherwise Condition becomes exactly
   `mm/min`.
3. Requirement fallback remains last, after extraction and normalization, so
   explicit force limits and meaningful text such as `No damage` are preserved.

The acceptance matrix now covers the specialized branches, generic Force,
explicit mating/un-mating without `force`, mating-only exclusion, empty and
label-only speed cases, specialized composite preservation, numeric and
no-damage Requirements, and an unrelated control.

## Decision

`reviewer_pass`

Recommended next action: explicit user approval for Developer implementation.

Blocking summary: none.
