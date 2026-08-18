# TASK_336 Project Lifecycle And Unified Workbench Contract Plan

Last Updated: 2026-06-26
Status: ready for user review
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: lifecycle-contract
Role: Planner

## 1. Purpose

This document is the implementation-facing contract for the Project Lifecycle + Unified Workbench series.

It exists to prevent downstream lanes from mixing product semantics, schema decisions, API behavior, UI shell changes, and write-operation guards without a shared contract.

This plan is contract-only. It does not implement product behavior.

## 2. Inputs

The contract is based on:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/lane_evidence/TASK_336_lifecycle-contract_planner.md`
- historical thread `019ed7ca-d5a3-7b32-92da-71094346e805`
- `PRODUCT.md` and `DESIGN.md` through `$impeccable` product context

Confirmed historical decisions:

- Stop project means pause and can resume.
- Temporary projects may later become formal projects by applying/registering an LTR.
- A stopped project may also be closed instead of resumed.
- Stopped is readonly and cannot edit draft information.
- Close supports Completed and Administrative closure.
- Close as completed v1 is default-scoped to formal/registered projects.
- Temporary/no-LTR planning projects should use Administrative close unless a later approved task explicitly defines an exception.
- Stop reason is optional. Administrative close reason is required. Completed close note is required.
- Closed is readonly archive and cannot resume.
- Current ConnLab has no StepInstance, so completed close v1 uses manual confirmation plus output status summary.
- The direction is unified Project Workbench Shell, not more separate mental models.

## 3. Non-Goals

TASK_336 must not:

- change product source code
- create database schema
- add API routes
- change existing route behavior
- change frontend UI
- change Office, LTR, Project Folder, Matrix, Fee, Basic Information, Public Drive, or output behavior
- implement StepInstance, execution persistence, Report generation, AI, permissions, LAN/server, or multi-user features
- run `TASK_337B` or `TASK_340`

## 4. Current Architecture Baseline

Existing relevant files discovered during planning:

```text
backend/application/project_lifecycle_service.py
backend/application/project_lifecycle_management_service.py
backend/api/routes_project.py
frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts
frontend/src/pages/ProjectListPage.tsx
frontend/src/features/project-workbench/
frontend/src/api/client.ts
```

Important current behavior:

- `project_lifecycle_management_service.py` maps user-facing `Stopped` to internal `ProjectStatus.CANCELLED`.
- `project_lifecycle_service.py` treats `ProjectStatus.CLOSED` and `ProjectStatus.CANCELLED` as closed-style blockers.
- `ProjectListPage.tsx` already has UI awareness of `stopped` and `cancelled`.
- Workbench lifecycle selectors currently collapse cancelled/stopped into a retained-review state.

Contract implication:

The next implementation should introduce a lifecycle overlay and avoid making `cancelled` the long-term product meaning for paused projects. Existing `cancelled` compatibility can remain during migration, but product language should be `stopped`.

## 5. Lifecycle Contract

### 5.1 Lifecycle State

Use lifecycle state as the authority for whether a project can be changed:

```text
active
stopped
closed
```

Use closure type only when lifecycle state is closed:

```text
completed
administrative
null
```

Recommended implementation vocabulary for future backend lanes:

```text
lifecycle_state: active | stopped | closed
closure_type: completed | administrative | null
stopped_reason
stopped_at
stopped_by
resumed_reason
resumed_at
resumed_by
closed_reason
closed_at
closed_by
completion_confirmed_by
completion_summary_json
```

Prefer a lifecycle event ledger for traceability:

```text
project_lifecycle_events
  project_id
  event_type: stop | resume | close_completed | close_administrative
  reason
  operator
  created_at
  metadata_json
