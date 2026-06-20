# TASK_330 Project Basic Information Authority Plan

## Current Control Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active implementation task: none. TASK_329 is complete.
- Why this task is allowed now: the user explicitly requested a controlled plan and task file for a new Project Workbench follow-up. This document is a reviewable plan only; no implementation code is authorized until the user approves.

## Goal

Introduce `Basic Information` as the project-level confirmed data source for formal downstream outputs.

The feature creates a confirmed `Project Basic Information` snapshot that can be reviewed and edited by the operator from a dedicated Workbench entry. Project folder generation and updates must use the latest confirmed snapshot when writing formal business files.

## Task Split

TASK_330 is an umbrella design and must be implemented as controlled subtasks:

1. `TASK_330A_PROJECT_BASIC_INFORMATION_AUTHORITY_DATA_API`
   - Backend persistence, source assembly, draft save, confirm, review status, and API.
   - Stop after API tests pass. No Workbench UI page and no project folder output consumption.
2. `TASK_330B_PROJECT_BASIC_INFORMATION_WORKBENCH_UI`
   - Workbench top `Basic Information` action, dedicated edit/confirm page, and read-only Workbench summary card.
   - Stop after frontend/API integration tests and browser smoke. No formal file output refresh.
3. `TASK_330C_PROJECT_BASIC_INFORMATION_OUTPUT_CONSUMPTION`
   - Project folder create/update blocker, Fee form, Customer Feedback form, copied application Word write-back, and output source signatures.
   - Stop after formal output tests and manual folder smoke.

Do not implement all three phases in a single coding pass.

## Business Intent

ConnLab currently gathers related project data from several places:

- application form intake,
- Project and LTR registration,
- Matrix confirmation and date-related execution fields,
- Fee Evaluation total cost,
- operator corrections.

Those values should become reusable by:

- Fee Evaluation form output,
- Customer Feedback form output,
- copied LTR application Word write-back,
- future LTR Excel workbook synchronization,
- future report generation.

TASK_330 only establishes and consumes the data source for the formal project-folder outputs listed in its subtasks. It does not implement public-drive LTR workbook writing or report generation.

## User-Facing Model

Workbench top action order:

```text
Matrix Editor | Fee Evaluation | Basic Information | Generate/Update project folder
```

`Basic Information` opens a dedicated editor page or work area, following the broad interaction model of Fee Evaluation:

- load current project identity and source-derived draft,
- allow operator edits,
- save draft changes,
- confirm the draft as the latest authoritative snapshot,
- return to Workbench after confirmation or cancel.

The Workbench right-side `Project Basic Information` card is summary-only:

- no edit fields,
- no duplicate DL Number / Product / Test Item values already visible in the top project identity,
- no `Edit` action,
- may provide a `View` action/disclosure to inspect all confirmed basic information read-only,
- should show compact status such as confirmed/not confirmed, needs review, last confirmed time, and whether folder outputs are using the latest confirmed snapshot.

## Core Rules

1. Project folder creation uses the latest confirmed Project Basic Information snapshot.
2. Project folder update uses the latest confirmed Project Basic Information snapshot to refresh formal outputs.
3. Fee form, Customer Feedback form, and copied application Word write-back must read the same confirmed snapshot.
4. If Basic Information is unconfirmed, formal project folder output generation must block with an actionable backend blocker.
5. If upstream sources change after confirmation, Basic Information becomes `needs_review`; confirmed data remains stable until the operator confirms a new snapshot.
6. Existing projects must not be silently confirmed. On first use, the backend assembles a draft from current sources and the operator must explicitly confirm it.
7. Workbench project-folder blockers must point the operator to confirm Basic Information first when no confirmed snapshot exists.
8. The frontend may display source-change state, but the backend remains authoritative.

## Data Design

Add a persisted Project Basic Information model with draft and confirmed concepts.

Recommended storage shape:

```text
ProjectBasicInformationRecord
  id
  project_id
  status: draft | confirmed
  version
  confirmed_at
  confirmed_by
  data_json
  source_signature_json
  created_at
  updated_at
```

`data_json` should contain structured fields grouped by business purpose:

- request info: project_type, requested_by, phone, requestor_email, location, business_unit, customer/contact fields when available
- product/test info: description_pn, product_description, test_item, applicable_specifications, test_type, sub_contract
- lab schedule: lab_performing_tests, condition_of_samples_when_received, date_lab_received_samples, estimated_completion_date, start_test_date, finish_test_date, report_date
- ownership/result: project_leader, test_result, failed_item, sample_deposition, remarks_po
- fee info: test_fee or total_fee, sourced from Fee Evaluation authority when available

