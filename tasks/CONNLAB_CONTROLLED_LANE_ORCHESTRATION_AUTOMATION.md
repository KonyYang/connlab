# CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION

Status: implementation checkpoint accepted at `76a6e736` / pending User bootstrap-and-pilot authorization
Lane: `connlab-controlled-lane-orchestration-automation`
Owner role: Planner
Implementation authorization: frozen 34-path implementation complete and Reviewer accepted
Bootstrap authorization: unauthorized
Migration, worktree creation, task archival, and remote actions: unauthorized
Date: 2026-07-27

Gate checkpoint:

- Reviewer plan re-gate: passed.
- User approval: Developer docs-only planning-first only.
- Developer planning-first: complete.
- Reviewer implementation-readiness: B6 identified direct TDD coverage missing for the sixth CAS
  mutation command.
- Developer B6 docs-only bounded planning fix: complete.
- Developer bounded implementation reached B10 and stopped after read-only native capability
  preflight. B10 is open; B11 post-hoc completion authority and B12 same-lane identical-owner
  repair remain open and must be completed by the same Developer only after B10 is reconciled.
- User selected Option A. The unreachable worktree-first/task-second order is superseded by one
  native `create_thread(worktree)` action that creates the first Developer task and worktree
  together, followed by exact asynchronous identity adoption. The required combined Reviewer
  re-gate has now passed.
- Planner B6 source-of-truth reconciliation: complete.
- Reviewer implementation-readiness re-gate: passed; B1-B6 closed.
- User product/test implementation approval: explicit and limited to the frozen scope.
- Reviewer combined Option A plan and implementation-readiness re-gate: passed; B10-B12 may
  resume with the same Developer inside the exact 34-path boundary.
- Developer B10-B12 and B17-B20 bounded implementation/fix: complete.
- Reviewer implementation re-gate: passed against the actual 34-path candidate.
- Dedicated isolated QA gate: passed; task-specific evidence is
  `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION_qa.md`.
- Integrator packaging/readiness: passed for the exact 35-path checkpoint; evidence is
  `docs/lane_evidence/CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION_integrator.md`.
- Bootstrap and real runtime side effects: unauthorized.

## Current Phase / Why Allowed

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active product lane: none.
- This Planner pass is allowed only for minimal docs-only closeout repair after the accepted local
  checkpoint; product/bootstrap/runtime actions remain unauthorized.
- Current local `HEAD == master == 76a6e736d66ca0207f262f597513a779a1634571`; local `origin/master`
  tracking ref is `6767a3ae4116185d8ed27b53cfdc050975efce2e`, with comparison `0/1`;
  no fetch or remote-freshness claim, index empty, and only the exact seven-path closeout candidate.
- The retained TASK_367A worktree is clean at `53840b42`, `lane...master=0/5`, with no unique commit; it and every old role/control task remain read-only.

## Goal

Define ConnLab v2 controlled-lane orchestration so a future user can submit one product goal to
`ConnLab｜研发任务编排与集成主控 v2`. The controller will deterministically inspect repository,
lane, ownership, worktree, evidence, and thread state, then perform exactly one legal routing
action per callback or heartbeat. It must preserve Planner, Reviewer, User approval, Developer,
QA, and Integrator authority instead of turning automation into implicit approval.

## User-Confirmed Requirements

1. Preflight active lanes, worktrees, branches, shared owners, primary cleanliness, and index.
2. Create one branch and one project-bound worktree per approved product/tests-only lane.
3. Use the order:
   Planner -> Reviewer plan gate -> User approval -> Developer -> Reviewer -> QA -> Integrator.
4. Reviewer fixes return to the same lane Developer task/worktree.
5. Reviewer/QA validate a clean lane HEAD or exact isolated archive.
6. Integrator integrates only accepted committed input and records every excluded residual.
7. Retire a lane only after integration, validation, committed governance closeout, clean
   worktree/index, and no unowned residual.
8. Manual smoke issues must route to same-lane bounded fix, scope reconciliation, or a new
   corrective lane based on current `master`.
9. Bootstrap must preserve the old controller, old role tasks, and TASK_367A topology until the
   v2 migration and pilot gates pass.
10. First exercise v2 through a low-risk tests-only dry-run and one real tests-only pilot.

## Repository-Confirmed Baseline

- Existing reusable governance:
  - `.agents/skills/connlab-lane-orchestrator/SKILL.md`;
  - `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`;
  - `docs/project_management/PARALLEL_EXECUTION_MODEL.md`;
  - `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`;
  - `docs/project_management/ROLE_THREAD_REGISTRY.md`.
- Existing reusable local helpers:
  - `scripts/run_task.ps1`;
  - `scripts/connlab_lane_worktree.ps1`;
  - `scripts/task_complete_commit.ps1`.
- No `.agents/skills/connlab-controlled-lane/` skill exists.
- No machine-readable lane/worktree/shared-owner/idempotency registry exists.
- No focused tests currently cover the orchestration/worktree/commit scripts.
- `run_task.ps1` produces a broad prompt but does not own a persistent state machine, route
  journal, owner algorithm, or callback idempotency.
