# TASK 007 — Application Form Parser

## Goal

Parse `.docx` laboratory test request forms into structured ApplicationForm and SampleInfo data.

## Scope

Implement parser only. No API upload yet unless simple local file service is already ready.

## Requirements

- Add `backend/modules/intake/application_form_parser.py`.
- Use `python-docx` first.
- Extract by labels/keywords, not hardcoded absolute table positions only.
- Extract:
  - Form No.
  - Form Rev.
  - Reference doc.
  - Lab Test Request Number.
  - Requested By.
  - Phone.
  - Date.
  - Email.
  - Business Unit.
  - Mfg. Site.
  - Project #.
  - Requested Testing Completion Date.
  - Results Format.
  - Test Type / Sample Status / Project Type if available.
  - Test Sample Information rows.
  - Post-testing disposition if available.
  - Description of Requested Testing.
  - Confidential/subcontract fields.
  - Additional Information.
  - Send copies recipients.
  - Section 2 lab fields.

## Parser Output

Return a parsed DTO/domain object without saving to DB.

## Tests

- Include tests using a small synthetic `.docx` fixture created in test code or a fixture file.
- Test extraction of at least one sample row.
- Test parser tolerates missing optional fields.

## Out of Scope

- No OCR.
- No PDF parsing.
- No AI extraction.
- No full customer-specific template support beyond robust label matching.

## Acceptance Criteria

- Parser returns structured data and sample rows.
- Missing fields are represented as None/empty, not crashes.
