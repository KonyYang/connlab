# ConnLab Personal Serial Workflow Simplification Plan

Status: `DRAFT_REVISION_2_FOR_USER_REVIEW`
Task: `TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION`
Date: 2026-08-05
Original planning base: `ae33faa38894c26245397226d8e4357512c77b91`
Revision-1 commit: `34379138df1fcd70ee305076662a502fb30389ff`

## 1. Outcome

ConnLab will use one personal active task and one durable FIFO queue. The current conversation is
the executor. It does not dispatch Planner, Developer, Reviewer, QA, Integrator, Quick Fixer, or
any other task conversation. Implementation occurs directly in the primary worktree.

A qualifying simple task skips plan creation and plan approval. Every implemented task still runs
bounded validation, creates a local commit, and remains active as
`implemented_pending_human_review` until the User says `关闭`.

This revision adds the missing atomic board writer, activation-before-implementation commit,
explicit simple-task classification record, blocked/dirty-worktree behavior, immutable history
checks, and an exact implementation allowlist.

Review disposition:

| Finding | Revision-2 resolution |
|---|---|
| no board write entry | one CAS/lock/atomic-replace helper is the sole post-migration writer |
| WIP gap during implementation | activation commit precedes every implementation edit |
| unprovable/expanded simple scope | structured classification; 1–3 total paths including tests and board |
| missing failure semantics | blocked task retains active slot; dirty close/cancel is forbidden |
| history compatibility | active-context helper/archive/index are protected and hash-checked |
| expandable test scope | commands may change; file allowlist may not change without new approval |

## 2. Discovery And Frozen User Decisions

Confirmed by the User:

- only one person develops ConnLab, so implementation concurrency is unnecessary;
- exactly one task may be active; every later task waits in FIFO order;
- a simple task has a clear root cause, is limited to one to three files, and changes no API,
  database, persistence, or business-rule semantics;
- simple tasks require neither a prior plan nor plan approval;
- completed implementation becomes `implemented_pending_human_review`; only `关闭` closes it;
- work happens directly in primary without lane branches or sibling worktrees;
- former roles are not dispatched and Task-A remains cancelled and retained.

Conservative clarification adopted by this revision:

- the one-to-three-file limit includes every changed repository file for the simple task,
  including tests and the mandatory `docs/task_board.md` state update;
- exceeding that total is not a simple task and requires the planned flow;
- closing makes the FIFO head eligible but never starts it automatically.

Repository evidence:

- planning began from clean `master@ae33faa38894c26245397226d8e4357512c77b91`;
- the board was valid `cancelled` state with `active=null` and no token owner;
- current WIP policy already says WIP=1/FIFO but retains parallel, preemption, reconciliation,
  worktrees, role gates, handoffs, and Integrator closeout;
- `scripts/run_task.ps1` promises execution through Integrator and has no board-state writer;
- `scripts/connlab_execution_gate.ps1` is read-only and validates the obsolete state model.

No implementation is authorized by this revision. The approved planning commit will be the
required clean primary HEAD before activation.

## 3. Single Board Writer

Add one bounded helper:

`scripts/connlab_personal_task.py`

After the migration activation commit, it is the only supported writer of the marker-delimited
control block in `docs/task_board.md`. Agents and PowerShell entry points must call it; they must
not independently patch control JSON.

Because the helper does not exist before this task is implemented, the migration has one explicit
bootstrap exception: immediately after plan approval, the current conversation applies one exact
`apply_patch` transition from the verified legacy cancelled block to the personal
`running/implementation` block and commits it before touching any other implementation path. The
patch is bound to the approved board bytes/HEAD, preserves retained-history pointers, and is
validated by independent JSON/hash checks. No later manual control-block patch is allowed.

### 3.1 Atomicity

Every write command must:

1. resolve and verify the primary repository;
2. acquire an exclusive temporary lock under `.git` using create-new semantics;
3. parse exactly one control block and validate its complete schema;
4. compare the current board SHA-256 with the caller's `expected_board_sha256`;
5. validate the requested transition and current Git facts;
6. render the complete new board in memory;
7. write, flush, and `fsync` a sibling temporary file, then atomically replace the board;
8. re-read and validate the resulting bytes;
9. release the lock in `finally`.

