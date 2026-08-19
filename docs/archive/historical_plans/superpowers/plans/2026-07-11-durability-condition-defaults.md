# Durability Condition Defaults

## Scope

Make Matrix Durability conditions concise and reviewable by extracting the
cycle count from sections `7.2` and `7.3`, while retaining an explicit
`mm/min` speed confirmation slot when the source section has no displacement
speed.

## Expected Output

- `7.2`: `20 cycles, mm/min`
- `7.3`: `200 cycles, mm/min`
- Existing `No damage` requirements remain unchanged.

## Files

- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_spec_section_text_extractor.py`
- `tasks/TASK_360J_DURABILITY_CONDITION_DEFAULTS.md`
- `docs/task_board.md`

## Boundary

Only the Durability condition extraction is changed. Existing method,
requirement, and unrelated family behavior remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
