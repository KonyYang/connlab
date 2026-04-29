# ConnLab Phase 7 Plan: Real LTR, Folder Evidence, And Lifecycle Governance

> Optimized date: 2026-04-27
> Current board state: Phase 7 complete; current active task is `NONE_PENDING_USER_APPROVAL`.
> Plan status: approved Phase 7 execution plan. `docs/task_board.md` remains the source of truth for the active task.
> Replacement target: `docs/ConnLab_Phase7_Real_LTR_Folder_Lifecycle_Plan.md`

---

## 0. Executive Reading

Phase 7 is the first phase that should prove ConnLab can handle the real laboratory intake-to-registration path instead of only the MVP happy path.

The original Phase 7 direction is correct:

```text
real .msg / direct .docx intake
  -> real application form parser calibration
  -> human-confirmed project data
  -> LTR readiness
  -> LTR preview
  -> optional real workbook write
  -> project folder evidence placement
  -> lifecycle operation gates
```

The optimized version makes the plan safer in four ways:

1. **Separate evidence, readiness, preview, and write.** Excel write must not be reached until real sample baseline, LTR field mapping, pure number rules, workbook snapshot, and readiness preview are all stable.
2. **Do not replace the existing `ProjectStatus` too early.** Add lifecycle events / operation guards around the current project statuses instead of creating a large status enum that may break existing services.
3. **Treat the real `.xls` workbook as an external integration.** `.xls` is not the same as `.xlsx`; the gateway must first inspect layout and choose an adapter behind `backend/infrastructure/office/`. API, frontend, and application services must never open Excel directly.
4. **Make server-upgrade readiness explicit.** Local Office automation is allowed only as a local gateway/agent capability. Future server processes must not depend on Office COM.

---

## 1. Anti-Skip Statement

- Current phase: `Phase 7 - Real LTR, Folder Evidence, And Lifecycle Governance`
- Current active task ID: `NONE_PENDING_USER_APPROVAL`
- Why no implementation task is allowed now: `TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC` is complete and `docs/task_board.md` is waiting for explicit next-phase approval.
- Why later implementation is not allowed yet: `docs/task_board.md` has not activated Phase 8 or any later task.
- Current permitted implementation step: none until the task board is explicitly updated.

Stop rule:

```text
If docs/task_board.md does not name a Phase 7 active task, do not code Phase 7.
If an implementation request jumps ahead of the active task, stop and report the mismatch.
```

---

## 2. Starting Point From Current Repository

### 2.1 What Phase 6A already established

Phase 6A validated the offline intake foundation:

- Office gateway boundary for Word, Excel placeholder, and Outlook `.msg`.
- `.msg` source preservation, metadata extraction, attachment extraction, and real sample compatibility checks.
- Controlled intake storage under `data/intake/{package_id}`.
- SQLite persistence for:
  - `IntakePackage`
  - `IntakeAsset`
  - `IntakeCase`
  - `IntakeDraft`
- Deterministic application form candidate detection from file metadata.
- Human-selected form asset to case/draft creation.
- Backend service for confirming an intake draft into:
  - `Project`
  - `ApplicationForm`
  - `SampleInfo`
  - `FileAsset`
- Direct Word intake into the same intake review flow.
- Attachment-aware deterministic precheck context.

### 2.2 Known Phase 6A limits that Phase 7 must respect

The Phase 6A validation summary lists important limits:

- Word content parsing is still not fully implemented for real forms.
- Frontend intake pages may still use preview/static data until endpoints are fully wired.
- Confirm-project backend exists, but frontend confirmation may not be fully wired.
- Outlook inbox auto-scan, email sending, Matrix, Report, AI review, LAN deployment, and permissions remain out of scope.

Phase 7 must therefore begin with **real sample baseline and parser calibration**, not Excel write.

### 2.3 Current LTR and folder state

Existing MVP services are intentionally minimal:

- `LtrService.register_ltr()` accepts a manually supplied `ltr_number`.
- It blocks duplicate active registered LTR records for one project.
- It updates project status to `ProjectStatus.LTR_REGISTERED`.
- `FolderService.preview_folder()` and `generate_folder()` are previewable and safe against overwrite.
- `FolderService.generate_folder()` currently copies the latest application form asset only.

Phase 7 must turn this into a controlled workflow:

```text
confirmed project
  -> precheck / data review
  -> readiness check
  -> LTR number preview
  -> approved commit
  -> evidence placement
  -> folder generation
```

---

## 3. Phase 7 Goal

Phase 7 should turn the current MVP into a real lab intake-to-registration operating path grounded in real samples:

```text
Real email / direct DOCX intake
  -> real application form parser calibration
  -> human-confirmed project data
  -> LTR readiness check
  -> LTR number preview / registration using real workbook rules
  -> project folder evidence placement
  -> lifecycle state gating
  -> operator-facing exception handling
```

Phase 7 must preserve the data and evidence needed for future Matrix, Test Record, Report, and AI review, but must not implement those future features.

---

## 4. Scope Boundaries

### 4.1 In scope

