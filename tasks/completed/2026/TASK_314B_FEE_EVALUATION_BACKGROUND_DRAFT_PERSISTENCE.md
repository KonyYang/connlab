# TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE

Status: Complete. Implemented after separate explicit user approval.

Review follow-up: Complete. Exact-context pricing draft miss now returns `missing`
instead of blocking current defaults with an old-context `stale` status. Confirmed Fee
creation now validates the submitted summary against the saved pricing draft snapshot
before writing the authority version.

Executable plan: `docs/task_314b_fee_evaluation_background_draft_persistence_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_314B is the Fee Evaluation-only execution slice split out from `TASK_314_MATRIX_AND_FEE_BACKGROUND_DRAFT_PERSISTENCE`.

TASK_314B is not a prerequisite for `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE`. TASK_315 depends on TASK_314A Matrix Editor draft persistence, which is already complete. TASK_314B is now complete and should not automatically advance the project into TASK_314C or TASK_315 without separate approval.

## Goal

Implement Fee Evaluation pricing draft autosave and explicit discard behavior so Fee edits follow the same non-authority draft principle as Matrix Editor:

- Operator edits to the Fee Evaluation preview are autosaved in the background as a pricing draft.
- Fee Evaluation re-entry restores the current saved pricing draft for the active Confirmed Matrix and fee rule context.
- Normal flow no longer requires or exposes a manual `Save changes` button.
- `Back to Workbench` or explicit cancel/discard behavior must not silently preserve changes the operator intended to discard.
- `Confirm Fee` must be disabled while pricing edits are dirty, pending save, failed save, stale, or otherwise not tied to the latest saved pricing draft id.

The authority distinction must remain clear:

```text
autosaved Fee pricing draft = non-authority working copy
Confirmed Fee = authority version, created only by explicit Confirm Fee
```

## Current Code Reality

- Fee Evaluation page route is `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`.
- Fee Evaluation preview table is `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`.
- Fee pricing draft API already exists:
  - `GET /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
  - `PUT /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
- Backend route file is `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`.
- Backend application service is `backend/application/fee_evaluation_pricing_draft_persistence_service.py`.
- Backend repository is `backend/infrastructure/storage/repositories/fee_evaluation_pricing_draft_edit.py`.
- Existing frontend already loads saved pricing drafts and has a manual `Save changes` button.
- Existing `Confirm Fee` flow currently calls `saveFeeEvaluationPricingDraft(...)` immediately before `confirmFeeVersion(...)`.
- Existing Confirmed Fee authority service requires `expected_pricing_draft_edit_id` and checks the saved pricing draft.

## V1 Contract

### Pricing Draft Autosave

- Editing any Fee Evaluation pricing field marks the page dirty:
  - editable line row fields
  - manual trailing row fields
  - condition confirmation spend time
  - external cost
  - external cost note
  - lab manpower hourly rate
- After 800 ms debounce, the frontend saves the current pricing payload through the existing `PUT /pricing-draft` endpoint.
- Autosave must skip initial load and skip when the current payload signature matches the latest saved local signature.
- If `GET /pricing-draft` returns `status="missing"` and the current Fee defaults are otherwise ready, the frontend must perform one controlled background seed save for the default pricing payload. This seed save is not a hydration autosave and must be tracked separately so a new project with unchanged default Fee values can still reach `Confirm Fee`.
- Autosave response must update:
  - latest saved pricing draft id
  - saved draft context status
  - latest saved local payload signature
  - visible save status
- Late autosave responses after cancel/discard must be ignored.

### Pricing Draft Restore

- Existing `GET /pricing-draft` restore remains the source of truth.
- If backend returns `status="current"` with payload, frontend hydrates the saved pricing draft into the preview.
- If backend returns `status="missing"`, frontend shows current defaults and no saved draft token.
- If backend returns `status="stale"`, frontend must not apply stale payload to current preview.
- Stale saved pricing draft presence should be visible as an operational warning, but must not mutate current pricing fields.
- Backend restore must resolve the draft for the current Confirmed Matrix and fee-rule context, not simply the latest pricing draft row for the project.

### Manual Save Button Removal

- Remove `Save changes` from the normal Fee Evaluation action row.
- The operator should see save state text instead of a normal-flow manual save action:
  - `Saving pricing draft...`
  - `Saved pricing draft.`
  - `Save failed. Retry before confirming.`
  - `Saved pricing draft belongs to an older Matrix or fee rule version.`
- No hidden future feature or decorative UI should be introduced.
- A later approved task may add an explicit retry affordance if needed; V1 may retry automatically on the next edit or after debounce if the failed payload remains current.

### Confirm Fee Gate

- `Confirm Fee` must be disabled while:
  - Fee draft is loading
  - Confirmed Fee state is loading
  - `confirmed_by` is empty
  - pricing payload is dirty
  - autosave is pending or running
  - autosave failed
  - saved pricing draft is stale/missing for a changed payload
  - latest saved pricing draft id is missing after an attempted save
- `Confirm Fee` must send the latest saved `pricing_draft_edit_id` already produced by autosave.
- `Confirm Fee` must not perform an implicit save as part of confirmation for the normal current-context edit path.
- If no user-visible pricing edits were made and a current saved pricing draft is already loaded, `Confirm Fee` may proceed with that saved draft id.
- If no current saved pricing draft exists because pricing draft load returned `status="missing"`, `Confirm Fee` remains unavailable only until the controlled background seed save produces a saved draft id.
- If the seed save fails, `Confirm Fee` stays disabled and the operator sees the same actionable save-failed state used by normal autosave.

### Discard / Back To Workbench

- Fee Evaluation must provide an explicit discard path for current unsaved/saved local pricing draft edits before returning to Workbench.
- V1 may implement this as `Back to Workbench` prompting to discard when local changes or a current saved draft exists.
- Before calling discard, frontend must clear debounce timers, enter a cancelling/discarding state, and block new autosave scheduling.
- If autosave is already in flight, frontend must abort the request when possible and use a bounded wait of about 1.5 seconds before discard. Back/Discard must not hang forever on a request that never settles.
- Late autosave responses after abort/discard must be ignored by generation/state checks and must not recreate an accepted draft state.
- Backend discard must reject mismatched expected draft id/context tokens and must not delete Confirmed Fee authority.
- If discard fails, frontend must stay on Fee Evaluation and show an actionable error.

### Backend Discard Endpoint

Add a pricing draft discard endpoint:

```text
DELETE /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft
```

Request body:

```json
{
  "expected_pricing_draft_edit_id": "string | null",
  "expected_confirmed_matrix_id": "string | null",
  "expected_confirmed_revision": "number | null",
  "expected_fee_rule_version_id": "string | null"
}
```

Response body:

```json
{
  "discarded": true,
  "current_confirmed_matrix_id": "string",
  "current_confirmed_revision": 1,
  "current_fee_rule_version_id": "string"
}
```

Implementation note: FastAPI supports DELETE with request body in the current offline local app path. If future deployment introduces a proxy/client that drops DELETE bodies, convert this endpoint to `POST /pricing-draft/discard` in a separately approved compatibility task.

Backend discard must resolve and delete by the current Confirmed Matrix and fee-rule context, not by latest row for the project alone. If the same project has a newer stale pricing draft and an older current-context pricing draft, discard must still target the current-context row.

## In Scope

- Fee Evaluation pricing draft autosave in the frontend.
- Fee Evaluation pricing draft discard backend route/service/repository behavior.
- Typed frontend API client function for discard.
- Removal of normal-flow `Save changes` button from Fee Evaluation preview controls.
- Confirm Fee disabled-state rules tied to autosave and saved draft id.
- Focused backend and frontend tests for autosave, discard, restore, stale, and confirm gating.
- Static frontend shell guard updates for Fee Evaluation copy/contracts if required.
- Task board update after implementation approval, validation, and completion.

## Out Of Scope

- No Matrix Editor changes. TASK_314A is already complete.
- No Matrix Draft -> Fee Draft incremental rebase. That belongs to TASK_315.
- No fee row add/remove preservation across Matrix structural edits. That belongs to TASK_315.
- No Confirmed Fee authority schema rewrite.
- No Fee Evaluation calculation rule changes.
- No Excel workbook template changes.
- No Fee Form generation behavior changes.
- No ProjectOutputRecord changes.
- No Project Folder Required forms behavior changes.
- No TASK_314C regression-only execution unless separately approved.
- No StepInstance, execution persistence, evidence/image handling, report engine, AI review, permissions, LAN/server sync, or multi-user merge.

## Acceptance Criteria

- Fee Evaluation autosaves pricing edits after debounce.
- Fee Evaluation does not autosave during initial load.
- Fee Evaluation performs one controlled background seed save when pricing draft status is `missing` and default pricing payload is ready.
- Fee Evaluation does not repeatedly save unchanged payloads.
- Fee Evaluation re-entry restores current saved pricing draft.
- Fee Evaluation restore uses current context rather than latest-by-project when multiple context rows exist.
- Fee Evaluation does not apply stale pricing drafts to current Matrix/Fee-rule context.
- Fee Evaluation normal flow no longer shows `Save changes`.
- Confirm Fee is disabled while dirty, autosave pending, autosave running, autosave failed, stale, missing saved draft id, or confirmed-by is empty.
- Confirm Fee becomes available for a default unchanged Fee payload after the controlled seed save succeeds.
- Confirm Fee uses the latest autosaved `pricing_draft_edit_id`.
- Confirm Fee does not implicitly save a newer UI payload before confirming.
- Discard removes the current pricing draft for the current Confirmed Matrix/Fee-rule context.
- Discard still targets the current-context row when a newer stale row exists for the same project.
- Discard carries expected draft/context tokens when known.
- Discard rejects mismatched expected tokens.
- Discard aborts or bounded-waits in-flight autosave and does not hang indefinitely.
- Discard failure keeps the operator on Fee Evaluation with an actionable error.
- Discard never deletes Confirmed Fee authority.
- Existing Confirmed Fee version tests remain green.
- Existing Fee Evaluation file generation/download tests remain green.
- Existing TASK_318/TASK_320/TASK_321 Project Folder readiness behavior is not changed by TASK_314B.

## Required Validation

Backend:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Confirmed Fee authority:

```powershell
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
```

Frontend:

```powershell
cd frontend
npm test -- FeeEvaluationReviewExportPage
```

Build:

```powershell
cd frontend
npm run build
```

Recommended narrow shell guard:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee"
```

Recommended regression after implementation:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/unit/test_official_project_folder_check_service.py -q
```

## Stop Point

TASK_314B implementation is complete. Stop here after validation and task board update.

Do not proceed to TASK_314C, TASK_315, package execution, StepInstance, reporting, AI, permissions, or multi-user scope without separate explicit approval.
