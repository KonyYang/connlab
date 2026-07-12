# TASK_360H - Temperature Rise Current Condition

## Goal

Populate blank Matrix Condition values for temperature-rise test items from
the applicable specification section's current statement, for example `75A`.

## Allowed Scope

- Temperature-rise condition extraction in the specification section parser.
- Focused unit tests.
- Task documentation and board completion note.

## Acceptance Criteria

- `Temperature rise` rows extract the first current value from the section.
- `T-rise` rows use the same rule.
- Existing specified-current and unrelated family behavior remains unchanged.

## Validation

- Focused extractor tests pass.
- Related parser/normalizer tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
