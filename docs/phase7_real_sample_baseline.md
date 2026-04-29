# Phase 7 Real Sample Baseline

Date: 2026-04-27

## Scope

This baseline covers `TASK_037_REAL_SAMPLE_BASELINE` only. It documents current behavior against the real local samples and defines what later tasks must improve.

No original `.msg` or `.docx` files are committed. The probes used temporary workspace directories and did not modify the source files.

## Inputs

Sample folder:

```text
C:\Users\White\Desktop\AI information
```

Inventory observed:

| File | Type | Size | Expected baseline role |
|---|---:|---:|---|
| `Including two Lab Test Requirements and production specification.msg` | `.msg` | 7423488 | email with multiple application forms plus specification |
| `Lab Test Requirement in the attachment msg.msg` | `.msg` | 2857472 | email with request evidence but no extractable Word application form from current gateway |
| `Standard with Lab Test Requirement.msg` | `.msg` | 1108480 | email with one application form candidate |
| `Without Lab Test Requirement.msg` | `.msg` | 2082816 | email with no application form candidate |
| `LTR by applicant.docx` | `.docx` | 84132 | applicant-filled real application form |
| `LTR modifed by Tester.docx` | `.docx` | 88589 | tester-modified real application form |
| `申请 LTR 前必须字段.png` | `.png` | 35750 | LTR readiness field reference for later task |

## Probe Method

`.msg` samples were imported through `OfficeFacade.import_outlook_msg()` into a temporary directory under `tmp`. Attachment names, file kinds, and current filename-based candidate scores were recorded.

`.docx` samples were read through `OfficeFacade.read_word_document()` and parsed through the current `ApplicationFormParser`. Only structural coverage and field names are documented here, not sensitive field values.

## Outlook `.msg` Baseline

| Sample | Gateway status | Attachments extracted | Current candidate behavior | Expected operator action |
|---|---|---:|---|---|
| `Including two Lab Test Requirements and production specification.msg` | supported | 4 | Current filename score marks both Word request files as supporting attachments because their names lack current positive terms; PDF is correctly treated as supporting specification; image is supporting/inline evidence. | User must be able to select each Word request file as a separate application form case. `TASK_038` or a later candidate task should add content-aware or broader filename detection for `test Request` names. |
| `Lab Test Requirement in the attachment msg.msg` | supported | 10 | All extracted attachments are images; no `.docx` application form candidate is available to the current automated path. | Package should remain follow-up/review required. Operator may request a Word application form or manually create a form from evidence in a later explicitly scoped workflow. |
| `Standard with Lab Test Requirement.msg` | supported | 8 | One `.docx` with `E-3718` in the name scores as an application form candidate. Images score as supporting/inline evidence. | User selects the detected Word application form candidate and proceeds to case review. |
| `Without Lab Test Requirement.msg` | supported | 2 | PDF specification and image only; no application form candidate. | Package should not create a project. Operator follows up for missing application form or attaches the request as evidence only. |

Current `.msg` conclusions:

- The gateway can preserve/read all four real `.msg` samples and extract attachments.
- The existing candidate detector is too filename-dependent.
- A package can validly produce zero, one, or multiple application form cases.
- Inline image filtering is not yet strong enough to distinguish signature images from supporting evidence.

## Real `.docx` Parser Baseline

| Sample | Word snapshot | Current parser coverage | Current gaps | Expected next action |
|---|---|---|---|---|
| `LTR by applicant.docx` | 5 paragraphs, 18 tables, 2 headers, 2 footers; header contains laboratory request marker; footer contains form/revision marker | 6 top-level fields parsed; 0 lab fields; 0 sample rows | form number/revision not mapped from footer; phone/date/site/project/sample/project type/subcontract/requested testing/lab section missing; sample table not recognized | `TASK_038` must calibrate footer parsing, table/merged-cell handling, sample row extraction, and requested testing extraction. |
| `LTR modifed by Tester.docx` | 5 paragraphs, 17 tables, 2 headers, 2 footers; header contains laboratory request marker; footer contains form/revision marker | 7 top-level fields parsed; 0 lab fields; 0 sample rows | same gaps as applicant version; project number is additionally detected in tester-modified form | `TASK_038` must compare applicant-filled and tester-modified layouts and preserve comparable draft output. |

Fields currently parsed in at least one real form:

- `requested_by`
- `email`
- `business_unit`
- `project_number`
- `requested_completion_date`
- `results_format`
- `test_type`

Fields not reliably parsed yet:

- `form_no`
- `form_rev`
- `reference_doc`
- `lab_test_request_number`
- `phone`
- `request_date`
- `manufacturing_site`
- `sample_status`
- `project_type`
- `post_testing_disposition`
- `requested_testing_description`
- `confidential`
- `subcontract`
- `additional_information`
- `send_copies_recipients`
- all lab section fields
- all sample rows

## Fixture Strategy

Original real samples must remain local and uncommitted.

Recommended fixture plan for `TASK_038`:

1. Create minimal generated `.docx` fixtures under `tests/fixtures/` that reproduce the structural patterns found here:
   - header table with laboratory request marker;
   - footer containing `E-3718` and `Rev`;
   - real-style requestor/project/testing rows;
   - real-style sample table shape;
   - lab section table shape.
2. Avoid copying customer/product-specific content from the real files.
3. Keep one fixture for applicant-filled layout and one for tester-modified layout.
4. Use synthetic values that prove extraction behavior without exposing business data.

Recommended fixture plan for future `.msg` regression:

1. Keep current synthetic fixture-style `.msg` tests for deterministic parser behavior.
2. Add synthetic email fixtures with attachment names mirroring structural cases:
   - two Word files with `test Request` naming plus one PDF specification;
   - images only;
   - one `E-3718` Word form plus signature images;
   - specification-only request.
3. Do not commit original Outlook `.msg` files.

## Acceptance Mapping

`TASK_037` acceptance status:

- Each `.msg` sample has expected classification: complete.
- Each `.docx` form has parser field coverage notes: complete.
- Real sample paths are documented but not hard-coded into code: complete.
- Originals are not committed: complete.
- No Phase 7 downstream implementation started: complete.

## Known Limits For Next Task

- Current parser does not extract form number/revision from footer.
- Current parser does not handle real sample table shape.
- Current parser does not extract lab section fields from the real forms.
- Current filename candidate scoring misses real Word request files named with `test Request` but without `E-3718` or `application form`.
- Inline image evidence needs later classification policy.
