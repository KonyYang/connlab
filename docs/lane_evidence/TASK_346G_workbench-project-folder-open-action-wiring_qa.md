# TASK_346G Workbench Project Folder Open Action Wiring - QA Evidence

Status: qa_pass
Date: 2026-07-01
Role: QA / Smoke Owner
Task: `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`
Lane: `workbench-project-folder-open-action-wiring`

## Gate Result

QA keyboard re-smoke gate: pass.

Recommended next role: Integrator packaging/readiness.

Keyboard re-smoke result:

- B1 original hit-test blocker is closed for pointer/mouse operation: the Open button center now resolves to `BUTTON Open`, and coordinate clicks trigger `POST /api/projects/72fbbfa290294da9a507344b68ff900f/folder/open-local`.
- B2 keyboard blocker is closed: with the same Open native button focused (`button[type="button"]`, enabled, `tabIndex=0`), Enter and Space each triggered exactly one additional `open-local` request.

No product source, product tests, board, packaging files, real local/public folders, public-drive roots, or real LTR workbook files were modified by QA. This QA pass only created this evidence file and artifacts under `docs/lane_evidence/artifacts/TASK_346G_qa/`.

## QA Keyboard Re-smoke - Enter / Space Fix, 2026-07-01

Objective:

- Re-test focused `Project folder -> Open` keyboard activation on `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f` after Reviewer keyboard re-gate passed.

Service setup:

- Backend QA service: `py -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000`.
- Frontend QA service: `npm run dev -- --host 127.0.0.1`.
- Services were stopped after the re-smoke; final listener check for ports `8000` and `5173` returned no remaining listener output.

Artifacts:

- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_keyboard_resmoke_before_20260701.png`
- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_keyboard_resmoke_after_20260701.png`
- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_keyboard_resmoke_observation_20260701.json`
- `docs/lane_evidence/artifacts/TASK_346G_qa/backend_uvicorn_keyboard_resmoke_20260701_215756.out.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/backend_uvicorn_keyboard_resmoke_20260701_215756.err.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/frontend_vite_keyboard_resmoke_20260701_215828.out.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/frontend_vite_keyboard_resmoke_20260701_215828.err.log`

Live browser observations:

- Folder Actions showed `Project folder`, `Local folder available.`, and one enabled `Open` button.
- Open button was a native focused button for keyboard checks: `tag=BUTTON`, `type=button`, `disabled=false`, `tabIndex=0`.
- Open button center hit-test resolved to `BUTTON Open`, not Matrix text `Current` or another overlay.
- Backend `open-local` POST count sequence:
  - Baseline after page load: `0`.
  - After coordinate click: `1`.
  - After semantic locator click: `2`.
  - After focused Open + Enter: `3`.
  - After focused Open + Space: `4`.
- Each pointer/semantic/keyboard action therefore triggered exactly one approved `POST /api/projects/72fbbfa290294da9a507344b68ff900f/folder/open-local`.
- Browser console warnings/errors from coordinate click, semantic click, Enter, and Space: none.
- Backend log showed no `public-folder-workflow/(sync|submit|pull)/(preview|execute)` requests from Open attempts.
- Backend log showed no old `project-folder/create` or `project-folder/update` requests from Open attempts.
- QA did not observe or perform any file create/move/delete/copy operation; Open attempts were limited to the non-mutating open-local bridge path.

Lightweight closeout checks:

```powershell
git diff --check -- frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx frontend/src/workbench.css frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_qa.md docs/lane_evidence/artifacts/TASK_346G_qa
Select-String -Path docs\lane_evidence\TASK_346G_workbench-project-folder-open-action-wiring_qa.md,docs\lane_evidence\artifacts\TASK_346G_qa\*.json -Pattern '[ \t]+$' -Encoding UTF8
Select-String -Path frontend\src\features\project-workbench\ProjectFolderTaskList.tsx,frontend\src\features\project-workbench\ProjectFolderTaskList.test.tsx,frontend\src\workbench.css,frontend\src\features\project-workbench\ProjectWorkbenchLayout.test.tsx -Pattern 'D:\\Test Project|D:\\PublicProject|public-folder-workflow/(sync|submit|pull)/(preview|execute)|project-folder/(create|update)' -Encoding UTF8
```

Results:

- `git diff --check`: passed with LF/CRLF warnings only for existing frontend working-copy files.
- Trailing whitespace scan for QA evidence/artifact JSON: no matches.
- No-real-folder / forbidden endpoint scan: no matches.
- Current targeted status still includes unrelated `docs/task_board.md` and product diff residuals; QA did not modify board or product source.

Reviewer rerun evidence cited, not rerun by QA because live browser keyboard re-smoke directly covered the remaining blocker:

- `ProjectFolderTaskList` passed: 1 file / 6 tests.
- Focused frontend passed: 4 files / 65 tests.
- Backend bridge passed: 5 tests.
- `npm run build` passed with existing Vite chunk-size warning only.

## QA Re-smoke - B1 Fix, 2026-07-01

Historical note: this section records the prior B1/B2 blocked observation before the keyboard fix. It is superseded by the latest `QA Keyboard Re-smoke - Enter / Space Fix` section above.

Objective:

- Re-test the prior live browser B1 for `Project folder -> Open` hit-testing and approved Open behavior on `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.

