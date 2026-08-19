# Floater Displacement Force Defaults

## Scope

Populate the Matrix defaults for `Floater Displacement Force (Side Force)`
from section `7.4`.

## Expected Output

- Condition: `25.4 mm/min` when the displacement-speed number is present.
- Requirement: `10 N ≤ Displacement Force ≤ 40 N` when both force limits are
  present.
- Missing source values remain blank.

## Boundary

Only the Floater Displacement Force family gets this specialized rule. The
existing Offset Mating Force rule and generic Force extraction remain
unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
