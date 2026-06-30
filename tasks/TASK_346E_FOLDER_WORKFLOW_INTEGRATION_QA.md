# TASK_346E Folder Workflow Integration QA

Status: complete/accepted after Reviewer plan gate, QA execution gate, and Integrator packaging/readiness
Lane: folder-workflow-integration-qa
Owner Roles: Planner / Reviewer / QA / Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-30

## 1. Purpose

Create the formal planning-first QA/integration lane for the accepted Folder Actions workflow.

TASK_346E verifies the complete safe Folder Actions path after accepted upstream lanes:

- `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT`
- `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS`
- `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`
- `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`
- `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`

This lane is complete/accepted as temp-dir integration QA and evidence only. It does not authorize product source changes, real folder mutation, LTR workbook authority writes, release residual cleanup, or new feature implementation.

## 2. Why This Follows TASK_346D

- `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT` defines the downstream sequence: UI refocus, backend public folder workflow, frontend functional wiring, then integration QA.
- `TASK_346B` and `TASK_346F` accepted the compact Folder Actions panel.
- `TASK_346C` accepted the backend public-folder workflow foundation.
- `TASK_346D` accepted frontend API-client and Workbench wiring.
- The remaining contract-backed step is end-to-end QA using safe temporary local/public roots, not another product implementation lane.

## 3. Scope

TASK_346E may plan and later execute QA/integration validation only:

- Create temp local and temp public roots under repository-controlled temp/artifact space.
- Exercise public-folder workflow context, Auto sync preference, Sync preview/execute, Submit preview/execute, and Pull preview/execute against temp roots only.
- Verify Submit locks Sync after approval-stage transition.
- Verify Pull preserves existing local history and never silently overwrites.
- Verify operation/audit evidence is created and readable.
- Run browser smoke against Workbench Folder Actions with temp-safe configuration when available.
- Record screenshots, command outputs, API observations, blockers, and residual risks in QA evidence.

## 4. Out Of Scope

TASK_346E must not implement or modify:

- backend/API/schema/service/repository/file-operation code
- frontend API client, Workbench UI, selectors, CSS, or tests
- Settings/LTR helper residuals
- release-engineering residuals
- Projects list or registry
- Matrix Editor business logic
- real `D:\Test Project`, real `D:\PublicProject`, real public-drive folders, or real local project folders
- real LTR workbook files or public-drive LTR workbook authority writes
- StepInstance, Report, AI, permissions, LAN/server, or multi-user scope
- `.agents/**` or `docs/project_management/**`

## 5. Planned May Touch

Planner lane creation may touch only:

- `tasks/TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA.md`
- `docs/task_346e_folder_workflow_integration_qa_plan.md`
- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_planner.md`
- `docs/task_board.md`

Future QA execution, after Reviewer/user routing, may touch only:

- `docs/lane_evidence/TASK_346E_folder-workflow-integration-qa_qa.md`
- `docs/lane_evidence/artifacts/TASK_346E_qa/**`
- temp-only fixture folders under repository temp space, such as `tmp/TASK_346E_folder_workflow/**`
- QA notes/checkpoints through normal evidence flow

## 6. Must Not Touch / Locked Paths

Locked paths:

- `backend/**`
- `frontend/**`
- `tests/**`
- `frontend/src/api/client.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- real local project folders
- real LTR workbook files
- `.agents/**`
- `docs/project_management/**`
- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/tasks/docs
- `temp_agents_stash.md`

## 7. Validation Gate

Reviewer plan gate must confirm:

- TASK_346E is QA/integration evidence only.
- All file operations use temp dirs or test fixtures only.
- No real local/public/LTR authority path is touched.
- No product source code or tests are modified by the Planner lane.
- QA has explicit stop points for missing temp-safe settings, unavailable fixtures, stale preview conflicts, or app startup blockers.

Future QA validation should include:

- Backend/API smoke with temp local root and temp public root.
- Sync preview then execute creates/copies only under temp public `Open\<year>\<project_folder_name>`.
- Submit preview then execute moves/archives only from temp Open to temp Closed and locks Sync.
- Pull preview then execute copies temp Closed authority back to local while preserving local history.
- Operation/audit record checks for Sync, Submit, and Pull.
- Conflict/blocker checks for missing root, stale preview hash, existing target, and ambiguous year where feasible.
- Browser smoke of Workbench Folder Actions showing context, Auto sync, Sync now, Submit, Pull, preview-first confirmations, short blockers/results, and no old readiness/status copy.

## 8. Merge Gate

TASK_346E can be accepted only after:

- Reviewer plan gate passes.
- QA evidence is created under the approved evidence/artifact paths.
- Integrator confirms the package contains only QA/evidence artifacts and board closeout.
- `git diff --check` passes for included docs/evidence.
- Targeted status proves no product source, real folder, LTR workbook, release residual, `.agents/**`, or `docs/project_management/**` changes were included.

Remote push is not authorized by this lane.

## 9. Current Stop Point

Current stop point: complete/accepted by Integrator. Do not start another TASK_346 lane without a separate Orchestrator/Planner/user routing action.

Recommended next role: Orchestrator/User for Folder Actions series closeout or a separately planned next lane.