- `connlab_lane_worktree.ps1` safely refuses dirty create/retire and never force-removes, but it
  has human text output, derived paths, no adopt/recovery contract, and no persistent registry.
- `_codex_runtime.ps1` copies Codex auth/config into ignored repository `tmp/**`. V2 must not use
  or expand that credential-copy path; native app thread tools are the planned routing adapter.
- Current Codex runtime exposes thread list/read/send/create/rename/archive and heartbeat
  automation capabilities, but no v2 automation is configured or authorized in this task.

## Planned State Machine

Only these normal transitions are legal:

```text
planned
  -> plan_review_pending
  -> user_approval_pending
  -> authorized
  -> developer_environment_pending
  -> developer_active
  -> review_pending
  -> reviewer_pass
  -> qa_pending
  -> qa_pass
  -> integration_pending
  -> integrator_accepted
  -> closeout_pending
  -> retired
  -> archived
```

Controlled exception transitions:

- `plan_review_pending -> planner_fix_pending -> plan_review_pending` when Reviewer blocks the
  plan; the same Planner task performs the docs-only fix and no implementation task is created;
- `review_pending -> developer_fix_active -> review_pending`;
- `qa_pending -> developer_fix_active -> review_pending` only for an attributed in-scope defect,
  so Reviewer re-gates the corrected immutable checkpoint before QA resumes;
- `qa_pending -> planner_reconciliation` for scope expansion, while an external or unattributed QA
  blocker enters `paused_conflict`; neither path may expand product scope without Planner/User;
- any state -> `paused_conflict` on board/evidence/owner/ref mismatch;
- any pre-accept state -> `planner_reconciliation` on scope expansion;
- `integrator_accepted -> corrective_planning` for a post-integration product defect; accepted
  history is never rewritten.

A callback is only a wake-up event. It cannot approve a transition. The controller must reread
board/task/plan/evidence, Git facts, registry generation, and target task status before taking
one action.

## Thread And Worktree Reuse

- One mutable Developer thread and one mutable lane worktree per lane.
- Every Developer fix pass reuses the same thread ID, branch, and worktree.
- Reviewer and QA are short-lived, sequential, read-only tasks bound to the reviewed commit or
  exact archive; they never own product writes.
- Integrator runs against the clean primary worktree only after Reviewer/QA pass.
- A role task records `route_id`, lane, role, worktree/archive, base, reviewed HEAD, and stop
  state. Duplicate creation with the same role/lane/route is forbidden.
- Future Goal authorization must explicitly include short-lived role-task creation. This
  discovery does not create any task.

The first Developer task and worktree are one native resource-creation action:

1. `authorized` prepares `create-developer-environment` without requiring unknown native
   `thread_id`, `pendingWorktreeId`, path, or actual branch. The canonical request freezes
   `route_id`, `operation_id`, idempotency key, client request digest, saved ConnLab `project_id`,
   role, task, lane, scope/owner digest, `environment: worktree`, exact committed integration
   starting ref/base, and native-worktree intent. The immutable prompt contains the route and
   operation markers used for read-back.
2. After `mark-invocation-started`, exactly one native `create_thread(worktree)` call creates the
   Developer task and Codex-managed worktree together. It is one external tool side effect even
   though it returns two coupled resources. The raw receipt, including an immediate `threadId`
   and/or asynchronous `pendingWorktreeId`, is durably recorded and the lane enters
   `developer_environment_pending`. The create call is never repeated.
3. A later scan observes asynchronous completion. Exact receipt/read-back must establish the
   actual thread ID, pending-worktree identity when supplied, canonical worktree path, actual
   non-primary branch, base, HEAD, saved project binding, lane/role markers, and owner identity.
   One expected-generation `ack-dispatch` CAS atomically binds all actual identities. Partial
   identity cannot be adopted, and `advance-state` to `developer_active` is forbidden before this
   acknowledgement.
4. A scan or callback may execute at most one external action. Registry CAS writes and read-only
   authority observations may surround that action, but a scan cannot invoke a second create,
   send, fork, handoff, or Git mutation.
5. `review_pending` blocked and only an attributed, in-scope, bounded `qa_pending` blocker return
   to the existing Developer binding/worktree; they never create a replacement task/worktree.
6. QA is required by default. `reviewer_pass -> integration_pending` without QA is legal only
   when the user-approved task/plan explicitly records `qa_required: false` and the Reviewer pass
   evidence confirms that exact no-QA contract. Otherwise `reviewer_pass -> qa_pending`.

### Option A Native Capability Contract

The User approved Option A. Native schema remains authoritative:

- `create_thread` targets the exact saved ConnLab project and uses
  `environment: {type: worktree, startingState: {type: branch, branchName: <integration-ref>}}`;
- the request does not contain an arbitrary destination path, actual native branch, thread ID, or
  pending-worktree ID;
- the native service may return a thread immediately or a pending worktree receipt completed
  asynchronously;
- `list_threads`/`read_thread` and read-only Git topology observations are adoption evidence, not
  authorization to create again.

