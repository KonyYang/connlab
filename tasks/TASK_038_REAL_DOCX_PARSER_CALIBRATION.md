# TASK_038_REAL_DOCX_PARSER_CALIBRATION

## Status

done

## Goal

Improve deterministic `.docx` parser coverage for the real application form layout documented in `docs/phase7_real_sample_baseline.md`.

## Scope

- Use the real `.docx` baseline only as local reference.
- Add sanitized or generated regression fixtures under `tests/fixtures/`.
- Improve parser extraction for real-style headers, footers, tables, sample rows, requested testing fields, and lab section fields.
- Keep parser output as draft data until human confirmation.
- Add/update focused parser tests.

## Out Of Scope

- LTR field catalog.
- LTR number rules.
- LTR workbook read/write.
- Folder evidence placement.
- Lifecycle guards.
- Frontend changes unless explicitly required by this task.
- Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
- Committing original real `.docx` files.

## Inputs

- `docs/phase7_real_sample_baseline.md`
- `C:\Users\White\Desktop\AI information\LTR by applicant.docx`
- `C:\Users\White\Desktop\AI information\LTR modifed by Tester.docx`
- Existing `backend/modules/intake/application_form_parser.py`

## Outputs

- Parser improvements.
- Generated/sanitized regression fixtures.
- Parser tests.
- Task board update after completion.

## Acceptance Criteria

- Form number/revision extracted when present.
- Requestor, phone, date, email, business unit, and project number are extracted from real-style layout.
- Sample fields are extracted or explicitly marked review-required by parser behavior/tests.
- Requested testing fields are extracted or explicitly marked review-required by parser behavior/tests.
- Applicant and tester-modified fixture layouts produce comparable structured drafts.
- Parser output remains draft-only before confirmation.

## Validation

- Run focused parser tests.
- Run related intake/precheck tests if parser behavior changes shared assumptions.
