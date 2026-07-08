# TASK_357D Fee Passive Consumes Matrix Step Quantities - QA Evidence

Date: 2026-07-08

Role: QA / Smoke Owner

Task: `TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES`

Lane: `fee-passive-consumes-matrix-step-quantities`

Result: `qa_pass`

Recommended next role: Integrator packaging/readiness

## Scope Read

QA re-read the current lane task, plan, Developer evidence, Reviewer evidence, and TASK_357D reconciliation evidence. QA also re-read upstream TASK_351, TASK_357A, TASK_357B, and TASK_357C accepted context/evidence relevant to quantity authority and Fee Evaluation default-fill.

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Why this QA gate is allowed: Reviewer implementation re-gate passed after the B1 line-limit/headroom blocker was closed, and Reviewer recommended QA because TASK_357D changes Fee default-fill behavior.

## Candidate Package Status

Observed TASK_357D candidate files:

- `backend/application/confirmed_matrix_fee_draft_service.py`
- `backend/application/confirmed_matrix_fee_step_quantities.py`
- `backend/modules/fee_evaluation/__init__.py`
- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/fee_default_fill_models.py`
- `backend/modules/fee_evaluation/fee_step_quantity_defaults.py`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_fee_default_fill.py`
- `tasks/TASK_357D_FEE_PASSIVE_CONSUMES_MATRIX_STEP_QUANTITIES.md`
- `docs/task_357d_fee_passive_consumes_matrix_step_quantities_plan.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_developer.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reviewer.md`
- `docs/lane_evidence/TASK_357D_fee-passive-consumes-matrix-step-quantities_reconciliation_planner.md`
- this QA evidence

External residuals remain visible in the worktree, including `docs/task_board.md`, `backend/api/dependencies.py`, Settings/LTR/template files, release/desktop/packaging files, frontend New Project test residuals, TASK_357A docs/evidence, and `temp_agents_stash.md`. QA treats those as excluded from TASK_357D packaging.

## Validation Commands

### Backend focused unit suite

Command:

```powershell
py -m pytest tests/unit/test_fee_default_fill.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_rule_seed_loader.py tests/unit/test_fee_rule_matcher.py -q
```

Observed result: `50 passed in 1.36s`.

Coverage confirmed:

- LLCR prefers confirmed Matrix Step quantity readings over text readings.
- LLCR unit-price tiering follows readings-per-sample.
- CR specified-current uses the same structured Step quantity source policy while preserving current/tier behavior.
- Missing, review-required, invalid, or conflicting Step quantity facts become review-required.
- Multiple Step tokens with same readings-per-sample calculate deterministically.
- Multiple Step tokens with different readings-per-sample become review-required.
- TASK_351 text fallback remains when structured Step quantity authority is absent.
- TASK_351 seed/rule behavior remains compatible.

### Backend focused integration suite

Command:

```powershell
py -m pytest tests/integration/test_confirmed_matrix_fee_draft_api.py tests/integration/test_fee_evaluation_pricing_draft_api.py tests/integration/test_confirmed_fee_version_api.py -q
```

Observed result: `20 passed in 4.01s`.

Coverage confirmed:

- Fee draft API remains healthy with default-fill changes.
- Pricing draft and confirmed Fee version API regressions remain passing.

### Backend compile

Command:

```powershell
py -m py_compile backend/application/confirmed_matrix_fee_draft_service.py backend/application/confirmed_matrix_fee_step_quantities.py backend/modules/fee_evaluation/fee_default_fill.py backend/modules/fee_evaluation/fee_step_quantity_defaults.py backend/modules/fee_evaluation/fee_default_fill_models.py backend/modules/fee_evaluation/__init__.py
```

Observed result: passed with no output.

### Frontend focused Fee Evaluation tests

Command:

```powershell
cd frontend
npm test -- FeeEvaluation --run
```

Observed result: `3 files / 55 tests passed`.

