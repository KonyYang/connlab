---
name: connlab-controlled-lane
description: Execute one authorized ConnLab lane routing action using the deterministic v2 helper.
---

# ConnLab Controlled Lane

Use this skill only after the repository task, plan, evidence, and board authorize the exact lane
phase. It implements one-action orchestration; it does not grant approval.

## Safety Boundary

- Reread `AGENTS.md`, `docs/task_board.md`, the task, plan, evidence, and Git/worktree facts.
- Only an authoritative `scan` may precede a native task or Git action. `route-plan` is a
  diagnostic-only pure projection and never authorizes dispatch preparation or execution.
- Execute exactly one external action per scan/callback, then stop.
- Never use `scripts/_codex_runtime.ps1`; it must not copy credentials or config.
- Never fetch, push, force-remove, reset, restore, clean, or discard.
- Never create, send, adopt, rename, or archive a task without the exact helper journal stage.
- `zero-write dry-run` performs no native task API call and no Git/registry mutation.

## Dispatch Protocol

1. `prepare-dispatch` with expected-generation CAS.
2. `mark-invocation-started` with the same route/operation binding.
3. Invoke exactly one approved native task or local Git action.
4. `record-action-result`.
5. Read back the exact target identity and call `ack-dispatch`.
6. `advance-state`.
7. Stop. Role completion is a later independent callback.

If the invocation may have started, never resend because history has zero matches. Adopt exactly
one frozen route/operation match; zero, multiple, wrong, partial, or unreadable results require
manual recovery. Same-ID retry is allowed only while the journal durably proves no invocation
marker or tool attempt exists.

## Native Task Adapter

The Codex app tools are the only native adapter:

- `create_thread`: only for the prepared lane/worktree-bound create action;
- `send_message_to_thread`: only for the frozen existing binding;
- `read_thread` or bounded task listing: exact receipt/read-back and adoption proof;
- `set_thread_archived`: only after a separate archive authorization and clean retired lane.

Every create/send payload includes immutable `route_id`, `operation_id`, task, lane, role,
worktree/archive, and scope digest. A task receipt acknowledges dispatch only after exact
read-back. A later role-completion callback cannot acknowledge or repeat dispatch.

## Role Routing

- Reviewer planning blocker returns to the same Planner.
- Reviewer implementation blocker and attributed bounded QA blocker reuse the same Developer task
  and worktree; QA fixes return through Reviewer.
- QA is default. Skip only with User-approved `qa_required=false` plus Reviewer confirmation.
- Scope/owner/authority change routes Planner/User.
- Post-accept manual smoke creates a corrective lane from current master.
- External or unattributed findings fail closed.

## Worktree Lifecycle

Use only exact helper preflights and the approved `connlab_lane_worktree.ps1` JSON/dry-run/adopt
surface. Create and Developer-task creation are separate scans. Adopt only exact clean
repo/path/lane/branch/base/HEAD/scope identity. Retire only clean integrated work with owners,
callbacks, recovery points, and residual ledger resolved.

## Callback

Send a concise `CONNLAB_CALLBACK_V2` JSON object bound to event, task, lane, role, status,
evidence digest, lane HEAD, route, operation, thread, and worktree. Then stop and let the next
scan recompute authority.
