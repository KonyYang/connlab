# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE

Status: qa_pass / pending Integrator packaging-readiness audit

Lane: `connlab-controlled-lane-orchestration-v2-thread-title-corrective`

Parent runtime blocker:
`CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_BOOTSTRAP`

## Current Phase And Authority

Current phase is post-implementation QA source-of-truth reconciliation. Reviewer implementation
re-gate and isolated QA passed for clean checkpoint
`2f3ba8c3e14fab6445c12d53dc783274e01fb0aa`. The candidate is locked pending Integrator
packaging-readiness audit. No registry, controller, heartbeat, pilot, task, worktree, branch, or
automation runtime object was created.

## Objective

Make the canonical controller title deterministic without pretending `create_thread` can set it.
The corrective inserts a separately journaled native `set_thread_title` action after controller
thread-ID adoption and before heartbeat creation.

Canonical title:

`ConnLab｜研发任务编排与集成主控 v2`

## Frozen Native Capability

- `set_thread_title` accepts exactly `threadId: string` and `title: string`.
- It exposes no project, worktree, lane, route, operation, or CAS fields.
- Its background result is opaque and is never title or identity authority.
- `read_thread(threadId=...)` returns a thread object containing at least `id`, `hostId`, `title`,
  `status`, and `cwd`; exact `id` and exact `title` are the acknowledgement authority.
- `list_threads(limit=..., query?=...)` exposes `id`, `projectId`, `hostId`, `cwd`, `title`, and
  `status`. Its current callable schema declares optional `query`, but query availability,
  filtering, and result ordering are discovery conveniences only; an unavailable or rejected
  query fails closed and never changes acknowledgement authority. It may support bounded
  discovery, not title acknowledgement by position or generated title.
- No native title mutation was invoked during discovery.

## State And Action Contract

The bootstrap state path becomes:

```text
bootstrap_controller_pending
  -> create_controller_task
  -> bootstrap_controller_title_pending
  -> set_controller_title or adopt_exact_controller_title
  -> bootstrap_heartbeat_pending
  -> create_paused_heartbeat
  -> bootstrap_dry_run_pending
  -> run_zero_write_dry_run
  -> bootstrap_ready
```

Controller creation and title mutation are distinct journal operations. One scan/callback may
invoke at most one native tool action, including read-back. Mutation and read-back therefore occur
in separate scans. `create_thread` is never repeated after exact thread-ID adoption.

Controller creation acknowledgement:

- accepts the exact returned/read-back thread identity and verified project binding;
- does not claim the generated title is canonical;
- stores the actual `thread_id`;
- stores the Controller role binding as `title_pending`, not active;
- advances only to `bootstrap_controller_title_pending`.

Title acknowledgement:

- freezes the adopted thread ID, canonical title, host/project/cwd binding, lane, route, operation,
  scope digest, and action version before invocation;
- persists invocation-start before `set_thread_title`;
- persists the opaque result and stops that scan;
- performs independent exact read-back in the next scan for the adopted thread ID and canonical
  title, then applies local CAS ack/advance without another native call;
- promotes the Controller binding to active and advances to heartbeat only after ack.

If pre-invocation read-back already shows the exact title, the action is
`adopt_exact_controller_title`: one journaled read-only native observation, zero title mutation,
exact read-back ack, and idempotent advance. It may not rely on title text alone.

## CAS And Idempotency

Both title modes use the accepted six-command journal without adding a command. Mutation and
read-back are separate scans over the same durable dispatch:

```text
prepare-dispatch
mark-invocation-started
record-action-result
stop
next scan: exact read-back
ack-dispatch
advance-state
```

The ordinary completion callback remains separate and is not used as dispatch acknowledgement.

Canonical identifiers are derived from registry ID, bootstrap lane ID, action version, adopted
thread ID, and action kind. Create and title operations have different stable route/operation IDs.
Canonical replay returns `CTL_ALREADY_APPLIED` without generation drift or native resend. Changed
thread, title, route, operation, scope, or action version is an idempotency/binding conflict.

## Crash And Recovery Contract

- Create succeeds, crash before create receipt persistence: exact thread read-back may adopt one
  frozen create match; zero/multiple/wrong/unreadable remains fail-closed and no create resend.
- Create adopted, crash before title prepare: scan returns the title action only; create remains
  complete and cannot be selected again.
- Title prepared before invocation marker: same-ID retry is allowed only with durable proof that
  invocation did not start.
- Title invocation may have started and receipt is missing: never resend. Exact adopted-thread
  read-back with canonical title may complete ack; wrong title, zero, or unreadable read-back is
  `CTL_RECOVERY_REQUIRED`; multiple matches is `CTL_NATIVE_READBACK_AMBIGUOUS`.
- Receipt persisted, crash before read-back/ack: exact read-back resumes ack with the same IDs.
- Wrong thread is `CTL_THREAD_BINDING_MISMATCH`; wrong title or changed frozen binding is
  `CTL_DISPATCH_ACK_MISMATCH`; stale generation is `CTL_CAS_CONFLICT`.
- Recovery never creates a second controller and never advances to heartbeat without exact title.

The existing 39-code catalog and six mutation commands remain authoritative. No new error code is
authorized because every frozen failure maps unambiguously to an existing code.

## Future May Touch

Implementation may touch only these paths after separate User approval:

1. `scripts/connlab_controlled_lane/bootstrap.py`
2. `scripts/connlab_controlled_lane/controller_title.py` (new)
3. `scripts/connlab_controlled_lane/state_machine.py`
4. `tests/unit/test_connlab_controlled_lane_registry.py` (exact existing controller-ack hunks only)
5. `tests/unit/test_connlab_controlled_lane_controller_title.py` (new)
6. `tests/integration/test_connlab_controlled_lane_controller_title_recovery.py` (new)
7. `.agents/skills/connlab-controlled-lane/SKILL.md`
8. `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`
9. `docs/project_management/ROLE_THREAD_REGISTRY.md`

