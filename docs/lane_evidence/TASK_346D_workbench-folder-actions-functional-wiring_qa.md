# TASK_346D Workbench Folder Actions Functional Wiring - QA Evidence

Status: qa_pass
Date: 2026-06-30
Role: QA / Smoke Owner
Task: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
Lane: `workbench-folder-actions-functional-wiring`

## Scope

QA validated the TASK_346D frontend UI/API-client functional wiring after the delegated Reviewer implementation re-gate pass.

No product source, tests, board, packaging files, backend code, real local/public folders, or LTR workbook files were modified by QA. This QA pass only created this evidence file and browser screenshot artifacts under `docs/lane_evidence/artifacts/TASK_346D_qa/`.

## Sources Re-read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product UI context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- Browser control skill documentation
- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_scope_reconciliation_planner.md`
- Reviewer callback from the current delegation prompt
- Relevant TASK_346D frontend files and focused tests:
  - `frontend/src/api/client.ts`
  - `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`

## Current Phase / Task Authorization

- Current phase from `docs/task_board.md`: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task from `docs/task_board.md`: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`.
- Board/task/plan text still records earlier `review blocked` / Developer fix-pass wording, but the current Orchestrator delegation and Reviewer callback state that Reviewer implementation re-gate passed and QA is required. QA records this as a source-of-truth timing mismatch and does not update the board.

## Validation Commands

Focused frontend/API-client Workbench suite:

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

Package diff check:

```powershell
git diff --check -- frontend/src/api/client.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_developer.md
```

Result: passed with LF/CRLF working-copy warnings only.

Trailing whitespace scan on TASK_346D package files:

```powershell
rg -n "[ \t]$" <TASK_346D package files>
```

Result: no matches.

Operation id type mismatch scan:

```powershell
rg -n "operation_id:\s*number|submit_operation_id:\s*number|last_sync_operation_id:\s*number|last_pull_operation_id:\s*number" frontend/src/api/client.ts frontend/src/features/project-workbench
```

Result: no matches. Frontend public-folder workflow operation id fields now match backend `str` / TypeScript `string` contract.

Banned old Folder Actions copy scan:

```powershell
rg -n -F -e "Ready" -e "Partial" -e "Waiting" -e "Not current" -e "Already current" -e "Ready to upload" -e "Request material" -e "Source material" -e "Project Folder progress" -e "Next step" -e "Public drive upload" -e "Upload to public drive" -e "Refresh public-drive preview" frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css
```

Result: matches were identifier-only occurrences of `Ready` such as `effectiveFolderReady`; no banned old user-facing Folder Actions copy was found in the touched production Folder Actions paths.

Old action-target scan:

```powershell
rg -n "public_drive_refresh|public_drive_upload|Refresh public-drive preview|Upload to public drive|Public drive upload" frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/ProjectFolderTaskList.tsx
```

Result:

- Source still has historical `public_drive_refresh` / `public_drive_upload` branch code in `ProjectWorkbenchLifecycleSections.tsx`.
- Diff-only scan shows TASK_346D removed old public-drive action targets from the Folder Actions path rather than adding them.
- `projectFolderTaskSelectors.ts` now routes Folder Actions through `public_folder_workflow_sync`, `public_folder_workflow_submit`, and `public_folder_workflow_pull`.

UI anti-pattern changed-lines scan:

```powershell
git diff -U0 -- <TASK_346D package files> | rg -n "border-(left|right):\s*[2-9]px|background-clip:\s*text|backdrop-filter|linear-gradient"
```

Result: no matches beyond LF/CRLF warnings.

Production real-folder/write scan:

```powershell
rg -n "D:\\Test Project|D:\\PublicProject|D:/Test Project|D:/PublicProject|mkdir|unlink|removeItem|Remove-Item|writeFile|fs\." frontend/src/api/client.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css
```

Result: no matches.

Test fixture path scan note:

- Diff-only scan over tests found `D:/PublicProject` and `D:/Test Project` strings only inside frontend test fixtures.
- QA treats these as non-mutating fixture strings, not real folder mutation.

Forbidden-scope status:

```powershell
git diff --name-only -- backend tests frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry frontend/src/features/matrix-editor .agents docs/project_management docs/packaging_notes.md pyproject.toml backend/desktop dist_release packaging scripts tasks/RELEASE_001_WINDOWS_DESKTOP_PORTABLE_EXE_PACKAGING.md tasks/RELEASE_002_BROWSER_LOCAL_SERVER_RELEASE_AND_LTR_CONFIG_BRIDGE.md
```

Result:

```text
backend/api/main.py
docs/packaging_notes.md
pyproject.toml
tests/unit/test_frontend_shell_files.py
```

Targeted status additionally showed external dirty settings/release files:

- `backend/api/routes_settings.py`
- `backend/application/local_ltr_workbook_config_service.py`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tasks/docs
- local LTR workbook config tests
- `temp_agents_stash.md`

Interpretation:

- No Projects registry, `ProjectListPage`, Matrix Editor, `.agents/**`, or `docs/project_management/**` diffs were detected.
- Backend/settings/release/test residuals are external to TASK_346D and must remain excluded during Integrator packaging.
- `frontend/src/api/client.ts` still contains unrelated LTR workbook local settings helper diff visible in the broad file diff. Reviewer B2 already classified this as a non-blocking external residual required by current dirty Settings files for buildability. QA confirms it is a packaging separation risk, not a TASK_346D functional blocker.

## Browser Smoke

Browser target:

```text
http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f
```

Observed page:

- URL loaded successfully.
- Page title: `ConnLab`.
- Browser console warnings/errors: none.
- Active Matrix Workbench rendered.
- Matrix remained primary visual workspace:
  - Matrix region observed width `1166`, height `1453.5`.
  - Folder Actions region observed width `360`, height `486.98`.
  - Matrix table content remained the dominant workspace.

Folder Actions DOM/IA observations:

- One `Folder Actions` region was present.
- Four operation rows appeared in order:
  1. `Project folder`
  2. `Public working copy`
  3. `Approval package`
  4. `Approved folder`
- Visible operation copy:
  - `Project folder` / `Folder access.` / `Open is not connected yet.`
  - `Public working copy` / `Keep the lab working copy aligned.` / `Public Open location will be prepared after preview.`
  - `Approval package` / `Submit controlled output.` / `Preview moves Open output to Closed after confirmation.`
  - `Approved folder` / `Bring approved public results back.` / `Closed output is available after approval package submission.`
- `Auto sync` checkbox was present under Public working copy.
- `Sync now`, `Submit`, and `Pull` buttons were present.
- Current local backend context returned blocker `Public Project locations must be an existing directory.`
- Because of that blocker:
  - Auto sync was disabled.
  - Sync now was disabled.
  - Submit was disabled.
  - Pull was disabled.
  - No execute path was triggered.
- No banned old Folder Actions copy appeared in the Folder Actions region.
- `elementFromPoint(...)` checks at the Folder Actions region confirmed visible top-left, center, and button-area points all resolved inside the Folder Actions panel, not behind Matrix.

Browser screenshots/artifacts:

- `docs/lane_evidence/artifacts/TASK_346D_qa/active_matrix_folder_actions_fullpage.png`
- `docs/lane_evidence/artifacts/TASK_346D_qa/active_matrix_folder_actions_after_scroll.png`
- Additional crop attempts are present in the same artifact directory; DOM geometry/visibility checks above are the authoritative browser evidence because screenshot clipping did not isolate the right rail cleanly.

## Coverage Mapping

- Four-row contextual panel and Matrix primary priority: covered by browser DOM/geometry smoke and component tests.
- Auto sync load/save UI path: covered by `useProjectWorkbenchModel.test.tsx` (`loads and saves backend-owned public folder Auto sync state`) and browser disabled-state smoke from backend blocker.
- Sync preview-first flow: covered by `ProjectFolderTaskList.test.tsx`, `projectFolderTaskSelectors.test.ts`, and `useProjectWorkbenchModel.test.tsx`; browser showed disabled/no-unsafe-action behavior when context blocks.
- Submit preview-first flow, confirmation, conflict/stale handling: covered by focused model/component tests; browser did not execute because the local backend context blocks public folder workflow.
- Pull preview-first flow and no silent overwrite copy: covered by focused model/component tests and backend TASK_346C QA; browser showed Pull disabled under current blocker.
- Short blocker/error copy only: covered by browser observation and banned-copy scan.
- Operation id fields as strings: covered by static scan and build.
- No real folder/LTR workbook mutation: covered by production scan and browser no-execute smoke.

## QA Result

QA gate: pass.

Blocking findings: none.

Residual risks:

- Current browser environment has `Public Project locations must be an existing directory.`, so browser smoke covered the real disabled/blocker path, not enabled real preview/confirm/execute. This is acceptable for TASK_346D because focused tests cover enabled preview/confirm/execute wiring, and real file operation safety belongs to TASK_346C/TASK_346E temp-root workflows.
- `frontend/src/api/client.ts` still includes unrelated LTR workbook local settings helper diff from external Settings residuals. QA agrees with Reviewer that this is non-blocking for TASK_346D, but Integrator must not stage/package the whole client file blindly without separating the authorized TASK_346D helper hunk.
- External backend/settings/release residuals remain in the worktree and must be excluded from TASK_346D packaging.

Recommended next role: Integrator packaging/readiness.
