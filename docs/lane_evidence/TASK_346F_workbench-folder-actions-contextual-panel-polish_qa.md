# TASK_346F QA Evidence - Workbench Folder Actions Contextual Panel Polish

Status: qa_pass
Task: TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH
Lane: workbench-folder-actions-contextual-panel-polish
Role: QA / Smoke Owner
Date: 2026-06-30

## Summary

QA reran the focused frontend tests, frontend build, package diff/whitespace/static scans, forbidden-scope status checks, and browser visual/IA smoke for the active Matrix Workbench fixture.

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Blocking findings: none.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product context and product reference
- Browser control skill instructions
- `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_planner.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_reconciliation_planner.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`
- Relevant Workbench Folder Actions source/tests/CSS:
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - `frontend/src/workbench.css`

Board note:

- `docs/task_board.md` still described TASK_346F as implementation-authorized / pending Developer implementation during QA read, while this delegation supplied `Reviewer implementation gate passed` and QA routing. QA proceeded from the newer Orchestrator delegation and recorded the mismatch.

## Validation Commands

Focused frontend tests:

```powershell
cd frontend
npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --run
```

Observed:

- Test files: 3 passed.
- Tests: 49 passed.

Frontend build:

```powershell
cd frontend
npm run build
```

Observed:

- Build passed.
- Existing Vite chunk-size warning only.

Package diff check:

```powershell
git diff --check -- frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md
```

Observed:

- Passed with LF/CRLF working-copy warnings only.

Trailing whitespace scan over the same TASK_346F package files:

- Passed, no matches.

## Static Scans

Banned old Folder Actions copy scan over TASK_346F production files:

```powershell
rg -n -e '"Ready"' -e '"Partial"' -e '"Waiting"' -e '"Not current"' -e '"Already current"' -e '"Ready to upload"' -e '"Request material"' -e '"Source material"' -e '"Project Folder progress"' -e '"Next step"' -e '"Public drive upload"' -e '"Upload to public drive"' -e '"Refresh public-drive preview"' frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/workbench.css
```

Observed:

- No user-facing string literal matches.
- A broader unquoted scan only matched internal identifiers such as `folderReady`, not visible copy.

Mutation/action-target scan:

```powershell
rg -n -e 'public_drive_upload' -e 'public_drive_refresh' -e 'fetchPublicDriveUploadPreview' -e 'uploadPublicDriveProjectFolder' -e 'syncProject' -e 'submitProject' -e 'pullProject' frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/workbench.css
```

Observed:

- Only type-union definitions for legacy action target names remain in `projectFolderTaskSelectors.ts`.
- No assignment, call, or active UI wiring to old public-drive upload/refresh helpers was found in TASK_346F production files.

Future-scope scan:

```powershell
rg -n -e 'StepInstance' -e 'Report generation' -e 'AI review' -e 'permissions' -e 'LAN' -e 'multi-user' -e 'public_folder_year' -e 'file count' -e 'last sync' -e 'Sync preview' -e 'Submit preview' -e 'Pull preview' -e 'Open\\' -e 'Closed\\' -e 'encrypt' -e 'compression' -e 'Windows permission' frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/workbench.css
```

Observed:

- No matches.
- TASK_346F does not implement backend workflow, public folder resolver, real count/timestamp/path/year facts, Sync/Submit/Pull preview/execute, StepInstance, Report, AI, permissions, LAN/server, or multi-user scope.

CSS anti-pattern scan on changed `workbench.css` diff:

- No thick side-stripe `border-left/right` additions.
- No gradient text.
- No `backdrop-filter`.
- No new `linear-gradient`.

Forbidden-scope status:

```powershell
git status --short -- backend frontend/src/api/client.ts frontend/src/features/matrix-editor frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry .agents docs/project_management temp_agents_stash.md
```

Observed:

- `?? temp_agents_stash.md` is present as an unrelated untracked root residual.
- No backend, API client, Matrix Editor, Projects list/registry, `.agents`, or `docs/project_management` changes appeared in the targeted status.
- `temp_agents_stash.md` was not touched by QA and must remain excluded from TASK_346F packaging unless a later role explicitly classifies it.

## Browser Smoke

Target:

- `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`
- Fixture: active Matrix project `DL-2026-05-011`

Method:

- In-app browser with read-only DOM inspection and screenshots.
- No file/folder/lifecycle mutation was submitted.

Artifacts:

- `docs/lane_evidence/artifacts/TASK_346F_qa/active_matrix_1280x1400_page.png`
- `docs/lane_evidence/artifacts/TASK_346F_qa/active_matrix_514x1400_scrolled_folder_actions_2.png`

Observed DOM facts:

- One `Folder Actions` region was present.
- Folder Actions region rendered four operation rows in order:
  1. `Project folder`
  2. `Public working copy`
  3. `Approval package`
  4. `Approved folder`
- Each row had an icon, title, compact helper/context text, and right-side control/button.
- `Public working copy` included `Auto sync` and `Sync now`.
- Row separator count was `3`, matching thin divider separation between four rows.
- Bottom blocker was one short panel-level message: `Project folder open is not connected yet.`
- Matrix table remained the main visual priority. DOM geometry showed the Matrix area as the large primary surface and Folder Actions as a secondary side/support panel.
- Controls stayed disabled/safe:
  - `Open`: disabled, title `Project folder open is not connected yet.`
  - `Auto sync public working copy`: disabled and unchecked.
  - `Sync now`: disabled, title `Sync workflow is not connected yet.`
  - `Submit`: disabled, title `Submit workflow is not connected yet.`
  - `Pull`: disabled, title `Pull workflow is not connected yet.`
- No banned old Folder Actions vocabulary appeared in the Folder Actions region or page body:
  - `Ready`, `Partial`, `Waiting`, `Not current`, `Already current`, `Ready to upload`, `Request material`, `Source material`, `Project Folder progress`, `Next step`, `Public drive upload`, `Upload to public drive`, `Refresh public-drive preview`.
- At `514px`, the Folder Actions rows were visible after scrolling, with no measured horizontal overflow.

Visual/IA judgment:

- The panel reads as a single-column contextual file operation panel, not the older readiness/status card grid.
- The panel is compact, secondary, and operational; it does not overtake the Matrix/Step workspace.
- Copy is concise and business-readable, with safe placeholder context instead of invented backend facts.

## QA Result

QA gate: pass.

Blocking findings: none.

Recommended next role: Integrator packaging/readiness.
