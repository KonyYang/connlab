# TASK_315F Fee Current Version Cancel And Update Semantics Plan

Status: Complete.

**Goal:** Protect the Fee current working version that belongs to the current Matrix authority version, make `Cancel` discard only the current page session edits without deleting that Fee current version, and present the primary publish action as `Update Fee`.

**Architecture:** Keep the existing backend pricing draft and confirmed fee version services as the persistence/authority boundary. This task mainly changes frontend workflow semantics and copy, with backend changes only if a focused regression proves that current services cannot preserve the entry baseline safely.

**Tech Stack:** React + TypeScript frontend, FastAPI/Python backend if needed, Vitest/Testing Library, pytest.

---

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Active Task

`TASK_315F_FEE_CURRENT_VERSION_CANCEL_UPDATE_SEMANTICS`

## Why This Is Allowed

The user explicitly identified that Fee Evaluation `Cancel` currently clears the Fee form by deleting the pricing draft, and clarified the intended Matrix-bound Fee lifecycle: Matrix Confirm must have a corresponding Fee Evaluation current working version; Fee Evaluation edits pricing details only; `Cancel` should discard the current page session edits, while `Update Fee` should publish the current saved Fee pricing payload as a new Confirmed Fee authority revision. This is a narrow follow-up to the completed TASK_314/TASK_315 Fee lifecycle work and does not introduce future Matrix execution scope.

## Task Understanding

1. Goal: preserve the current Matrix-bound Fee working version across normal Cancel, and rename/clarify the authority update action.
2. Input data: current confirmed Matrix Fee draft, saved Fee pricing payload, page edit state, entry Matrix/Fee context, latest saved pricing draft id, autosave state, Confirmed Fee latest status.
3. Output data: durable current pricing payload, user-facing `Update Fee` action, Confirmed Fee authority version created from latest saved pricing payload.
4. Modules involved: Fee Evaluation React page/test, frontend API wiring/static guards, possibly Confirmed Fee copy tests and pricing draft persistence tests.
5. Not allowed: destructive reset UI, Fee history UI, hidden inactive-row UI, Matrix structure edits from Fee Evaluation, StepInstance/report/AI/permissions/LAN/multi-user scope.

## Current Implementation Summary

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx` imports `discardFeeEvaluationPricingDraft`.
- `handleBackToWorkbench()` prompts `Discard Fee Evaluation pricing edits and return to Workbench?`, aborts pending autosave, waits briefly for in-flight autosave, then calls `discardFeeEvaluationPricingDraft`.
- `backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py` exposes DELETE for pricing draft discard.
- `backend/application/fee_evaluation_pricing_draft_persistence_service.py` implements `discard()` by deleting the exact current pricing draft context.
- `handleConfirmFee()` calls `confirmFeeVersion()` and creates a `ConfirmedFeeVersion` authority revision from the latest saved pricing draft.

## Design Decision

Keep the backend DELETE endpoint available for now as an explicit internal/legacy reset capability, but remove it from the normal Fee Evaluation `Cancel` path. This avoids a broad API deletion or migration while fixing the user-facing destructive behavior.

The implementation must use an entry-baseline model with deterministic safety guards:

- Capture the loaded pricing payload signature, values, and Matrix/Fee context when Fee Evaluation enters ready state.
- On normal edits, keep existing autosave behavior.
- On `Cancel`, stop pending autosave but do not abort an already sent autosave.
- If no autosaved session change is known after entry, return to Workbench directly.
- If the current page state differs from entry baseline and restoring is needed, first verify the entry context still matches the current server Matrix/Fee context, then save the entry baseline payload back to the pricing draft with expected Matrix/Fee context tokens before returning.
- If an in-flight autosave cannot be confirmed complete, do not navigate away. Stay on Fee Evaluation and show a retry message.
- If the server context changed since entry, do not write the old baseline. Stay on Fee Evaluation and show a refresh message.
- If restore fails, remain on the page and show the error instead of deleting anything.

This preserves the user's intended meaning of Cancel even with background autosave.

## File-Level Plan

### 1. Frontend Cancel Semantics

Modify `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`.

- Remove `discardFeeEvaluationPricingDraft` from the normal page flow import/use.
- Replace `isDiscardingPricingDraft` / `discardingRef` semantics with cancel/restore naming.
- Track an entry baseline payload:

```ts
const baselinePricingPayloadRef =
  useRef<FeeEvaluationEditedFileExportRequest | null>(null);