Task/plan/evidence/board updates belonging to this lane are governance paths, not implementation
scope expansion.

## Must Not Touch

- `scripts/connlab_controlled_lane/contracts.py`, `registry.py`, `cli.py`, `ownership.py`,
  `native_environment.py`, `completion_authority.py`, `callbacks.py`, and `git_preflight.py`
- `scripts/connlab_controlled_lane.ps1`
- existing oversized/mixed tests except the one exact registry controller-ack hunk listed above
- `AGENTS.md`, product backend/frontend/API/schema/database/business tests
- credentials, `_codex_runtime`, real registry/controller/heartbeat/task/worktree/automation state
- TASK_367A worktree/branch/task and the accepted bootstrap branch/worktree

Any need outside Future May Touch returns to Planner/User and cannot be inferred as authorization.

## Line Budgets And Split Trigger

- `bootstrap.py`: current 300; mandatory semantic extraction to `controller_title.py`; final
  `<=270`, with no blank-line removal or statement compaction.
- `controller_title.py`: final `<=220`.
- `state_machine.py`: current 280; title-state wiring must use extracted helpers; final `<=280`
  with no net-growth fallback by formatting compression.
- `test_connlab_controlled_lane_registry.py`: current 485; exact existing assertions/fixture
  migration only, final `<=485`, no new test nodes.
- new unit test: `<=240`.
- new integration recovery test: `<=300`.
- skill `<=150`; controlled-v2 protocol `<=190`; role registry `<=60`.

At 80% of a frozen budget, Developer must report headroom and the Reviewer must check split
readiness. Crossing an explicit final budget mandates semantic extraction or a new bounded test
module. The already full bootstrap module and pressure registry test use the mandatory
extraction/no-growth rules above. All Python files remain below the 500-line hard limit.

## TDD And Validation

RED must prove the current checkpoint cannot represent the independent title action and currently
advances directly from controller creation to heartbeat.

GREEN must cover:

- thread-only create acknowledgement and `title_pending` binding;
- exact set-title request schema and opaque receipt handling;
- exact read-back before heartbeat;
- exact-title adoption without title mutation;
- stable create/title IDs and replay without generation drift;
- pre/post invocation crash points, lost receipt, and no resend;
- wrong thread/title, zero/multiple/unreadable read-back, and stale CAS zero-write;
- one side-effecting external action per scan;
- 39 codes and six mutation commands unchanged;
- absent-registry restart and no prior failed-runtime adoption.

Focused commands:

```powershell
py -m pytest tests/unit/test_connlab_controlled_lane_controller_title.py -q
py -m pytest tests/integration/test_connlab_controlled_lane_controller_title_recovery.py -q
py -m pytest tests/unit/test_connlab_controlled_lane_registry.py -q
py -m pytest tests/unit/test_connlab_controlled_lane_state_machine.py -q
py -m pytest tests/unit/test_connlab_controlled_lane_bootstrap.py -q
py -m pytest tests/integration/test_connlab_controlled_lane_bootstrapped_pilot.py -q
$files = @(
    Get-ChildItem 'tests/unit' -Filter 'test_connlab_controlled_lane_*.py' -File
    Get-ChildItem 'tests/integration' -Filter 'test_connlab_controlled_lane_*.py' -File
) | Sort-Object FullName | ForEach-Object FullName
py -m pytest $files -q
```

Also require candidate `py_compile`, three PowerShell parser checks, 39-code/six-command parity,
UTF-8/trailing/diff-check, exact whitelist, physical-line budgets, and no-real-side-effect audit.

## Runtime Restart And Worktree Strategy

After corrective acceptance and a separate User runtime gate, bootstrap restarts from proven
registry absence. It does not adopt any state from the failed pre-genesis attempt.

Future implementation uses a new branch and worktree:

- branch: `lane/connlab-controlled-lane-orchestration-v2-thread-title-corrective`
- worktree:
  `D:\PythonProject\connlab\tmp\worktrees\connlab-controlled-lane-orchestration-v2-thread-title-corrective`
- base: the clean governance checkpoint that contains this approved plan and descends from
  `62ded4291822e84512afcaf2e3b536b0b22fd230`

The accepted bootstrap worktree remains clean/read-only at `91c6b425`; it is not reused because
its branch is an accepted implementation baseline. No topology change is authorized in this pass.

## Gate

Reviewer implementation re-gate passed and isolated QA accepted clean checkpoint
`2f3ba8c3e14fab6445c12d53dc783274e01fb0aa`: exact 10 reviewed paths, `945/106`, bounded
`188 passed`, recovery integration `7 passed`, and product-code diff `0`.

The future Integrator inventory is frozen as the reviewed 10-path checkpoint plus this exact
seven-path governance overlay:

1. `tasks/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE.md`
2. `docs/connlab_controlled_lane_orchestration_v2_thread_title_corrective_plan.md`
3. `docs/task_board.md`
4. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE_planner.md`
5. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE_developer.md`
6. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE_reviewer.md`
7. `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_V2_THREAD_TITLE_CORRECTIVE_qa.md`

The Developer evidence is already one of the reviewed 10 paths, so the union is exact 16 paths.
Governance-overlay numstat is `208/33`; base-to-final package numstat is `1152/138`. The accepted
bootstrap worktree remains read-only and is not reused.

Runtime bootstrap/pilot, real registry/controller/heartbeat/task/automation creation, fetch, push,
migration, archive, and cleanup remain unauthorized. After corrective acceptance, runtime
bootstrap must restart from verified registry absence under a separate User gate. Next role is
Integrator packaging-readiness audit only.