The starting ref must be the clean committed primary integration branch frozen at prepare time;
`working-tree` starting state is forbidden. The native actual branch is adopted only when it is
non-detached, non-primary, unique, checked out only in the returned worktree, clean, at the
expected base/HEAD, and owned exclusively by the lane. Native-generated `codex/*` is permitted as
the physical branch for this Option A environment; the registry remains the canonical
`lane_id -> actual_branch/path` mapping. A `lane/*` branch remains valid if the native service
returns one. No rename is implicit.

While an acknowledged `pendingWorktreeId` remains incomplete, the lane stays
`developer_environment_pending` and returns existing success code `CTL_NO_ACTION` with typed facts
`native_worktree_status=pending`, exact operation/route/pending-worktree IDs,
`retry_allowed=false`, and `adopted=false`. This is a zero-write/read-only observation and does not
change the authoritative 39-code catalog or exit class 0. If
invocation may have started and the receipt is missing, or read-back is zero after authoritative
completion, multiple, wrong, partial, or unreadable, recovery is
`CTL_RECOVERY_REQUIRED`; preserve the operation and do not create, send, adopt, or clean anything.

Before atomic adoption, verify primary/index cleanliness still matches prepare authority, project
and Git-common-dir identity, path uniqueness, expected starting base and ancestry, actual HEAD,
branch policy, lane prompt markers, scope digest, and exact/directory/authority shared-owner
conflicts. A mismatch is fail-closed and creates no owner claim or cleanup action.

Reviewer and QA tasks do not bind the existing Developer path. After the Developer produces a
clean committed lane checkpoint, each short-lived read-only role task may use one separately
prepared native `create_thread(worktree)` action from that exact reviewed branch/HEAD and must
adopt its own returned read-only worktree identity through the same receipt rules. Integrator uses
the saved primary project only after the reviewed package is integrated and primary is clean.
Implementation/QA fixes always reuse the original Developer thread/worktree via an exact send.

B11 post-hoc completion authority uses existing `record-callback`; no seventh mutation command is
added. Dispatch/adoption freezes only role, active gate, exact evidence path, and immutable input
HEAD. It must not freeze a final evidence digest or completion HEAD before the role runs. On role
completion, `record-callback` under one expected-generation CAS:

1. proves the adopted thread/worktree, current role/gate, callback key, and frozen evidence path;
2. reads that exact evidence below the adopted worktree, computes SHA-256, and reads the actual
   worktree completion HEAD;
3. requires callback payload evidence path/digest/HEAD to equal the observed values and requires
   the completion HEAD to satisfy the gate's ancestry/currentness contract;
4. atomically records callback plus observed completion authority, or performs zero write.

Normal post-dispatch evidence update and a new clean role commit must pass. A pre-dispatch
digest/HEAD, tamper, late or consumed callback, cross-gate/role/lane target, stale generation,
wrong evidence path, or mismatched HEAD must fail closed without storing completion authority.

B12 owner materialization is also explicit. Provisional-to-exact same-lane identical identity may
materialize once; canonical identical replay returns `CTL_ALREADY_APPLIED` with no generation
drift. Same-lane changed key, content digest, path, directory ancestry, authority ancestry, branch,
or worktree identity is a conflict and must never overwrite an owner. Cross-lane overlap remains
`CTL_OWNER_CONFLICT`. Direct bounded TDD must cover all of these cases. B11/B12 remain open for
the same Developer after scope approval and Reviewer re-gate.

## Shared-Owner Conflict Algorithm

1. Load authoritative board/task scope and operational registry.
2. Normalize repository paths to forward slashes, collapse dot segments, reject repo escape,
   and compare case-insensitively on Windows.
3. Only exact files and explicit directory prefixes are lockable; arbitrary globs are rejected.
4. Normalize logical authority keys as dot-separated segments.
5. A conflict exists when:
   - exact paths match;
   - a file lies under another active lane's directory prefix;
   - directory prefixes overlap;
   - authority keys match or one is an ancestor of the other;
   - an unregistered worktree/branch touches declared scope;
   - `docs/task_board.md` is requested by a non-Planner/non-Integrator mutation.
6. Owning states are `authorized` through `integration_pending`.
7. Owners release only when Integrator records the integrated commit and residual ledger.
8. Any unknown or ambiguous overlap returns `CTL_OWNER_CONFLICT` with zero Git/thread action.

## Idempotency And Recovery

- Canonical scope fingerprint:
  SHA-256 of sorted normalized May Touch, Locked Paths, authority locks, task ID, lane ID, and
  base commit.
- Callback event ID:
  SHA-256 of task, lane, role, evidence path, evidence content digest, reported status, and lane
  HEAD.
- Route ID:
  SHA-256 of lane, current state, target role, evidence digest, lane HEAD, and registry
  generation.
- Worktree operation ID:
  SHA-256 of action, lane, branch, exact path, base/integration commit, and scope fingerprint.
- Replaying a completed ID returns `CTL_ALREADY_APPLIED` and performs no duplicate route or Git
  mutation.
