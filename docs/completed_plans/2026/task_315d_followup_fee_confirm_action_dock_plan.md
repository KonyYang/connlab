# TASK_315D Follow-up Fee Confirm Action Dock Plan

Date: 2026-06-15

Status: Complete after explicit user approval on 2026-06-15.

Task file: `tasks/TASK_315D_FOLLOWUP_FEE_CONFIRM_ACTION_DOCK.md`

## Current Phase And Authorization

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current board state: `TASK_315D_FEE_UI_PROJECT_FOLDER_REGRESSION` is complete, and `TASK_315` is complete as a split sequence. This follow-up is not yet active implementation work.

This plan exists because the operator-facing Fee Evaluation page should match the Matrix Editor completion behavior: the final authority action belongs in a bottom-right completion dock, and successful confirmation should return the operator to Project Workbench.

## Goal

Move Fee Evaluation final actions into a Matrix Editor-style completion dock:

- `Cancel`
- `Confirm Fee`

After `Confirm Fee` succeeds, return to Workbench because the Fee authority version has been created/refreshed.

## Current Code Reality

Relevant existing code:

- `FeeEvaluationReviewExportPage.tsx`
  - Owns the Confirm Fee handler `handleConfirmFee()`.
  - Owns the existing cancel/back discard handler `handleBackToWorkbench()`.
  - Passes both handlers into `FeeEvaluationPreviewTable`.
- `FeeEvaluationPreviewTable.tsx`
  - Currently renders `Back to Workbench` in the header controls.
  - Currently renders Confirmed Fee status, `Confirmed by`, and `Confirm Fee` in `fee-evaluation-confirm-strip`.
- `workbench.css`
  - Matrix Editor already has `matrix-editor-completion-dock`.
  - Fee Evaluation currently has `fee-evaluation-confirm-strip` but no bottom completion dock.

No backend change is required.

## Design

### UI Layout

Keep Fee Evaluation dense and operational:

- Header remains for page identity, group filter, total fee, and Fee Form generation.
- Confirmed Fee status and `Confirmed by` input remain near the top of the pricing review.
- Final navigation/authority actions move to a sticky completion dock at the bottom of the page.

Proposed structure:

```tsx
<section className="fee-evaluation-page">
  <FeeEvaluationPreviewTable ... />
  <footer
    aria-label="Fee Evaluation completion actions"
    className="fee-evaluation-completion-dock"
  >
    <span>{confirmFeeDisabledReason ?? "Confirm Fee returns to Workbench after authority is updated."}</span>
    <div className="fee-evaluation-completion-actions">
      <button type="button" onClick={handleBackToWorkbench}>Cancel</button>
      <button
        type="button"
        className="fee-evaluation-primary-action"
        disabled={...}
        onClick={handleConfirmFee}
      >
        Confirm Fee
      </button>
    </div>
  </footer>
</section>
```

The exact component boundary can be adjusted during implementation, but the preferred direction is:

- Keep `FeeEvaluationReviewExportPage` as the owner of final action wiring.
- Let `FeeEvaluationPreviewTable` keep preview/status editing surfaces.
- Avoid adding backend concepts or API-path copy to UI.

### Confirm Success Navigation

Current `handleConfirmFee()` behavior:

- calls `confirmFeeVersion(...)`;
- updates local Confirmed Fee state;
- sets success message.

Required follow-up behavior:

- after `confirmFeeVersion(...)` resolves successfully and local state is updated, call `onBackToWorkbench()`.
- on error, keep the current error behavior and do not navigate.

### Cancel Behavior

Use the existing `handleBackToWorkbench()` logic:

- if a pricing draft exists or has local dirty/error state, prompt before discard;
- abort/bounded-wait in-flight autosave;
- call `discardFeeEvaluationPricingDraft(...)`;
- stay on page and show error if discard fails.

Only the visible label and position change from `Back to Workbench` to `Cancel`.

## File-Level Changes

### `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

- Render a bottom completion dock after `FeeEvaluationPreviewTable`.
- Wire `Cancel` to `handleBackToWorkbench()`.
- Wire `Confirm Fee` to `handleConfirmFee()`.
- Call `onBackToWorkbench()` after successful Confirm Fee.
- Remove final action button wiring from the preview table props if it is no longer needed there.

### `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`

- Keep Confirmed Fee status and `Confirmed by`.
- Remove or relocate the inline `Confirm Fee` button from `fee-evaluation-confirm-strip`.
- Remove `Back to Workbench` from header controls if the bottom dock is the only exit action.
- Keep Fee Form generation in the header controls.

### `frontend/src/workbench.css`

- Add `fee-evaluation-completion-dock`, modeled after `matrix-editor-completion-dock`.
- Add `fee-evaluation-completion-actions`.
- Add or reuse `fee-evaluation-primary-action`.
- Ensure bottom dock does not cover table content and remains readable on the current 14-inch laptop target.

### `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

Add/update tests:

- renders a completion dock with `Cancel` and `Confirm Fee`;
- successful Confirm Fee calls `onBackToWorkbench()`;
- failed Confirm Fee does not call `onBackToWorkbench()`;
- Cancel still uses existing discard path;
- promoted current pricing draft missing/stale Confirmed Fee tests still pass with the relocated button.

### `tests/unit/test_frontend_shell_files.py`

Optional static guard:

- Fee Evaluation page contains `fee-evaluation-completion-dock`;
- final action copy uses `Cancel` / `Confirm Fee`;
- no backend terms are exposed in Fee UI.

## Risks

1. Existing tests that query `Confirm Fee` by role should still work if there is only one button with that name.
2. Removing `Back to Workbench` may require updating tests that assert the previous label.
3. Confirm success navigation could make a success message invisible because the page unmounts. That is acceptable for this requirement, but tests should assert navigation callback rather than success text.
4. Sticky dock must not obscure the last preview rows. CSS may need bottom padding on `.fee-evaluation-page`.

## Validation Plan

Frontend focused:

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
npm run build
```

Static guard:

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
```

Optional browser smoke after implementation:

1. Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f/fee-evaluation`.
2. Confirm bottom-right dock shows `Cancel` and `Confirm Fee`.
3. Confirm successful `Confirm Fee` returns to Workbench when the backend accepts the action.

## Stop Point

Stop after the Fee Evaluation action dock and confirm-success navigation are validated. Do not implement future Fee UI, inactive removed-row editing, Project Folder behavior, StepInstance, report, AI, permissions, LAN/server, or multi-user scope from this follow-up.

## Completion Summary

Implemented the approved frontend-only follow-up:

- Added a bottom sticky Fee Evaluation completion dock with `Cancel` and `Confirm Fee`.
- Reused the existing Fee pricing draft discard lifecycle for `Cancel`.
- Reused existing Confirm Fee gating and request payload for `Confirm Fee`.
- Changed successful Confirm Fee to return the operator to Project Workbench after the backend confirm response is accepted.
- Kept Confirm failure on the Fee Evaluation page.
- Kept Confirmed Fee status and `Confirmed by` visible in the page body.
- Removed the old `Back to Workbench` header action from the Fee page.

Validation completed:

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
```

Results: `20 passed`, `37 passed`, `12 passed, 134 deselected`, and frontend build passed. Browser smoke confirmed the dock on the live Fee Evaluation route.
