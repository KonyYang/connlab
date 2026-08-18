# TASK_345A Project Lifecycle Business Model Contract Plan

Status: planned - ready for Reviewer plan gate, not approved for implementation
Task: `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`
Lane: `project-lifecycle-business-model-contract`
Role: Planner
Date: 2026-06-28

## 1. Discovery Continuation

### Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

### Current Active Task / Lane

No active implementation lane. `docs/task_board.md` reports `TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT` complete and accepted.

### Why Planner Is Allowed

The user asked Planner to continue the completed Discovery Gate after answering the blockers, and explicitly requested only one legal action: create or update the next formal planning lane contract draft. The user also forbade product code edits and Developer routing.

## 2. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/lane_evidence/DISCOVERY_project-lifecycle-business-model-rework_planner.md`
- current `docs/task_board.md` lifecycle series state

The earlier Discovery evidence remains the detailed code/document evidence source for TASK_336 to TASK_344 and lifecycle backend/frontend files.

## 3. Confirmed By User

- Main Workbench lifecycle action should be one primary button.
- Active projects use `Close project`.
- Stopped and closed projects use an Activate direction.
- `Completed = Activate` is the accepted primary-action policy for the prior stopped/closed label blocker. The contract must not keep permanent readonly or Reopen-only semantics.
- `Completed` is no longer a special close path. All close reasons use one unified close form.
- Temporary `Apply/Register LTR` is only a process entrypoint in this first contract series.
- Public-drive LTR workbook authority writing belongs in a later authority lane, not this first business-model contract.

## 4. Confirmed By Repository Evidence

- Current TASK_336 to TASK_344 accepted behavior is incompatible with the new target model:
  - closed projects are readonly archives;
  - closed projects cannot resume;
  - current close type is `completed | administrative`;
  - Workbench and Projects registry expose administrative/archive copy.
- Current backend has audit infrastructure through `project_lifecycle_events`, but no activate/reopen event type for closed projects.
- Current frontend API client has stop/resume/close completed/close administrative helpers, but no activate/reopen helper.
- Current temporary Workbench has a same-project LTR registration placeholder message, not a functional Apply/Register LTR process entrypoint.

## 5. Contract Target

### 5.1 Public Lifecycle States

The contract should preserve a small operator-facing lifecycle vocabulary:

- `Active`: project work can proceed.
- `Closed`: project has reached a business phase end and business writes stay blocked until activation.
- `Stopped`: retained paused or halted project state, business writes stay blocked until activation.
- `Temporary`: identity state for a project without registered LTR/DL, not a lifecycle stop/close state.

Implementation may keep compatibility fields internally, but user-facing copy must not expose `administrative`, `closed_administrative`, `closure_type`, `cancelled`, or raw lifecycle enum names.

### 5.2 Primary Action Policy

The Workbench exposes one primary lifecycle action at a time:

| Project condition | Primary action |
|---|---|
| Active formal/registered | `Close project` |
| Active temporary/no-LTR | `Apply LTR number` or `Register LTR` as the process entrypoint, with close handled by the unified close form only if the contract explicitly permits it |
| Stopped | `Activate project` |
| Closed with reason Completed | `Activate project` |
| Closed with any other business reason | `Activate project` |

`Reopen project` may be considered as supporting copy in later UX work, but TASK_345A target contract uses Activate as the primary action direction.

### 5.3 Close Form

`Close project` uses one unified form. It is not split into completed and administrative endpoints in the product model.

Required fields and signals:

- close reason category:
  - `Completed`
  - `Failed`
  - `Cancelled`
  - `Cannot test`
  - `Duplicate`
  - `Other`
- operator note or reason text, required for all close reasons unless a later contract explicitly loosens it;
- operator identity when available;
- close timestamp.

`Completed` is a business reason, not a special close path. The first implementation should not require a special completed-only output summary acknowledgement unless a later reviewed contract explicitly adds a non-blocking summary preview.

### 5.4 Activate Behavior

Activation is the action that moves a stopped or closed project back into active project work.

The contract must require:

- activation timestamp;
- activation reason or note if the implementation lane chooses to require it;
- operator identity when available;
- previous close reason/category if activating from a closed state;
- previous lifecycle state;
- event ledger entry.

Activation should restore the project to the appropriate active operational state without guessing legacy status. If the prior state cannot be determined from audit/history, the backend implementation lane must return a business-readable conflict rather than inventing a project progress state.

### 5.5 Audit And History

Audit history is a product requirement, not optional telemetry.

The future backend lane must preserve:

- close timestamp;
- close reason category;
- close note;
- close operator;
- activate timestamp;
- activate reason or note when present;
- activate operator;
- previous lifecycle state;
- previous close reason/category;
- previous project progress/status if needed to restore active work safely.

Existing `project_lifecycle_events` may be extended, but this contract must not require a new table if metadata extension is enough. The backend implementation lane owns the exact storage decision.

### 5.6 Temporary Apply/Register LTR Boundary

Temporary projects need a Workbench entrypoint to apply or register LTR.

This TASK_345A contract only authorizes the product model boundary:

