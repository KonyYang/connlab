# TASK_346D Workbench Folder Actions Functional Wiring - Planner Evidence

Status: ready_for_review - planned lane, not approved implementation
Date: 2026-06-30
Role: Planner
Task: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
Lane: `workbench-folder-actions-functional-wiring`

## 1. Current Phase / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current board state: no active implementation lane after accepted `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`.
- Planner action: create one formal planning-first downstream Folder Actions lane.
- Stop point: Reviewer plan gate.

## 2. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` product context, `PRODUCT.md`, `DESIGN.md`, and product-register reference
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- TASK_346A/B/F/C task, plan, evidence, QA, and accepted board closeout context
- `backend/api/routes_public_folder_workflow.py`
- `backend/application/public_folder_workflow_service.py`
- `tests/integration/test_public_folder_workflow_api.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Current `git status --short`

## 3. Confirmed Facts

Confirmed by user / Orchestrator delegation:

- `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` is Integrator accepted with local commit `855a919`.
- The user confirmed the next step can enter a new formal TASK_346D+ lane.
- This Planner pass must not write product code or route Developer.

Confirmed by repository evidence:

- `TASK_346A`, `TASK_346B`, `TASK_346F`, and `TASK_346C` are complete/accepted in `docs/task_board.md`.
- `TASK_346A` recommends `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING` after TASK_346B/C.
- `TASK_346C` backend/API exposes context, auto-sync, sync/submit/pull preview, and sync/submit/pull execute endpoints.
- `TASK_346C` QA passed temp-dir backend/API smoke and explicitly leaves frontend wiring to TASK_346D/TASK_346E.
- Current frontend Folder Actions UI is accepted as a compact contextual panel but still uses placeholder blockers for workflow operations.
- Current frontend API client has old public-drive upload helpers but no accepted TASK_346C workflow helpers.
- Current dirty workspace contains unrelated release-engineering residuals that must remain excluded.

## 4. Lane Decision

Created:

- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_planner.md`

Updated:

- `docs/task_board.md`

Decision:

- TASK ID: `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
- Lane: `workbench-folder-actions-functional-wiring`
- Status: planned, ready for Reviewer plan gate, not approved implementation
- Recommended next role: Reviewer plan gate

## 5. Why TASK_346D Is Next

- TASK_346B/F established the frontend operation panel.
- TASK_346C established the backend/API/file-operation workflow.
- The remaining gap is typed frontend API-client consumption and Workbench wiring.
- TASK_346E integration QA should wait until this wiring exists.

## 6. May Touch / Must Not Touch / Locked Paths

May Touch, Must Not Touch, and Locked Paths are recorded in:

- `tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md`
- `docs/task_346d_workbench_folder_actions_functional_wiring_plan.md`
- `docs/task_board.md`

Key future Developer May Touch after Reviewer/user gates:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css` only for existing Folder Actions confirmation/blocker/result state styling

Key locked scope:

- `backend/**`
- backend tests
- Projects registry/list
- Matrix Editor
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- real LTR workbook files
- public-drive LTR workbook authority writes
- `.agents/**`
- `docs/project_management/**`
- release-engineering residuals and `temp_agents_stash.md`
- StepInstance, Report, AI, permissions, LAN/server, multi-user

## 7. Validation Gate / Merge Gate

Reviewer plan gate must confirm:

- TASK_346D is the correct next lane after accepted TASK_346C.
- Scope is frontend API-client/Workbench wiring only.
- Backend/API schema and file-operation logic remain locked.
- UI remains preview-first and confirmation-gated.
- TASK_346E remains the later integration/QA lane.

Future merge requires:

- explicit user approval for Developer implementation
- Developer evidence
- focused frontend tests
- frontend build
- Reviewer implementation gate
- QA browser smoke if routed
- Integrator packaging/readiness

## 8. Validation Performed By Planner

Completed after board/evidence write:

- `git diff --check -- docs/task_board.md tasks/TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING.md docs/task_346d_workbench_folder_actions_functional_wiring_plan.md docs/lane_evidence/TASK_346D_workbench-folder-actions-functional-wiring_planner.md` passed with only the existing `docs/task_board.md` LF/CRLF warning.
- Trailing whitespace scan on touched TASK_346D docs and `docs/task_board.md` returned no matches.
- Targeted status check showed only `docs/task_board.md` and new TASK_346D task/plan/evidence docs changed; no frontend/backend product code, API client, Projects registry, Matrix Editor, or backend public-folder workflow files were changed by this Planner pass.
- Source-of-truth scan confirmed TASK_346D is recorded as planned for Reviewer plan gate and not approved for Developer implementation.

## 9. Stop Point

Planner gate: ready.

Recommended next role: Reviewer plan gate for `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`.

Do not route Developer implementation.
