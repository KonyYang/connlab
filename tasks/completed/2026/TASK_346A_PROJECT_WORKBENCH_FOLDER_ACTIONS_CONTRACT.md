# TASK_346A Project Workbench Folder Actions Contract

Status: complete/accepted contract after Reviewer plan re-gate; not approved for product implementation
Lane: project-workbench-folder-actions-contract
Owner Roles: Planner / Reviewer
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-29

## 1. Purpose

Create the formal contract lane for the redesigned Project Workbench Folder Actions workflow.

TASK_346A is a planning-first contract only. It defines the business semantics, UI boundaries, backend safety model, public-drive path rules, `public_folder_year` resolver, and validation expectations for future implementation lanes.

It does not write product code and does not authorize Developer implementation.

## 2. Inputs

- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product UI guidance
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- Current Workbench Folder Action frontend files
- Current local official workspace, public-drive upload, external-resource, and LTR registration/workbook services

## 3. User-Confirmed Contract Inputs

- Folder Actions returns to a quiet file operation toolbar.
- Folder Actions must not be a readiness/status card system.
- Default UI should show only:
  - Project folder: `Open`
  - Public working copy: `Auto sync` and `Sync now`
  - Approval package: `Submit`
  - Approved folder: `Pull`
- Submit click, after required confirmation and checks, is the workflow point that enters approval stage.
- After Submit succeeds, Sync is locked.
- Submit v1 is only safe move/archive placeholder behavior. It does not implement real encryption, permission control, or compression.
- Public Project locations may be a real public drive or a local development directory such as `D:\PublicProject`.
- Public structure remains:
  - `Open\<public_folder_year>\<project_folder_name>`
  - `Closed\<public_folder_year>\<project_folder_name>`
- `public_folder_year` resolver priority is:
  - local ConnLab LTR application/registration time
  - LTR Excel sheet year containing the DL number
  - project `created_at` / `created_on`
  - human confirmation blocker
- Sync, Submit, and Pull must be preview-first.
- No workflow may silently overwrite, delete, or move real user folders.

## 4. Scope

TASK_346A owns contract planning for:

- four-action Folder Actions IA and copy
- Submit-to-approval-stage state semantics
- Sync lock after Submit
- Submit confirmation and prerequisite checks
- public root classification strategy for local development vs public-like paths
- safe creation policy for `Open`, `Closed`, and year subdirectories
- `public_folder_year` resolver contract
- sync/submit/pull preview and execute safety model
- operation history and audit expectations
- future lane split and validation gates

## 5. Out Of Scope

TASK_346A must not implement:

- frontend UI changes
- backend services, API routes, schema, migrations, or file operations
- public-drive LTR workbook authority writes
- Matrix Editor business logic
- Projects list changes
- StepInstance, Report generation, AI review, permissions, LAN/server, or multi-user scope
- real encryption, Windows permission automation, compressed archive packaging, or public-drive deployment policy

## 6. May Touch

Planner/Reviewer may touch only:

- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `docs/task_board.md`

## 7. Must Not Touch

- `backend/`
- `frontend/`
- `tests/`
- public-drive roots
- local project folders such as `D:\Test Project`
- development public roots such as `D:\PublicProject`
- LTR workbook files
- Matrix Editor implementation
- Projects list implementation
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 8. Locked Paths

- `backend/**`
- `frontend/**`
- `tests/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `.agents/**`
- `docs/project_management/**`

## 9. Validation Gate

Reviewer plan gate must confirm:

- This lane is contract-only and does not authorize implementation.
- Submit is explicitly defined as the approval-stage entry point after confirmation and checks.
- Submit v1 excludes encryption/permissions/compression and treats those as later lanes.
- Public root classification and subdirectory creation strategy is safe for both local development paths and real public-drive-like paths.
- `public_folder_year` resolver priority matches the user-confirmed order and does not infer from DL number.
- Sync, Submit, and Pull are preview-first and never silently overwrite/delete/move folders.
- UI acceptance rejects readiness/status-card behavior and persistent path/count/status displays.
- Backend file operation acceptance requires service-layer logic and never puts filesystem behavior in React or API route bodies.

## 10. Merge Gate

No implementation merge is possible from TASK_346A.

TASK_346A can be accepted only after:

- Reviewer plan gate passes.
- Planner updates evidence with Reviewer result.
- Integrator or Planner records accepted planning status in `docs/task_board.md` if requested.

Future implementation lanes require separate task files, lane evidence, Reviewer gates, user approval, Developer implementation, QA where required, and Integrator packaging.

## 11. Recommended Downstream Lanes

- `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS`
- `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`
- `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`
- `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA`

Current stop point: Reviewer plan gate. Do not route Developer implementation.