```

This is a contract recommendation, not an implemented schema.

### 5.2 Existing Status Compatibility

Existing `Project.status` values continue to represent compatibility and progress until a backend task changes them.

The future backend lane should decide whether to add fields to project storage, add a side table, or both. That decision must preserve existing LTR, Matrix, Fee, Basic Information, Project Folder, output record, and public-drive workflows.

The contract forbids silently replacing current public-drive LTR Excel authority with local-only lifecycle behavior.

### 5.3 State Transitions

Allowed:

```text
active -> stopped
stopped -> active
active -> closed_completed
active -> closed_administrative
stopped -> closed_completed
stopped -> closed_administrative
```

Completed-close eligibility:

- `active -> closed_completed` and `stopped -> closed_completed` are lifecycle transitions for formal/registered projects in v1.
- Temporary or no-LTR planning projects should use `closed_administrative` by default.
- A later task may explicitly approve an exception rule, but implementations must not infer one from this contract.

Forbidden:

```text
closed_completed -> active
closed_administrative -> active
closed_completed -> stopped
closed_administrative -> stopped
closed_completed -> closed_administrative
closed_administrative -> closed_completed
```

### 5.4 Operator-Facing Labels

Use business-readable labels:

```text
Active
Stopped
Closed: Completed
Closed: Administrative
```

Avoid exposing backend enum words such as `closed_completed` or `cancelled` in UI copy.

## 6. Operation Guard Contract

### 6.1 Read Operations

Allowed for active, stopped, and closed:

- view Project registry row
- view Project Workbench
- view Matrix authority and draft history
- view Basic Information
- view Fee Evaluation
- view Project Folder status
- view LTR status and update previews where explicitly readonly
- view output records
- view history and audit information

Readonly previews that do not mutate state may remain allowed, but each implementation lane must classify preview endpoints carefully.

### 6.2 Write Operations

Blocked for stopped and closed:

- edit Basic Information draft
- confirm Basic Information
- edit Matrix draft
- confirm Matrix
- edit Fee draft
- confirm Fee
- update or generate Project Folder outputs
- write Application Form updates
- generate Fee Form, Customer Feedback, Test Record, Approval Package, or any required form output
- update LTR workbook
- upload or sync public-drive project folder
- collect or place request material
- write Section 2 back to Application Form
- create future execution records or evidence

Allowed for stopped:

- Resume project
- Close project

Allowed for closed:

- view only

### 6.3 Guard Error Contract

When an operation is blocked by lifecycle:

```text
HTTP status: 409 Conflict
Error code: project_lifecycle_readonly
Message for stopped: This project is stopped. Resume it before making changes.
Message for closed completed: This project is closed as completed and is readonly.
Message for closed administrative: This project is closed administratively and is readonly.
```

Downstream implementation may add structured fields:

```json
{
  "code": "project_lifecycle_readonly",
  "project_id": "P1",
  "lifecycle_state": "stopped",
  "closure_type": null,
  "allowed_actions": ["resume", "close"]
}
```

This is a contract example, not implemented by TASK_336.

## 7. API Contract For Future Backend Lane

Future backend implementation should provide lifecycle actions under Project routes or a narrow lifecycle route.

Recommended endpoints:

```text
GET  /api/projects/{project_id}/lifecycle
POST /api/projects/{project_id}/lifecycle/stop
POST /api/projects/{project_id}/lifecycle/resume
POST /api/projects/{project_id}/lifecycle/close-completed
POST /api/projects/{project_id}/lifecycle/close-administrative
```

Recommended request DTOs:

```text
StopProjectRequest:
  reason: string optional
  operator: string optional

ResumeProjectRequest:
  reason: string optional
  operator: string optional

CloseCompletedRequest:
  close_note: string required
  operator: string optional
  manual_completion_confirmed: true
  output_summary_acknowledged: true

CloseAdministrativeRequest:
  reason: string required
  operator: string optional
```

Recommended response DTO:

```text
ProjectLifecycleResponse:
  project_id: string
  lifecycle_state: active | stopped | closed
  closure_type: completed | administrative | null
  status_label: string
  readonly: boolean
  allowed_actions: string[]
  stopped_at: string | null
  closed_at: string | null
  reason: string | null
