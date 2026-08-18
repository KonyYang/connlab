# TASK_309 Fee Confirm UI And Stale Guard Plan

> For agentic workers: REQUIRED SUB-SKILL: Use test-driven development when implementing this plan.

Status: Implemented and validated.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_309_FEE_CONFIRM_UI_AND_STALE_GUARD` complete.

Allowed reason: `docs/task_board.md` says TASK_309 was the current approved task. The implementation is complete; TASK_310 remains blocked until a separate task file, executable plan, and explicit approval exist.

## Goal

Add an operator-facing Confirm Fee action and status to the existing Fee Evaluation page.

The page must confirm the current visible Fee Evaluation values by saving them as a pricing draft first, then confirming the saved draft id through the TASK_308 Confirmed Fee API.

## Architecture

TASK_309 is a narrow frontend/API-integration task with one small backend response contract extension. It reuses the existing Fee Evaluation page state, existing pricing draft save endpoint, and existing Confirmed Fee authority endpoint. It does not create a new route, does not alter Excel export, and does not create package outputs.

## Mandatory Preconditions

Before implementation:

1. Read `AGENTS.md`.
2. Read `docs/task_board.md`.
3. Read `tasks/TASK_309_FEE_CONFIRM_UI_AND_STALE_GUARD.md`.
4. Load `$impeccable`.
5. Read `docs/02_ARCHITECTURE_RULES.md`.
6. Read `docs/frontend_architecture_rules.md`.
7. Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
8. Re-read this executable plan.
9. Confirm explicit user approval for implementation.

## Current Code Context

Relevant frontend files:

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
  - loads Fee Evaluation draft
  - hydrates saved pricing draft
  - tracks local preview edits and cost summary values
  - saves pricing drafts through `saveFeeEvaluationPricingDraft(...)`
  - downloads Fee Form through `generateConfirmedMatrixFeeFileDownload(...)`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
  - renders page header controls, totals cards, editable table, Save changes, and Fee Form buttons
- `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts`
  - builds rows, payloads, totals, and hydration helpers
- `frontend/src/api/client.ts`
  - already has Fee Evaluation draft/export/pricing-draft functions
  - does not yet expose Confirmed Fee client functions

Relevant backend files:

- `backend/api/routes_confirmed_fee_version.py`
  - already exposes Confirmed Fee GET/POST endpoints
  - POST requires `confirmed_by`, `expected_pricing_draft_edit_id`, and `summary`
- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`
  - returns saved pricing draft data but currently does not expose `draft_edit_id` to the frontend response
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py`
  - saved snapshot already has `draft_edit_id`

## V1 Contract

`Confirm Fee` click flow:

1. Build the same edited-values payload used by Save changes and Fee Form.
2. Save the payload with `saveFeeEvaluationPricingDraft(projectId, payload)`.
3. Require the save response to contain `saved_draft_edit_id`.
4. Build an all-project Confirmed Fee summary from the full preview rows and summary values:
   - `testing_fee_total`
   - `working_hours`
   - `lab_manpower_cost`
   - `external_cost`
   - `grand_cost`
5. Call `confirmFeeVersion(projectId, { confirmed_by, expected_pricing_draft_edit_id, summary })`.
6. Refresh latest Confirmed Fee status after success.

The selected group filter affects the visible table and selected group fee display only. It must not affect Confirm Fee summary totals.

## File-Level Design

### Backend API Response Extension

Modify `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py`:

- Add `saved_draft_edit_id: str | None = None` to `FeeEvaluationPricingDraftResponse`.
- Populate it from `snapshot.draft_edit_id` when a saved snapshot exists.
- Keep existing response fields unchanged.

Test:

- Update `tests/integration/test_fee_evaluation_pricing_draft_api.py` or the existing pricing-draft API test to assert the save response includes `saved_draft_edit_id`.

Reason:

- TASK_308 Confirmed Fee authority requires `expected_pricing_draft_edit_id`.
- The frontend cannot safely confirm the current saved pricing draft without this id.

### Frontend API Client

Modify `frontend/src/api/client.ts`:

- Extend `FeeEvaluationPricingDraftResponse` with `saved_draft_edit_id?: string | null`.
- Add types:
  - `ConfirmedFeeStatus = "missing" | "current" | "stale"`
  - `ConfirmedFeeSummary`
  - `ConfirmedFeeVersion`
  - `ConfirmedFeeLatestResponse`
  - `ConfirmFeeVersionRequest`
- Add functions:
  - `getConfirmedFeeLatest(projectId: string): Promise<ConfirmedFeeLatestResponse>`
  - `confirmFeeVersion(projectId: string, input: ConfirmFeeVersionRequest): Promise<ConfirmedFeeLatestResponse>`

Contract:

```ts
export type ConfirmedFeeSummary = {
  testing_fee_total: string;
  working_hours: string;
  lab_manpower_cost: string;
  external_cost: string;
  grand_cost: string;
};

