# TASK_360K - Offset Mating Force Defaults

## Goal

Extract the operator-facing Condition and Requirement defaults for section
`7.4 Offset mating insertion force into floater`.

## Acceptance Criteria

- `10 times` is extracted from the offset-position mating instruction.
- A numeric displacement speed is rendered as `<value> mm/min`, ignoring the
  source tolerance suffix for the concise Matrix condition.
- Missing speed numbers retain the `mm/min` confirmation slot.
- `no more than 60N` becomes `≤ 60 N` in Requirement.
- Existing unrelated family behavior remains unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
