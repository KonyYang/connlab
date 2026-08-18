# TASK_340 Unified Project Workbench Shell Plan

Last Updated: 2026-06-26
Status: accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: unified-shell-plan
Role: Planner/Designer

## 1. Anti-Skip Statement

Current active lane: `unified-shell-plan`.

Why this work is allowed now: `docs/task_board.md` marks `TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN` as an approved Planner/Designer lane after accepted `TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT`.

This document is planning-only. It does not implement frontend UI, backend behavior, API contracts, lifecycle persistence, Matrix internals, Project Folder behavior, registry behavior, StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope.

## 2. Purpose

The Unified Project Workbench Shell should make Project feel like one lifecycle-aware workspace rather than a collection of separate task pages and stage modes.

Target operator question:

```text
What is this project's lifecycle state, what is authoritative now, what is readonly, and what should I do next?
```

The shell must preserve the approved ConnLab principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

## 3. Source Decisions

Accepted lifecycle contract from TASK_336:

- Stop project means pause and can resume.
- Stopped projects are readonly for drafts and write operations.
- Stopped projects may be resumed or closed.
- Close supports `Completed` and `Administrative`.
- Closed projects are readonly archives.
- Closed projects cannot resume.
- Completed close v1 defaults to formal/registered projects.
- Temporary/no-LTR projects default to Administrative close unless a later approved task defines an exception.
- Stop reason is optional.
- Administrative close reason is required.
- Completed close note is required.
- Current ConnLab has no StepInstance, so completed close v1 is manual confirmation plus output status summary.
- UI copy should expose `Active`, `Stopped`, `Closed: Completed`, and `Closed: Administrative`, not backend enum words such as `cancelled`.

Design constraints from `$impeccable` and frontend architecture rules:

- workflow before tools
- state before action
- Matrix before output
- current capabilities before future promises
- operational, business-readable copy
- restrained Windows-first workbench UI
- feature selectors should calculate display state, disabled state, blockers, and next action
- route pages should compose feature components rather than accumulate large workflow logic
- disabled states need visible reasons when the operator needs to act

## 4. Current Shape To Simplify

Current Workbench already has useful pieces:

- project identity top bar
- stage banner
- Matrix planning/setup entry
- Project Folder preparation
- active Matrix workspace
- Fee Evaluation and Basic Information entry points
- lifecycle management panel
- registry awareness of `Stopped`

Current risk:

```text
temporary planning + registered setup + package preparation + execution console + lifecycle actions + output actions
```

can feel like multiple adjacent products. TASK_340 should not create another tab set. It should define one shell grammar that future implementation lanes can apply gradually.

## 5. Shell Information Architecture

Recommended shell regions:

```text
Project Workbench Shell
  1. Project lifecycle header
  2. Lifecycle state banner
  3. Primary authority workspace
  4. Supporting output rail
  5. History and evidence drawer
```

### 5.1 Project Lifecycle Header

Always visible.

Content:

- project identity: DL/project number when present, product, requestor, project id fallback
- lifecycle label: `Active`, `Stopped`, `Closed: Completed`, or `Closed: Administrative`
- formal identity marker: `Temporary planning` or `Registered project`
- Matrix authority marker: `No Matrix`, `Candidate Matrix`, or `Active Matrix`
- last relevant lifecycle timestamp when stopped or closed
- one contextual primary action when allowed

Rules:

- the header explains state before showing actions
- stopped and closed state must be visible without opening a panel
- closed headers never show Resume
- temporary/no-LTR projects must not visually imply they are completed formal projects

### 5.2 Lifecycle State Banner

The banner appears directly below the header when lifecycle state changes the operator's ability to act.

Banner states:

| State | Banner Title | Supporting Copy | Allowed Primary Action |
|---|---|---|---|
| Active | Current project | Continue from the next project action. | one context-specific action |
| Stopped | Stopped project | This project is paused. Resume it before making changes. | Resume project |
| Closed completed | Closed: Completed | This project is archived as completed and is readonly. | none |
| Closed administrative | Closed: Administrative | This project is archived administratively and is readonly. | none |

Stopped secondary action:

- `Close project`

Closed secondary action:

- view history or close summary only

Disabled write reason:

```text
Resume this project before editing or updating files.
```

Closed disabled write reason:

```text
Closed projects are readonly.
```

### 5.3 Primary Authority Workspace

The central workspace should be selected by project readiness, not by a user-facing collection of tools.

Priority order:

1. Active Matrix authority workspace when an active Matrix exists.
2. Matrix authority setup when the project is registered but has no active Matrix.
3. Temporary planning workspace when the project has no registered LTR.
4. Readonly archive workspace when the project is stopped or closed.

The Matrix authority workspace remains the first-class work surface after Matrix authority exists:

- Matrix authority bar
- group/step overview
- selected group/step inspector
- compact downstream status strip

