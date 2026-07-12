# TASK_360J - Durability Condition Defaults

## Goal

Populate concise, operator-reviewable Conditions for Durability sections `7.2`
and `7.3`.

## Acceptance Criteria

- Section `7.2` extracts `20 cycles` and includes the `mm/min` confirmation
  slot.
- Section `7.3` extracts `200 cycles` and includes the `mm/min` confirmation
  slot.
- A source-provided `mm/min` speed is preserved when present.
- Existing `No damage` requirements and unrelated family behavior remain
  unchanged.

## Validation

- Focused extractor, normalizer, and parser tests pass.
- `git diff --check` passes, allowing existing CRLF warnings only.
