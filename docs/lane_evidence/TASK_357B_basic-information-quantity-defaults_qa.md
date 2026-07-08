# TASK_357B QA Evidence - Basic Information Quantity Defaults

## Gate Summary

- Date: 2026-07-08
- Role: QA / Smoke Owner
- TASK_ID: `TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS`
- Lane: `basic-information-quantity-defaults`
- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Result: `qa_pass`
- Recommended next role: Integrator packaging/readiness

Why allowed: the latest Reviewer callback reports `reviewer_implementation_pass` and requests QA gate. QA did not update `docs/task_board.md`, product code, tests, packaging, commits, or real workbook/folder data.

## Scope Boundary

QA verified TASK_357B only: Basic Information project-level quantity defaults.

Validated field scope:

- `test_points_per_sample`
- `readings_per_point`
- `contact_points_per_sample`

`total_readings` remains omitted from Basic Information persistence/UI as downstream/derived scope.

Candidate TASK_357B files observed:

- `backend/application/project_basic_information_service.py`
- `backend/application/project_basic_information_source.py`
- `backend/api/routes_project_basic_information.py`
- `frontend/src/features/project-basic-information/basicInformationFieldConfig.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx`
- `tests/unit/test_project_basic_information_service.py`
- `tests/unit/test_project_basic_information_repository.py`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reviewer.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_qa.md`

External residuals observed and excluded include Settings/LTR helper files, desktop/release/packaging files, `dist_release/**`, `packaging/**`, release scripts, frontend New Project test residuals, release/settings tests, `temp_agents_stash.md`, and `docs/task_board.md`.

## Facts Read

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/task_board.md`
- `tasks/TASK_357A_MATRIX_QUANTITY_AUTHORITY_CONTRACT.md`
- `docs/task_357a_matrix_quantity_authority_contract_plan.md`
- `docs/lane_evidence/TASK_357A_matrix-quantity-authority-contract_reconciliation_planner.md`
- `tasks/TASK_357B_BASIC_INFORMATION_QUANTITY_DEFAULTS.md`
- `docs/task_357b_basic_information_quantity_defaults_plan.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_planner.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reconciliation_planner.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md`
- `docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reviewer.md`
- Current `git status` and TASK_357B product/test diff scope

## Validation Commands

### Backend focused tests

Command:

```powershell
py -m pytest tests/unit/test_project_basic_information_service.py tests/unit/test_project_basic_information_repository.py -q
```

Observed result:

```text
19 passed in 1.68s
```

Coverage notes:

- Blank quantity defaults are accepted and omitted/cleaned as optional values.
- Non-negative decimals round-trip through Basic Information values-map persistence.
- Invalid values block confirmation with business-readable quantity field labels.
- Values-map persistence works without schema migration.

### Python compile

Command:

```powershell
py -m py_compile backend/application/project_basic_information_service.py backend/application/project_basic_information_source.py backend/api/routes_project_basic_information.py
```

Observed result:

```text
passed
```

### Frontend focused tests

Command:

```powershell
cd frontend
npm test -- ProjectBasicInformationWorkspace --run
```

Observed result:

```text
1 file / 20 tests passed
```

Coverage notes:

- `Quantity defaults` appears in the config-driven Basic Information UI.
- `Test points / sample`, `Readings / point`, and `Contact points / sample` fields are present.
- Invalid quantity defaults block Confirm and show a user-visible validation message.
- Quantity inputs are disabled in readonly lifecycle state.
- Valid quantity defaults are included in Basic Information confirm payload.

### Frontend build

Command:

```powershell
cd frontend
npm run build
```

Observed result:

```text
passed
```

Notes: existing Vite chunk-size warning only.

### Diff / whitespace checks

Command:

```powershell
git diff --check -- backend/application/project_basic_information_service.py backend/application/project_basic_information_source.py backend/api/routes_project_basic_information.py frontend/src/features/project-basic-information/basicInformationFieldConfig.ts frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx tests/unit/test_project_basic_information_service.py tests/unit/test_project_basic_information_repository.py docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_developer.md docs/lane_evidence/TASK_357B_basic-information-quantity-defaults_reviewer.md
```

Observed result:

```text
passed with LF/CRLF warnings only
```

Command:

```powershell
Select-String -Path <TASK_357B package files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result:

```text
no matches
```

## Static / Scope Checks

Field reference scan:

```powershell
rg -n "test_points_per_sample|readings_per_point|contact_points_per_sample|total_readings" backend frontend tests
```

Observed result:

- TASK_357B quantity fields appear in Basic Information service/UI/tests and repository tests.
- The only non-TASK_357B hit was an existing Fee default-fill test name containing `total_readings`; no TASK_357B Fee consumption path was introduced.

Locked-path status:

```powershell
git status --short -- frontend/src/api/client.ts frontend/src/features/matrix-editor backend/modules/fee_evaluation backend/application/confirmed_matrix_fee_draft_service.py backend/application/project_matrix_* backend/domain/project_matrix_draft_models.py backend/domain/confirmed_matrix_authority_models.py .agents docs/project_management dist_release packaging scripts temp_agents_stash.md
```

Observed result:

- No TASK_357B changes in API client, Matrix Editor, Fee modules, Matrix authority files, `.agents/**`, or `docs/project_management/**`.
- External residuals remain under `dist_release/**`, `packaging/**`, release scripts, and `temp_agents_stash.md`; these must be excluded.

Additional source/test spot checks confirmed:

- `backend/api/routes_project_basic_information.py` returns structured 422 for invalid Basic Information quantity defaults.
- `ProjectBasicInformationWorkspace.tsx` exposes `aria-label="Quantity default validation"` for the validation surface.
- `basicInformationFieldConfig.ts` adds the compact `Quantity defaults` group with the three approved fields.
- No Matrix Step override, Fee Evaluation consumption/default-fill, Test Record, Report, LTR workbook/public-drive, schema migration, API client, `.agents/**`, or `docs/project_management/**` change was introduced by TASK_357B.

## Browser / Manual Smoke

Live browser smoke was not executed because browser automation is unavailable in this thread:

```text
bundled=browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system=browserType.launch: spawn EPERM
```

Disposition: non-blocking tooling residual. The UI behavior required by this gate is covered by focused `ProjectBasicInformationWorkspace` component tests and source inspection.

## QA Result

`QA gate: pass`

No blocking TASK_357B defect was found. Basic Information quantity defaults validate as optional project-level defaults only, with blank/non-negative decimals accepted, invalid values blocking confirmation, readonly disabling inputs, and no downstream Matrix/Fee/Test Record/Report/LTR scope introduced.

## Residual Risk

- Browser smoke remains unavailable due local tooling failure, not an observed product failure.
- Existing Vite chunk-size warning remains non-blocking.
- Integrator must package-isolate only TASK_357B candidate files/hunks and exclude external Settings/LTR, release/desktop/packaging, dist/release, scripts, New Project test, and temp-stash residuals.
