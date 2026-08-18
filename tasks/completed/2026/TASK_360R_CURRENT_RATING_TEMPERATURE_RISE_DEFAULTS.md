# TASK_360R - Current Rating Temperature-Rise Defaults

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Goal

Apply the Temperature rise default parsing rules to `Current Rating` rows.

## Acceptance Criteria

- A Current Rating section with `75A` extracts Condition as `75 A`.
- A Current Rating temperature limit such as `shall not exceed 30 C` becomes
  `≤ 30 ℃` in Requirement.
- Existing Temperature rise and unrelated family behavior remains unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
