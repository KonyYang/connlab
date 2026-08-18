# TASK_332C Application Form Write-Back Scope And Header LTR Plan

## Summary

TASK_332C should narrow Application Form write-back to stable laboratory/header fields and make header LTR replacement match the real Word header structure. It should not attempt row-level request-form detail-table synchronization.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Task

`TASK_332C_APPLICATION_FORM_WRITE_BACK_SCOPE_AND_HEADER_LTR`

## Why This Task Is Allowed When Approved

This is a controlled follow-up to TASK_332A/TASK_332 official output write-back. It fixes Application Form write-back scope and safety. It does not introduce new UI, Basic Information schema changes, project folder orchestration changes, LTR workbook behavior, report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

## Implementation Design

### 1. Critical Field Scope

Modify `APPLICATION_FORM_CRITICAL_FIELDS` so only these fields block:

- `ltr_number`
- `lab`
- `project_leader`
- `received_date`
- `estimated_completion_date`
- `sample_condition`

Keep aliases aligned with existing Basic Information/Application Form payload:

- `lab` maps to `lab_performing_tests`
- `project_leader` maps to Lab Personnel Assigned style labels
- `received_date` maps to Date Lab Received Samples
- `sample_condition` maps to Condition of Samples when Received

Canonical payload rule:

- `Lab Personnel Assigned` must be represented by one payload key: `project_leader`.
- Parsed `assigned_personnel` may only be used as a fallback when confirmed Basic Information `project_leader` is blank.
- The Office gateway must not receive both `project_leader` and `assigned_personnel`.

Required value rule:

- `ltr_number`, `lab`, `project_leader`, `received_date`, `estimated_completion_date`, and `sample_condition` must be non-empty before the Office gateway is called.
- Missing required values return an Application Form write-back blocker; they are not silently skipped.

### 2. Excluded Multi-Row Detail Fields

Remove these fields from Application Form Word write-back in TASK_332C:

- `description_pn`
- `product_description`
- `test_item`
- `applicable_specifications`

They remain available for other outputs, but this task must not write them to copied Application Form Word files. Do not add any row-level write-back logic.

### 3. Header LTR Replacement

Update the Word COM header writer to operate on paragraphs:

1. Locate label paragraph containing `Lab Test Request Number`.
2. Locate following `Page` paragraph.
3. Inspect paragraphs between them.
4. Replace an existing `DL-...` paragraph if found.
5. Else fill a blank/intermediate value paragraph if present.
6. Else insert a new value paragraph before `Page`.
7. If label/page cannot be found, raise `ValueError` with a clear message.

Do not rewrite the whole header cell.

### 4. Verification

Header read-back should extract the value between label and page. Verification should confirm the extracted value equals the expected LTR after cleanup. Body/table critical fields should continue exact visible-value comparison.

If there are multiple non-empty paragraphs between `Lab Test Request Number` and `Page`, implementation must block unless exactly one of those paragraphs is a replaceable `DL-...` value and all other intermediate paragraphs are blank. Do not concatenate intermediate text and do not use loose `contains` matching.

## File-Level Changes

- `backend/infrastructure/office/application_form_word_mapping.py`
  - Update critical field set.
- `backend/application/project_application_form_write_back_service.py`
  - Validate critical values before Office write-back.
  - Build one canonical `project_leader` value and drop `assigned_personnel` unless it is used as fallback.
  - Exclude multi-row detail fields from Application Form gateway payload.
- `backend/infrastructure/office/application_form_word_gateway.py`
  - Update header paragraph replacement/read-back helpers.
  - Keep exact body read-back.
- `backend/infrastructure/office/word_document_gateway.py`
  - Consume updated critical-field set only; keep thin fallback.
- `tests/unit/test_application_form_word_gateway.py`
  - Add fake paragraph/header tests.
  - Add critical/non-critical behavior tests where appropriate.
