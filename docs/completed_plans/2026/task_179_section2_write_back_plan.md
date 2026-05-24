# TASK_179 Section 2 Write Back Plan

> Status: proposed for review
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 1. Goal

Add controlled `.docx` Section 2 write-back for the original application form.

The implementation must be safe enough for real lab evidence files:

- preview values come from TASK_177 logic;
- backup always happens before mutation;
- only known Section 2 fields are written;
- all Word file operations stay inside infrastructure.

---

## 2. Design

### Infrastructure

Extend `WordDocumentGateway` with a narrow Section 2 write method, for example:

```text
write_section2_fields(source_path, fields) -> WordSection2WriteResult
```

The gateway should:

- open `.docx` with python-docx;
- locate known Section 2 label/value cells by deterministic labels;
- update only matching value cells;
- save the document;
- return old/new values and locations.

Do not put business test-plan logic in the gateway.

### Office Facade

Expose the gateway through `OfficeFacade`, for example:

```text
write_word_section2_fields(source_path, fields)
```

### Application

Add `Section2WriteBackService`.

Responsibilities:

- verify Project and draft through existing repositories;
- compute preview values by using `Section2CompletionPreviewService`;
- validate target path and `.docx` extension;
- create backup file before write;
- call `OfficeFacade.write_word_section2_fields`;
- return write-back result.

### API

Add:

```text
POST /api/projects/{project_id}/test-plan/drafts/{draft_id}/section2-write-back
```

The route stays typed and thin.

---

## 3. Field Mapping

Initial deterministic labels:

```text
lab -> Lab / Laboratory
assigned_personnel -> Assigned Personnel / Assigned Engineer / Test Engineer
received_date -> Received Date / Sample Received Date
estimated_completion_date -> Estimated Completion Date / Estimated Complete Date
sample_condition -> Sample Condition / Sample Received Condition
```

If labels are absent, the gateway should fail before save. Do not guess arbitrary table cells.

The test demand summary field should be included only if a clear Section 2 target label exists in the real/template document. If no stable label is confirmed, it should remain out of first implementation.

---

## 4. Files

Expected implementation files:

- `backend/infrastructure/office/models.py`
- `backend/infrastructure/office/word_document_gateway.py`
- `backend/infrastructure/office/office_facade.py`
- `backend/application/section2_write_back_service.py`
- `backend/api/routes_section2_write_back.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_word_document_section2_write_gateway.py`
- `tests/unit/test_section2_write_back_service.py`
- `tests/integration/test_section2_write_back_api.py`

---

## 5. Risks

- Real E-3718 forms may use merged cells, content controls, or label variations.
- python-docx may not preserve all advanced Word features perfectly.
- Writing to the preserved original file is operationally sensitive; backup and audit are mandatory.
- `.doc` write-back is not supported in this task.

---

## 6. Validation

Targeted:

```powershell
py -m pytest tests\unit\test_section2_write_back_service.py tests\unit\test_word_document_section2_write_gateway.py tests\integration\test_section2_write_back_api.py -q
```

Regression:

```powershell
py -m pytest tests\unit\test_section2_completion_preview_service.py tests\integration\test_section2_completion_preview_api.py -q
```

Task board guards:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 7. Approval Gate

This plan is only the executable design. Implementation starts only after explicit approval, for example:

```text
批准执行 TASK_179
```
