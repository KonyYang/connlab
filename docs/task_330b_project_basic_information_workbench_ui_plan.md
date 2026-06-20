# TASK_330B Project Basic Information Workbench UI Plan

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Current Active Task

`TASK_330B_PROJECT_BASIC_INFORMATION_WORKBENCH_UI` planning only.

## Why This Task Is Allowed

`TASK_330A_PROJECT_BASIC_INFORMATION_AUTHORITY_DATA_API` is complete and validated, including review follow-up. `TASK_330B` is the next split task in the approved Project Basic Information authority sequence and consumes only the 330A backend API. Implementation still requires explicit user approval after this plan review.

## Goal

Add the operator-facing Basic Information UI without changing backend authority semantics or formal file outputs:

- Workbench top action: `Basic Information`, placed between `Fee Evaluation` and project-folder action.
- Dedicated `/projects/{project_id}/basic-information` edit work area.
- Draft save and confirm flows consuming 330A APIs.
- Read-only Workbench summary card with a `View` expansion.

## Product/UI Posture

ConnLab is a product UI for lab engineers on Windows workstations. The screen should feel like a dense operational form, not a landing page or decorative dashboard.

Design rules for 330B:

- Keep the top action row compact: `Matrix Editor | Fee Evaluation | Basic Information | Generate/Update project folder`.
- Use business-readable labels from the user's provided reference list.
- Show state before action: unconfirmed, confirmed, needs review, missing required fields.
- Do not duplicate DL Number, Product, or Test Item in the Workbench summary card because the top project identity already shows them.
- The summary card is read-only; no inline editing, no `Edit` shortcut.
- Use `View` only to expand all confirmed Basic Information fields read-only.
- Keep errors visible only when there is an actual load/save/confirm problem.

## Scope

### In Scope

- Frontend API client DTOs and functions for the 330A API.
- App route parsing and navigation for `/projects/{project_id}/basic-information`.
- Dedicated Basic Information page/work area.
- Feature-level hook/model for load, draft edit, save draft, confirm, cancel.
- Grouped field config and rendering.
- Workbench top `Basic Information` button.
- Workbench read-only Project Basic Information summary card.
- Frontend unit tests, static shell tests, and build verification.

### Out Of Scope

- No backend model/API changes unless a frontend integration bug reveals a 330A contract defect.
- No project folder blocker.
- No project folder output refresh.
- No Excel/Word/Office writes.
- No LTR workbook writeback.
- No report generation.
- No Matrix/Fee source provider additions.
- No 330C output consumption.

## Existing API Contract From 330A

Frontend consumes:

```text
GET  /api/projects/{project_id}/basic-information
PUT  /api/projects/{project_id}/basic-information/draft
POST /api/projects/{project_id}/basic-information/confirm
```

Core response fields:

- `project_id`
- `status`: `unconfirmed | confirmed | needs_review`
- `draft.values`
- `latest_confirmed`
- `field_suggestions`
- `changed_source_fields`
- `missing_required_fields`
- `missing_required_labels`
- `blockers`
- `warnings`

Frontend must treat the API as authoritative. It may display and edit values, but it must not invent confirmation rules beyond the returned missing fields and API errors.

## UX Flow

### Workbench Entry

1. User opens active Matrix Workbench.
2. Top action row shows `Basic Information` after `Fee Evaluation`.
3. Clicking it navigates to `/projects/{project_id}/basic-information`.

### Basic Information Page

1. Page loads 330A GET.
2. If loading, render quiet work area shell, not a large copy block.
3. If load fails, show a compact error with retry.
4. Render grouped editable fields using `draft.values`.
5. Show missing required field labels if present.
6. Show changed source fields when `status === "needs_review"`, using source suggestions as review context.
7. `Save Draft` calls PUT and stays on the page.
8. `Confirm` calls POST. On success, update the page model to the returned confirmed response, then navigate back to Workbench with a refresh signal so the Workbench summary card reloads Basic Information state.
9. `Cancel` navigates back to Workbench without save/confirm.

### Workbench Summary Card

1. Load Basic Information through `useProjectWorkbenchModel` or a thin support hook.
2. Render a `Project Basic Information` card in the right/supporting action area where folder/action support cards live.
3. Do not show DL Number, Product, or Test Item.
4. Show compact business summary from confirmed values where available:
   - Project Type
   - Requested By
   - Project Leader
   - Lab Performing the Tests
   - Test Result
   - Sub-contract
   - Test Fee
