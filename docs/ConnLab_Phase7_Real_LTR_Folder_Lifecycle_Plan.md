# ConnLab Phase 7 Plan: Real LTR, Folder Evidence, And Lifecycle Governance

> Draft date: 2026-04-27
> Current board state: Phase 6A validated, no active implementation task.
> Plan status: proposed only. Do not implement until `docs/task_board.md` activates the first Phase 7 task.

---

## 1. Anti-Skip Statement

- Current phase: `Phase 6A - Outlook Email Package Intake, Application Form Selection And Human Confirmation`
- Current active task ID: `NONE_PHASE6A_VALIDATED`
- Why Phase 7 planning is allowed now: Phase 6A is validated and stopped; the user requested a detailed Phase 7 plan. This document is planning work only and does not start implementation.
- Why implementation is not allowed yet: `docs/task_board.md` has no active Phase 7 task.

---

## 2. Phase 7 Goal

Phase 7 should turn the current MVP workflow into a real lab intake-to-registration operating path grounded in real samples:

```text
Real email / direct DOCX intake
  -> real application form parser calibration
  -> human-confirmed project data
  -> LTR readiness check
  -> LTR number preview / registration using real Excel rules
  -> project folder evidence placement
  -> lifecycle state gating
  -> operator-facing exception handling
```

Phase 7 must not implement Matrix, test execution, report generation, report audit, AI review, permissions, LAN deployment, or Outlook inbox auto-scan. Report generation is a known high-value future phase, but Phase 7 should only preserve the structured data and evidence needed for that later work.

---

## 3. Real Inputs To Use

### 3.1 Outlook `.msg` samples

Folder:

```text
C:\Users\White\Desktop\AI information
```

Files:

- `Including two Lab Test Requirements and production specification.msg`
- `Lab Test Requirement in the attachment msg.msg`
- `Standard with Lab Test Requirement.msg`
- `Without Lab Test Requirement.msg`

Required Phase 7 usage:

- validate the Phase 6A intake path against all four samples;
- classify attachments as selected application form candidate, supporting specification, inline image, ignored, or missing application form;
- verify the rule that one email can create zero, one, or multiple intake cases;
- document expected operator action for each sample.

### 3.2 Real `.docx` application forms

Folder:

```text
C:\Users\White\Desktop\AI information
```

Files:

- `LTR by applicant.docx`
- `LTR modifed by Tester.docx`

Required Phase 7 usage:

- calibrate deterministic parser fields against real form layout;
- compare applicant-filled and tester-modified variants;
- ensure parser output remains draft data until human confirmation;
- expand parser tests with sanitized fixtures or minimal generated equivalents committed to `tests/fixtures`.

### 3.3 LTR Excel backup

File:

```text
D:\Source\Office Auto\TestDocument\LTR_number.xls
```

Required Phase 7 usage:

- treat as a local validation backup of the public drive workbook;
- inspect sheet layout, year sheet naming, header rows, DL column, and writable columns;
- build a gateway behind `backend/infrastructure/office/`, not direct Excel access from API/UI/application services;
- keep real workbook path configurable, never hard-coded.

### 3.4 LTR readiness fields

Source image:

```text
C:\Users\White\Desktop\AI information\申请 LTR 前必须字段.png
```

Fields extracted from the image:

1. DL
2. Project Type
3. Description P/N
4. Test Item
5. Applicable Specifications
6. Test Type
7. Requested by
8. Location
9. Project Leader
10. Test Result
11. Failed item
12. Sample deposition
13. Sub-contract
14. Test Fee
15. Remarks (PO)
16. Phone
17. E-mail of Requestor
18. Product Description
19. Lab Performing the Tests

Required Phase 7 usage:

- add an LTR readiness check before registration;
- map each field to either confirmed application form data, manual user input, default empty value requiring confirmation, or future non-MVP data;
- block Excel registration until required fields are confirmed.

---

## 4. Phase 7 Scope

### In Scope

- Real `.msg` sample compatibility matrix.
- Real `.docx` parser calibration.
- LTR number format validation:
  - standard format: `DL-{YYYY}-{MM}-{NNN}`, for example `DL-2026-04-001`;
  - W prefix: `W` plus letters/digits, for example `W123`;
  - suffix format: base DL plus suffix, for example `DL-2026-04-001ABC`;
  - monthly sequence starts from `001` and increments by existing workbook data.
