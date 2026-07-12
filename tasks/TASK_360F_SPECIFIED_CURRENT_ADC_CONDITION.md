# TASK_360F Specified Current ADC Condition

Status: complete
Lane: `specified-current-adc-condition`
Owner Role: Developer
Created: 2026-07-11

## Purpose

Normalize the Matrix Condition for `Contact Resistance, Specified Current` to the report-aligned `ADC` unit spelling.

## Scope

- Convert conditions such as `75 a`, `75A`, and `75 amperes DC` to `75 ADC`.
- Preserve the existing space between the numeric value and unit.
- Limit the rule to the specified-current contact-resistance family.
- Do not change frontend behavior, API contracts, persistence, or unrelated units.

## Validation

- `py -m pytest tests\unit\test_mcr_text_normalizer.py tests\unit\test_spec_section_text_extractor.py tests\unit\test_product_spec_matrix_parser.py -q`: passed, `76 passed`.
- `py -m compileall -q backend\modules\test_plan\mcr_text_normalizer.py backend\modules\test_plan\spec_section_text_extractor.py`: passed.
