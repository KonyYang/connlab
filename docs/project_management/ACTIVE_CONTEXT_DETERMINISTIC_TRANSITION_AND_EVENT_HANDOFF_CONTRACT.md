# Active Context, Deterministic Transition, And Event Handoff Contract

Status: normative for classic permanent-role execution. `docs/task_board.md` execution-control JSON
remains the sole machine authority; the human Current Active Task line is its deterministic
projection, never a second state store.

## 1. Authority And Safety

- Resolve the main `master` worktree before reading authority. A lane board copy cannot authorize
  transitions, dispatch, maintenance, or resume.
- All planning commands are zero-write. Missing, ambiguous, stale, dirty, conflicting, or
  unprovable facts fail closed with stable `BLOCKED_*` reason codes.
- There is no force, ignore, assume, callback-only, or chat-memory override.
- Preserve WIP=1, token ownership, queue, residuals, pause, Quick Fix, parallel exception, branch,
  worktree, base, locks, scope, and required-gate metadata through routine transitions.

## 2. Routine State Machine

Exactly four events are mechanical:

| Event | Required authority | Evidence status | Durable result |
| --- | --- | --- | --- |
| `DEVELOPER_READY` | `implementation_running/Developer` | `ready_for_review` | `gate_running/Reviewer` |
| `REVIEWER_BLOCKED` | `gate_running/Reviewer` | `reviewer_blocked` | `implementation_running/Developer` bounded fix |
| `REVIEWER_PASS` | `gate_running/Reviewer` | `reviewer_pass` | `gate_running/QA`, or Integrator only when immutable `required_gates` omits QA |
| `QA_PASS` | `gate_running/QA` | `qa_pass` | `gate_running/Integrator` |

Before apply, `scripts/connlab_execution_transition.py` verifies the expected primary and lane
HEAD, task/lane/token/state/role, clean worktree and index, base ancestry, evidence
`path@commit#sha256`, evidence callback facts, changed paths against locks, queue/pause/Quick
Fix/parallel invariants, required gates, unique markers, and summary agreement. Apply changes only
`docs/task_board.md`. Same facts return `ALREADY_APPLIED`; a divergent duplicate returns
`BLOCKED_DUPLICATE_CONFLICT`.

## 3. Board Maintenance And Rollback

Maintenance is required above any threshold: 400 physical lines, 65536 UTF-8 bytes, or 24
terminal-detail records. The first generation archives the exact board bytes. Later generations
archive only the oldest formally terminal detail necessary to restore every budget. Active,
queued, paused, Quick Fix, parallel, residual, current/proposed task, and direct evidence facts
remain active.

Archives use
`docs/archive/task_board_history/generation-<six-digits>-<40-char-source-commit>.md`; the canonical,
append-only chain is `docs/archive/task_board_history/index.v1.jsonl`. Every record binds source
commit/blob/hash/bytes/record count, archive path/hash/count, compact board hash/count, previous
index hash, and rollback hash. Corrupt/non-contiguous indexes, path escape, conflicting archives,
or hash/count mismatch block writes. The board is replaced last; any partial failure restores
board/index bytes and removes only the exact uncommitted archive created by that attempt.

Production apply-maintenance is Integrator-only: clean `master`, `gate_running/Integrator`, the
closing task as sole token owner, accepted helper ancestry, all required gates, exact HEAD/hash,
empty queue, and null pause/Quick Fix/parallel facts. Other roles may inspect, plan, and prove
rollback only. Every Integrator closeout runs plan-maintenance before token release.

## 4. Reference-Only Handoff

References are `path@commit#sha256`. The minimal safe role read set is the board execution JSON and
generated summary, current task, approved plan, current-role evidence, and declared direct
dependencies. Invalid references or any unsafe/unprovable omission return `FULL_READ_REQUIRED`.
Unrelated immutable archive generations alone do not force a full read.

A callback is exactly seven ordered, non-empty lines and at most 1024 UTF-8 bytes:

```text
TASK_ID: ...
ROLE: ...
STATUS: ...
EVIDENCE: ...
COMMIT: <40-char SHA>
NEXT: ...
BLOCKER: ...
```

The callback is a wake-up signal, not authority. Per Orchestrator turn: validate durable facts,
perform at most one transition and one dispatch, then stop. Do not wait after dispatch. Routine
events launch zero Planner conversations. Planner is reserved for Discovery, scope/authority/API/
schema change, unclassifiable blockers, destructive decisions, and merge/evidence conflicts.

## 5. Budgets And Cadence

- Orchestrator core skill <=16384 bytes; Planner core skill <=8192 bytes.
- Active orchestration protocol <=12288 bytes.
- Role dispatch template <=2048 bytes; complete capsule <=4096 bytes.
- Each role minimal-read capsule <=4096 bytes; callback <=1024 bytes.
- Commentary is limited to role start, role end, blocker, material direction change, or heartbeat
  after at least 60 seconds. Suppress unchanged waits.
- Controlled pilot callback-to-legal-dispatch latency is <=90 seconds.

## 6. CLI

```text
py scripts/connlab_execution_transition.py inspect|plan|apply ... --json
py scripts/connlab_active_context.py inspect|plan-maintenance|apply-maintenance|prove-rollback ... --json
py scripts/connlab_handoff_contract.py validate-dispatch|resolve-read-set|validate-callback|validate-cadence ... --json
```

The exact arguments and outputs are frozen by the approved task and executable tests. V1-Lite and
Controlled Lane V2 remain frozen audit material; V2 heartbeat remains `PAUSED`.
