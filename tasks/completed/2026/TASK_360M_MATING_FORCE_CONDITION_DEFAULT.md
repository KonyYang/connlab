# TASK_360M - Mating Force Condition Default

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Goal

Populate the Matrix Condition for `Mating/Un-mating Force` from its cross-head
speed statement.

## Acceptance Criteria

- A numeric speed such as `25.4±6 mm per minute` becomes `25.4 mm/min`.
- Missing speed numbers leave Condition blank.
- Existing Requirement and unrelated family behavior remains unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