Use a typed application DTO, for example:

```python
ProjectBasicInformationSnapshot
ProjectBasicInformationDraft
ProjectBasicInformationFieldSource
```

The exact field list should be implemented from the approved subtask file, not inferred ad hoc during coding.

## Minimum Required Fields For Confirmation

The confirm endpoint must validate a minimal field set before creating an authoritative version:

- DL/LTR number,
- project type,
- product description or description P/N,
- test item,
- requested by,
- project leader,
- lab performing the tests.

Other fields may remain blank and still be written as blank to output files. Validation errors must identify the missing business labels, not backend field names.

## Source Assembly And Merge Rules

Add an application service that assembles a draft from known project sources.

Draft assembly priority:

1. Existing unconfirmed operator draft values.
2. Latest confirmed Basic Information snapshot values.
3. Current source suggestions from application form / intake parsed fields.
4. Current source suggestions from Project identity and LTR fields.
5. Current source suggestions from Matrix authority-derived date fields, where available and approved.
6. Current source suggestions from Fee authority total fee, where available.

Source updates must not silently overwrite either an operator draft or a confirmed snapshot. They should produce field-level suggestions and set `needs_review` when a source suggestion differs from the latest confirmed value. The UI may show suggestions, but the operator must explicitly accept/edit and confirm.

Stored field metadata should retain source information where useful:

```text
field_key
value
source: operator | confirmed_snapshot | application_form | project_identity | matrix_authority | fee_authority
source_value
needs_review
```

## Existing Project Initialization

For existing projects with no confirmed Basic Information:

1. `GET /basic-information` assembles a draft from current stored project, application, Matrix, and Fee sources.
2. The response status is `unconfirmed`.
3. Workbench may show a project-folder blocker that says Basic Information must be confirmed first.
4. The backend must not auto-confirm this draft.
5. The operator opens `Basic Information`, reviews/edits, and confirms.

## Backend API

Add typed APIs under Project scope:

```text
GET  /api/projects/{project_id}/basic-information
PUT  /api/projects/{project_id}/basic-information/draft
POST /api/projects/{project_id}/basic-information/confirm
```

Suggested response contract:

- project id
- draft data
- latest confirmed data, if present
- status: `unconfirmed` | `confirmed` | `needs_review`
- changed source fields
- blockers
- warnings
- last confirmed metadata

The confirm endpoint should:

- validate required fields,
- write a new confirmed version,
- keep previous confirmed versions for traceability,
- return the newly confirmed snapshot.

## Project Folder Integration

Update the Workbench project folder flow so formal file generation uses Basic Information:

- before creating or updating the official project folder, backend checks latest confirmed Basic Information,
- if missing, return a blocker and do not mutate files,
- Required form generation and copied application Word write-back receive the confirmed snapshot,
- output records should include the Basic Information version/signature used,
- `Update project folder` can refresh formal outputs when the confirmed Basic Information version changes.

Refresh safety must reuse TASK_321 managed-output semantics:

- ConnLab may refresh only files that are managed outputs and whose current disk fingerprint still matches the last stored managed-output fingerprint.
- If a Fee form, Customer Feedback form, or copied application Word document is unmanaged, missing managed metadata, or has a changed disk fingerprint, return conflict/block instead of overwriting.
- Final placement must use staging and safe replace rules already established for formal outputs.
- The output record must include the Basic Information version/signature used for that generation.

This task should not change unrelated Matrix authority rules, Fee editing behavior, public-drive upload rules, report generation, StepInstance scope, AI, permissions, LAN, or multi-user behavior.

## Office Output Integration

The formal output generators should receive a single confirmed Basic Information DTO.

Fee form:

- fill base identity fields only,
- continue preserving current Fee Evaluation row/pricing behavior,
- do not let form output invent missing values.

Customer Feedback form:

- fill base identity plus contact/date details,
- use the same DTO as Fee form.

Copied LTR application Word document:

- write known application fields from the confirmed snapshot,
- only modify the copied document in Submitted Material,
- never mutate original intake attachments.

Office access remains inside infrastructure gateways. If Excel COM lifecycle is centralized, it should be through a thin OfficeFacade/session helper; field mapping remains in template-specific gateways, not in the facade.

## Frontend Design

Add a Project Workbench top action:

```text
Basic Information
```

Route suggestion:

```text
/projects/{project_id}/basic-information
```

Dedicated page/work area:

