---
name: connlab-lane-orchestrator
description: Run ConnLab's active Personal Serial Workflow V2 for task intake, read-only planning, approved implementation, review, QA, integration, recovery, and closeout. Use whenever the User asks to start, continue, approve, inspect, recover, or close ConnLab repository work.
---

# ConnLab Personal Serial Orchestrator

Status: active version-2 runtime.

Use this skill when the User submits, approves, resumes, inspects or closes a ConnLab complex task.
Read `AGENTS.md`, `docs/task_board.md`, the active Task/Plan and relevant evidence first. The board's
version-2 control block and Git facts override conversation memory.

Detailed schemas, evidence topology, model routing, recovery, and integration rules live only in
`docs/project_management/SERIAL_COMPLEX_ROLE_CHAIN_PROTOCOL.md`. Read the relevant section before a
write or dispatch; do not duplicate or improvise that contract here.

## User contract

A normal complex task has only three User interactions:

1. requirement submission;
2. Planner-plan approval;
3. completed-result inspection and `关闭`.

Do not request routine approvals for host creation, Developer -> Reviewer -> QA -> Integrator, an approved
bounded fix, non-conflicting local integration, or retained closeout. Return to the User only for a
scope/behavior/authority change, a destructive action, or an unresolved blocker.

## Event loop

Perform one durable state transition at a time with `scripts/connlab_personal_task.py`, using the
fresh expected board SHA-256. Exact-stage and locally commit each authority transition before the
next write-capable action. Never use chat text as a substitute for board state.

```text
idle -> submit/classify; simple -> direct implementation -> human review
complex -> planning/approval -> Developer -> Reviewer -> QA -> Integrator -> human review
User 关闭 -> retained closeout -> idle
```

Planner runs before the host and cannot write. After approval, Developer, Reviewer, QA and Integrator
run sequentially in the same isolated task host. Spawn only the role required by the current durable
phase, record its native action and returned identity, wait for its exact callback, validate the
subject/evidence, then consume it. Reviewer or QA blocking findings route back to Developer without
new approval when the fix remains inside approved scope.

Primary owns execution-role evidence. Keep the task host clean at the exact subject and follow the
protocol's fixed transition/evidence order for every callback and bounded fix loop.

## Simple-fast

Within an already classified simple task, use `simple-fast` only when every detailed-protocol predicate
is true; it is not a task kind, state, role, or approval. Keep normal states and apply its bounded contract.

## Canonical entry

Use only `scripts/run_task.ps1` for User-facing Submit, Approve, and Close. Copy the exact payload and
decision contracts from the normative protocol. A schema error is terminal and zero-write; never guess
another schema or bypass the entry with direct request JSON.

## Supporting engineering skills

Supporting skills improve a role's method; they never create another route, broaden approved scope, or
override board authority.

- Developer uses `$tdd` for substantive behavior changes. Add `$diagnosing-bugs` only for hard,
  repeated, flaky, or unexplained failures—not routine implementation and not Windows hardware faults.
- Reviewer uses `$code-review` after a meaningful diff; QA does not repeat that review.
- Planner or Developer uses `$codebase-design` only for an approved structural refactor or module seam.
- Planner or Orchestrator uses `$grilling` only for material product ambiguity; ask at most three
  blocking questions and decide ordinary technical details autonomously.
- UI work loads `$impeccable` except for protocol-eligible `simple-fast`; UI QA uses `$playwright`
  only when observable browser behavior changed.

Choose and audit role models exactly as defined by the normative protocol.

## Validation ownership

Developer self-reviews and runs the complete approved matrix last on the final exact subject; any later
implementation or test change invalidates that result. Reviewer runs risk-targeted tests and uses
`$code-review` as its method, not a second review route. QA independently runs the complete matrix once
on the clean reviewed subject. Integrator verifies exact Git/evidence/integration facts, does not repeat
the matrix, and stops immediately on a deterministic blocker. Use known permission boundaries on the
first attempt and recover interrupted work mechanically from board, Git, worktree, and evidence.

## Recovery

Recover from `inspect` and its `active_snapshot` / `next_action`, reusing the board/Git/evidence host.
Build actions/refs with `connlab_serial_payload.py native-action` / `git-reference`; never copy hashes/JSON.
Use atomic `reenter-development` for an approved bounded fix and one `approve` for a scope amendment.
Fail closed on unproved identity; retry only after proving zero state change. Do not duplicate activation.

## Safety

WIP is one. Reuse a recorded host and never duplicate activation. Do not push, rebase, force-remove,
restore, reset, stash, discard, delete, archive, or retire automatically. Stop with a typed blocker on
unprovable identity/evidence, dirty or divergent state, conflict, scope expansion, destructive work,
or repeated failure. Integrate only after the protocol's subject/evidence/Git gate passes; remain at
`implemented_pending_human_review` until the User says `关闭`.
