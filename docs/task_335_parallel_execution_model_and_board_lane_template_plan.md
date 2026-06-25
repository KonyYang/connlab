# TASK_335 Parallel Execution Model And Board Lane Template Plan

Last Updated: 2026-06-25
Status: proposal for review only; not approved for implementation
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Board Baseline: TASK_334E_FEE_FORM_COM_SECOND_PASS_OPTIMIZATION complete; TASK_334F_LTR_WORKBOOK_READONLY_OPEN_AT_EXACT_DL_MATCH is proposed only

## 1. Purpose

ConnLab has grown from a small sequential MVP into a complex offline Windows-first workbench involving Matrix authority, Project Folder orchestration, Fee Evaluation, LTR workbook sync, Word/Excel Office gateways, SQLite-backed local state, and frontend runtime/workbench surfaces.

The current governance model deliberately prevents AI from skipping stages:

- one current active task in `docs/task_board.md`
- plan first, user approval before implementation
- implement only the approved task
- update board after completion
- stop before the next task

This has protected ConnLab from scope creep and architecture drift, but it now limits throughput when multiple tasks are actually independent. The goal of TASK_335 is to introduce a controlled parallel execution model without weakening task scope, approval, validation, or board authority.

## 2. Governance Freeze Exception

`docs/runtime_governance_freeze_rule.md` forbids governance-only expansion unless there is a concrete blocker, impact on implementation, and exit condition. TASK_335 is allowed only as a narrow exception with the following evidence.

Concrete blocker:

- The current single-active-task board model prevents safe parallel work even when tasks are independent, such as frontend-only polish, backend read-only services with stable contracts, test-only regression coverage, documentation/smoke checklist work, and QA review of completed branches.
- The existing process has role concepts only implicitly. Review currently runs as executor self-check rather than as an independently schedulable lane.
- The board has no place to declare branch/worktree, conflict scope, file locks, validation gate, or merge owner for concurrent work.

Impact on active implementation slices:

- Independent work has to wait behind unrelated Office/COM, Project Folder, LTR, Matrix, or UI tasks even when there is no file or authority-path conflict.
- Frontend/backend contract-first work cannot be split cleanly because the board can name only one executable task at a time.
- QA and review work cannot run in parallel with implementation without violating the current active-task wording.

Exit condition:

- TASK_335 may only add a formal task file, a bounded parallel execution model document, and inactive task-board lane template text.
- TASK_335 must not open a chain of further governance tasks unless a later product implementation task exposes a concrete blocker.
- After TASK_335, the next active work must return to product implementation, integration, validation, or a user-approved concrete follow-up.

## 3. Non-Goals

This task must not:

- start TASK_334F or any other product implementation task
- change backend, frontend, database, Office, Matrix, Fee, LTR, Project Folder, or runtime behavior
- introduce multi-user product features, permissions, LAN/server deployment, or collaboration runtime scope
- replace `docs/task_board.md` as the source of truth
- allow a single executor/Agent to implement multiple tasks at the same time
- remove the requirement for explicit user approval before implementation
- turn governance into an open-ended process redesign with no consumable output

## 4. Proposed Execution Model

Replace the current project-wide single active task assumption with controlled active lanes:

```text
Current model:
  one project -> one active task -> one executor -> stop

Proposed model:
  one project -> multiple approved lanes when parallel-safe
  one lane -> one task -> one executor -> isolated branch/worktree -> review -> integration
```

Core rule:

```text
A single executor/Agent may work on only one task at a time.
The ConnLab project may have multiple active lanes only when Planner marks them as approved and parallel-safe in docs/task_board.md.
```

## 5. Roles

### Planner

Responsibilities:

- maintain the global execution model in `docs/task_board.md`
- split large task groups into lane-sized tasks
- decide whether tasks are parallel-safe
- define dependencies, conflict scopes, allowed files/modules, file locks, and validation gates
- approve active lanes only after user confirmation

Planner must not silently convert a proposed task into an implementation task.

### Developer

Responsibilities:

- work on exactly one approved lane
- use the lane branch/worktree declared in `docs/task_board.md`
- read `AGENTS.md`, `docs/task_board.md`, current task file, and referenced docs
- implement only the lane task
- run lane-specific validation
- submit completion evidence for review

Developer must not edit files outside the lane scope unless the Planner updates the lane definition.

Developer board updates during parallel execution:

- Developer may update only lane-local evidence if the lane definition explicitly allows it.
- Developer must not change global current phase, global next task, unrelated lane rows, or merge status.
- If a lane is completed, Developer records completion evidence in the lane output or final response; Integrator performs the authoritative `docs/task_board.md` status update.

### Reviewer

Responsibilities:

