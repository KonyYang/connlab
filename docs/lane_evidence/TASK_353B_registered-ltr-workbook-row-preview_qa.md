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
