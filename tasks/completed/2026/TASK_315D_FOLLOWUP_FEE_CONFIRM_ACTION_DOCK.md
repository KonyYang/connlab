# TASK_315D_FOLLOWUP_FEE_CONFIRM_ACTION_DOCK

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Related completed task: `TASK_315D_FEE_UI_PROJECT_FOLDER_REGRESSION`.

Plan: `docs/task_315d_followup_fee_confirm_action_dock_plan.md`

## Goal

Make the Fee Evaluation confirmation flow match the Matrix Editor completion pattern:

- Keep the Fee page's final actions fixed at the lower right of the work surface.
- Show two final action buttons: `Cancel` and `Confirm Fee`.
- Treat `Confirm Fee` as the explicit authority-write action.
- After `Confirm Fee` succeeds, return the operator to Project Workbench.

## Scope

Frontend/UI-only follow-up:

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- `frontend/src/workbench.css`
- optional static guard update in `tests/unit/test_frontend_shell_files.py`

## Required Behavior

1. The Fee Evaluation page renders a sticky/fixed completion dock at the lower right, visually aligned with the Matrix Editor `Cancel` / `Confirm Matrix` pattern.
2. The dock contains:
   - `Cancel`: uses the existing Fee Evaluation cancel/back discard lifecycle.
   - `Confirm Fee`: uses the existing Confirm Fee gating and request payload.
3. The existing Confirmed Fee status and `Confirmed by` input remain visible in the page body.
4. The old top-level `Confirm Fee` button is removed or relocated so the final authority action appears only in the completion dock.
5. When `Confirm Fee` succeeds, the page calls `onBackToWorkbench()` after the backend confirm response is accepted.
6. Confirm failure keeps the operator on Fee Evaluation and displays the existing actionable error.

## Out Of Scope

Do not change:

- Confirm Fee backend authority rules.
- Fee pricing calculations or summary derivation.
- Pricing draft autosave/discard backend behavior.
- Matrix rebase or Matrix Confirm promotion.
- Project Folder readiness semantics.
- Required forms generation.
- StepInstance, report, evidence/image, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- Fee page has a completion dock with `Cancel` and `Confirm Fee`.
- `Confirm Fee` remains disabled for the existing blocker reasons.
- `Cancel` still uses the existing discard confirmation and failure behavior.
- Successful `Confirm Fee` calls `onBackToWorkbench()`.
- Failed `Confirm Fee` does not navigate away.
- Existing TASK_315D promoted draft and Project Folder regression tests still pass.

## Required Validation

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
```

## Stop Point

Stop after this UI follow-up is implemented and validated. Do not proceed to TASK_316 or later work without separate explicit approval.

## Completion Notes

Completed after explicit user approval on 2026-06-15.

Implemented a frontend-only Fee Evaluation completion dock aligned with the Matrix Editor final action pattern. The page now renders bottom sticky `Cancel` and `Confirm Fee` actions, keeps Confirmed Fee status and `Confirmed by` in the review body, removes the old `Back to Workbench` header button, and calls `onBackToWorkbench()` after `Confirm Fee` succeeds. Confirm failure still keeps the operator on Fee Evaluation with the existing actionable error path, and Cancel still uses the existing pricing draft discard lifecycle.

Validation:

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage --watch=false
npm test -- --run ProjectWorkbenchLayout projectFolderTaskSelectors ProjectFolderTaskList FeeEvaluationStatusSummary --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task315 or fee or project_workbench"
```

Results: Fee Evaluation tests `20 passed`; Workbench/Project Folder tests `37 passed`; static guard `12 passed, 134 deselected`; frontend build passed. Browser smoke on `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f/fee-evaluation` confirmed `.fee-evaluation-completion-dock` with `Cancel` and `Confirm Fee`, and no `Back to Workbench` button.
