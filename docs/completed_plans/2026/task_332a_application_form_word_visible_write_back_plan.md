# TASK_332A Application Form Word Visible Write-Back Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task ID

`TASK_332A_APPLICATION_FORM_WORD_VISIBLE_WRITE_BACK`

## Why This Task Is Allowed Now

This is a smoke-test follow-up to completed `TASK_332_OFFICIAL_OUTPUT_HEADERS_CONSUME_BASIC_INFORMATION`. Manual testing proved that Application Form Word write-back can modify the file timestamp without visibly changing the document. The task is limited to fixing that formal output defect.

## Step 1 - Task Understanding

### Goal

Make the copied selected Application Form Word document in `Submitted Material` visibly receive Project Basic Information / project identity values during Project Folder output write-back.

### Input Data

- The selected Application Form copied from the New Project email attachment flow into `Submitted Material`.
- Latest confirmed Project Basic Information values already consumed by TASK_332.
- Project/LTR identity already available to the write-back service.

### Output Data

- The same copied `.docx` file, visibly updated in Word.
- Write result metadata listing changed, unchanged, warning, or blocked fields.

### Modules

- Application orchestration:
  - `backend/application/project_application_form_write_back_service.py`
- Office boundary:
  - `backend/infrastructure/office/office_facade.py`
  - `backend/infrastructure/office/word_document_gateway.py`
  - `backend/infrastructure/office/models.py`
- Tests:
  - `tests/unit/test_word_document_gateway.py`
  - `tests/unit/test_project_application_form_write_back_service.py`
  - existing Required Forms tests if write-back result behavior changes

### Not Allowed

- No UI work.
- No LTR workbook sync.
- No Report generation.
- No Basic Information schema/API changes.
- No direct reuse/import of old TestFlowManager code.
- No automated dependency on user desktop/sample files.

## Step 2 - Design

### Core Design

The implementation should use a hybrid Word gateway:

1. `WordDocumentGateway.write_application_form_fields()` remains the public infrastructure method.
2. The gateway first uses a Word COM writer for real Application Form documents because visible updates may live in Word header tables, content controls, and legacy form fields.
3. If COM is unavailable:
   - plain-table documents may fall back to the existing `python-docx` writer;
   - documents containing content controls/form fields/header LTR targets must fail the formal Application Form write-back step with an actionable Office automation message. This must surface as a blocked/failed Project Folder output step, not as a warning while the overall output is reported successful.
4. The application service stays unaware of COM. It only calls the Office facade and consumes typed result metadata.

### Why Not Pure `python-docx`

`python-docx` is useful for simple `.docx` table text. It is not reliable for the current request form because the target file contains:

- header content that users see in Word;
- Word content controls (`w:sdt`);
- legacy form fields (`w:ffData`);
- dropdown-like fields where the visible value must be selected through Word, not only text-replaced in XML.

If a future template is plain text only, the fallback can still use `python-docx`. For this task’s real Application Form, Word COM is the safer implementation boundary.

### Field Mapping

Add a focused Application Form mapping table:

| Basic Information / identity key | Word label aliases | Target rule |
| --- | --- | --- |
| `ltr_number` | `Lab Test Request Number`, `LTR Number`, `DL Number` | header visible value |
| `project_type` | `Project Type` | next row, same column |
| `test_type` | `Test Type` | next row, same column |
| `test_sample_status` | `Test Sample Status` | next row, same column |
| `requested_by` / `requester` | `Requested By:`, `Requestor:` | same row, next cell |
| `phone` | `Phone #:` | same row, next cell |
| `email` | `Email:`, `E-mail of Requestor` | same row, next cell |
| `business_unit` | `Business Unit:` | same row, next cell |
| `project_number` | `Project #:` | same row, next cell |
| `location` / `manufacturing_site` | `Mfg. Site:`, `Manufacturing Site:`, `Site:` | same row, next cell |
| `sub_contract` | `Can testing be subcontracted?`, `Sub-contract` | same row, next cell |
| `test_item` | `Tests to be Performed`, `Test Item` | next row, same column |
| `applicable_specifications` | `Applicable Specifications` | next row, same column |
| `lab` | `Lab Performing the Tests:` | same row, next cell |
| `project_leader` / `assigned_personnel` | `Lab Personnel Assigned:`, `Assigned Personnel` | same row, next cell |
| `received_date` | `Date Lab Received Samples:` | same row, next cell |
| `estimated_completion_date` | `Estimated Completion Date:` | same row, next cell |
| `sample_condition` | `Condition of Samples when Received:` | same row, next cell |

