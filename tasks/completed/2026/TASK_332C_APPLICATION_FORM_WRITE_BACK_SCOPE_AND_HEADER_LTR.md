# TASK_332C Application Form Write-Back Scope And Header LTR

## Status

Complete.

## Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Needed

TASK_332A made copied Application Form Word write-back visible and verifiable, but the current field scope still treats several multi-row application-form detail fields as critical write-back targets. Manual review clarified that these fields are table line-item summaries in the request form, not stable single-value header fields:

- `Description P/N`
- `Product Description / Product Name`
- `Tests to be Performed / Test Item / Requested Testing`
- `Applicable Specifications`

Writing these summary values into a single cell can overwrite or distort multi-row request-form content. The Application Form write-back scope should instead focus on stable laboratory confirmation/header fields and make line-item table write-back a separate future task if needed.

## Goal

Adjust Application Form Word write-back so project folder generation updates only stable, safe Application Form targets and uses a safer header LTR replacement rule matching the real request-form header structure.

## In Scope

- Backend only.
- Application Form Word write-back behavior only.
- Update Application Form critical-field rules.
- Update header LTR write/read-back behavior.
- Keep existing selected copied request form targeting in `Submitted Material`.
- Keep COM gateway boundary; API/application services must not directly automate Word.
- Add automated fake/pure tests for the new scope and header behavior.
- Add or update a manual smoke checklist for copied real request-form samples.

## Out Of Scope

- No Workbench UI changes.
- No Basic Information schema/API/persistence changes.
- No project folder template/copy/archive logic changes.
- No Fee Form or Customer Feedback changes.
- No LTR workbook sync changes.
- No Report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- No line-item Application Form table model or row-level write-back.

## Product Rules

### Multi-Row Detail Fields

These fields should not be treated as critical Application Form write-back targets in this task:

- `description_pn`
- `product_description`
- `test_item`
- `applicable_specifications`

Reason: in the real Application Form they can represent multi-row table content. TASK_332C should not guess which row to write or collapse multiple rows into one summary cell.

Implementation rule:

- TASK_332C must remove these fields from the Application Form write-back payload/mapping path.
- They must not be written to copied Application Form Word files in this task, even as optional fields.
- They remain available to Basic Information, Fee Form, Customer Feedback, Test Record, LTR workbook, and future Report outputs through their own output mappings.
- Future Application Form row-level write-back requires a separate line-item model/task.

### Critical Fields

The formal Application Form write-back critical fields are:

- header `Lab Test Request Number` / LTR number
- `Lab Performing the Tests`
- `Lab Personnel Assigned`
- `Date Lab Received Samples`
- `Estimated Completion Date`
- `Condition of Samples when Received`

Critical value rule:

- These critical values must be present before Application Form write-back starts.
- If any critical value is missing or blank, the Application Form write-back step must return a blocker instead of silently skipping the field.
- `Lab Personnel Assigned` must use one canonical payload key: `project_leader`.
- Existing `assigned_personnel` may only be used as a fallback when `project_leader` is blank. It must not be sent alongside `project_leader`, and it must not be a separate critical field.

Critical write failure, missing target, or read-back mismatch must block the Application Form write-back step.

### Header LTR Rule

The real header structure is:

```text
Lab Test Request Number:
DL-2026-05-011
Page 1 / 2
```

Write rule:

1. Find a header paragraph containing `Lab Test Request Number`.
2. Find the value paragraph after that label and before the next `Page` paragraph.
3. If a value paragraph exists and contains a `DL-...` style value, replace that value with the current LTR.
4. If a value paragraph exists but is blank/non-LTR, replace that paragraph text with the current LTR.
5. If no value paragraph exists but a `Page` paragraph exists, insert a new LTR paragraph before `Page`.
6. If a safe label/value/page structure cannot be found, return a blocker. Do not rewrite the entire header cell.

Read-back rule:

- Header verification succeeds only when exactly one non-empty value paragraph exists between `Lab Test Request Number` and `Page`, and that extracted value equals the expected LTR after cleanup.
- If multiple non-empty paragraphs exist between label and page, the writer may replace one recognized `DL-...` paragraph only when all other intermediate paragraphs are blank. Multiple non-empty non-LTR paragraphs must block instead of being concatenated or treated as a loose contains match.

## Planned File Changes

- Modify `backend/infrastructure/office/application_form_word_mapping.py`
  - Update `APPLICATION_FORM_CRITICAL_FIELDS` to the new laboratory/header critical set.
  - Remove multi-row detail fields from the Application Form write-back mapping path for this task.
- Modify `backend/infrastructure/office/application_form_word_gateway.py`
  - Refine `_replace_header_ltr_value` to replace/insert the paragraph between label and page.
  - Refine `_header_ltr_visible_value` or add a small helper to extract the header LTR value.
  - Ensure unsafe header structure raises a clear blocker.
  - Ensure multiple non-empty intermediate header paragraphs block unless the structure has one exact replaceable LTR value and otherwise blank lines.
  - Keep body/table read-back exact matching from TASK_332A.
- Modify `backend/application/project_application_form_write_back_service.py`
  - Validate the required write-back values before calling the Office gateway.
  - Build one canonical `project_leader` value for `Lab Personnel Assigned`, falling back to parsed `assigned_personnel` only when confirmed `project_leader` is blank.
  - Do not pass both `project_leader` and `assigned_personnel` to the Office gateway.
  - Do not pass multi-row detail fields to the Application Form gateway.
