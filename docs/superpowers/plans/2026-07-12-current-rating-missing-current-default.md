# Current Rating Missing Current Default

## Scope

Refine the `Current Rating` temperature-rise alias for source sections that
state the temperature limit but omit the rated-current number.

## Expected Output

- `shall not exceed 30 deg C` becomes `≤ 30 ℃`.
- Missing current uses the `A` review placeholder for both Current Rating and
  ordinary Temperature rise behavior.

## Boundary

Current Rating and ordinary Temperature rise rows share the same
missing-current placeholder behavior.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
