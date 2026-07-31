# ConnLab Parallel Execution Model

Last Updated: 2026-07-31
Status: active referencing model
Scope: WIP=1 execution, explicit parallel exceptions, role boundaries, lane evidence, and merge gates

The normative token, queue, Quick Fix, preemption, reconciliation, and exception contract is
`docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`.

## 1. Purpose

ConnLab runs one implementation owner by default. A second owner is allowed only through the
explicit User-approved parallel exception defined by the normative policy. This model preserves:

- formal task files
- plan-before-implementation
- explicit user approval
- one task per executor/Agent
- task board as source of truth
- role-specific evidence
- review and integration gates

This model does not introduce product multi-user collaboration, permissions, LAN/server deployment, or runtime collaboration features.

Operational implementation is defined by:

- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `scripts/connlab_lane_worktree.ps1`
- `scripts/task_complete_commit.ps1`

## 2. Core Rule

```text
A single executor/Agent may work on only one task at a time.
The ConnLab project uses WIP=1 and one board execution token by default.
Multiple implementation owners require a recorded explicit User-approved parallel exception, exact independence proof, and maximum concurrency two.
Every implementation lane must use its own lane/* branch and sibling worktree.
The primary master worktree is reserved for planning and integration.
```

Proposed or planned lanes are not executable. Approval alone does not acquire the execution token:
the board must record ownership before implementation write, or record a FIFO queue position.

## 3. Roles

### Planner

Planner owns task decomposition and lane readiness.

Allowed:

- run Planner Discovery Gate before task/lane proposal or approval
- update planned lane definitions in `docs/task_board.md`
- split work into lane-sized tasks
- define dependencies, conflict scope, `May Touch`, `Must Not Touch`, `Locked Paths`, evidence file, validation gate, and merge gate
- mark lanes as proposed/planned/approved after explicit user approval

Forbidden:

- implement product code
- convert a short or ambiguous user request directly into an approved lane without Discovery Gate
- silently convert a proposed task into an executable lane
- bypass required task files or explicit approval

Planner readiness is governed by `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`. A lane may be `approved` only when the Planner Definition of Ready is satisfied. If user goal, evidence, dependencies, ownership, validation, or non-goals are unclear, Planner must keep the lane `proposed`/`planned` and ask for clarification instead of routing to Developer.

### Developer

Developer owns one approved implementation lane.

Allowed:

- edit only files allowed by the lane `May Touch`
- run lane validation
- write developer evidence under `docs/lane_evidence/`
- prepare completion evidence for Reviewer/Integrator

Forbidden:

- edit `Must Not Touch` or another lane's `Locked Paths`
- update global task board state unless the lane explicitly allows lane-local evidence edits
- merge branches or mark lanes complete globally
- perform Reviewer, QA, Planner, or Integrator duties silently

### Reviewer

Reviewer owns independent review of one lane or integration package.

Allowed:

- inspect diffs and evidence
- use `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- write review evidence and findings
- classify findings as blocking or non-blocking

Forbidden:

- silently fix code while acting as Reviewer
- merge code
- update global task board completion state

### QA / Smoke Owner

QA owns reproducible validation evidence.

Allowed:

- run manual or real-environment smoke checks
- record environment, inputs, commands, observed behavior, and failures
- write QA evidence under `docs/lane_evidence/`

Forbidden:

- modify product code
- hide failures by changing implementation
- mark a lane merged or globally complete

### Integrator

Integrator owns merge readiness, conflict resolution, integration validation, and authoritative board status.

Allowed:

- merge approved lanes after required review/QA gates
- resolve conflicts within approved integration scope
- run affected integration validation
- update global `docs/task_board.md` lane status, completion notes, validation summary, and next recommendation

Forbidden:

- bypass Reviewer/QA gates when they are required
- merge lanes with unresolved blocking findings
- expand product scope during integration

## 4. Lane Schema

Every active lane must declare:

| Field | Meaning |
|---|---|
| Lane | Stable lane id, e.g. `ltr-office` |
| Task | Formal task id in `tasks/` |
| Type | backend/frontend/test/docs/review/qa/integration/etc. |
| Status | proposed/planned/approved/in_progress/review/integration/blocked/complete/cancelled |
| Branch / Worktree | Concrete `lane/*` branch and existing sibling worktree; `TBD` is not approval-ready |
| Owner Role | Planner/Developer/Reviewer/QA/Integrator |
| Depends On | Required predecessor tasks or lanes |
| Conflict Scope | Business/architecture boundary that can conflict |
| May Touch | Allowed files, directories, or modules |
| Must Not Touch | Forbidden files, directories, modules, workflows, or authority paths |
| Locked Paths | Files/directories reserved exclusively while active |
| Evidence File | Role/lane evidence path under `docs/lane_evidence/` |
| Validation Gate | Required checks before review or integration |
| Merge Gate | Required approval and final integration evidence |

## 5. Evidence Files

Each lane must maintain evidence under `docs/lane_evidence/`.

Recommended naming:

```text
docs/lane_evidence/<TASK_ID>_<lane_id>_<role>.md
```

Evidence must record:

- role
- lane
- task
- status
- allowed scope
- commands or checks run
- outputs/results
- changed files when applicable
- findings or failures
- handoff notes
- stop point

The evidence file is the durable memory for long Codex conversations. Chat history may be compressed; evidence files must preserve decisions and validation.

## 6. Role Mismatch Protocol

If the user's request does not match the active role:

1. Stop before editing files, running merge actions, or changing global board state.
2. State the current role and allowed responsibilities.
3. State why the requested action belongs to another role.
4. Suggest the correct role/lane.
5. Offer only safe handoff output, such as evidence, findings, smoke notes, or a transfer note.

A role must not silently perform another role's responsibility.

## 7. Explicit Parallel Exception Rules

A second implementation owner may be approved only if every condition below and the normative
policy's exception contract are satisfied:

1. It has a formal task file.
2. Non-trivial implementation has a plan file.
3. Dependencies are declared and satisfied.
4. Conflict scope is declared.
5. `May Touch`, `Must Not Touch`, and `Locked Paths` are declared.
6. An evidence file is declared.
7. A concrete branch/worktree has been created from the recorded clean base commit and verified clean.
8. Validation and merge gates are declared.
9. Planner marks it approved after explicit user approval.
10. No active lane owns the same shared file or authority path.
11. The board records exact scope proof, both owners, end condition, and explicit User approval evidence.
12. No more than two implementation owners exist.

Potentially exception-eligible after proof and User approval:

- frontend-only UI polish without API changes
- backend read-only service with stable DTOs
- test-only regression coverage
- docs or smoke checklist work
- independent parser hardening with isolated fixtures
- QA validation against a completed branch
- Reviewer review of a completed lane

Usually serialized:

- same Word/Excel Office gateway path
- Project Folder Required Forms orchestration
- SQLite schema or repository contracts
- Matrix authority, Fee draft, Basic Information authority, or LTR authority
- global `docs/task_board.md` status updates
- frontend/backend work without an approved API contract

## 8. Contract-First Split Rule

For frontend/backend parallel work, create a contract task first:

```text
TASK_XXX_CONTRACT
  defines DTOs, endpoint shape, error semantics, state transitions, sample payloads, and acceptance examples

TASK_XXXA_BACKEND
  implements backend against the approved contract

TASK_XXXB_FRONTEND
  implements UI/client behavior using the approved contract and mocks if needed

TASK_XXXC_INTEGRATION
  merges backend + frontend and runs end-to-end validation
```

Contract tasks must remain short and implementation-facing.

## 9. Thread Usage

A Codex thread can act as a task-scoped role-specific agent when the first prompt declares:

- role
- lane
- task
- allowed docs/files
- evidence file
- allowed responsibilities
- forbidden responsibilities
- stop point

Threads do not share chat memory. They coordinate through:

- git branches/worktrees
- `docs/task_board.md`
- lane evidence files
- code diffs
- validation output

Creating a new role thread does not create Git isolation. The orchestrator must create the lane worktree before routing implementation and must include the exact branch/path in every role prompt.

Normal product TASKs reuse the permanent roles in `ROLE_THREAD_REGISTRY.md`.
`ACTIVE_TASK_THREAD_BUNDLE.md` is a frozen V1-Lite snapshot and is not execution authority.

## 10. Stop Rules

Stop immediately when:

- the lane is not approved
- the requested action belongs to another role
- the request touches `Must Not Touch` or another lane's `Locked Paths`
- validation fails and requires Developer repair
- merge gates are not satisfied
- the user requests product scope outside the active lane
## 11. Automated Handoff Orchestration

ConnLab may use a dedicated orchestrator skill to reduce manual role-to-role prompting:

- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

The orchestrator is a router, not a replacement for role authority. It may inspect the board/evidence and send the next valid role a standard prompt, but it must not approve planned lanes, implement product code, override Reviewer/QA findings, or merge before the merge gate is satisfied.

Typical automated chain:

```text
Planner approved lane
  -> Orchestrator sends Developer start prompt
  -> Developer writes ready_for_review evidence
  -> Orchestrator sends Reviewer gate prompt
  -> Reviewer pass/fail evidence
  -> blocking findings return to Developer fix pass
  -> passing gate goes to QA or Integrator
  -> Integrator merges only after merge gate is satisfied
```

If thread tools are unavailable, the orchestrator must print the exact prompt for the user to paste into the target Chinese role thread.

## 12. Repository Hygiene Gates

Parallel execution is accepted only when all of the following are enforced:

1. New regression coverage uses bounded focused test modules by default.
2. Developer hands off a clean local commit on the lane branch, not an ambient dirty diff.
3. Reviewer compares the recorded base commit to lane HEAD.
4. QA validates the reviewed commit from a clean worktree or exact archive.
5. Integrator stages only the reviewed package and updates the board from the primary worktree.
6. Integrator classifies every excluded path as retained, duplicate, stale, format-only, or conflict.
7. A retained residual receives a named owner immediately; duplicate/stale/format-only residuals enter one exact discard list.
8. Task, plan, and evidence documents are committed with their owning package.
9. Lane completion requires clean lane status/index and a clean primary worktree, or an explicit residual ledger with owner and expiry.
10. Remote push and destructive discard remain separate explicit authorization gates.
11. Permanent role conversations remain available after closeout; task state closes through
    board/evidence/worktree/residual records, not role-thread archival.

For a multi-lane series, one user-approved Goal may authorize normal role handoffs, bounded fix passes, evidence updates, local commits, and worktree lifecycle operations. The orchestrator should not request a fresh human approval for each small hunk unless scope, product behavior, destructive cleanup, or remote state changes.
