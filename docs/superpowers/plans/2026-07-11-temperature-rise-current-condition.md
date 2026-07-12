# Temperature Rise Current Condition

## Scope

Fill the Matrix Condition for temperature-rise rows from the source section's
test-current statement. Recognize both `Temperature rise` and `T-rise` test
item labels and normalize the source current token such as `75A` using the
existing display convention (`75 A`).

## Files

- `backend/modules/test_plan/spec_section_text_extractor.py`: add the narrow
  temperature-rise condition extractor.
- `tests/unit/test_spec_section_text_extractor.py`: cover `Temperature rise`
  and `T-rise` labels.
- `tasks/TASK_360H_TEMPERATURE_RISE_CURRENT_CONDITION.md`: task record.
- `docs/task_board.md`: completion note after validation.

## Boundaries

- No frontend, API, persistence, import, or report changes.
- No change to generic token extraction or unrelated test families.

## Validation

Run the focused extractor tests, the related parser/normalizer tests, and
`git diff --check`.
