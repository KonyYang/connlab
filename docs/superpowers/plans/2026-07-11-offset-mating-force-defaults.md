# Offset Mating Force Defaults

## Scope

Populate the Matrix defaults for `Offset mating insertion force into floater`
from specification section `7.4`.

## Expected Output

- Condition: `10 times, 25.4 mm/min` when the source contains both values.
- Condition: `10 times, mm/min` when the speed number is absent.
- Requirement: `≤ 60 N` from the `no more than 60N` threshold.

## Boundary

Only the offset-mating-force Test Item gets this specialized rule. Existing
Durability, Mating/Un-mating Force, Normal Force, and generic extraction rules
remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