Do not make Project Folder, Fee Evaluation, or Required Forms visually outrank Matrix after Matrix authority exists.

### 5.4 Supporting Output Rail

The supporting output rail summarizes derived or downstream surfaces.

Current-feature entries only:

- Basic Information
- Project Folder
- Required Forms
- Fee Evaluation
- LTR/Public Drive status when available
- output freshness where current data supports it

Rules:

- entries should be compact status/action rows, not full competing panels
- write actions disabled in stopped and closed states
- readonly previews may remain available when a future implementation lane confirms they do not mutate state
- no visible Report generation, AI review, StepInstance, image management, permissions, or collaboration controls in the current shell

### 5.5 History And Evidence Drawer

The history drawer is a supporting readonly surface.

Content:

- lifecycle events: stop, resume, close completed, close administrative
- reason/note/operator/timestamp where available
- completed close summary when available
- output status summary used for completed close v1
- source evidence links already available through current features

Rules:

- do not turn history into an editable activity feed
- do not expose future multi-user collaboration
- stopped and closed projects should remain inspectable here

## 6. State-Specific Shell Behavior

### 6.1 Active Temporary Or No-LTR Project

Operator label:

```text
Temporary planning
```

Primary workspace:

- Matrix and Fee planning before formal registration

Allowed:

- edit Matrix draft or candidate where current implementation supports it
- estimate Fee when Matrix draft exists
- stop project
- administrative close in a later lifecycle implementation lane

Not allowed by this plan:

- imply project is formally completed
- show completed close as the default action
- show Project Folder package generation as primary

### 6.2 Active Registered Project Without Active Matrix

Operator label:

```text
Matrix authority setup
```

Primary workspace:

- create, review, or confirm Matrix authority

Allowed:

- open Matrix workflow
- show Basic Information and LTR context
- stop project

Design emphasis:

- active Matrix is required before derived outputs feel primary

### 6.3 Active Registered Project With Active Matrix

Operator label:

```text
Active project
```

Primary workspace:

- Matrix authority workspace

Supporting surfaces:

- Project Folder
- Required Forms
- Fee Evaluation
- Basic Information
- Public Drive/LTR status

Design emphasis:

- Matrix map is authoritative
- downstream outputs are status entries and entry points
- next action comes from the highest-impact blocker or stale output that current data can support

### 6.4 Stopped Project

Operator label:

```text
Stopped project
```

Primary workspace:

- readonly version of the same shell

Allowed:

- view project
- view Matrix authority and draft history
- view Basic Information
- view Fee Evaluation
- view Project Folder status
- view output records
- view history
- Resume project
- Close project

Blocked:

- edit Basic Information
- confirm Basic Information
- edit or confirm Matrix
- edit or confirm Fee
- generate or update Project Folder outputs
- generate Required Forms
- upload/write public-drive files
- create future execution records or evidence

Banner:

```text
Stopped project
This project is paused. Resume it before making changes.
```

### 6.5 Closed Completed Project

Operator label:

```text
Closed: Completed
```

Primary workspace:

- readonly archive summary

Allowed:

- view shell
- view Matrix and output status
- view completed close summary
- view lifecycle history

Blocked:

- all write operations
- Resume project
- stop project
- close project again

Completed close note:

- required by contract
- should be visible in history/close summary

Completed close eligibility:

- v1 defaults to formal/registered projects
- temporary/no-LTR projects should use Administrative close unless a later approved task defines an exception

### 6.6 Closed Administrative Project

Operator label:

```text
Closed: Administrative
```

Primary workspace:

- readonly archive summary with administrative reason emphasis

Allowed:

- view shell
- view available project artifacts
- view administrative close reason
- view lifecycle history

Blocked:

- all write operations
- Resume project
- stop project
- close project again

Administrative close reason:

- required by contract
- should be prominent enough that operators do not confuse it with completed project work

## 7. Navigation Model

Do not expose the old mental model as a large tab set.

Recommended future shell anchors:

```text
Project State
Matrix
Outputs
History
```

Meaning:

- `Project State`: identity, lifecycle, next action, blockers
- `Matrix`: authority map, candidate state, selected group/step detail
- `Outputs`: Basic Information, Project Folder, Required Forms, Fee, Public Drive/LTR status
- `History`: lifecycle events, close summary, source evidence

These anchors are information regions, not necessarily route tabs. A future implementation may render them as scroll anchors, compact segmented controls, or responsive panels, but the operator should still feel they are inside one Project Workbench.

## 8. Action Model

Action rules:

- one visible primary action should match the current highest-priority next action
- secondary actions stay close to the surface that owns them
- destructive or lifecycle-changing actions require confirmation in implementation lanes
- disabled write actions must explain the lifecycle reason
- stopped state may show `Resume project` and `Close project`
- closed states show no Resume action

