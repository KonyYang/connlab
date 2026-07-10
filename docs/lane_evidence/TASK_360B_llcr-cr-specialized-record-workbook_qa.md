# TASK_360B LLCR/CR Specialized Record Workbook - QA Evidence

Date: 2026-07-10

Role: QA / Smoke Owner

Task: `TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK`

Lane: `llcr-cr-specialized-record-workbook`

Gate: QA gate

## Scope Read

- Read `AGENTS.md` and confirmed current phase is Phase 11 controlled Project Workbench / Matrix / Approval Package foundation.
- Read `docs/task_board.md`; TASK_360B is the current active implementation-authorized lane after accepted TASK_360A.
- Read `tasks/TASK_360B_LLCR_CR_SPECIALIZED_RECORD_WORKBOOK.md`.
- Read `docs/task_360b_llcr_cr_specialized_record_workbook_plan.md`.
- Read Planner evidence:
  - `docs/lane_evidence/TASK_360B_llcr-cr-specialized-record-workbook_planner.md`
  - `docs/lane_evidence/TASK_360B_llcr-cr-specialized-record-workbook_planner_fix.md`
  - `docs/lane_evidence/TASK_360B_llcr-cr-specialized-record-workbook_reconciliation_planner.md`
- Read Developer evidence: `docs/lane_evidence/TASK_360B_llcr-cr-specialized-record-workbook_developer.md`.
- Read Reviewer evidence: `docs/lane_evidence/TASK_360B_llcr-cr-specialized-record-workbook_reviewer.md`.
- Inspected actual worktree status and candidate diff boundaries.

QA did not modify product code, tests, board, package state, real public-drive data, real LTR workbook files, or real project folders. This file is QA evidence only.

## Candidate Package / External Residuals

Observed TASK_360B candidate package:

- Dedicated LLCR/CR projection, preview, generation, artifact store, workbook gateway, route, dependency/main wiring.
- Typed frontend API helper, Matrix Contact Measurement Plan inline card row, Matrix Editor wiring, scoped CSS, and focused tests.
- TASK_360B task/plan/evidence files.

External residuals visible in the worktree and excluded from the TASK_360B package decision:

- `backend/modules/fee_evaluation/fee_default_fill.py`
- `backend/modules/fee_evaluation/seeds/fee_rules_v2026_06_03.json`
- `tests/unit/test_confirmed_matrix_fee_draft_service.py`
- `tests/unit/test_fee_default_fill.py`
- `tests/unit/test_fee_rule_matcher.py`
- `docs/task_board.md` board residual

Integrator must isolate these unless a separate owner explicitly claims them.

## Validation Commands

Backend/API/authority/generic Test Record suite:

```powershell
py -m pytest tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py tests/unit/test_llcr_cr_specialized_record_workbook_gateway.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py tests/unit/test_confirmed_matrix_authority_service.py tests/unit/test_confirmed_matrix_authority_repository.py tests/unit/test_confirmed_matrix_fee_step_quantities.py tests/unit/test_confirmed_matrix_test_record_preview_service.py tests/unit/test_confirmed_matrix_test_record_document_generation_service.py tests/integration/test_llcr_cr_specialized_record_workbook_api.py tests/integration/test_confirmed_matrix_test_record_preview_api.py tests/integration/test_confirmed_matrix_test_record_generation_api.py -q
```

Result: `59 passed in 9.14s`.

Frontend Matrix card/model/workspace suite:

```powershell
cd frontend
npm test -- MatrixEditorWorkspace MatrixContactMeasurementPlanCard useLlcrCrSpecializedRecordWorkbookModel --run
```

Result: `3 files / 44 tests passed`.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed. Existing Vite chunk-size warning only.

Python compile:

```powershell
py -m py_compile backend/application/confirmed_matrix_llcr_cr_record_projection.py backend/application/confirmed_matrix_llcr_cr_record_preview_service.py backend/application/confirmed_matrix_llcr_cr_record_generation_service.py backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py backend/api/dependencies.py backend/api/main.py
```

Result: passed.

Diff/trailing whitespace:

```powershell
git diff --check -- <TASK_360B candidate files>
Select-String -Path <TASK_360B candidate files> -Pattern '[ \t]+$' -Encoding UTF8
```

Result: diff-check passed with LF/CRLF normalization warnings only. Trailing whitespace scan had no matches.

Line-count scan:

```text
276 backend/application/confirmed_matrix_llcr_cr_record_projection.py
38  backend/application/confirmed_matrix_llcr_cr_record_preview_service.py
99  backend/application/confirmed_matrix_llcr_cr_record_generation_service.py
67  backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py
146 backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py
236 backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py
80  frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts
282 frontend/src/features/matrix-editor/MatrixContactMeasurementPlanCard.tsx
```

Scope/static scans:

- Diff-only scan for VBA/XLSM/Excel COM, Fee, parser, StepInstance, Report generation, public-drive/public drive, and real `D:\...` path references in TASK_360B product/test candidates produced no blocking matches.
- Feature-level raw `fetch(` scan under Matrix Editor/page surfaces produced no matches; requests stay through `frontend/src/api/client.ts`.
- `git diff --name-only` confirmed visible Fee residuals are separate from TASK_360B and must remain excluded.

## Preview-First Artifact Smoke

Executed a disposable temp-dir artifact probe using the existing TASK_360B service fixture. No real public-drive, LTR workbook, or project folder path was touched.

Observed output:

```text
preview ready 1 True
stale_rejected True xlsx_after_stale 0
artifact_parent generated_llcr_cr_record_files\project-1
artifact_name project-1_llcr_cr_record_r4_a56702e8c18141d78c62c907e4c361b5.xlsx
sheets Record Summary|LLCR Record|CR Record
headers Type|Group|Source Step|Sample|Contact ID|Contact Label|Initial|After|Final|Result|Remarks
contact SIG1 Signal contact
formulas =IF(COUNT(G4:G4)=0,"",AVERAGE(G4:G4)) =IF(COUNTA(J4:J4)=0,"",COUNTIF(J4:J4,"PASS")&"/"&COUNTA(J4:J4))
has_vba False
temp_exists_after_cleanup False
```

This confirms:

- Preview creates no workbook.
- Stale preview fingerprint blocks generation and leaves zero `.xlsx` files.
- Generate writes only under app-managed `generated_llcr_cr_record_files/<project>` in temp scope.
- Generated workbook has fixed sheet order, fixed columns, manual measurement cells, guarded formulas, and no `vbaProject.bin`.
- Temporary artifact directory was cleaned up after the probe.

## Behavior Coverage

1. Confirmed snapshot authority

The preview/generate path reads active `ConfirmedMatrixSnapshot` contact-plan data only. Draft Matrix, Basic Information, Fee, generic Test Record, and generated workbook values are not authority.

2. Expansion and blockers

Focused projection/API tests cover positive integer family expansion, zero omission, invalid decimal/negative/blank/non-numeric count blockers, no rounding, readings-per-sample sum validation, and no-output-on-blocker behavior.

3. Prefix collisions

Focused projection/API/frontend tests cover same-section normalized prefix collision diagnostics with both conflicting IDs and labels. Separate-section prefix reuse remains permitted.

4. Stale preview and download lifecycle

Focused generation/API tests and the temp-dir probe cover stale fingerprint rejection, preview-before-write, opaque artifact ID/download URL, contained artifact resolution, and absence of absolute output paths in API payloads.

5. UI placement and generic Test Record isolation

Frontend tests cover the compact inline LLCR/CR record workbook row inside `MatrixContactMeasurementPlanCard`, Preview/Generate/Download states, concise blocker copy, and the generic top `Test record` path not being reused. Generic Test Record preview/document API regression tests passed in the 59-test backend suite.

6. Locked scope

No TASK_360B package change was found for generic Test Record/Word output semantics, VBA/XLSM/COM, Fee rule/default-fill behavior, Matrix parser/import, StepInstance, full Report, LTR/public-drive, real workbook/folder mutation, `.agents/**`, or `docs/project_management/**`.

## Browser Smoke

Attempted local browser tooling probe with Playwright:

```text
bundled chromium: browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system chrome: browserType.launch: spawn EPERM
```

Live browser smoke could not be completed due local browser tooling, not product behavior. This is recorded as a non-blocking tooling residual because focused frontend tests, API tests, source/static scans, and the temp-dir artifact probe cover the requested functional and artifact behavior.

## QA Result

QA gate: pass

Blocking findings: none

Residual risk:

- Live browser smoke is unavailable in this thread because bundled Chromium is missing and system Chrome launch is blocked by EPERM.
- Integrator must stage only the TASK_360B candidate package and exclude visible external Fee residuals and board residual unless separately authorized.

Recommended next role: Integrator packaging/readiness.
