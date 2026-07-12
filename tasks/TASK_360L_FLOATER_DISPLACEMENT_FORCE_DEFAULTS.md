# TASK_360L - Floater Displacement Force Defaults

## Goal

Extract the Condition and Requirement defaults for `Floater Displacement Force
(Side Force)` from specification section `7.4`.

## Acceptance Criteria

- A numeric displacement speed is rendered as `<value> mm/min`, ignoring the
  source tolerance suffix for the concise Matrix condition.
- The lower and upper force limits become
  `10 N ≤ Displacement Force ≤ 40 N`.
- Missing speed or force data remains blank.
- Existing Offset Mating Force and unrelated family behavior remains
  unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