Existing React `act(...)` warnings appeared in `FeeEvaluationReviewExportPage.test.tsx`; QA treats them as known/non-blocking because the focused suite passed and Reviewer recorded the same warning class.

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
git diff --check -- <TASK_357D candidate files>
```

Observed result: passed with LF/CRLF normalization warnings only.

Command:

```powershell
Select-String -Path <TASK_357D candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

Line-count scan:

```text
413 backend/application/confirmed_matrix_fee_draft_service.py
127 backend/application/confirmed_matrix_fee_step_quantities.py
426 backend/modules/fee_evaluation/fee_default_fill.py
123 backend/modules/fee_evaluation/fee_step_quantity_defaults.py
81  backend/modules/fee_evaluation/fee_default_fill_models.py
```

Observed result: B1 remains closed. Split modules are focused and all checked Python files are below the 500-line hard limit with meaningful headroom.

### Forbidden-scope scan

Command:

```powershell
git diff --name-only -- frontend/src/features/matrix-editor backend/application/matrix_step_quantity_service.py backend/infrastructure/storage/models_project_matrix_draft.py backend/infrastructure/storage/models_confirmed_matrix_authority.py backend/infrastructure/storage/repositories/project_matrix_draft.py backend/infrastructure/storage/repositories/confirmed_matrix_authority.py backend/application/project_basic_information_service.py frontend/src/features/project-basic-information backend/modules/test_plan backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/application/test_record* backend/api/routes_*test_record* backend/application/*report* backend/application/*ltr* backend/api/routes_ltr* .agents docs/project_management dist_release packaging scripts temp_agents_stash.md
```

Observed result: no TASK_357D candidate diff in locked paths.

## Behavior Assessment

QA did not find a blocking behavior issue in tests/source/static inspection.

Confirmed Matrix Step quantity passive consumption:

- `ConfirmedMatrixFeeDraftService` consumes active confirmed Matrix data and delegates read-only Step quantity context construction to `confirmed_matrix_fee_step_quantities.py`.
- Step quantity lookup uses confirmed group, row, step sequence, and normalized suffix identity.
- Fee default-fill receives `FeeStepQuantityContext` facts and does not call Matrix Step mutation/storage write behavior.

LLCR / CR per-reading behavior:

- `fee_step_quantity_defaults.py` derives readings per sample from `test_points_per_sample * readings_per_point`.
- The structured source label is `Matrix Step quantity`.
- `contact_points_per_sample` is carried as context/review metadata and is not silently substituted as total readings.
- Unit-price tiering follows readings-per-sample.

Review-required and fallback behavior:

- Missing, unmatched, review-required, invalid, or conflicting Step quantity facts return `Confirm Matrix Step quantity`.
- TASK_351 text parsing fallback remains only when structured Step quantity authority is absent/unmapped.
- Existing manual/default rows and unmapped rules remain on TASK_351 behavior.

No Fee-side quantity editing UI:

- No frontend Fee Evaluation product file is part of the TASK_357D candidate diff.
- Source scan found only existing fee unit labels such as `per reading` / `per contact` in Fee Evaluation frontend code, and no Step quantity setup/editor surface in Fee Evaluation.

## Browser Smoke

Live browser smoke was attempted at tooling level but could not be completed:

```text
bundled=browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system=browserType.launch: spawn EPERM
```

No screenshot artifact was captured. This is a non-blocking QA residual because TASK_357D is backend/default-fill focused, no frontend Fee product code changed, and the behavior is covered by focused backend unit/integration tests, frontend Fee regression tests, build, source inspection, and static scope scans.

## Residual Risk

- Browser-only presentation issues were not directly observed in this thread due browser tooling restrictions.
- Integrator must keep external Settings/LTR, release/desktop/packaging, New Project, board, TASK_357A, and `temp_agents_stash.md` residuals out of the TASK_357D package.

## QA Conclusion

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Integrator packaging note: stage only the TASK_357D candidate files and this QA evidence. Do not stage external residuals or locked-scope paths.