- Real `.msg` sample compatibility matrix.
- Real `.docx` application form parser calibration.
- LTR field catalog and readiness source mapping.
- LTR number parsing, validation, formatting, and next-number calculation.
- Read-only LTR workbook snapshot gateway.
- LTR registration preview before any write.
- Optional workbook write behind explicit feature flag and infrastructure gateway.
- Local ConnLab LTR record synchronization.
- Project folder evidence placement policy and implementation.
- Lifecycle operation guards.
- Exception workflows:
  - email has no application form;
  - one email has multiple application forms;
  - application form data is missing;
  - LTR number is added later or changed;
  - folder already exists and application form is later corrected.
- Quick lookup surfaces for sample information and testing condition/method.

### 4.2 Out of scope

- Automatic Outlook inbox scan.
- Reading the currently selected Outlook item.
- Sending or replying to emails.
- Matrix planning.
- Test record execution.
- Test result ingestion.
- Report generation.
- Report audit.
- AI review.
- User permissions / roles.
- LAN deployment or multi-user collaboration.
- Server deployment.
- Copying old TestFlowManager architecture.
- Direct Office/Excel/Word/Outlook access from frontend, API routes, or application services.

---

## 5. Real Inputs To Use

### 5.1 Outlook `.msg` samples

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
- classify attachments as:
  - selected application form candidate;
  - supporting specification;
  - inline image;
  - ignored;
  - missing application form;
- verify that one email can create zero, one, or multiple intake cases;
- document expected operator action for each sample.

Do not commit original `.msg` files to Git.

### 5.2 Real `.docx` application forms

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
- keep parser output as draft data until human confirmation;
- create sanitized fixtures or minimal generated equivalents under `tests/fixtures`.

Do not commit original `.docx` files to Git unless explicitly sanitized.

### 5.3 LTR Excel backup

File:

```text
D:\Source\Office Auto\TestDocument\LTR_number.xls
```

Required Phase 7 usage:

- treat this as a local validation backup, not the public drive source of truth;
- inspect workbook type, sheet layout, year/month sheet naming, header rows, DL column, and writable columns;
- build access behind `backend/infrastructure/office/`;
- keep workbook path configurable;
- never hard-code this path in service, API, frontend, or tests.

Important `.xls` note:

```text
LTR_number.xls is an old binary Excel format.
Do not assume openpyxl can read/write it.
Phase 7 must first inspect and document the workbook format, then choose the adapter.
If COM automation is required, keep it behind OfficeLifecycleManager / Excel gateway only.
```

### 5.4 LTR readiness source image

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

Optimized interpretation:

```text
These are workbook/readiness fields that must have a write policy before registration.
Not every field is necessarily a blocking business requirement at the same severity.
Some future-result fields may use an intentional placeholder such as "Pending", "N/A", or blank-by-policy.
```

---

## 6. Key Architecture Decisions

### 6.1 Keep existing layering

```text
Frontend -> API -> Application Services -> Domain + Ports -> Infrastructure
```

Allowed:

- `api -> application`
- `application -> domain`
- `application -> ports/interfaces`
- `infrastructure -> domain/application ports`

Forbidden:

- frontend -> Office / SQLite / project folders directly
- API route -> Excel / Word / Outlook directly
- domain -> infrastructure
- application service -> raw COM / direct workbook manipulation

### 6.2 Recommended Phase 7 module layout

```text
backend/domain/
  models.py                         # add small value records only
  enums.py                          # add minimal enums only if necessary

backend/application/
  ltr_readiness_service.py
  ltr_registration_workflow_service.py
  project_lifecycle_service.py
  evidence_placement_service.py
  lookup_service.py

backend/infrastructure/office/
  excel_ltr_workbook_gateway.py
  ltr_workbook_snapshot.py
  ltr_workbook_adapters.py          # optional if adapter split is needed

backend/modules/ltr/
  ltr_number_rules.py
  ltr_excel_layout.py
  ltr_readiness_rules.py
  ltr_field_catalog.py

backend/modules/folder/
  evidence_placement_rules.py

backend/api/
  routes_ltr_readiness.py           # or extend routes_ltr.py while still thin
  routes_evidence.py                # only if evidence has separate endpoints
  routes_lookup.py                  # only if lookup UI/API is included
```

### 6.3 What each layer owns

| Layer | Owns | Must not own |
|---|---|---|
| `modules/ltr` | Pure parsing, validation, formatting, next-number calculation, field catalog, readiness rules | SQLite, Excel COM, API DTOs |
| `infrastructure/office` | Workbook read/write adapters, file metadata, Office lifecycle | Business decisions, project status |
| `application` | Orchestration across project, readiness, LTR record, workbook gateway port, evidence, lifecycle | Raw Excel/Word/Outlook operations |
| `api` | Pydantic DTOs, HTTP errors, thin service calls | Business rules, Excel operations |
| `frontend` | Operator workflow display and confirmations | Workbook path rules, filesystem mutation |

### 6.4 OfficeFacade and future server readiness

For the current offline Windows version:

```text
OfficeFacade / infrastructure gateways may use:
  - file-level parsers where possible;
  - pywin32 COM only behind infrastructure gateways;
  - explicit lifecycle/cleanup handling.
```

For future server/network versions:

```text
Server processes must not use Office COM.
Server-compatible options must be:
  - pure file parsers;
  - document conversion service;
  - local Windows worker/agent that owns Office automation;
  - external document-processing service.
```