- Temporary projects may expose `Apply LTR number` / `Register LTR` as the primary process entrypoint.
- The first contract series must not write to the public-drive LTR workbook authority.
- A later LTR authority lane must define workbook writeback, row ownership, backup/lock behavior, and public-drive validation.
- Until that authority lane exists, implementation lanes may only route to an existing workflow or show a clearly scoped entrypoint that does not claim workbook authority write success.

## 6. Downstream Lane Recommendations

### TASK_345B Project Lifecycle Backend Model / API / Audit

Purpose:
Implement backend business lifecycle model, close reason taxonomy, unified close endpoint, activate endpoint, lifecycle response shape, audit event behavior, and migration compatibility.

Serial dependency:
Must wait for TASK_345A accepted contract.

### TASK_345C Lifecycle Write Guard And Readonly Rule Update

Purpose:
Update stopped/closed write guards so business writes remain blocked until activation, but activation itself is allowed and error details point to Activate.

Serial dependency:
Must wait for backend API/event semantics from TASK_345B.

### TASK_345D Workbench Primary Lifecycle Action UX

Purpose:
Implement one primary Workbench lifecycle action, unified close form, Activate action for stopped/closed, and temporary Apply/Register LTR entrypoint copy/routing.

Serial dependency:
Must wait for TASK_345B and TASK_345C. Temporary authority writing remains excluded.

### TASK_345E Projects Registry Copy / Routing Realignment

Purpose:
Align Projects list state labels, Next Step, and row action copy with Activate and unified close semantics while keeping registry routing-only.

Parallel candidate:
Can plan after TASK_345A, but implementation should wait for backend and Workbench semantics.

### TASK_345F Temporary Apply/Register LTR Entrypoint

Purpose:
Implement only the safe entrypoint/routing for temporary projects if not included in TASK_345D.

Boundary:
Public-drive LTR workbook authority writing remains deferred to a later authority lane.

### TASK_345G LTR Authority Write Lane

Purpose:
Define and implement actual public-drive LTR workbook authority write behavior for temporary-to-formal registration.

Boundary:
Separate lane because AGENTS.md treats public-drive LTR Excel files as current business authority.

### TASK_345H Lifecycle Audit / Migration / QA Closeout

Purpose:
Run integration QA for active, stopped, closed Completed, closed other reasons, temporary Apply/Register LTR entrypoint, audit history, and compatibility migration.

Serial dependency:
Final closeout after implementation lanes.

## 7. Proposed Lane Definition

Lane: `project-lifecycle-business-model-contract`

Task: `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`

Status: `planned`

Owner Role: Planner, then Reviewer plan gate

Depends On:

- `DISCOVERY_project-lifecycle-business-model-rework` checkpoint
- user blocker answers from 2026-06-28
- accepted TASK_344C closeout as current board baseline

Conflict Scope:

- lifecycle business model and downstream contract only;
- no product runtime code.

May Touch:

- `tasks/TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT.md`
- `docs/task_345a_project_lifecycle_business_model_contract_plan.md`
- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`
- `docs/task_board.md` planned/proposed row and next-step text only

Must Not Touch:

- `backend/`
- `frontend/`
- `tests/`
- `frontend/src/api/client.ts`
- public-drive / Office / LTR workbook authority paths
- Matrix, Fee, Folder, Basic Information, Required Forms, Approval Package, Public Drive implementation
- completed TASK_336 to TASK_344 task/plan/evidence files except read-only reference
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

Locked Paths:

- All backend, frontend, test, Office, public-drive, LTR authority, Matrix, Fee, Folder, Basic Information, Report, StepInstance, AI, permissions, LAN/server, and multi-user implementation paths are locked against this lane.
- The TASK_345A planning files listed in May Touch are Planner-owned draft inputs until Reviewer plan gate completes.

Evidence File:

- `docs/lane_evidence/TASK_345A_project-lifecycle-business-model-contract_planner.md`

Validation Gate:

- `git diff --check` over TASK_345A planning files and `docs/task_board.md`.
- Static status check records whether `backend/`, `frontend/`, or `tests/` have existing dirty paths; any such paths are outside this Planner package and must not be routed or packaged as TASK_345A work.
- Plan names downstream lanes and states no implementation approval.

Merge Gate:

- Reviewer plan gate pass.
- User approval required before downstream implementation lanes are created or approved.
- Orchestrator must not route Developer from this `planned` lane.
- Any unrelated product or governance/orchestration dirty residuals remain excluded unless a future approved lane names them.

## 8. Reviewer Plan Gate Focus

The first object ready for Reviewer plan gate is:

`TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT` / lane `project-lifecycle-business-model-contract`.

Reviewer should check:

- Whether the contract correctly incorporates the three user blocker answers.
- Whether it cleanly rejects old permanent closed readonly / administrative semantics as target product meaning.
- Whether temporary Apply/Register LTR is correctly scoped to entrypoint only.
- Whether downstream lane split protects LTR authority and product-code boundaries.
- Whether no implementation lane is accidentally approved.

## 9. Stop Point

Stop after this plan, task file, Planner evidence, and planned board row are created. Do not route Developer implementation.
