# ConnLab Parallel Execution Model

Last Updated: 2026-06-25
Status: active governance policy after TASK_335
Scope: controlled project-level parallel execution, role boundaries, lane evidence, and merge gates

## 1. Purpose

ConnLab allows controlled project-level parallel execution when `docs/task_board.md` defines approved active lanes. This model is intended to improve throughput without weakening existing ConnLab safeguards:

- formal task files
- plan-before-implementation
- explicit user approval
- one task per executor/Agent
- task board as source of truth
- role-specific evidence
- review and integration gates

This model does not introduce product multi-user collaboration, permissions, LAN/server deployment, or runtime collaboration features.

## 2. Core Rule

```text
A single executor/Agent may work on only one task at a time.
The ConnLab project may have multiple active lanes only when docs/task_board.md marks them as approved and parallel-safe.
```

Proposed or planned lanes are not executable. Only `approved` lanes may be implemented.

## 3. Roles

### Planner

Planner owns task decomposition and lane readiness.

Allowed:

- update planned lane definitions in `docs/task_board.md`
- split work into lane-sized tasks
- define dependencies, conflict scope, `May Touch`, `Must Not Touch`, `Locked Paths`, evidence file, validation gate, and merge gate
- mark lanes as proposed/planned/approved after explicit user approval

Forbidden:

- implement product code
- silently convert a proposed task into an executable lane
- bypass required task files or explicit approval

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
| Branch / Worktree | Required isolation target |
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

## 7. Parallel-Safe Rules

A task may be approved as a parallel lane only if:

1. It has a formal task file.
2. Non-trivial implementation has a plan file.
3. Dependencies are declared and satisfied.
4. Conflict scope is declared.
5. `May Touch`, `Must Not Touch`, and `Locked Paths` are declared.
6. An evidence file is declared.
7. Branch/worktree isolation is declared.
8. Validation and merge gates are declared.
9. Planner marks it approved after explicit user approval.

Usually parallel-safe:

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

A Codex thread can act as a role-specific agent when the first prompt declares:

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

## 10. Stop Rules

Stop immediately when:

- the lane is not approved
- the requested action belongs to another role
- the request touches `Must Not Touch` or another lane's `Locked Paths`
- validation fails and requires Developer repair
- merge gates are not satisfied
- the user requests product scope outside the active lane
