# TASK_080_DOCX_PARSER_FIELD_CALIBRATION_FOR_SECTION1

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion.

## Goal

Calibrate the E-3718 Rev H `.docx` parser and draft field mapping for SECTION 1 project-creation fields before further Precheck UI completion.

## Inputs

- Real or desensitized sample:
  - `local/office files samples/E-3718_H Laboratory Test Request-Even.docx`
- User-reported Precheck issues from 2026-05-03:
  - `Business Unit` is parsed as `Mfg. Site:` or otherwise absorbs the following label/value.
  - `Date` does not map to the application form request date.
  - `Phone #` is not imported into the draft.

## Scope

Allowed:

- Parser rule adjustments for table-driven E-3718 Rev H SECTION 1 fields.
- Regression tests with generated or sanitized fixtures.
- Draft mapping corrections if parsed values are available but not surfaced.
- Clear parser warning behavior when a required field is genuinely blank.

Not allowed:

- Changing lookup option storage.
- Broad Precheck UI redesign.
- Sample row edit/copy/delete implementation.
- LTR workbook write hardening.
- Future Matrix, Report, AI review, LAN, permissions, or Outlook inbox automation.

## Acceptance Criteria

- Real-style E-3718 Rev H parser tests cover `phone`, `request_date`, `business_unit`, and `manufacturing_site`.
- Parser does not confuse neighboring labels as values.
- Blank fields remain blank and are reported as missing by deterministic precheck instead of being filled with label text.
- Existing intake/precheck parser tests continue to pass.

## Completion Notes

- Added parser protection so neighboring labels such as `Mfg. Site:` and `Requested Testing Completion Date:` are not accepted as field values.
- Added ordered E-3718 Rev H content-control extraction for SECTION 1 and related downstream form fields.
- Verified the provided local sample now extracts Phone, Date, Business Unit, Mfg. Site, Results Format, requested completion date, Test Type, Sample Status, Project Type, and Post-Testing Sample Disposition.
- Added a Precheck UI hotfix so Word-style dates such as `10/11/2024` render correctly in browser date inputs as `2024-10-11`.

## Validation

- `py -m pytest tests\unit\test_application_form_parser.py tests\integration\test_intake_precheck_api.py -q`
- Result: `9 passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py tests\unit\test_application_form_parser.py -q`
- Result: `31 passed`
- `npm run build`
- Result: passed
