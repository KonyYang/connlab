# Controlled Lane Orchestration V2

Status: bootstrap implementation candidate; production runtime inactive

Bootstrap is not activated. Bootstrap support is implemented, but this document does not
authorize a controller, heartbeat, production registry creation, real task call, branch/worktree
mutation, migration, retirement, archive, fetch, or push.

## Authority

The authority order is:

1. `AGENTS.md`;
2. `docs/task_board.md`;
3. current task, plan, and role evidence;
4. Git refs/worktrees/index;
5. local registry-v2 operational facts;
6. attributed callback/thread read-back.

The registry is an operational cache. It cannot approve a planned lane, widen May Touch, bypass a
User gate, or override repository governance.

## Deterministic Helper

The standard-library helper uses canonical UTF-8 JSON schema version 2. Standard output is one
JSON object. Decisions branch on typed `CTL_*` codes and exit classes, never message text.

Read-only commands:

```text
scan, route-plan, registry-status, recover, worktree-preflight,
integration-preflight, retire-preflight
```

CAS mutation commands:

```text
prepare-dispatch, mark-invocation-started, record-action-result,
record-callback, ack-dispatch, advance-state
```

Administrative commands:

```text
bootstrap-registry, register-lane
```

`bootstrap-registry` is genesis-only and creates generation `1`; exact replay is idempotent.
`register-lane` creates only a `planned` lane and cannot grant implementation authority. Both use
the same token-owned lock, expected-generation CAS, atomic replace, reread, and digest checks.
They add no error codes; the stable catalog remains 39 `CTL_*` codes.

Every mutation binds task, lane, route, operation, idempotency key, scope fingerprint, canonical
payload digest, expected stage, and expected registry generation. Identical replay returns
`CTL_ALREADY_APPLIED`; stale generation, changed key payload, or wrong stage fail closed.

## Journal Order

```text
prepare-dispatch
-> mark-invocation-started
-> exactly one external action
-> record-action-result
-> exact receipt/read-back or post-Git observation
-> dispatch_ack
-> advance-state
-> stop
```

Role completion is a later event. It cannot acknowledge dispatch or repeat state advance.

Possible-start recovery never resends because target history has zero matches. Exactly one frozen
route/operation match may be adopted. Zero, multiple, wrong, partial, or unreadable matches require
manual recovery. Retry is legal only while durable journal evidence proves invocation never
started.

## Registry

The future registry path is:

```text
<git-common-dir>/connlab-controlled-lane/registry-v2.json
```

Writes require a token-owned exclusive lock, expected-generation CAS, same-directory temporary
file, flush/fsync, atomic replace, reread, and digest verification. There is no silent lock TTL.
Real registry creation remains a separate User gate. Current legacy inventory has no machine v1
registry, so bootstrap records `migration.status=not_required` and imports only read-only
`legacy_retained` identities. Any unexpected v1/partial/recovery state stops bootstrap.

## Bootstrap Runtime

The bootstrap lane states are:

```text
bootstrap_controller_pending
-> bootstrap_controller_title_pending
-> bootstrap_heartbeat_pending
-> bootstrap_dry_run_pending
-> bootstrap_ready
```

Registry genesis is one administrative write. Controller creation, controller-title handling,
paused-heartbeat creation, and zero-write dry-run are separate journaled external actions. A native
controller thread ID is never preinvented: prepare freezes the request identity, then receipt plus
exact read-back supplies the thread ID that acknowledgement atomically adopts. This adoption leaves
the role binding `title_pending`; it does not trust an automatically generated title.

The controller title is `ConnLab｜研发任务编排与集成主控 v2`. The heartbeat is named
`ConnLab v2 controlled-lane scan`, uses `FREQ=MINUTELY;INTERVAL=5`, and is created `PAUSED`.
Callbacks are processed before heartbeat scans. Activation and pausing are independent actions;
idle state never keeps a heartbeat active.

At title pending, exact observed title selects a journaled read-only adoption. Any other title
selects `set_thread_title` bound to the adopted thread, lane, task, route, operation, and canonical
title. It follows prepare, invocation-start, one native mutation, result, exact read-back, ack, and
advance. Zero, multiple, wrong-thread, wrong-title, or unreadable observations fail closed.
Controller becomes active only after this title action; replay never recreates the thread.

## One-Action Routing

Each scan/callback produces either one typed blocker, no action, or one next action. Worktree
create/adopt and Developer-task create/adopt are separate scans. Reviewer implementation and
attributed bounded QA fixes reuse the same Developer task/worktree. QA is default unless both the
approved task and Reviewer evidence prove `qa_required=false`.

Manual smoke classifications:

- `active_lane_bounded_fix`;
- `planner_reconciliation_required`;
- `corrective_lane_required`.

Owner, scope, topology, dirty index/worktree, stale evidence, external blocker, or ambiguous
attribution conflicts fail closed.

## Native Task Adapter

Only the Codex app skill adapter may call native task APIs. Repository Python and PowerShell do not
copy credentials or call `_codex_runtime.ps1` for v2. Native create/send requires a durable
invocation marker; acknowledgement requires exact thread/lane/worktree/route/operation read-back.
`set_thread_title` is independently journaled and accepts only the exact adopted `threadId` and
canonical `title`; it cannot acknowledge controller creation.
Archive requires a separate User gate after clean non-force retirement and callback drain.

## Worktree Boundary

Create requires clean primary/index, exact base, absent branch/path, and no owner conflict. Adopt
requires exact repository/path/lane/branch/base/HEAD/scope and cleanliness. Retire requires
integrated clean HEAD, residual ledger, released owners, drained recovery/callbacks, and no active
task. Force, reset, restore, clean, branch `-D`, remote action, and ambient deletion are forbidden.

## Dry Run And Tests

Dry-run uses fake/in-memory task adapters and disposable Git repositories/registry roots. It
performs no real task API, automation, registry, branch/worktree, product, or remote action. The
real tests-only pilot remains separately gated after implementation acceptance.

The pilot task is `CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`. Its sole implementation
candidate is `tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py`; it uses public
CLI calls, disposable Git and registry roots, and fake native identities. It cannot change the
bootstrap helper. A helper defect stops the pilot and requires a corrective task.
