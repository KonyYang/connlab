# TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH Plan

Status: `approved`
Date: 2026-07-31
Planning base: `ec93a0b686ff7a690e4955bd4238b7b9016de041`
Task: `TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH`
Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

The User approved this exact plan on 2026-07-31 at planning revision
`75ed37425029393780fad80b1b3745c4652e4f1d` and authorized automatic implementation through local
Integrator acceptance. Orchestrator then created and verified the exact isolated lane at approval
governance commit `a1968c4999a33c6bee18c9185882ea3b927c2004`. This gate records the sole
implementation token and Developer dispatch authority in existing board prose. It does not
implement or seed the approved structured JSON schema/helper. Remote push, publication, service
restart, product-lane mutation, and destructive cleanup remain excluded.

Activated lane identity:

- lane: `task-governance-wip1-and-proportionate-quick-fix-fast-path`
- branch: `lane/task-governance-wip1-and-proportionate-quick-fix-fast-path`
- sibling worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-wip1-and-proportionate-quick-fix-fast-path`
- base and initial lane HEAD: `a1968c4999a33c6bee18c9185882ea3b927c2004`
- dispatch preflight: primary and lane worktree/index clean; no competing owner; no paused task or
  parallel exception

## 1. Discovery Gate

### Current state and why Planner may act

- Primary was verified at `master` HEAD
  `ec93a0b686ff7a690e4955bd4238b7b9016de041`, with clean worktree/index and no `MERGE_HEAD`.
- `docs/task_board.md` records `Current Active Task: None`, `Proposed Next Task: None`, Phase 11,
  TASK_368A/B/C accepted and locally integrated, and browser-release cancelled/closed without
  integration.
- `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md` is empty with no active task id.
- Permanent roles exist in `ROLE_THREAD_REGISTRY.md`; the permanent Orchestrator is the only daily
  router and the permanent Planner owns Discovery/task/plan/scope/gates.
- The User initially authorized isolated governance Discovery and later explicitly approved the
  exact formal task/plan plus automatic execution through local Integrator acceptance.

### User goal restatement

ConnLab should run one implementation task at a time by default, regardless of how many worktrees
or non-overlapping file sets exist. Ordinary work should queue, while genuinely small and safe
fixes should use a compact, proportionate fast path. A Quick Fix may serially preempt one task only
through a committed clean pause and must restore the original lane by non-destructive merge-based
reconciliation. The same rules must survive new conversations and script entry points without
creating a second authority beside the task board.

### Evidence read

- User request attachment:
  `C:\Users\White\.codex\attachments\12886837-6afa-4b75-b990-df65485932a5\pasted-text.txt`
- `AGENTS.md` sections 13-20
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/project_management/TASK_REVIEW_CHECKLIST.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `scripts/run_task.ps1`
- `scripts/connlab_lane_worktree.ps1`
- `tests/unit/test_connlab_lane_worktree_script.py`
- `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`
- TASK_368C task/plan as the latest concrete Quick Fix orchestration example
- read-only Git branch/HEAD/status/worktree inventory

### Confirmed by User

- Default implementation WIP limit is `1`; worktree isolation is mandatory but does not authorize
  parallel implementation.
- A token remains held through Reviewer/QA/Integrator gates until acceptance, cancellation/close,
  or a formal `paused_preempted` transition.
- Ordinary second tasks queue FIFO by default; paused-preempted recovery outranks ordinary queued
  work; the User may explicitly reprioritize.
- When every 19.1 predicate is proven and no escalation trigger exists, the Orchestrator must not
  route an independent Planner conversation, require a separate full plan, repeat User approval,
  or add default QA. The Quick Fix still requires an isolated worktree, targeted tests,
  proportionate risk gates, Integrator closeout, and no automatic push/release/restart.
- Preemption, recovery, parallel exception, cross-conversation enforcement, the minimum state
  fields, the 18 planning outputs, and 16 validation scenarios are required.
- `docs/task_board.md` must remain the single execution authority.
- The approval-record turn may update only the task, plan, Planner evidence, and primary task board;
  it must not create the implementation worktree or dispatch implementation roles.

### Confirmed by repository evidence

- Existing active protocols still say independent non-overlapping tasks can run in parallel by
  default, which conflicts with the requested WIP=1 default.
- `run_task.ps1` gathers Git facts and prompts Codex, but does not parse or enforce an execution
  token/queue/pause state.
- `connlab_lane_worktree.ps1 -Action Create` checks primary cleanliness and branch/path existence,
  but has no TaskId or execution-authority gate.
- The current orchestration skill has permanent-role routing, but still contains stale
  task-specific Controller/bundle callback wording.
- The operations guide and parallel model retain obsolete V1-Lite task-bundle rules inconsistent
  with `AGENTS.md` 19-20 and the permanent role registry.
- The current active bundle is a frozen empty routing snapshot, not approval authority.
- The two relevant governance tests contain stale V1-Lite assertions and currently do not protect
  WIP/token/queue/preemption/recovery semantics.
- Every registered worktree inspected in Discovery was clean. Four frozen V2 worktrees, the
  cancelled browser-release worktree, and retained TASK_368B/C worktrees exist; TASK_368A has a
  retained non-worktree residual directory. None is an active implementation token owner.

### Inferred by Planner

- A marker-delimited JSON block embedded in `docs/task_board.md` is the safest single-authority
  representation because Windows PowerShell can parse it with `ConvertFrom-Json` without adding a
  dependency or a second state file.
- The execution-gate helper should be read-only; board mutations remain explicit governance commits
  by authorized roles. This avoids making a script both judge and owner of execution state.
- A Quick Fix still needs a compact formal task file/capsule for durable scope and evidence, but it
  should not need a separate plan document.
- Permanent Integrator is the correct owner of pause-to-master reconciliation because it controls
  merge safety and local acceptance; any conflict returns to Planner/User.
- QA is mandatory for implementing this governance task because it changes Windows PowerShell
  routing and recovery behavior, although QA remains optional/proportionate for future Quick Fixes.

### Not yet confirmed

- No material Definition-of-Ready fact remains unconfirmed. Developer output, checkpoint HEAD, and
  validation results are future execution evidence rather than dispatch blockers.
- The structured JSON execution block and read-only helper intentionally do not exist before
  implementation; the existing board prose is the sole one-time bootstrap authority.

### Planning risks

- A second state file would drift from the board.
- A helper that mutates state could partially acquire/release a token or touch retained lanes.
- Updating only prose without entry-point enforcement would allow new conversations/scripts to
  bypass the model.
- Over-broad Quick Fix classification could relabel semantic changes as copy/style fixes.
- Preemption without immutable checkpoints or merge-based recovery could lose work or rewrite
  evidence SHAs.
- Updating current retained worktrees during migration would violate ownership and cancellation
  records.

### Questions and continue/stop decision

No clarification remains. The User explicitly approved the exact plan and local automatic role
chain, and Orchestrator proved the physical lane gate. Continue only through primary dispatch
governance, then return `developer_dispatch_ready`; Orchestrator performs the actual role routing.

### Definition of Ready

- User approval: **satisfied** for the exact plan at revision `75ed3742...`.
- Scope/behavior/authority/validation DoR: **satisfied**.
- Physical activation: **satisfied** — exact branch/worktree/base/HEAD are created and clean.
- Token/serialization gate: **satisfied** by the one-time existing-board bootstrap with WIP `1`,
  this task as sole owner, empty queue, no paused task, and no parallel exception.
- Required task/plan status: `approved`; current activation state: `implementation_running`;
  handoff status: `developer_dispatch_ready`.

## 2. Current Model Versus Target Model

| Concern | Current repository model | Target model |
|---|---|---|
| Default concurrency | Parallel-ready when paths appear independent | WIP=1, serial by default |
| Token | No authoritative implementation token | Board-embedded token, held through gates |
| Second ordinary task | May create another worktree/lane | Durable FIFO `queued`, no worktree |
| Worktree meaning | Isolation plus parallel-readiness input | Isolation only; never concurrency permission |
| Quick Fix | 19.1 exists, but recent fix still has full task/plan/Planner-style dispatch | Mandatory compact-capsule fast path, with no separate plan/Planner/reapproval/default QA when all predicates are proven and no escalation trigger exists |
| Preemption | No complete state/checkpoint/resume algorithm | One paused original + one Quick Fix, serialized and checkpointed |
| Recovery | Residual/worktree rules exist; preempted-base reconciliation is not normative | Merge current master into preserved lane, validate, checkpoint, resume |
| Parallel exception | Non-overlap can be enough | Explicit User approval, proof, owner/end condition, max two |
| Cross-conversation gate | Documentary checks only | Shared read-only PowerShell gate at CLI/worktree/skill dispatch |
| Authority | Board is prose source of truth; bundle is routing index | Board plus embedded structured authority; bundle remains frozen derived snapshot |
| Role model | AGENTS/registry are permanent, some docs/tests still V1-Lite | Permanent roles consistently referenced; V1-Lite/V2 frozen |

## 3. Complete State Machine And Transitions

### State invariants

| State | Token | Allowed durable shape | Forbidden |
|---|---|---|---|
| `idle` | none | queue may be empty or waiting for selection | implementation write |
| `queued` | owned by another task | task has unique queue position, no implementation worktree | Developer/Quick Fixer dispatch |
| `implementation_running` | current task | clean recorded base/worktree and implementation owner | second normal owner |
| `gate_running` | original task retained | immutable lane HEAD under Reviewer/QA/Integrator gate | another ordinary implementation |
| `paused_preempted` | none | one preserved clean checkpoint, complete pause record, and explicit residual ownership for any failed/cancelled preempting Quick Fix | original-lane writes or silent resume |
| `quick_fix_running` | Quick Fix | one capsule, isolated worktree, no nested preemption | second Quick Fix/ordinary start |
| `reconciling` | original task | accepted Quick Fix ancestor plus preserved original checkpoint | rebase/history rewrite |
| `complete` | none after closeout | acceptance, residual ledger, clean state | continued implementation |
| `cancelled` | none after closeout | explicit cancellation and retained/discard ownership | silent cleanup/restart |

### Transition table

| From | Event/gate | To | Required durable action | Stop/fail condition |
|---|---|---|---|---|
| `idle` | approved task selected | `implementation_running` | set owner/state/locks; commit board before write | readiness or clean-base failure |
| any owned state | ordinary second task | `queued` | append unique FIFO record and position | task not approved or duplicate ambiguity |
| `queued` | owner released and task is next eligible | `implementation_running` | remove queue entry, set owner, create/verify worktree | paused recovery has priority |
| `implementation_running` | Developer handoff | `gate_running` | record clean checkpoint/HEAD and next gate | dirty or missing evidence |
| `gate_running` | blocking finding | `implementation_running` | same owner returns for bounded fix | scope expansion/unclear failure |
| `gate_running` | all gates accepted | `complete` | Integrator acceptance, residual ledger, release token | merge/validation failure |
| `implementation_running` / `gate_running` | explicit normal-task cancellation closeout | `cancelled` | retain/discard ownership, release token | destructive action not authorized |
| `implementation_running` | eligible preemption + clean pause | `paused_preempted` | full pause record; release original token | dirty/no checkpoint/overlap |
| `gate_running` | read-only gate finishes, eligible pause | `paused_preempted` | reuse immutable HEAD and record pause | Integrator merge in progress |
| `idle` | standalone Quick Fix capsule activated | `quick_fix_running` | set Quick Fix as sole owner before write | capsule/readiness/risk failure |
| `quick_fix_running` without paused original | Integrator acceptance | `complete` | record residual closeout, then release Quick Fix token | acceptance/closeout failure |
| `quick_fix_running` without paused original | cancelled/closed without integration | `cancelled` | record retained/discard ownership, then release token | destructive action not authorized |
| `paused_preempted` | preempting Quick Fix capsule activated | `quick_fix_running` | acquire Quick Fix as sole owner; preserve paused record | existing Quick Fix or incomplete pause record |
| `quick_fix_running` with paused original | accepted and proven on `master` | `reconciling` | release Quick Fix ownership and acquire original task as reconciliation owner | Quick Fix not ancestor of master |
| `quick_fix_running` with paused original | cancelled/closed without integration/irrecoverable failure | `paused_preempted` | release Quick Fix token; preserve original pause/checkpoint and own Quick Fix residual; return Planner/User | no silent original resume |
| `reconciling` | merge/validation/checkpoint pass | `implementation_running` | reconciliation checkpoint and restored owner | any conflict/validation/ownership drift |
| `reconciling` | failure | `paused_preempted` | release original reconciliation token, set owner null, preserve all state, and return Planner/User | never auto-resolve/reset |
| serial state | approved parallel exception | same state + secondary owner | record exception proof/approval/end condition | max two or any shared ownership |
| parallel state | end condition | serial state | close secondary lane and clear exception | unresolved residual/conflict |

`complete` and `cancelled` are terminal for that task instance. Reopening requires a new explicit
governance action, not an implicit transition.

## 4. Execution Token Acquisition, Retention, And Release

### Acquisition

1. Permanent Orchestrator re-reads board/task/approval/evidence/Git/worktrees.
2. `connlab_execution_gate.ps1 -Intent StartTask -TaskId <id> -Json` returns a stable decision.
3. If allowed, authorized primary governance updates the board JSON/prose and commits the token
   owner before any Developer/Quick Fixer implementation write.
4. Worktree Create then rechecks that the caller TaskId is the recorded owner.
5. Dispatch rechecks again immediately before the role is authorized to write.

### Retention

- Developer work, Reviewer review, QA, and Integrator merge gate are one token lifetime.
- A blocked review/fix cycle does not release the token.
- A long-running read-only gate does not permit another ordinary implementation.
- Conversation inactivity, a clean worktree, or a separate branch never releases ownership.

### Release

- Integrator acceptance after exact package/validation/residual closeout.
- Explicit cancelled/closed governance with retained/discard ownership.
- Formal `paused_preempted` transition containing every mandatory pause field.
- Release is a board governance commit. A role callback alone is never release authority.

`paused_preempted` is a deliberately inspectable durable gap between owners: its complete pause
record remains authoritative while `execution_token_owner` is `null`. A preempting Quick Fix
acquires the token only in a later board commit that enters `quick_fix_running`. After an accepted
preempting Quick Fix is proven on `master`, a later board commit transfers the token to the
original task and enters `reconciling`. Reconciliation failure releases that token and restores
durable `paused_preempted` with owner `null`.

### Parallel exception representation

`execution_token_owner` remains the primary owner. `parallel_exception` may contain exactly one
`secondary_execution_token_owner`, approval evidence, proof, and expiry. The helper treats both as
owners and rejects a third.

## 5. Ordinary Queue Flow

1. `run_task.ps1` performs a read-only gate.
2. If no owner exists, it routes the Orchestrator to readiness/activation.
3. If another owner exists, the Orchestrator verifies the requested task is approved and records a
   unique queue entry; no implementation worktree or role dispatch occurs.
4. Queue entries contain task/lane, enqueue sequence/time, `queue_position`, dependencies, locks,
   requested priority, and evidence link.
5. Default selection is FIFO among eligible tasks.
6. A `paused_preempted` original whose Quick Fix was accepted and proven on `master` reconciles
   before ordinary queue selection. A cancelled/failed preempting Quick Fix leaves the original
   paused with owner `null` for Planner/User decision; it does not auto-resume.
7. User reprioritization requires exact evidence and recomputed unique positions.
8. Cancelled/invalid queue entries are closed explicitly; they are not silently dropped.

Repeated execute commands for the same task are idempotent: resume or report the existing queue
entry; never create duplicates.

## 6. Compact Quick Fix Capsule And Risk Gate

### Capsule storage

Use one compact file under `tasks/<TASK_ID>.md`; do not create a separate plan document. The
Orchestrator creates the capsule from explicit User intent and current evidence only after every
19.1 predicate is true. When those predicates are proven and no escalation trigger exists, the
Orchestrator must use the capsule fast path and must not route independent Planner, create a full
plan, repeat User approval, or add default QA. The board row and Quick Fixer evidence point to the
capsule. Planner becomes mandatory only for ambiguity, an escalation trigger, or QF-4 scope.

### Required capsule fields

1. Goal
2. Why Safe, including explicit 19.1 predicate evidence
3. May Touch
4. Must Not Touch
5. Locked Paths
6. Targeted Validation
7. Risk Gate (`QF-1`..`QF-3`)
8. Branch/worktree/base
9. Evidence path

### Risk decision

- QF-1: Quick Fixer -> Integrator. If semantic neutrality cannot be established, reclassify to
  QF-2/QF-4; do not retain QF-1 while adding discretionary ceremony. QA is not part of QF-1.
- QF-2: Quick Fixer -> Reviewer -> Integrator. QA only on Reviewer-identified environment gap.
- QF-3: Quick Fixer -> Reviewer -> QA -> Integrator.
- QF-4: no capsule/dispatch; Planner Discovery and User approval.

Scope changes, semantic button renames, authority/API/schema/persistence work, public-drive writes,
or a second failed same-class attempt are QF-4 regardless of file count.

### Standalone And Preempting Lifecycle

- Standalone: `idle` with owner `null` -> `quick_fix_running` with Quick Fix sole owner ->
  Integrator-accepted `complete` with owner `null`. Token release occurs only after acceptance and
  residual closeout.
- Standalone cancellation: `quick_fix_running` -> `cancelled` with owner `null` after exact
  closed-without-integration residual ownership; no destructive cleanup is implied.
- Preempting: durable `paused_preempted` with owner `null` -> `quick_fix_running` with Quick Fix sole
  owner and preserved pause record -> accepted-on-master `reconciling` with the original task as
  sole owner -> `implementation_running` after reconciliation checkpoint/validation.
- Preempting cancellation or irrecoverable failure: return to `paused_preempted` with owner `null`,
  preserve the original checkpoint/pause record, retain the Quick Fix branch/worktree/evidence
  under an exact residual owner, and stop at Planner/User. Do not silently resume the original.
- Reconciliation failure: release the original reconciliation token, return to
  `paused_preempted` with owner `null`, preserve both histories/evidence, and stop at Planner/User.

## 7. Preemption Rules By Starting State

| Starting state | Allowed preparation | When pause becomes valid | Quick Fix start condition |
|---|---|---|---|
| Developer dirty | Developer creates exact clean checkpoint and evidence | clean branch/index at checkpoint | only after board pause commit |
| Developer clean | reuse committed HEAD; no no-op commit | HEAD/owner/unfinished work recorded | only after board pause commit |
| Waiting Reviewer | reuse immutable handoff HEAD | pending gate and resume condition recorded | only after pause commit |
| Waiting QA | reuse reviewed HEAD | required QA/resume condition recorded | only after pause commit |
| Reviewer/QA running | let current read-only gate finish; block next write/handoff | final gate result plus immutable HEAD recorded | only afterward |
| Integrator merging | none | only after merge completes or clean safe abort/no merge state | otherwise forbidden |

Every pause records `paused_reason`, `preempted_by`, `checkpoint_sha`, `pause_master_sha`, previous
owner, unfinished items, resume condition, locks, branch, worktree, and evidence. The durable pause
commit sets `execution_token_owner` to `null`; Quick Fix activation is a later, inspectable commit.
At most one paused original and one Quick Fix exist. No stash/reset/restore/delete/retire/discard
and no nested Quick Fix are permitted.

## 8. Non-Destructive Reconciliation Algorithm

Inputs: paused record `P`, preserved lane `L`, accepted Quick Fix `Q`, current `master` `M`.

1. Fail unless `Q` is an ancestor of `M`.
2. Fail unless `L` exists on the recorded branch, is clean, and HEAD equals
   `P.checkpoint_sha` (or a documented gate-only evidence commit descended from it).
3. Fail unless `P.pause_master_sha` is still an ancestor of `M` and pause metadata matches board
   and evidence.
4. Compare `git diff --name-only P.pause_master_sha..M` with original and Quick Fix locks; re-run
   shared/authority ownership checks.
5. Only after the accepted Quick Fix is proven on `master`, set state `reconciling` and acquire the
   original task as sole token owner in a primary governance commit.
6. Permanent Integrator merges `M` into `L` with no rebase. A conflict stops immediately; do not
   resolve automatically.
7. Run original affected validations plus targeted tests for every intersecting dependency.
8. Record the merge/reconciliation checkpoint SHA and prove lane/index clean.
9. Update pause evidence and board; clear pause/Quick Fix fields; restore the original token and
   `implementation_running` with the recorded continuation point.
10. If steps 6-9 fail, release the reconciliation token, leave the lane preserved, return the board
    to `paused_preempted` with `execution_token_owner: null`, record the exact blocker, and return
    Planner/User.

Reconciliation never rebases because the checkpoint SHA is durable evidence. It never resets,
restores, stashes, discards, or deletes to obtain cleanliness.

## 9. Parallel Exception Gate

Candidate reasons are limited to material external waiting, proven independent scopes with
independent developers, or an explicit User request. Before starting a second implementation:

1. Prove exact May Touch, Locked Paths, authority, tests, governance writes, and owners are disjoint.
2. Reject shared board-edit timing unless a single primary governance owner serializes those
   writes.
3. Reject shared files, oversized mixed tests, authority paths, or any uncertainty.
4. Record reason, proof, both lane owners, end condition, approval evidence, and max concurrency 2.
5. Obtain explicit User approval for this instance.
6. Re-run the gate at worktree creation and dispatch.

The exception expires automatically at its declared closeout condition but still needs an exact
board governance update. It cannot authorize a third lane or future parallel work.

## 10. Cross-Conversation And Restart Recovery

### Board embedded authority schema

Implementation adds exact markers around a fenced JSON object, with schema/version validation. The
object contains:

- schema/version, WIP limit, primary token owner, execution state;
- active task/lane/role and locked paths;
- ordered queue records;
- optional paused record;
- optional Quick Fix record;
- residual-owner records;
- optional parallel exception and secondary owner;
- last governance commit/evidence reference.

The schema must retain these exact contract keys (nested where appropriate): `wip_limit`,
`execution_token_owner`, `execution_state`, `queue_position`, `paused_reason`, `preempted_by`,
`checkpoint_sha`, `pause_master_sha`, `resume_condition`, `locked_paths`, `residual_owner`, and
`parallel_exception`.

Owner invariants are normative: `paused_preempted` requires a complete pause record and
`execution_token_owner: null`; `quick_fix_running` requires the Quick Fix as sole owner;
`reconciling` requires a paused-original record, proof that the accepted Quick Fix is on `master`,
and the original task as sole owner. `complete`/`cancelled` require owner `null` after closeout.
A preempting Quick Fix cancellation/failure or reconciliation failure must restore
`paused_preempted` plus owner `null`, never an ownerless `quick_fix_running`/`reconciling` state.

The helper rejects missing markers, duplicate blocks, invalid JSON, unsupported schema, duplicate
queue positions, owner/state contradictions, too many owners, incomplete pause records, or stale
worktree/branch facts.

### Helper interface

Planned command:

```powershell
.\scripts\connlab_execution_gate.ps1 `
  -Intent <Inspect|StartTask|CreateWorktree|ImplementationDispatch|QuickFixPreempt|Reconcile|Resume> `
  -TaskId <TASK_ID> `
  -Lane <lane-id> `
  -Json
