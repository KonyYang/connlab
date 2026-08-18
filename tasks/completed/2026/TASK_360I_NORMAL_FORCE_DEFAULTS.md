# TASK_360I - Normal Force Defaults

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Goal

Fill the Matrix defaults for `Normal Force` from specification section `7.7`.

## Acceptance Criteria

- Section `7.7` continues to produce `EIA-364-04` as Method.
- Condition remains empty because the source provides no separate condition.
- The source threshold `not less than 1.5N per beam` becomes
  `≥ 1.5 N per beam` in Requirement.
- Existing family behavior remains unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