- Modify `backend/infrastructure/office/word_document_gateway.py`
  - Ensure python-docx fallback uses the updated critical-field set.
  - No new COM code here.
- Add or update `tests/unit/test_application_form_word_gateway.py`
  - Header existing `DL-...` paragraph is replaced.
  - Blank value paragraph is filled.
  - Missing value paragraph inserts before `Page`.
  - Missing safe `Page` structure blocks.
  - Multiple non-empty paragraphs between label and page block.
  - Body read-back remains exact.
  - Multi-row detail fields are not written.
- Add or update `tests/unit/test_word_document_gateway.py`
  - Plain fallback no longer receives `test_item` / `applicable_specifications` from the Application Form write-back service.
  - Plain fallback still blocks when laboratory critical fields are absent.
- Update `docs/task_board.md`
  - Mark TASK_332C proposed or complete only according to implementation state.

## Acceptance Criteria

- Application Form write-back no longer blocks project folder generation because `Description P/N`, `Product Description`, `Tests to be Performed`, or `Applicable Specifications` cannot be safely written.
- Application Form write-back no longer writes `Description P/N`, `Product Description`, `Tests to be Performed`, or `Applicable Specifications` to the copied Application Form Word file in TASK_332C.
- Application Form write-back blocks before Office write when any critical value is blank.
- `Lab Personnel Assigned` is written from one canonical payload key, preferring confirmed `project_leader` and using parsed `assigned_personnel` only as fallback.
- Application Form write-back does block when any provided laboratory/header critical field cannot be written or verified:
  - header LTR
  - `Lab Performing the Tests`
  - `Lab Personnel Assigned`
  - `Date Lab Received Samples`
  - `Estimated Completion Date`
  - `Condition of Samples when Received`
- Header LTR is updated by replacing/filling/inserting the paragraph between `Lab Test Request Number` and `Page`, not by rewriting the whole header cell.
- Existing `DL-...` header values are replaced with the current project LTR.
- Header structures with multiple non-empty intermediate paragraphs block unless one exact LTR paragraph is safely replaceable and other intermediate paragraphs are blank.
- Unsafe header structure returns a blocker with an actionable message.
- Tests do not depend on external user sample files.
- Existing TASK_332A selected-request-form targeting remains unchanged.

## Test Plan

- `py -m pytest tests/unit/test_application_form_word_gateway.py -q`
- `py -m pytest tests/unit/test_word_document_gateway.py -q`
- `py -m pytest tests/unit/test_project_application_form_write_back_service.py -q`
- `py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q`
- Optional manual smoke:
  - Copy a real request-form `.docx` into `tmp/`.
  - Run Application Form write-back against the copy.
  - Reopen the copy and verify header LTR plus the laboratory confirmation fields.
  - Confirm multi-row detail fields were not overwritten.

## Risks

- Word header paragraph structure can vary by template revision. The implementation must prefer blocker over destructive rewrite when the structure is unknown.
- Future row-level Application Form detail write-back needs a separate data model and should not be smuggled into this task.

## Completion Notes

- Application Form Word write-back is narrowed to stable laboratory/header fields only: header LTR, lab, project leader / assigned personnel, received date, estimated completion date, and sample condition.
- Multi-row detail fields are no longer sent to the Application Form write-back path in this task: `description_pn`, `product_description`, `test_item`, and `applicable_specifications`.
- `Lab Personnel Assigned` uses canonical `project_leader`, with parsed `assigned_personnel` only as a fallback before the Office gateway call.
- Missing critical values block before Office write-back starts.
- Header LTR replacement now normalizes the header cell to `Lab Test Request Number:` / blank paragraph / current `DL-...` / `Page ...`; ambiguous or unsafe header structures block instead of rewriting the whole header cell.
- Because Word COM can reject deletion of the cell-final empty paragraph, a narrow DOCX header XML cleanup runs before and after Word COM to repair/normalize the header and remove trailing blank paragraphs after `Page` while preserving the rest of the document package.
- Recovery-prompt follow-up fixed the XML cleanup namespace handling so `mc:Ignorable` prefixes such as `w15`, `w16...`, and `wp14` remain declared instead of being rewritten to invalid automatic `ns*` prefixes.
- Visible read-back remains exact for normal text fields. Word date content controls are accepted when their displayed date format is semantically equal to the requested `received_date` or `estimated_completion_date`.

## Validation

- `py -m pytest tests/unit/test_application_form_word_gateway.py tests/unit/test_word_document_gateway.py tests/unit/test_project_application_form_write_back_service.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q` (`63 passed`)
- Manual Word COM smoke on copied real request forms in `tmp/task_332c_header_fixed_layout_smoke/` and `tmp/task_332c_recovery_fix_smoke/` verified the fixed header paragraph layout, namespace repair, Word reopen without recovery prompt, lab, project leader, received date, estimated completion date, and sample condition with no warnings.
- `git diff --check` reported no whitespace errors, only CRLF conversion warnings.

## Stop Point

This task is proposed only. Do not implement until the user explicitly approves TASK_332C.