- Dispatch uses a prepared/result-or-sent/acknowledged/advanced journal for both native task
  actions and Git/worktree actions.
- Registry writes use an exclusive lock and atomic same-directory replace.
- A native task create/send embeds the immutable `route_id` and `operation_id`. Recovery reads
  the frozen target topology/history. Exactly one matching task/message is adopted. Zero matches
  never proves that invocation did not occur. Same-ID retry is legal only with durable,
  independently verifiable pre-invocation evidence that no invocation-start marker or tool-call
  attempt was recorded. Once invocation may have started, zero, multiple, wrong-target, ambiguous,
  or unreadable read-back returns `CTL_RECOVERY_REQUIRED` with no resend/create.
- If Git succeeds but result persistence fails, recovery may only adopt one exact clean
  branch/path/base/scope match. Absence of that topology is not proof that Git was never invoked.
  Same-ID retry likewise requires durable pre-invocation proof; possible-start plus zero, partial,
  duplicate, dirty, mismatched, or unreadable topology returns `CTL_RECOVERY_REQUIRED`. Recovery
  never creates a second worktree or deletes the discovered one.
- Merge conflicts, partial closeout, or thread archival failure remain explicit recovery
  checkpoints; no automatic reset, restore, clean, force removal, or history rewrite is allowed.

## Deterministic Helper Contract

The future helper is standard-library-only and provides these read-only operations:

- `scan`, `route-plan`, `worktree-preflight`, `integration-preflight`, `retire-preflight`,
  `registry-status`, and `recover`.

It also provides these single-responsibility CAS mutation operations:

- `prepare-dispatch`;
- `mark-invocation-started`;
- `record-action-result`;
- `record-callback`;
- `ack-dispatch`;
- `advance-state`.

Input includes:

- repository root and expected primary branch/HEAD;
- task/lane/current and desired state;
- exact branch/worktree/base/integration refs;
- normalized May Touch, Locked Paths, authority keys, evidence paths/status/digests;
- role/thread binding, route/callback/operation IDs;
- `dry_run` and expected registry generation.

Stable JSON output includes:

- `ok`, `code`, `message`;
- `operation_id`, `registry_generation`, `zero_write`;
- normalized Git/worktree/owner/evidence facts;
- conflicts and required recovery checkpoint;
- exactly one `next_action`, or `none`.

Every mutation request requires:

- `expected_registry_generation`;
- the canonical `idempotency_key`, `operation_id`, and `route_id`;
- task/lane, current state, action kind, canonical action payload digest, and scope fingerprint;
- the exact dispatch stage expected by that command.

Mutation results additionally return `dispatch_stage`, `previous_generation`,
`registry_generation`, and the canonical stored record digest. A successful first mutation
increments generation once. Repeating the same command with the same key and canonical payload
returns `CTL_ALREADY_APPLIED`, the stored result/stage, and no generation increment. Reusing a key
with different content returns `CTL_IDEMPOTENCY_CONFLICT`. A stale expected generation returns
`CTL_CAS_CONFLICT`; neither case performs an external action.

Command responsibilities:

1. `prepare-dispatch` validates the legal state/action pair and writes one `prepared` journal
   entry before any external action. It cannot create/send a task or mutate Git.
2. `mark-invocation-started` CAS-writes the durable `invocation_started` marker immediately before
   the one external call. Without this marker the adapter must not invoke the external action.
3. The controller performs exactly the marked external action.
4. `record-action-result` stores the exact external result. Native task/message actions use stage
   `sent`; Git/worktree actions use stage `result_recorded`. It cannot advance lane state.
5. `record-callback` stores a deduplicated `role_completion_callback` only after the target
   dispatch is acknowledged and the lane is in that role's active/pending state. It cannot
   acknowledge dispatch, regress state, or repeat an already consumed completion. It advances
   only that role binding to `completion_recorded`; a later route dispatch advances lane state.
6. `ack-dispatch` stores a distinct `dispatch_ack`. Native acknowledgement requires tool receipt
   plus target-thread read-back of the exact route/operation/lane/worktree/thread binding; Git
   acknowledgement requires the exact post-Git observation. Role evidence and completion
   callbacks are not valid dispatch acknowledgements.
7. `advance-state` is the only state-changing command. It requires the exact acknowledged
   dispatch, current generation, and one legal transition, then records `advanced`.

The event types and keys are disjoint:

- `dispatch_ack` key: SHA-256 of route ID, operation ID, action kind, frozen target identity, tool
  receipt digest, and read-back/observation digest;
- `role_completion_callback` key: the callback event ID derived from role, evidence digest,
  reported status, and lane HEAD;
- dispatch acknowledgement permits only dispatch/target/receipt/read-back fields;
- role completion permits only role/status/evidence/HEAD/blocker fields and must reference an
  acknowledged, advanced target-role route.

Exact replay returns `CTL_ALREADY_APPLIED`. Changed content under the same key returns
`CTL_IDEMPOTENCY_CONFLICT`. Mismatched dispatch identity returns
`CTL_DISPATCH_ACK_MISMATCH`; an early, stale, regressive, or already-consumed completion returns
`CTL_ROLE_CALLBACK_STATE_MISMATCH`.