- LTR readiness check and registration preview before writing.
- Excel LTR workbook gateway behind OfficeFacade / infrastructure boundary.
- Project folder evidence placement rules for email, application form, attachments, LTR evidence, and communication evidence.
- Lifecycle state model and operation gating through current MVP workflow.
- Exception workflows:
  - email has no application form;
  - one email has multiple application forms;
  - application form data is missing;
  - LTR number is added later or changed;
  - folder already exists and application form is later corrected.
- Quick lookup surfaces for sample information and testing condition/method.

### Out Of Scope

- Automatic Outlook inbox scan.
- Sending reply emails.
- Matrix planning.
- Test record execution.
- Test result ingestion.
- Report generation or report audit.
- AI review.
- Multi-user locking beyond local Excel file conflict detection.
- LAN deployment.
- Copying old TestFlowManager architecture.

---

## 5. Target Architecture

Phase 7 should preserve existing layering:

```text
backend/domain
  LtrNumber, LtrReadiness, ProjectLifecycleEvent, EvidenceAssetPlacement

backend/application
  ltr_readiness_service.py
  ltr_registration_workflow_service.py
  project_lifecycle_service.py
  evidence_placement_service.py
  lookup_service.py

backend/infrastructure/office
  excel_ltr_workbook_gateway.py
  ltr_workbook_snapshot.py

backend/modules/ltr
  ltr_number_rules.py
  ltr_excel_layout.py
  ltr_readiness_rules.py

backend/modules/folder
  evidence_placement_rules.py

backend/api
  thin routes that call application services only
```

Key boundary decisions:

- `modules/ltr` owns deterministic number parsing, validation, and next-number calculation.
- `infrastructure/office` owns Excel workbook read/write and Office lifecycle handling.
- `application` coordinates project, readiness, LTR record, file assets, folder evidence, and lifecycle state.
- API and frontend never directly open Excel, Word, Outlook, or project folders.

---

## 6. Lifecycle Model Proposed For Phase 7

Use explicit workflow stages instead of relying only on one broad project status:

| Stage | Meaning | Allowed Next Actions | Blocked Actions |
|---|---|---|---|
| `email_imported` | Email/direct form package is stored | select application form, classify attachments | LTR registration, folder generation |
| `application_form_selected` | One form candidate selected | parse draft, create/review intake case | LTR registration |
| `application_form_confirmed` | Human confirmed structured data | run precheck, check LTR readiness | Excel write if readiness fails |
| `precheck_completed` | Deterministic precheck recorded | resolve issues, continue to LTR readiness | final project close |
| `ltr_ready` | Required LTR fields confirmed | preview next LTR number, register LTR | folder generation if no LTR required by policy |
| `ltr_registered` | LTR record registered in ConnLab and external workbook if enabled | preview folder, generate folder | duplicate active LTR |
| `folder_generated` | Standard project folder exists and evidence is placed | project created/ready for testing | unsafe overwrite |
| `project_created` | Operational handoff point for test execution | record later manual testing/report status notes | changing intake data without evidence |
| `testing_in_progress` | Future/manual state only in Phase 7 | record lookup notes, preserve evidence | automated result ingestion/report generation |
| `closed` | Project completed or cancelled | read-only lookup, archive notes | LTR changes, folder mutation |

Implementation note:

- Phase 7 can either extend `ProjectStatus` carefully or introduce a separate `ProjectLifecycleRecord` history table. The safer path is a history table plus derived current workflow state, because existing `ProjectStatus` is already used by services.

---

## 7. Detailed Task Breakdown

### TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION

Goal:

- approve Phase 7 scope, add this plan to the board, and activate the first implementation task only.

Inputs:

- this plan document;
- `docs/task_board.md`;
- Phase 6A validation result.

Outputs:

- `docs/task_board.md` updated with Phase 7 section;
- first active task set to `TASK_037_REAL_SAMPLE_BASELINE`.

Acceptance:

- board states that Phase 7 does not include report generation or Matrix;
- no code implementation in this task.

### TASK_037_REAL_SAMPLE_BASELINE

Goal:

- build a documented compatibility baseline for the four real `.msg` samples and two `.docx` forms.

Inputs:

- real files in `C:\Users\White\Desktop\AI information`;
- existing Phase 6A intake services.

Outputs:

- `docs/phase7_real_sample_baseline.md`;
- non-sensitive fixture strategy;
- tests for sample classification using sanitized or generated fixtures.

Acceptance:

- each `.msg` sample has expected result:
  - no application form;
  - one application form;
  - multiple application forms;
  - application form plus specification;
