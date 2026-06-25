# TASK_335 Parallel Execution Model And Board Lane Template

Status: proposal for review only; not approved for implementation
Created: 2026-06-25
Plan: `docs/task_335_parallel_execution_model_and_board_lane_template_plan.md`

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

None for implementation. `TASK_334E_FEE_FORM_COM_SECOND_PASS_OPTIMIZATION` is complete. `TASK_334F_LTR_WORKBOOK_READONLY_OPEN_AT_EXACT_DL_MATCH` is proposed only and must not be implemented by this task.

## Allowed Reason

ConnLab's current single-active-task governance protects scope but blocks safe project-level parallelism for independent lanes such as frontend-only work, backend read-only work with stable contracts, test-only coverage, docs/smoke checklist work, review, and integration. This task is a bounded documentation/process slice to define controlled parallel execution without changing product behavior.

This task is allowed only as the governance-freeze exception described in `docs/task_335_parallel_execution_model_and_board_lane_template_plan.md`.

## Objective

Introduce a controlled parallel execution model in documentation so ConnLab can later support multiple approved lanes while preserving:

- one task per executor/Agent at a time
- explicit task files
- plan-before-implementation
- explicit user approval
- task board as source of truth
- review and validation gates
- stop points after each lane

## Scope

This task may update or create only documentation/process files:

```text
AGENTS.md
docs/task_board.md
docs/project_management/PARALLEL_EXECUTION_MODEL.md
tasks/TASK_335_PARALLEL_EXECUTION_MODEL_AND_BOARD_LANE_TEMPLATE.md
```

## Out Of Scope

This task must not:

- implement TASK_334F or any product task
- change backend, frontend, database, Office, Matrix, Fee, LTR, Project Folder, or runtime behavior
- introduce multi-user product features, permissions, LAN/server deployment, or collaboration runtime scope
- edit product source code or tests
- approve any real active lane beyond an inactive template
- allow unapproved implementation work

## Required Design Decisions

The final documentation must define:

1. Controlled active lanes.
2. Planner, Developer, Reviewer, Integrator, and QA / Smoke Owner roles.
3. Lane statuses.
4. Required lane fields:
   - task id
   - owner role
   - branch/worktree
   - dependencies
   - conflict scope
   - `May Touch`
   - `Must Not Touch`
   - `Locked Paths`
   - validation gate
   - merge gate
5. Developer, Planner, and Integrator boundaries for updating `docs/task_board.md`.
6. Parallel-safe task categories.
7. Serialized/high-risk task categories.
8. Contract-first split rule for frontend/backend parallelism.
9. Governance freeze exception exit condition back to implementation work.

## Validation

Documentation validation is sufficient for this task.

Required checks:

- `AGENTS.md` still requires formal task files, plans, explicit approval, validation, and stop points.
- `docs/task_board.md` remains the source of truth.
- Proposed/planned lanes remain non-executable.
- Only approved lanes may be implemented.
- Lane template contains `May Touch`, `Must Not Touch`, and `Locked Paths`.
- The model does not allow unsafe parallel edits to Office gateways, authority paths, database schema, lifecycle state, or task board global status.
- No product behavior or source code changes are included.

Optional mechanical checks:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Select-String -Path AGENTS.md -Pattern 'Controlled Parallel Execution' -Encoding UTF8
Select-String -Path docs\task_board.md -Pattern 'Active Lanes' -Encoding UTF8
Test-Path docs\project_management\PARALLEL_EXECUTION_MODEL.md
Test-Path tasks\TASK_335_PARALLEL_EXECUTION_MODEL_AND_BOARD_LANE_TEMPLATE.md
```

## Stop Point

Stop after documentation changes and validation. Do not start TASK_334F or any other implementation task without separate explicit user approval.
