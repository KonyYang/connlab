# TASK_360C Matrix Contact Plan Revision-Draft Enablement - QA Evidence

Date: 2026-07-11

Role: QA / Smoke Owner

Task: `TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT`

Lane: `matrix-contact-plan-revision-draft-enablement`

Gate: QA gate

## Scope Read

- Read `AGENTS.md` and confirmed current phase is Phase 11 controlled Project Workbench / Matrix / Approval Package foundation.
- Read `docs/task_board.md`; TASK_360C is the current active implementation-authorized lane after accepted TASK_360A and TASK_360B.
- Read `tasks/TASK_360C_MATRIX_CONTACT_PLAN_REVISION_DRAFT_ENABLEMENT.md`.
- Read `docs/task_360c_matrix_contact_plan_revision_draft_enablement_plan.md`.
- Read Planner/reconciliation evidence:
  - `docs/lane_evidence/TASK_360C_matrix-contact-plan-revision-draft-enablement_planner.md`
  - `docs/lane_evidence/TASK_360C_matrix-contact-plan-revision-draft-enablement_reconciliation_planner.md`
- Read Developer evidence: `docs/lane_evidence/TASK_360C_matrix-contact-plan-revision-draft-enablement_developer.md`.
- Read Reviewer evidence: `docs/lane_evidence/TASK_360C_matrix-contact-plan-revision-draft-enablement_reviewer.md`.
- Inspected actual worktree status and candidate diff boundaries.

QA did not modify product code, tests, board, package state, real public-drive data, real LTR workbook files, or real project folders. This file is QA evidence only.

## Candidate Package / External Residuals

Observed TASK_360C candidate package:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx`
- `frontend/src/workbench.css` scoped TASK_360C bridge styles only
- TASK_360C task/plan/evidence files

External residuals visible in the worktree and excluded from the TASK_360C package decision:

- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_fee_default_fill.py`
- `tests/unit/test_fee_rule_matcher.py`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `docs/superpowers/`
- `tasks/TASK_360D_MATRIX_EDITOR_RESPONSIVE_BREAKPOINT.md`
- `tasks/TASK_360E_MATRIX_EDITOR_STEP_CARD_OVERFLOW.md`
- Existing unrelated `frontend/src/workbench.css` responsive breakpoint hunk (`1180px` to `1024px`)

Integrator must isolate these unless a separate owner explicitly claims them.

## Validation Commands

Focused frontend suite:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard --run
```

Result: `2 files / 47 tests passed`.

Backend revision and Step-quantity regression:

```powershell
py -m pytest tests/unit/test_matrix_revision_flow_service.py tests/integration/test_matrix_revision_flow_api.py tests/unit/test_matrix_step_quantity_service.py tests/integration/test_matrix_step_quantity_api.py -q
```

Result: `20 passed in 3.66s`.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed. Existing Vite chunk-size warning only.

Diff/trailing whitespace:

```powershell
git diff --check -- <TASK_360C candidate files>
Select-String -Path <TASK_360C candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Result: diff-check passed with LF/CRLF normalization warnings only. Trailing whitespace scan had no matches.

Line-count scan:

```text
4040 frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx
1827 frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx
284  frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx
9275 frontend/src/workbench.css
```

These are pre-existing large frontend/CSS surfaces. TASK_360C changes are localized bridge/card/test/style hunks.

Scope/static scans:

- Candidate diff shows expected `createMatrixRevisionDraft` usage, draftless `Open editable Matrix draft` tests, and `workbookDisabled` split.
- No TASK_360C backend, API-client, schema, Matrix revision service/route/domain, Fee, TASK_360B service, generic Test Record, Matrix parser/import, StepInstance, Report, LTR/public-drive, or real path implementation change was found.
- Candidate diff contains the unrelated `workbench.css` breakpoint hunk; it is recorded above as excluded from TASK_360C package scope.

## Controlled Fixture Smoke

Executed a disposable temp SQLite/API fixture using existing integration helpers. No real user project, public-drive, LTR workbook, or real project folder was touched.

Smoke flow:

1. Create source Matrix draft in temp DB.
2. Save old confirmed Contact Plan with `readings_per_sample = 1`.
3. Confirm base Matrix.
4. TASK_360B preview reads active confirmed snapshot.
5. Open revision draft.
6. Verify confirmed Contact Plan is carried forward.
7. Save new revision draft Contact Plan with HP `4`, LP `5`, Signal `24`, derived `readings_per_sample = 33`.
8. TASK_360B preview before reconfirm still reads old active confirmed snapshot.
9. Reconfirm revision.
10. TASK_360B preview reads the new active confirmed snapshot.
11. Generate managed `.xlsx` artifact from the new preview.

Observed output:

```text
base_draft 201
save_old_plan 200
confirm_base 201 1
preview_old 200 ready 6 1
open_revision 201
carried_forward 1 1
save_new_plan 200
preview_before_reconfirm ready 6 1
confirm_revision 201 2
preview_new 200 ready 198 33
generate_new 200 False P1_llcr_cr_record_r2_887a2b93635347209f72d770c5adae73.xlsx
xlsx_count 1
```

This confirms:

- TASK_360B preview is available before opening a revision draft and reads the active confirmed snapshot.
- Opening the revision draft carries forward confirmed Contact Plan data.
- Saving Contact Plan changes in the revision draft does not change TASK_360B preview before reconfirmation.
- Reconfirmation promotes the new Contact Plan into active confirmed authority.
- TASK_360B then reads only the new confirmed snapshot and can generate a managed `.xlsx` artifact.
- The generated response did not expose `output_path`.

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
- Integrator must stage only the TASK_360C candidate package and exclude visible external Fee, board, responsive CSS, TASK_360D/E, and docs residuals unless separately authorized.

Recommended next role: Integrator packaging/readiness.
