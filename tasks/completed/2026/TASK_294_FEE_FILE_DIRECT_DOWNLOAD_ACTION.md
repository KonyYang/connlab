# TASK_294 Fee File Direct Download Action

Status: complete (archived 2026-08-18; implementation integrated and covered by tests)

Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Allowed reason: TASK_293 is complete. The user reviewed the `/fee-evaluation` page and explicitly approved creating a follow-up task to replace the verbose export panel with a direct Fee File download action.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task. The work is a bounded backend/frontend integration that follows existing patterns: the Test Record direct-download endpoint, the existing Fee Evaluation export service, the TASK_291 timeout boundary, and the TASK_293 preview-first UI. The main risks are preserving Office/COM isolation, not bypassing the application service, and keeping the UI focused without hiding actionable export failures. These are appropriate for GPT-5.3-codex if implementation follows the executable plan and stops after this task.

## Goal

Make the Fee Evaluation page behave like the current `Test record` action:

- the operator clicks a simple `Fee file` action
- ConnLab generates the Matrix basic-fill Fee Evaluation workbook in a controlled generated-output folder
- the browser downloads the generated `.xls` file
- the action does not require the project folder to already exist

The page should no longer show a separate export-settings card. The primary surface is the `Fee File` preview.

## Business Reason

The operator's main question is:

```text
What will the Fee file look like, and can I generate it now?
```

They do not need to choose an output directory, read backend freshness metadata, or manage optional file names on the main page. Manual price completion still happens in the generated Excel workbook.

## Scope

### Backend

- Add a direct-download Fee Evaluation endpoint modeled after the existing Confirmed Matrix Test Record download endpoint.
- Reuse the existing Confirmed Matrix Fee Evaluation export service and timeout-aware dependency.
- Use Matrix basic-fill mode:

```text
fill_mode = "matrix_basic"
allow_review_required = true
template_path = D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls
output_dir = settings.data_dir / "generated_fee_files"
```

- Return `FileResponse` with the generated `.xls` workbook.
- Continue registering the Fee Evaluation output through the existing export service behavior.

### Frontend

- Remove the separate `Excel output` / export-settings card from `/projects/:projectId/fee-evaluation`.
- Rename the main preview card title from `Testing Prices preview` to `Fee File`.
- Put the direct `Fee file` action inside the `Fee File` card.
- Remove project-folder gating from the Fee page export action.
- Remove the separate `Selected total` card.
- Keep the `All Group` selector, but show the selected scope fee in the same selector card:
  - `All Group` shows all-row total status
  - a selected group shows that group's total status
- Keep review details secondary.

## Out Of Scope

- No fee calculation rule changes.
- No persistent fee-line edits.
- No new database tables or migrations.
- No rule-maintenance UI.
- No template mutation.
- No new workbook writer dependency.
- No project-folder generation or approval-package workflow change.
- No StepInstance, execution persistence, report expansion, AI review, permissions, or multi-user workflow.
- No broad Excel process kill beyond the existing TASK_291 timeout/cleanup behavior.

## Required Backend Behavior

New endpoint:

```text
POST /api/projects/{project_id}/confirmed-matrix/fee-evaluation/file/generate
```

V1 request body:

```text
none
```

V1 response:

```text
FileResponse
```

Expected behavior:

- Uses the formal optimized template path.
- Writes output into `settings.data_dir / "generated_fee_files"`.
- Creates the generated output directory if needed.
- Calls the existing timeout-aware Fee Evaluation export dependency.
- Calls the service with `fill_mode="matrix_basic"` and `allow_review_required=true`.
- Before returning the browser download, validates the generated path at route level:
  - `result.output_path.resolve()` must exist.
  - It must be a file.
  - It must have suffix `.xls`.
  - It must live under `(settings.data_dir / "generated_fee_files").resolve()`.
- Returns the generated workbook as a browser download.
- Maps known export errors to actionable HTTP responses:
  - `404` for missing active authority / required records
  - `400` or `422` for invalid export state/template problems
  - `503` for Office unavailable or timeout
- Preserves structured timeout detail with `manual_cleanup_warning`.

## Required Frontend Behavior

Fee Evaluation page V1 layout:

```text
Fee File
  Back to Workbench
  All Group [dropdown] | Fee: <selected scope fee>
  Fee file [button]
  Testing Prices-style preview
  Totals band

Review details
```

Button behavior:

- V1 enable rule: `Fee file` is enabled only when the current Fee Evaluation draft has loaded successfully in the page.
- This is intentionally stricter than the backend Matrix basic-fill export capability, because the current page preview is fee-draft based and TASK_294 does not add a separate active-Matrix/basic-fill readiness read model.
- It does not require latest project folder path.
- It calls the new direct-download endpoint.
- On success, it downloads the workbook using the same blob-download pattern as `Test record`.
- On failure, it shows concise business-readable inline feedback.
- It must not expose raw backend route names, output directories, or internal traceability metadata.

Group fee behavior:

- The group dropdown remains defaulted to `All Group`.
- The same card displays a fee label/value for the current selection.
- If every row in scope has numeric `testing_fee`, display the calculated scope total.
- If any row in scope is pending/manual, display `Pending Excel confirmation`.
- The old separate `Selected total` card is removed.

## Acceptance Criteria

- `/projects/:projectId/fee-evaluation` no longer renders a standalone `Excel output` card.
- The primary preview card title is `Fee File`.
- The `Fee file` button lives inside the `Fee File` card.
- Clicking `Fee file` calls the new direct-download API and triggers a browser download.
- Direct-download route rejects any generated result path outside `settings.data_dir / "generated_fee_files"`, any missing/non-file path, and any non-`.xls` path before `FileResponse`.
- The action works without a project folder path.
- The V1 frontend enable rule is fee-draft-loaded, not project-folder-loaded and not an inferred active-Matrix readiness state.
- The frontend no longer blocks with `Create the project folder before generating the workbook.`
- The group selector card shows the fee for the selected scope.
- The separate `Selected total` card is gone.
- Review details remain secondary and unchanged in behavior.
- Existing JSON export endpoint remains available for backend/API compatibility.
- Existing Test Record download behavior remains unchanged.

## Validation

Expected implementation validation:

```text
py -m pytest tests/unit/test_confirmed_matrix_fee_file_download_route.py tests/integration/test_confirmed_matrix_fee_file_download_api.py -q
py -m pytest tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py tests/unit/test_fee_evaluation_workbook_gateway.py -q
cd frontend; npm test -- --run FeeEvaluation ProjectWorkbench --watch=false
cd frontend; npm run build
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or project_workbench"
git diff --check
```

Browser smoke:

- Open `http://localhost:5173/projects/2cd4b0e7ff6f4df99448c9ffdd78629f/fee-evaluation`.
- Confirm the first Fee page business card is `Fee File`.
- Confirm there is no standalone `Excel output` card.
- Confirm `All Group` shows its fee status in the same card.
- Confirm `Fee file` attempts a direct file download without requiring project folder creation.
