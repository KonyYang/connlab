# TASK_315D Follow-up Remove Fee Confirmed By UI Plan

Date: 2026-06-15

Status: Complete after explicit user approval on 2026-06-15.

Task file: `tasks/TASK_315D_FOLLOWUP_REMOVE_FEE_CONFIRMED_BY_UI.md`

## Current Phase And Authorization

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

This is a narrow UI follow-up to the completed Fee Evaluation action dock work. It is not a backend authority redesign.

## User Feedback

The selected Fee Evaluation field is `Confirmed by`. The requested behavior is:

> 当前不需要这个指定人员批准的机制，费用表由用户自己负责评估。

Interpretation:

- Fee Evaluation should not ask the operator to choose or type a separate approving person.
- The operator performing Fee Evaluation owns the assessment.
- The UI should not describe Fee confirmation as named-person approval.

## Current Code Reality

Frontend:

- `FeeEvaluationReviewExportPage.tsx`
  - stores `confirmedBy` state initialized to `"Lab User"`;
  - blocks Confirm Fee when `confirmedBy.trim()` is empty;
  - sends `confirmed_by: confirmedBy.trim()` to `confirmFeeVersion(...)`;
  - renders status detail as `Confirmed by ${confirmedFee.confirmed_by}.`;
  - passes `confirmedBy` and `onConfirmedByChange` into `FeeEvaluationPreviewTable`.
- `FeeEvaluationPreviewTable.tsx`
  - renders the visible `Confirmed by` label/input.

Backend:

- `ConfirmedFeeVersionService.confirm(...)` validates `confirmed_by` as required.

## Design

### UI Behavior

Remove the user-facing Confirmed-by mechanism:

- no visible `Confirmed by` input;
- no user-facing blocker saying `Enter confirmed by before confirming.`;
- no status detail saying `Confirmed by Lab User.`;
- status should remain operational, for example:
  - `Confirmed`
  - `Fee authority is current.`

### Backend Compatibility

Do not change the backend in this follow-up.

While the backend still requires `confirmed_by`, the frontend will submit a stable internal value such as the existing local user label `"Lab User"`. This preserves backend compatibility and audit metadata without exposing a user-editable approval-person mechanism.

If the product later wants to remove `confirmed_by` from the API/schema entirely, that should be a separate backend migration task.

## File-Level Changes

### `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`

- Remove `confirmedBy` React state if no longer needed as editable state.
- Use a stable internal constant for request `confirmed_by`.
- Remove `confirmedBy` from `confirmFeeBlocker(...)`.
- Remove the `confirmedBy` empty-field error path.
- Update confirmed status detail to avoid named-person approval language.
- Stop passing `confirmedBy` and `onConfirmedByChange` props to `FeeEvaluationPreviewTable`.

### `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`

- Remove `confirmedBy` and `onConfirmedByChange` props.
- Remove the `Confirmed by` label/input block from `fee-evaluation-confirm-strip`.
- Let the Confirmed Fee status row occupy the available width.

### `frontend/src/workbench.css`

- Simplify `.fee-evaluation-confirm-strip` from two columns to one status area.
- Remove or leave harmless unused `.fee-evaluation-confirm-by` styles only if shared CSS cleanup is too noisy. Preferred: remove selectors if they become dead and are local to Fee Evaluation.

### `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`

Update tests:

- assert `Confirmed by` input is not rendered;
- assert Confirm Fee request still includes `confirmed_by: "Lab User"` or the chosen internal local-user attribution;
- remove tests that depend on user editing the person field;
- confirm dock behavior remains intact.

### `tests/unit/test_frontend_shell_files.py`

Optional static guard:

- Fee Evaluation source should not expose `Confirmed by` as UI copy.

## Risks

1. Backend still requires `confirmed_by`, so frontend must keep sending a non-empty internal value.
2. Existing tests may assert the old status detail `Confirmed by Lab User.` and need to be updated to the new product copy.
3. Project Folder or Confirmed Fee response may still contain `confirmed_by` data. This follow-up only removes the Fee Evaluation UI mechanism, not the backend field.

## Validation Plan

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
```

Browser smoke:

1. Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f/fee-evaluation`.
2. Confirm the `Confirmed by` row/input is gone.
3. Confirm bottom dock still shows `Cancel` and `Confirm Fee`.

## Stop Point

Stop after this UI follow-up is validated. Do not change backend schema/API, Project Folder semantics, Matrix rebase, Required forms generation, StepInstance, report, AI, permissions, LAN/server, or multi-user scope.

## Completion Summary

Implemented the approved frontend-only follow-up:

- Removed the visible `Confirmed by` label/input from Fee Evaluation.
- Removed the frontend Confirm Fee blocker for missing user-entered confirmed-by text.
- Kept Confirm Fee backend compatibility by sending the existing local internal attribution value.
- Changed current Confirmed Fee status copy from named-person approval to `Fee authority is current.`
- Preserved the bottom `Cancel` / `Confirm Fee` action dock and Confirm-success Workbench return.

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

Results: `20 passed`, `37 passed`, `12 passed, 134 deselected`, and frontend build passed. Browser smoke confirmed the removed field and retained completion dock on the live Fee Evaluation route.