Therefore Phase 7 services should depend on ports such as:

```text
LtrWorkbookGatewayPort
EvidenceStoragePort
ProjectLifecycleRepositoryPort
```

not on Office COM or local paths directly.

### 6.5 Excel write must be feature-gated

Add settings before real write:

```text
CONNLAB_LTR_WORKBOOK_PATH=
CONNLAB_LTR_WORKBOOK_MODE=local_only|excel_readonly|excel_write
CONNLAB_LTR_WORKBOOK_WRITE_ENABLED=false
CONNLAB_LTR_WORKBOOK_BACKUP_DIR=
CONNLAB_LTR_WORKBOOK_PASSWORD=
```

Required behavior:

| Mode | Behavior |
|---|---|
| `local_only` | ConnLab stores LTR record locally; no external workbook read/write |
| `excel_readonly` | ConnLab can snapshot workbook and preview target row; no write |
| `excel_write` | ConnLab may write only after readiness pass, preview approval, backup policy, workbook password handling, and feature flag |

Default should be:

```text
CONNLAB_LTR_WORKBOOK_MODE=local_only
CONNLAB_LTR_WORKBOOK_WRITE_ENABLED=false
```

Workbook password policy:

- the LTR workbook may be password-protected to prevent simultaneous manual operation;
- default deployment configuration may use `DGLAB`, but code and tests must not hard-code that value;
- password must be supplied through settings, a secret store, or an explicit gateway call parameter;
- password changes must not require code changes;
- when applying for a new LTR number through a later workbook adapter/write task, the infrastructure gateway should automatically open the workbook with the configured password;
- missing or wrong password must return an actionable error and must not create a local registered state.

### 6.6 Evidence is immutable by default

Original evidence must be preserved:

```text
original email
original selected application form
supporting specifications
communication evidence
corrected forms
LTR preview/commit note
folder placement note
```

Correction should append new evidence and record reason. It should not delete or silently overwrite old evidence.

---

## 7. LTR Field Catalog And Readiness Policy

### 7.1 Readiness severity

Use three severities instead of a single required/missing flag:

| Severity | Meaning | Registration behavior |
|---|---|---|
| `BLOCKER` | Field must have a confirmed value before registration | Block |
| `REVIEW_REQUIRED` | Field can be missing only if operator explicitly confirms a policy | Block until confirmed |
| `PLACEHOLDER_ALLOWED` | Field is not knowable at registration time; use defined placeholder policy | Do not block if placeholder policy is explicit |

### 7.2 Initial field mapping

| # | LTR field | Primary source | Fallback / policy | Initial severity |
|---:|---|---|---|---|
| 1 | DL | proposed LTR number / `LtrRecord.ltr_number` | generated by preview before commit | `BLOCKER` |
| 2 | Project Type | `ApplicationForm.project_type` | manual confirmation | `BLOCKER` |
| 3 | Description P/N | `SampleInfo.part_number`, `SampleInfo.product_name` | manual confirmation | `BLOCKER` |
| 4 | Test Item | requested testing text / extracted test item | manual confirmation | `BLOCKER` |
| 5 | Applicable Specifications | specification attachments / requested testing text | manual confirmation or selected supporting document | `BLOCKER` |
| 6 | Test Type | `ApplicationForm.test_type` | manual confirmation | `BLOCKER` |
| 7 | Requested by | `ApplicationForm.requester` | email sender / manual confirmation | `BLOCKER` |
| 8 | Location | manufacturing site / lab location | manual confirmation | `REVIEW_REQUIRED` |
| 9 | Project Leader | lab assigned personnel / operator input | manual confirmation | `REVIEW_REQUIRED` |
| 10 | Test Result | future result data | placeholder policy: `Pending` / blank-by-policy | `PLACEHOLDER_ALLOWED` |
| 11 | Failed item | future result data | placeholder policy: `N/A` / blank-by-policy | `PLACEHOLDER_ALLOWED` |
| 12 | Sample deposition | post-testing disposition / sample disposition | manual confirmation | `REVIEW_REQUIRED` |
| 13 | Sub-contract | subcontract allowed / subcontract text | manual confirmation | `BLOCKER` |
| 14 | Test Fee | future cost sheet / manual fee | manual confirmation or placeholder policy | `REVIEW_REQUIRED` |
| 15 | Remarks (PO) | additional information / PO note | optional manual note | `REVIEW_REQUIRED` |
| 16 | Phone | `ApplicationForm.phone` | manual confirmation | `BLOCKER` |
| 17 | E-mail of Requestor | `ApplicationForm.email` | sender email / manual confirmation | `BLOCKER` |
| 18 | Product Description | `Project.product_name` / `SampleInfo.product_name` | manual confirmation | `BLOCKER` |
| 19 | Lab Performing the Tests | `ApplicationForm.lab` | default lab policy or manual confirmation | `BLOCKER` |

### 7.3 Readiness output shape

The readiness service should return a business-readable object:

