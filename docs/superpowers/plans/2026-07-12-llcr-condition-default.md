# LLCR Condition Default

## Scope

Make `LLCR` use the same Condition rule as `Contact Resistance (Low Level)`.

## Expected Output

- Source condition present: preserve the extracted low-level measurement
  condition.
- Source condition absent: default to `20 mV, 100 mA`.

## Boundary

Only LLCR/low-level contact resistance Condition extraction changes. Existing
Requirement and unrelated CR families remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
