# TASK_346E Folder Workflow Integration QA - QA Evidence

Status: qa_pass
Date: 2026-06-30
Role: QA / Smoke Owner
Task: `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA`
Lane: `folder-workflow-integration-qa`

## Gate Result

QA execution gate: pass.

Recommended next role: Integrator packaging/readiness.

## Integrator Packaging / Readiness Closeout

Integrator gate: accepted.

Package scope accepted:

- TASK_346E task, plan, Planner evidence, QA evidence, QA artifacts, and `docs/task_board.md` TASK_346E closeout only.

Product source status:

- No product backend/frontend/API-client/test changes were staged or committed for TASK_346E.
- QA recorded test/build/temp-dir/browser validation is accepted for this evidence-only lane.

Excluded residuals:

- Settings/LTR helper hunk and backend/settings residuals.
- Release/packaging residuals and release task/docs/scripts/tests.
- `temp_agents_stash.md`.
- Unrelated `docs/task_board.md` release note.
- Real folders, real LTR workbook files, `.agents/**`, `docs/project_management/**`, StepInstance, Report, AI, permissions, LAN/server, and multi-user scope.

Integrator package checks:

- `git diff --cached --check` -> passed.
- Staged whitelist/forbidden-path check -> passed.
- No-real-folder scan on TASK_346E docs/evidence/artifacts -> no real `D:\Test Project` / `D:\PublicProject` references beyond QA documentation of locked real paths.
- Trailing whitespace scan on TASK_346E docs/evidence -> no matches.

Remote push: intentionally not performed.

No product source, product tests, board, release files, real local/public folders, public-drive roots, or real LTR workbook files were modified by QA. This QA pass only created:

- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_qa.md`
- `docs/lane_evidence/artifacts/TASK_346E_qa/temp_dir_workflow_smoke.json`
- `docs/lane_evidence/artifacts/TASK_346E_qa/browser_workbench_folder_actions.png`

## Sources Re-read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA.md`
- `docs/task_346e_folder_workflow_integration_qa_plan.md`
- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_planner.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_qa.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_qa.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_scope_reconciliation_planner.md`
- Browser control skill documentation
- Current `git status --short`

Board/task timing note:

- `docs/task_board.md` and the TASK_346E task/plan still describe TASK_346E as planned and ready for Reviewer plan gate only.
- The current Orchestrator/User delegation states Reviewer plan gate passed and explicitly authorizes QA execution. QA records this source-of-truth timing mismatch and does not update the board.

Current phase:

- `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

## Command Validation

TASK_346C focused backend/API workflow suite:

```powershell
py -m pytest tests\unit\test_public_folder_year_resolver.py tests\unit\test_public_folder_workflow_service.py tests\unit\test_public_folder_workflow_gateway.py tests\integration\test_public_folder_workflow_api.py tests\integration\test_public_folder_workflow_migration.py -q
```

Result:

```text
19 passed in 4.62s
```