5. If no confirmed snapshot exists, show an unconfirmed state with missing labels, but no edit button.
6. If `needs_review`, show a review-needed status label and changed field count.
7. `View` expands the card to display all confirmed values read-only.
8. The card is not an edit entry point. For unconfirmed or needs-review states, copy should point operators to the top `Basic Information` button, for example `Confirm from Basic Information`.

### Confirm Feedback Contract

Confirm success must be visible after navigation:

- The Basic Information page must use the POST response to set local status to `confirmed` before leaving.
- Workbench navigation must trigger a Basic Information reload, for example by returning to `/projects/{project_id}?basicInformation=confirmed` or by using an equivalent route/state refresh signal.
- The Workbench summary card must render the fresh confirmed status and confirmed values after return.
- No generic success banner is required if the summary card visibly updates to confirmed. Error messages still render only on real load/save/confirm failures.

## Field Set

Use a field config owned by the Basic Information feature. Initial TASK_330B fields:

```text
project_type
description_pn
test_item
applicable_specifications
test_type
requested_by
location
project_leader
test_result
failed_item
sample_deposition
sub_contract
test_fee
remarks_po
phone
requestor_email
product_description
lab_performing_tests
condition_of_samples_when_received
date_lab_received_samples
estimated_completion_date
start_test_date
finish_test_date
report_date
```

Notes:

- `dl_number` must always be included in the editor model and confirm payload. Display it as a compact read-only meta field sourced from `draft.values` or backend API state. Do not show it in the Workbench summary card because the top project identity already carries it.
- `test_fee` is editable in 330B as Basic Information data, but it does not synchronize from Fee authority until a later source-provider task.
- Date fields are simple text/date inputs in TASK_330B; no Matrix/Fee provider semantics are added.

## Frontend File Plan

### API

Modify `frontend/src/api/client.ts`:

- Add types:
  - `ProjectBasicInformationStatus`
  - `ProjectBasicInformationRecord`
  - `ProjectBasicInformationDraft`
  - `ProjectBasicInformationFieldSuggestion`
  - `ProjectBasicInformationResponse`
  - `ProjectBasicInformationDraftRequest`
  - `ProjectBasicInformationConfirmRequest`
- Add functions:
  - `getProjectBasicInformation(projectId: string): Promise<ProjectBasicInformationResponse>`
  - `saveProjectBasicInformationDraft(projectId: string, values: Record<string, string>): Promise<ProjectBasicInformationResponse>`
  - `confirmProjectBasicInformation(projectId: string, values: Record<string, string>, confirmedBy: string): Promise<ProjectBasicInformationResponse>`

### Route/Page

Modify `frontend/src/App.tsx`:

- Add route name `projectBasicInformation`.
- Parse `/projects/:projectId/basic-information`.
- Treat it as active Workbench route.
- Navigate from Workbench top action.
- Render `ProjectBasicInformationPage`.
- Keep `topBarTitle` quiet/consistent, likely `Basic Information`.

Create `frontend/src/pages/ProjectBasicInformationPage.tsx`:

- Page boundary only.
- Calls feature hook and renders feature layout.
- Receives `projectId` and `onBackToWorkbench`.

### Feature

Create folder `frontend/src/features/project-basic-information/`.

Create `basicInformationFieldConfig.ts`:

- Defines field groups and labels.
- Marks required display fields:
  - `dl_number`
  - `project_type`
  - `product_description` or `description_pn`
  - `test_item`
  - `requested_by`
  - `project_leader`
  - `lab_performing_tests`

Create `basicInformationSelectors.ts`:

- `selectBasicInformationStatusLabel(response)`
- `selectBasicInformationMissingLabels(response)`
- `selectChangedSourceFieldLabels(response)`
- `selectWorkbenchSummaryItems(response)`
- `selectConfirmedViewItems(response)`

Create `useProjectBasicInformationModel.ts`:

- Owns load/save/confirm state.
- Keeps local editable `values`.
- Resets local values after successful GET/PUT.
- Confirm uses a single user display source for `confirmed_by`. If the existing app/user display model is not available in the feature boundary, introduce one small shared fallback helper/constant and use `"Lab User"` only there. Do not hard-code `"Lab User"` in multiple feature files.
- Confirm success stores the returned confirmed response before triggering Workbench navigation/refresh.

Create `ProjectBasicInformationWorkspace.tsx`:

- Renders dedicated editor page.
- Uses grouped fields and compact status strip.
- Buttons:
  - `Cancel`
  - `Save Draft`
  - `Confirm`
- Displays API errors as alerts.

Create `ProjectBasicInformationSummaryCard.tsx`:

- Read-only card for Workbench.
- Props accept `response`, `loading`, `error`.
- `View` toggles expanded confirmed values.
- Does not expose an edit entry.

