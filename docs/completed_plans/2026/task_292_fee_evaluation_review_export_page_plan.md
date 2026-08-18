# TASK_292 Fee Evaluation Review & Export Page Plan

## Execution Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task: TASK_292_FEE_EVALUATION_REVIEW_EXPORT_PAGE.
- Allowed reason: TASK_291 is complete and the user explicitly approved implementing the TASK_292 plan.

## Design

Fee Evaluation becomes its own operator surface at `/projects/:projectId/fee-evaluation`. The Workbench keeps a compact derived-output card only, so the Matrix workspace no longer stretches around the 57-row fee review table.

V1 is Review+Export, not in-app pricing. The table shows Matrix source, matched fee rule, unit price, calculated fee, status, and review reasons. It does not render editable units, base fee, or discount controls because those values are neither persisted nor consumed by Matrix basic-fill export.

The export panel uses the existing production timeout-protected backend endpoint from TASK_291:

```text
POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/export
```

with:

```json
{
  "fill_mode": "matrix_basic",
  "template_path": "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls",
  "output_dir": "<latest project folder path>",
  "allow_review_required": true,
  "overwrite": false
}
```

## File-Level Changes

- `tasks/TASK_292_FEE_EVALUATION_REVIEW_EXPORT_PAGE.md`
  - Add controlled task file.
- `docs/task_292_fee_evaluation_review_export_page_plan.md`
  - Add executable plan.
- `docs/task_board.md`
  - Mark TASK_292 active/complete with validation summary.
- `frontend/src/api/client.ts`
  - Add typed export request/response DTOs and `exportConfirmedMatrixFeeEvaluation`.
- `frontend/src/App.tsx`
  - Parse and render `/projects/:projectId/fee-evaluation`.
- `frontend/src/pages/ProjectWorkbenchPage.tsx`
  - Pass fee navigation callback.
- `frontend/src/pages/ProjectFeeEvaluationPage.tsx`
  - New route page.
- `frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx`
  - New fee review/export feature surface.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Remove full fee panel and wire compact summary action.
- `frontend/src/features/project-workbench/FeeEvaluationStatusSummary.tsx`
  - Add compact action and Matrix-authority enablement.
- `frontend/src/workbench.css`
  - Add dense fee page styling and remove misleading local-edit emphasis.
- Frontend tests
  - Add fee page tests for filtering/export/error behavior.
  - Update Workbench summary tests for navigation.
  - Remove old full-panel local-edit test coverage.
- `tests/unit/test_frontend_shell_files.py`
  - Add route/client static coverage.

## Risks And Controls

- Route parsing is hand-written: add explicit parser branch before generic project route.
- Export can hang at Office COM: use the existing TASK_291 timeout-protected API path, no direct frontend workaround.
- Output directory must be controlled: use latest project folder path only; no arbitrary output directory input.
- Review-required lines are allowed in Matrix basic fill: copy must make clear the Excel file still needs manual pricing completion.
- Avoid Workbench growth: keep full table out of Workbench and place all fee review controls in the new feature folder.

## Validation

Run:

```text
cd frontend; npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Manual/browser smoke:

- Open `http://localhost:5173/projects/ce15026d119f408f80970ea7077f6e41`.
- Confirm Workbench only shows compact Fee Evaluation summary.
- Open `http://localhost:5173/projects/ce15026d119f408f80970ea7077f6e41/fee-evaluation`.
- Confirm the review/export page loads, filters work, and export blockers/status are visible.
