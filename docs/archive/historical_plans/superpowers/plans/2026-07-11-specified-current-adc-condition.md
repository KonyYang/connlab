# Specified Current ADC Condition Implementation Plan

**Goal:** Normalize specified-current Matrix conditions to the report-aligned `75 ADC` format.

**Architecture:** Keep the change inside the existing `mcr_text_normalizer` path and gate it by the `Contact Resistance, Specified Current` test family.

## Changes

- `backend/modules/test_plan/mcr_text_normalizer.py`: normalize amperes/amps/A/ADC variants to `<value> ADC` for specified-current rows.
- `tests/unit/test_mcr_text_normalizer.py`: protect the `75 a` input case and expected `75 ADC` output.

## Validation

- Run the focused normalizer, extractor, and parser tests.
- Run Python compile checks and `git diff --check`.
