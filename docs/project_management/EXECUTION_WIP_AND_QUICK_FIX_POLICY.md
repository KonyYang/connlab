# ConnLab Personal Serial Execution Policy

Last Updated: 2026-08-06
Status: normative daily execution policy

## Authority

`docs/task_board.md` contains the sole machine authority in one marker-delimited
`connlab.personal-serial-control` version 1 JSON block. The supported writer is
`scripts/connlab_personal_task.py`; after the completed bootstrap migration, conversations and
PowerShell adapters must not patch the control block independently.

Current conversation execution is the sole daily path. There is no role dispatch, lane branch,
sibling worktree, parallel exception, Quick Fix role, QA role, Reviewer role, or Integrator role in
the personal workflow. Historical role/lane artifacts remain retained but non-executable.

## Serial State

- `wip_limit` is 1.
- `running` and `implemented_pending_human_review` both occupy the active slot.
- A new request received while occupied is appended to the durable FIFO `queue`.
- `close` releases the slot but never starts the queue head automatically.
- Only an explicit later command may run `activate-next` for the exact FIFO head.

Each helper write uses the caller's expected board SHA-256, an ignored
`tmp/connlab_personal_task.lock`, schema validation, an atomic replace, and a post-write readback.
The helper never stages, commits, restores, cleans, pushes, creates worktrees, or dispatches tasks.

## Simple Task

A task is `simple` only when its root cause and expected behavior are clear, its complete change is
1–3 total repository paths including `docs/task_board.md` and any test, and all named forbidden
categories are false. API contract, database, schema/migration, persistence, authority,
public-drive workflow, business semantics, destructive action, and external mutation always make
the task planned.

A simple task needs no plan or separate approval. The flow is:

```text
inspect/classify -> submit -> activation commit -> implement -> targeted validation
-> mark-review -> implementation commit -> implemented_pending_human_review
-> explicit User “关闭” -> close -> closeout board commit
```

## Planned Task

A planned intake initially records only task ID, summary, and `kind=planned`. Planning occupies the
active slot. After the short plan is committed and the User explicitly approves it, `approve`
atomically binds the exact scope, validation, plan reference, and approval reference. That board
transition receives its own local commit and the primary must be clean before implementation.

## Failure And Cancellation

A failure remains active. `block` records the typed blocker and dirty paths; `resume` requires an
explicit User decision. No automatic restore, discard, stash, cleanup, or scope expansion is
allowed. `cancel` and `close` require a clean primary. `close` additionally requires passed
validation and `implemented_pending_human_review`.

All work is local on primary `master`. Stage exact paths, create local commits, and do not push
unless separately authorized.