Service setup:

- Backend temp QA service was already running on `127.0.0.1:8000` from this QA re-smoke setup.
- Frontend temp QA service was already running on `127.0.0.1:5173`.
- Services were stopped after the re-smoke; final listener check for ports `8000` and `5173` returned no remaining listener output.

Artifacts:

- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_resmoke_b1_before_open_20260701.png`
- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_resmoke_b1_after_open_attempts_20260701.png`
- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_resmoke_b1_observation_20260701.json`
- `docs/lane_evidence/artifacts/TASK_346G_qa/backend_uvicorn_resmoke_20260701_214038.out.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/backend_uvicorn_resmoke_20260701_214038.err.log`

Live browser observations:

- Folder Actions showed `Project folder`, `Local folder available.`, and one enabled `Open` button.
- Sticky `Close project` control remained visually colocated with the Folder Actions region; close confirmation could not be expanded in this live state, but the overlap-prone control was present.
- Open button center hit-test resolved to `BUTTON Open`, not Matrix text `Current` or another overlay.
- Coordinate click at the Open button center produced `POST /api/projects/72fbbfa290294da9a507344b68ff900f/folder/open-local HTTP/1.1" 200 OK`.
- Semantic locator click on the unique `Open` button also produced approved Open behavior and showed `Project folder opened`.
- Browser console warnings/errors from Open attempts: none.
- Backend log showed no `public-folder-workflow/(sync|submit|pull)/(preview|execute)` requests from Open attempts.
- Backend log showed no old `project-folder/create` or `project-folder/update` requests from Open attempts.
- QA did not observe or perform any file create/move/delete/copy operation; Open attempts were limited to the non-mutating open-local bridge path.

Keyboard re-smoke blocker:

- Open was a native focused button: `tag=BUTTON`, `type=button`, `disabled=false`, `tabIndex=0`, active element text `Open`.
- `locator.press('Enter')`, CUA `Enter`, and visible-browser Enter-only attempts did not increase the `open-local` POST count.
- `locator.press('Space')` also did not increase the `open-local` POST count.
- Open-local POST count remained unchanged after Enter-only activation while the button was focused, so QA cannot pass the keyboard activation requirement.

Lightweight closeout checks:

```powershell
git diff --check -- frontend/src/workbench.css frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_qa.md docs/lane_evidence/artifacts/TASK_346G_qa
Select-String -Path docs\lane_evidence\TASK_346G_workbench-project-folder-open-action-wiring_qa.md,docs\lane_evidence\artifacts\TASK_346G_qa\*.json -Pattern '[ \t]+$' -Encoding UTF8
Select-String -Path frontend\src\workbench.css,frontend\src\features\project-workbench\ProjectWorkbenchLayout.test.tsx,frontend\src\features\project-workbench\ProjectFolderTaskList.tsx,frontend\src\features\project-workbench\useProjectWorkbenchModel.ts -Pattern 'D:\\Test Project|D:\\PublicProject|public-folder-workflow/(sync|submit|pull)/(preview|execute)|project-folder/(create|update)' -Encoding UTF8
```

Results:

- `git diff --check`: passed with LF/CRLF warnings only for `frontend/src/workbench.css` and `ProjectWorkbenchLayout.test.tsx`.
- Trailing whitespace scan for QA evidence/artifact JSON: no matches.
- No-real-folder / forbidden endpoint scan: no matches.
- Current package status still includes unrelated external residuals, including `docs/task_board.md`; QA did not modify board or product source.