The journal lives only under the approved Git-common-dir registry directory. These commands may
write registry/journal state but never product files, governance files, Git refs/worktrees, or
native tasks themselves.

Core result codes:

- `CTL_OK`, `CTL_DRY_RUN`, `CTL_NO_ACTION`, `CTL_ALREADY_APPLIED`;
- `CTL_INVALID_REQUEST`, `CTL_SCHEMA_UNSUPPORTED`, `CTL_REGISTRY_SCHEMA_MISMATCH`,
  `CTL_PAYLOAD_DIGEST_MISMATCH`;
- `CTL_REGISTRY_LOCKED`, `CTL_LOCK_BUSY`, `CTL_ATOMIC_WRITE_FAILED`,
  `CTL_POST_WRITE_VERIFY_FAILED`;
- `CTL_PRIMARY_DIRTY`, `CTL_INDEX_NOT_EMPTY`, `CTL_HEAD_MISMATCH`;
- `CTL_WORKTREE_MISMATCH`, `CTL_WORKTREE_DIRTY`, `CTL_UNINTEGRATED_HEAD`;
- `CTL_AUTHORIZATION_REQUIRED`, `CTL_LANE_NOT_AUTHORIZED`, `CTL_INVALID_TRANSITION`,
  `CTL_OWNER_CONFLICT`;
- `CTL_EVIDENCE_STALE`, `CTL_CALLBACK_CONFLICT`, `CTL_THREAD_BINDING_MISMATCH`;
- `CTL_SCOPE_CONFLICT`, `CTL_SCOPE_VIOLATION`, `CTL_GIT_PRECONDITION_FAILED`,
  `CTL_TOPOLOGY_STALE`;
- `CTL_CAS_CONFLICT`, `CTL_IDEMPOTENCY_CONFLICT`, `CTL_DISPATCH_STAGE_MISMATCH`;
- `CTL_DISPATCH_ACK_MISMATCH`, `CTL_ROLE_CALLBACK_STATE_MISMATCH`;
- `CTL_NATIVE_READBACK_AMBIGUOUS`, `CTL_RECOVERY_REQUIRED`;
- `CTL_REMOTE_FORBIDDEN`, `CTL_DESTRUCTIVE_FORBIDDEN`, `CTL_GIT_FAILED`.

All scan, plan, recover-plan, and `dry_run` operations are zero-write. A failing mutation
preflight performs no Git/thread action and does not advance the registry generation.

## External Action And Crash-Recovery Order

For every route, task, message, branch, or worktree side effect:

```text
prepare-dispatch CAS
  -> mark-invocation-started CAS
  -> exactly one external action
  -> record-action-result/sent CAS
  -> collect native receipt + exact target read-back proof, or exact post-Git observation
  -> ack-dispatch CAS
  -> advance-state CAS
  -> stop
```

The later role-completion callback is an independent journal event. It can enable a subsequent
route plan, but it cannot acknowledge the earlier dispatch or replay/regress its state advance.

Recovery is deterministic at every crash boundary:

| Observed durable stage | Recovery decision |
|---|---|
| no `prepared` entry | recompute from authoritative governance and prepare once |
| `prepared`, external invocation durably proven not started | retry the same operation ID only; proof must include pre-invocation journal state and absence of an invocation-start marker/tool-call attempt, not merely target-history zero-match |
| `prepared`, native create/send may have started but receipt is missing | read back the frozen target; exactly one route/operation match is adopted, while zero or multiple matches fail closed without another create/send |
| external side effect exists, result not recorded | adopt exactly one matching `route_id`/task or branch/worktree tuple, then record its result; ambiguous/mismatched state fails closed |
| native receipt/result recorded, no dispatch acknowledgement | read back the exact target binding and record `dispatch_ack`; do not wait for role completion and do not resend |
| Git result recorded, no dispatch acknowledgement | record only the exact post-Git acknowledgement; do not repeat the Git action |
| acknowledged, state not advanced | run only `advance-state` with CAS; do not repeat the external action |
| dispatch advanced, role completion absent | remain in the active/pending role state; do not recreate or resend |
| role completion replayed after consumption | return `CTL_ALREADY_APPLIED`; do not regress or repeat state advance |

A retry never receives a new operation ID. Once native create/send may have started, zero-match,
multi-match, unreadable target history, or inability to prove identity returns
`CTL_RECOVERY_REQUIRED` and never resends. Git retry remains limited to a durably not-started
operation; partial or ambiguous topology also fails closed.

## Registry Schema

The future local schema is JSON at:

```text
<git-common-dir>/connlab-controlled-lane/registry-v2.json
```

It is machine-local, contains no credentials, and is never committed. Required top-level fields:

- `schema_version = 2`, `registry_id`, `repository_fingerprint`,
  `git_common_dir_fingerprint`, `generation`;
- `created_at`, `updated_at`, and explicit `migration` markers;
- `lanes`, `worktrees`, `shared_owners`, `role_bindings`, `dispatches`, `callbacks`,
  `recovery_points`.

Each lane records:

