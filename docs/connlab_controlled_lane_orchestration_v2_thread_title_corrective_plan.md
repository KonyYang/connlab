# ConnLab Controlled Lane V2 Thread Title Corrective Plan

Status: implementation_tests_authorized / pending isolated corrective worktree creation and Developer implementation

Task: `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE`

Lane: `connlab-controlled-lane-orchestration-v2-thread-title-corrective`

## 1. Discovery Decision

Continue as an independent corrective lane. Reopening the accepted bootstrap implementation would
hide a newly discovered native-capability mismatch, while treating automatic title generation as
authority would violate deterministic read-back and replay.

Confirmed by User:

- the controller title must be exact;
- `set_thread_title` must be a separate journaled external action;
- every scan/callback permits at most one side-effecting external action;
- no runtime effect exists and none is authorized in this pass.

Confirmed by repository/native evidence:

- master is `62ded4291822e84512afcaf2e3b536b0b22fd230`;
- primary/index and retained worktrees were clean at discovery;
- registry/controller/heartbeat/pilot do not exist;
- `create_thread` has no exact-title argument;
- `set_thread_title` accepts only `threadId` and `title`;
- `read_thread` returns exact thread `id` and `title`;
- `list_threads` returns title/project/host/cwd facts and its current callable schema declares
  optional `query`; filtered or unfiltered results remain discovery-only, and unavailable or
  rejected query use fails closed;
- current bootstrap advances directly from controller creation to heartbeat and requires
  `title_verified` during create acknowledgement;
- the code catalog has 39 CTL codes and six mutation commands.

Planner inference:

- no new error code or journal command is necessary;
- a dedicated bounded title module is required because `bootstrap.py` is already 300 lines;
- a new corrective worktree is safer than mutating the accepted bootstrap branch.

Unresolved implementation details do not change scope: exact internal helper signatures may be
selected by Developer if they preserve the frozen input/output and line budgets.

## 2. Native Adapter Contract

### Mutation

```text
set_thread_title({
  threadId: <adopted controller thread id>,
  title: "ConnLab｜研发任务编排与集成主控 v2"
})
```

No project/worktree/lane fields are passed to the native tool. The tool result is opaque and is
stored only as a result digest/status. It cannot prove title or thread identity.

### Read-Back

The preferred exact read is:

```text
read_thread({threadId: <adopted controller thread id>, turnLimit: 1})
```

Ack requires returned `thread.id` to equal the adopted ID and `thread.title` to equal the
canonical title. Frozen host/cwd identity must also remain compatible with the adopted binding.
Bounded `list_threads(limit=..., query?=...)` may support recovery discovery, but any candidate
must still be filtered locally by exact thread ID. Query availability and ordering are advisory;
title text, list position, and generated summary are never identity.

## 3. State Redraw

| State | Required proof | Next action | Legal advance |
|---|---|---|---|
| `bootstrap_controller_pending` | none | `create_controller_task` | `bootstrap_controller_title_pending` |
| `bootstrap_controller_title_pending` | adopted exact thread | `set_controller_title` or `adopt_exact_controller_title` | `bootstrap_heartbeat_pending` |
| `bootstrap_heartbeat_pending` | exact title acknowledged | `create_paused_heartbeat` | `bootstrap_dry_run_pending` |
| `bootstrap_dry_run_pending` | paused heartbeat acknowledged | `run_zero_write_dry_run` | `bootstrap_ready` |

Create acknowledgement stores `controller.thread_id`, `observed_initial_title`, and a role binding
with status `title_pending`. It does not set `controller_acknowledged`.

Title acknowledgement stores canonical title verification, promotes the role binding to active,
sets `controller_acknowledged`, and only then exposes heartbeat creation.

## 4. Dispatch And Replay

Title target binding:

```text
task_id
lane_id
route_id
operation_id
scope_fingerprint
action_kind
action_version
thread_id
expected_title
saved_project_id
host_id
cwd
project_path
```

Create and title action identifiers are distinct canonical digests. The canonical inputs are
registry ID, bootstrap lane ID, action version, action kind, and the adopted thread ID where
available. Payload drift produces existing CAS/idempotency/binding codes.

The title mutation and acknowledgement sequence spans two scans:

```text
scan N:
prepare-dispatch
-> mark-invocation-started
-> one set_thread_title call
-> record-action-result
-> stop

scan N+1:
-> independent exact read_thread
-> ack-dispatch
-> advance-state
-> stop
```

