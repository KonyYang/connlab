# TASK_360G Matrix Contact Plan Confirmation Persistence - QA Evidence

Date: 2026-07-11

Role: QA / Smoke Owner

Task: `TASK_360G_MATRIX_CONTACT_PLAN_CONFIRMATION_PERSISTENCE`

Lane: `matrix-contact-plan-confirmation-persistence`

Gate: QA gate

## Scope Read

- Read `AGENTS.md` and confirmed current phase is Phase 11 controlled Project Workbench / Matrix / Approval Package foundation.
- Read `docs/task_board.md`; TASK_360G is the current active implementation-authorized lane after accepted TASK_360A/B/C.
- Read `tasks/TASK_360G_MATRIX_CONTACT_PLAN_CONFIRMATION_PERSISTENCE.md`.
- Read `docs/task_360g_matrix_contact_plan_confirmation_persistence_plan.md`.
- Read Planner/reconciliation evidence:
  - `docs/lane_evidence/TASK_360G_matrix-contact-plan-confirmation-persistence_planner.md`
  - `docs/lane_evidence/TASK_360G_matrix-contact-plan-confirmation-persistence_reconciliation_planner.md`
- Read Developer evidence: `docs/lane_evidence/TASK_360G_matrix-contact-plan-confirmation-persistence_developer.md`.
- Read Reviewer evidence: `docs/lane_evidence/TASK_360G_matrix-contact-plan-confirmation-persistence_reviewer.md`.
- Inspected actual worktree status and candidate diff boundaries.

QA did not modify product code, tests, board, package state, real public-drive data, real LTR workbook files, or real project folders. This file is QA evidence only.

## Candidate Package / External Residuals

Observed TASK_360G candidate package:

- `backend/application/matrix_editor_session_service.py`
- `backend/application/matrix_step_quantity_authority_comparison.py`
- `tests/unit/test_matrix_editor_session_service.py`
- `tests/unit/test_matrix_step_quantity_authority_comparison.py`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts`
- `frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.test.ts`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_360G task/plan/evidence files

External residuals visible in the worktree and excluded from the TASK_360G package decision:

- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `backend/modules/test_plan/mcr_text_normalizer.py`
- `backend/modules/test_plan/spec_section_text_extractor.py`
- `frontend/src/workbench.css`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_fee_default_fill.py`
- `tests/unit/test_fee_rule_matcher.py`
- `tests/unit/test_frontend_shell_files.py`
- `tests/unit/test_mcr_text_normalizer.py`
- `tests/unit/test_spec_section_text_extractor.py`
- `docs/task_board.md`
- `docs/superpowers/`
- Untracked future task files `TASK_360D` through `TASK_360K`

Integrator must isolate these unless a separate owner explicitly claims them.

## Validation Commands

Focused frontend Matrix Editor/contact selector/card suite:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace matrixContactMeasurementPlanSelectors MatrixContactMeasurementPlanCard --run
```

Result: `3 files / 56 tests passed`.

Backend authority/session/API suite:

```powershell
py -m pytest tests/unit/test_matrix_step_quantity_authority_comparison.py tests/unit/test_matrix_editor_session_service.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/integration/test_matrix_editor_session_api.py tests/integration/test_matrix_step_quantity_api.py -q
```

Result: `52 passed in 13.43s`.

Confirmed-only TASK_360B/Fee downstream regression:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py tests/integration/test_llcr_cr_specialized_record_workbook_api.py tests/unit/test_confirmed_matrix_fee_step_quantities.py -q
```

Result: `9 passed in 4.83s`.

Python compile:

```powershell
py -m py_compile backend/application/matrix_editor_session_service.py backend/application/matrix_step_quantity_authority_comparison.py
```

Result: passed.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed. Existing Vite chunk-size warning only.

Diff/trailing whitespace:

```powershell
git diff --check -- <TASK_360G candidate files>
Select-String -Path <TASK_360G candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Result: diff-check passed with LF/CRLF normalization warnings only. Trailing whitespace scan had no matches.

Line-count scan:

```text
1895 backend/application/matrix_editor_session_service.py
150  backend/application/matrix_step_quantity_authority_comparison.py
463  frontend/src/features/matrix-editor/matrixContactMeasurementPlanSelectors.ts
4045 frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx
```

`matrix_editor_session_service.py` and `MatrixEditorWorkspace.tsx` are pre-existing large files. TASK_360G keeps canonical comparison isolated in the new 150-line helper.

Scope/static scans:

- Candidate diff shows the expected canonical comparison/session-confirm changes and uniform hydration selector changes.
- Diff-only forbidden scan found no TASK_360G schema/model/repository/migration/API-client/Fee default-fill/TASK_360B artifact/generic Test Record/parser/StepInstance/Report/LTR/public-drive/real path implementation changes.
- Diff-only matches for Fee were limited to existing fee-rebase promotion fields in `matrix_editor_session_service.py`, not new Fee default-fill or rule behavior.
- Frontend selector tests cover normal-plus-override and override-only persisted plans; both keep target authority and surface `Contact plans differ by target. Review target coverage.`

## Controlled Fixture Smoke

Executed a disposable temp SQLite/API fixture using existing integration helpers. No real user project, public-drive, LTR workbook, or real project folder was touched.

Smoke flow:

1. Create and confirm a base Matrix in a temp DB.
2. Verify TASK_360B confirmed-snapshot preview is empty before a contact plan is confirmed.
3. Create a revision draft.
4. Save the Matrix editor session draft and capture its saved payload signature.
5. Save Contact Plan Step quantities on the revision draft: HP `4`, LP `5`, Signal `24`, derived readings `33`.
6. Verify TASK_360B preview remains empty before session confirmation.
7. Confirm through `/matrix-editor/session/confirm` with expected editor draft id/signature.
8. Verify publish status is `published`, revision is `2`, and active confirmed snapshot retains `readings_per_sample = 33` and family counts `4/5/24`.
9. Verify TASK_360B preview is ready from the new confirmed snapshot and managed workbook generation succeeds without exposing `output_path`.

Observed output:

```text
base_confirm 201 1
preview_before empty 0
save_session 200 True
save_quantities 200 33
preview_before_session_confirm empty 0
session_confirm 200 published 2
active_confirmed_plan 33 ['4', '5', '24']
preview_after ready 198 33
generate_after 200 False P1_llcr_cr_record_r2_5cfc7d8851f246f8ba3ff67f9067b963.xlsx
```

This confirms:

- Contact-plan-only revision changes publish a new confirmed revision through the Matrix Editor session-confirm path.
- Confirmed snapshot retains structured families and derived readings.
- TASK_360B sees the result only after reconfirmation.
- Managed workbook generation remains contained and does not expose an absolute output path.

## Browser Smoke

Attempted local browser tooling probe with Playwright:

```text
bundled chromium: browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system chrome: browserType.launch: spawn EPERM
```

Live browser smoke could not be completed due local browser tooling, not product behavior. This is recorded as a non-blocking tooling residual because focused frontend tests plus the controlled API fixture cover the required state-writing flow.

## QA Result

QA gate: pass

Blocking findings: none

Residual risk:

- Live browser smoke is unavailable in this thread because bundled Chromium is missing and system Chrome launch is blocked by EPERM.
- Integrator must stage only the TASK_360G candidate package and exclude visible external Fee, parser, CSS, board, docs, shell-test, and future-task residuals unless separately authorized.

Recommended next role: Integrator packaging/readiness.
