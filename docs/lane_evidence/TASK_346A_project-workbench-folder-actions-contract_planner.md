# TASK_346A Project Workbench Folder Actions Contract - Planner Evidence

Task ID: TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT
Lane: project-workbench-folder-actions-contract
Role: Planner
Status: accepted - contract lane complete after Reviewer plan re-gate; not approved product implementation
Created: 2026-06-29

## Planner Checkpoint

### Current Phase / Task / Lane

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active implementation lane: none after `TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI` complete/accepted.
- Current task: `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT`.
- Current lane: `project-workbench-folder-actions-contract`.
- Why allowed: the user answered Discovery blockers and requested a Discovery follow-up that may create a proposed/planned contract lane but must not create approved implementation or route Developer.

### Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- Existing Workbench Folder Actions frontend code and backend public-drive/LTR facts from the Discovery checkpoint

### User Answers Incorporated

- Submit click, after manual confirmation and prerequisite checks, enters approval stage.
- Submit success locks Sync.
- Submit v1 is safe move/archive placeholder only, with no real encryption, permissions, or compression.
- Public Project locations may be local during development. Planner should define a safe strategy for root classification and preview/execute directory creation.

### Definition Of Ready

Satisfied for planned contract lane and Reviewer plan gate.

Not satisfied for Developer implementation because this lane is intentionally contract-only and downstream implementation lanes have not been approved.

## Files Created / Updated

- Created `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`.
- Created `docs/task_346a_project_workbench_folder_actions_contract_plan.md`.
- Created `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`.
- Updated `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`.
- Updated `docs/task_board.md`.

## May Touch

- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `docs/task_board.md`

## Must Not Touch

- `backend/`
- `frontend/`
- `tests/`
- local project folders
- public-drive folders
- LTR workbook files
- Matrix Editor business logic
- Projects list implementation
- StepInstance, Report, AI, permissions, LAN/server, multi-user
- unrelated governance/orchestration residuals

## Locked Paths

- `backend/**`
- `frontend/**`
- `tests/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`

## Evidence / Validation / Merge Gates

Evidence file:

- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`

Validation Gate:

- Reviewer plan gate next.
- Reviewer should check that the contract is planning-only, safe for public/local roots, preview-first, and not an implementation authorization.

Merge Gate:

- No product merge is possible from this contract lane.
- Planning acceptance requires Reviewer plan gate pass and a later Planner/Integrator board update if requested.

## Next Role Recommendation

Recommended next role: Reviewer plan gate.

Do not route Developer implementation.

## Planner Fix Pass - 2026-06-29

Reviewer B1 fixed:

- Standard plan path now exists: `docs/task_346a_project_workbench_folder_actions_contract_plan.md`.
- Nonstandard plan path `docs/task_346a_project_workbench_folder_actions_contract.md` was moved to the standard `_plan.md` path and is no longer an authoritative duplicate.
- TASK_346A task, board, planner evidence, and Discovery evidence references now use the standard `_plan.md` path.
- No product code was modified by this Planner fix pass.
- External product residuals remain excluded from the TASK_346A package:
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - `frontend/src/workbench.css`

Updated stop point: Reviewer plan re-gate.

### Fix Pass Validation

- Standard plan path exists: `docs/task_346a_project_workbench_folder_actions_contract_plan.md`.
- Old nonstandard plan file is absent: `docs/task_346a_project_workbench_folder_actions_contract.md`.
- Exact old-path search across TASK_346A source-of-truth files now returns only this non-authoritative fix note.
- Standard `_plan.md` path search returns task, board, plan, planner evidence, and Discovery evidence references.
- `git diff --check` passed for touched docs with CRLF conversion warnings only.
- Trailing whitespace scan for touched docs returned no matches.
- Product code was not modified by this fix pass. Targeted status still shows only pre-existing frontend residuals:
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - `frontend/src/workbench.css`

## Completion Callback Text

来源角色：ConnLab｜总计划者 Planner
完成状态：ready_for_review
TASK_ID：TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT
lane：project-workbench-folder-actions-contract
evidence 路径：docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md
建议下一角色：Reviewer plan gate
阻塞摘要：Reviewer B1 fixed. Standard plan path exists and source-of-truth references now use `docs/task_346a_project_workbench_folder_actions_contract_plan.md`. TASK_346A remains planned contract-only and not approved for Developer implementation. 请立即执行一次全自动编排扫描，只执行一个合法路由动作。
