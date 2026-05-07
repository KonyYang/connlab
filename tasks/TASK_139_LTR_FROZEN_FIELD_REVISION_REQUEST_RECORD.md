# TASK_139_LTR_FROZEN_FIELD_REVISION_REQUEST_RECORD

## Status

done

## Phase / Active Task Justification

- Current Phase: `Phase 10B - LTR workbook write hardening`
- Current Active Task on board: `None - TASK_100 complete, pending user decision for next task`
- Why this task is allowed to plan now: `TASK_099` froze normal base-field editing after LTR registration, and `TASK_100` removed creation-stage controls from Project Workbench. The remaining controlled gap is a traceable way to record requested corrections for frozen base fields without reopening New Project editing or silently mutating the LTR workbook/folder.

## Step 1 Plan Only

This document is the executable implementation plan for review.
No implementation code may be written until the user approves this plan.

## Purpose

Add a narrow backend/API record for post-LTR frozen-field revision requests.

After an LTR number has been registered, normal New Project / Precheck base-field editing is frozen. Operators still need a traceable way to request corrections. This task records those requests as structured data, linked to the intake case/project/LTR, without applying the correction automatically.

## Task Understanding

Goal:

- Preserve the `TASK_099` freeze rule.
- Add a structured request record for proposed changes to frozen fields.
- Make the request auditable and reviewable later.
- Avoid implementing the approval/apply workflow in this task.

Inputs:

- intake case id
- project id when already confirmed
- registered LTR number or LTR record id when available
- requested field changes:
  - field key
  - current value snapshot
  - proposed value
  - reason
- requested by / operator identity when available from local Windows/user context or request payload

Outputs:

- persisted revision request record
- typed API response for create/list/detail
- tests proving frozen fields cannot be directly edited but can have a revision request recorded

## Scope

Backend/API:

1. Add a narrow `frozen_field_revision_request` persistence model.
2. Add repository/service boundaries for creating and reading requests.
3. Validate that each requested field is in the current frozen field set.
4. Validate that the intake case is actually frozen before accepting a request.
5. Store immutable request details as structured data, including current/proposed values and reason.
6. Expose minimal API endpoints:
   - create request for an intake case
   - list requests for an intake case or project
   - get one request detail

Frontend:

1. No full management UI in this task.
2. If frontend is touched, keep it minimal:
   - show that frozen fields can be handled through a recorded revision request
   - do not add approval/apply actions
   - do not create a modal-first workflow

Documentation:

1. Record request status meanings.
2. Record that approval/apply and workbook/folder mutation are future tasks.
3. Update `docs/task_board.md` when implementation is approved and completed.

## Request Status Model

Use a deliberately small status set:

- `requested`: request is recorded and awaiting manual review.
- `cancelled`: request was withdrawn before approval.

Do not add `approved`, `rejected`, or `applied` in this task unless implementation discovery proves an existing status model already supports them cleanly. Approval/application is a later controlled task.

## Frozen Field Set

Use the authoritative frozen-field list from `IntakeCaseReviewService` rather than duplicating a second list.

Expected fields include:

- form number / revision metadata when stored in review data
- requestor and project identity fields
- product name
- sample rows
- requested testing rows
- setup confirmation values written to the LTR workbook

Implementation must discover the exact current field keys before coding and test against those actual keys.

## Out Of Scope

- No automatic edit to intake draft data.
- No external LTR workbook update.
- No folder rename.
- No project identity rewrite.
- No approval workflow.
- No full revision management UI.
- No Matrix, Report, AI review, LAN deployment, permissions, Outlook auto-scan, or email sending.

## Proposed Backend Design

Preferred model:

```text
FrozenFieldRevisionRequest
  request_id
  intake_case_id
  project_id nullable
  ltr_record_id nullable
  ltr_number nullable
  status
  requested_by nullable
  reason
  field_changes_json
  created_at
  updated_at
```

Each `field_changes_json` item should contain:

```text
field_key
field_label nullable
current_value
proposed_value
```

Keep values JSON-serializable. For sample/requested-testing rows, store the relevant row/list snapshot rather than inventing per-cell child tables in this task.

## Proposed API Design

