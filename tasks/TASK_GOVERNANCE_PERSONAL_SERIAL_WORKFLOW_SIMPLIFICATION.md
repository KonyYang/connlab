# TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION

Status: `draft_for_user_review`
Type: governance workflow simplification
Planning base: `ae33faa38894c26245397226d8e4357512c77b91`
Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
Current active task: none

## Why This Planning Task Is Allowed

The board is valid `cancelled` state with no active task and no execution-token owner. The User has
explicitly requested a replacement personal workflow, authorized preparation of this reviewable
plan in the primary worktree, and prohibited dispatch to the former permanent roles. This planning
package does not activate implementation.

## Goal

Replace ConnLab's multi-role/lane execution model with a personal serial workflow optimized for one
developer:

1. Exactly one task may be active.
2. Every later task enters a durable FIFO queue.
3. A qualifying simple task is implemented directly without a prior plan or plan approval.
4. Implementation happens in the primary worktree without a lane branch or sibling worktree.
5. Completion means a targeted validation and local commit followed by
   `implemented_pending_human_review`.
6. Only the User command `关闭` closes the task and releases the active slot.

## Confirmed Simple-Task Boundary

A task is simple only when all conditions are true:

- root cause and expected behavior are clear;
- implementation changes are limited to one to three files, plus bounded tests when needed;
- no API contract, database, schema, migration, persistence, authority, public-drive workflow, or
  business-rule semantic change exists;
- no destructive action, push, publication, or external-state mutation is required;
- a targeted automated check, compile check, or bounded manual smoke can be named.

Anything outside this boundary requires a short implementation plan and explicit User approval.

## Required Personal Lifecycle

```text
idle
  -> running(simple | planned)
  -> implemented_pending_human_review
  -> closed by explicit User command
  -> idle; FIFO head becomes eligible
```

- `running` and `implemented_pending_human_review` both occupy the sole active slot.
- New requests received in either state are queued; they do not start and do not create Git
  branches/worktrees.
- `关闭` closes only the current task. It makes the oldest queued item eligible but does not
  silently begin implementation.
- A failed or scope-expanded simple task stops for User direction or conversion to a planned task.

## Non-Goals

- No product/backend/frontend/API/database/Office behavior change.
- No parallel execution, priority exception, preemption, reconciliation, resume, or role handoff.
- No Planner/Developer/Reviewer/QA/Integrator/Quick Fixer conversation dispatch.
- No lane branch or sibling worktree creation, adoption, merge, retirement, or cleanup.
- No Task-A restoration, adoption, reconciliation, merge, deletion, or evidence rewrite.
- No remote push, publication, service restart, destructive cleanup, or external governance work.

## Planning And Approval State

The implementation plan is
`docs/task_governance_personal_serial_workflow_simplification_plan.md`.

Implementation is forbidden until the User explicitly approves that plan. Approval authorizes
direct implementation in the primary worktree only within its exact allowlist; it does not
authorize push, destructive cleanup, Task-A mutation, or automatic execution of a queued task.