```

Test-only disposable roots require an explicit `-RepositoryRoot` plus
`-AllowTestRepositoryRoot`; the helper remains read-only in all modes. Stable results include
`ALLOW_START`, `ALLOW_RESUME`, `QUEUE_REQUIRED`, `ALLOW_PREEMPT_CHECKPOINTED`,
`ALLOW_RECONCILE`, and `BLOCKED_*` reason codes.

### Entry-point wiring

- `run_task.ps1`: gate before orchestration; pass snapshot/decision to the permanent Orchestrator.
  `QUEUE_REQUIRED` routes queue governance, not implementation.
- `connlab_lane_worktree.ps1 Create`: require TaskId and `ALLOW_*` ownership; all other existing
  cleanliness/branch/path checks remain. Inspect/List/Adopt/Retire safety remains unchanged.
- Orchestrator skill: require fresh gate result before every write-capable dispatch, preemption,
  reconciliation, resume, and parallel start.
- A new conversation cannot self-dispatch; non-Orchestrator roles stop when the board does not name
  them as current authorized owner/gate role.

## 11. Exact Scope: May Touch, Must Not Touch, Locked Paths

### May Touch

| Area | Exact paths |
|---|---|
| Single policy/authority | `AGENTS.md`; `docs/task_board.md`; new `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md` |
| Referencing protocols | `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`; `docs/project_management/PARALLEL_EXECUTION_MODEL.md`; `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`; `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md` |
| Permanent-role skills | `.agents/skills/connlab-lane-orchestrator/SKILL.md`; `.agents/skills/connlab-planner/SKILL.md` |
| Enforcement scripts | new `scripts/connlab_execution_gate.ps1`; `scripts/run_task.ps1`; `scripts/connlab_lane_worktree.ps1` |
| Tests | new `tests/unit/test_connlab_execution_gate_script.py`; new `tests/integration/test_connlab_execution_gate_recovery.py`; new `tests/unit/test_execution_wip_and_quick_fix_governance.py`; `tests/unit/test_connlab_lane_worktree_script.py`; `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` |
| This task governance | task, plan, Planner evidence, and exact role evidence for this TASK only |

### Must Not Touch

- `ROLE_THREAD_REGISTRY.md` by default; registry facts already match permanent-role ownership.
- `ACTIVE_TASK_THREAD_BUNDLE.md`; it stays the frozen empty V1-Lite snapshot.
- Controlled Lane V2 protocol/skill/helper/registry/heartbeat/tests and every frozen V2 worktree.
- `scripts/task_complete_commit.ps1`.
- Existing product code/tests, API/schema/database/Office/Matrix/Fee/LTR/public-drive/runtime files.
- All other tasks/plans/evidence and all retained/cancelled worktrees/checkpoints/residuals.
- Remote state, publication, release artifacts, services, localhost, real data/files.

### Locked Paths

At implementation activation, lock every May Touch policy/skill/script/test path to this task.
`docs/task_board.md` is primary-only. Existing retained/frozen/cancelled paths remain under their
existing owners. No parallel exception is planned for this governance implementation because it
changes global dispatch authority and shared entry points.

## 12. File-Level Implementation Plan

| Order | Path | Exact planned change | Stop condition |
|---:|---|---|---|
| 1 | `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md` | Create the single normative WIP/token/queue/capsule/preemption/reconciliation/parallel/recovery policy | Any unresolved authority duplication |
| 2 | `AGENTS.md` | Replace default independent-lane parallel semantics with WIP=1, proportional Quick Fix, preemption/recovery, explicit exception, and policy reference; keep V2 frozen | Product/role scope expansion |
| 3 | `docs/task_board.md` | Seed marker-delimited JSON execution section from fresh facts and align current execution prose without changing retained ownership | Live state differs or migration would overwrite it |
| 4 | four protocol docs | Reference the single policy; remove contradictory default-parallel and V1-Lite bundle/controller rules; preserve role gates/residual hygiene | Copying a second full state machine becomes necessary |
| 5 | two skills | Require board/gate checks, compact capsule path, permanent callbacks, WIP queue/preemption/recovery; Planner enforces exception approval | Registry identity change needed |
| 6 | `scripts/connlab_execution_gate.ps1` | Add read-only parser/invariant checker/decision emitter with stable JSON and test-root support | Any write/cleanup capability is required |
| 7 | `scripts/run_task.ps1` | Call helper before routing; surface queue/block/allow decisions; preserve frozen explicit V2 path | V2 behavior would be reactivated/changed |
| 8 | `scripts/connlab_lane_worktree.ps1` | Require TaskId and helper allow decision for Create; preserve no-force/no-discard checks and other actions | Existing worktree must be altered to test |
| 9 | three new test modules | Add dynamic disposable-board/repo tests, restart recovery, and static governance/capsule/risk assertions | Tests require real retained worktree writes |
| 10 | two existing test modules | Replace stale V1-Lite assertions with permanent-role/frozen-legacy/gate compatibility while retaining V2 safety checks | Historical V2 behavior must be modified |
| 11 | task/evidence/board closeout | Record exact commits, gates, residuals, local-only state | Any out-of-scope path appears |

Implementation follows TDD for the helper: add failing disposable-fixture tests, implement the
minimal parser/decisions, then wire callers and update static governance tests.

## 13. Migration Strategy For Current Board/Active/Paused/Retained State

### Fresh pre-migration audit

Immediately before activation, hash/read the board, active bundle, registry, AGENTS, worktree list,
every worktree status, current HEAD/branch/index, and any `MERGE_HEAD`. If facts differ, Planner
reconciles before implementation; no snapshot is overwritten.

### Dispatch bootstrap from live facts

- state `implementation_running`, WIP `1`, execution token owner
  `TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH`, empty queue;
- no paused task, Quick Fix, or parallel exception;
- exact clean isolated lane exists at base/initial HEAD
  `a1968c4999a33c6bee18c9185882ea3b927c2004`;
- this is a one-time prose bootstrap under the existing board authority; the Developer must create
  the approved marker-delimited JSON section and read-only helper from these fresh facts, not from
  the older idle planning snapshot;
- ACTIVE_TASK_THREAD_BUNDLE remains empty/unmodified;
- TASK_368A/B/C remain complete/accepted/locally integrated;
- browser-release remains cancelled/closed_without_integration;
- current retained/frozen worktrees and TASK_368A residual remain recorded under the same owners
  and restrictions, never adopted by this task.

### Governance task activation

User approval, primary approval governance, exact clean branch/worktree creation, and the pre-write
token gate are satisfied. The task is `implementation_running` with the sole token held continuously
through Developer, mandatory Reviewer, mandatory QA, and Integrator acceptance or a separately
recorded terminal transition. The historical planning base remains evidence; the implementation
base is `a1968c4999a33c6bee18c9185882ea3b927c2004`.

### Existing active or paused task discovered later

- If an active token owner exists, this governance task queues unless the User separately approves
  an exact parallel exception (not recommended for a global gate change).
- If a paused-preempted task exists, preserve it and complete/resume its recovery before ordinary
  queue selection.
- Existing retained/cancelled/frozen items are residual inventory only; they never become token
  owners merely because their worktrees exist.

## 14. Compatibility Risks And Rollback

| Risk | Compatibility control | Rollback |
|---|---|---|
| Existing docs disagree | One normative policy; other docs link to it and retain role-specific detail only | Revert exact governance commit before any task uses new schema |
| Board parser breaks on prose | Exact unique markers and JSON schema; fixture malformed/duplicate tests | Restore prior board plus scripts as one atomic local revert |
| Old CLI calls Create without TaskId | Clear fail-closed message; update all documented callers/tests in same package | Revert caller/helper/worktree script together |
| Existing V2 path changes | Keep explicit `-ControlledLaneV2` branch frozen and covered by existing safety assertions | Revert any accidental V2-adjacent hunk; task forbids V2 files |
| Permanent roles regress to bundles | Static tests require registry IDs/permanent role wording and frozen empty bundle | Revert protocol/skill docs together |
| Quick Fix becomes loophole | Capsule predicate evidence, QF risk classes, semantic-copy negatives, gate tests | Disable Quick Fix routing in board/policy while preserving normal WIP gate |
| Token deadlock | State invariants, explicit terminal/pause release, recovery tests, User/Planner fail-closed path | Governance-only board correction with evidence; never edit product lane to unlock |
| Preemption loses work | Clean SHA, no stash/reset, immutable pause record, merge-not-rebase recovery | Keep original paused; revert only governance transition if no implementation write occurred |
| Real retained worktree altered in QA | Disposable repositories plus before/after worktree/hash assertions | Stop immediately; no cleanup; return User/Planner with exact diff |

Rollback is local and exact-path. Once another task has relied on the new board schema, rollback
requires Planner Discovery and a migration plan; it is not a blind script revert. No remote push is
part of this task.

## 15. Reviewer, QA, And Integrator Gates

### Reviewer gate (mandatory)

- Compare recorded implementation base to clean lane HEAD.
- Verify state/transition completeness, token invariants, queue priority, preemption state rules,
  non-destructive reconciliation, max-two exception, permanent role consistency, and frozen V2.
- Confirm helper has no writes/cleanup/routing and every write-capable entry point requires it.
- Review PowerShell quoting/path/JSON errors and stable reason codes.
- Confirm no product/retained worktree path is in the diff.

### QA gate (mandatory for this task)

- Use clean reviewed commit or disposable archive/worktree.
- Run all five governance test modules and Windows PowerShell parse checks.
- Exercise disposable Git repositories/board fixtures for token/queue/pause/reconcile/restart cases.
- Snapshot real worktree list/status/HEAD and protected file hashes before and after; require exact
  equality.
- Do not use Create/Retire against real worktrees and do not touch localhost/remote state.

### Integrator gate (mandatory)

- Require Reviewer pass and QA pass on the same reviewed ancestry.
- Verify exact allowlist and no missing/unexpected paths.
- Merge locally only under explicit implementation authorization.
- Re-seed/check board state against current facts rather than planning-time facts.
- Rerun the merged-tree suite and PowerShell parsing.
- Record residuals, primary/lane clean state, ancestry, and no push/restart/destructive action.

## 16. Validation Matrix And Concrete Tests

| # | Required scenario | Expected result | Primary test file |
|---:|---|---|---|
| 1 | idle normal task | `ALLOW_START`; governance can record sole owner | `tests/unit/test_connlab_execution_gate_script.py` |
| 2 | second normal task | `QUEUE_REQUIRED`; no Create/dispatch | same |
| 3 | Reviewer/QA/Integrator gate | existing task retains its token through every required gate; second task queues | same |
| 4 | dirty original before Quick Fix | preemption blocked until clean checkpoint | same |
| 5 | clean checkpoint | original can enter `paused_preempted` with complete record | same |
| 6 | overlapping Locked Paths | preemption rejected | same |
| 7 | nested Quick Fix | rejected when paused/Quick Fix already exists | same |
| 8 | accepted preempting Quick Fix closeout | only accepted-on-master proof permits transition from Quick Fix owner to original reconciliation owner; paused original outranks ordinary queue | `tests/integration/test_connlab_execution_gate_recovery.py` |
| 9 | reconciliation success | accepted Quick Fix ancestor + clean merge facts allow deterministic resume | same |
| 10 | reconciliation conflict | fail closed; original stays paused; no reset/selection | same |
| 11 | no exception/approval | second parallel implementation rejected | `tests/unit/test_connlab_execution_gate_script.py` |
| 12 | complete exception proof/approval | at most one secondary owner allowed | same |
| 13 | new conversation/restart | re-read fixture board/evidence restores token/queue/pause identically | integration recovery test |
| 14 | retained/frozen/cancelled worktrees | before/after path/HEAD/status unchanged and never adopted | integration recovery test |
| 15 | semantically neutral button copy | QF-1 capsule, no Planner/full plan/default QA | `tests/unit/test_execution_wip_and_quick_fix_governance.py` |
| 16 | API/schema/authority request | QF-4/full Planner; fast path rejected | same |
| 17 | malformed/missing/duplicate board JSON | stable `BLOCKED_*`, zero write | execution gate unit test |
| 18 | duplicate queue positions/owners | stable blocked result | execution gate unit test |
| 19 | `run_task.ps1` wiring | helper called before Codex routing; queue result does not dispatch implementation | governance static test |
| 20 | worktree Create wiring | TaskId required and helper allow required; no force/reset/cleanup | `tests/unit/test_connlab_lane_worktree_script.py` |
| 21 | permanent role model | no task-specific Controller/bundle routing; V1-Lite/V2 remain frozen | `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` |
| 22 | explicit V2 compatibility | existing ControlledLaneV2 branch remains frozen/unchanged | lane worktree script test |
| 23 | standalone Quick Fix lifecycle | `idle(null)` -> `quick_fix_running(QF)` -> Integrator-accepted `complete(null)`; token releases only after acceptance/residual closeout | execution gate unit + integration recovery tests |
| 24 | standalone Quick Fix cancellation | `quick_fix_running(QF)` -> closed-without-integration `cancelled(null)` with exact residual ownership and no destructive cleanup | integration recovery test |
| 25 | preempting Quick Fix lifecycle | `paused_preempted(null)` -> `quick_fix_running(QF)` -> accepted-on-master `reconciling(original)` -> `implementation_running(original)` | integration recovery test |
| 26 | preempting Quick Fix cancellation/failure | returns to `paused_preempted(null)`, preserves original checkpoint and Quick Fix residual, does not silently resume, and routes Planner/User | integration recovery test |
| 27 | reconciliation failure owner invariant | returns to `paused_preempted(null)` with both histories/evidence preserved and no reset/selection | integration recovery test |

Additional commands planned:

```powershell
py -m pytest tests\unit\test_connlab_execution_gate_script.py -q
py -m pytest tests\integration\test_connlab_execution_gate_recovery.py -q
py -m pytest tests\unit\test_execution_wip_and_quick_fix_governance.py -q
py -m pytest tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\connlab_execution_gate.ps1' -Raw -Encoding UTF8))"
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\run_task.ps1' -Raw -Encoding UTF8))"
powershell -NoProfile -Command "$null = [ScriptBlock]::Create((Get-Content 'scripts\connlab_lane_worktree.ps1' -Raw -Encoding UTF8))"
git diff --check
git status --short
```

Reviewer/QA/Integrator also run exact allowlist, forbidden-path, ancestry, and before/after protected
worktree/hash checks.

## 17. Proof Current Product Lanes Are Not Modified

Discovery baseline identifiers:

- Primary: `master@ec93a0b686ff7a690e4955bd4238b7b9016de041`, clean.
- Board blob: `a9b127dd1b0263c422c29bfac66860a34b1cbbde`.
- Active bundle blob: `3635fa070b7e5d1bc3453678c71c98f38ab54e99`.
- Role registry blob: `c5083212ea3c85915057e98de92c18fbcbdc9531`.
- AGENTS blob: `7ced6d5a2549057cb65fd89b3611793cdbc1566e`.

Read-only worktree inventory showed these clean registered worktrees and exact HEADs:

- V2 bootstrap `91c6b42564c1ef030761bd9c757889159e438974`
- V2 thread-title corrective `afe8ed173cf1f4f0f2bad4ad6aa7fb4fe10eb9ca`
- V2 approval-binding corrective `e22404456d0ee99d2d557e78d511c94d2e363002`
- V2 developer-plan-binding corrective `5f30db85b675b7f606a7b7474ce475d984988f6c`
- cancelled browser-release `0bf56ea09ba1a1baedd5ce982d0b47d73d1889df`
- retained TASK_368B `5cac86b60c728bcbb6a1b72a9e3d340fc976d21b`
- retained TASK_368C `e7e5ac635aa06eda0c11e18436ffa60c2d83c062`

The TASK_368A residual directory was observed as present but is not a registered worktree. This
planning turn neither entered nor changed it. Final planning verification must prove the commit
contains only the new task, plan, and Planner evidence; board/bundle/registry/AGENTS blobs and the
worktree inventory must remain identical.

## 18. Implementation Sequence And Per-Step Stop Conditions

| Step | Action after User approval | Required pass before next step | Stop condition |
|---:|---|---|---|
| 0 | Fresh Planner/Orchestrator audit | clean primary; live state reconciled; no conflicting owner | any mismatch needing scope/ownership choice |
| 1 | User-approval evidence and primary activation | satisfied by the approval-governance commit; exact approval, task/plan revision, and board status recorded | approval revoked/contradicted |
| 2 | Record sole token and create isolated lane | satisfied: exact branch/worktree/base clean; WIP=1 prose bootstrap records this task as sole owner | any later ownership/path contradiction |
| 3 | RED tests for board parser/token/queue/preemption/recovery | failures demonstrate missing policy behavior only | test needs real worktree mutation |
| 4 | Create normative policy and align AGENTS/board schema | one authority, schema parses, live migration exact | duplicate authority or live-state overwrite |
| 5 | Implement read-only helper | unit scenarios and zero-write checks pass | any mutation/cleanup capability needed |
| 6 | Wire `run_task` and worktree Create | entry-point tests/PowerShell parse pass; V2 frozen path preserved | compatibility cannot be bounded |
| 7 | Align protocols/skills and stale tests | static governance/permanent-role tests pass | registry/bundle/V2 change required |
| 8 | Full Developer validation and exact checkpoint | exact allowlist, clean lane/index, evidence ready | unexpected path/failure |
| 9 | Reviewer gate | pass on committed diff | blocking finding returns Developer; scope issue Planner/User |
| 10 | Mandatory QA disposable recovery gate | all validation-matrix scenarios, including standalone/preempting terminal paths, plus protected-state equality | any real-state change or unexplained failure |
| 11 | Integrator local merge/merged-tree validation | exact package, ancestry, board/live-state match, residual ledger, clean trees | merge conflict, stale migration, missing gate |
| 12 | Closeout | accepted locally, token released, queue state correct, no push/restart/destructive action | any residual lacks owner |

The task stops after local Integrator acceptance. Remote push, publication, service restart,
worktree force-removal, and cleanup of any pre-existing retained/frozen/cancelled item require
separate explicit authority.

## User Approval Record And Physical Activation Gate

The User approval covers this exact task/plan, especially:

- the board-embedded JSON authority design;
- the full May Touch/Must Not Touch/Locked Paths lists;
- compact task-file Quick Fix capsules without separate plans;
- mandatory QA for this governance implementation;
- read-only helper and its three enforcement points;
- live-state migration and rollback strategy;
- automatic execution through local Integrator acceptance without push, product-lane mutation, or
  destructive cleanup.

Status is `approved`. The exact branch/worktree, protected worktrees, and pre-write token ownership
have been verified and recorded. Activation state is `implementation_running`; callback state is
`developer_dispatch_ready`. The structured JSON schema/helper remain unimplemented until Developer
works in the isolated lane, and the token must remain held through mandatory Reviewer, QA, and
Integrator gates.