- each `.docx` form has expected parser field coverage;
- real sample paths are documented but not hard-coded.

### TASK_038_REAL_DOCX_PARSER_CALIBRATION

Goal:

- improve deterministic `.docx` parser coverage for the real application form layout.

Inputs:

- `LTR by applicant.docx`;
- `LTR modifed by Tester.docx`;
- existing parser and precheck rules.

Outputs:

- parser support for real header/footer/table patterns;
- field alias map updates;
- regression tests.

Acceptance:

- form number/revision extracted when present;
- requestor, phone, date, email, business unit, project number extracted;
- sample and requested testing fields extracted or explicitly left as review-required;
- applicant and tester-modified samples produce comparable structured drafts;
- parser output remains draft-only before confirmation.

### TASK_039_LTR_NUMBER_RULES

Goal:

- isolate LTR number parsing, validation, formatting, and next monthly sequence calculation as pure deterministic rules.

Inputs:

- current `backend/application/ltr_service.py`;
- old TestFlowManager code as reference only;
- required formats from user.

Outputs:

- `backend/modules/ltr/ltr_number_rules.py`;
- unit tests for standard, W-prefix, suffix, invalid formats, and sequence generation.

Acceptance:

- `DL-2026-04-001` is valid base format;
- `W123` is valid W-prefix input;
- `DL-2026-04-001ABC` is valid suffix format;
- current month sequence increments from existing base DL values only;
- invalid values return actionable errors.

### TASK_040_LTR_WORKBOOK_SNAPSHOT_GATEWAY

Goal:

- read LTR workbook layout and existing numbers through an infrastructure gateway without writing.

Inputs:

- configurable workbook path;
- backup workbook `D:\Source\Office Auto\TestDocument\LTR_number.xls`.

Outputs:

- Excel gateway under `backend/infrastructure/office/`;
- workbook snapshot model with sheet name, row range, existing numbers, and file metadata;
- tests using generated workbook fixture where possible.

Acceptance:

- no API/UI/application service opens Excel directly;
- gateway can identify current year/month sheet strategy or report unsupported layout;
- gateway can list existing monthly numbers;
- file lock / missing file errors are explicit.

### TASK_041_LTR_READINESS_CHECK

Goal:

- verify all required LTR registration fields before any number is registered or workbook write is attempted.

Inputs:

- confirmed project/application form/sample data;
- 19 required fields from `申请 LTR 前必须字段.png`.

Outputs:

- readiness result with missing fields, source mapping, and required manual inputs;
- API endpoint for previewing readiness;
- frontend readiness panel if UI is included in task.

Acceptance:

- missing required fields block registration;
- each missing field shows where the operator should fill or confirm it;
- confirmed values are traceable to application form, project, manual override, or future field placeholder.

### TASK_042_LTR_REGISTRATION_PREVIEW

Goal:

- preview the next LTR number and target workbook row before writing.

Inputs:

- readiness check result;
- workbook snapshot;
- number rules.

Outputs:

- preview object:
  - proposed LTR number;
  - target sheet;
  - target row;
  - fields to write;
  - conflicts/warnings.

Acceptance:

- no write happens during preview;
- user can see proposed number before committing;
- conflict cases are actionable.

### TASK_043_LTR_EXCEL_WRITE_AND_LOCAL_RECORD_SYNC

Goal:

- commit an approved LTR registration to both external Excel workbook and ConnLab SQLite record.

Inputs:

- approved preview;
- confirmed readiness data.

Outputs:

- Excel write gateway;
- application workflow service;
- synchronized `LtrRecord`;
- audit/evidence note.

Acceptance:

- Excel is opened, written, saved, and released through infrastructure gateway;
- ConnLab record is only marked registered after successful write or explicitly configured local-only mode;
- duplicate active LTR is blocked;
- workbook write failures do not create a misleading registered state.

### TASK_044_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN

Goal:

- support safe correction when LTR number is added later or changed.

Inputs:

- existing LTR record;
- folder record;
- project assets.

Outputs:

- rename preview for project folder and related file names;
- evidence preservation plan;
- no-overwrite conflict handling.

Acceptance:

- renumbering requires preview and explicit confirmation;
- folder/file rename conflicts block execution;
- old number, new number, reason, and related email evidence are recorded.

### TASK_045_FOLDER_EVIDENCE_PLACEMENT_RULES

Goal:

- define and implement where email, application forms, attachments, specifications, and communication evidence go in the project folder.

Inputs:

