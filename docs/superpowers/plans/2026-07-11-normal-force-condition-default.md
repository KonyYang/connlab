# Normal Force Condition Default

## Scope

Populate the Matrix Condition for `Normal Force` from a numeric displacement
speed when present, or retain a visible `mm/min` confirmation slot when the
specification gives no speed number.

## Expected Output

- Numeric source: `25.4 mm/min`.
- Missing numeric source: `mm/min`.
- Existing Normal Force Requirement remains `≥ 1.5 N per beam`.

## Boundary

Only the Normal Force Condition rule changes. Existing Normal Force
Requirement and unrelated Force family rules remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
