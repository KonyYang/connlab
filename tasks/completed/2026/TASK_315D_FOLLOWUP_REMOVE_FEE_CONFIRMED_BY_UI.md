# TASK_315D_FOLLOWUP_REMOVE_FEE_CONFIRMED_BY_UI

Status: Complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Related completed task: `TASK_315D_FOLLOWUP_FEE_CONFIRM_ACTION_DOCK`.

Plan: `docs/task_315d_followup_remove_fee_confirmed_by_ui_plan.md`

## Goal

Remove the user-facing `Confirmed by` mechanism from Fee Evaluation.

Fee Evaluation is an operator-owned pricing assessment surface. The operator does not need to select or type a separate approver/person before confirming the Fee authority version.

## Scope

Frontend/UI-only follow-up:

- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx`
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx`
- `frontend/src/workbench.css`
- optional static guard update in `tests/unit/test_frontend_shell_files.py`

## Required Behavior

1. Remove the visible `Confirmed by` label and input from Fee Evaluation.
2. Remove `Confirmed by` as a Confirm Fee blocker in the frontend.
3. Keep `Confirm Fee` gated by the existing saved pricing draft and autosave conditions.
4. Keep Confirm Fee backend request compatible by sending a non-empty internal attribution value while the backend still requires `confirmed_by`.
5. Remove user-facing status copy that presents Fee confirmation as approval by a named person.
6. Keep Confirm Fee success returning to Workbench.

## Out Of Scope

Do not change:

- Backend `confirmed_by` schema or service validation.
- Confirm Fee authority version storage.
- Fee pricing calculations or summary derivation.
- Pricing draft autosave/discard behavior.
- Matrix rebase/promotion.
- Project Folder readiness semantics.
- Required forms generation.
- StepInstance, report, evidence/image, AI, permissions, LAN/server, or multi-user scope.

## Acceptance Criteria

- Fee Evaluation page no longer renders `Confirmed by` label/input.
- Confirm Fee can be enabled without any user-entered person field.
- Confirm Fee request still includes a backend-compatible non-empty `confirmed_by`.
- Confirmed Fee status no longer says `Confirmed by <name>` in the UI.
- Existing Cancel/Confirm dock behavior remains intact.

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

Stop after this UI follow-up is implemented and validated. Do not proceed to backend schema changes or later task scope without separate explicit approval.

## Completion Notes

Completed after explicit user approval on 2026-06-15.

Removed the user-facing `Confirmed by` mechanism from Fee Evaluation. The Fee page no longer renders the `Confirmed by` label/input, no longer blocks Confirm Fee on a user-entered person field, and no longer presents current Fee authority as named-person approval. Confirm Fee still sends a backend-compatible non-empty internal attribution value because the backend authority schema currently requires `confirmed_by`.

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

Results: Fee Evaluation tests `20 passed`; Workbench/Project Folder tests `37 passed`; static guard `12 passed, 134 deselected`; frontend build passed. Browser smoke on `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f/fee-evaluation` confirmed no `Confirmed by` text/input, current status copy `Fee authority is current.`, and the bottom `Cancel` / `Confirm Fee` dock remains present.