```json
{
  "project_id": "string",
  "status": "blocked|review_required|ready",
  "fields": [
    {
      "field_key": "requested_by",
      "label": "Requested by",
      "value": "Alice",
      "source": "application_form.requester",
      "severity": "BLOCKER",
      "state": "confirmed|missing|placeholder|needs_review",
      "operator_action": "Confirm requestor name before LTR registration."
    }
  ],
  "blockers": [],
  "warnings": []
}
```

Note:

- `DL` is generated during preview and should remain `pending_preview` before a candidate number exists.
- The mailed application form is not expected to contain a DL value.

---

## 8. LTR Number Rules

### 8.1 Supported formats

Phase 7 rules must support at least:

| Format | Example | Meaning |
|---|---|---|
| Standard monthly DL | `DL-2026-04-001` | ConnLab generated normal LTR |
| W prefix | `W123` | Existing / special external number format |
| Standard plus suffix | `DL-2026-04-001ABC` | Existing base DL with suffix |
| Invalid | `DL-26-4-1`, `abc`, empty | Actionable validation error |

### 8.2 Monthly sequence rule

For generated standard DL numbers:

```text
DL-{YYYY}-{MM}-{NNN}
```

Sequence rule:

- current month starts at `001`;
- next sequence increments from existing workbook/local values for the same year and month;
- suffix records should not inflate base monthly sequence unless explicitly configured;
- invalid or unrecognized values should be reported but ignored for next-number calculation only if safe.

### 8.3 Pure rule module

Put pure logic in:

```text
backend/modules/ltr/ltr_number_rules.py
```

Expected API:

```python
parse_ltr_number(value: str) -> LtrNumberParseResult
validate_ltr_number(value: str) -> LtrValidationResult
format_standard_ltr(year: int, month: int, sequence: int) -> str
next_monthly_ltr(existing: Sequence[str], year: int, month: int) -> str
```

No SQLite, no Excel, no API, no current date hidden inside pure functions unless passed explicitly.

---

## 9. Workbook Snapshot And Write Policy

### 9.1 Snapshot before write

Before any write task, create a read-only snapshot:

```text
LtrWorkbookSnapshot
  - workbook_path
  - workbook_format: xls|xlsx|unknown
  - modified_time
  - file_size
  - sheet_names
  - selected_sheet
  - header_row
  - column_map
  - existing_ltr_numbers
  - layout_warnings
```

### 9.2 Layout mapping must be explicit

The workbook gateway must discover or be configured for:

- year/month sheet naming;
- header row;
- DL column;
- target columns for the 19 readiness fields;
- last data row;
- next writable row;
- merged cell behavior, if any;
- protected sheet / workbook lock state.

### 9.3 Write commit safety

A real workbook write is allowed only when all conditions are true:

```text
readiness status is ready
preview was generated from current workbook snapshot
operator approved preview
no duplicate active LTR exists in ConnLab
no duplicate target LTR exists in workbook snapshot
workbook path is configured
workbook password is configured when the workbook requires it
workbook write is enabled
backup policy is satisfied
gateway can obtain write access
```

### 9.4 Failure behavior

If workbook write fails:

- do not mark the local `LtrRecord` as `REGISTERED` unless operating in explicit `local_only` mode;
- return actionable error:
  - missing workbook;
  - workbook locked;
  - workbook password missing or invalid;
  - unsupported `.xls` adapter;
  - sheet not found;
  - required column not mapped;
  - duplicate DL;
  - save failed;
- preserve preview and error evidence for operator review.

---

## 10. Project Lifecycle Governance

### 10.1 Do not replace `ProjectStatus` in Phase 7 first step

Current `ProjectStatus` already includes:

```text
draft
intake_received
precheck_passed
confirmed
ltr_registered
folder_created
closed
cancelled
```

The safer Phase 7 approach is:

```text
ProjectStatus remains coarse.
ProjectLifecycleEvent records detailed workflow history.
ProjectLifecycleService derives current operation permissions.
```

### 10.2 Proposed lifecycle event model

```text
ProjectLifecycleEvent
  - event_id
  - project_id
  - event_type
  - from_state
  - to_state
  - actor
  - reason
  - evidence_asset_id
  - created_at
```

Recommended event types:

```text
intake_confirmed
precheck_completed
ltr_readiness_checked
ltr_preview_generated
ltr_registered_local
ltr_registered_workbook
ltr_registration_failed
folder_preview_generated
folder_generated
evidence_added
application_form_corrected
ltr_renumbered
project_closed
project_cancelled
```

### 10.3 Operation guard table

| Operation | Minimum condition | Block reason example |
|---|---|---|
| Run readiness | project confirmed and application form exists | `Project has no confirmed application form.` |
| Preview LTR | readiness has no blockers | `Required LTR fields are missing.` |
| Commit LTR | approved preview and no duplicate active LTR | `Project already has registered LTR.` |
| Preview folder | project has LTR or explicit local-only no-LTR policy | `LTR registration is not complete.` |
| Generate folder | folder preview has no conflicts | `Target folder already exists.` |
| Correct application form | project not closed | `Closed projects are read-only.` |
| Renumber LTR | reason supplied and preview clean | `Renumbering requires evidence and conflict check.` |

---

## 11. Evidence Placement Policy

### 11.1 Recommended folder structure

Update `docs/06_FOLDER_TEMPLATE.md` during the folder evidence task if approved:

