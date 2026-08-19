# Current Rating Temperature-Rise Defaults

## Scope

Treat `Current Rating` as the same Matrix extraction and normalization family
as `Temperature rise`.

## Expected Output

- Condition extracts the section current, for example `75 A`.
- Requirement normalizes the temperature-rise limit, for example `≤ 30 ℃`.

## Boundary

Only the `Current Rating` family alias changes. Existing Temperature rise,
CR, Force, and unrelated family behavior remains unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
