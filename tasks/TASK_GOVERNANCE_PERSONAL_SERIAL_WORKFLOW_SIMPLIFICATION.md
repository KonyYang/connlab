# TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION

Status: `draft_revision_3_for_user_review`
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
- the complete task changes one to three total repository files, including implementation, tests,
  documentation, configuration, and the mandatory `docs/task_board.md` state update;
- no API contract, database, schema, migration, persistence, authority, public-drive workflow, or
  business-rule semantic change exists;
- no destructive action, push, publication, or external-state mutation is required;
- a targeted automated check, compile check, or bounded manual smoke can be named.

Anything outside this boundary requires a short implementation plan and explicit User approval.

## Required Personal Lifecycle

```text
idle
  -> running(simple | planned)
  -> running(blocked) when implementation or validation cannot complete
  -> implemented_pending_human_review
  -> closed by explicit User command
  -> idle; FIFO head becomes eligible
```

- `running` and `implemented_pending_human_review` both occupy the sole active slot.
- New requests received in either state are queued; they do not start and do not create Git
  branches/worktrees.
- One atomic board helper is the only state writer. Natural-language handling and PowerShell entry
  points must call that helper rather than patching the board independently.
- Approval is followed first by a local activation commit that records this task as `running`;
  implementation writes begin only after that commit.
- `关闭` is allowed only for a clean, successfully validated
  `implemented_pending_human_review` task. It makes the oldest queued item eligible but does not
  silently begin implementation. A later explicit execute/continue command must call
  `activate-next` for the exact FIFO head; no queued item may skip ahead.
- Failure keeps the task active as `running` with a blocker. It cannot release the slot or enter
  pending review. Continue, retain-and-commit, or cancel-and-resolve requires explicit User
  direction; no helper may restore, discard, or clean modifications.

## Required Simple-Task Record

Before a simple task can enter `running`, its board record must contain:

- exact `may_touch` paths and `expected_file_count` between one and three, counting tests and the
  mandatory board path;
- `classification_reason` explaining why the root cause and expected behavior are clear;
- `targeted_validation` commands or bounded manual-smoke instructions;
- explicit false checks for API contract, database, schema/migration, persistence, authority,
  public-drive workflow, business-rule semantics, destructive action, and external mutation.

The state helper validates that this declaration is complete and that observed paths stay within
it. It does not pretend to infer business semantics from a Task ID.

The helper only atomically edits `docs/task_board.md`; it never stages or commits. The current
conversation owns exact-path staging and local commits. A planned task's `approve` transition must
be committed and primary verified clean before implementation begins.

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