Old public-drive/default regression:

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py tests\integration\test_public_drive_upload_api.py tests\integration\test_api_default_dependencies.py -q
```

Result:

```text
20 passed in 2.08s
```

TASK_346D focused frontend/API-client Workbench suite:

```powershell
cd frontend
npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout useProjectWorkbenchModel --run
```

Result:

```text
Test Files 4 passed (4)
Tests 58 passed (58)
```

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed. Vite emitted the existing chunk-size warning only.

Backend compile smoke:

```powershell
py -m py_compile backend\application\public_folder_workflow_service.py backend\application\public_folder_year_resolver.py backend\application\public_folder_path_resolver.py backend\infrastructure\files\public_folder_workflow_gateway.py backend\infrastructure\storage\repositories\public_folder_workflow.py backend\api\routes_public_folder_workflow.py backend\api\dependencies.py backend\api\main.py
```

Result: passed.

Diff check:

```powershell
git diff --check -- backend\application\public_folder_workflow_service.py backend\application\public_folder_year_resolver.py backend\application\public_folder_path_resolver.py backend\infrastructure\files\public_folder_workflow_gateway.py backend\infrastructure\storage\repositories\public_folder_workflow.py backend\api\routes_public_folder_workflow.py backend\api\dependencies.py backend\api\main.py frontend\src\api\client.ts frontend\src\features\project-workbench frontend\src\workbench.css docs\lane_evidence\TASK_346E_folder-workflow-integration-qa_qa.md docs\lane_evidence\artifacts\TASK_346E_qa
```

Result: passed with existing LF/CRLF working-copy warnings for:

- `backend/api/main.py`
- `frontend/src/api/client.ts`

## Temp-dir Integration Smoke

QA ran an additional disposable temp-dir integration smoke using:

- real `PublicFolderWorkflowService`
- real `PublicFolderWorkflowGateway`
- FastAPI `TestClient` with dependency override to the temp service
- OS temp root: `C:\Users\White\AppData\Local\Temp`
- QA temp root pattern: `C:\Users\White\AppData\Local\Temp\connlab_task346e_qa_*`

The script asserted the temp root was contained under OS temp before file operations. The concrete temp root for the passing run was:

```text
C:\Users\White\AppData\Local\Temp\connlab_task346e_qa_w4p7fxl9
```

`TemporaryDirectory` disposed it automatically. The artifact records:

```text
temp_root_exists_after_context: false
```

Artifact:

- `docs/lane_evidence/artifacts/TASK_346E_qa/temp_dir_workflow_smoke.json`

Observed service happy path:

- Sync preview: `ready`.
- Sync execute: `completed`.
- Managed local file copied to temp Public Open.
- Submit preview: `ready`.
- Submit execute: `completed`.
- Temp Public Open folder removed after Submit.
- Temp Public Closed file exists with expected content.
- Submit set backend `sync_locked=True`.
- Sync preview after Submit included blocker `Sync is locked after Submit.`
- Pull preview: `ready`.
- Pull execute: `completed`.
- Pull target was a local history folder named `DL-2026-06-001 Product - Pull Closed`.
- Existing current local file remained unchanged.
- Operation audit sequence: `sync`, `submit`, `pull`.
- All operation ids were strings.

Observed API happy path:

- `POST /api/projects/P1/public-folder-workflow/sync/preview` -> `200`, `ready`.
- `POST /api/projects/P1/public-folder-workflow/sync/execute` -> `200`, `completed`, string `operation_id`.
- `POST /api/projects/P1/public-folder-workflow/submit/preview` -> `200`, `ready`.
- `POST /api/projects/P1/public-folder-workflow/submit/execute` -> `200`, `completed`, string `operation_id`.
- `POST /api/projects/P1/public-folder-workflow/pull/preview` -> `200`, `ready`.
- `POST /api/projects/P1/public-folder-workflow/pull/execute` -> `200`, `completed`, string `operation_id`.

Observed unmanaged Public Open conflict:

- After managed Sync, QA added `human-extra.txt` directly under temp Public Open.
- Submit preview returned `conflict`.
- Submit preview `next_action` was `none`.
- Conflict copy: `Public Open file is not managed by ConnLab; remove or sync through ConnLab before Submit.`
- Submit execute rejected with the same conflict.
- Temp Public Open folder remained intact.
- `human-extra.txt` remained in Open.
- Temp Closed folder was not created.

Observed API unmanaged Public Open conflict:

- Submit preview returned `200`, `conflict`.
- Submit execute returned `409`.
- Error detail: `Public Open file is not managed by ConnLab; remove or sync through ConnLab before Submit.`
- Temp Public Open folder remained intact.
- Temp Closed folder was not created.

Observed stale preview hash rejection:

- QA took a ready Submit preview.
- QA then added unmanaged `human-extra.txt`.
- Submit execute with the old preview hash rejected with `Public folder preview is stale.`
- Temp Public Open remained intact.
- Temp Closed folder was not created.

Observed missing root/config blocker:

- `PublicFolderPathResolver.resolve(...)` with a missing temp public root raised `Public Project locations must be an existing directory.`
- The missing public root was not created.

## Browser Smoke

Browser target:

```text
http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f
```

Artifact:

- `docs/lane_evidence/artifacts/TASK_346E_qa/browser_workbench_folder_actions.png`

Observed:

- Page loaded as `ConnLab`.
- Browser console warnings/errors: none.
- Folder Actions panel was present.
- Four rows appeared in order:
  - `Project folder`
  - `Public working copy`
  - `Approval package`
  - `Approved folder`
- `Auto sync` checkbox was present under `Public working copy`.
- Buttons were present:
  - `Open`
  - `Sync now`
  - `Submit`
  - `Pull`
- Current local browser context was the disabled/missing-root path:
  - `Open` disabled with title `Project folder open is not connected yet.`
  - `Auto sync` disabled.
  - `Sync now` disabled with title `Public Project locations must be an existing directory.`
  - `Submit` disabled with title `Public Project locations must be an existing directory.`
  - `Pull` disabled with title `Public Project locations must be an existing directory.`
- No real file/folder operation was triggered.
- No old Folder Actions readiness/status/source-material copy appeared inside the Folder Actions panel.
- DOM geometry after scrolling the panel into view:
  - Folder Actions width `360`, height `486.984375`.
  - `elementFromPoint(...)` checks at panel center and button area both resolved inside Folder Actions.
- Matrix content remained present; Folder Actions remained secondary right-side tooling.

Enabled browser execute was not attempted because the running local app exposes a missing Public Project root blocker, and configuring it to a temp root through the real app settings would mutate local settings/user environment. The enabled preview/confirm/execute workflow is covered by the temp-dir service/API smoke and focused frontend wiring tests above.

## Static Safety Checks

Trailing whitespace scan before this QA evidence file existed:

```powershell
rg -n "[ \t]$" <TASK_346C/TASK_346D package paths and TASK_346E artifact path>
```

Result: no matches in existing package/artifact paths. A final evidence-only trailing whitespace scan is recorded below in the post-evidence check section.

Production no-real-folder scan:

```powershell
rg -n "D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject" <TASK_346C backend/API production paths, TASK_346D frontend production paths, TASK_346E artifacts>
```

Result: no matches.

Broad scan note:

- A broader scan over `frontend/src/features/project-workbench` found `D:/Test Project` and `D:/PublicProject` only in frontend test fixtures.
- QA treats those as non-mutating fixture strings, not real folder mutation.

Diff-only banned old Folder Actions copy/action-target scan:

```powershell
git diff -U0 -- frontend\src\api\client.ts frontend\src\features\project-workbench frontend\src\workbench.css | Select-String -Pattern 'Ready to upload|Request material|Source material|Project Folder progress|Public drive upload|Upload to public drive|Refresh public-drive preview|public_drive_upload|public_drive_refresh' -Encoding UTF8
```

Result: no matches beyond LF/CRLF working-copy warning on `frontend/src/api/client.ts`.

Operation id type scan:

```powershell
rg -n "operation_id:\s*number|submit_operation_id:\s*number|last_sync_operation_id:\s*number|last_pull_operation_id:\s*number" frontend\src\api\client.ts frontend\src\features\project-workbench
```

Result: no matches.

Forbidden-scope status:

```powershell
git status --short -- docs\lane_evidence\TASK_346E_folder-workflow-integration-qa_qa.md docs\lane_evidence\artifacts\TASK_346E_qa frontend backend tests docs\task_board.md docs\packaging_notes.md pyproject.toml .agents docs\project_management temp_agents_stash.md
```

Observed external residuals still present:

- `M backend/api/main.py`
- `M docs/packaging_notes.md`
- `M docs/task_board.md`
- `M frontend/src/api/client.ts`
- `M frontend/src/features/settings/SettingsExternalResourcesPanel.tsx`
- `M frontend/src/pages/SettingsPage.tsx`
- `M frontend/src/settings.css`
- `M pyproject.toml`
- `M tests/unit/test_frontend_shell_files.py`
- `?? backend/api/routes_settings.py`
- `?? backend/application/local_ltr_workbook_config_service.py`
- `?? backend/desktop/**`
- `?? tests/integration/test_local_ltr_workbook_config_api.py`
- `?? tests/unit/test_desktop_packaged_*.py`
- `?? tests/unit/test_local_ltr_workbook_config_service.py`
- `?? temp_agents_stash.md`

Interpretation:

- These are pre-existing/external Settings/LTR, backend/settings, release/packaging, board, and stash residuals already called out by upstream lanes.
- QA did not modify or package them.
- Integrator must exclude them from TASK_346E packaging unless a separate owner/lane authorizes them.

## Coverage Mapping

- Backend/API temp-dir Sync -> Submit -> Pull happy path: covered by service and FastAPI `TestClient` temp smoke.
- Preview-first execute phases: covered by temp smoke and focused suites.
- Unmanaged Public Open conflict: covered by service and API temp smoke.
- Stale preview hash rejection: covered by service temp smoke and focused tests.
- Submit lock after approval stage: covered by service temp smoke and focused tests.
- Missing Public Project root/config blocker: covered by resolver temp smoke and browser disabled path.
- Frontend/browser Folder Actions disabled/missing-root path: covered by browser smoke.
- Enabled browser preview/confirm path: not run against real local app to avoid mutating real settings; covered by temp API smoke and focused frontend model/component tests.
- Four Folder Actions rows and quiet contextual panel: covered by browser DOM/geometry smoke and screenshot.
- Matrix remains primary and Folder Actions secondary: covered by browser DOM/geometry smoke.
- No old readiness/status/source-material copy in current Folder Actions panel: covered by browser observation and diff-only scan.
- No real-folder writes and no LTR workbook mutation: covered by temp-root containment, no-real-folder scans, no-execute browser path, and status review.

## Residual Risks

- The local browser environment still exposes the missing Public Project root disabled path. QA did not mutate local settings to inject temp roots into the running app. This is non-blocking because TASK_346E directly exercised the enabled workflow through temp-dir service/API smoke and the frontend preview/confirm wiring through focused tests.
- External Settings/LTR, release/packaging, board, and `temp_agents_stash.md` residuals remain in the worktree and must be excluded by Integrator packaging/readiness.

## Recommendation

QA closeout: pass.

Recommended next role: Integrator packaging/readiness.
