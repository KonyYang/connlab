# ConnLab Personal Serial Execution Policy

Last Updated: 2026-08-07
Status: normative version-2 daily execution policy

## Authority and serial occupancy

The version-2 `connlab.personal-serial-control` block in `docs/task_board.md` is the sole machine
authority. `scripts/connlab_personal_task.py` is its only writer.

- `wip_limit` is 1.
- `running` and `implemented_pending_human_review` occupy the active slot.
- A request received while active returns `BLOCKED_ACTIVE_TASK_RUNNING` immediately after board
  parsing, before Git/worktree inspection, writer-lock acquisition, JSON parsing or classification.
  It performs zero writes; the User submits it again after the current task closes.
- Every write uses caller-supplied board SHA-256, the ignored lock, atomic replace and readback.
- Helpers never stage, commit, restore, stash, clean, push, dispatch or delete.

## Simple tasks

A task is simple only when root cause and expected result are clear, the complete change uses 1–3
repository paths including board and tests, and it changes no API, database, schema/migration,
persistence, authority, public-drive workflow, business rule, destructive behavior or external
state. It runs directly in the current primary worktree:

```text
submit -> activation commit -> implement -> targeted validation
-> implementation commit -> implemented_pending_human_review
-> User 关闭 -> closeout commit -> idle
```

## Complex tasks

Every other request is complex or needs discovery. Its normal User contract is limited to three
interactions: submit requirement, approve the Planner plan, inspect the result and say `关闭`.

Planning occupies the active slot. Planner is read-only. User approval binds a committed plan,
exact `may_touch` and validation contract. After that commit, the runtime automatically creates one
task host and completes Developer -> Reviewer -> QA -> Integrator in order. Approved bounded fixes
and the non-conflicting local integration transaction do not require another User approval. The
validated integrated result enters `implemented_pending_human_review`.

Scope changes, destructive actions and unresolved blockers return to the User. All other provable
transitions continue automatically. Failures remain active with typed blocker and durable Git/
evidence facts; no automatic cleanup or discard is permitted.

User close verifies and records retained clean resources before releasing active. The next request
is classified only when the User submits it against the idle board. No push occurs without separate
authorization.