```text
{DL_NUMBER}/
  00_Request/
    original_email/
    application_form/
    corrected_application_forms/
    attachments/
    communication_evidence/
  01_LTR/
    preview/
    registration/
    corrections/
  02_Specifications/
    product_spec/
    standards/
    customer_requirements/
  03_Matrix/
  04_Test_Record/
  05_Raw_Data/
  06_Images/
  07_Report/
  08_Customer_Report/
  99_Archive/
```

### 11.2 Evidence placement rules

| Evidence type | Target | Rule |
|---|---|---|
| Original `.msg` | `00_Request/original_email/` | Preserve exactly once |
| Selected application form | `00_Request/application_form/` | Copy selected form separately |
| Corrected application form | `00_Request/corrected_application_forms/` | Append with timestamp/reason |
| Supporting attachments | `00_Request/attachments/` | Keep original names when safe |
| Product specifications | `02_Specifications/product_spec/` | Classify from intake asset role |
| Standards | `02_Specifications/standards/` | Classify from filename/operator role |
| Customer requirements | `02_Specifications/customer_requirements/` | Classify from filename/operator role |
| LTR preview | `01_LTR/preview/` | Store preview JSON/text summary |
| LTR registration evidence | `01_LTR/registration/` | Store commit summary / workbook row pointer |
| LTR correction evidence | `01_LTR/corrections/` | Preserve old/new number and reason |
| Communication evidence | `00_Request/communication_evidence/` | Follow-up emails, screenshots, notes |

### 11.3 No-overwrite policy

The evidence placement service must:

- use deterministic destination rules;
- detect conflicts before copying;
- never overwrite existing evidence silently;
- append suffixes or block based on policy;
- return a placement preview before execution if multiple files will be copied.

---

## 12. Operator-Facing Exception Workflows

### 12.1 Email has no application form

Expected behavior:

```text
IntakePackage imported
IntakeAsset records created
No IntakeCase created automatically
Package status: NEEDS_APPLICATION_FORM_SELECTION or NEEDS_FOLLOWUP
Operator action: request missing application form / attach direct form later
No Project created
No LTR allowed
```

### 12.2 One email has multiple application forms

Expected behavior:

```text
One IntakePackage
Multiple application form candidate assets
Operator selects one form per IntakeCase
Each confirmed IntakeCase can create one Project
Supporting attachments may be shared as evidence
```

### 12.3 Missing application form data

Expected behavior:

```text
IntakeDraft created with missing fields
Human review required
Confirmed data source is manual override where necessary
Readiness blocks LTR until required fields are confirmed or placeholder policy is explicit
```

### 12.4 LTR number is added later or changed

Expected behavior:

```text
Generate renumber preview
Check local LTR record, workbook row, folder path, file names, and evidence paths
Require reason
Preserve old number and evidence
Never overwrite folder or files
```

### 12.5 Folder already exists and application form is later corrected

Expected behavior:

```text
Do not regenerate the whole folder automatically
Create corrected evidence placement preview
Copy corrected form to corrected_application_forms/
Record lifecycle event
Do not delete original request evidence
```

---

## 13. API Surface Plan

Keep route bodies thin. Suggested contracts:

### 13.1 Readiness

```text
GET /api/projects/{project_id}/ltr/readiness
POST /api/projects/{project_id}/ltr/readiness/confirm-field
```

### 13.2 Preview

```text
POST /api/projects/{project_id}/ltr/preview
```

Response should include:

```text
proposed_ltr_number
target_sheet
target_row
field_write_map
warnings
snapshot_id or snapshot_fingerprint
```

### 13.3 Commit

```text
POST /api/projects/{project_id}/ltr/commit
```

Request should include:

```text
preview_id
operator_confirmed: true
mode: local_only|excel_write
```

### 13.4 Evidence placement

```text
POST /api/projects/{project_id}/evidence/placement-preview
POST /api/projects/{project_id}/evidence/place
```

Only add these routes if evidence placement is implemented outside folder generation.

### 13.5 Lookup

```text
GET /api/projects/lookup?query=
GET /api/projects/{project_id}/sample-summary
GET /api/projects/{project_id}/testing-summary
```

---

## 14. Execution Waves

### Wave 1: Real input baseline and parser calibration

Goal:

```text
Prove ConnLab can understand the real request materials without writing LTR or generating folders.
```

Includes:

- board activation;
- real sample baseline;
- real DOCX parser calibration;
- fixture strategy.

No Excel write.

### Wave 2: LTR rules, readiness, and preview

Goal:

```text
Prove ConnLab can calculate and preview registration safely.
```

Includes:

- LTR field catalog;
- LTR number rules;
- workbook snapshot gateway;
- readiness service;
- preview service.

No real Excel write by default.

### Wave 3: Commit, evidence, lifecycle guards

Goal:

```text
Commit approved registrations safely and preserve project evidence.
```

Includes:

- local record sync;
- optional workbook write behind feature flag;
- evidence placement;
- lifecycle guards;
- exception workflows.

### Wave 4: Lookup and validation close

Goal:

```text
Give operators quick visibility and close Phase 7 with regression evidence.
```

Includes:

- lookup surfaces;
- manual smoke checklist;
- docs and task board sync.

