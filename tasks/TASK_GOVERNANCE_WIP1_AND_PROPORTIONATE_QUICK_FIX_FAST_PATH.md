# TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH

Status: `approved`
Type: governance execution-model change
Planning base: `ec93a0b686ff7a690e4955bd4238b7b9016de041`
Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
Owner at this gate: permanent Developer — implementation dispatch ready through Orchestrator
Next gate: Developer implementation in the exact isolated lane, then mandatory Reviewer/QA/Integrator

## Approval And Activation Status

- At approval preflight, `docs/task_board.md` recorded `Current Active Task: None` and no competing
  implementation owner; this approval commit activates only this governance task for worktree
  preparation.
- On 2026-07-31 the User explicitly approved the exact task/plan at planning revision
  `75ed37425029393780fad80b1b3745c4652e4f1d` and authorized automatic implementation through
  local Integrator acceptance.
- The authorization includes only the exact approved plan scope. It excludes remote push,
  publication, service restart, product-lane mutation, retained/frozen/cancelled worktree mutation,
  and destructive cleanup.
- Orchestrator created and independently verified the approved isolated lane without modifying any
  existing lane or retained/frozen/cancelled worktree.
- Lane: `task-governance-wip1-and-proportionate-quick-fix-fast-path`.
- Branch: `lane/task-governance-wip1-and-proportionate-quick-fix-fast-path`.
- Sibling worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-wip1-and-proportionate-quick-fix-fast-path`.
- Base and initial lane HEAD: `a1968c4999a33c6bee18c9185882ea3b927c2004`.
- Primary and lane worktree/index were clean at dispatch preflight; no competing implementation
  owner exists.
- One-time pre-schema bootstrap authority is recorded in the existing board prose with
  `wip_limit: 1`, `execution_state: implementation_running`, execution token owner
  `TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH`, empty queue, no paused task, and no
  parallel exception.
- The approved structured JSON execution schema and read-only helper do not exist yet. Their
  implementation remains Developer scope; this dispatch governance does not implement or pretend
  to validate them.

## Goal

Establish one enforceable ConnLab execution policy with default implementation WIP limit `1`, a
single execution token, FIFO queuing, proportional Quick Fix handling, safe serialized Quick Fix
preemption, deterministic non-destructive lane recovery, explicit user-approved parallel
exceptions, and cross-conversation fail-closed enforcement.

The policy must reduce ceremony for genuinely bounded fixes without weakening branch/worktree
isolation, review gates, authority boundaries, residual ownership, local integration acceptance,
or explicit gates for push, publication, restart, and destructive action.

## User-Visible Outcome

Under the approved implementation:

1. Starting a normal task while no token exists can activate that one task.
2. Starting another normal task while the token is held records it as `queued`; a separate
   worktree or non-overlapping paths do not bypass the queue.
3. A qualifying small fix uses one compact Quick Fix task capsule, an isolated worktree, targeted
   validation, risk-proportionate Reviewer/QA gates, and Integrator closeout without an independent
   Planner conversation or full plan file.
4. A Quick Fix may temporarily preempt one task only after the original lane has an immutable clean
   checkpoint and a complete pause record; recovery merges new `master` into the preserved lane
   without history rewriting.
5. A new conversation or script invocation re-reads the same task-board authority and cannot create
   an unauthorized implementation lane.

## Approved Policy Decisions

### Authority

- `docs/task_board.md` remains the sole business execution authority.
- Implementation adds one marker-delimited, fenced JSON execution-control block inside the board.
  It is not a second state file. Prose/lane rows remain human-readable views; the JSON block is the
  machine-readable authoritative execution section.
- `scripts/connlab_execution_gate.ps1` will be read-only. It parses the board block, validates Git
  and worktree facts for the requested intent, emits a stable decision code, and fails closed on
  missing, malformed, contradictory, or stale state. It never edits the board, creates/cleans a
  worktree, changes a branch, or routes a role.
- `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md` remains the frozen empty V1-Lite routing
  snapshot and is not execution authority.

### Default WIP And Token

- Default `wip_limit = 1`.
- `execution_token_owner` is `null` in `idle`, in a fully recorded `paused_preempted` state, and
  after `complete` or `cancelled` closeout. One task/lane owns it in
  `implementation_running`, `gate_running`, `quick_fix_running`, or `reconciling`.
- Reviewer, QA, and Integrator do not consume a second token, but the original task retains its
  token while those gates run.
- The token is recorded in the board before the first Developer/Quick Fixer product or governance
  implementation write and is released only after Integrator acceptance, formal
  cancelled/closed closeout, or a complete `paused_preempted` checkpoint transition.
- A user-approved parallel exception may record one secondary owner; it never silently changes the
  default WIP limit and is capped at two implementation lanes.

### Quick Fix Capsule

A proportional Quick Fix remains a formal task, but its task file is a compact capsule and no
separate full plan file is required. The capsule must contain:

- Goal
- Why Safe
- May Touch
- Must Not Touch
- Locked Paths
- Targeted Validation
- Risk Gate
- Branch / worktree / base
- Evidence path

When the User's goal is explicit, every `AGENTS.md` 19.1 predicate is proven from current
repository facts, and no escalation trigger exists, the Orchestrator must use this fast path. It
must not require or route an independent Planner conversation, a separate full plan, repeated User
approval, or default QA. Ambiguity, scope expansion, ownership conflict, unexplained failure,
second failed same-class fix, destructive need, or QF-4 classification makes Planner/User
escalation mandatory instead of optional.

Risk routing:

| Risk | Examples | Required route |
|---|---|---|
| QF-1 | spelling, semantically neutral copy, comment, one assertion | Quick Fixer -> Integrator |
| QF-2 | launcher, error handling, explicit wiring, bounded style | Quick Fixer -> Reviewer -> Integrator |
| QF-3 | real Windows, Office, browser, or runtime behavior | Quick Fixer -> Reviewer -> required QA -> Integrator |
| QF-4 | API contract, schema, migration, authority, persistence, public-drive write, or business semantics | forbidden from Quick Fix; full Planner/User flow |

A button-label change is QF-1 only when action, permission, authority, and lifecycle semantics are
unchanged. `Submit -> Approve`, `Delete -> Archive`, and `Confirm Matrix -> Save` are not presumed
copy-only fixes.

### Quick Fix Lifecycle And Terminal States

- Standalone Quick Fix: `idle` -> `quick_fix_running` with the Quick Fix as sole token owner ->
  `complete` after Integrator acceptance, residual closeout, and token release.
- Preempting Quick Fix: the original task first reaches durable `paused_preempted` with a complete
  pause record and `execution_token_owner: null`; only then does Quick Fix activation enter
  `quick_fix_running` with the Quick Fix as sole owner.
- After a preempting Quick Fix is accepted and proven on `master`, the board transfers ownership to
  the original task and enters `reconciling`. Successful reconciliation returns to
  `implementation_running`.
- A standalone Quick Fix cancelled/closed without integration enters `cancelled`, releases its
  token, and records its exact retained/discard residual closeout without destructive action.
- A preempting Quick Fix cancelled, closed without integration, or irrecoverably failed releases
  the Quick Fix token and returns the durable global state to `paused_preempted` with owner `null`.
  The original checkpoint and pause record remain intact; the Quick Fix branch/worktree/evidence
  receive explicit residual ownership. The original task does not silently resume. Planner/User
  must decide retry, abandon, or reconciliation scope.
- Reconciliation failure likewise returns to `paused_preempted` with owner `null`, preserves both
  checkpoints/evidence, and fails closed to Planner/User.

## State Model

The implementation must support these states without inventing aliases:

- `idle`
- `queued`
- `implementation_running`
- `gate_running`
- `paused_preempted`
- `quick_fix_running`
- `reconciling`
- `complete`
- `cancelled`

The board's structured execution section must express at least:

- `wip_limit`
- `execution_token_owner`
- `execution_state`
- `queue_position`
- `paused_reason`
- `preempted_by`
- `checkpoint_sha`
- `pause_master_sha`
- `resume_condition`
- `locked_paths`
- `residual_owner`
- `parallel_exception`

The complete state transitions, invariants, and decision codes are frozen in the associated plan.

## Queue And Priority Contract

- Only an approved/implementation-ready normal task may enter the implementation queue.
- With no token owner, the oldest eligible task may acquire the token.
- With an owner, a second ordinary task becomes `queued`; no implementation worktree is created.
- Default queue order is FIFO by durable board enqueue sequence/time.
- A preserved `paused_preempted` task has resume priority over ordinary queued tasks after its Quick
  Fix closes and reconciliation succeeds.
- User priority changes are explicit board governance actions with evidence; they are not inferred
  from repeated commands or conversation order.

## Serialized Quick Fix Preemption Contract

Preemption is allowed only when all of the following hold:

1. Stable reproduction, confirmed root cause, and unambiguous expected behavior.
2. One to three implementation files plus bounded tests.
3. No authority, schema, migration, API-contract, persistence, or public-drive semantic change.
4. No overlap with the original task's `Locked Paths`, shared files, or authority ownership.
5. The original lane can be represented by a clean committed checkpoint.
6. No destructive action is required.
7. No other `paused_preempted` task or `quick_fix_running` task exists.

Starting-state rules:

- Developer dirty: checkpoint is mandatory; Quick Fix remains blocked until the checkpoint commit,
  evidence, and clean status exist.
- Developer clean: record the existing committed HEAD; no empty/no-op commit.
- Waiting Reviewer/QA: reuse the immutable reviewed HEAD.
- Reviewer/QA running: the read-only gate may finish; no later write/handoff begins before the
  pause transition is durably recorded.
- Integrator merging: preemption is forbidden until merge completes or is safely aborted and the
  primary is verified clean with no merge state.

Pause records preserve branch, worktree, checkpoint, unfinished work, owner, pause reason,
`preempted_by`, `pause_master_sha`, and `resume_condition`. They never use stash, reset, restore,
branch deletion, worktree removal, or residual discard. The paused Developer must not continue
writing. Quick Fix preemption cannot nest.

## Non-Destructive Reconciliation Contract

After a preempting Quick Fix has Integrator acceptance and is proven on `master`, the permanent
Integrator performs the reconciliation gate. A standalone Quick Fix has no original lane and
closes directly as `complete` instead:

1. Prove the accepted Quick Fix HEAD is an ancestor of current `master`.
2. Re-read the pause record and verify the preserved lane remains at the recorded clean checkpoint.
3. Compare `checkpoint_sha`, `pause_master_sha`, and current `master`.
4. Recheck locked paths, shared ownership, and product-baseline changes.
5. Merge current `master` into the original lane; do not rebase or rewrite the recorded checkpoint.
6. Run the original task's affected validation and any new conflict-sensitive checks.
7. Create/record the reconciliation checkpoint and clean status.
8. Update evidence and the board, restore the original token owner, and resume
   `implementation_running` according to the recorded resume condition.

Any merge conflict, validation failure, ownership ambiguity, checkpoint drift, or product-behavior
disagreement fails closed. The original returns to/remains `paused_preempted` with
`execution_token_owner: null`; no side is selected and no reset/restore/discard is allowed. The
next role is Planner/User.

## Parallel Exception Contract

Default behavior is serial. A second implementation lane can start only when:

- a material external wait would otherwise stop useful work, or the User actively asks for
  parallel execution;
- path, locked-path, shared-governance, authority, test, and owner independence is proven;
- the board records the reason, both owners, exact scope proof, end condition, and explicit User
  approval evidence;
- no shared file, oversized mixed test, authority path, or uncertain ownership exists;
- no more than two implementation lanes will exist.

The exception expires at its recorded end condition and does not establish a new default.

## Cross-Conversation And Entry-Point Contract

Before any implementation write, every role must re-read `AGENTS.md`, the board execution section,
the current task/capsule/evidence, token/queue/paused state, and locked/shared ownership. Only the
permanent Orchestrator may initiate or resume implementation routing.

Planned enforcement points:

- `scripts/run_task.ps1` calls the execution gate before invoking orchestration and passes the
  stable gate result into the Orchestrator prompt.
- `scripts/connlab_lane_worktree.ps1 -Action Create` requires `-TaskId` and calls the gate; Create
  is allowed only for the recorded token owner or an approved secondary parallel owner.
- `.agents/skills/connlab-lane-orchestrator/SKILL.md` requires a fresh gate before implementation
  dispatch, Quick Fix preemption, reconciliation, and resume.

## Approved Implementation May Touch

Core policy and authority:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md` (new)
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`

Skills and enforcement:

- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `scripts/connlab_execution_gate.ps1` (new)
- `scripts/run_task.ps1`
- `scripts/connlab_lane_worktree.ps1`

Governance regression tests:

- `tests/unit/test_connlab_execution_gate_script.py` (new)
- `tests/integration/test_connlab_execution_gate_recovery.py` (new)
- `tests/unit/test_execution_wip_and_quick_fix_governance.py` (new)
- `tests/unit/test_connlab_lane_worktree_script.py`
- `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py`

Task-owned governance/evidence:

- this task file
- `docs/task_governance_wip1_and_proportionate_quick_fix_fast_path_plan.md`
- `docs/lane_evidence/TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH_planner.md`
- role evidence for this exact task using `_developer.md`, `_reviewer.md`, `_qa.md`, and
  `_integrator.md` suffixes

Role ownership remains strict: Developer changes the implementation allowlist and Developer
evidence in the isolated lane; Planner/Integrator alone update primary board state; Reviewer and QA
write only their evidence unless a separately approved package explicitly says otherwise.

## Must Not Touch

- `docs/project_management/ROLE_THREAD_REGISTRY.md` unless later Discovery proves a real role-duty
  change and the User separately approves that scope expansion
- `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`
- all Controlled Lane V2 helpers, registry, heartbeat, pilot/corrective files and tests
- `.agents/skills/connlab-controlled-lane/**`
- `scripts/connlab_controlled_lane.ps1` and `scripts/connlab_controlled_lane/**`
- `scripts/task_complete_commit.ps1`
- all product/backend/frontend/API/domain/database/schema/Office/LTR/Matrix/Fee/runtime code and tests
- every existing task, plan, evidence file, retained/cancelled branch, worktree, checkpoint, and
  residual directory not named in May Touch
- generated/release artifacts, real data/files, localhost processes, remote branches, and published
  state

The User approval authorizes Orchestrator to create the one exact isolated governance lane and
continue its approved role chain through local Integrator acceptance. This Planner gate performs
none of those actions. Cherry-pick, remote push, publication, service restart, stash, reset,
restore, clean, forced retirement, destructive cleanup, and any existing product-lane/worktree
mutation remain unauthorized.

## Locked Paths For Implementation

Upon User approval and successful activation, every implementation May Touch path above is locked
to this governance task until Integrator acceptance/cancellation. `docs/task_board.md` remains a
primary-only shared authority path. Existing retained/frozen/cancelled worktrees and their paths
remain independently locked to their recorded owners and are never absorbed into this task.

## Migration Baseline

The implementation must seed the structured board execution section from the fresh dispatch facts,
not from the older idle planning snapshot. At Developer dispatch, the authoritative one-time prose
bootstrap is:

- `wip_limit: 1`
- `execution_token_owner: TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH`
- `execution_state: implementation_running`
- queue empty
- no `paused_preempted` task
- no parallel exception
- ACTIVE_TASK_THREAD_BUNDLE remains `state: empty`, `active_task_id: null`
- TASK_368A/B/C stay accepted/locally integrated
- browser-release stays cancelled/closed without integration
- all listed retained/frozen worktrees and TASK_368A residual directory keep their current owner,
  checkpoint, branch/path, and non-destructive restrictions
- exact lane branch/worktree/base/initial HEAD are the verified values recorded above
- the structured JSON block and helper do not yet exist; Developer creates them from this bootstrap
  without releasing or transferring the token

If any of those facts change before implementation, activation stops for Planner reconciliation;
the implementation must not overwrite live state with the older planning snapshot.

## Acceptance Gates

### Reviewer

Mandatory. Review the exact planning-base-to-lane committed diff for state-machine consistency,
single authority, token invariants, fail-closed behavior, Quick Fix classification, non-destructive
recovery, frozen V2 compatibility, role ownership, and test completeness.

### QA

Mandatory because the task changes Windows PowerShell orchestration entry points and cross-session
recovery. QA uses a clean reviewed commit and disposable repositories/boards only. QA must not
create, modify, pause, resume, reconcile, or retire any real retained worktree.

### Integrator

Mandatory. Integrator validates the merged tree, confirms the exact package and ancestry, checks
the board migration against then-current live facts, records a residual ledger, and leaves primary
and lane clean. No push, publication, restart, or destructive retirement is included.

## Minimum Validation

The implementation must satisfy all sixteen original User-required scenarios plus explicit
standalone-Quick-Fix completion, preempting-Quick-Fix ownership transfer, preempting cancellation
or failure, reconciliation-failure owner-null semantics, Reviewer/QA/Integrator token retention,
and nested-preemption rejection. Compatibility, parser, static-governance, no-real-mutation, diff,
and clean-status checks also remain required. The exact matrix and concrete test allocation are in
the plan. All dynamic execution-gate tests use disposable repositories or fixture board text and
must prove the real retained worktrees are unchanged.

## Stop Conditions

Stop and return to Planner/User if:

- the exact User approval is revoked, contradicted, or would need scope expansion;
- the primary state no longer matches the migration assumptions and cannot be reconciled without
  changing scope;
- a second execution authority/file is required;
- board JSON cannot coexist safely with current human-readable board use;
- helper enforcement would need to mutate or clean an existing lane;
- any required path falls outside May Touch;
- V2 reactivation, product behavior, API/schema/authority/persistence semantics, remote mutation,
  runtime restart, or destructive action becomes necessary;
- Reviewer/QA finds an unresolved invariant, bypass, or real-worktree mutation risk;
- an implementation conflict would require choosing between accepted behavior and this policy.

## Current Stop Point

Commit the exact four-path primary dispatch governance package, then return to Orchestrator with
status `developer_dispatch_ready` and next role Developer. The execution token remains held by this
task through Developer, mandatory Reviewer, mandatory QA, and Integrator acceptance or a separately
recorded terminal transition. This Planner does not edit the isolated lane, implement the JSON
schema/helper, dispatch a role directly, modify any retained lane, merge, or push.