Minimal endpoints:

```text
POST /api/intake-cases/{case_id}/frozen-field-revision-requests
GET  /api/intake-cases/{case_id}/frozen-field-revision-requests
GET  /api/frozen-field-revision-requests/{request_id}
```

Request body:

```json
{
  "reason": "Correct product name after customer clarification.",
  "requested_by": "White",
  "changes": [
    {
      "field_key": "product_name",
      "proposed_value": "Updated connector name"
    }
  ]
}
```

Response should include the stored current-value snapshot from the backend, not trust the client for current values.

## Validation Rules

- Reject unknown field keys.
- Reject non-frozen field keys.
- Reject requests for an intake case that is not frozen by registered LTR state.
- Reject empty changes.
- Reject blank reason.
- Allow multiple requested fields in one request.
- Do not mutate the original intake case fields.

## Proposed File-Level Changes

Likely backend files:

1. `backend/domain/enums.py`
   - add a narrow request status enum if no suitable enum exists
2. `backend/domain/models.py`
   - add domain dataclass for frozen-field revision request
3. `backend/infrastructure/storage/models.py`
   - add SQLAlchemy row model
4. `backend/infrastructure/storage/repositories/frozen_field_revision_request.py`
   - create/list/get repository
5. `backend/application/frozen_field_revision_request_service.py`
   - validation and orchestration
6. `backend/api/routes_intake_review.py` or a new narrow route module
   - typed Pydantic request/response DTOs
7. `backend/api/dependencies.py`
   - service wiring

Likely frontend files, only if needed for a minimal affordance:

1. `frontend/src/api/client.ts`
   - typed request/response functions
2. `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
   - optional concise frozen-state request entry point, if approved during implementation discovery

Likely tests:

1. `tests/unit/test_frozen_field_revision_request_service.py`
2. `tests/integration/test_frozen_field_revision_request_api.py`
3. `tests/unit/test_frontend_shell_files.py` only if frontend API/affordance is added

## UI Design Constraints

Using `$impeccable` product register if any frontend is touched:

- Keep the frozen notice operational and quiet.
- Prefer inline/progressive request capture over modal-first interaction.
- Do not introduce a new page unless backend-only request recording proves insufficient for operator workflow.
- Do not add future approval/apply buttons.
- Copy must avoid backend terms such as raw route names or database status names.

## Acceptance Criteria

- Normal frozen base-field edits remain blocked after LTR registration.
- A frozen intake case can create a revision request for allowed frozen fields.
- The stored request captures current values from backend state and proposed values from the operator request.
- Requests are persisted and can be listed/read through typed API responses.
- Invalid field keys, non-frozen fields, non-frozen cases, empty changes, and blank reasons are rejected.
- No request creation mutates intake case data, project identity, LTR workbook, or project folder.
- No future-scope modules are surfaced.

## Validation Plan

Required after implementation:

```powershell
py -m pytest tests\unit\test_frozen_field_revision_request_service.py -q
py -m pytest tests\integration\test_frozen_field_revision_request_api.py -q
py -m pytest tests\unit\test_intake_case_review_service.py -q
```

If frontend is touched:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
npm run build
```

Final verification:

```powershell
py -m pytest tests\unit tests\integration -q
git diff --check
```

Expected result:

- targeted service/API tests pass
- existing frozen-edit tests keep passing
- full backend suite stays green
- frontend build passes only if frontend files changed
- `git diff --check` passes, with only known LF/CRLF working-copy warnings if present

## Risks And Mitigations

Risk: this turns into an approval workflow.

- Mitigation: only `requested` and `cancelled` status in this task.

Risk: request data diverges from current backend frozen-field rules.

- Mitigation: reuse `IntakeCaseReviewService` frozen-state/frozen-field logic instead of duplicating rules.

Risk: large row-level sample changes are hard to represent.

- Mitigation: store JSON snapshots for complex values in this first record task; normalize later only if the review/apply workflow needs it.

Risk: UI work expands into revision management.

- Mitigation: backend/API foundation first; frontend is optional and limited to a small request affordance if needed.

## Approval Gate

After user explicitly approves this plan, Step 2 implementation may start.
