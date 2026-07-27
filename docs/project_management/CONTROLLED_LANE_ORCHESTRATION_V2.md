# Controlled Lane Orchestration V2

Status: implementation contract only

Bootstrap is not activated. This document does not authorize a controller, heartbeat, registry
creation, real task call, branch/worktree mutation, migration, retirement, archive, commit, fetch,
or push.

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
Real registry creation and v1-to-v2 migration remain separate User gates.

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