- title: `Basic Information`
- grouped fields, not one huge unstructured table
- save draft and confirm actions
- cancel returns to Workbench
- confirmation returns to Workbench
- visible source/review state when upstream data changed

Right-side summary card:

- status only,
- compact metadata,
- optional `View` read-only expansion,
- no editing fields,
- no repeated project title identity.

All frontend API calls must go through `frontend/src/api/client.ts` or a controlled API split that preserves the shared request boundary.

## In Scope

- `TASK_330A`: Backend persistence model/repository for Project Basic Information.
- `TASK_330A`: Application service for source assembly, draft save, confirm, and source review state.
- `TASK_330A`: Thin FastAPI routes and Pydantic DTOs.
- `TASK_330B`: Workbench top action wiring.
- `TASK_330B`: Dedicated Basic Information editor page/work area.
- `TASK_330B`: Workbench summary-only card with optional read-only View expansion.
- `TASK_330C`: Project folder create/update integration with confirmed snapshot blocker and output version/signature.
- `TASK_330C`: Fee form, Customer Feedback form, and copied application Word write-back using confirmed snapshot.
- Focused backend, API, frontend, and static shell tests in each subtask.
- Task board update after each approved implementation subtask.

## Out Of Scope

- No StepInstance implementation.
- No report generation implementation.
- No public-drive upload or LTR authority rule redesign.
- No LTR workbook writeback.
- No changes to Matrix editing semantics.
- No changes to Fee Evaluation pricing authority semantics beyond consuming confirmed Basic Information for formal outputs.
- No generic template mapping UI.
- No automatic overwriting of confirmed Basic Information from source changes.
- No direct frontend file, Office, or SQLite access.

## Risks

- Field naming may diverge between application forms, LTR Excel, Fee form, Customer Feedback form, and future reports. Mitigation: define one explicit field dictionary and template-specific mappings.
- Upstream source changes could confuse users if they silently replace confirmed values. Mitigation: `needs_review` state and explicit confirm.
- Office template labels may vary. Mitigation: gateway-level warnings for missing labels and tests for expected templates.
- The feature touches backend, frontend, persistence, and Office output integration. Mitigation: split into TASK_330A, TASK_330B, and TASK_330C.

## Acceptance Criteria

- `TASK_330A`: existing projects with no confirmed snapshot receive an assembled unconfirmed draft and are never silently confirmed.
- `TASK_330A`: merge priority preserves operator draft values, then latest confirmed values, then source suggestions.
- `TASK_330A`: confirm validates the minimum required fields and returns business-readable missing-field errors.
- `TASK_330B`: Workbench has a `Basic Information` action between `Fee Evaluation` and the project folder button.
- `TASK_330B`: `Basic Information` opens a dedicated editable page/work area.
- `TASK_330B`: The operator can save a draft and confirm it as the latest authoritative snapshot.
- `TASK_330B`: Workbench summary card is read-only and does not duplicate DL Number / Product / Test Item.
- `TASK_330B`: Summary card can show all basic information through a read-only View expansion.
- `TASK_330C`: Project folder create/update blocks when no confirmed Basic Information snapshot exists.
- `TASK_330C`: Project folder create/update uses the latest confirmed snapshot for:
  - Fee form base identity fields,
  - Customer Feedback form base/contact fields,
  - copied LTR application Word write-back fields.
- `TASK_330C`: Reconfirming Basic Information creates a new version and makes `Update project folder` able to refresh formal outputs with the new version only when managed-output fingerprints are safe.
- `TASK_330C`: Existing generated output records store enough Basic Information version/signature context to explain whether outputs are current.
- UI and API do not expose backend implementation terms such as raw table names or SQLite.

## Validation Plan

`TASK_330A`:

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py -q
py -m pytest tests/integration/test_project_basic_information_api.py -q
```

`TASK_330B`:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout BasicInformation --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task330 or basic_information or project_workbench"
```

`TASK_330C`:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
py -m pytest tests/unit/test_official_project_workspace_service.py -q
py -m pytest tests/integration/test_official_project_workspace_api.py -q
```

Manual smoke after each implementation approval:

- Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
- After TASK_330B, confirm top action order includes `Basic Information`.
- Open Basic Information, edit a field, save draft, confirm, and return to Workbench.
- Confirm summary card shows confirmed/review state and View is read-only.
- After TASK_330C, click `Generate/Update project folder`.
- Verify generated Fee form, Customer Feedback form, and copied application Word document use the confirmed Basic Information values.

## Stop Point

Stop after this plan and split task files are reviewed. Do not implement until the user explicitly approves the next subtask, starting with TASK_330A.
