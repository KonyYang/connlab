# Planner Evidence - TASK_340 Unified Shell Plan

Status: complete
Task: TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN
Lane: unified-shell-plan
Role: Planner/Designer
Last Updated: 2026-06-26

## Approval

The user approved this lane planning batch on 2026-06-26.

This lane is approved for execution after TASK_336 was accepted on 2026-06-26.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## Why This Lane Is Allowed

The lane is a planning-only information architecture task for the unified Project Workbench Shell. It is parallel-safe because TASK_336 defines lifecycle states and readonly rules and this lane does not implement UI.

## Goal

Plan the unified Project Workbench Shell so operators experience one lifecycle-aware workspace instead of a complex 5+2 mental model.

The plan must include active, stopped, closed completed, and closed administrative states. Stopped and closed states must remain readable but block edits and write operations. Closed states must not expose Resume.

## May Touch

- Workbench shell plan doc under `docs/`, exact path to be declared by TASK_340
- Information architecture or smoke checklist docs
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`

## Must Not Touch

- Product code
- Backend API contracts
- Lifecycle status implementation
- Matrix/Fee internals
- StepInstance
- Report generation
- AI, permissions, LAN/server, or multi-user scope

## Locked Paths

- Workbench shell plan docs declared by TASK_336
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`

## Validation Gate

Plan shows unified shell states for active/stopped/closed, readonly banners/actions, and current-feature-only navigation without exposing future scope.

## Merge Gate

User approval before any Workbench implementation lane.

## Execution Notes

Executed on 2026-06-26 as Planner/Designer.

Anti-skip confirmation:

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
- Current approved lane: `unified-shell-plan`
- Current role: Planner/Designer
- Allowed because `docs/task_board.md` marks TASK_340 as approved after accepted TASK_336

Read inputs:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- `$impeccable` ConnLab product/design guidance
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- existing Workbench IA docs and current Workbench frontend files, read-only

Created or updated:

- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- `docs/task_board.md` lane status note only

No product code was changed. No frontend/backend runtime behavior was changed. TASK_337B was not executed.

## Commands Or Checks Run

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Select-String -Path 'docs\task_board.md' -Pattern 'Current Active Task|Proposed Next Task|TASK_340|unified-shell-plan|TASK_337B|guard-inventory|No product implementation lane' -Encoding UTF8
Get-Content 'docs\lane_evidence\TASK_340_unified-shell-plan_planner.md' -Encoding UTF8
Test-Path 'tasks\TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md'
Get-Content 'docs\project_management\TASK_EXECUTION_SKILL.md' -Encoding UTF8 | Select-Object -First 220
Get-Content 'docs\project_management\PARALLEL_EXECUTION_MODEL.md' -Encoding UTF8 | Select-Object -First 260
Select-String -Path 'docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md' -Pattern 'Unified|Workbench|Stopped|Closed|completed|Administrative|readonly|Resume|temporary|registered|Matrix|5\+2|State Transitions|API Contract|Completed Close' -Context 2,3 -Encoding UTF8
Select-String -Path 'docs\02_ARCHITECTURE_RULES.md' -Pattern 'frontend|UI|Project Workbench|Matrix|page|component|state|route|business|copy|mock|authority' -Context 1,2 -Encoding UTF8
Select-String -Path 'docs\frontend_architecture_rules.md' -Pattern 'page|feature|component|state|selector|API|copy|mock|Project Workbench|Matrix|route|implementation' -Context 1,2 -Encoding UTF8
rg --files 'frontend/src' | rg 'project-workbench|ProjectWorkbench|ProjectList|projectWorkbench'
Get-Content 'frontend\src\features\project-workbench\ProjectWorkbenchLayout.tsx' -Encoding UTF8 | Select-Object -First 260
Get-Content 'frontend\src\features\project-workbench\projectWorkbenchLifecycleSelectors.ts' -Encoding UTF8 | Select-Object -First 260
Get-Content 'docs\project_workbench_runtime_console_information_architecture.md' -Encoding UTF8 | Select-Object -First 220
Get-Content 'docs\project_workbench_matrix_authority_workspace_target.md' -Encoding UTF8 | Select-Object -First 180
Get-Content 'frontend\src\features\project-workbench\ProjectWorkbenchLayout.tsx' -Encoding UTF8 | Select-Object -Skip 260 -First 260
Get-Content 'frontend\src\features\project-workbench\ProjectWorkbenchLifecycleSections.tsx' -Encoding UTF8 | Select-Object -First 260
Get-Content 'frontend\src\features\project-workbench\ProjectWorkbenchLifecycleSections.tsx' -Encoding UTF8 | Select-Object -Skip 260 -First 220
```

Final documentation validation:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path tasks\TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md
Test-Path docs\task_340_unified_project_workbench_shell_plan.md
Select-String -Path docs\task_340_unified_project_workbench_shell_plan.md -Pattern 'Stopped project' -Encoding UTF8
Select-String -Path docs\task_340_unified_project_workbench_shell_plan.md -Pattern 'Closed: Completed' -Encoding UTF8
Select-String -Path docs\task_340_unified_project_workbench_shell_plan.md -Pattern 'Closed: Administrative' -Encoding UTF8
Select-String -Path docs\task_340_unified_project_workbench_shell_plan.md -Pattern 'current-feature-only' -Encoding UTF8
Select-String -Path docs\lane_evidence\TASK_340_unified-shell-plan_planner.md -Pattern 'Status: complete' -Encoding UTF8
git diff --check -- tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md docs/task_340_unified_project_workbench_shell_plan.md docs/lane_evidence/TASK_340_unified-shell-plan_planner.md docs/task_board.md
```

## Validation Result

- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md` exists.
- `docs/task_340_unified_project_workbench_shell_plan.md` exists.
- Plan contains `Stopped project`.
- Plan contains `Closed: Completed`.
- Plan contains `Closed: Administrative`.
- Plan contains `current-feature-only`.
- Evidence contains `Status: complete`.
- `git diff --check -- tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md docs/task_340_unified_project_workbench_shell_plan.md docs/lane_evidence/TASK_340_unified-shell-plan_planner.md docs/task_board.md` completed with no whitespace errors. Git printed a CRLF normalization warning for `docs/task_board.md`.

## Review Follow-Up

User accepted TASK_340 on 2026-06-26 with non-blocking documentation findings.

Follow-up changes:

- Updated `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md` status from `approved` to `complete`.
- Added explicit serial dependency notes that `TASK_339A` waits for approved backend lifecycle/API shape from `TASK_337A`, and broad write blocking depends on `TASK_338`.
- Added smoke checklist note that readonly preview endpoints remain available only when `TASK_337B` or `TASK_338` classifies them as non-mutating.
- Updated `docs/task_board.md` to mark `unified-shell-plan` complete/accepted.

Follow-up validation:

- Task file contains `Status: complete`.
- Plan file contains `Status: accepted`.
- Plan file contains `TASK_337A`, `TASK_338`, and the readonly preview endpoint smoke boundary.
- Evidence file contains `Status: complete`.
- Board marks `TASK_340` complete/accepted and keeps Workbench implementation unapproved.
- Search found no remaining old review-status token in the TASK_340 plan or evidence.
- `git diff --check -- tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md docs/task_340_unified_project_workbench_shell_plan.md docs/lane_evidence/TASK_340_unified-shell-plan_planner.md docs/task_board.md` completed with no whitespace errors. Git printed a CRLF normalization warning for `docs/task_board.md`.

## Stop Point

TASK_340 planning output is accepted and complete. Stop here. Do not implement frontend UI. Do not execute TASK_337B or any implementation lane.
