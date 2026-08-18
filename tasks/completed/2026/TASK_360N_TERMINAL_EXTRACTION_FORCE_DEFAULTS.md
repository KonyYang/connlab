# TASK_360N - Terminal Extraction Force Defaults

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Goal

Extract the Condition and Requirement defaults for `Terminal extraction force`
from specification section `7.6`.

## Acceptance Criteria

- A numeric cross-head speed such as `50mm max per minute` becomes
  `50 mm/min`.
- The minimum extraction force becomes `≥ 150 N`.
- Missing source numbers leave the corresponding field blank.
- Existing unrelated Force behavior remains unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