```

- Track an entry baseline context:

```ts
const baselinePricingContextRef = useRef<PricingDraftContext | null>(null);
```

- Set the baseline payload and context when pricing draft load/hydration establishes the entry state.
- Update `handleBackToWorkbench()`:
  - if no local/session changes, call `onBackToWorkbench()`;
  - if changes exist, prompt with copy such as `Discard this Fee Evaluation page session and return to Workbench?`;
  - cancel pending autosave timers but do not abort an already sent autosave request;
  - wait on a bounded path that can determine the in-flight autosave finished;
  - if the in-flight autosave cannot be confirmed complete/safe, set an error such as `Fee Evaluation is still saving. Wait a moment and retry Cancel.` and stay on page;
  - reload or otherwise verify the current pricing draft context before restore;
  - if the current context differs from the entry context, set an error such as `Fee Evaluation context changed. Refresh before leaving.` and stay on page;
  - save the baseline payload back through `saveFeeEvaluationPricingDraft()` with expected Matrix/Fee context tokens when the page may have autosaved edits after entry;
  - call `onBackToWorkbench()` only after restore succeeds;
  - on failure, show `Unable to restore Fee Evaluation pricing before leaving.`

The restore save must happen after the autosave safety check, not concurrently with an unresolved save. The page must never race a baseline restore against an unknown in-flight autosave and then navigate away.

### 2. Update Fee Copy

Modify `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`.

- Rename visible action label:
  - `Confirm Fee` -> `Update Fee`
  - `Confirming...` -> `Updating...`
  - `Fee confirmed.` -> `Fee updated.`
  - `Unable to confirm Fee.` -> `Unable to update Fee.`
  - footer helper copy to `Update Fee returns to Workbench after authority is updated.`
- Keep API function name `confirmFeeVersion()` in this task unless a small alias improves readability without broad churn.

### 3. Frontend Regression Tests

Modify `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`.

- Replace button expectations from `Confirm Fee` to `Update Fee`.
- Add/adjust tests:
  - Cancel with loaded saved pricing draft navigates without calling `discardFeeEvaluationPricingDraft`.
  - Cancel after dirty edit with no completed autosave clears pending autosave, returns to Workbench, and leaves the saved baseline intact.
  - Cancel after completed autosave restores the entry baseline via `saveFeeEvaluationPricingDraft` before returning.
  - Cancel while an in-flight autosave cannot be confirmed safe stays on the Fee page and shows a retry error.
  - Cancel restore refuses to save an entry baseline when the current Matrix/Fee context changed and shows a refresh error.
  - Restore failure stays on the page and shows an error.
  - Reopen after Cancel loads the original baseline pricing content instead of an empty or dirty-edited form.
  - Update Fee still calls `confirmFeeVersion()` with latest saved draft id and summary.

### 4. Static Guard Updates

Modify `tests/unit/test_frontend_shell_files.py` only where existing static guards assert the old destructive discard wiring or old `Confirm Fee` copy.

- Remove or invert the guard requiring `discardFeeEvaluationPricingDraft` in the Fee Evaluation page.
- Add a guard that the Fee Evaluation page does not call `discardFeeEvaluationPricingDraft` in normal Cancel handling.
- Update expected user-facing copy to `Update Fee` where the test guards the Fee page.

### 5. Backend Verification

Backend implementation is limited to a narrow optimistic context guard on pricing draft save.

- `confirmed_fee_version_service.py` already creates immutable revisions from the saved pricing draft and strips inactive rows.
- `fee_evaluation_pricing_draft_persistence_service.py` already preserves hidden inactive rows during active-only saves.
- Pricing draft DELETE can remain available but unused by the normal page Cancel path.
- Pricing draft PUT accepts optional expected Matrix/Fee context tokens and rejects mismatches before writing with the existing conflict response shape.

No database schema changes are introduced.

### 6. Task Board And Task File

After implementation and validation:

- Mark `tasks/TASK_315F_FEE_CURRENT_VERSION_CANCEL_UPDATE_SEMANTICS.md` complete.
- Update `docs/task_board.md` with validation results and stop point.

## Data And API Design

No new persisted data structure is planned.

Existing API behavior retained:

- `GET /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
- `PUT /api/projects/{project_id}/confirmed-matrix/fee-evaluation/pricing-draft`
- `POST /api/projects/{project_id}/confirmed-fee/versions`

