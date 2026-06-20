# TASK_330B_PROJECT_BASIC_INFORMATION_WORKBENCH_UI

## Status

Plan ready for user review. Implementation not started.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Why This Task Is Allowed

TASK_330A is complete and provides the backend Project Basic Information authority API. TASK_330B is the next split task and only consumes the 330A API in the frontend. It is not authorized for implementation until the user explicitly approves this task.

## Plan

Detailed implementation plan:

- `docs/task_330b_project_basic_information_workbench_ui_plan.md`

## Goal

Add the operator-facing Basic Information workflow:

- top Workbench `Basic Information` action,
- dedicated editable page/work area,
- save draft and confirm actions,
- read-only Workbench summary card with optional `View` expansion.

## User-Facing Shape

Workbench top action order:

```text
Matrix Editor | Fee Evaluation | Basic Information | Generate/Update project folder
```

The Workbench `Project Basic Information` card:

- summary-only,
- no edit fields,
- no duplicate DL Number / Product / Test Item,
- no `Edit` action,
- optional `View` expansion for all confirmed fields, read-only.

## In Scope

- Frontend API client types/functions for TASK_330A routes.
- Route/page for `/projects/{project_id}/basic-information`.
- Basic Information grouped edit form.
- Save draft action.
- Confirm action.
- Cancel/confirm return behavior to Workbench.
- Workbench top action button.
- Workbench read-only summary card and optional View expansion.
- Frontend unit/static tests and build verification.

## Out Of Scope

- No backend persistence changes beyond consuming TASK_330A APIs.
- No project folder blocker.
- No formal output file refresh.
- No Office access.
- No LTR workbook writeback.
- No report generation.
- No Matrix/Fee source provider additions.
- No TASK_330C output consumption.

## Required UI Behavior

- Workbench shows `Basic Information` between `Fee Evaluation` and the project folder button.
- Clicking `Basic Information` opens `/projects/{project_id}/basic-information`.
- The Basic Information page loads draft, confirmed, missing-field, and needs-review state from backend.
- Operator can edit draft values and click `Save Draft`.
- Operator can click `Confirm` to create a backend confirmed version.
- Confirm success updates local state from the POST response, returns to Workbench, and triggers Workbench Basic Information refresh.
- Cancel returns to Workbench without confirming.
- Save Draft stays on the Basic Information page.
- Missing required labels are shown from backend response/errors.
- Needs-review state uses backend `changed_source_fields` and `field_suggestions`.
- Workbench summary card is read-only and does not duplicate top project identity.
- Summary card is not an edit entry point; unconfirmed/needs-review copy points operators to the top `Basic Information` button.
- `View` expansion displays all confirmed Basic Information fields as read-only.
- No direct `fetch()` outside the frontend API boundary.

## Field Set

The editable page should include these configured fields:

- Project Type
- Description P/N
- Test Item
- Applicable Specifications
- Test Type
- Requested by
- Location
- Project Leader
- Test Result
- Failed item
- Sample deposition
- Sub-contract
- Test Fee
- Remarks (PO)
- Phone
- E-mail of Requestor
- Product Description
- Lab Performing the Tests
- Condition of Samples when Received
- Date Lab Received Samples
- Estimated Completion Date
- Start Test Date
- Finish Test Date
- Report Date

`DL/LTR Number` must always be included in the editor model and confirm payload. Display it as a compact read-only meta field in the Basic Information page. Do not show it in the Workbench summary because the project identity already shows it.

## Acceptance Criteria

- Workbench top action order is correct.
- Basic Information route opens a dedicated work area.
- Page consumes the 330A API through `frontend/src/api/client.ts`.
- Draft save persists operator edits through PUT.
- Confirm creates a confirmed version through POST, includes `DL/LTR Number` in the payload, returns to Workbench, and refreshes the Workbench summary card to confirmed state.
- Cancel returns to Workbench without API mutation.
- Workbench summary card is read-only and excludes DL Number/Product/Test Item.
- Workbench summary card has no `Edit` action.
- `View` expansion displays all confirmed fields read-only.
- No backend Office/file output behavior changes.

## Validation

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout ProjectBasicInformation --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task330 or basic_information or project_workbench"
```

Manual smoke:

Preferred smoke uses a temporary/test project to avoid creating confirmed Basic Information versions on business data.

1. Open a temporary/test project Workbench.
2. Click `Basic Information`.
3. Verify read-only `DL/LTR Number` is present.
4. Save draft.
5. Confirm.
6. Return to Workbench.
7. Confirm summary card shows confirmed state and fresh values.
8. Inspect summary card and `View` expansion.

If smoke must use real project `72fbbfa290294da9a507344b68ff900f`, do not click `Confirm` unless the user explicitly accepts that it will create a real Basic Information confirmed version. Save Draft only is safe for non-authority smoke.

## Stop Point

Stop after TASK_330B is implemented and validated. Do not start TASK_330C without explicit user approval.
