# TASK_360Q - LLCR Condition Default

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Goal

Provide the standard low-level measurement Condition when an LLCR source
section does not state one.

## Acceptance Criteria

- A present source condition is preserved.
- A blank source condition becomes `20 mV, 100 mA`.
- Existing LLCR Requirement and unrelated CR behavior remain unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