A pre-existing lock, hash mismatch, malformed board, failed replacement, or failed post-write
validation returns stable `BLOCKED_*` output without attempting a second transition. A stale lock
is reported for manual inspection and is never deleted automatically.

### 3.2 Commands

The helper exposes only:

- `inspect`: zero-write schema, board hash, active, queue, and Git-status summary;
- `submit`: atomically activates when idle or idempotently appends to FIFO when occupied;
- `approve`: moves a planned task from planning to implementation after an explicit approval ref;
- `mark-review`: records passed validation and enters `implemented_pending_human_review`;
- `block`: keeps `running`, records reason, failed validation, and observed dirty paths;
- `resume`: clears a blocker only after explicit User direction while retaining the same task;
- `cancel`: releases a task only after explicit User direction and a clean worktree;
- `close`: closes only a clean, validated `implemented_pending_human_review` task.

No command stages, commits, restores, discards, cleans, pushes, starts another task, creates a
branch/worktree, or dispatches a conversation.

## 4. Minimal Board Schema

Keep one marker-delimited JSON object with:

- `schema: connlab.personal-serial-control` and `version: 1`;
- `mode: personal_serial` and `wip_limit: 1`;
- global `state: idle | running | implemented_pending_human_review`;
- nullable `active`;
- ordered `queue` and monotonic `next_enqueue_sequence`;
- bounded `last_closed` summary;
- short `retained_history` entries for every currently retained residual.

An active record contains:

- `task_id`, `summary`, and `kind: simple | planned`;
- `phase: planning | implementation | blocked | human_review`;
- exact `may_touch` and `expected_file_count`;
- `classification_reason` and `targeted_validation`;
- named forbidden-category checks;
- `approval_ref` for planned implementation;
- `activation_parent_sha`, timestamps, nullable `blocker`, and nullable validation result.

For `kind=simple`, `expected_file_count` must be 1–3, equal `may_touch` length, include
`docs/task_board.md`, and every forbidden check must be explicitly false:

- API contract;
- database;
- schema or migration;
- persistence;
- authority;
- public-drive workflow;
- business-rule semantics;
- destructive action;
- remote/publication/service/external mutation.

The helper validates complete declarations and observed paths. It does not claim to infer semantic
safety from a Task ID; the current conversation supplies the classification from repository
evidence and stops on ambiguity.

Queue records contain task ID, summary, requested kind, enqueue sequence, timestamp, and the same
classification fields when the request is declared simple. Repeated submission of the same active
or queued ID is idempotent. FIFO order cannot be rewritten by ordinary task commands.

## 5. State And Commit Protocol

### 5.1 New simple task

1. Read-only inspect and classification.
2. `submit` writes `running/implementation` or queues the task atomically.
3. If activated, exact-stage the board and create an activation commit before any implementation
   file is edited.
4. Implement only declared paths and run targeted validation.
5. On pass, `mark-review` writes pending-human-review state; exact-stage payload plus board and
   create the implementation commit.
6. Stop for human review.

### 5.2 New planned task

Under the installed personal workflow, `submit` first records `running/planning`, so planning also
occupies the single active slot. The short plan is committed and reviewed. `approve` records the
explicit approval before implementation. Implementation then follows the same validation,
pending-review, and local-commit path.

This governance migration is a one-time bootstrap exception because its plan predates the new
helper. After User approval it must create two primary commits:

1. activation commit: migrate the board and record this task `running/implementation` before any
   rule, helper, script, or test implementation edit;
2. implementation commit: include approved implementation paths, passed validation summary, and
   board state `implemented_pending_human_review`.

The activation commit is not a role dispatch or implementation acceptance.

### 5.3 Failure, dirty worktree, and cancellation

- A validation failure, unexpected path, expanded scope, or partial implementation remains
  `running` and uses `block` to record the blocker and observed dirty paths.
