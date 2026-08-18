# TASK_360P - Dust Exposure Condition Defaults

Status: closed (archived 2026-08-18; superseded by Sol-native manual task publishing; implementation not approved)

## Goal

Populate a concise, report-style Condition for `Dust exposure`.

## Acceptance Criteria

- Default Condition is `Benign dust composition 1#, 1 hour, unmated for both connectors`.
- A numbered dust composition such as `2#` is preserved.
- Ambiguous connector states do not receive the automatic bilateral-unmated
  suffix and remain reviewable by the operator.
- Existing method and unrelated family behavior remain unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