Existing DELETE stays in the API but should not be used by the Fee Evaluation page's normal `Cancel` action.

## Risks

- Background autosave can persist an edit before the operator clicks Cancel. The entry-baseline restore path must handle this, or Cancel would only navigate and leave autosaved edits behind.
- Aborting in-flight autosave is not sufficient proof that the server stopped processing it. Cancel must not abort an already sent autosave; restore can happen only after the in-flight save actually settles. If that cannot be confirmed, Cancel must stay on the page and ask the operator to retry.
- Baseline restore can corrupt state if the Matrix/Fee context changed after page entry. Restore must compare entry context with current server context before writing and must send expected context tokens so the backend rejects context changes between pre-check and PUT.
- Restoring the baseline must preserve server-side hidden inactive rows. This should already be handled by the pricing draft persistence service's inactive-row merge behavior from TASK_315E.
- Workbench and Project Folder copy may still say `Confirm Fee`; this task should update only copy that is directly misleading for the current user flow, avoiding a broad terminology rewrite.

## Validation Plan

Run after implementation:

```powershell
cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false
```

The Fee page test set must include:

- existing pricing draft + edit before autosave + Cancel + reopen baseline still present;
- existing pricing draft + completed autosave + Cancel restore + reopen baseline still present;
- unresolved in-flight autosave + Cancel stays on page with retry guidance;
- context mismatch during Cancel restore stays on page with refresh guidance;
- `discardFeeEvaluationPricingDraft` is not called by normal Cancel;
- Matrix soft-remove/reselect hidden-row recovery is not broken by baseline restore;
- Update Fee still creates or refreshes the Confirmed Fee authority revision from latest saved draft id.

Run if Workbench copy/static guards change:

```powershell
cd frontend; npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or task315"
```

Run if backend code changes:

```powershell
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Always run for frontend changes:

```powershell
cd frontend; npm run build
git diff --check
```

## Review Checklist

- Architecture: frontend remains inside feature/API boundaries; backend routes stay thin.
- Scope: only Fee Evaluation Cancel/Update Fee semantics and related tests/copy.
- Data: no new database schema, no Matrix structural edits from Fee page.
- UX: Cancel is no longer destructive; Update Fee communicates revision/update semantics.
- Tests: regression covers no DELETE call and successful authority update.
- Stop point: no reset UI, history UI, inactive-row UI, StepInstance, report, AI, permissions, LAN/server, or multi-user work.

## Completion Summary

TASK_315F is implemented. Fee Evaluation now treats the Matrix-bound pricing payload as the durable current Fee working version. Normal `Cancel` no longer deletes that payload. Session edits are cancelled by restoring the page entry baseline only after autosave safety and Matrix/Fee context checks pass. Unsafe in-flight autosave, context mismatch, or restore failure keeps the operator on the Fee page with actionable guidance. The visible authority action is now `Update Fee`, while the backend Confirmed Fee version creation service remains unchanged and continues to create active-only authority revisions.

Review follow-up implemented the stricter safety model: Cancel no longer aborts an already sent autosave, unresolved in-flight autosave keeps the user on the page, and the baseline restore PUT includes expected Matrix/Fee context tokens that the backend validates before writing.

Validation:

- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false` (`24 passed`, with existing non-failing React `act(...)` warnings)
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or task315"` (`9 passed, 137 deselected`)
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` (`25 passed`)
- `py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py tests/unit/test_confirmed_fee_version_service.py tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` (`61 passed`)
- `cd frontend; npm run build` passed
