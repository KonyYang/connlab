# TASK_336 Project Lifecycle And Unified Workbench Contract

Status: ready for user review
Created: 2026-06-26
Plan: `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
Lane: `lifecycle-contract`
Role: Planner

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Lane

`lifecycle-contract`

## Allowed Reason

`TASK_335_PARALLEL_EXECUTION_MODEL_AND_BOARD_LANE_TEMPLATE` completed the controlled-parallel governance model. The user approved the first controlled-parallel planning batch on 2026-06-26 and explicitly approved starting `TASK_336 / lifecycle-contract`.

This lane is allowed because it is a Planner contract lane only. It creates a formal task file and reviewable plan for the Project Lifecycle + Unified Workbench series. It does not approve or implement backend lifecycle behavior, frontend Workbench behavior, database schema changes, Office gateway changes, or runtime product changes.

## Objective

Define the contract for Project lifecycle and Unified Workbench work before implementation lanes begin.

The contract must preserve these confirmed business rules:

- `Stop project` means pause and may be resumed.
- `Stopped` is readonly.
- `Stopped` projects cannot edit drafts or execute write operations.
- `Resume project` restores the project to active lifecycle.
- `Close project` supports `Completed` and `Administrative` closure.
- Closed projects are readonly archives.
- Closed projects cannot be resumed.
- Because StepInstance does not exist yet, `Close as completed` v1 uses manual confirmation plus output status summary.
- `Close as completed` v1 is intended for formal/registered projects by default. Temporary/no-LTR projects should use Administrative close unless a later approved task explicitly defines an exception.
- Stop reason is optional. Administrative close reason is required. Completed close note is required.
- The product direction is a unified Project Workbench Shell, not a continued complex 5+2 user mental model.

## Scope

This task may create or update only planning and governance documents:

```text
tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md
docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md
docs/task_board.md
docs/lane_evidence/TASK_336_lifecycle-contract_planner.md
```

## Out Of Scope

This task must not:

- implement product code
- change backend services, API behavior, frontend UI, database schema, Office gateways, or runtime behavior
- execute `TASK_337B` or `TASK_340`
- approve backend lifecycle implementation
- approve frontend Workbench implementation
- implement Report generation
- implement StepInstance or execution persistence
- introduce AI, permissions, LAN/server, or multi-user scope
- change public-drive authority, LTR workbook write behavior, Project Folder generation behavior, Matrix authority, Fee authority, or Basic Information authority behavior

## Contract Decisions

### Lifecycle State Model

The contract defines a lifecycle overlay separate from existing project progress/status values:

```text
lifecycle_state: active | stopped | closed
closure_type: null | completed | administrative
```

Existing project progress/status values should remain compatibility data until an approved implementation task changes them. Do not use legacy `cancelled` as the long-term product meaning for stopped projects.

### State Transitions

Allowed lifecycle transitions:

```text
active -> stopped
stopped -> active
active -> closed completed
active -> closed administrative
stopped -> closed completed
stopped -> closed administrative
```

Completed-close eligibility:

- `active -> closed completed` and `stopped -> closed completed` are valid lifecycle transitions only for formal/registered projects in the first implementation.
- Temporary or no-LTR planning projects should close through `closed administrative` by default.
- A future task may approve an explicit exception rule, but TASK_336 does not.

Forbidden lifecycle transitions:

```text
closed -> active
closed -> stopped
closed completed -> closed administrative
closed administrative -> closed completed
```

### Readonly Rules

`stopped` and `closed` both block write operations.

`stopped` still allows:

- view Project Workbench
- view Matrix
- view Basic Information
- view Fee, Test Record, Project Folder, LTR, output status, and history
- Resume project
- Close project

`closed` allows viewing only. It must not expose Resume.

### Close As Completed v1

Because StepInstance and execution persistence are not implemented, `Close as completed` v1 must not pretend ConnLab can automatically verify testing completion.

`Close as completed` v1 is default-scoped to formal/registered projects. Temporary or no-LTR planning projects should use Administrative close unless a future approved task explicitly adds an exception.

The first implementation must use:

- output status summary
- required operator confirmation
- required close note
- explicit warning that completion is manually confirmed for this phase

The output summary should include current available signals such as Matrix authority, Project Folder readiness, required form/output freshness, LTR sync/public-drive status where available, and known blockers or warnings. Exact data providers belong to implementation tasks, not this contract task.

### Administrative Close

`Close administratively` is for projects that will not continue, including customer cancellation, sample issue, request withdrawal, duplicate project, or internal administrative stop.

It requires a reason and creates a readonly archive. It does not require testing completion.

Reason contract:

- Stop reason is optional.
- Administrative close reason is required.
- Completed close note is required.

### Unified Workbench Direction

Stopped and closed projects should not become separate pages. They should use the same Project Workbench Shell with lifecycle-aware banners, allowed actions, disabled write actions, and clear readonly explanations.

The Workbench Shell should organize by project lifecycle and next action, not by implementation modules or a toolbox of buttons.

## Approved Follow-Up Lanes

These lanes are approved but blocked until this contract is accepted:

```text
TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX
TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN
```

These lanes are not product implementation lanes. They must not change backend/frontend runtime behavior.

## Recommended Future Series

After this contract is accepted, the series should continue with:

```text
TASK_337A_PROJECT_LIFECYCLE_BACKEND_STATE_AND_EVENTS
TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX
TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION
TASK_339A_WORKBENCH_LIFECYCLE_FRONTEND_READONLY_MODEL
TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS
TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN
TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION
TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT
```

`TASK_337A`, `TASK_338`, `TASK_339A`, `TASK_339B`, `TASK_341`, and `TASK_342` require separate explicit approval before execution.

## Validation

Documentation validation is sufficient for this task.

Required checks:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path tasks\TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md
Test-Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md
Select-String -Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md -Pattern 'Stop project means pause'
Select-String -Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md -Pattern 'Close as completed'
Select-String -Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md -Pattern 'Unified Workbench'
Select-String -Path docs\lane_evidence\TASK_336_lifecycle-contract_planner.md -Pattern 'ready_for_review'
```

Acceptance criteria:

- The contract captures Stop/Resume/Close semantics.
- The contract distinguishes stopped readonly from closed archive.
- The contract defines completed and administrative closure.
- The contract states that completed close v1 is manual confirmation plus output summary.
- The contract states that completed close v1 is default-scoped to formal/registered projects.
- The contract fixes reason requirements: stop optional, administrative close required, completed close note required.
- The contract preserves the current no-StepInstance boundary.
- The contract defines follow-up lane sequencing and blocks product implementation.
- The contract supports Unified Project Workbench Shell planning without implementing UI.
- No backend, frontend, database, Office, or runtime product files are changed.

## Stop Point

Stop after producing this task file, the plan file, and Planner evidence. Wait for user review. Do not execute `TASK_337B` or `TASK_340`.
