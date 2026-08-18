# TASK_360O - Normal Force Condition Default

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Goal

Populate a reviewable displacement-speed Condition for `Normal Force`.

## Acceptance Criteria

- A numeric speed such as `25.4±6 mm per minute` becomes `25.4 mm/min`.
- Missing speed numbers produce the `mm/min` confirmation slot.
- The existing `≥ 1.5 N per beam` Requirement is preserved.
- Unrelated Force behavior remains unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