export type ConfirmFeeVersionRequest = {
  confirmed_by: string;
  expected_pricing_draft_edit_id: string;
  summary: ConfirmedFeeSummary;
  confirmation_note?: string | null;
};
```

### Fee Evaluation Page State

Modify `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`:

- Import new Confirmed Fee client functions/types.
- Add state:
  - `confirmedFeeState`
  - `confirmedBy`
  - `confirmFeeActionState`
  - `latestSavedPricingDraftId`
  - `pricingDraftDirtySinceConfirm`
- Load latest Confirmed Fee in page context load or in a dedicated effect after the Fee draft loads.
- Default `confirmedBy` to the existing operator label if available; otherwise `Lab User`.
- Track latest saved pricing draft id from both `getFeeEvaluationPricingDraft(...)` and `saveFeeEvaluationPricingDraft(...)` responses.
- Track local dirty status using existing edit/cost state updates. If local edits exist after a confirmed status, display `Unconfirmed local changes`.
- Derive `Unconfirmed saved changes` when latest saved pricing draft id exists and differs from latest Confirmed Fee `pricing_draft_edit_id`.
- Add `handleConfirmFee`:
  1. block blank confirmer
  2. build current edited-values payload
  3. save pricing draft
  4. require `saved_draft_edit_id`; if absent, stop and show `Save returned no pricing draft id. Refresh and save again before confirming.`
  5. build all-group summary from full `previewRows` and summary values
  6. call `confirmFeeVersion`
  7. update latest saved pricing draft id from the save response
  8. update Confirmed Fee status and clear local dirty indicator

Important:

- Do not use `visiblePreviewRows` or `scopedPreviewRows` for confirmation totals.
- Do not call Fee Form download.
- Do not create a ProjectOutputRecord.

### Fee Evaluation Preview Table UI

Modify `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`:

- Add compact Confirm Fee props:
  - `confirmedFeeStatusLabel`
  - `confirmedFeeStatusTone`
  - `confirmedFeeDetail`
  - `confirmedBy`
  - `confirmFeeDisabledReason`
  - `confirmFeeBusy`
  - `confirmFeeError`
  - `onConfirmedByChange`
  - `onConfirmFee`
- Render a compact control near `Save changes` and `Fee Form`:
  - small status text/chip
  - `Confirmed by` input
  - `Confirm Fee` button
- Keep the layout dense and operator-focused.
- Do not introduce a large new management card.
- At 14-inch workstation width, the Confirm Fee controls must not cause header controls to overflow horizontally or button text to wrap. If the header row becomes crowded, place Confirm Fee on a second compact action strip directly above the totals cards instead of forcing it into the same row as `Back to Workbench`, group selection, Save changes, and Fee Form.

Suggested copy:

- Missing: `Not confirmed`
- Current: `Confirmed`
- Stale: `Confirmed fee stale`
- Local dirty: `Unconfirmed local changes`
- Saving/confirming: `Saving and confirming...`
- Error if blank: `Enter confirmed by before confirming.`
- Error if stale draft: `Save current Fee Evaluation pricing, then confirm again.`

### Preview Model Helpers

Modify `frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts` only if it keeps the page component smaller:

- Add a helper to build Confirmed Fee summary from full rows and cost values:
  - Use full `previewRows`
  - Use current `conditionConfirmationSpendTime`
  - Use current `externalCost`
  - Use current `labManpowerHourlyRate`
  - Return string totals matching backend request fields

Do not add backend pricing logic here; this is only the same UI calculation already shown on the page.

## Stale And Dirty Rules

Backend status:

- `missing`: no Confirmed Fee record exists
- `current`: latest Confirmed Fee binding matches current Matrix id/revision and fee rule version
- `stale`: latest Confirmed Fee exists but binding no longer matches current Matrix/rule version

Frontend overlay status:

- If backend is `current` but local page edits or summary edits changed after confirmation, show `Unconfirmed local changes`.
- If a saved pricing draft exists and its `saved_draft_edit_id` differs from latest confirmed fee `pricing_draft_edit_id`, show `Unconfirmed saved changes`.
- If backend is `stale`, show stale even if local edits are clean.

## Testing Plan

### Frontend API Client / Shell Tests

Update `tests/unit/test_frontend_shell_files.py`:

- Assert `client.ts` exports Confirmed Fee request/response types.
- Assert `client.ts` includes:
  - `/api/projects/${projectId}/confirmed-fee/latest`
  - `/api/projects/${projectId}/confirmed-fee/versions`
- Assert pricing draft response includes `saved_draft_edit_id`.

### Fee Evaluation Page Tests

Update `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`:

- Mock new API functions:
  - `getConfirmedFeeLatest`
  - `confirmFeeVersion`
- Add tests:
  1. Missing Confirmed Fee renders `Not confirmed`.
  2. Current Confirmed Fee renders confirmed revision/metadata.
  3. Stale Confirmed Fee renders stale warning text.
  4. Clicking `Confirm Fee` saves current edits first, then calls Confirmed Fee API with returned `saved_draft_edit_id`.
  5. Confirmation summary uses all-group totals even when the preview group filter is set to one group.
  6. Editing a row after a current confirmation shows `Unconfirmed local changes`.
  7. Blank confirmed-by blocks Confirm Fee and does not call save/confirm APIs.
  8. Save failure or Confirm Fee failure displays inline actionable error.
  9. Loaded/saved pricing draft id different from latest confirmed fee `pricing_draft_edit_id` shows `Unconfirmed saved changes`.
  10. Save returns `status: "current"` but `saved_draft_edit_id: null`; `confirmFeeVersion` is not called and the page shows an actionable save/refresh error.

### Backend API Regression

Update `tests/integration/test_fee_evaluation_pricing_draft_api.py`:

- Assert save/load response contains `saved_draft_edit_id` for current saved draft.

Existing TASK_308 Confirmed Fee backend tests should remain unchanged unless response type alignment requires small fixture updates.

## Validation Commands

Run:

```powershell
npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
npm run build
py -m pytest tests/integration/test_fee_evaluation_pricing_draft_api.py tests/integration/test_confirmed_fee_version_api.py tests/unit/test_confirmed_fee_version_service.py -q
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Expected:

- All focused tests pass.
- `git diff --check` passes, allowing only existing CRLF warnings if they appear.

## Risks And Controls

- Risk: Confirming stale UI values.
  - Control: Confirm Fee always saves the current visible payload first and confirms the returned saved draft id.
- Risk: Confirming selected group totals instead of full fee.
  - Control: Confirmation summary is built from full preview rows, not filtered visible rows.
- Risk: UI suggests Fee Form was generated.
  - Control: Copy says Confirm Fee is an approval/status action only; Fee Form remains the Excel download action.
- Risk: Confirmed Fee appears current after unsaved local changes.
  - Control: local dirty state overrides backend current status with `Unconfirmed local changes`.

## Documentation Updates After Implementation

After implementation only:

- Update `tasks/TASK_309_FEE_CONFIRM_UI_AND_STALE_GUARD.md` to `Status: Complete`.
- Update `docs/task_board.md` with validation results and next recommended task.
- Update `docs/task_306_313_project_package_execution_series_plan.md` to mark TASK_309 complete.

## Stop Point

Stop after TASK_309 validation. Do not implement TASK_310 in the same turn.