---

## 15. Detailed Task Breakdown

### TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION

Goal:

- approve Phase 7 scope;
- add Phase 7 section to `docs/task_board.md`;
- activate only the first implementation task.

Inputs:

- this plan document;
- `docs/task_board.md`;
- `docs/phase6a_validation.md`.

Outputs:

- `docs/task_board.md` updated with Phase 7 section;
- first active task set to `TASK_037_REAL_SAMPLE_BASELINE`.

Acceptance:

- board states that Phase 7 does not include Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan;
- no code implementation in this task.

---

### TASK_037_REAL_SAMPLE_BASELINE

Goal:

- build a documented compatibility baseline for the four real `.msg` samples and two `.docx` forms.

Inputs:

- real files in `C:\Users\White\Desktop\AI information`;
- existing Phase 6A intake services;
- `docs/phase6a_validation.md`.

Outputs:

- `docs/phase7_real_sample_baseline.md`;
- table of expected behavior for each sample;
- fixture strategy for sanitized/generated tests.

Acceptance:

- each `.msg` sample has expected classification:
  - no application form;
  - one application form;
  - multiple application forms;
  - application form plus specification;
- each `.docx` form has parser field coverage notes;
- real sample paths are documented but not hard-coded;
- originals are not committed.

---

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
- sanitized or generated regression fixtures;
- parser coverage report.

Acceptance:

- form number/revision extracted when present;
- requestor, phone, date, email, business unit, project number extracted;
- sample fields extracted or marked review-required;
- requested testing fields extracted or marked review-required;
- applicant and tester-modified samples produce comparable structured drafts;
- parser output remains draft-only before confirmation.

---

### TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP

Goal:

- define the authoritative Phase 7 LTR readiness field catalog before building the readiness service.

Inputs:

- 19-field image list;
- confirmed `Project`, `ApplicationForm`, `SampleInfo`, `IntakeAsset`, and `FileAsset` data;
- current workbook snapshot notes if available.

Outputs:

- `backend/modules/ltr/ltr_field_catalog.py`;
- `docs/phase7_ltr_field_mapping.md`;
- field source, fallback, severity, placeholder policy, and operator action mapping.

Acceptance:

- each of the 19 fields has:
  - canonical field key;
  - display label;
  - source path;
  - fallback/manual policy;
  - severity;
  - placeholder policy if applicable;
- contradictory future-result fields such as Test Result / Failed item are handled by explicit placeholder policy, not accidental blocking.

---

### TASK_040_LTR_NUMBER_RULES

Goal:

- isolate LTR number parsing, validation, formatting, and next monthly sequence calculation as pure deterministic rules.

Inputs:

- existing `backend/application/ltr_service.py`;
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
- invalid values return actionable errors;
- pure rules do not import Excel, SQLite, FastAPI, or current settings.

---

### TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY

Goal:

- read LTR workbook metadata and existing numbers through an infrastructure gateway without writing.

Inputs:

- configurable workbook path;
- backup workbook `D:\Source\Office Auto\TestDocument\LTR_number.xls`;
- `backend/infrastructure/office/excel_workbook_gateway.py` placeholder.

Outputs:

- `backend/infrastructure/office/excel_ltr_workbook_gateway.py`;
- `backend/infrastructure/office/ltr_workbook_snapshot.py`;
- workbook snapshot model;
- layout discovery report;
- tests using generated workbook fixtures where possible.

Acceptance:

- no API/UI/application service opens Excel directly;
- gateway reports workbook format as `.xls`, `.xlsx`, or unsupported;
- gateway identifies sheet strategy or reports unsupported layout;
- gateway lists existing monthly numbers where possible;
- file lock / missing file / unsupported adapter errors are explicit;
- no write operation exists in this task.

---

### TASK_042_LTR_READINESS_SERVICE_AND_API

Goal:

- verify required LTR registration fields before any number is registered or workbook write is attempted.

Inputs:

- confirmed project/application form/sample data;
- field catalog from `TASK_039`;
- optional supporting evidence assets.

Outputs:

- `backend/application/ltr_readiness_service.py`;
- readiness result DTOs;
- thin API route;
- tests for blockers, review-required fields, and placeholder-allowed fields.

Acceptance:

- missing `BLOCKER` fields block preview/registration;
- `REVIEW_REQUIRED` fields require manual confirmation or policy;
- `PLACEHOLDER_ALLOWED` fields use explicit placeholder policy;
- each missing field shows where the operator should fill or confirm it;
- confirmed values are traceable to application form, project, sample, evidence, manual override, or placeholder policy.

---

### TASK_043_LTR_REGISTRATION_PREVIEW

Goal:

- preview the next LTR number and target workbook row before writing.

Inputs:

- readiness check result;
- workbook snapshot;
- number rules;
- existing local LTR records.

Outputs:

- `backend/application/ltr_registration_workflow_service.py`;
- preview object:
  - proposed LTR number;
  - source sequence values;
  - target sheet;
  - target row;
  - fields to write;
  - conflicts/warnings;
  - snapshot fingerprint;
- preview API route.

Acceptance:

- no write happens during preview;
- user can see proposed number and field mapping before committing;
- duplicate local LTR and duplicate workbook DL are reported;
- stale workbook snapshot can be detected before commit;
- preview can operate in `local_only` mode.

---

### TASK_044_LTR_LOCAL_COMMIT_AND_AUDIT_RECORD

Goal:

- commit an approved LTR registration to ConnLab local records without requiring workbook write.

Inputs:

- approved preview;
- confirmed readiness data;
- current `LtrService`.

Outputs:

- local commit workflow;
- synchronized `LtrRecord`;
- lifecycle event;
- audit/evidence note.

Acceptance:

- duplicate active LTR is blocked;
- local commit is explicit and traceable;
- project status changes to `LTR_REGISTERED` only after successful local commit;
- commit stores preview reference or equivalent field snapshot;
- local-only mode is clearly identified.

---

### TASK_045_LTR_EXCEL_WRITE_GATEWAY_AND_SYNC

Goal:

- optionally commit an approved LTR registration to the external Excel workbook through the gateway.

Inputs:

- approved preview;
- confirmed readiness data;
- workbook snapshot;
- feature flag/settings.

Outputs:

- workbook write gateway method;
- backup/write policy;
- synchronized local `LtrRecord`;
- workbook row pointer;
- lifecycle event and audit note.

Acceptance:

- write path is disabled by default;
- Excel is opened, written, saved, and released only through infrastructure gateway;
- `.xls` adapter strategy is documented and tested as far as safely possible;
- password-protected workbook open uses configured password, not a hard-coded value;
- missing/invalid workbook password produces an actionable error and does not create a misleading registered state;
- ConnLab record is marked registered only after successful write, unless explicit local-only mode is used;
- workbook write failures do not create a misleading registered state;
- no tests write to the real workbook path.

---

### TASK_046_LTR_RENUMBER_AND_PROJECT_FOLDER_RENAME_PLAN

Goal:

- support safe correction when LTR number is added later or changed.

Inputs:

- existing LTR record;
- folder record;
- project assets;
- evidence placement policy.

Outputs:

- rename preview for project folder and related file names;
- workbook/local record update plan;
- evidence preservation plan;
- no-overwrite conflict handling.

Acceptance:

- renumbering requires preview and explicit confirmation;
- folder/file rename conflicts block execution;
- old number, new number, reason, and related evidence are recorded;
- no automatic destructive rename occurs.

---

### TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES

Goal:

- define where email, application forms, attachments, specifications, LTR evidence, and communication evidence go in the project folder.

Inputs:

- `docs/06_FOLDER_TEMPLATE.md`;
- current `FolderService`;
- Phase 6A `IntakePackage`, `IntakeAsset`, and project `FileAsset` records;
- evidence placement policy in this plan.

Outputs:

- `backend/modules/folder/evidence_placement_rules.py`;
- `backend/application/evidence_placement_service.py`;
- updated folder template documentation if approved;
- tests with temporary directories.

Acceptance:

- original `.msg` is preserved;
- selected application form is copied separately from supporting attachments;
- corrected forms preserve old and new evidence;
- specifications can be classified and placed under `02_Specifications`;
- LTR preview/registration evidence can be placed under `01_LTR`;
- later corrected forms do not delete original evidence.

---

### TASK_048_PROJECT_LIFECYCLE_GATING

Goal:

- prevent operations that are invalid for the current project lifecycle stage.

Inputs:

- lifecycle governance section in this plan;
- existing project, intake, precheck, LTR, and folder states.

Outputs:

- `backend/application/project_lifecycle_service.py`;
- lifecycle event model/repository if needed;
- operation guard integration through application services;
- frontend disabled/reason states if UI is included.

Acceptance:

- cannot preview/commit LTR before confirmed data and readiness pass;
- cannot generate folder unsafely before LTR/folder prerequisites;
- cannot mutate closed/cancelled projects;
- blocked actions return business-readable reasons;
- current `ProjectStatus` is not needlessly expanded or broken.

---

### TASK_049_EXCEPTION_WORKFLOWS

Goal:

- make real failure cases explicit and traceable.

Inputs:

- exception workflows in this plan;
- real sample baseline.

Outputs:

- exception reason records or lifecycle events;
- operator action guidance in API/UI;
- evidence attachment path for corrections.

Acceptance:

- no application form in email creates a package needing follow-up, not a project;
- one email with multiple application forms creates separate cases/projects;
- missing application form info blocks downstream steps until confirmed;
- corrected application forms preserve original and communication evidence;
- LTR changes require reason and preview.

---

### TASK_050_LOOKUP_SURFACES_FOR_SAMPLE_AND_TEST_CONDITIONS

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
- no Matrix/test execution/report generation is implemented;
- lookup uses structured records, not raw Word/Excel as source of truth.

---

### TASK_051_PHASE7_VALIDATION_AND_DOCS_SYNC

Goal:

- close Phase 7 with validation and board sync.

Outputs:

- updated `docs/task_board.md`;
- validation summary;
- manual smoke checklist for real sample flow;
- known limitations;
- next phase recommendation.

Acceptance:

- relevant backend tests pass;
- frontend build passes if UI changed;
- real sample manual validation matrix is updated;
- workbook write mode and limitations are documented;
- next phase recommendation is documented;
- no Matrix, Report, AI review, LAN deployment, or permissions slipped into Phase 7.