```

Close completed preview/summary may be either part of the lifecycle GET response or a separate preview endpoint in the implementation task. It must not require StepInstance.

Reason requirements are fixed by this contract:

- Stop reason is optional because Stop means pause/resumable.
- Administrative close reason is required because it archives a project without completion.
- Completed close note is required because v1 relies on operator completion confirmation.

## 8. Completed Close Summary Contract

For v1, close completed requires a summary of current output state and manual confirmation.

Close as completed v1 is default-scoped to formal/registered projects. Temporary or no-LTR planning projects should use Administrative close by default unless a later approved task explicitly defines a narrow exception.

Summary categories should include available signals only:

```text
Project identity
LTR registration and workbook sync state
Matrix authority state
Basic Information state
Fee authority/output state
Project Folder readiness
Required forms and output freshness
Public-drive upload/preview state
Known blockers and warnings
Manual completion note
```

The implementation must not claim all tests are complete unless a future StepInstance task explicitly provides that authority.

## 9. Frontend And Workbench Contract

### 9.1 Unified Shell Direction

Stopped and closed projects remain inside the Project Workbench Shell.

They should show:

- project identity
- lifecycle badge
- readonly banner
- reason and timestamp when available
- allowed actions
- disabled write actions with reasons
- same read surfaces as active projects where data exists

They should not show a separate stopped page or closed page as the primary experience.

### 9.2 Stopped Workbench

Top message:

```text
Stopped project
This project is paused. Resume it before making changes.
```

Visible primary actions:

```text
Resume project
Close project
```

Disabled actions should explain:

```text
Resume this project before editing or updating files.
```

### 9.3 Closed Workbench

Completed close message:

```text
Closed: Completed
This project is archived as completed and is readonly.
```

Administrative close message:

```text
Closed: Administrative
This project is archived administratively and is readonly.
```

No Resume action.

### 9.4 Projects Registry

Recommended registry views:

```text
On-going
Planning
Closed
All
```

Classification guidance:

- Planning: temporary or no registered LTR, not closed
- On-going: formal active or stopped projects with registered LTR or formal project identity, not closed
- Closed: closed completed and closed administrative
- All: all visible projects

Stopped projects should remain findable in On-going or Planning depending on whether they are formal or temporary. They should not be hidden as cancelled.

### 9.5 Design Rules

Use ConnLab product design rules:

- state before action
- workflow before tools
- preview before write
- Matrix before output
- no future-feature showcase
- no generic toolbox page
- no decorative dashboard treatment

## 10. Downstream Lane Plan

### TASK_337A Project Lifecycle Backend State And Events

Type: backend implementation

Must wait for explicit approval.

Scope:

- lifecycle storage strategy
- lifecycle event/audit records
- lifecycle API routes
- typed DTOs
- migration/compatibility from current stopped/cancelled behavior
- backend tests

Must not:

- change frontend shell
- touch Office gateways
- implement broad write guards beyond lifecycle actions

### TASK_337B Project Lifecycle Guard Inventory And Test Matrix

Type: docs/test-planning

Approved but blocked until TASK_336 is accepted.

Scope:

- inventory all write routes/services
- classify read, readonly preview, write, close, resume
- define expected active/stopped/closed behavior
- propose focused tests for TASK_338

Must not:

- change product behavior
- update backend/frontend source code

### TASK_338 Project Lifecycle Write Guard Integration

Type: backend implementation

Must wait for explicit approval and completion of TASK_337A and TASK_337B.

Scope:

- integrate lifecycle write guards into approved write paths
- return business-readable 409 errors
- keep active behavior unchanged

Must not:

- redesign UI
- implement StepInstance
- change Office mappings or public-drive authority behavior except to block writes by lifecycle

### TASK_339A Workbench Lifecycle Frontend Readonly Model

Type: frontend implementation

Must wait for explicit approval and stable backend/API contract.

Scope:

- frontend lifecycle types
- client functions
- readonly selectors
- disabled action model
- stopped/closed banners

Must not:

- broad Workbench shell redesign
- backend implementation

### TASK_339B Projects Registry Lifecycle Views

Type: frontend implementation

Must wait for explicit approval and stable lifecycle contract.

Scope:

- On-going, Planning, Closed, All registry views
- lifecycle labels and badges
- stopped projects remain visible

Must not:

- backend lifecycle implementation
- Workbench shell implementation

### TASK_340 Unified Project Workbench Shell Plan

Type: docs/ux-planning

Approved but blocked until TASK_336 is accepted.

Scope:

- information architecture
- active/stopped/closed shell states
- how to reduce 5+2 mental model
- smoke checklist for future implementation

Must not:

- implement frontend UI
- change API contracts

### TASK_341 Unified Project Workbench Shell Implementation

Type: frontend implementation

Must wait for explicit approval and completed TASK_339A/TASK_340.

Scope:

- shell layout implementation
- preserve existing feature components
- lifecycle-aware navigation and readonly surfaces

Must not:

- backend behavior
- StepInstance or Report generation

### TASK_342 Lifecycle Integration QA And Board Closeout

Type: integration/QA

Must wait for explicit approval and completion of implementation lanes.

Scope:

- integration validation
- manual smoke
- review/QA evidence
- final board update by Integrator

## 11. First Approved Execution After This Contract

After user accepts TASK_336, the already-approved blocked lanes may proceed:

```text
TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX
TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN
```

They may proceed in parallel because they are documentation/planning lanes and do not modify product behavior.

Backend and frontend implementation lanes remain unapproved.

## 12. Validation Plan

Documentation-only validation:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path tasks\TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md
Test-Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md
Select-String -Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md -Pattern 'Stop project means pause' -Encoding UTF8
Select-String -Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md -Pattern 'Close as completed' -Encoding UTF8
Select-String -Path docs\task_336_project_lifecycle_and_unified_workbench_contract_plan.md -Pattern 'Unified Workbench' -Encoding UTF8
Select-String -Path docs\lane_evidence\TASK_336_lifecycle-contract_planner.md -Pattern 'ready_for_review' -Encoding UTF8
git diff --check -- tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md docs/lane_evidence/TASK_336_lifecycle-contract_planner.md docs/task_board.md
```