The exact-title adoption branch uses one scan with one read-only native observation, the same
journal and exact ack, zero title mutation, and one advance. Replaying either completed mode is
`CTL_ALREADY_APPLIED`, with no generation drift and no native call.

## 5. Recovery Matrix

| Crash/observation | Result |
|---|---|
| create completed, no receipt, one exact create read-back | adopt create; never recreate |
| create adopted, before title prepare | title action is the only next action |
| title prepared, no invocation marker | same-ID retry allowed |
| title invocation possible, receipt missing, exact title read-back | adopt/ack; no resend |
| title invocation possible, wrong title/zero/unreadable | `CTL_RECOVERY_REQUIRED`; no resend |
| read-back multiple | `CTL_NATIVE_READBACK_AMBIGUOUS`; no resend |
| wrong thread | `CTL_THREAD_BINDING_MISMATCH`; zero-write |
| exact thread, wrong title/binding | `CTL_DISPATCH_ACK_MISMATCH`; zero-write |
| stale expected generation | `CTL_CAS_CONFLICT`; zero-write |
| exact title already present | journaled exact-title adoption; no title mutation |

Possible-start uncertainty always wins over target-history zero matches. No recovery path can
select `create_controller_task` after thread adoption.

## 6. File Plan

### Implementation

- `bootstrap.py`: keep genesis/admin and bootstrap progression; delegate title validation,
  acknowledgement, and adoption; final `<=270`.
- `controller_title.py`: own title target schema, exact read-back validation, action-mode choice,
  and title adoption mutation; final `<=220`.
- `state_machine.py`: insert title pending/action selection using helper; final `<=280`.
- registry/controller-ack existing test: migrate only the exact create-ack expectations from
  title-verified to thread-adopted; no new nodes or line growth.
- skill/protocol/role registry: document the native action and runtime contract.

### Tests

- `test_connlab_controlled_lane_controller_title.py` `<=240`: direct state, binding, ack,
  idempotency, and error matrix.
- `test_connlab_controlled_lane_controller_title_recovery.py` `<=300`: crash/recovery,
  no-resend, and one-action integration.
- existing registry test remains `<=485` and receives line-neutral expectation migration only.
- all other existing controlled-lane tests remain read-only regressions.

## 7. Package Isolation

Future implementation package is limited to the nine Future May Touch paths in the task plus its
governance evidence. No whole-directory staging is allowed. Reviewer compares the approved
governance base to one clean corrective checkpoint. QA uses that exact checkpoint in an isolated
worktree/archive. Integrator records excluded residual explicitly.

## 8. Worktree Sequence

1. Obtain Reviewer plan/readiness pass.
2. Obtain explicit User implementation approval.
3. Create a controlled local docs-only governance checkpoint so primary/index are clean.
4. Create the new corrective branch/worktree from that checkpoint.
5. Keep the accepted bootstrap and TASK_367A worktrees read-only and clean.
6. Run Developer TDD, Reviewer, QA, and Integrator gates.
7. Do not start runtime bootstrap until a later explicit User runtime gate.

## 9. Rollback

Before integration, discard only the isolated corrective branch/worktree after explicit
authorization. After integration, revert the corrective commit rather than editing registry or
runtime state. Runtime rollback is not required because implementation and tests use fake/temp
adapters and bootstrap restarts from registry absence.

## 10. Acceptance

- current RED proves direct create-to-heartbeat/title-in-create mismatch;
- GREEN verifies the complete title action and recovery matrix;
- exact 39-code/six-command parity;
- all line budgets and package whitelist pass;
- no real task/title/worktree/registry/automation mutation;
- original bootstrap runtime remains blocked until corrective acceptance plus a separate runtime
  authorization.

Reviewer plan/readiness re-gate passed and the User explicitly authorized implementation and tests
within the frozen exact nine-path scope. The next controlled action is Orchestrator creation of the
new isolated corrective worktree after a local governance checkpoint leaves the primary worktree
and index clean, followed by Developer implementation in that worktree. The accepted bootstrap
worktree remains read-only.

Runtime bootstrap/pilot, real registry/controller/heartbeat creation, fetch, push, migration,
archive, and cleanup remain unauthorized. After corrective acceptance, bootstrap restarts from
verified registry absence under a separate User gate.
