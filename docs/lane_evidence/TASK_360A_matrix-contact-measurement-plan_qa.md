# TASK_360A Matrix Contact Measurement Plan - QA Evidence

Date: 2026-07-10

Role: QA / Smoke Owner

Task: `TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN`

Lane: `matrix-contact-measurement-plan`

Gate: QA gate

## Scope Read

- Read `AGENTS.md` and confirmed current phase is Phase 11 controlled Project Workbench / Matrix / Approval Package foundation.
- Read `docs/task_board.md`; TASK_360A is the active/current Matrix Contact Measurement Plan lane and TASK_360B remains future serial scope.
- Read `tasks/TASK_360A_MATRIX_CONTACT_MEASUREMENT_PLAN.md`.
- Read `docs/task_360a_matrix_contact_measurement_plan.md`.
- Read Developer evidence: `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_developer.md`.
- Read Reviewer evidence: `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_reviewer.md`.
- Read reconciliation evidence: `docs/lane_evidence/TASK_360A_matrix-contact-measurement-plan_reconciliation_planner.md`.

QA did not modify product code, tests, board, or packaging state. This file is QA evidence only.

## Candidate Package / Residual Status

Observed TASK_360A candidate surface includes Matrix Step quantity/contact-plan backend domain/service/API/storage, Matrix Editor UI/selectors/tests/CSS, Fee passive authority mapping, and focused tests/evidence.

External residuals visible in the worktree and excluded from the TASK_360A QA package decision:

- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `tests/unit/test_fee_rule_matcher.py`
- `docs/task_board.md` board residual

Integrator must isolate these unless a separate owner explicitly claims them.

## Validation Commands

Backend contact plan/service/API/Fee authority focused suite:

```powershell
py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/unit/test_matrix_contact_measurement_schema_migration.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/unit/test_confirmed_matrix_fee_step_quantities.py tests/unit/test_confirmed_matrix_fee_draft_service.py tests/unit/test_fee_default_fill.py tests/integration/test_matrix_step_quantity_api.py -q
```

Result: `64 passed in 9.49s`.

Generic Test Record regression suite:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_confirmed_matrix_test_record_preview_api.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
```

Result: `30 passed in 8.42s`.

Frontend Matrix Editor + contact selector suite:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors --run
```

Result: `2 files / 46 tests passed`.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed. Existing Vite chunk-size warning only.

Python compile:

```powershell
py -m py_compile backend/domain/matrix_contact_measurement_models.py backend/application/matrix_contact_plan_validation.py backend/application/matrix_step_quantity_service.py backend/application/matrix_step_quantity_authority_builder.py backend/application/confirmed_matrix_fee_step_quantities.py backend/api/routes_matrix_step_quantities.py backend/infrastructure/storage/matrix_contact_measurement_schema_migration.py backend/domain/project_matrix_draft_models.py backend/domain/confirmed_matrix_authority_models.py backend/infrastructure/storage/models_project_matrix_draft.py backend/infrastructure/storage/models_confirmed_matrix_authority.py backend/infrastructure/storage/repositories/project_matrix_draft.py backend/infrastructure/storage/repositories/confirmed_matrix_authority.py backend/infrastructure/storage/database.py
```

Result: passed.

Diff/trailing whitespace:

```powershell
git diff --check -- <TASK_360A candidate files>
Select-String -Path <TASK_360A candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Result: diff-check passed with LF/CRLF normalization warnings only. Trailing whitespace scan had no matches.

Line-count scan:

```text
471  backend/application/matrix_step_quantity_service.py
263  backend/api/routes_matrix_step_quantities.py
92   backend/application/matrix_contact_plan_validation.py
67   backend/domain/matrix_contact_measurement_models.py
137  backend/application/confirmed_matrix_fee_step_quantities.py
32   backend/infrastructure/storage/matrix_contact_measurement_schema_migration.py
200  frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx
397  frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts
3956 frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx
183  frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx
```

`MatrixEditorWorkspace.tsx` remains a pre-existing large frontend file; TASK_360A changes are localized in the existing workspace integration surface plus new card/selector files.

Scope/static scans:

- Diff-only scan for `TASK_360B`, workbook generation, specialized workbook, StepInstance, report generation, real-folder paths, public-drive/public drive, and Test Record copy in TASK_360A product/test candidates produced no blocking matches.
- `git diff --name-only` for generic Test Record implementation paths produced no TASK_360A-owned Test Record package changes.
- External Fee seed/rule residuals were confirmed present separately and excluded: `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`, `tests/unit/test_fee_rule_matcher.py`.

## Browser Smoke

Attempted browser tooling probe with Playwright:

```text
bundled chromium: browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system chrome: browserType.launch: spawn EPERM
```

Live browser smoke could not be completed due local browser tooling, not product behavior. This is recorded as a non-blocking tooling residual because the focused UI tests, source placement inspection, and static scans directly cover the requested behavior.

## Observations

1. Matrix Editor placement

`MatrixEditorWorkspace.tsx` renders `MatrixSchedulePlanningCard` and then `MatrixContactMeasurementPlanCard` in the main matrix section before the Group Step workspace. The Contact Measurement Plan is standalone and adjacent to Project Schedule; it is not embedded inside Project Schedule.

2. Contact family behavior

`matrixContactMeasurementPlanSelectors.ts` defines contact-family built-ins: `High Power Pin`, `Low Power Pin`, and `Signal Pin`. The card/selectors cover custom family add/edit/remove with label/count/prefix fields and derived `readings_per_sample`. Regression coverage verifies monotonic custom IDs across add/remove/reload and persisted ID collisions: `custom-llcr-1`, `custom-llcr-2`, `custom-llcr-3`, then persisted reload produces `custom-llcr-4`.

3. Target coverage and blank-only apply

Tests and source cover include/exclude state, required exclusion reason, coverage status persistence, and blank-only common apply. Backend validation rejects excluded contact targets without a reason. Common apply skips excluded/manual/nonblank targets and preserves overrides.

4. Group-Step authority

Contact plan is stored in draft and confirmed Matrix Step quantity authority. Confirmed authority snapshot carries the same contact plan data forward without introducing a separate authority source.

5. Fee passive consumption

Fee authority uses confirmed Matrix Step contact-plan `readings_per_sample` per existing Group+Step and sample quantity context. Focused tests verify confirmed contact-plan readings are preferred and multiple steps are not collapsed into cross-Step aggregation.

6. Generic Test Record and TASK_360B

Generic Test Record preview/document/API regression suite passed (`30 passed`). Diff/static scans found no TASK_360B workbook generation or specialized workbook generation scope in the TASK_360A package.

## QA Result

QA gate: pass

Blocking findings: none

Residual risk:

- Live browser smoke was not possible because local Chromium executable is missing and system Chrome launch is blocked by EPERM. Component/source/static coverage is sufficient for this QA gate.
- Integrator must stage only the TASK_360A candidate package and exclude visible external Fee seed/rule/test residuals and board residual unless separately authorized.

Recommended next role: Integrator packaging/readiness.