- `mark-review`, `close`, and promotion of a queued task are forbidden while blocked, dirty,
  validation-failed, or out of scope.
- `block` may exact-stage and commit only the board while task files remain dirty, so all other
  conversations fail closed without hiding partial work.
- Only explicit User direction may choose: continue; preserve an exact checkpoint commit and keep
  working; or cancel after separately resolving the modifications.
- `resume` never alters files. `cancel` requires a clean worktree and records the User-approved
  disposition; it never restores, discards, stashes, or cleans.
- `关闭` requires pending-human-review state, passed validation, and clean primary. It writes a
  closeout board change and requires a separate exact local board commit. It releases the slot but
  does not auto-start the queue head.

## 6. Entry Points

- `scripts/run_task.ps1` becomes a thin local adapter to `connlab_personal_task.py submit`. It
  accepts the structured task record, returns activated/queued/blocked JSON, and invokes no Codex
  runtime, old role, V2 path, worktree, or external process beyond the helper.
- `scripts/connlab_execution_gate.ps1` becomes a thin read-only adapter for inspect,
  implementation-allowed, and close-allowed decisions from the same helper/schema.
- Direct natural-language execution in the current conversation calls the helper itself.
- Old lane, transition, handoff, role-registry, parallel, and Controlled Lane V2 materials remain
  frozen historical references and are not daily entry points.

## 7. Exact Implementation Allowlist

Only these files may be added or modified after approval.

Core authority and policy:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`

Frozen legacy labeling/references:

- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/connlab-planner/SKILL.md`

Entry points:

- `scripts/connlab_personal_task.py` (new)
- `scripts/run_task.ps1`
- `scripts/connlab_execution_gate.ps1`

Governance tests:

- `tests/unit/test_connlab_personal_serial_workflow.py` (new)
- `tests/unit/test_connlab_execution_gate_script.py`
- `tests/integration/test_connlab_execution_gate_recovery.py`
- `tests/unit/test_execution_wip_and_quick_fix_governance.py`
- `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
- `tests/unit/test_connlab_lane_worktree_script.py`
- `tests/unit/test_connlab_active_context_governance.py`

Task-owned planning/status:

- `tasks/TASK_GOVERNANCE_PERSONAL_SERIAL_WORKFLOW_SIMPLIFICATION.md`
- `docs/task_governance_personal_serial_workflow_simplification_plan.md`

Test commands may be adjusted to obtain stronger evidence. Adding or modifying any unlisted file
path requires stopping and obtaining new explicit User approval.

## 8. Must Not Touch

- all product/backend/frontend/API/domain/database/schema/migration/Office/LTR/Matrix/Fee/report/
  release/runtime feature code and tests;
- `scripts/connlab_active_context.py` and its existing archive/rollback logic;
- `docs/archive/task_board_history/**`, including generation-1 and `index.v1.jsonl`;
- every Task-A task/plan/evidence/transition/attestation file, retained lane/worktree, branch, and
  commit;
- the external `connlab-governance-migration` repository;
- Controlled Lane V2 helper, registry, heartbeat, pilot/corrective packages, skill, and tests;
- existing transition/handoff helpers and their tests;
- all other tasks, plans, evidence, retained worktrees, artifacts, real data, remotes, and services;
- deletion, restoration, merge, adoption, retirement, reconciliation, or cleanup of legacy state.

## 9. Implementation Sequence After Approval

1. Recheck clean primary at the approved revision and snapshot protected hashes/worktree facts.
2. Apply the one-time exact bootstrap board transition, update only this task/plan approval status,
   validate it, exact-stage those three paths, and create the activation commit before any helper,
   rule, entry-point, or test implementation edit.
3. Add the personal schema/helper failing tests.
4. Implement the complete atomic helper and its state transitions.
5. Simplify the two PowerShell entry points.
6. Replace daily multi-role rules with the personal policy; mark old routing documents/skills
   frozen without deleting them.
7. Update only allowlisted governance tests for the new contract.
8. Run the exact behavioral, PowerShell, history, protected-state, and diff checks.
9. On success, call `mark-review`, exact-stage the allowlist, and create the implementation commit.
10. Verify clean primary and stop at `implemented_pending_human_review`; no push and no queued start.

If any step needs an unlisted path, destructive action, Task-A mutation, archive/index write, or
scope/semantic decision, stop for User approval.

## 10. Validation And Acceptance

Behavioral coverage must prove:

- idle submit activates exactly one task; occupied submit idempotently queues in FIFO order;
- activation board state is committed before implementation writes;
- pending human review and blocked/dirty states continue to occupy the slot;
- simple records require 1–3 total paths including tests and board, explicit classification,
  targeted validation, and all forbidden checks false;
- planned implementation requires an explicit approval ref;
- failed validation cannot mark review, close, cancel dirty work, or release the slot;
- close requires explicit User direction, passed validation, clean primary, and does not auto-start;
- no path dispatches old roles or creates a branch/worktree;
- malformed schema, hash race, duplicate queue ID/sequence, and lock conflict fail closed;
- atomic-write failure preserves the prior board bytes.

History compatibility must prove without modifying history files:

- generation-1 archive remains exactly 798128 bytes, SHA-256
  `3e57b913098e565de3fee8f4a0ffdff597e3d7fdfec5232fe63027298f1a2507`, Git blob
  `972b1c2386145114cb3daa35037913d709bb5180`;
- `index.v1.jsonl` remains exactly 6787 bytes, SHA-256
  `cc732a742f60914e8c922d9f91f05d93fcd3bf4ec0f3483b1248a9e64c094aae`, Git blob
  `77f43609e1b8ecde0e058c5e0d24d4e554a2f895`;
- no archive/index generation is rebuilt, appended, or rewritten;
- generation-1 direct `prove-rollback` returning `BLOCKED_ROLLBACK_CHAIN` after the later legitimate
  cancelled-board update is expected protection, not a failure;
- active-context `inspect` and the unchanged mixed-EOL/archive regression suite still pass.

Planned commands include:

```powershell
py -m pytest tests\unit\test_connlab_personal_serial_workflow.py -q
py -m pytest tests\unit\test_connlab_execution_gate_script.py -q
py -m pytest tests\integration\test_connlab_execution_gate_recovery.py -q
py -m pytest tests\unit\test_execution_wip_and_quick_fix_governance.py -q
py -m pytest tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
py -m pytest tests\unit\test_connlab_lane_worktree_script.py -q
py -m pytest tests\unit\test_connlab_active_context_governance.py -q
py -m pytest tests\unit\test_connlab_active_context.py -q
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\connlab_execution_gate.ps1' -Raw -Encoding UTF8))"
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\run_task.ps1' -Raw -Encoding UTF8))"
py scripts\connlab_active_context.py inspect --repo-root . --json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\connlab_execution_gate.ps1 -Intent Inspect -Json
git diff --check
git status --short
```

Before/after SHA-256, Git blob, branch/HEAD/status, Task-A retained-lane HEAD/status, external-repo
HEAD/status, and archive/index facts must match their protected baseline except for the approved
primary commits.

## 11. Rollback

The activation commit is the migration boundary. Before any later task uses the personal schema,
rollback requires explicit User authorization and exact reverts of the implementation commit and
activation commit in reverse order. Once later tasks depend on the schema, rollback becomes a new
explicit migration decision.

No reset, restore, archive rewrite, Task-A mutation, branch/worktree cleanup, or remote operation is
part of rollback.

## 12. Stop Point

Implementation is complete only when:

- the activation and implementation commits both exist on primary in order;
- only allowlisted paths changed;
- all required validation and history/protected-state checks pass;
- primary is clean at the implementation commit;
- board records this task as `implemented_pending_human_review` with no blocker;
- no old role/worktree/V2 dispatch occurred, no push occurred, and no queue item started.

Then stop for User review. Only `关闭` may create the later closeout board commit and release the
slot. This plan remains non-executable until the User explicitly approves this revision.