- current `docs/06_FOLDER_TEMPLATE.md`;
- user folder rule requirements;
- Phase 6A file assets.

Outputs:

- evidence placement policy;
- folder generation/copy updates if needed;
- tests with temporary directories.

Recommended placement:

```text
{DL_NUMBER} {PROJECT_NO}/
  00_Request/
    original_email/
    application_form/
    attachments/
    communication_evidence/
  01_LTR/
  02_Specifications/
    product_spec/
    standards/
    customer_requirements/
```

Acceptance:

- original `.msg` is preserved;
- selected application form is copied separately from supporting attachments;
- specifications can be classified and placed under `02_Specifications`;
- later corrected forms do not delete the original evidence.

### TASK_046_PROJECT_LIFECYCLE_GATING

Goal:

- prevent operations that are invalid for the current project lifecycle stage.

Inputs:

- Phase 7 lifecycle table;
- existing project, intake, precheck, LTR, and folder states.

Outputs:

- lifecycle policy service;
- route-level guard integration through application services;
- frontend disabled/reason states if UI is included.

Acceptance:

- cannot register LTR before application form confirmation and readiness pass;
- cannot generate folder unsafely before LTR/folder prerequisites;
- cannot mutate closed projects;
- blocked actions return business-readable reasons.

### TASK_047_EXCEPTION_WORKFLOWS

Goal:

- make real failure cases explicit and traceable.

Inputs:

- user-provided exception cases.

Outputs:

- exception state/reason records;
- operator action guidance in API/UI;
- evidence attachment for corrections.

Acceptance:

- no application form in email creates a package needing follow-up, not a project;
- one email with multiple application forms creates separate cases/projects;
- missing application form info blocks downstream steps until confirmed;
- corrected application forms preserve original and communication evidence;
- LTR changes require reason and preview.

### TASK_048_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS

Goal:

- provide fast lookup for data operators often need to check.

Inputs:

- confirmed sample info;
- requested testing description;
- applicable specifications;
- test type/test item fields.

Outputs:

- backend lookup service/API;
- frontend compact lookup panel if UI is in task.

Acceptance:

- sample info is searchable by project, DL, part number, product name, requestor;
- testing conditions/method text is visible without opening Word;
- no Matrix/test execution/report generation is implemented.

### TASK_049_PHASE7_VALIDATION_AND_DOCS_SYNC

Goal:

- close Phase 7 with validation and board sync.

Outputs:

- updated `docs/task_board.md`;
- validation summary;
- manual smoke checklist for real sample flow;
- known limitations.

Acceptance:

- relevant backend tests pass;
- frontend build passes if UI changed;
- real sample manual validation matrix is updated;
- next phase recommendation is documented.

---

## 8. Suggested Phase 7 Acceptance Gate

Phase 7 is done only when:

- all real `.msg` and `.docx` samples have documented expected behavior;
- parser handles real `.docx` forms well enough to create reviewable drafts;
- LTR readiness check blocks incomplete registration;
- LTR number rules are deterministic and tested;
- workbook preview is available before write;
- external workbook write, if enabled, is behind infrastructure gateway and safely releases Excel;
- project folder evidence placement preserves original email, selected application form, attachments, and correction evidence;
- lifecycle guards prevent invalid next actions;
- sample info and testing condition/method lookup is available;
- no Matrix, report generation, AI review, or future-scope feature slipped into Phase 7.

---

## 9. Risks And Controls

| Risk | Control |
|---|---|
| Real `.msg` / `.docx` files may contain sensitive information | Do not commit originals; create sanitized fixtures or synthetic regression fixtures |
| Excel workbook may be locked on public drive | Gateway must detect lock and return actionable error |
| Workbook layout may differ by year/sheet | Snapshot task must document sheet and column layout before write task |
| LTR registration could create mismatched SQLite/Excel state | Commit workflow must write Excel and local record as a coordinated operation with failure handling |
| LTR renumbering can break folder/file names | Always preview rename; never overwrite; preserve old evidence |
| Lifecycle model could overtake current MVP | Add guards around current workflow only; keep future states as manual/placeholder if needed |
| Report pain point may pull scope forward | Preserve report-ready structured data, but keep automated report generation out of Phase 7 |

---

## 10. Recommended Next Step

If this plan is approved, update `docs/task_board.md` to add Phase 7 and activate only:

```text
TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION
```

After that task completes, activate:

```text
TASK_037_REAL_SAMPLE_BASELINE
```

Do not start implementation tasks before the board is updated.