Create `ProjectBasicInformationWorkspace.test.tsx` and `ProjectBasicInformationSummaryCard.test.tsx`.

### Workbench Integration

Modify `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`:

- Load `ProjectBasicInformationResponse`.
- Add model fields:
  - `basicInformation`
  - `basicInformationLoading`
  - `basicInformationError`
- Keep this read-only in Workbench.

Modify `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`:

- Add prop callback `onOpenBasicInformation`.
- Insert top action button between `Fee Evaluation` and folder action.
- Pass Basic Information state to summary card.

Modify `frontend/src/pages/ProjectWorkbenchPage.tsx`:

- Accept `onOpenBasicInformation`.
- Pass it to layout.

Modify active/supporting Workbench component only as needed to place the summary card without creating nested cards.

### Styling

Modify `frontend/src/workbench.css` or add a focused CSS file imported by the page if the current app pattern supports it.

Rules:

- Use existing ConnLab tokens/classes where possible.
- Buttons match current Workbench command button style.
- Form fields use compact rows, not oversized marketing cards.
- No gradient text, no side-stripe cards, no decorative blobs.
- Summary card must stay compact and not crowd the Matrix projection.

## Test Plan

### Frontend Unit Tests

Add/extend tests:

- `ProjectWorkbenchLayout.test.tsx`
  - top action order includes `Matrix Editor`, `Fee Evaluation`, `Basic Information`, project folder button.
  - clicking `Basic Information` calls `onOpenBasicInformation`.
  - summary card renders confirmed values without DL Number/Product/Test Item.
  - summary card can expand with `View`.

- `ProjectBasicInformationWorkspace.test.tsx`
  - loads draft values from mocked API.
  - edits a value and calls save draft.
  - confirm sends values and `confirmed_by`.
  - confirm payload includes `dl_number` from the read-only meta field.
  - confirm success calls `onBackToWorkbench`.
  - cancel calls `onBackToWorkbench` without API mutation.
  - missing required labels display.
  - `needs_review` displays changed field hints.

- `ProjectBasicInformationSummaryCard.test.tsx`
  - unconfirmed state displays missing labels.
  - unconfirmed copy points to the top `Basic Information` button, not an inline edit action.
  - confirmed state displays compact summary only.
  - needs-review state displays review-needed status.

### Static Boundary Tests

Update `tests/unit/test_frontend_shell_files.py`:

- Assert Basic Information route exists.
- Assert no direct `fetch(` in new feature/page files.
- Assert Workbench action label exists.

### Build

Run:

```powershell
cd frontend
npm test -- --run ProjectWorkbenchLayout ProjectBasicInformation --watch=false
npm run build
```

Run:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task330 or basic_information or project_workbench"
```

### Manual Smoke

Preferred smoke uses a temporary/test project to avoid creating confirmed Basic Information versions on business data.

1. Open a temporary/test project Workbench.
2. Confirm top action order includes `Basic Information`.
3. Click `Basic Information`.
4. Confirm URL is `/projects/{project_id}/basic-information`.
5. Verify the read-only `DL/LTR Number` meta field is present and the payload will retain it.
6. Edit a non-critical field and click `Save Draft`.
7. Fill required fields if needed and click `Confirm`.
8. Confirm return to Workbench.
9. Confirm the Workbench summary card now shows confirmed state and fresh values.
10. Inspect `View` expansion.

If smoke must use real project `72fbbfa290294da9a507344b68ff900f`, do not click `Confirm` unless the user explicitly accepts that it will create a real Basic Information confirmed version. Save Draft only is safe for non-authority smoke.

## Risks And Controls

- Risk: Workbench model is already large. Control: add only read-only Basic Information state in 330B; keep editor state in `features/project-basic-information`.
- Risk: Summary card could become another edit surface. Control: no inline inputs and no edit button.
- Risk: 330B could accidentally imply outputs use Basic Information. Control: UI copy must not say generated forms/reports already consume this snapshot; that is 330C.
- Risk: Date fields may need richer picker behavior. Control: simple controlled text/date inputs only; source-provider semantics are later.
- Risk: user identity is not yet authoritative. Control: use current local display fallback for `confirmed_by`, keep it as API payload detail only.

## Review Checklist

- Scope does not include backend persistence changes.
- Scope does not include Office/file output generation.
- UI reads 330A API state instead of duplicating business rules.
- Workbench card is summary-only.
- Basic Information page owns editing.
- No direct `fetch()` outside API client.

## Approval Gate

This plan and `tasks/TASK_330B_PROJECT_BASIC_INFORMATION_WORKBENCH_UI.md` are ready for review. Do not implement TASK_330B until the user explicitly approves.
