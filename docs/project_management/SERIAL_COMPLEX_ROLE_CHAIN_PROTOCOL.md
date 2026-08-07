# ConnLab Serial Complex Role-Chain Protocol

Status: `NORMATIVE_V2`

The personal serial complex workflow is active. A normal complex task has exactly three User interactions:

1. submit the requirement;
2. approve the Planner plan;
3. inspect the completed result and say `关闭`.

After plan approval, Developer -> Reviewer -> QA -> Integrator proceeds automatically. The runtime
returns to the User only for an approved-scope change, a destructive action, or an unresolved
blocker.

## Authority and WIP

- The version-2 `connlab.personal-serial-control` block in `docs/task_board.md` is the sole machine
  authority.
- `scripts/connlab_personal_task.py` is the sole board writer. Every write uses expected board
  SHA-256, the ignored lock, atomic replacement and readback.
- WIP is one from activation through User close. Submit reads and parses the board, then checks
  occupancy before repository Git verification, worktree inspection, writer-lock acquisition, JSON
  parsing or classification. While occupied it returns `BLOCKED_ACTIVE_TASK_RUNNING`, changes no
  board byte and stores no request. After close, the User submits the next requirement again.
- Conversation memory is not authority. Board, Git, task, plan and evidence must reconstruct the
  next legal action.
- No helper stages, commits, pushes, messages, restores, stashes, deletes branches or force-removes
  worktrees.

## Daily flow

```text
requirement -> classify/submit
  simple -> direct primary implementation -> human review
  complex/needs_discovery -> Planner -> User approval
    -> one task host -> Developer -> Reviewer -> QA -> Integrator
    -> verified primary integration -> human review
User 关闭 -> retained closeout verification -> idle
```

Planner is read-only and runs before host creation. Approval binds the exact plan, `may_touch` and
validation contract in a committed board transition. One task branch/worktree host is then shared
sequentially by Developer, Reviewer, QA and Integrator. Reviewer or QA findings return automatically
to Developer within approved scope. Integrator binds the accepted subject and evidence before the
runtime performs the approved non-conflicting local integration transaction.

Planner `ready` enters `awaiting_user_approval`; User approval enters `development` before host
creation. A complex blocker resumes only to its validated `resume_phase`. User `Close` records
`request-close` and keeps WIP occupied while the Orchestrator automatically records the retained
closeout and calls `finalize-close`; only that final transition releases active. Simple-task close
retains its direct validated close behavior.

The public complex writer commands are `begin-role`, `record-invocation`, `consume-callback`,
`begin-host`, `record-host`, `record-integration`, `request-close`, `record-closeout` and
`finalize-close`. Callback schemas, blocker policies and phase order are closed tables in
`scripts/connlab_serial_complex.py`; unknown combinations fail closed. There is no public cutover,
manifest, permission-receipt or lifecycle-cleanup command family.

`scripts/run_task.ps1` exposes only `Submit`, `Approve` and `Close`. The helper's legacy
`activate-next` parser token remains only for version-1 rollback compatibility; a version-2 board
always returns `BLOCKED_LEGACY_MODE_FROZEN` with zero writes.

The common `block` command is also the legal non-callback failure writer for a v2 complex task. It
accepts only `connlab.serial-task-blocker` version 1, enforces the frozen code policy and requires the
blocker's `stage` to equal the active phase. `record-integration` writes human review only after the
integration-ready board is committed and Git independently proves the current primary merge commit,
its parents/tree, the exact QA-accepted task branch/worktree HEAD and clean state, and every accepted
evidence reference's committed byte hash.

## Stop and recovery

Failures keep the active slot and record a typed blocker with exact Git/evidence facts. Automatic
routing stops for scope or behavior change, destructive work, conflict, dirty/divergent state that
the approved transaction cannot resolve, ambiguous identity/evidence, or a repeated unresolved
failure. It never silently discards or cleans.

User `关闭` moves a complex task through retained closeout verification. Clean integrated task/thread/
worktree/branch/HEAD/evidence references remain retained; archive and retirement are not daily
gates. Close ends at idle; there is no queue activation action.

The first ordinary complex task is the monitored first real run, not a pilot or another governance
task. Repository-level validation proves the workflow contract but does not claim that the native
role chain has already passed end to end.
