# TASK_360N - Terminal Extraction Force Defaults

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