- task/lane IDs, state, base, branch, worktree path/HEAD;
- scope fingerprint, exact path/directory/authority locks;
- evidence paths/digests and validation/merge gates;
- role-thread bindings and route IDs;
- integration commit/ref, residual ledger, closeout and retirement eligibility.

The board/task/evidence remain approval authority. The registry is an operational cache. Any
conflict with repository governance fails closed and routes Planner reconciliation.
Creation of the real registry, import from any v1 state, schema activation, and migration remain
separate User gates. The v1 source is never overwritten during conversion.

## Callback Template

```text
CONNLAB_CALLBACK_V2 {"event_id":"<sha256>","task_id":"<TASK>","lane_id":"<lane>","role":"<role>","status":"<status>","evidence_path":"<repo-path>","evidence_sha256":"<sha256>","lane_head":"<commit-or-null>","next_role_hint":"<role-or-user>","blocker_code":"<code-or-null>"}
```

The callback is sent once after evidence/checkpoint changes, then the role stops. The controller
validates it and performs at most one legal route.

## Manual Smoke Classification

| Condition | Route |
|---|---|
| Lane not yet integrated; issue is inside frozen behavior and May Touch | Same Developer thread/worktree bounded fix, then Reviewer and QA again |
| Issue changes behavior, May Touch, authority, API/data contract, or shared owner | `planner_reconciliation`; request User approval before implementation |
| Lane already integrated/accepted, regardless of retained worktree | New corrective lane based on exact current `master` |
| Failure cannot be attributed or reproduces only with ambient data | Fail closed to Planner/User; no product edit |

## V1 To V2 Migration And Retirement

1. Keep v1 controller, role tasks, TASK_367A thread/worktree/branch, and registry docs unchanged.
2. Implement and accept v2 skill/helper/tests in a separate approved lane.
3. Obtain separate User bootstrap approval.
4. Create `ConnLab｜研发任务编排与集成主控 v2`; register it without archiving v1.
5. Import old role task IDs and TASK_367A topology as `legacy_retained`, read-only.
6. Pass zero-write fixture dry-run.
7. Pass one real tests-only pilot through all roles, local integration, residual ledger, clean
   retirement, and role-task archival.
8. Reconcile v1/v2 callback queues and record a final v1 checkpoint.
9. Only after explicit retirement approval may the clean, integrated, no-unique-commit
   TASK_367A worktree/branch be retired non-force.
10. Archive short-lived pilot tasks only after retirement. Archive old controller/role tasks
    last, only with explicit approval and after v2 has no unresolved callback or recovery point.

Current preservation facts:

- retained TASK_367A worktree:
  `C:\Users\White\.codex\worktrees\705b\connlab`;
- retained branch:
  `lane/task-367a-matrix-editor-live-xlsx-export`;
- retained lane HEAD:
  `53840b42ea73358c31fe40c5225646363d485829`;
- worktree clean; lane has zero commits not in master and is four commits behind current master.

## Bootstrap Minimum Permission Contract

Bootstrap requires a separate User approval after Reviewer plan and implementation gates.
Minimum permissions:

- read repository governance, Git refs/worktrees, and registered task status;
- write only approved governance or exact lane worktrees;
- local branch/worktree create/inspect/non-force retire;
- exact-path local commits and authorized local integration;
- list/read/send/create/rename/archive Codex tasks inside the approved Goal;
- create a reviewed heartbeat proposal for the v2 controller.

Forbidden:

- fetch, push, network publishing, credential copying, broad filesystem access;
- `git add -A`, reset, clean, force delete, force worktree removal, history rewrite;
- automatic product approval, scope expansion, destructive discard, or old-task archival;
- operating on real DB, public drive, attachments, or generated product artifacts.

## Dry-Run And Pilot

### Zero-Write Dry-Run

- Use disposable temporary Git repositories, fake evidence, fake thread adapter, and temporary
  registry.
- Exercise every state transition, duplicate callback/route, owner conflict, crash recovery,
  dirty primary/index, stale evidence, partial worktree, integration, retire, and archive gate.
- Exercise all six mutation commands independently: `prepare-dispatch`,
  `mark-invocation-started`, `record-action-result`, `record-callback`, `ack-dispatch`, and
  `advance-state`.
- Direct `mark-invocation-started` command tests must prove: exact `prepared` is the only accepted
  source stage; the first write increments generation by exactly one; identical canonical
  operation/route/key/payload replay returns `CTL_ALREADY_APPLIED` without a generation increment;
  stale expected generation returns `CTL_CAS_CONFLICT`; changed payload or key reuse returns
  `CTL_IDEMPOTENCY_CONFLICT`; wrong stage returns `CTL_DISPATCH_STAGE_MISMATCH`; and the command
  writes only the durable invocation-start marker with zero external action.
- Crash after each durable stage and prove native task/message and Git/worktree actions are not
  duplicated. Crash-at-`invocation_started` and possible-start/no-resend recovery remain separate
  integration tests and do not substitute for the direct command tests above.
- Prove one unseeded native create call returns the first Developer task/worktree pair, moves to
  `developer_environment_pending`, and never invokes a second create.
