# TASK_353B QA Evidence - Registered LTR Workbook Row Preview

## Gate Summary

- Date: 2026-07-07
- Role: QA / Smoke Owner
- TASK_ID: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW`
- Lane: `registered-ltr-workbook-row-preview`
- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Result: `qa_pass`
- Recommended next role: Integrator packaging/readiness

Why allowed: the latest Orchestrator/Reviewer callback reports `reviewer_pass` after B1 fix and requests QA gate. `docs/task_board.md` still shows implementation authorization text, but lane evidence and the direct callback are newer for this gate. QA did not update the board.

## Scope Boundary

QA verified the TASK_353B registered-LTR read-only preview package. QA did not modify product source, tests, board, packaging, real workbooks, public-drive folders, user folders, `.agents/**`, or `docs/project_management/**`.

Candidate TASK_353B files observed:

- `backend/application/registered_ltr_workbook_row_preview_service.py`
- `backend/api/routes_ltr_workbook_registered_row_preview.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
- `tests/integration/test_registered_ltr_workbook_row_preview_api.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_qa.md`

External residuals observed and excluded include TASK_352/PDF files, Settings/LTR/template resource files, release/desktop/packaging files, `frontend/src/workbench.css`, unrelated Word/Fee output files/tests, `docs/task_board.md`, and `temp_agents_stash.md`. Integrator must package-isolate TASK_353B and not stage broad dirty files.

## Facts Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `tasks/TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW.md`
- `docs/task_353b_registered_ltr_workbook_row_preview_plan.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
- `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`
- Actual `git status` / TASK_353B diff scope
- Registered-row preview service/API/client/UI tests and Workbench wiring files

## Validation Commands

### Backend registered-row focused tests

Command:

```powershell
py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py -q
```

Observed result:

```text
9 passed in 2.22s
```

Coverage notes:

- Registered LTR preview returns row data through a project-id-only API.
- No registered LTR / not found / duplicate / workbook read-open failure paths return readable preview states.
- B1 regression is covered: workbook open/read failures map to `status="blocked"` with no row values and no unhandled 500.

### Backend regression suite

Command:

```powershell
py -m pytest tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q
```

Observed result:

```text
42 passed in 2.33s
```

Coverage notes:

- Existing Basic Information sync preview/commit behavior remains separate.
- Existing Basic Information sync commit gate remains intact.
- TASK_349A specified-LTR authority preview regressions remain passing.

### Frontend side-card tests

Command:

```powershell
cd frontend
npm test -- ProjectBasicInformationSummaryCard --run
```

Observed result:

```text
1 file / 10 tests passed
```

Coverage notes:

- `LTR workbook row preview` and `Update LTR from Basic Information` are separate actions.
- Read-only row preview can be available without Basic Information confirmation when a registered project reference is present.
- Read-only preview renders workbook row fields and does not render `Confirm update`.
- Existing update/sync action remains confirmed-Basic-Information gated and preserves the commit flow.
- Blocked/not-found states are visible through focused component coverage.

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

Notes:

- Existing Vite chunk-size warning only.

### Python compile

Command:

```powershell
py -m py_compile backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py backend/api/dependencies.py backend/api/main.py
```

Observed result:

```text
passed
```

### Diff / whitespace / scope scans

Command:

```powershell
git diff --check -- backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py backend/api/dependencies.py backend/api/main.py tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py frontend/src/api/client.ts frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md
```

Observed result:

```text
passed with LF/CRLF warnings only
```

Command:

```powershell
Select-String -Path <TASK_353B package files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result:

```text
no matches
```

Command:

```powershell
Select-String -Path backend/application/registered_ltr_workbook_row_preview_service.py,backend/api/routes_ltr_workbook_registered_row_preview.py -Pattern 'open_transaction|run_short_transaction|commit|backup|save|preview_ack|write' -Encoding UTF8
```

Observed result:

```text
no matches
```

Command:

```powershell
git diff --name-only -- .agents docs/project_management backend/infrastructure/office/excel_com_ltr_workbook_gateway.py backend/infrastructure/storage
```

Observed result:

```text
no matches
```

No-real-folder scan note: focused tests contain fake fixture/assertion strings such as `D:/PublicProject/LTR.xlsx`; no command or product code path wrote to that path during QA.

## Browser / Manual Smoke

Live browser smoke was not executed because browser automation is unavailable in this thread:

```text
bundled=browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system=browserType.launch: spawn EPERM
```

Disposition: non-blocking tooling residual. The critical operator behavior is covered by backend API/service tests plus focused `ProjectBasicInformationSummaryCard` component tests. No screenshot artifact was produced.

## QA Result

`QA gate: pass`

No blocking TASK_353B defect was found. The registered-LTR workbook row preview validates as read-only, returns readable blocked results for workbook open/read failures, and stays separated from the write-capable `Update LTR from Basic Information` sync flow.

## Residual Risk

- Browser smoke remains pending due local browser tooling failure, not product failure.
- Integrator must stage only TASK_353B candidate files/hunks and exclude visible external residuals, especially shared dirty files such as `backend/api/dependencies.py`, `backend/api/main.py`, `frontend/src/api/client.ts`, Workbench files, and unrelated release/settings/TASK_352 residuals.
- Existing Vite chunk-size warning remains non-blocking.

---

## Correction QA Re-Gate - TASK_353B / TASK_353C User Direction Alignment

### Gate Summary

- Date: 2026-07-07
- Role: QA / Smoke Owner
- TASK_ID: `TASK_353B_REGISTERED_LTR_WORKBOOK_ROW_PREVIEW` / corrective scope aligned with `TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT`
- Lane: `registered-ltr-workbook-row-preview` / `ltr-update-preview-minimal-registered-ltr-enablement`
- Result: `qa_pass`
- Recommended next role: Planner/source-of-truth reconciliation before Integrator packaging/readiness

This section supersedes the earlier QA result for the independent `LTR workbook row preview` product direction. The user correction rejects that separate row-preview workflow and keeps only the original `LTR update preview` entry.

### Facts Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `tasks/TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT.md`
- `docs/task_353c_ltr_update_preview_minimal_registered_ltr_enablement_plan.md`
- `docs/lane_evidence/TASK_353C_ltr-update-preview-minimal-registered-ltr-enablement_planner.md`
- `docs/lane_evidence/TASK_353C_ltr-update-preview-minimal-registered-ltr-enablement_reviewer.md`
- Updated `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md`
- Updated `docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md`
- Current diff/status for the corrective package and external residuals

Board/source-of-truth note: `docs/task_board.md` currently says `TASK_353C_LTR_UPDATE_PREVIEW_MINIMAL_REGISTERED_LTR_ENABLEMENT` is planned / ready for Reviewer plan gate, while the latest Reviewer callback and TASK_353B evidence show a completed correction implementation re-gate. QA treats this as a non-product source-of-truth mismatch and recommends Planner reconciliation before packaging.

### Corrective Package Observed

Observed correction-owned product/test changes:

- `backend/application/project_basic_information_output.py`
- `backend/application/ltr_workbook_basic_information_sync_service.py`
- `tests/unit/test_ltr_workbook_basic_information_sync_service.py`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx`
- `frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/api/client.ts`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- deleted rejected files:
  - `backend/application/registered_ltr_workbook_row_preview_service.py`
  - `backend/api/routes_ltr_workbook_registered_row_preview.py`
  - `tests/unit/test_registered_ltr_workbook_row_preview_service.py`
  - `tests/integration/test_registered_ltr_workbook_row_preview_api.py`

External residuals still visible and excluded: TASK_352/PDF files, Settings/LTR/template resources, release/desktop/packaging files, Fee/Word output files/tests, `frontend/src/workbench.css`, `docs/task_board.md`, and `temp_agents_stash.md`.

### Validation Commands

Command:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py -q
```

Observed result:

```text
19 passed in 0.97s
```

Command:

```powershell
py -m pytest tests/unit/test_ltr_workbook_basic_information_sync_service.py tests/integration/test_ltr_workbook_basic_information_sync_api.py tests/unit/test_specified_ltr_workbook_authority_preview_service.py -q
```

Observed result:

```text
34 passed in 2.75s
```

Coverage notes:

- Registered-LTR + unconfirmed Basic Information preview can use preview/draft snapshot behavior.
- Commit remains gated by `_require_basic_information(...)`, preview acknowledgement, operator confirmation, expected confirmed version/hash, lifecycle write guard, and workbook write transaction.
- TASK_349A specified LTR authority preview regression remains passing.

Command:

```powershell
cd frontend
npm test -- ProjectBasicInformationSummaryCard --run
```

Observed result:

```text
1 file / 10 tests passed
```

Coverage notes:

- Only `LTR update preview` is present as the LTR workbook action.
- Registered-LTR + unconfirmed Basic Information can open the existing preview path.
- `Confirm update` is disabled for unconfirmed/draft preview because confirmed version/hash are null.
- No registered LTR remains disabled/blocked.
- Confirmed Basic Information update flow remains covered.

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

Command:

```powershell
py -m py_compile backend/application/project_basic_information_output.py backend/application/ltr_workbook_basic_information_sync_service.py backend/api/dependencies.py backend/api/main.py
```

Observed result:

```text
passed
```

Command:

```powershell
git diff --check -- backend/application/project_basic_information_output.py backend/application/ltr_workbook_basic_information_sync_service.py tests/unit/test_ltr_workbook_basic_information_sync_service.py frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.tsx frontend/src/features/project-basic-information/ProjectBasicInformationSummaryCard.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/api/client.ts backend/api/dependencies.py backend/api/main.py backend/application/registered_ltr_workbook_row_preview_service.py backend/api/routes_ltr_workbook_registered_row_preview.py tests/unit/test_registered_ltr_workbook_row_preview_service.py tests/integration/test_registered_ltr_workbook_row_preview_api.py docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_developer.md docs/lane_evidence/TASK_353B_registered-ltr-workbook-row-preview_reviewer.md
```

Observed result:

```text
passed with LF/CRLF warnings only
```

Command:

```powershell
Select-String -Path <corrective package files> -Pattern '[ \t]+$' -Encoding UTF8
```

Observed result:

```text
no matches
```

Command:

```powershell
git diff --name-only -- .agents docs/project_management backend/infrastructure/storage backend/infrastructure/office/excel_com_ltr_workbook_gateway.py
```

Observed result:

```text
no matches
```

### Static Behavior / Rejected Surface Scans

Command:

```powershell
rg -n "registered-row-preview|RegisteredLtrWorkbookRowPreview|previewRegisteredLtrWorkbookRow|LTR workbook row preview|Update LTR from Basic Information" backend frontend tests
```

Observed result:

```text
no product/test references to the rejected registered-row surface
```

The only remaining broad-string hits were old generic no-write LTR workbook row preview docstrings in:

- `backend/api/routes_ltr.py`
- `backend/application/ltr_workbook_write_preview_service.py`

These are not the rejected TASK_353B independent registered-row workflow.

Source inspection notes:

- `ProjectBasicInformationSummaryCard.tsx` renders `LTR update preview` and `Confirm update`; no second `LTR workbook row preview` / `Update LTR from Basic Information` split remains.
- `ProjectBasicInformationSummaryCard.test.tsx` covers unconfirmed initial Basic Information preview opening through `LTR update preview` and disabled `Confirm update`.
- `LtrWorkbookBasicInformationSyncService.commit(...)` still calls `_require_basic_information(...)` and retains preview acknowledgement / operator confirmation / expected confirmed version-hash requirements.

### Browser / Manual Smoke

Live browser smoke was not executed because browser automation is unavailable in this thread:

```text
bundled=browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
system=browserType.launch: spawn EPERM
```

Disposition: non-blocking tooling residual. The corrected behavior is covered by focused backend service/API regressions and `ProjectBasicInformationSummaryCard` tests.

### QA Result

`QA gate: pass`

No blocking corrective-scope product defect was found. The rejected independent `LTR workbook row preview` surface is removed from product/test references, the original `LTR update preview` entry is the sole visible action, registered-LTR unconfirmed Basic Information preview is enabled, and `Confirm update` remains disabled/blocked until confirmed Basic Information safety requirements are met.

### Residual Risk / Next Role

- Browser smoke remains unavailable due local tooling failure.
- `docs/task_board.md` still presents TASK_353C as planned / Reviewer plan gate while TASK_353B evidence now contains the implemented correction and Reviewer pass. QA recommends Planner/source-of-truth reconciliation before Integrator packaging/readiness.
- Integrator must hunk/file isolate the corrective package and exclude external TASK_352/PDF, Settings/LTR/template, release/desktop/packaging, Fee/Word, `workbench.css`, board, and temp-stash residuals.
