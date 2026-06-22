# TASK_332A Application Form Word Visible Write-Back

## Status

Complete including review fixes. Implemented and verified on 2026-06-22.

## Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed Now

TASK_332 is complete, but manual smoke testing found a defect in its Application Form Word write-back output: the copied request form file timestamp changes, yet the visible Word content remains unchanged. This is a TASK_332 follow-up defect fix because it affects formal project folder output generation. It does not introduce new UI, LTR sync behavior, report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Goal

Make copied Application Form Word write-back visibly update the selected request form in `Submitted Material` when `Generate project folder` / `Update project folder` runs, including header LTR number and modeled Basic Information fields stored in Word tables, content controls, or legacy form fields.

## Problem Statement

The current implementation can reach the selected copied Application Form path, and the file can be saved, but visible content may remain unchanged because the request form template contains Word-specific structures:

- header table content for `Lab Test Request Number`
- content controls such as dropdowns, text controls, or date controls
- legacy form fields
- table layouts where values are sometimes in the cell to the right, and sometimes in the row below the label

`python-docx` can edit simple table text, but it is not reliable for visible updates to Word content controls, form fields, or the header behavior used by the real Application Form template. TASK_332A should use the existing Office infrastructure boundary to handle these Word-specific write targets while preserving a safe fallback for plain `.docx` documents where applicable.

## In Scope

- Backend only.
- Add or update Application Form Word write-back behavior behind the infrastructure Office gateway boundary.
- Update the application-form field mapping used by formal Project Folder output write-back.
- Ensure the selected request form copied into `Submitted Material` is the target file.
- Write visible values for:
  - `Lab Test Request Number` / LTR number in the header.
  - `Project Type`.
  - `Test Type`.
  - `Requested By`.
  - `Phone #`.
  - `Email`.
  - `Business Unit`.
  - `Project #`.
  - manufacturing site / location.
  - subcontract flag.
  - `Tests to be Performed`.
  - `Applicable Specifications`.
  - `Lab Performing the Tests`.
  - `Lab Personnel Assigned`.
  - `Date Lab Received Samples`.
  - `Estimated Completion Date`.
  - `Condition of Samples when Received`.
- Return meaningful warnings or blockers when a mapped field cannot be found or cannot be written because a Word control is locked or unsupported.
- Treat these as critical fields for formal write-back: header LTR number, `Requested By`, manufacturing site / `location`, `Tests to be Performed`, `Applicable Specifications`, and `Lab Performing the Tests`. Critical field write or verification failure must block/fail the write-back step; non-critical missing fields may be warnings.
- Add automated regression tests for field mapping, selected-target behavior, and Word gateway behavior using fixtures/fakes that do not depend on user desktop files.
- Add an optional manual smoke procedure using a copied real `.docx` instance, never mutating the user’s original sample unless they explicitly ask.

## Out Of Scope

- No Workbench UI changes.
- No Project Basic Information schema/API/persistence changes.
- No Matrix/Fee behavior changes.
- No LTR workbook sync or TASK_333 behavior changes.
- No report generation.
- No StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- No direct dependency on `D:/PythonProject/TestFlowManager` code. The old utility may be used only to understand field-location intent.
- No automated tests that depend on `C:/Users/White/Desktop/...` or `D:/Test Project/...` sample files.

## Technical Decision

Use a hybrid Word gateway strategy:

1. Keep `python-docx` as the lightweight fallback for simple plain-table `.docx` documents.
2. Add a Word COM-backed write path inside `backend/infrastructure/office/word_document_gateway.py` for Application Form write-back, because the real request form uses header content, content controls, and form fields that require Microsoft Word’s object model for visible updates.
3. Do not silently claim success if COM is unavailable for a document that contains Word content controls, legacy form fields, or the header LTR target. In the formal Project Folder flow this must surface as a blocked/failed Application Form write-back step, not as a warning while the overall output reports success.
4. Keep business orchestration in `backend/application/project_application_form_write_back_service.py`; it must not directly call COM or inspect Word internals.

This is not a copy of the old TestFlowManager utility. The old utility only informs field-location rules. The ConnLab implementation must stay inside the current architecture: application service -> Office facade/gateway -> Word implementation.

## Design Notes

### Field Location Rules

- Header:
  - Find `Lab Test Request Number` in header tables and write the LTR value in the visible header location used by the template.
- Same-row fields:
  - Find label cell and write to the cell on the right.
  - Examples: `Requested By:`, `Phone #:`, `Email:`, `Business Unit:`, `Project #:`, `Mfg. Site:`, `Lab Performing the Tests:`, `Lab Personnel Assigned:`, `Date Lab Received Samples:`, `Estimated Completion Date:`, `Condition of Samples when Received:`.
- Next-row fields:
  - Find label cell and write to the same column in the next row.
  - Examples: `Project Type`, `Test Type`, `Test Sample Status`, `Tests to be Performed`, `Applicable Specifications`.

### Word Control Rules

- If the target cell contains a content control:
  - text/date/plain/rich controls: write visible text through the control range.
  - dropdown controls: select a matching entry when available; if no matching entry exists, report a warning/blocker rather than writing invisible text.
  - combo boxes may accept text only if Word accepts the value and read-back verification passes.
  - checkboxes may only be set when the source value can be normalized to a boolean.
  - locked controls: report a warning/blocker.
- If the target cell contains a legacy text form field:
  - write through the form field result.