- Prove pending completion, immediate and delayed receipt/read-back adoption, duplicate replay,
  partial identity, wrong path/branch/project/base/HEAD, owner conflict, and every crash boundary.
- Prove pending observation returns `CTL_NO_ACTION` exit 0 with the exact typed pending facts,
  preserves all 39 catalog codes, and performs zero write/generation change.
- Prove exact atomic identity adoption precedes `developer_active`, then Reviewer/QA bounded fixes
  reuse the same Developer environment.
- Prove `record-callback` accepts updated post-dispatch evidence and completion commit only after
  reading/recomputing their actual path/SHA/HEAD; pre-dispatch digest/HEAD, tamper, late,
  cross-gate/role/lane, wrong path, and stale generation are zero-write.
- Prove B12 identical first materialization and replay, same-lane non-identical
  key/content/path/directory/authority conflict, and cross-lane `CTL_OWNER_CONFLICT`.
- Prove Reviewer plan blockers return to the same Planner docs-only fix, implementation blockers
  return to the same Developer/worktree, QA is default, and no-QA bypass requires both explicit
  user-approved task contract and Reviewer confirmation.
- Prove native create/send acknowledgement advances to `developer_active` before any role
  completion callback; the later completion is recorded independently and enables the next route.
- Prove receipt-present/unacknowledged recovery and receipt-lost/exact-read-back adoption; zero,
  multiple, wrong-thread, wrong-worktree, or wrong-lane read-back fails closed without resend.
- Prove durable pre-invocation journal evidence permits same-ID retry, while possible-start plus
  zero, multiple, wrong-target, or unreadable read-back never retries; stale scans must contain no
  unconditional zero-match retry rule.
- Prove a QA blocker routes once to the same Developer/worktree only when attributed, in-scope,
  and bounded; Reviewer re-gates before QA resumes. Scope expansion routes Planner/User, while an
  external or unattributed blocker remains fail-closed.
- Assert no real branch, worktree, task, registry, product file, or remote action.

### Real Tests-Only Pilot

Planned candidate:
`CONNLAB_CONTROLLED_LANE_AUTOMATION_PILOT_TEST_ONLY`.

- One new bounded automation regression test module only.
- Run the full v2 role/task/worktree lifecycle from a clean current `master`.
- No product/API/schema/database/frontend behavior.
- Local integration only; no push.
- Acceptance requires one worktree, one reusable Developer task, immutable review input, isolated
  QA, exact residual ledger, clean retirement, archived short-lived tasks, primary/index clean,
  and idempotent replay producing no second action.

The pilot remains unauthorized until v2 implementation is accepted and the User explicitly
approves bootstrap/pilot execution.

## Future May Touch

### Skill And Governance

