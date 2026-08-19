# Normal Force Defaults

## Scope

Populate the Matrix defaults for section `7.7 Normal Force` from the
specification text. The source states the EIA method and a minimum normal
force per beam, but no separate condition.

## Expected Output

- Method: `EIA-364-04`
- Condition: empty
- Requirement: `≥ 1.5 N per beam`

## Files

- `backend/modules/test_plan/spec_section_text_extractor.py`
- `tests/unit/test_spec_section_text_extractor.py`
- `tasks/TASK_360I_NORMAL_FORCE_DEFAULTS.md`
- `docs/task_board.md`

## Boundary

Only the Normal Force requirement extraction is added. Existing Method,
Condition, and unrelated test-family rules remain unchanged.

## Validation

Run the focused extractor/normalizer/parser tests and `git diff --check`.