- review scope compliance, architecture boundaries, regression risk, and test coverage
- use `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- verify that the lane did not implement future scope or cross another lane's conflict boundary
- request fixes before integration when needed

Reviewer should not be the same executor that implemented the lane unless explicitly accepted for a low-risk lane.

### Integrator

Responsibilities:

- merge approved lanes
- resolve conflicts
- run affected integration validation
- update `docs/task_board.md` after merge
- record final lane status, validation evidence, and next recommended task/lane

Only Planner or Integrator should update global `docs/task_board.md` execution state during controlled parallel work.

### QA / Smoke Owner

Responsibilities:

- maintain manual smoke paths for high-risk flows
- capture real Office/COM/LTR/Project Folder timing or behavior evidence when required
- separate reproducible defects from feature requests

## 6. Lane Definition Template

Add an `Active Lanes` section to `docs/task_board.md` when controlled parallel execution is enabled.

```md
## Active Execution Model

Mode: controlled-parallel

Global rules:

- A single executor/Agent may work on only one task at a time.
- Multiple lanes are allowed only when this board marks them as approved lanes.
- Each lane must use an isolated branch or worktree.
- Cross-lane merge requires Reviewer and Integrator gates.
- Planner/Integrator own global task board updates during parallel work.
- Developer may update only lane-local evidence when explicitly allowed by the lane.

## Active Lanes

| Lane | Task | Type | Status | Branch / Worktree | Owner Role | Depends On | Conflict Scope | May Touch | Must Not Touch | Locked Paths | Validation Gate | Merge Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ltr-office | TASK_334F | backend/office | proposed | TBD | Developer | TASK_334E | LTR workbook gateway, LTR workbook preview/read path | TBD | Matrix, Fee, Project Folder orchestration, frontend UI | TBD | unit + focused COM/read-only smoke | Reviewer + Integrator |
```

Field meanings:

- `Conflict Scope`: business or architecture boundary that may conflict with other lanes.
- `May Touch`: allowed files, directories, or modules.
- `Must Not Touch`: forbidden files, directories, modules, workflows, or authority paths.
- `Locked Paths`: files or directories reserved exclusively by this lane while it is active.
- `Validation Gate`: exact checks required before review or integration.
- `Merge Gate`: who must approve merge and what final integration evidence is required.

Recommended lane statuses:

- `proposed`
- `planned`
- `approved`
- `in_progress`
- `review`
- `integration`
- `blocked`
- `complete`
- `cancelled`

## 7. Parallel-Safe Rules

A task may be approved as a parallel lane only if all of the following are true:

1. It has a task file and, when implementation is non-trivial, a plan file with explicit scope.
2. It declares dependencies and does not depend on an incomplete lane.
3. It declares conflict scope and expected touched modules.
4. It declares `May Touch`, `Must Not Touch`, and `Locked Paths`.
5. It has an isolated branch/worktree.
6. It has lane-specific validation.
7. It does not require the same authority path or shared mutable workflow as another active lane.
8. Planner has marked it as approved in `docs/task_board.md` after user approval.

Examples that are usually parallel-safe:

- frontend-only UI polish that does not change API contracts
- backend-only read service with stable DTO contract
- test-only regression coverage
- documentation or smoke checklist updates
- independent parser hardening with isolated fixtures
- QA validation against a completed branch

Examples that should normally remain serialized:

- Office COM gateway changes touching the same Word/Excel path
- Project Folder Required Forms orchestration changes
- SQLite schema or repository contract changes
- Matrix authority, Fee draft, Basic Information authority, or LTR authority changes
- changes to `docs/task_board.md` global status from multiple lanes
- frontend and backend work where the API contract is not yet approved

## 8. Contract-First Split Rule

For frontend/backend parallel work, create a small contract task before implementation lanes.

Recommended split:

```text
TASK_XXX_CONTRACT
  defines DTOs, endpoint shape, error semantics, state transitions, sample payloads, and acceptance examples

TASK_XXXA_BACKEND
  implements backend against the approved contract

TASK_XXXB_FRONTEND
  implements UI/client behavior using approved contract and mocks if needed

TASK_XXXC_INTEGRATION
  merges backend + frontend and runs end-to-end validation
```

The contract task should be short and reviewable. It should not become a broad architecture task unless a real implementation blocker is documented.

## 9. AGENTS.md Change Proposal

Update the `How to Work on Tasks`, `Task Board Is The Current Source Of Truth`, and `Anti-Skip Protocol` sections to distinguish executor-level serialization from project-level controlled parallelism.

Proposed wording:

```md
## Controlled Parallel Execution

ConnLab supports controlled parallel execution only through `docs/task_board.md` active lanes.

Rules:

