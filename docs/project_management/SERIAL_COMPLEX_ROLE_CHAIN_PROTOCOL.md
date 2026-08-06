# Serial Complex Role-Chain Protocol

Status: `IMPLEMENTED_DORMANT_PRE_CUTOVER_REVISION_6`

This protocol describes the version-2 personal serial workflow implemented by
`TASK_GOVERNANCE_SERIAL_COMPLEX_ROLE_CHAIN_AUTOMATION`. It is non-normative until an exact second
User approval and one verified atomic cutover commit. The current version-1 board, entry script,
execution gate, policy, `AGENTS.md`, and orchestrator skill remain authoritative.

## Invariants

- WIP is one. A second Task ID enters durable FIFO and never starts automatically.
- Classification is exactly `simple`, `complex`, or `needs_discovery`; missing decision facts never
  default to simple.
- Simple work stays on primary. Complex work uses a read-only Planner before approval, then exactly
  one task branch/worktree host for Developer, Reviewer, QA, and Integrator in that order.
- A role dispatch is first recorded as a native action. Its returned identity is then recorded, and
  only an exact committed callback may advance one phase.
- `SUBJECT_COMMIT` identifies the code tree. `EVIDENCE` identifies a distinct evidence commit/ref.
  Reviewer, QA, and Integrator must bind the same accepted subject.
- Every failure retains active authority, Git facts, evidence, and WIP. No helper stages, commits,
  pushes, messages, restores, stashes, force-removes, or deletes a branch.
- User close changes a complex task to `closing`; the active slot is released only after exact,
  read-only verification records the clean integrated host as `retained` with its task, thread,
  worktree, branch, HEAD, integration, evidence, and User decision identity.

## Commands and phases

The sole public writer is `scripts/connlab_personal_task.py`. Version-1 commands and result contracts
remain stable. Version-2 adds `classify`, `begin-role`, `record-invocation`, `consume-callback`,
`begin-host`, `record-host`, `record-integration`, `request-close`, `record-closeout`, and
`finalize-close`. The cutover commands are `plan-cutover`, `apply-cutover`, and
`verify-cutover-commit`.

The legal complex sequence is:

```text
planning/Planner -> awaiting_user_approval -> development/Developer
-> review/Reviewer -> qa/QA -> integration/Integrator
-> human_review/User -> closing -> idle
```

Reviewer or QA blocking callbacks return to `development`; other blockers use their frozen
`resume_phase`. Exact callback and blocker tables are normative in sections 7.3.1 and 7.4 of
`docs/task_governance_serial_complex_role_chain_automation_plan.md` and are encoded as closed tables
in `scripts/connlab_serial_complex.py`. Unknown fields, aliases, roles, statuses, next values, codes,
or state/command pairs fail closed.

## Storage and recovery

`scripts/connlab_serial_board.py` owns UTF-8 board parsing, version validation, CAS facts, the ignored
primary lock, atomic replace/readback, v1-to-v2 migration, and FIFO activation. Version 2 stores only
durable routing facts: task/worktree identity, role attempt and invocation IDs, exact subjects,
evidence refs, pending action/callback, integration, retained closeout disposition, and retained
resource refs. Conversation text is never authority. Reopening from board plus Git/task/plan/evidence
must be sufficient.

Revision 6 runtime closeout invokes no lifecycle mutation. The current helper verifies the registered
worktree identity, clean status, integration ancestry, and committed evidence before recording the
retained disposition. `scripts/connlab_serial_worktree.ps1` remains dormant compatibility material;
its bounded non-forced `Retire` path is optional future maintenance requiring separate exact User
authority. Dirty or unverifiable resources remain active and fail closed.

## Cutover safety boundary

The first implementation approval does not authorize cutover. All cutover-only bytes must remain
unchanged until a second approval binds the committed manifest and exact target hashes.

Both manifest planning and apply use the same intrinsic permission probe. For each of the eight
existing targets it opens an `O_RDWR|O_BINARY` handle without create/truncate/append and makes no
write call, then proves byte count, SHA-256, and Git blob unchanged. No caller permission JSON is
accepted. A read-only target returns `BLOCKED_CUTOVER_PATH_READ_ONLY` before materialization.

`apply-cutover` may only materialize the eight manifest-bound worktree targets; the Controller alone
exact-stages and commits. No runtime message is legal until `verify-cutover-commit` proves the exact
parent, tree, paths, index, hashes, and approval. Any permission drift requires a new manifest and a
new second approval.

The atomic cutover commit must simultaneously migrate v1 to v2, close this governance task, and
release active. There is no committed v1 idle interval. Retirement, archive, or closeout ordering is
not a cutover gate. History generation 1, its canonical index, Task-A, retained worktrees/evidence,
legacy helpers, external repositories, and remotes are never rewritten by this protocol.