### Payload Source Alignment

Application Form write-back consumes the same modeled formal-output payload prepared from the latest confirmed Project Basic Information snapshot in TASK_332. It must not remap an already-mapped identity payload a second time.

Required alignment checks:

- `location` must reach the gateway for `Mfg. Site` / site write-back.
- `project_leader` or `assigned_personnel` must reach the gateway for `Lab Personnel Assigned`.
- `test_item` must reach the gateway for `Tests to be Performed`.
- `applicable_specifications` must reach the gateway for `Applicable Specifications`.
- `requested_by`, `phone`, `email`, `business_unit`, and `project_number` must reach the gateway as source values, even when some values are empty.

### Word Cell Write Rules

When a target cell is found:

1. If it contains a content control:
   - write visible text into plain/rich/date controls;
   - select matching dropdown entry for dropdown controls;
   - return a warning/blocker if dropdown value is not an allowed option.
2. Else if it contains a legacy text form field:
   - set the form field result.
3. Else:
   - write normal cell text.

### Content Control Strategy

Use Word COM content-control type handling explicitly:

| Control category | COM behavior | Missing/unsupported value behavior |
| --- | --- | --- |
| Plain text / rich text | Write `Range.Text` and verify visible value | blocker for critical fields, warning for non-critical fields |
| Date | Write display text through the control and verify visible value | blocker for critical fields, warning for non-critical fields |
| Combo box | Prefer matching dropdown entry; otherwise write text only if Word accepts and verification passes | blocker for critical fields, warning for non-critical fields |
| Dropdown list | Select matching entry only | blocker if no matching entry for critical fields; warning for non-critical fields |
| Checkbox | Only set when source value can be normalized to boolean | blocker for critical checkbox fields; warning otherwise |
| Locked control | Do not bypass lock | blocker for critical fields, warning for non-critical fields |
| Unknown control type | Do not claim success without verification | blocker for critical fields, warning for non-critical fields |

### Verification Read

COM write-back must perform visible-value verification. This is mandatory, not best-effort:

- After each attempted critical field write, read the visible value back through Word COM before reporting the field changed or unchanged.
- Header LTR verification is mandatory.
- At minimum, verification must cover these critical fields when values are provided: `ltr_number`, `requested_by`, `location` / `manufacturing_site`, `test_item`, `applicable_specifications`, and `lab`.
- If a critical field cannot be found, cannot be written, or read-back does not match the requested visible value, the write-back result is blocked/failed rather than successful with warning.
- Non-critical field failures may be warnings if the document is otherwise updated and verified.
- The result must distinguish:
  - changed;
  - unchanged because the visible value already matched;
  - warning because field was not found;
  - blocked because a Word control could not accept the value.

The task is not accepted if tests or smoke verification only prove that the file modification timestamp changed.

## Step 3 - Implementation Tasks

### Task 1: Add Application Form Mapping and Target Rules

**Files**

- Modify: `backend/infrastructure/office/word_document_gateway.py`
- Test: `tests/unit/test_word_document_gateway.py`

**Steps**

1. Add `APPLICATION_FORM_FIELD_LABELS` aliases for the fields listed above.
2. Add `APPLICATION_FORM_NEXT_ROW_FIELDS`.
3. Add pure helper functions for label normalization and target-rule selection.
4. Add tests for:
   - `Project Type` resolves as next-row;
   - `Requested By:` resolves as same-row next-cell;
   - `Mfg. Site:` resolves from `location`;
   - `Tests to be Performed` resolves from `test_item`.

**Validation**

Run:

```powershell
py -m pytest tests/unit/test_word_document_gateway.py -q
```

### Task 2: Add COM-Based Application Form Writer

