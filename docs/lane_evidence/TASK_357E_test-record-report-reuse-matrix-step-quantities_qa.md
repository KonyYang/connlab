# TASK_357E Test Record / Report Reuse Matrix Step Quantities - QA Evidence

Date: 2026-07-08

Role: QA / Smoke Owner

Task: `TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES`

Lane: `test-record-report-reuse-matrix-step-quantities`

Result: `qa_pass`

Recommended next role: Integrator packaging/readiness

## Scope Read

QA re-read the current lane task, plan, Developer evidence, Reviewer evidence, and TASK_357E reconciliation evidence. QA also re-read upstream TASK_357A, TASK_357B, TASK_357C, and TASK_357D accepted context/evidence relevant to confirmed Matrix Step quantity authority and downstream reuse boundaries.

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Why this QA gate is allowed: Reviewer implementation gate passed and recommended QA because TASK_357E changes Test Record preview/API quantity metadata and document-generation pass-through behavior.

## Candidate Package Status

Observed TASK_357E candidate files:

- `backend/application/confirmed_matrix_step_quantity_projection.py`
- `backend/application/confirmed_matrix_test_record_preview_service.py`
- `backend/api/routes_confirmed_matrix_test_record_preview.py`
- `tests/unit/test_confirmed_matrix_test_record_preview_service.py`
- `tests/unit/test_confirmed_matrix_test_record_document_generation_service.py`
- `tests/integration/test_confirmed_matrix_test_record_preview_api.py`
- `tests/integration/test_confirmed_matrix_test_record_generation_api.py`
- `tasks/TASK_357E_TEST_RECORD_REPORT_REUSE_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357e_test_record_report_reuse_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_developer.md`
- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_reviewer.md`
- `docs/lane_evidence/TASK_357E_test-record-report-reuse-matrix-step-quantities_reconciliation_planner.md`
- this QA evidence

External residuals remain visible in the worktree, including `docs/task_board.md`, `backend/api/dependencies.py`, Settings/LTR/template files, release/desktop/packaging files, frontend New Project test residuals, TASK_357A docs/evidence, and `temp_agents_stash.md`. QA treats those as excluded from TASK_357E packaging.

## Validation Commands

### Focused Test Record preview/document/API suite

Command:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_confirmed_matrix_test_record_preview_api.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
```

Observed result: `30 passed in 13.46s`.

Coverage confirmed:

- Test Record preview projects confirmed Matrix Step quantity metadata for matching Step tokens.
- Preview exposes `missing` when an active confirmed Matrix has Step quantity authority but the preview Step has no matching quantity record.
- Preview preserves `review_required` Step quantity records and review reasons.
- `total_readings` derives from `test_points_per_sample * readings_per_point`.
- API response exposes optional per-step `quantity` metadata.
- Document generation receives the same preview group/step quantity projection objects through the writer path.
- Existing Test Record generation API regressions remain passing.

### Backend compile

Command:

```powershell
py -m py_compile backend/application/confirmed_matrix_step_quantity_projection.py backend/application/confirmed_matrix_test_record_preview_service.py backend/application/confirmed_matrix_test_record_document_generation_service.py backend/api/routes_confirmed_matrix_test_record_preview.py
```

Observed result: passed with no output.

### Frontend build

Command:

```powershell
cd frontend
npm run build
```

Observed result: passed. Existing Vite chunk-size warning only.

### Diff, whitespace, and line-count checks

Command:

```powershell
git diff --check -- <TASK_357E candidate files>
```

Observed result: passed with LF/CRLF normalization warnings only.

Command:

```powershell
Select-String -Path <TASK_357E candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

Line-count scan:

```text
133 backend/application/confirmed_matrix_step_quantity_projection.py
255 backend/application/confirmed_matrix_test_record_preview_service.py
451 backend/application/confirmed_matrix_test_record_document_generation_service.py
138 backend/api/routes_confirmed_matrix_test_record_preview.py
```

Observed result: checked TASK_357E Python files remain below the 500-line hard limit.

### Forbidden-scope scan

Command:

```powershell
git diff --name-only -- backend/modules/fee_evaluation backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_step_quantities.py frontend/src/features/fee-evaluation frontend/src/features/matrix-editor backend/application/matrix_step_quantity_service.py backend/infrastructure/storage/models_project_matrix_draft.py backend/infrastructure/storage/models_confirmed_matrix_authority.py backend/infrastructure/storage/repositories/project_matrix_draft.py backend/infrastructure/storage/repositories/confirmed_matrix_authority.py backend/application/project_basic_information_service.py frontend/src/features/project-basic-information backend/modules/test_plan backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/application/*ltr* backend/api/routes_ltr* .agents docs/project_management dist_release packaging scripts temp_agents_stash.md
```

Observed result: no TASK_357E candidate diff in locked paths.

## Behavior Assessment

QA did not find a blocking behavior issue in tests/source/static inspection.

Confirmed Matrix Step quantity projection:

- `confirmed_matrix_step_quantity_projection.py` is a read-only downstream projection helper.
- Projection lookup uses confirmed group id, confirmed row id, step sequence, and normalized suffix.
- Projection status is `ready`, `missing`, or `review_required`.
- `total_readings` is derived only from valid `test_points_per_sample * readings_per_point`.
- `contact_points_per_sample` is carried as metadata and is not used as a replacement for total readings.

Test Record preview/API:

- `ConfirmedMatrixTestRecordPreviewStep` now carries optional `quantity` metadata.
- Preview service attaches projected quantity metadata to parsed Step tokens.
- Preview API serializes optional `quantity` fields: `test_points_per_sample`, `readings_per_point`, `contact_points_per_sample`, `total_readings`, `status`, `source`, and `review_reason`.
- Missing and review-required Step quantity states surface explicit metadata rather than invented values.

Document generation:

- Document generation continues to consume preview groups/steps.
- Focused test confirms the writer receives the same preview step quantity projection object.
- No Word template placement was added.
- No full Report generation was added.

Authority and scope:

- Confirmed Matrix Step quantities remain the downstream quantity authority.
- Basic Information defaults are not used as final Test Record/Report quantity authority.
- Fee Evaluation default-fill or edited values are not used as downstream authority.
- Existing Basic Information/LTR references in document generation remain header metadata behavior and are not TASK_357E quantity-authority changes.
- No StepInstance/execution persistence, Matrix parser/import changes, LTR/public-drive mutation, or real workbook/folder mutation was found in the TASK_357E candidate package.

## Browser Smoke

Live browser smoke was attempted at tooling level but could not be completed:

```text
bundled=browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system=browserType.launch: spawn EPERM
```

No screenshot artifact was captured. This is a non-blocking QA residual because TASK_357E is backend preview/API/document-generation focused, no frontend product code changed, and focused backend/API tests plus build/source/static checks cover the changed behavior.

## Residual Risk

- Browser-only presentation issues were not directly observed in this thread due browser tooling restrictions.
- Integrator must keep external Settings/LTR, release/desktop/packaging, New Project, board, TASK_357A, and `temp_agents_stash.md` residuals out of the TASK_357E package.

## QA Conclusion

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Integrator packaging note: stage only the TASK_357E candidate files and this QA evidence. Do not stage external residuals or locked-scope paths.