- `.agents/skills/connlab-controlled-lane/SKILL.md` (new, <=500 lines).
- `.agents/skills/connlab-controlled-lane/agents/openai.yaml` (new, <=80).
- `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md` (new, <=500).
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md` (compatibility/deprecation hunk <=80).
- `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md` (v2 hook <=60).
- `AGENTS.md` (v2 entry/locks only, <=40 additions).

### Deterministic Helpers

- `scripts/connlab_controlled_lane.ps1` (new thin adapter, <=180).
- `scripts/connlab_controlled_lane/__init__.py` (new, <=40).
- `scripts/connlab_controlled_lane/contracts.py` (new, <=300).
- `scripts/connlab_controlled_lane/registry.py` (new, <=350).
- `scripts/connlab_controlled_lane/ownership.py` (new, <=300).
- `scripts/connlab_controlled_lane/state_machine.py` (new, <=300).
- `scripts/connlab_controlled_lane/git_preflight.py` (new, <=400).
- `scripts/connlab_controlled_lane/callbacks.py` (new, <=220).
- `scripts/connlab_controlled_lane/cli.py` (new, <=350).
- User-authorized B16 bounded split:
  - `scripts/connlab_controlled_lane/native_environment.py` (new, cap 300; final <=220).
  - `scripts/connlab_controlled_lane/completion_authority.py` (new, cap 240; final <=180).
- `scripts/connlab_lane_worktree.ps1` (exact JSON/dry-run/adopt hooks; final <=350).
- `scripts/run_task.ps1` (exact v2 delegation hunk; final <=180).

`scripts/task_complete_commit.ps1` is reused read-only. `scripts/_codex_runtime.ps1` and its
credential-copy behavior are locked and must not be used by v2.

### Tests

- `tests/unit/test_connlab_controlled_lane_contracts.py` (new, <=300).
- `tests/unit/test_connlab_controlled_lane_registry.py` (new, <=400).
- `tests/unit/test_connlab_controlled_lane_ownership.py` (new, <=350).
- `tests/unit/test_connlab_controlled_lane_state_machine.py` (new, <=400).
- `tests/unit/test_connlab_controlled_lane_callbacks.py` (new, <=300).
- User-authorized B16 bounded split:
  - `tests/unit/test_connlab_controlled_lane_native_environment.py` (new, cap 300; final <=230).
  - `tests/unit/test_connlab_controlled_lane_completion_authority.py` (new, cap 260; final <=200).
- `tests/unit/test_connlab_controlled_lane_git_preflight.py` (new, <=450).
- `tests/integration/test_connlab_controlled_lane_dry_run.py` (new, <=450).
- `tests/unit/test_connlab_lane_worktree_script.py` (new, <=350).

Every Python file must remain below 500 UTF-8 physical lines including blanks. The User approved
the four bounded paths, expanding the frozen package from 30 to exactly 34 paths. They remain
uncreated until implementation is separately resumed after Reviewer re-gate.

Mandatory net budgets after the split use UTF-8 physical lines including blanks and require
semantic deletion/replacement of superseded worktree-first, preseeded-target, and pre-dispatch
completion-authority implementation/tests. Blank-line suppression or statement compaction is
forbidden:

- `ownership.py`: current 239, final <=235 (<240 80% trigger);
- `state_machine.py`: current 239, final <=230 (<240);
- `cli.py`: current 279, final <=270 (<280);
- `registry.py`: current 276, final <=276 (<280);
- `callbacks.py`: current 166, final <=170 (<176);
- registry test: current 319, final <=315 (<320);
- state-machine test: current 318, final <=310 (<320);
- callback test: current 239, final <=235 (<240);
- ownership test: current 146, final <=220 (<280).

`native_environment.py` owns Option A request/receipt/pending/adoption normalization and performs no
native calls. `completion_authority.py` owns B11 read-only evidence/HEAD observation and comparison
used by `record-callback`. Their bounded tests own the detailed B10 and B11 matrices. B12 direct
cases stay in the existing ownership test.

Implementation tests may exercise native-task and Git/worktree behavior only through fake,
in-memory, disposable temporary-repository, or dry-run adapters. They must not create, adopt,
retire, clean, or delete any real repository branch/worktree; write the current repository's
Git-common-dir registry; create/send/archive any real Codex task; or create a real automation or
heartbeat.

## Must Not Touch / Locked Paths

- Product backend/frontend/API/schema/database/Office/Matrix/Fee/LTR/project lifecycle code.
- Existing product and business-rule tests.
- Real DB, public-drive files, attachments, user workbooks, and generated artifacts.
- Current v1 role/control tasks and TASK_367A task/worktree/branch.
- `docs/project_management/ROLE_THREAD_REGISTRY.md` until bootstrap is separately authorized.
- Current `.agents/skills/connlab-lane-orchestrator/**`.
- Remote refs and all fetch/push/network actions.
- Destructive Git/filesystem actions and task archival.

## Planned Validation Gate

- Unit tests for schema, normalization, state machine, owner conflict, idempotency, callbacks,
  atomic registry, and deterministic codes.
- Disposable Git integration tests for create/adopt/inspect/integrate/retire failure-close.
- PowerShell parser and static forbidden-command/credential-copy checks.
- Crash/recovery tests at every prepared/external-result/sent/acknowledged/advanced boundary.
- Direct first-write, identical replay, stale-CAS, changed-payload/key, wrong-stage, and
  zero-external-action tests for `mark-invocation-started`.
- CAS conflict, duplicate replay, idempotency-payload conflict, and dispatch-stage tests.
- Suspended prior-contract worktree-create/adopt and Developer-task-create/adopt transition tests;
  the selected User-approved B10 contract must replace or retain them explicitly.
- Reviewer plan-fix, same-Developer implementation-fix, default-QA, and explicit no-QA tests.
- Native `dispatch_ack` versus later `role_completion_callback` ordering/replay tests.
- QA bounded blocker, scope-expansion, and external-blocker routing tests.
- Exact path/line-budget/UTF-8/trailing/diff checks.
- Dry-run proves zero writes outside temporary fixtures.
- Pilot proves no duplicate Developer/worktree/route and clean closeout.
- Reviewer security/scope review, QA isolated validation, and Integrator exact package gate.

## Rollback

Before bootstrap, rollback is deletion of the new unactivated skill/helper/tests and exact
protocol hooks. After bootstrap, first pause heartbeat/routing, preserve registry and evidence,
finish or freeze active lanes, revert routing to v1, and only then retire v2 short-lived tasks.
Never delete a registry, worktree, branch, or task as an automatic rollback.

## Stop Point

`post_checkpoint_source_of_truth_reconciliation_complete /
pending_reviewer_docs_only_closeout_gate`.

The exact 34-path candidate completed B10-B12 plus B17-B20, passed Reviewer implementation
re-gate and dedicated isolated QA, and is accepted at checkpoint `76a6e736` with parent
`6767a3ae`, exact 35 paths, `8097/21`, `138 passed`, clean `git show --check`, and residual `0`.
Local `master` leads the unfetched local `origin/master` tracking ref by `0/1`; no remote freshness
is claimed. Bootstrap, pilot, and TASK_367A cleanup remain separate User gates. Real registry
activation, heartbeat creation, real worktree/branch mutation, role-task creation or archival,
migration execution, local commit, fetch, and push remain unauthorized.