**Files**

- Modify: `backend/infrastructure/office/word_document_gateway.py`
- Test: `tests/unit/test_word_document_gateway.py`

**Steps**

1. Add `_write_application_form_fields_with_com(path, fields)`.
2. Open Word through `pythoncom` and `win32com.client.DispatchEx("Word.Application")`.
3. Set Word invisible and alerts off.
4. Update header LTR through a focused helper.
5. Locate body target cells by table label scanning.
6. Write target cells through content-control/form-field/plain-cell helpers.
7. Read back and verify critical visible values before returning `changed`.
8. Save only when at least one visible field changes and critical verification passed.
9. Always close document, quit Word, and uninitialize COM.

**Validation**

Run:

```powershell
py -m pytest tests/unit/test_word_document_gateway.py -q
```

### Task 3: Preserve Safe Fallback and Failure Semantics

**Files**

- Modify: `backend/infrastructure/office/word_document_gateway.py`
- Test: `tests/unit/test_word_document_gateway.py`

**Steps**

1. Keep existing `python-docx` fallback for plain test documents.
2. Detect likely Word form documents by checking the `.docx` XML package for `w:sdt` or `w:ffData`.
3. If the document is a Word form and COM is unavailable, return/raise an actionable Office automation failure instead of returning false success.
4. Map formal Project Folder Application Form write-back COM-unavailable failures to a blocked/failed step result.
5. Ensure warnings for non-critical missing fields are visible in `WordSection2WriteResult`.
6. Ensure critical field failures are not downgraded to warnings.

**Validation**

Run:

```powershell
py -m pytest tests/unit/test_word_document_gateway.py -q
```

### Task 4: Confirm Application Service Propagation

**Files**

- Modify if needed: `backend/application/project_application_form_write_back_service.py`
- Test: `tests/unit/test_project_application_form_write_back_service.py`

**Steps**

1. Confirm the service targets the selected request material path copied to `Submitted Material`.
2. Confirm write warnings/blockers are surfaced in step results.
3. Do not add source fallback for modeled Basic Information fields.
4. Add tests that prove `location`, `project_leader`, `test_item`, and `applicable_specifications` are included in the payload passed to the Word gateway.
5. Add tests that prove critical gateway failures block/fail the Application Form write-back step.

**Validation**

Run:

```powershell
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
```

### Task 5: Manual Smoke on a Copied Real Document

**Files**

- Optional helper or documented procedure only.
- Do not write to the original user-provided sample.

**Steps**

1. Copy the real sample `.docx` into `tmp/task_332a/`.
2. Run the gateway write-back against the copy with known Basic Information values.
3. Reopen/read through Word COM or manual Word inspection.
4. Verify visible values, including header LTR and table fields.
5. Close the reopened Word document without performing extra manual save, then reopen/read again to confirm values persist.

**Validation**

Expected output:

- header LTR visible value changed;
- `Requested By`, `Phone #`, `Email`, `Mfg. Site`, `Tests to be Performed`, and lab fields visibly populated;
- result metadata reports changed/unchanged/warnings accurately.
- closing and reopening the copied document does not require an extra manual save to preserve the values.

## Step 4 - Review Checklist

- Architecture:
  - Office automation remains inside `backend/infrastructure/office`.
  - Application service does not import COM or inspect Word internals.
- Scope:
  - No UI, no Report, no LTR sync behavior changes.
  - No Basic Information schema/API changes.
- Quality:
  - COM resources are always released.
  - No hardcoded user paths.
  - Tests use fixtures/fakes or temp copies only.
- Behavior:
  - Timestamp-only modification is not treated as success.
  - Header LTR and critical fields are verified by visible-value read-back.
  - Missing or locked critical Word targets block/fail the write-back step.
  - Missing or locked non-critical Word targets produce actionable warnings.

## Step 5 - Recommended Verification Commands

```powershell
py -m pytest tests/unit/test_word_document_gateway.py -q
py -m pytest tests/unit/test_project_application_form_write_back_service.py -q
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
git diff --check
```

## Stop Point

This plan is ready for review. Do not implement TASK_332A until the user explicitly approves execution.
