# TASK_346B QA Evidence - Workbench Folder Actions UI Refocus

Status: qa_pass
Task: TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS
Lane: workbench-folder-actions-ui-refocus
Role: QA / Smoke Owner
Date: 2026-06-29

## Summary

QA reran the required focused frontend tests, frontend build, static copy/scope scans, and browser smoke for available Workbench fixtures.

QA gate: pass.

Recommended next role: Integrator packaging/readiness.

Residual risk: wide 1280px screenshot capture in the in-app browser returned left-shell-only images in this thread, although DOM checks succeeded. QA therefore used DOM verification plus 514px screenshots for active Matrix, registered/no-Matrix, and temporary/no-LTR Workbench states. This does not block the gate because browser DOM and visible 514px artifacts verify the Folder Actions surface and the visual/narrow layout target.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product context and product reference
- Browser control skill instructions
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_planner.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_reconciliation_planner.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`
- Current Workbench Folder Actions source/tests:
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - focused Workbench tests

Board note:

- `docs/task_board.md` still described TASK_346B as implementation-authorized / pending Developer implementation during QA read, while the delegation supplied `Reviewer implementation gate passed` and QA routing. QA proceeded from the newer Orchestrator delegation and recorded the mismatch.

## Validation Commands

Focused frontend tests:

```powershell
cd frontend
npm test -- ProjectFolderTaskList projectFolderTaskSelectors projectWorkbenchLifecycleSelectors ProjectWorkbenchLayout useProjectWorkbenchModel --run
```

Observed:

- Test files: 5 passed.
- Tests: 76 passed.
- Non-blocking stdout logs from existing `useProjectWorkbenchModel` tests were present.

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
git diff --check -- frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/workbench.css docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md
```

Observed:

- Passed with LF/CRLF working-copy warnings only.

Trailing whitespace scan over the same package files:

- Passed, no matches.

CSS anti-pattern scan on changed `workbench.css` diff:

- No thick side-stripe `border-left/right` additions.
- No gradient text.
- No `backdrop-filter`.

## Static Scans

TASK_346B package-file production copy scan:

```powershell
rg -n "Ready to upload|Upload to public drive|Refresh public-drive preview|Project Folder progress|Next step|Public drive upload|Source Book|Already current|Request material|Source material|Not current|Waiting|Partial" frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/projectFolderTaskSelectors.ts frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/workbench.css -g "*.ts" -g "*.tsx" -g "*.css"
```

Observed:

- No matches in TASK_346B changed production package files.

Broad Workbench old-copy scan:

- Found legacy text in files outside the TASK_346B product package surface, including `OfficialWorkspaceActionPanel.tsx`, `ProjectFolderCreationPanel.tsx`, evidence/material panels, and tests.
- Follow-up import/reference scan showed the default Workbench Folder Actions surface now uses `ProjectFolderActionsSurface`; the legacy `OfficialWorkspaceActionPanel` and `ProjectFolderCreationPanel` are not the TASK_346B default Folder Actions surface. This is recorded as non-blocking legacy code/copy outside the current lane package, not as user-visible TASK_346B failure.

Forbidden-scope status:

```powershell
git status --short -- backend frontend/src/api/client.ts frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry frontend/src/features/matrix-editor tests
git diff --name-only -- backend frontend/src/api/client.ts frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry frontend/src/features/matrix-editor tests
```

Observed:

- No backend changes.
- No `frontend/src/api/client.ts` changes.
- No Projects registry / `ProjectListPage` changes.
- No Matrix Editor changes.
- No root backend tests changes.

Future-scope scan:

```powershell
rg -n "StepInstance|Report generation|AI review|permissions|LAN|multi-user|public_folder_year|Submit preview|Pull preview|Sync preview|Open\\<|Closed\\<|encrypt|compression|Windows permission" frontend/src/features/project-workbench frontend/src/workbench.css -g "*.ts" -g "*.tsx" -g "*.css"
```

Observed:

- Matches were limited to existing static guard tests for future scope.
- No TASK_346B implementation of backend public-folder resolver, Sync/Submit/Pull preview/execute, Open/Closed path workflow, encryption/compression/Windows permissions, StepInstance, Report, AI, permissions, LAN/server, or multi-user behavior surfaced.

## Browser Smoke

Browser method:

- In-app browser on `http://localhost:5173`.
- Read-only DOM checks plus screenshot artifacts.
- No file-operation or lifecycle mutation control was submitted.

Artifacts:

- `docs/lane_evidence/artifacts/TASK_346B_qa/narrow_514_active_matrix_DL-2026-05-011.png`
- `docs/lane_evidence/artifacts/TASK_346B_qa/narrow_514_active_matrix_DL-2026-05-011_scrolled_folder_actions_2.png`
- `docs/lane_evidence/artifacts/TASK_346B_qa/narrow_514_registered_no_matrix_DL-2026-05-002_tall.png`
- `docs/lane_evidence/artifacts/TASK_346B_qa/narrow_514_temporary_no_ltr_TMP-C4F39233_scrolled_folder_actions.png`

Fixtures:

- Active Matrix: `72fbbfa290294da9a507344b68ff900f` / `DL-2026-05-011`
- Registered no-Matrix: `7c55618e2acc41bd9973b7e4eaaf7e0f` / `DL-2026-05-002`
- Temporary/no-LTR: `c4f39233742949febda453a428bd5e42` / `TMP-C4F39233`

Observed across all three fixtures:

- One `Folder Actions` region was present.
- Four entries were present:
  - `Project folder` with `Open`
  - `Public working copy` with `Auto sync` and `Sync now`
  - `Approval package` with `Submit`
  - `Approved folder` with `Pull`
- `Open`, `Sync now`, `Submit`, and `Pull` buttons were disabled.
- `Auto sync public working copy` checkbox was disabled and unchecked.
- Disabled reasons were short and business-readable:
  - `Project folder open is not connected yet.` or `Project folder is not available yet.`
  - `Sync workflow is not connected yet.`
  - `Submit workflow is not connected yet.`
  - `Pull workflow is not connected yet.`
- No `Request material`, `Source material`, `Ready to upload`, `Upload to public drive`, `Refresh public-drive preview`, `Project Folder progress`, `Next step`, `Public drive upload`, `Source Book`, `Already current`, `Not current`, `Waiting`, `Partial`, persistent target path, file count, last sync/submit time, or pull time appeared in the Folder Actions region or page body for the smoked pages.
- Active Matrix kept the Matrix table and Step Workspace primary; Folder Actions appeared as a quiet secondary operation area below supporting workspace content.
- Registered no-Matrix and temporary/no-LTR states used the same compact Folder Actions surface and did not imply backend Sync/Submit/Pull availability.
- At `514px` width, Folder Actions entries were visible, wrapped into a compact grid, and had no measured horizontal overflow. `Auto sync` wrapped within its control but remained readable and did not overlap adjacent controls.

## QA Result

QA gate: pass.

Blocking findings: none.

Recommended next role: Integrator packaging/readiness.