1. A single executor/Agent may work on only one task at a time.
2. The project may have multiple active lanes only when `docs/task_board.md` marks them as approved lanes.
3. Every lane must declare task id, owner role, branch/worktree, dependencies, conflict scope, May Touch, Must Not Touch, Locked Paths, validation gate, and merge owner.
4. Executors must not edit files outside their lane scope.
5. Developer may update only lane-local evidence if the lane explicitly allows it.
6. `docs/task_board.md` global execution state may only be updated by Planner or Integrator during parallel execution.
7. Parallel lanes touching the same authority path, Office gateway, database schema, lifecycle state, or locked path must be serialized unless Planner explicitly marks the boundary safe.
8. After a lane completes, it enters review; it must not be merged until Reviewer and Integrator gates pass.
```

Existing task controls remain active:

- read the formal TASK file
- plan before implementation
- explicit user approval before implementation
- implement only approved scope
- run validation
- stop after lane completion

## 10. Files To Change If Approved

Required documentation-only changes:

```text
AGENTS.md
docs/task_board.md
docs/project_management/PARALLEL_EXECUTION_MODEL.md
tasks/TASK_335_PARALLEL_EXECUTION_MODEL_AND_BOARD_LANE_TEMPLATE.md
```

No source code, tests, frontend, backend, database, Office, or runtime behavior should change in TASK_335.

## 11. Implementation Steps

1. Create `tasks/TASK_335_PARALLEL_EXECUTION_MODEL_AND_BOARD_LANE_TEMPLATE.md` as the formal executable task file.
2. Create `docs/project_management/PARALLEL_EXECUTION_MODEL.md`.
3. Update `AGENTS.md` to add controlled parallel execution rules while preserving existing task approval rules.
4. Update `docs/task_board.md` with an inactive lane template and clarify that no real lane is active until explicit user approval.
5. Review the final text against `docs/runtime_governance_freeze_rule.md` to confirm the governance exception remains bounded and has an exit condition back to implementation slices.

## 12. Validation Plan

Since TASK_335 is documentation/process-only, validation should be document review rather than code tests.

Required checks:

- `tasks/TASK_335_PARALLEL_EXECUTION_MODEL_AND_BOARD_LANE_TEMPLATE.md` exists and is consistent with this plan.
- `AGENTS.md` still requires task files, plans, explicit approval, validation, and stop points.
- `docs/task_board.md` remains the source of truth.
- The new lane model does not allow unapproved implementation.
- The new lane model clearly forbids unsafe parallel edits to shared authority paths.
- The lane template includes owner, branch/worktree, dependency, conflict scope, May Touch, Must Not Touch, Locked Paths, validation gate, and merge gate.
- Developer, Planner, and Integrator task-board update boundaries are explicit.
- No product behavior or source code is changed.

Optional mechanical checks:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Select-String -Path AGENTS.md -Pattern 'Controlled Parallel Execution' -Encoding UTF8
Select-String -Path docs\task_board.md -Pattern 'Active Lanes' -Encoding UTF8
Test-Path docs\project_management\PARALLEL_EXECUTION_MODEL.md
Test-Path tasks\TASK_335_PARALLEL_EXECUTION_MODEL_AND_BOARD_LANE_TEMPLATE.md
```

## 13. Risks

### Risk: Governance expansion slows execution further

Mitigation:

- Keep TASK_335 documentation-only and bounded.
- Do not add new recurring meetings, large reports, or broad process ceremony.
- Require lane definitions to be compact and operational.
- Stop after TASK_335 and return to implementation, integration, validation, or a user-approved concrete follow-up.

### Risk: Parallel lanes cause merge conflicts

Mitigation:

- Require branch/worktree isolation.
- Declare conflict scope before approval.
- Declare `May Touch`, `Must Not Touch`, and `Locked Paths`.
- Serialize tasks touching the same Office gateway, authority path, database schema, task board global status, or locked path.

### Risk: AI uses lanes to bypass active-task control

Mitigation:

- `docs/task_board.md` remains the only source of truth.
- Only lanes marked `approved` may be implemented.
- Proposed/planned lanes remain non-executable.
- Each lane must still map to a formal TASK file.

### Risk: Reviewer role becomes performative

Mitigation:

- Reviewer must use the existing `TASK_REVIEW_CHECKLIST.md`.
- Review must identify scope, architecture, test, and regression evidence.
- Integrator may not merge a lane without review status.

## 14. Acceptance Criteria

TASK_335 is acceptable when:

- controlled parallel execution is documented as project-level parallelism, not executor-level multitasking
- the formal TASK_335 task file exists
- lane template is present and usable
- Planner, Developer, Reviewer, Integrator, and QA roles are defined
- parallel-safe and serialized task categories are explicit
- lane file boundaries are explicit through `May Touch`, `Must Not Touch`, and `Locked Paths`
- Developer/Planner/Integrator task-board update responsibilities are explicit
- frontend/backend contract-first splitting is documented
- existing ConnLab safeguards remain intact
- the governance freeze exception has concrete blocker evidence, impact, and exit condition
- no product implementation task is started as part of this plan

## 15. Recommended Stop Point

After this revised plan is reviewed, stop and wait for explicit user approval before editing `AGENTS.md`, `docs/task_board.md`, or adding the formal `PARALLEL_EXECUTION_MODEL.md` document.
