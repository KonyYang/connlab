# TASK_357C Matrix Step Quantity Setup - QA Evidence

Date: 2026-07-08

Role: QA / Smoke Owner

Task: `TASK_357C_MATRIX_STEP_QUANTITY_SETUP`

Lane: `matrix-step-quantity-setup`

Result: `qa_pass`

Recommended next role: Integrator packaging/readiness

## Scope Read

QA re-read the task, plan, Developer evidence, Reviewer evidence, reconciliation evidence, and prior TASK_357A/TASK_357B context for quantity authority and Basic Information quantity defaults.

Current allowed scope is Matrix Step quantity setup only:

- Draft and confirmed Matrix Step quantity storage/repository/domain/API support.
- Matrix Step quantity service and authority builder.
- Confirmed Matrix revision carry-forward support.
- Matrix Editor Step quantity panel, selectors, client helper, CSS, and focused tests.
- Duplicate no-suffix identity regression coverage from Reviewer B1.

Locked scope remains excluded:

- Fee Evaluation consumption/default-fill.
- Test Record or Report reuse.
- StepInstance or execution persistence.
- Matrix parser/import rule changes.
- LTR/public-drive authority changes.
- Project Workbench or Projects registry changes.
- `.agents/**`, `docs/project_management/**`, release/package cleanup, and unrelated residuals.

## Candidate Package Status

Observed TASK_357C candidate files are limited to backend Matrix quantity/domain/storage/API/service files, Matrix Editor quantity UI/client/test/CSS files, focused backend/frontend tests, and TASK_357C task/plan/evidence files.

External dirty residuals remain visible elsewhere in the worktree, including Settings/LTR, release/desktop/packaging, and `temp_agents_stash.md`. QA treats those as excluded from TASK_357C packaging.

## Validation Commands

### Backend focused TASK_357C and B1 regression suite

Command:

```powershell
py -m pytest tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_replaces_step_quantities tests/unit/test_project_matrix_draft_repository.py::test_project_matrix_draft_repository_rejects_duplicate_no_suffix_step_quantity tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_roundtrips_step_quantities tests/unit/test_confirmed_matrix_authority_repository.py::test_confirmed_matrix_authority_repository_rejects_duplicate_no_suffix_step_quantity tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_matrix_revision_flow_service.py tests/integration/test_matrix_revision_flow_api.py -q
```

Observed result: `30 passed in 6.90s`.

Coverage confirmed:

- Matrix Step quantity service load/save paths.
- Draft API save/load paths.
- Duplicate no-suffix save payload rejection.
- Draft repository duplicate no-suffix storage rejection.
- Confirmed repository duplicate no-suffix storage rejection.
- Confirmed Matrix service and revision carry-forward behavior.

### Backend compile

Command:

```powershell
py -m py_compile backend/application/matrix_step_quantity_service.py backend/application/matrix_step_quantity_authority_builder.py backend/application/confirmed_matrix_authority_service.py backend/application/matrix_revision_flow_service.py backend/infrastructure/storage/repositories/project_matrix_draft.py backend/infrastructure/storage/repositories/confirmed_matrix_authority.py backend/api/routes_matrix_step_quantities.py backend/api/main.py backend/domain/project_matrix_draft_models.py backend/domain/confirmed_matrix_authority_models.py backend/infrastructure/storage/models_project_matrix_draft.py backend/infrastructure/storage/models_confirmed_matrix_authority.py
```

Observed result: passed with no output.

### Frontend Matrix Editor focused tests

Command:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace --run
```

Observed result: `1 file / 39 tests passed`.

Coverage confirmed from tests/source inspection:

- Matrix Editor renders the per-step `Step quantity setup` panel.
- Selected group quantity rows load and save through the Step quantity API path.
- Basic Information defaults can be imported into Matrix Step quantity setup.
- Manual override and clear behavior are represented through saved override rows and fallback/default source behavior.
- `Total readings` is rendered as a derived/read-only column rather than an editable input.
- Readonly/lifecycle guard behavior remains wired through Matrix Editor readonly handling.

### Frontend build

Command:

```powershell
cd frontend
npm run build
```

Observed result: passed. Existing Vite chunk-size warning only.

### Diff, whitespace, line-count, and scope checks

Command:

```powershell
git diff --check -- <TASK_357C candidate files>
```

Observed result: passed with LF/CRLF normalization warnings only.

Command:

```powershell
Select-String -Path <TASK_357C candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result: no matches.

Line-count scan:

```text
backend/application/matrix_step_quantity_service.py                  360
backend/application/matrix_step_quantity_authority_builder.py         113
backend/application/confirmed_matrix_authority_service.py             274
backend/application/matrix_revision_flow_service.py                   448
backend/infrastructure/storage/repositories/project_matrix_draft.py   356
backend/infrastructure/storage/repositories/confirmed_matrix_authority.py 293
backend/api/routes_matrix_step_quantities.py                          154
```

Observed result: checked TASK_357C Python files remain below the 500-line hard limit.

Forbidden-scope diff scan:

```powershell
git diff --name-only -- backend/modules/fee_evaluation frontend/src/features/fee-evaluation backend/application/confirmed_matrix_fee_draft_service.py backend/application/test_record* backend/api/routes_*test_record* backend/application/*report* backend/modules/test_plan/product_spec_matrix_parser.py backend/application/project_test_plan_matrix_preview_service.py backend/api/routes_project_test_plan.py backend/application/*ltr* backend/api/routes_ltr* frontend/src/features/project-workbench frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry .agents docs/project_management dist_release packaging scripts temp_agents_stash.md
```

Observed result: no TASK_357C candidate diff in locked paths.

## UI Behavior Assessment

QA did not find a blocking Matrix Editor behavior issue in focused tests/source inspection:

- Per-step quantity panel is present as `Step quantity setup`.
- Quantity fields are scoped to step rows and include Basic Information default import behavior.
- Manual overrides persist as `matrix_step_override`.
- Cleared/missing values fall back to default/manual-required source behavior.
- `total_readings` is derived from test points and readings per point and displayed read-only.
- Review-required/manual-required states remain explicit.
- Readonly state disables editing/saving through the panel disabled path.

## B1 Regression Assessment

B1 is accepted as closed in QA:

- Storage models persist no-suffix identity as a non-null empty-string value.
- Domain/API read shape still maps no-suffix to optional/blank presentation.
- Service rejects duplicate normalized payload identities before persistence.
- Draft and confirmed repository uniqueness reject duplicate no-suffix rows.
- Focused regression tests for duplicate no-suffix payload/storage paths passed.

## Browser Smoke

Live browser smoke was attempted at tooling level but could not be completed:

```text
bundled=browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system=browserType.launch: spawn EPERM
```

No screenshot artifact was captured. This is a non-blocking QA residual because the Matrix Editor quantity behavior is covered by focused component tests, backend/API tests, and source/static inspection. Integrator may optionally perform a manual browser spot-check if a browser is available in a less restricted environment.

## Residual Risk

- Browser-only layout issues in seeded Matrix data were not directly observed in this thread due browser tooling restrictions.
- External dirty residuals must remain excluded during packaging.

## QA Conclusion

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Integrator packaging note: stage only the TASK_357C candidate files and TASK_357C evidence/task/plan files. Exclude external Settings/LTR, release/desktop/packaging, `temp_agents_stash.md`, and other unrelated residuals.