---

## 16. Suggested Phase 7 Acceptance Gate

Phase 7 is done only when:

- all real `.msg` and `.docx` samples have documented expected behavior;
- parser handles real `.docx` forms well enough to create reviewable drafts;
- LTR field catalog maps all 19 readiness fields to source/fallback/severity/policy;
- LTR readiness check blocks incomplete registration correctly;
- LTR number rules are deterministic and tested;
- workbook snapshot is available before write;
- LTR registration preview is available before commit;
- local commit is traceable and duplicate-safe;
- external workbook write, if enabled, is behind infrastructure gateway and safely releases Excel;
- project folder evidence placement preserves original email, selected application form, attachments, specifications, LTR evidence, and correction evidence;
- lifecycle guards prevent invalid next actions;
- sample info and testing condition/method lookup is available;
- no Matrix, report generation, AI review, LAN deployment, permissions, or future-scope feature slipped into Phase 7.

---

## 17. Validation Strategy

### 17.1 Backend validation

Run:

```text
py -m pytest -q
```

Expected:

- all existing tests continue to pass;
- new tests cover:
  - LTR number rules;
  - LTR field catalog;
  - readiness blockers/review/placeholder policy;
  - workbook snapshot errors;
  - preview no-write behavior;
  - duplicate LTR conflict;
  - local commit;
  - evidence placement conflict;
  - lifecycle guards.

### 17.2 Frontend validation

If frontend is touched, run:

```text
npm run build
```

Manual smoke:

- intake package can be opened;
- case review draft can be reviewed;
- confirmed project shows readiness/LTR/folder guidance;
- disabled actions show reason;
- LTR preview does not write;
- commit path clearly distinguishes local-only and workbook-write mode.

### 17.3 Real sample validation

Create:

```text
docs/phase7_real_sample_baseline.md
```

Minimum table columns:

```text
sample file
source type
expected package count
expected application form candidates
expected supporting specs
expected inline/ignored assets
expected intake cases
parser coverage
operator action
known limitation
```

### 17.4 Real workbook validation

Create:

```text
docs/phase7_ltr_workbook_layout.md
```

Minimum table columns:

```text
workbook path
format
sheet strategy
header row
DL column
readable fields
writable fields
unsupported fields
adapter used
lock behavior
write mode
known limitation
```

---

## 18. Risks And Controls

| Risk | Control |
|---|---|
| Real `.msg` / `.docx` files may contain sensitive information | Do not commit originals; create sanitized fixtures or synthetic regression fixtures |
| `.xls` workbook may not be readable by openpyxl | Snapshot task must detect format and choose adapter behind gateway |
| Workbook may be locked on public drive | Gateway must detect lock and return actionable error |
| Workbook layout may differ by year/sheet | Snapshot task must document sheet and column layout before write task |
| LTR registration could create mismatched SQLite/Excel state | Commit workflow must coordinate write/local record with failure handling |
| Future-result fields appear in “required” LTR list | Use severity and placeholder policy, not blind blocking |
| LTR renumbering can break folder/file names | Always preview rename; never overwrite; preserve old evidence |
| Lifecycle model could overtake current MVP | Add operation guards around current workflow first; avoid broad enum replacement |
| Report pain point may pull scope forward | Preserve report-ready structured data, but keep automated report generation out of Phase 7 |
| Server upgrade could be blocked by local Office COM | Keep COM behind local infrastructure gateway/agent boundary; services depend on ports |

---

## 19. Recommended Next Step

Current task board recommendation:

```text
TASK_047_FOLDER_EVIDENCE_PLACEMENT_RULES
```

Why this is next:

- `TASK_036_PHASE7_SCOPE_AND_BOARD_ACTIVATION` is complete.
- `TASK_037_REAL_SAMPLE_BASELINE` is complete.
- `TASK_038_REAL_DOCX_PARSER_CALIBRATION` is complete.
- `TASK_039_LTR_FIELD_CATALOG_AND_READINESS_SOURCE_MAP` is complete.
- `TASK_040_LTR_NUMBER_RULES` is complete.
- `TASK_041_LTR_WORKBOOK_SNAPSHOT_GATEWAY` is complete.
- readiness service/API is complete.
- registration preview is complete.
- local commit is complete.
- optional workbook write/sync boundary is complete.
- renumber/folder rename preview is complete.
- evidence placement is the next controlled step before lifecycle guards and exception workflows.

Do not start `TASK_048` or later tasks until `TASK_047` is complete and `docs/task_board.md` is updated.

---

## 20. Operator Prompt For AI/Codex

Use this prompt when starting Phase 7:

```text
Read AGENTS.md first.
Then read docs/task_board.md.
Then read docs/ConnLab_Phase7_Real_LTR_Folder_Lifecycle_Plan.md.
Implement only the active task allowed by docs/task_board.md.
Do not implement Matrix, Report, AI review, LAN deployment, permissions, or Outlook inbox auto-scan.
Do not write to the real LTR workbook unless the active task explicitly allows workbook write and settings enable it.
Before coding, state the current phase and active task ID.
After finishing, update docs/task_board.md with status, validation, and next step.
```