- If the target cell has no Word control:
  - write normal cell text.

### Verification Rule

The task is not complete when the file timestamp changes. It is complete only when a verification read proves the visible Word value changed in a copied test document. COM write-back must verify header LTR and all provided critical fields before reporting success.

## Planned File Changes

- Modify `backend/infrastructure/office/word_document_gateway.py`
  - Add Application Form COM write path.
  - Add header LTR writer.
  - Add label matching rules and same-row / next-row target resolution.
  - Add content-control and form-field write helpers.
- Modify or confirm `backend/infrastructure/office/office_facade.py`
  - Keep the existing facade method as the application boundary.
- Modify or confirm `backend/application/project_application_form_write_back_service.py`
  - Keep selected copied request form targeting.
  - Surface write warnings/blockers clearly.
- Add or update `tests/unit/test_word_document_gateway.py`
  - Cover field labels and target-resolution behavior without real user files.
  - Cover COM writer behavior with fakes/mocks where possible.
- Add or update `tests/unit/test_project_application_form_write_back_service.py`
  - Ensure the copied selected request form remains the target.
  - Ensure warning/blocker results are propagated.
- Optionally add `tests/manual/` documentation or a smoke helper that copies a real sample into `tmp/` and verifies visible field values, but only as a manual diagnostic path.

## Acceptance Criteria

- Creating/updating a project folder writes visible Application Form values into the selected copied request form in `Submitted Material`.
- Header `Lab Test Request Number` visibly contains the project LTR number.
- COM write-back read-back verifies header LTR and the provided critical fields before returning success.
- If a critical field cannot be found, cannot be written, or does not match read-back verification, the Application Form write-back step is blocked/failed with an actionable message.
- If COM is unavailable for the real Word-form request document, the Application Form write-back step is blocked/failed; it is not reported as successful with warnings.
- At minimum, manual smoke can prove visible updates for:
  - LTR number
  - Requested By
  - Phone
  - Email
  - Business Unit
  - Mfg. Site / location
  - Tests to be Performed
  - Applicable Specifications
  - Lab Performing the Tests
  - Lab Personnel Assigned
  - Date Lab Received Samples
  - Estimated Completion Date
- If multiple request forms were parsed from the same imported email, the write-back targets the selected request form copied into `Submitted Material`, not an arbitrary `.docx`.
- A file modified timestamp alone is not treated as success.
- The payload passed to the Word gateway is aligned with TASK_332 formal output values; tests must prove `location`, `project_leader`, `test_item`, and `applicable_specifications` are not lost before gateway write-back.
- Tests do not depend on external user sample paths.

## Test Plan

- Unit:
  - `py -m pytest tests/unit/test_word_document_gateway.py -q`
  - `py -m pytest tests/unit/test_project_application_form_write_back_service.py -q`
- Integration/regression if existing coverage applies:
  - `py -m pytest tests/unit/test_project_folder_required_forms_service.py -q`
  - `py -m pytest tests/integration/test_project_folder_required_forms_api.py -q`
- Manual smoke:
  - Copy the real sample `.docx` into a workspace `tmp/` folder.
  - Run the Application Form write-back through the ConnLab gateway or Project Folder output flow against the copy.
  - Re-open/read the copied `.docx` and verify visible field values, not only file modification time.
  - Close without manually saving, reopen/read again, and confirm values persist.

## Risks

- Word COM can be slower than `python-docx`, but Application Form write-back is a formal Office output operation and correctness is more important than speed here.
- Some dropdown values may not exactly match template options. The implementation must report this clearly instead of pretending success.
- Locked controls may require a future template-maintenance task if the Word template prevents automation.
- COM automation must release Word documents and application instances reliably.

## Completion Notes

- Application Form Word write-back now detects real Word form documents and uses the Word COM gateway path instead of silently relying on `python-docx`.
- Header LTR and critical fields are verified by visible read-back before success.
- Plain `.docx` table fallback remains for simple documents and now supports same-row and next-row target rules.
- Critical field failures are surfaced as Application Form write-back blockers.
- Review follow-up split Application Form COM write-back helpers out of the general Word gateway into `application_form_word_gateway.py`, with mapping constants isolated in `application_form_word_mapping.py`, keeping Office gateway files within the project 500-line hard limit.
- Review follow-up tightened visible read-back verification: body/table target cells require exact cleaned visible-value equality, while header LTR keeps label/value mixed-text matching.
- Review follow-up constrained the `Business Unit` row site fallback to the observed six-column request-form shape and changed unsafe header LTR fallback behavior to block when a safe replacement point cannot be found.
- Manual smoke used copied request forms under `tmp/task_332a_smoke/` and `tmp/task_332a_smoke_review_fix/`; the original user sample was not modified.

## Validation

- `py -m pytest tests/unit/test_application_form_word_gateway.py tests/unit/test_word_document_gateway.py tests/unit/test_project_application_form_write_back_service.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q` passed (`49 passed`).
- Manual COM smoke on copied request form verified visible values after reopen:
  - header LTR contains `DL-2026-05-011`
  - `requested_by` = `Ming-Peng.Cao`
  - `location` = `Dongguan`
  - `test_item` = `Qualification test`
  - `applicable_specifications` = `GS-12-2113 Rev3`
  - `lab` = `Dongguan`
- `git diff --check` passed with CRLF warnings only.

## Stop Point

TASK_332A is complete. Stop here and wait for the next explicitly approved task.