Action priority:

1. lifecycle restriction or archive state
2. missing Matrix authority
3. active Matrix attention
4. derived output freshness or setup completeness
5. readonly history/evidence inspection

## 9. Current-Feature-Only Rule

The shell may mention future scope only in planning documents. It must not expose unavailable product actions in the UI.

Do not show current UI entries for:

- StepInstance execution persistence
- test result entry
- image evidence management
- Report generation
- AI review
- permission management
- LAN/server collaboration
- multi-user assignments

Future implementation lanes may add these only after explicit task approval and contract work.

## 10. Future Implementation Split

Recommended serial order:

1. `TASK_337B` guard inventory and test matrix remains independent and may run separately.
2. `TASK_337A` backend lifecycle/API contract and implementation shape must be approved before frontend readonly behavior depends on lifecycle API data.
3. `TASK_338` write guard integration must establish broad write blocking before the shell treats stopped/closed blocking as product-wide.
4. `TASK_339A` Workbench lifecycle readonly model should establish frontend lifecycle display types, disabled model, and stopped/closed banners after the backend/API lifecycle shape from `TASK_337A` is stable. Broad write blocking depends on `TASK_338`.
5. `TASK_339B` Projects registry lifecycle views should keep stopped projects visible in Planning or On-going and closed projects in Closed.
6. `TASK_341` Unified Project Workbench Shell implementation may start only after user approval and after its dependencies are satisfied.
7. Integration/QA should verify stopped/closed readonly behavior across Workbench surfaces.

TASK_341 should preserve existing feature components where practical and avoid a large rewrite.

## 11. Future Smoke Checklist

Future implementation lane should manually or automatically verify:

- Active temporary project shows `Temporary planning`.
- Active temporary project does not default to Completed close.
- Active registered project without Matrix shows Matrix authority setup as primary.
- Active registered project with active Matrix shows Matrix as primary workspace.
- Stopped temporary project is visible and readonly.
- Stopped registered project is visible and readonly.
- Stopped project shows Resume and Close actions.
- Stopped project disables draft edits and file writes with a visible lifecycle reason.
- Closed completed project is readonly and has no Resume action.
- Closed completed project shows completed close note and output status summary.
- Closed administrative project is readonly and has no Resume action.
- Closed administrative project shows administrative reason.
- Closed projects cannot expose stop, resume, or close-again actions.
- Project Folder, Required Forms, Fee, Matrix confirm, Basic Information confirm, and Public Drive write actions are blocked in stopped and closed states.
- Readonly preview endpoints remain available only when `TASK_337B` or `TASK_338` classifies them as non-mutating.
- History remains readable in stopped and closed states.
- Current shell does not expose StepInstance, Report generation, AI, permissions, LAN/server, or multi-user controls.
- Narrow viewport preserves lifecycle label, readonly reason, and primary action without overlapping text.
- Keyboard focus order reaches header, banner, primary workspace, outputs, and history in a logical order.

## 12. Risks And Mitigations

### Risk: Shell plan becomes a hidden implementation request

Mitigation: this task defines IA and smoke expectations only. Product code remains locked until a future implementation lane is approved.

### Risk: Stopped projects remain visually equivalent to cancelled/deleted projects

Mitigation: shell copy uses `Stopped project`, keeps the project readable, and exposes Resume as the key difference from closed archive.

### Risk: Closed completed overclaims laboratory execution

Mitigation: completed close v1 is manual confirmation plus output status summary because StepInstance does not exist.

### Risk: Temporary planning projects are closed as completed by habit

Mitigation: plan states completed close defaults to formal/registered projects; temporary/no-LTR projects default to Administrative close.

### Risk: Navigation keeps the 5+2 mental model

Mitigation: future shell anchors are `Project State`, `Matrix`, `Outputs`, and `History`, with stage-specific emphasis inside one shell.

### Risk: Matrix loses authority to output tools

Mitigation: active Matrix remains the primary authority workspace; outputs are compact status entries and entry points.

## 13. Acceptance Criteria

TASK_340 is accepted when:

- formal TASK_340 file exists
- shell plan exists
- plan covers active, stopped, closed completed, and closed administrative states
- plan includes readonly banners and action behavior
- plan explains how to reduce the current 5+2 mental model
- plan preserves current-feature-only navigation
- plan excludes future StepInstance, Report, AI, permissions, LAN/server, and multi-user UI exposure
- plan includes future smoke checklist
- evidence file records changed files, validation checks, and stop point
- no frontend/backend runtime behavior changed

## 14. Documentation Validation Commands

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

Expected result:

- all paths exist
- all searched contract terms are present
- diff check has no whitespace errors

## 15. Stop Point

Stop after this plan and lane evidence are ready for user review. Do not implement frontend or backend behavior. Do not execute TASK_337B or any implementation lane.
