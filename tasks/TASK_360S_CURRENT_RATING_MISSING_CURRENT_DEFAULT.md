# TASK_360S - Current Rating Missing Current Default

## Goal

Keep Current Rating Matrix defaults reviewable when the source omits the
current number but provides a temperature-rise limit.

## Acceptance Criteria

- `shall not exceed 30 deg C` normalizes to `≤ 30 ℃`.
- A missing current number produces `A` as the review placeholder for both
  Current Rating and Temperature rise.
- Existing Current Rating with a numeric current remains `75 A`.
- Ordinary Temperature rise behavior remains unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