Expected result:

- task file exists
- plan file exists
- lifecycle semantics are present
- evidence records ready_for_review
- no whitespace errors, CRLF warnings are non-blocking if present

## 13. Risks

### Risk: Lifecycle state duplicates existing project status

Mitigation:

Define lifecycle as a separate overlay and keep compatibility status until a backend implementation task chooses the persistence strategy.

### Risk: Close completed overclaims test completion

Mitigation:

Require manual confirmation plus output summary until StepInstance exists.

### Risk: Stopped projects are hidden as cancelled

Mitigation:

Registry contract says stopped projects stay visible in Planning or On-going based on formal project identity.

### Risk: Guard scope misses a write path

Mitigation:

Run TASK_337B guard inventory before TASK_338 write-guard integration.

### Risk: Unified Workbench becomes a large rewrite

Mitigation:

TASK_340 plans information architecture first. TASK_341 should preserve existing feature components and only reshape shell behavior after approval.

## 14. Acceptance Criteria

TASK_336 is acceptable when:

- formal task file exists
- contract plan exists
- Stop/Resume/Close semantics are unambiguous
- stopped readonly and closed readonly are distinct
- completed and administrative close are distinct
- completed close v1 is default-scoped to formal/registered projects
- temporary/no-LTR planning projects default to administrative close
- stop reason is optional
- administrative close reason is required
- completed close note is required
- completed close v1 is manual confirmation plus output summary
- no-StepInstance boundary is explicit
- write guard contract is clear
- Workbench readonly shell contract is clear
- Projects registry classification is clear
- downstream lanes and dependency gates are clear
- product implementation remains unapproved
- Planner evidence is updated

## 15. Stop Point

TASK_336 stops here for user review.

Do not execute TASK_337B or TASK_340 until the user accepts this contract.