- `tests/unit/test_word_document_gateway.py`
  - Update missing-critical tests to reflect new critical set.
- `tasks/TASK_332C_APPLICATION_FORM_WRITE_BACK_SCOPE_AND_HEADER_LTR.md`
  - Mark status after implementation.
- `docs/task_board.md`
  - Record proposed/complete status.

## Detailed Tasks

### Task 1: Update Field Scope Tests

- Add a unit test proving missing `test_item` and `applicable_specifications` do not block plain fallback write-back.
- Add a unit test proving `test_item` and `applicable_specifications` are not passed to the Application Form gateway payload.
- Add a unit test proving missing `lab`, `project_leader`, `received_date`, `estimated_completion_date`, or `sample_condition` values block before Office write-back.
- Add a unit test proving parsed `assigned_personnel` is used only when confirmed `project_leader` is blank, and both keys are never sent together.
- Run:
  - `py -m pytest tests/unit/test_word_document_gateway.py -q`
- Expected first run before implementation:
  - failing assertions around old critical-field behavior.

### Task 2: Update Mapping Constants

- Change `APPLICATION_FORM_CRITICAL_FIELDS` in `application_form_word_mapping.py`.
- Remove line-item fields from the Application Form write-back payload/mapping path for this task.
- Run:
  - `py -m pytest tests/unit/test_word_document_gateway.py -q`
- Expected:
  - field-scope tests pass.

### Task 3: Add Header Paragraph Fake Tests

- In `tests/unit/test_application_form_word_gateway.py`, add fakes for:
  - existing value paragraph: label / `DL-OLD` / page -> `DL-NEW`
  - blank value paragraph: label / blank / page -> `DL-NEW`
  - missing value paragraph: label / page -> insert `DL-NEW` before page
  - unsafe header: missing page -> blocker
  - ambiguous middle paragraphs: label / `DL-OLD` / `extra text` / page -> blocker
- These tests should call the small helper used by `_replace_header_ltr_value` or verify behavior through `_replace_header_ltr_value` with fake COM paragraph objects.

### Task 4: Implement Header Paragraph Replacement

- Refactor `_replace_header_ltr_value` in `application_form_word_gateway.py`.
- Prefer helper functions small enough to keep file under 500 lines.
- Preserve current Word COM cleanup behavior.
- Do not modify unrelated COM content-control or form-field logic.

### Task 5: Verify Application Form Flow

- Run:
  - `py -m pytest tests/unit/test_application_form_word_gateway.py tests/unit/test_word_document_gateway.py tests/unit/test_project_application_form_write_back_service.py -q`
- Then run:
  - `py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q`
- Run:
  - `git diff --check`
- Optional manual smoke on a copied `.docx` in `tmp/`.

## Risks And Mitigations

- Risk: Word header templates differ.
  - Mitigation: blocker instead of destructive full-cell rewrite.
- Risk: line-item fields are useful but not safely writable yet.
  - Mitigation: exclude them from Application Form write-back and reserve row-level write-back for a future task.
- Risk: gateway file grows over 500 lines again.
  - Mitigation: keep helpers compact or split header-specific helpers if needed.

## Acceptance Checklist

- [ ] Critical field set matches the user-defined laboratory/header fields.
- [ ] Critical blank values block before Office write-back.
- [ ] `Lab Personnel Assigned` has one canonical source: `project_leader`, with `assigned_personnel` fallback only.
- [ ] Multi-row detail fields are not written to Application Form Word files.
- [ ] Header LTR replacement uses label/value/page paragraph structure.
- [ ] Existing `DL-...` header value is replaced.
- [ ] Multiple non-empty intermediate header paragraphs block.
- [ ] Unsafe header structure blocks.
- [ ] Tests pass.
- [ ] `docs/task_board.md` is updated only after implementation approval and completion.

## Stop Point

Stop after this plan/task file is created. Do not implement TASK_332C until explicitly approved.