## Sources Re-read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md`
- `docs/task_346g_workbench_project_folder_open_action_wiring_plan.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_reconciliation_planner.md`
- Browser control skill documentation
- Current `git status --short`

Board/task timing note:

- `docs/task_board.md` and TASK_346G task/plan still describe the lane as implementation authorized / pending Developer implementation.
- The current Orchestrator/User delegation states Reviewer implementation gate passed and QA is required. QA records this source-of-truth timing mismatch and does not update the board.

Current phase:

- `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

## Command Validation

Focused frontend tests:

```powershell
cd frontend
npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run
```

Result:

```text
Test Files 4 passed (4)
Tests 63 passed (63)
```

Focused backend tests:

```powershell
py -m pytest tests\unit\test_project_folder_open_service.py tests\unit\test_local_folder_open_gateway.py tests\integration\test_project_folder_open_api.py -q
```

Result:

```text
5 passed in 2.56s
```

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed. Vite emitted the existing chunk-size warning only.

Backend compile smoke:

```powershell
py -m py_compile backend\application\project_folder_open_service.py backend\infrastructure\files\local_folder_open_gateway.py backend\api\routes_folder.py backend\api\dependencies.py
```

Result: passed.

Diff check:

```powershell
git diff --check -- backend\api\routes_folder.py backend\api\dependencies.py backend\application\project_folder_open_service.py backend\infrastructure\files\local_folder_open_gateway.py frontend\src\api\client.ts frontend\src\features\project-workbench\projectFolderTaskSelectors.ts frontend\src\features\project-workbench\projectFolderTaskSelectors.test.ts frontend\src\features\project-workbench\ProjectFolderTaskList.tsx frontend\src\features\project-workbench\ProjectFolderTaskList.test.tsx frontend\src\features\project-workbench\useProjectWorkbenchModel.ts frontend\src\features\project-workbench\useProjectWorkbenchModel.test.tsx frontend\src\features\project-workbench\useProjectRuntimeConsoleModel.ts frontend\src\features\project-workbench\ProjectWorkbenchLayout.tsx frontend\src\features\project-workbench\ProjectWorkbenchLayout.test.tsx frontend\src\features\project-workbench\ProjectWorkbenchActiveMatrixWorkspace.tsx tests\unit\test_project_folder_open_service.py tests\unit\test_local_folder_open_gateway.py tests\integration\test_project_folder_open_api.py docs\lane_evidence\TASK_346G_workbench-project-folder-open-action-wiring_qa.md docs\lane_evidence\artifacts\TASK_346G_qa
```

Result before this QA evidence file existed: passed with LF/CRLF working-copy warnings only. Final evidence-only checks are recorded below.

Trailing whitespace scan before this QA evidence file existed:

```powershell
rg -n "[ \t]$" <TASK_346G package paths and TASK_346G artifact path>
```

Result: no matches in existing package paths; command also reported the expected missing QA evidence path before this file was created. Final evidence-only checks are recorded below.

## Static Scope Checks

Production no-real-folder path scan:

```powershell
rg -n "D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject" backend\api\routes_folder.py backend\api\dependencies.py backend\application\project_folder_open_service.py backend\infrastructure\files\local_folder_open_gateway.py frontend\src\api\client.ts frontend\src\features\project-workbench\projectFolderTaskSelectors.ts frontend\src\features\project-workbench\ProjectFolderTaskList.tsx frontend\src\features\project-workbench\useProjectWorkbenchModel.ts frontend\src\features\project-workbench\useProjectRuntimeConsoleModel.ts frontend\src\features\project-workbench\ProjectWorkbenchLayout.tsx frontend\src\features\project-workbench\ProjectWorkbenchActiveMatrixWorkspace.tsx
```

Result: no matches.

File-mutation keyword scan:

```powershell
rg -n "create|copy|move|delete|remove|unlink|rmdir|mkdir|shutil|copytree|copyfile|write_text|write_bytes|open\(" backend\application\project_folder_open_service.py backend\infrastructure\files\local_folder_open_gateway.py backend\api\routes_folder.py tests\unit\test_project_folder_open_service.py tests\unit\test_local_folder_open_gateway.py tests\integration\test_project_folder_open_api.py
```

Observed:

- `tests/unit/test_project_folder_open_service.py:14` uses `folder.mkdir(parents=True)` in a test temp fixture.
- `backend/api/routes_folder.py` matches `created_on` model fields only.
- No production create/move/delete/copy/overwrite file operation was found in the TASK_346G open bridge paths.

Action-target scan:

```powershell
Select-String -Path frontend\src\features\project-workbench\ProjectWorkbenchLayout.tsx,frontend\src\features\project-workbench\useProjectWorkbenchModel.ts,frontend\src\features\project-workbench\projectFolderTaskSelectors.ts,frontend\src\features\project-workbench\ProjectFolderTaskList.tsx -Pattern 'project_folder_open|actionTarget === "folder"|onOpenLocalProjectFolder|openLocalProjectFolder|public_folder_workflow_sync|public_folder_workflow_submit|public_folder_workflow_pull'
```

Observed:

- `ProjectWorkbenchLayout.tsx` keeps `actionTarget === "folder"` separate from `actionTarget === "project_folder_open"`.
- `project_folder_open` routes to `onOpenLocalProjectFolder()`.
- Sync/Submit/Pull action targets remain separate.

Forbidden-scope status check:

```powershell
git diff --name-only -- backend\application\public_folder_year_resolver.py backend\application\public_folder_path_resolver.py backend\application\public_folder_workflow_service.py backend\infrastructure\files\public_folder_workflow_gateway.py frontend\src\pages\ProjectListPage.tsx frontend\src\features\projects-registry frontend\src\features\matrix-editor .agents docs\project_management docs\packaging_notes.md pyproject.toml backend\desktop dist_release packaging scripts temp_agents_stash.md
```

Observed:

- `docs/packaging_notes.md`
- `pyproject.toml`

Interpretation:

- These are known external release/packaging residuals and must remain excluded from TASK_346G packaging.
- Locked resolver, public-folder workflow service/gateway, Projects registry/list, Matrix Editor, `.agents/**`, and `docs/project_management/**` did not appear in this TASK_346G forbidden-scope check.

Diff-only workflow semantic scan:

```powershell
git diff -U0 -- <TASK_346G package paths> | Select-String -Pattern 'executePublicFolderWorkflowSync|executePublicFolderWorkflowSubmit|executePublicFolderWorkflowPull|previewPublicFolderWorkflowSync|previewPublicFolderWorkflowSubmit|previewPublicFolderWorkflowPull|public_folder_year|public_open_path|public_closed_path'
```

Result: no matches beyond LF/CRLF working-copy warnings.

## Browser Smoke Environment

Initial browser attempt:

- `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f` returned `ERR_CONNECTION_REFUSED`.
- QA verified ports `5173` and `8000` were not listening.

QA started temporary local services only for browser smoke:

- Backend: `py -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000`
- Frontend: `npm run dev -- --host 127.0.0.1`
- Logs stored under `docs/lane_evidence/artifacts/TASK_346G_qa/`.

Service status:

- Port `8000` listened with pid `6584`.
- Port `5173` listened with pid `18664`.

After browser smoke, QA stopped both port listeners:

- `port 8000 stopped`
- `port 5173 stopped`

## Browser Smoke Artifacts

- `docs/lane_evidence/artifacts/TASK_346G_qa/backend_uvicorn.out.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/backend_uvicorn.err.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/frontend_vite.out.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/frontend_vite.err.log`
- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_before_open_click.png`
- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_after_open_attempt.png`
- `docs/lane_evidence/artifacts/TASK_346G_qa/browser_open_action_observation.json`

## Browser Smoke Steps And Observations

Target:

```text
http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f
```

Page load:

- Page title: `ConnLab`.
- Browser console warnings/errors after click attempts: none.

Pre-click DOM observation:

- `Folder Actions` region found.
- `Project folder` row text: `Project folderFolder access.Local folder available.Open`.
- `Local folder available.` was present.
- `Open` button was present and `disabled=false`.
- `Open` button title was `null`.
- No old create/update copy appeared inside the Folder Actions panel.
- Sync/Submit/Pull buttons were present and enabled; QA did not click them.

Pointer hit-test observation:

- After scrolling the Folder Actions area into view, the Open button rect was:
  - `x=1160.875`
  - `y=172.3046875`
  - `width=53.125`
  - `height=30.3984375`
  - center `1187.4375,187.50390625`
- `document.elementFromPoint(...)` at the Open button center did not return the Open button.
- Hit target was `STRONG` with text `Current`.
- This indicates the visually reachable Open button area is overlapped by Matrix/current-workspace content in the live browser.

Pointer click attempt:

- QA clicked the Open button center coordinate.
- No success/fallback message appeared.
- Backend log showed no `POST /api/projects/72fbbfa290294da9a507344b68ff900f/folder/open-local`.
- Backend log showed no Sync/Submit/Pull preview or execute request caused by the click.

Semantic locator click attempt:

- `getByRole('button', { name: 'Open', exact: true })` count was `1`.
- Locator was enabled.
- QA clicked the unique locator.
- No success/fallback message appeared.
- Clipboard remained empty.
- Browser console warnings/errors: none.
- Backend log still showed no `POST /folder/open-local`.
- Backend log still showed no Sync/Submit/Pull preview or execute request caused by the click.

Keyboard activation attempt:

- QA pressed `Enter` on the same unique Open button locator.
- No success/fallback message appeared.
- Browser console warnings/errors: none.
- Backend log still showed no `POST /folder/open-local`.

Backend log check:

```powershell
Select-String -Path docs\lane_evidence\artifacts\TASK_346G_qa\backend_uvicorn.out.log -Pattern 'open-local|public-folder-workflow/(sync|submit|pull)/(preview|execute)|folder/latest|required-forms|official-workspace|public-folder-workflow/context'
```

Observed:

- Expected page-load/context requests, including:
  - `GET /public-folder-workflow/context` -> `200`
  - `GET /official-workspace/preview` -> `200`
  - `GET /project-folder/required-forms/preview` -> `200`
  - legacy `GET /folder/latest` -> `404`
- No `POST /folder/open-local`.
- No Sync/Submit/Pull preview or execute request from the Open attempts.

## Expected vs Actual

Expected:

- With `publicFolderWorkflowContext.local_official_folder_path` present, `Project folder -> Open` should be enabled and clicking it should either:
  - call the safe backend `open-local` bridge and open Explorer, or
  - show/copy a short fallback path message.

Actual:

- The row is enabled and displays `Local folder available.`
- The live Open control is not effectively reachable:
  - pointer hit-test at button center resolves to Matrix text (`Current`);
  - pointer click does not call the bridge;
  - semantic locator click does not call the bridge;
  - keyboard `Enter` activation does not call the bridge;
  - no fallback copy/path message appears.

## Coverage Mapping

- Project folder row with resolved local folder context: covered by browser pre-click DOM observation.
- Open no longer disabled with local path present: covered by browser pre-click DOM observation.
- Click behavior: blocked; click and keyboard activation did not call bridge or fallback.
- No console errors/warnings caused by click: covered; none observed.
- Does not trigger old create/update behavior: covered; no create/update dialog or Folder Actions copy appeared from Open attempts, though body-level old action text exists elsewhere in legacy Workbench surfaces.
- Does not trigger Sync/Submit/Pull: covered; backend log showed no Sync/Submit/Pull preview or execute request from Open attempts.
- Disabled/unavailable path: covered by focused frontend selector/component/model tests and backend service/API tests; not fully re-smoked in browser because the required live fixture has local path present.

## Residual Risks

- QA did not call the `open-local` endpoint directly from the browser because the gate objective is the Workbench in-app button behavior. Focused backend tests already validate the endpoint/service/gateway boundary.
- The live browser smoke did not prove Explorer launch because the Workbench Open action did not reach the backend bridge.
- External Settings/LTR, release/packaging, intake/parser, Office gateway, board, release-task, and `temp_agents_stash.md` residuals remain in the worktree and must be excluded during packaging.

## Recommendation

QA keyboard re-smoke gate: pass.

Recommended next role: Integrator packaging/readiness.

Closeout note:

- The original pointer/hit-test B1 and the follow-up keyboard B2 are both closed in live browser re-smoke.
- Integrator packaging must still exclude unrelated external Settings/LTR, release/packaging, intake/parser, Office gateway, board, release-task, and `temp_agents_stash.md` residuals.
