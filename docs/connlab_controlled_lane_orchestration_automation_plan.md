# ConnLab Controlled Lane Orchestration Automation Plan

Date: 2026-07-27
Status: implementation checkpoint accepted at `76a6e736` / pending User bootstrap-and-pilot authorization
Task: `CONNLAB_CONTROLLED_LANE_ORCHESTRATION_AUTOMATION`
Lane: `connlab-controlled-lane-orchestration-automation`
Implementation/tests: accepted locally in exact 35-path checkpoint `76a6e736`
Bootstrap, real runtime side effects, migration, worktree creation, archival, commit, and push:
unauthorized

## 1. Discovery Decision

The User selected Option A after Developer proved the old worktree-first/task-second sequence
unreachable. The redrawn contract uses one native `create_thread(worktree)` action to create the
first Developer task and Codex worktree together, then atomically adopts the complete asynchronous
identity. Reviewer passed the combined Option A plan/readiness re-gate, Developer completed
B10-B12 and the bounded B17-B20 follow-up, Reviewer accepted the actual 34-path candidate, and
dedicated isolated QA passed. The QA source is this task's own evidence, not TASK_367A history.
Integrator packaging/readiness accepted the exact local checkpoint. Bootstrap, pilot, and real
runtime side effects remain separately gated and unauthorized.

Confirmed by user:

- one product goal should drive deterministic role/worktree orchestration;
- one legal route action per scan/callback;
- Reviewer fixes reuse the same Developer/worktree;
- clean committed review/QA input and exact Integrator residual ownership;
- strict closeout before retirement or task archival;
- preserve all v1 tasks and TASK_367A topology during discovery;
- use tests-only dry-run and real pilot;
- implementation is now authorized only in the frozen files; bootstrap, network, and real Git/task
  lifecycle mutation remain unauthorized.

Confirmed by repository:

- v1 governance and three local scripts cover parts of the lifecycle;
- `connlab-controlled-lane` does not exist;
- no machine registry, owner engine, idempotent dispatch journal, or tests exist;
- current Git baseline and retained TASK_367A topology match the task;
- native Codex task tools exist at runtime but are not a repository-level deterministic contract.

Planner inference:

- the deterministic core should be a standard-library Python package with stable JSON I/O;
- native Codex task tools should be an adapter invoked by the skill, not by repository code;
- the operational registry belongs under Git common-dir, not in committed product/config data;
- accepted post-integration issues require a new corrective lane rather than reopening history.

Authorized by the current implementation gate:

- implementing the exact frozen skill/helper/protocol hooks and bounded tests.

Still not authorized:

- creating `ConnLab｜研发任务编排与集成主控 v2`;
- creating a heartbeat or short-lived role tasks;
- adopting or retiring legacy topology;
- executing the real pilot.

## 2. Existing Capability Inventory

| Existing item | Reuse | Gap |
|---|---|---|
| `connlab-lane-orchestrator` skill | role order, prompts, one-action callback rule | prose-only state; no registry/idempotency/owner engine |
| `LANE_ORCHESTRATION_PROTOCOL.md` | approval and role authority | no machine transition schema or recovery journal |
| `PARALLEL_EXECUTION_MODEL.md` | lane fields and role locks | board table is not an operational registry |
| `PARALLEL_LANE_OPERATIONS_GUIDE.md` | hygiene and residual model | no deterministic enforcement |
| `ROLE_THREAD_REGISTRY.md` | v1 static role IDs | no lane-scoped short-lived task lifecycle |
| `run_task.ps1` | user CLI entry and read-only snapshot | no structured output/state; invokes broad CLI runtime |
| `connlab_lane_worktree.ps1` | clean create/inspect/non-force retire | no JSON, dry-run, adopt, registry, idempotency |
| `task_complete_commit.ps1` | exact-path local lane commit | no mixed-hunk support by design; sufficient read-only reuse |
| native task tools | list/read/send/create/rename/archive and heartbeat | runtime-only; calls require skill policy and durable journal |

Security finding:

- `_codex_runtime.ps1` copies `auth.json` and `config.toml` into ignored repository `tmp/**`.
  V2 must not use or extend this path. Native app task tools are the only planned task adapter.

## 3. Architecture

```text
User product goal
  -> controlled-lane skill
  -> deterministic helper scan/route plan
  -> board/task/evidence + local registry consistency
  -> prepared journal CAS
  -> exactly one native task or local Git action
  -> result/sent CAS
  -> independent dispatch acknowledgement CAS
  -> state advance CAS
  -> later role-completion callback
  -> next scan
```

Authority order:

1. `AGENTS.md`;
2. `docs/task_board.md`;
3. task/plan/evidence;
4. Git refs/worktrees/index;
5. operational registry;
6. callback/thread summaries.

The registry never upgrades a planned lane to authorized and never overrides repository
governance.

## 4. Modules And Responsibilities

1. `contracts.py`
   - enums, immutable request/result records, canonical JSON, error codes.
2. `registry.py`
   - schema validation, exclusive lock, generation CAS, atomic replace, v2 load, and a pure
     synthetic v1-to-v2 converter that is not executed against the real topology in this lane.
3. `ownership.py`
   - Windows-safe path normalization, directory/path/authority overlap and owner release.
4. `state_machine.py`
   - legal transitions, role routing, fix-loop and scope-expansion stops.
5. `git_preflight.py`
   - read-only Git facts, primary/index/worktree/ref/ancestry/package checks.
6. `callbacks.py`
   - callback parse/digest, duplicate/conflict handling, and
     prepared/result-or-sent/acknowledged/advanced dispatch journal.
7. `cli.py`
   - stable JSON CLI; no native task API, no remote operation.
8. `connlab_controlled_lane.ps1`
   - thin Windows entry, explicit UTF-8, preserves helper exit code.
9. `connlab-controlled-lane` skill
   - reads helper output, invokes exactly one approved native task/Git action, writes evidence
     through the current role, then stops.

## 5. Registry And Concurrency

Registry:

```text
<git-common-dir>/connlab-controlled-lane/registry-v2.json
<git-common-dir>/connlab-controlled-lane/registry-v2.lock
```

Write protocol:

1. open exclusive lock;
2. reread and validate schema/generation;
3. apply one validated transition;
4. write UTF-8 canonical JSON to adjacent temporary file;
5. flush and atomically replace;
6. reread and verify generation/digest;
7. release lock.

No silent TTL releases. Owner release requires integrated commit and residual ledger.

### 5.1 CAS Command Surface

Read-only commands are `scan`, `route-plan`, all Git preflights, `registry-status`, and
`recover`. `route-plan` never mutates the registry or performs an external action.

The only registry mutation commands are:

| Command | Required stage/input | Sole durable effect |
|---|---|---|
| `prepare-dispatch` | expected generation, idempotency/operation/route IDs, current state, action kind, canonical payload and scope digests | append one `prepared` dispatch |
| `mark-invocation-started` | expected generation and exact prepared dispatch | append the durable `invocation_started` marker immediately before the one external call |
| `record-action-result` | expected generation, exact prepared dispatch and external result digest | record `sent` for native task/message or `result_recorded` for Git/worktree |
| `record-callback` | expected generation, role-completion event ID, acknowledged/advanced target-role route, evidence/status/HEAD digests | append/deduplicate one `role_completion_callback` and mark only that role binding `completion_recorded`; never acknowledge dispatch or regress lane state |
| `ack-dispatch` | expected generation, exact result plus native tool receipt and exact target-thread read-back, or exact post-Git observation | append one independent `dispatch_ack` and record `acknowledged` |
| `advance-state` | expected generation, acknowledged dispatch and exact legal from/to states | change lane state and record `advanced` |

All mutation inputs include `task_id`, `lane_id`, `expected_registry_generation`,
`idempotency_key`, `operation_id`, `route_id`, `scope_fingerprint`, and canonical payload digest.
Each successful first write increments generation once and returns old/new generation, durable
stage, and stored digest. Same key plus identical canonical input returns `CTL_ALREADY_APPLIED`
without another write. Same key plus changed input returns `CTL_IDEMPOTENCY_CONFLICT`. Stale
generation returns `CTL_CAS_CONFLICT`. Wrong stage returns `CTL_DISPATCH_STAGE_MISMATCH`.

`mark-invocation-started` has its own direct command contract and test matrix. It accepts only the
exact `prepared` stage and writes only the durable invocation-start marker; it never invokes a
native task API or Git mutation. Its first write increments generation by one. Identical canonical
`operation_id`, `route_id`, idempotency key, and payload replay returns
`CTL_ALREADY_APPLIED` with no generation change. Stale expected generation returns
`CTL_CAS_CONFLICT`; changed payload or reused key returns `CTL_IDEMPOTENCY_CONFLICT`; any
non-`prepared` source stage returns `CTL_DISPATCH_STAGE_MISMATCH`. Every failure and replay is
zero-external-action.

`dispatch_ack` and `role_completion_callback` are different event types:

- dispatch acknowledgement key hashes route/operation/action, frozen target
  thread/worktree/lane identity, tool receipt digest, and read-back/observation digest;
- role completion key is the callback event ID derived from role, status, evidence digest, and
  lane HEAD;
- native acknowledgement allows only receipt and exact target binding/read-back fields;
- role completion allows only role/status/evidence/HEAD/blocker fields and requires the target
  role dispatch already acknowledged and advanced.

Exact duplicate replay returns the stored event with `CTL_ALREADY_APPLIED`. Changed content under
one key returns `CTL_IDEMPOTENCY_CONFLICT`. Wrong native target/read-back returns
`CTL_DISPATCH_ACK_MISMATCH`; early, stale, regressive, or consumed completion returns
`CTL_ROLE_CALLBACK_STATE_MISMATCH`. A role completion callback cannot acknowledge or re-advance
its task/message dispatch.

The helper may write only the registry and journal under the approved Git-common-dir directory.
It never writes product/governance files and never invokes native task or Git mutation itself.
The skill/controller performs the one prepared external action.

### 5.2 External Action And Recovery Protocol

Required order:

```text
prepare-dispatch
  -> mark-invocation-started
  -> one external side effect
  -> record-action-result/sent
  -> collect native receipt + exact target read-back proof, or exact post-Git observation
  -> ack-dispatch
  -> advance-state
  -> stop
```

Role completion is a later independent `record-callback` event. It may authorize planning the next
route but is never dispatch acknowledgement.

Crash recovery:

| Durable observation | Only legal recovery |
|---|---|
| nothing prepared | recompute authoritative facts and prepare once |
| prepared, invocation durably not started | retry the same operation ID only when pre-invocation journal state plus absence of any invocation-start marker/tool-call attempt is durably verified; target-history zero-match alone is never proof |
| native invocation may have started, receipt missing | read back the frozen target; adopt exactly one route/operation match; zero, multiple, wrong-target, or unreadable results return `CTL_RECOVERY_REQUIRED` without another create/send |
| exact external side effect, no stored result | adopt exactly one matching route/task or branch/path/base/scope tuple and record it |
| native receipt/result, no dispatch acknowledgement | exact target read-back then `ack-dispatch`; do not wait for role completion and do not resend |
| Git result, no dispatch acknowledgement | bind only exact post-Git observation; do not repeat action |
| acknowledged, not advanced | run only `advance-state` with generation CAS |
| advanced, no role completion | remain in active/pending role state; do not recreate/resend |
| consumed role completion replayed | return `CTL_ALREADY_APPLIED`; do not regress or repeat advance |

Native task creation and message dispatch embed immutable `route_id` and `operation_id`. Once
invocation may have started, exactly one target read-back match is adoptable; zero, multiple, or
ambiguous matches fail closed and never resend; wrong-target and unreadable results do the same.
A returned tool receipt that was not acknowledged is completed by exact target read-back and
`ack-dispatch`. Worktree/branch recovery additionally requires an exact clean
base/path/branch/scope match. Missing target topology after possible invocation is not
pre-invocation proof. Registry loss, partial Git topology, mismatch, or inability to prove
identity returns `CTL_RECOVERY_REQUIRED`; no deletion, force removal, new operation ID, duplicate
create, or duplicate send is allowed.

## 6. State And Role Routing

| State | Required proof | One legal next action |
|---|---|---|
| `planned` | task/plan/Planner evidence | Reviewer plan gate |
| `plan_review_pending` blocked | exact Reviewer plan findings | route same Planner to `planner_fix_pending` |
| `planner_fix_pending` | docs-only correction evidence | Reviewer plan re-gate |
| `plan_review_pending` pass | Reviewer plan pass | User approval request |
| `user_approval_pending` | explicit approval recorded | authorization reconciliation |
| `authorized` | clean primary/index, exact saved project/start ref/base/scope, no owner conflict | prepare and invoke one native Developer task+worktree create action |
| `developer_environment_pending` | durable native receipt/pending ID; no complete adopted identity yet | observe completion/read-back only; never create again |
| `developer_active` | clean checkpoint + Developer evidence | Reviewer implementation gate |
| `review_pending` blocked | exact findings | same Developer task fix pass |
| `developer_fix_active` | same worktree checkpoint + fix evidence | Reviewer implementation re-gate |
| `review_pending` pass, QA default | reviewed immutable HEAD | QA task |
| `review_pending` pass, explicit no-QA | user-approved `qa_required: false` plus Reviewer confirmation | Integrator task |
| `qa_pending` blocked, attributed/in-scope/bounded | exact QA evidence and unchanged approved scope | one route to the same Developer task/worktree as `developer_fix_active` |
| `qa_pending` blocked, scope expansion | changed behavior/May Touch/authority proof | Planner/User reconciliation; no Developer product route |
| `qa_pending` blocked, external/unattributed | external or ambiguous evidence | `paused_conflict`; fail closed |
| `qa_pending` pass | isolated validation evidence | Integrator task |
| `integration_pending` accepted | commit integrated + ledger | governance closeout |
| `closeout_pending` | committed closeout + clean lane/primary | non-force retire |
| `retired` | no pending callback/recovery | archive short-lived role tasks |

`authorized -> developer_environment_pending` contains exactly one native create tool side effect
that returns two coupled resources. A later scan may observe asynchronous completion and atomically
bind the complete actual identity before `developer_active`. No scan performs a second create.
Reviewer implementation/QA fixes reuse the existing Developer task and worktree. QA remains
mandatory unless both the approved task contract and Reviewer evidence explicitly confirm no-QA.
An attributed bounded QA fix always returns through `review_pending` for Reviewer re-gate before
QA resumes; it never routes directly to Integrator. Any missing proof yields one blocker result
and no route.

### 6.1 Option A Native Contract

The User selected Option A. The canonical prepare payload freezes only facts known before native
creation:

```text
route_id
operation_id
idempotency_key
client_request_digest
task_id / lane_id / role=Developer
saved_project_id + canonical project path + repository fingerprint
environment=worktree
starting_state.type=branch
starting_state.branchName=<frozen clean integration ref>
expected_base_commit / expected_primary_head
scope_digest / provisional owner intent
immutable prompt digest with route and operation markers
```

Unknown `thread_id`, `pendingWorktreeId`, worktree path, and actual native branch are forbidden in
prepare. The native API has no separate idempotency parameter; the durable journal and immutable
route/operation prompt markers are the canonical client request identity.

After `mark-invocation-started`, exactly one `create_thread` call is allowed. The raw receipt is
recorded without interpretation. An immediate thread ID or asynchronous pending-worktree ID moves
the lane to `developer_environment_pending`; it is not an adopted Developer binding. Later
read-back must resolve every actual identity:

```text
thread_id
pending_worktree_id when issued
canonical_worktree_path
actual_branch_ref
base_commit
actual_head
saved_project_id / project path / repository fingerprint
task_id / lane_id / role markers
scope_digest / exact owner claim
```

One expected-generation `ack-dispatch` mutation atomically stores the complete binding and
dispatch acknowledgement. `advance-state` may then enter `developer_active`; it cannot fill or
change identity fields. Partial identity, stale generation, changed request digest, or mismatched
read-back cannot advance.

`pendingWorktreeId` is an asynchronous receipt, not resend authority. A known still-pending result
returns existing `CTL_NO_ACTION` (exit 0) with typed facts
`native_worktree_status=pending`, exact route/operation/pending ID, `retry_allowed=false`, and
`adopted=false`; it preserves `developer_environment_pending` with zero write. No new code or exit
class is added to the authoritative 39-code catalog. Receipt loss
after possible start, authoritative zero completion, multiple/wrong/partial/unreadable read-back,
or terminal setup ambiguity returns `CTL_RECOVERY_REQUIRED`; never resend, create, adopt, or
clean. Canonical replay returns the stored pending/adopted result without generation drift.

Before adoption, validate unchanged primary/index authority, exact saved project/repository,
unique canonical path, actual non-primary/non-detached branch, expected committed base and
ancestry, exact HEAD, clean worktree/index, immutable prompt markers, scope, and shared owners.
Option A permits a native-generated `codex/*` physical branch or native-returned `lane/*` branch;
the registry owns the logical lane-to-actual-branch mapping. Any other branch, checkout collision,
owner conflict, or topology mismatch fails closed.

Short-lived Reviewer and QA tasks use their own one-action native worktree creation from the exact
clean committed lane branch/HEAD and are read-only. They never bind the Developer path. Integrator
uses the saved clean primary project only after integration authority. Reviewer/QA fixes send one
message to the same Developer task/worktree and return through immutable review/QA gates.

B11 uses the existing `record-callback` mutation. Prepare/adoption freezes role, active gate,
evidence path, and input HEAD only; a final evidence digest or completion HEAD cannot exist yet.
Within one expected-generation callback CAS, the helper verifies the adopted target and gate,
reads the exact evidence under that worktree, recomputes SHA-256, reads actual completion HEAD,
compares payload path/digest/HEAD, checks ancestry/currentness, and atomically stores callback plus
observed completion authority. Any mismatch is zero-write. A normal evidence update and clean
post-dispatch commit passes; pre-dispatch digest/HEAD, tamper, late/consumed, cross-gate/role/lane,
wrong path/HEAD, and stale CAS fail closed.

B12 permits one provisional-to-exact same-lane identical owner materialization and canonical
identical replay with no generation drift. Same-lane changed key/content/path/directory/
authority/branch/worktree is a zero-write conflict and never overwrites; cross-lane overlap remains
`CTL_OWNER_CONFLICT`. Both remain open for the same Developer after scope approval and Reviewer
re-gate.

## 7. Manual Smoke Decision Table

| Timing / finding | Classification | Action |
|---|---|---|
| before integration, same contract/scope | `active_lane_bounded_fix` | same Developer/worktree |
| before integration, scope or behavior changes | `scope_expansion` | Planner then User |
| after integration/acceptance | `corrective_lane` | new lane from exact current master |
| unknown origin or ambient-only repro | `unattributed` | fail closed, preserve state |

## 8. File-Level Implementation Order

1. Add contracts/state-machine/ownership tests and RED fixtures.
2. Implement `contracts.py`, `state_machine.py`, and `ownership.py`.
3. Add registry concurrency/atomicity tests, then implement `registry.py`.
4. Add disposable Git preflight tests, then implement `git_preflight.py`.
5. Add callback/idempotency/recovery tests, then implement `callbacks.py`.
6. Add CLI and PowerShell wrapper tests, then implement adapters.
7. Add JSON/dry-run/adopt hooks to `connlab_lane_worktree.ps1`.
8. Add the v2 skill and protocol/AGENTS compatibility hooks.
9. Run full zero-write dry-run suite.
10. Reviewer, QA, and Integrator accept the automation implementation.
11. Stop for separate bootstrap approval.

No step creates the v2 controller or operates on TASK_367A.

## 9. Exact Future May Touch

Skill/governance:

- `.agents/skills/connlab-controlled-lane/SKILL.md`;
- `.agents/skills/connlab-controlled-lane/agents/openai.yaml`;
- `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`;
- exact v2 hooks in `AGENTS.md`,
  `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`, and
  `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`.

Helpers:

- `scripts/connlab_controlled_lane.ps1`;
- `scripts/connlab_controlled_lane/{__init__,contracts,registry,ownership,state_machine,git_preflight,callbacks,cli}.py`;
- User-authorized B16 additions:
  `scripts/connlab_controlled_lane/native_environment.py` and
  `scripts/connlab_controlled_lane/completion_authority.py`;
- exact JSON/dry-run/adopt hooks in `scripts/connlab_lane_worktree.ps1`;
- exact v2 delegation hunk in `scripts/run_task.ps1`.

Tests:

- the eight bounded test modules named in the task;
- User-authorized B16 additions:
  `tests/unit/test_connlab_controlled_lane_native_environment.py` and
  `tests/unit/test_connlab_controlled_lane_completion_authority.py`.

Governance for this lane:

- this plan, task, Planner/Developer/Reviewer/QA/Integrator evidence, and exact board hunks.

## 10. Locked Paths

- all product/backend/frontend/API/schema/database/business tests;
- v1 role tasks and TASK_367A topology;
- `ROLE_THREAD_REGISTRY.md` until bootstrap authorization;
- `_codex_runtime.ps1`, credential files, real data and generated artifacts;
- remote refs/network;
- destructive Git/filesystem and any task archival.

## 11. Line Budgets

- Every Python module: hard `<500`, planned maximum `<=450`.
- Skill/protocol: `<=500`.
- PowerShell worktree helper after exact hooks: `<=350`.
- PowerShell v2 adapter and `run_task.ps1`: `<=180`.
- Tests: `<=450`, with smaller module-specific limits in the task.
- No blank-line suppression or generated monolith.

## 12. TDD Matrix

### State And Authorization

- planned cannot route Developer;
- Reviewer pass cannot replace explicit User approval;
- invalid/skipped transition fails closed;
- one callback causes one route only;
- same Reviewer blocker returns to the same Developer binding.

### Ownership

- exact path, directory ancestor/descendant, case variation, slash variation;
- authority exact/ancestor conflict;
- unrelated scopes parallel-safe;
- repo escape/glob rejected;
- board mutation rejected for Developer;
- unknown worktree/branch blocks.

### Idempotency And Recovery

- duplicate callback and duplicate route no-op;
- every CAS mutation rejects stale generation and changed-payload key reuse;
- duplicate replay for all six commands - `prepare-dispatch`, `mark-invocation-started`,
  `record-action-result`, `record-callback`, `ack-dispatch`, and `advance-state` - returns the
  stored result without a second mutation;
- direct `mark-invocation-started` tests cover first-write generation `+1`, identical replay with
  no generation increment, stale generation, changed payload/key reuse, wrong stage, and zero
  external action;
- crash tests cover after prepared, after external side effect, after result/sent, after
  acknowledgement, and after advance; crash-at-`invocation_started` and possible-start/no-resend
  are separate integration tests rather than substitutes for direct command coverage;
- unseeded Option A create proves prepare contains no invented thread/path/actual-branch identity,
  exactly one fake native create returns a coupled task/worktree receipt, and the lane enters
  `developer_environment_pending`;
- immediate and delayed pending-worktree completion prove the same operation is observed and
  atomically adopted with no second create;
- partial identity and wrong thread, pending ID, path, branch policy, project, base, HEAD, lane,
  role, prompt digest, scope, or owner fail closed before `developer_active`;
- duplicate receipt/read-back replay returns the stored pending or adopted result without a
  generation increment; stale generation and changed client request identity remain conflicts;
- crash tests separately cover create returning before result persistence, pending ID persisted
  before completion, complete read-back before acknowledgement, acknowledgement before advance,
  and completion callback after `developer_active`;
- native branch/path uniqueness, primary/index drift, wrong ancestry, dirty worktree, checkout
  collision, and exact/directory/authority owner conflict all reject adoption without cleanup;
- native create/send with receipt but no acknowledgement is acknowledged from exact target
  read-back before role completion;
- receipt-lost native create/send found exactly once in target history is adopted, not resent;
- zero, multiple, wrong-thread, wrong-worktree, or wrong-lane read-back fails closed without
  create/send retry;
- durable pre-invocation journal proof permits same-ID retry; target-history zero-match alone does
  not, and possible-start plus zero/multiple/wrong/unreadable always fails closed;
- stale-contract scan rejects any unconditional zero-match retry statement;
- role completion arrives later as a separate event and cannot acknowledge, regress, or repeat
  the dispatch state transition;
- Git-created/registry-missing exact worktree is safely adopted;
- mismatched partial worktree returns recovery-required;
- registry generation conflict and lock contention fail closed;
- atomic-write interruption keeps prior valid registry.

### One-Action Routing

- `authorized` prepares/invokes one native Developer task+worktree create;
- `developer_environment_pending` performs completion observation/adoption only and never creates;
- acknowledged Developer-task dispatch reaches `developer_active` without waiting for Developer
  completion callback;
- Reviewer plan blocked returns to the same Planner docs-only task;
- Reviewer implementation blocked and attributed QA blocked return to the same Developer/worktree;
- attributed QA fix requires bounded in-scope evidence and Reviewer re-gate before QA resumes;
- QA scope expansion routes Planner/User; external/unattributed QA blockers fail closed;
- default Reviewer pass creates QA;
- Reviewer pass creates Integrator directly only for explicit user-approved and
  Reviewer-confirmed `qa_required: false`;
- one callback never advances through two external actions.

### Git Hygiene

- dirty primary/index prevents create;
- branch/path/base mismatch prevents adopt;
- dirty/unintegrated worktree prevents retire;
- clean integrated worktree passes;
- forbidden remote/destructive actions are rejected;
- exact whitelist and residual ledger required before closeout.

### Thread Lifecycle

- no duplicate Developer task;
- Reviewer/QA receive immutable commit/archive;
- archive blocked before worktree retirement and callback drain;
- archival failure leaves `closeout_pending`, without Git rollback.

## 13. Verification Commands

Future implementation gate:

```powershell
py -m pytest tests/unit/test_connlab_controlled_lane_contracts.py `
  tests/unit/test_connlab_controlled_lane_registry.py `
  tests/unit/test_connlab_controlled_lane_ownership.py `
  tests/unit/test_connlab_controlled_lane_state_machine.py `
  tests/unit/test_connlab_controlled_lane_callbacks.py `
  tests/unit/test_connlab_controlled_lane_git_preflight.py `
  tests/unit/test_connlab_lane_worktree_script.py `
  tests/integration/test_connlab_controlled_lane_dry_run.py -q
```

Also:

- Python compile for every new helper;
- PowerShell parser for both scripts;
- `git diff --check`;
- UTF-8/trailing/line-budget/scope/forbidden-command scans;
- disposable Git-only integration;
- primary/index/worktree/branch preservation.

No real product tests, real DB/file access, network, or real lane creation belongs to the
implementation dry-run.

## 14. Bootstrap Contract

After automation implementation acceptance, a separate User-approved bootstrap task must:

1. verify clean/equal primary refs and zero recovery points;
2. create `ConnLab｜研发任务编排与集成主控 v2` project-bound to ConnLab;
3. register its ID without renaming/archiving v1;
4. propose, review, and explicitly enable one heartbeat;
5. import legacy topology read-only;
6. run zero-write dry-run;
7. request the real pilot gate.

The v2 controller receives only the minimum permissions in the task. It never receives remote
push, destructive Git, credential-copy, real-data, or implicit approval authority.

## 15. Pilot Acceptance

The real tests-only pilot passes only if:

- the exact lane is created once from current master;
- one Developer task/worktree is reused through any fix;
- Reviewer and QA use immutable clean input;
- Integrator creates an exact local accepted commit and residual ledger;
- primary and lane indexes are clean;
- worktree/branch retire non-force;
- short-lived tasks archive only after retirement;
- replayed callback/heartbeat produces `CTL_ALREADY_APPLIED`;
- no push/network/product/real-data action occurs.

Any failure pauses v2 and keeps v1 and all topology intact.

## 16. V1 Migration / Rollback

Migration order is exactly:

```text
v2 implementation accepted
-> bootstrap approved
-> v2 controller registered beside v1
-> legacy topology imported read-only
-> zero-write dry-run
-> real tests-only pilot
-> callback/recovery drain
-> explicit legacy retirement approval
-> TASK_367A non-force retirement
-> short-lived task archival
-> old controller/role archival last
```

Rollback pauses v2, preserves registry/evidence, freezes active lanes, and routes back to v1.
No automatic delete/reset/restore/clean occurs.

## 17. Developer Planning-First Implementation Freeze

### 17.1 Exact Future Ownership

| Path | Future owner and exact responsibility | Locked adjacent behavior |
|---|---|---|
| `scripts/connlab_controlled_lane/contracts.py` | JSON request/result/event dataclasses, canonicalization, stable codes | no Git, registry, task API, or policy I/O |
| `scripts/connlab_controlled_lane/registry.py` | v2 schema, lock, expected-generation CAS, atomic replace, pure v1 conversion | no role routing or external action |
| `scripts/connlab_controlled_lane/ownership.py` | canonical repo/path/branch/scope identities and overlap decisions | no owner acquisition write outside registry CAS |
| `scripts/connlab_controlled_lane/state_machine.py` | pure transition table and unique next-action selection | no evidence/Git mutation |
| `scripts/connlab_controlled_lane/git_preflight.py` | read-only Git facts and create/adopt/retire/integrate decisions | no fetch, push, force, clean, reset, restore, or remove |
| `scripts/connlab_controlled_lane/callbacks.py` | callback attribution, journal transition validation, replay decisions | no native task API |
| `scripts/connlab_controlled_lane/cli.py` | command parsing, one helper call, one JSON response | no hidden default mutation |
| `scripts/connlab_controlled_lane.ps1` | UTF-8 thin launcher preserving stdout/stderr/exit code | no credential/config copy |
| `scripts/connlab_lane_worktree.ps1` | exact JSON, dry-run, and adopt hooks only | existing non-force behavior remains |
| `scripts/run_task.ps1` | exact v2 delegation entry only | `_codex_runtime.ps1` remains unused and locked |
| `.agents/skills/connlab-controlled-lane/SKILL.md` | the only native task API adapter and one-action executor | no credential copy or implicit approval |
| `.agents/skills/connlab-controlled-lane/agents/openai.yaml` | bounded skill metadata only | no secrets or topology |
| `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md` | public machine-contract reference | no live registry data |
| `AGENTS.md`, `LANE_ORCHESTRATION_PROTOCOL.md`, `PARALLEL_LANE_OPERATIONS_GUIDE.md` | exact compatibility hooks after implementation approval | no broad rewrite |
| eight task-listed test modules | bounded unit/contract/disposable integration coverage | no existing product-test edits |

`ROLE_THREAD_REGISTRY.md`, the current orchestrator skill, `task_complete_commit.ps1`, all product
paths, all existing product tests, and the TASK_367A topology remain read-only. If implementation
proves a missing path, it stops for Planner re-scope rather than borrowing an adjacent file.

### 17.2 Deterministic CLI Contract

The PowerShell entry is:

```powershell
.\scripts\connlab_controlled_lane.ps1 `
  -Command <command> `
  -RequestJson <path-or-> `
  [-RegistryRoot <disposable-test-root>] `
  [-DryRun]
```

It delegates to:

```text
py -m scripts.connlab_controlled_lane.cli
  <command>
  --request-json <path-or->
  [--registry-root <path>]
  [--dry-run]
```

Production derives the registry root from `git rev-parse --git-common-dir`; a caller-supplied root
is accepted only under an explicit test flag. Standard output contains exactly one UTF-8 JSON
result. Diagnostics use stderr. Input and output use schema version 2, sorted keys, compact
separators, LF, and SHA-256 over the canonical UTF-8 bytes.

Common request fields are:

```text
schema_version, command, request_id, repo_root, task_id, lane_id,
expected_registry_generation, idempotency_key, operation_id, route_id,
scope_fingerprint, payload, payload_digest, dry_run
```

Common result fields are:

```text
schema_version, ok, code, message, request_id, command, task_id, lane_id,
zero_write, old_generation, new_generation, operation_id, route_id,
state, durable_stage, record_digest, facts, conflicts, recovery, next_action
```

`next_action` is either null or one object with `kind`, `target_role`, frozen thread/worktree
binding, required proof digests, and one canonical payload. Read-only commands are `scan`,
`route-plan`, `registry-status`, `recover`, `worktree-preflight`, `integration-preflight`, and
`retire-preflight`. Mutation commands are the six commands in section 5.1.

Stable exit classes are:

| Exit | Codes |
|---|---|
| 0 | `CTL_OK`, `CTL_DRY_RUN`, `CTL_NO_ACTION`, `CTL_ALREADY_APPLIED` |
| 2 | `CTL_INVALID_REQUEST`, `CTL_SCHEMA_UNSUPPORTED`, `CTL_REGISTRY_SCHEMA_MISMATCH`, `CTL_PAYLOAD_DIGEST_MISMATCH` |
| 3 | `CTL_CAS_CONFLICT`, `CTL_IDEMPOTENCY_CONFLICT`, `CTL_DISPATCH_STAGE_MISMATCH`, `CTL_CALLBACK_CONFLICT`, `CTL_ROLE_CALLBACK_STATE_MISMATCH` |
| 4 | `CTL_AUTHORIZATION_REQUIRED`, `CTL_LANE_NOT_AUTHORIZED`, `CTL_INVALID_TRANSITION`, `CTL_SCOPE_CONFLICT`, `CTL_SCOPE_VIOLATION`, `CTL_OWNER_CONFLICT`, `CTL_EVIDENCE_STALE`, `CTL_THREAD_BINDING_MISMATCH`, `CTL_GIT_PRECONDITION_FAILED`, `CTL_PRIMARY_DIRTY`, `CTL_INDEX_NOT_EMPTY`, `CTL_HEAD_MISMATCH`, `CTL_WORKTREE_MISMATCH`, `CTL_WORKTREE_DIRTY`, `CTL_UNINTEGRATED_HEAD` |
| 5 | `CTL_RECOVERY_REQUIRED`, `CTL_TOPOLOGY_STALE`, `CTL_DISPATCH_ACK_MISMATCH`, `CTL_NATIVE_READBACK_AMBIGUOUS` |
| 6 | `CTL_REGISTRY_LOCKED`, `CTL_LOCK_BUSY`, `CTL_ATOMIC_WRITE_FAILED`, `CTL_POST_WRITE_VERIFY_FAILED`, `CTL_GIT_FAILED` |
| 7 | `CTL_REMOTE_FORBIDDEN`, `CTL_DESTRUCTIVE_FORBIDDEN` |

Option A pending setup deliberately reuses `CTL_NO_ACTION`; its typed `facts` distinguish pending
native setup from ordinary no-route results. `contracts.py`, the 39-code assertion, and all exit
classes remain unchanged.

No message text is used for branching; only the stable code and typed fields are authoritative.

### 17.3 Registry V2, Locking, And Migration

The root registry schema contains:

```text
schema_version=2, registry_id, repository_fingerprint, git_common_dir_fingerprint,
generation, created_at, updated_at, migration, lanes, worktrees, shared_owners,
role_bindings, dispatches, callbacks, recovery_points
```

Each lane stores its task/lane identity, governance authorization digests, state, QA policy,
base/branch/worktree binding, owner set, active dispatch, accepted commit, residual ledger, and
closeout state. Each owner key is a typed canonical tuple (`path`, `authority`, `worktree`, or
`governance`) and records lane, scope digest, acquisition generation, and release proof.

The lock is an exclusive-create file containing a random token, PID, host fingerprint, registry
generation, and timestamp. Only the matching token removes it. There is no TTL auto-break; stale
or unreadable ownership returns `CTL_LOCK_BUSY` or `CTL_RECOVERY_REQUIRED`.

One write performs: acquire lock; reread; validate schema and expected generation; validate one
transition; write an adjacent operation-scoped temporary file; flush and `fsync`; `os.replace`;
reread and verify generation/digest; release the matching lock. A pre-replace failure removes only
its own temporary file. A post-replace verification failure preserves files and records recovery;
it never guesses or rewrites.

The implementation may test a pure v1-to-v2 converter but may not migrate the real topology.
Synthetic migration order is:

```text
validate immutable v1 bytes and generation
-> build v2 candidate in memory
-> attach source_schema_version/source_digest/source_generation/converter_version/migration_id
-> validate identities, owners, dispatch stages, and generation
-> write disposable v2 candidate
-> reread exact digest
-> mark migration verified/committed in one final CAS
```

The real `registry-v2.json` creation, v1 import, and schema activation remain separate User gates.
V1 is never overwritten. If v1 and v2 coexist without an explicitly committed migration marker,
the helper returns `CTL_RECOVERY_REQUIRED`.

### 17.4 Dispatch Journal And Replay

All journal records bind `schema_version`, task/lane, repository, route, operation, idempotency,
scope, frozen role/thread/worktree/branch/base/HEAD, payload digest, actor role, registry
generation, timestamps, and record digest.

| Event | Required fields and precondition | Durable result |
|---|---|---|
| `dispatch_prepare` | legal current state, unique route/operation, authorized action, frozen target and payload | `prepared` |
| `invocation_start` | exact prepared record and same generation CAS | `invocation_started`; external call may now occur |
| `action_result` | invocation marker plus native receipt or exact Git observation | `sent` or `result_recorded` |
| `dispatch_ack` | exact receipt and target read-back, or exact post-Git observation | `acknowledged` |
| `state_advance` | acknowledged dispatch and legal from/to state | `advanced` and active dispatch cleared |
| `role_completion` | previously advanced role binding, evidence/status/HEAD/blocker digests | completion recorded once; no dispatch acknowledgement |

The executor must persist `invocation_start` immediately before the one native/Git call. A crash
while merely `prepared` can retry the same operation only after durable proof that no invocation
marker exists. A crash after `invocation_started` can never resend from a zero history match:
exactly one matching receipt/read-back is adopted; zero, multiple, wrong, or unreadable matches
fail closed. Duplicate canonical events return the stored record; changed data under an existing
key returns `CTL_IDEMPOTENCY_CONFLICT`.

### 17.5 Complete One-Action State Table

| State/proof | Unique next action |
|---|---|
| `planned` | dispatch Reviewer plan gate |
| Reviewer plan blocked | return the same Planner binding for docs-only fix |
| Reviewer plan passed | request User Developer-planning approval |
| planning approval recorded | dispatch Developer planning-first |
| Developer plan completed | dispatch Planner source-of-truth reconciliation |
| reconciliation completed | dispatch Reviewer implementation-readiness |
| readiness blocked | return the same Developer binding for docs-only planning fix |
| readiness passed | request User product/tests/package implementation approval |
| implementation approval recorded | dispatch Planner final authorization reconciliation |
| `authorized` | invoke one native Developer task+worktree create action |
| `developer_environment_pending` | observe and atomically adopt complete native identity; no create/send |
| Developer implementation completed | dispatch Reviewer implementation gate |
| Reviewer implementation blocked | same Developer task and worktree bounded fix |
| Reviewer passed and QA required | dispatch QA against immutable reviewed commit/archive |
| Reviewer passed and no-QA double proof | dispatch Integrator |
| QA bounded in-scope blocker | same Developer/worktree fix, then Reviewer re-gate |
| QA scope/attribution blocker | Planner reconciliation; no product route |
| QA passed | dispatch Integrator |
| Integrator blocked | route the exact owning role named by attributed evidence |
| Integrator accepted | local governance closeout only |
| closeout committed and clean | non-force worktree retire only |
| retired with drained callbacks/recovery | archive one short-lived task only after separate archive gate |

The unique-next-action algorithm first validates governance authority, then reconciles any active
dispatch/recovery point, then consumes at most one attributed callback, then checks owner/Git
conflicts, and finally selects the first exact state-table action. More than one matching action,
missing proof, stale topology, or ambiguous attribution yields one fail-closed result and no
external action.

Skipping QA requires two independent canonical digests: an explicitly User-approved task contract
with `qa_required=false`, and Reviewer evidence confirming that exact policy for the reviewed
commit. A conversation hint or missing QA section is insufficient.

Manual smoke has exactly three top-level classifications:

1. `active_lane_bounded_fix`: before integration, same accepted scope and attributable owner;
2. `planner_reconciliation_required`: before integration but scope, behavior, ownership, or
   attribution differs or is uncertain;
3. `corrective_lane_required`: after local acceptance/integration, based on current master.

### 17.6 Native Task Adapter

Repository helpers never import or invoke Codex APIs. The skill is the only adapter and may use
native `create_thread`, `fork_thread`, `send_message_to_thread`, read-back/task listing for
adoption, and later separately authorized archive capability. It must not call
`_codex_runtime.ps1`, copy
`auth.json`/`config.toml`, access remote refs, or synthesize a task receipt.

- `create`: Option A creates and later adopts the first Developer task/worktree pair from one
  project-bound native worktree request; it never binds a pre-existing arbitrary path.
- `send`: only to the frozen existing binding with route/operation markers.
- `read-back`: verify thread ID, lane, worktree, route, operation, and immutable payload digest.
- `adopt`: exactly one matching task; zero or multiple matches fail closed after possible start.
- `archive`: only after separate User archive gate, retired worktree, drained callbacks, and clean
  residual ledger.
- `dry-run`: calls no task API and writes no registry; it emits the proposed request and proof list.

Create/send result and later role-completion callback are never conflated.

### 17.7 Worktree And Branch Lifecycle

Canonical worktree identity is:

```text
repository_fingerprint + case-normalized absolute path + lane_id + branch_ref +
base_commit + expected_head + scope_fingerprint
```

Option A prepare requires equal clean primary/origin facts recorded by governance, empty
primary/index, exact saved project/start ref/base, provisional scope owners, and no active
dispatch. Actual native path/branch do not exist in the request. Adoption requires exact common
dir, unique path, non-primary branch, base ancestry, expected HEAD, clean index/worktree,
lane/task/prompt markers, project binding, and scope owners.
Retire requires accepted commit integrated, exact residual ledger, clean lane and primary indexes,
no unique unintegrated commit, released owners, drained callbacks/recovery, and no active task.

Partial outcomes are fail-closed. An exact branch-created/worktree-missing tuple under the same
operation may resume creation; an exact clean worktree-created/registry-missing tuple may be
adopted. Any path/branch/base/HEAD/scope mismatch returns recovery-required. Rollback deletes only
an operation-owned empty temporary directory created before Git registration. There is no force
remove, branch delete, clean, reset, restore, or ambient-directory cleanup.

### 17.8 Bounded TDD And Checkpoints

1. RED pure contract tests: canonical JSON, caps, codes, malformed schemas, v1 converter.
2. RED state/ownership tests: every state row, no-QA double proof, manual-smoke classes, overlap.
3. GREEN contracts/state/ownership helpers.
4. RED registry tests: lock, CAS, atomic replace, interruption, migration markers, replay, and
   direct `mark-invocation-started` first-write/replay/stale/conflict/wrong-stage/zero-action cases.
5. GREEN registry/callback journal.
6. RED disposable Git tests: create/adopt/retire, partial topology, dirty/conflict failure-close.
7. GREEN Git preflight and exact PowerShell hooks.
8. RED fake native-adapter contract tests: create/send/read-back/adopt/archive/dry-run.
9. GREEN skill/CLI/protocol integration with no real native action.
10. Crash tests at prepared, invocation-started, result, ack, completion, and advance boundaries.
11. Disposable tests-only pilot simulation; clean immutable Reviewer/QA archives; no product data.
12. Full static, UTF-8, line, forbidden-path, no-secret, no-network, no-real-data validation.
13. Reviewer, QA, and Integrator implementation gates.
14. Stop for separate bootstrap User gate.

Bootstrap, controller/task creation, automation/heartbeat creation, real worktree creation,
registry migration/import, real pilot, retirement, and archive are independent later User gates.
Implementation acceptance authorizes none of them.

### 17.9 Physical Line Budgets And Split Triggers

| Future file | Maximum |
|---|---:|
| `contracts.py` | 300 |
| `registry.py` | 350 |
| `ownership.py` | 300 |
| `state_machine.py` | 300 |
| `git_preflight.py` | 400 |
| `callbacks.py` | 220 |
| `cli.py` | 350 |
| `__init__.py` | 40 |
| each new Python test | task-listed cap, never above 450 |
| `connlab_controlled_lane.ps1` | 180 |
| `connlab_lane_worktree.ps1` final | 350 |
| `run_task.ps1` final | 180 |
| skill and v2 protocol | 500 each |
| skill metadata | 80 |
| AGENTS/protocol/operations hooks | 40/80/60 additions |

Counts use `(Get-Content <path> -Encoding UTF8).Count`, including blank lines. At 80 percent of a
budget, or when a file acquires a second I/O responsibility, implementation stops and splits along
the ownership table; it never suppresses blank lines or moves logic into oversized legacy files.

### 17.10 B16 Mandatory Bounded Split

Current blank-inclusive facts are `ownership.py=239/300`, `state_machine.py=239/300`,
`cli.py=279/350`, registry/state/callback tests `319/400`, `318/400`, and `239/300`.
They have only 1-4 lines before the 80-percent split trigger, so B10-B12 cannot be added honestly
inside the 30-path package.

The User approved these four exact bounded paths:

- `scripts/connlab_controlled_lane/native_environment.py`, cap 300, final <=220;
- `scripts/connlab_controlled_lane/completion_authority.py`, cap 240, final <=180;
- `tests/unit/test_connlab_controlled_lane_native_environment.py`, cap 300, final <=230;
- `tests/unit/test_connlab_controlled_lane_completion_authority.py`, cap 260, final <=200.

The frozen package is exactly 34 paths. Native-environment owns B10 pure request, receipt, pending,
and complete-adoption decisions; completion-authority owns B11 evidence/HEAD observation and
comparison for `record-callback`. B12 stays in ownership plus its existing bounded test. The four
files stayed uncreated through the combined Reviewer re-gate and may now be created only by the
same Developer within these frozen responsibilities and budgets.

| Existing file | Current | Final maximum | 80% trigger |
|---|---:|---:|---:|
| `ownership.py` | 239 | 235 | 240 |
| `state_machine.py` | 239 | 230 | 240 |
| `cli.py` | 279 | 270 | 280 |
| `registry.py` | 276 | 276 | 280 |
| `callbacks.py` | 166 | 170 | 176 |
| registry test | 319 | 315 | 320 |
| state-machine test | 318 | 310 | 320 |
| callback test | 239 | 235 | 240 |
| ownership test | 146 | 220 | 280 |

These budgets require deletion/replacement of superseded two-step resource creation, preseeded
Developer target, and pre-dispatch final completion-authority code/tests. No blank-line
suppression, multiple-statement compaction, or semantic coverage loss is permitted.

Validation includes exact pytest nodes, `py -m py_compile`, PowerShell parser checks,
`git diff --check`, UTF-8 trailing scan, physical counts, exact whitelist and forbidden-path scan,
secret/credential-copy scan, no-real-data scan, `git diff --cached --name-only`, and worktree/ref
topology comparison. Rollback before activation removes only the unactivated new package/tests and
exact compatibility hunks from the isolated implementation branch.

### 17.11 Preserved Baseline

At this planning checkpoint:

- `HEAD`, `master`, and `origin/master` are
  `6767a3ae4116185d8ed27b53cfdc050975efce2e`; origin delta is `0/0`;
- primary index is empty;
- TASK_367A branch `lane/task-367a-matrix-editor-live-xlsx-export`, worktree
  `C:\Users\White\.codex\worktrees\705b\connlab`, and task
  `019f9c46-d3be-7c72-bafd-5412a054cfa8` remain preserved;
- Planner, Developer, Reviewer, QA, Integrator, and current Orchestrator tasks remain present;
- this pass creates no branch, worktree, task, controller, registry, automation, or heartbeat.

## 18. Planner Source-Of-Truth Reconciliation

Planner independently compared this planning-first freeze with the task, Planner evidence, and
board. No new product or automation scope was introduced. The effective contract is now
consistent on:

- registry schema v2 and separate User gates for real creation, import, migration, and activation;
- six CAS mutation commands, including the durable `mark-invocation-started` boundary;
- the full stable error-code catalog and exit classes;
- exact Future May Touch, read-only locks, line budgets, TDD, rollback, and preserved topology.

## 19. Reviewer B6 Developer Planning Fix

Reviewer implementation-readiness B6 identified that the sixth mutation command was present in
the command surface and recovery protocol but absent from direct TDD enumeration. The task and
plan now require direct `mark-invocation-started` tests for:

1. exact `prepared` first write and generation `+1`;
2. identical canonical replay returning `CTL_ALREADY_APPLIED` with unchanged generation;
3. stale expected generation returning `CTL_CAS_CONFLICT`;
4. changed payload or idempotency-key reuse returning `CTL_IDEMPOTENCY_CONFLICT`;
5. wrong source stage returning `CTL_DISPATCH_STAGE_MISMATCH`;
6. zero native/Git external action for every command path.

Crash-at-`invocation_started` and possible-start/no-resend remain independent integration tests.
All other readiness contracts and independent User gates remain unchanged.

Planner independently verified that all six CAS mutation commands now have direct command-level
TDD. The `mark-invocation-started` command matrix covers prepared-only admission, first-write
generation `+1`, canonical replay/no increment, stale CAS, changed payload/key conflict, wrong
stage, and marker-only zero external action. Crash-at-`invocation_started` and possible-start
no-resend remain separate integration tests and do not substitute for that matrix.

## 20. Authorization Boundary And Superseded Checkpoint

Reviewer implementation-readiness passed with B1-B6 closed, and User approval covered the exact
Future May Touch package. B10 subsequently proved that the approved native resource order is
unreachable. The User then selected Option A and approved the four B16 paths, and Reviewer passed
the combined Option A plan/readiness re-gate. That sequence supersedes the temporary B10 pause and
restores implementation authority only for the same Developer's bounded B10-B12 fix.

During implementation and validation:

- native task calls use fake or in-memory adapters only;
- registry and Git/worktree tests use disposable temporary repositories only;
- dry-run paths must prove zero writes to the primary repository and retained topology;
- no real task, automation, heartbeat, branch, worktree, migration, registry activation, archive,
  cleanup, commit, fetch, or push operation is allowed.

## 21. Stop Point

`post_checkpoint_source_of_truth_reconciliation_complete /
pending_reviewer_docs_only_closeout_gate`.

Checkpoint `76a6e736d66ca0207f262f597513a779a1634571` contains the exact 35-path inventory:
34 implementation candidate paths plus task-specific QA evidence. It records `8097 additions /
21 deletions`, parent `6767a3ae4116185d8ed27b53cfdc050975efce2e`, fresh bounded
`138 passed`, clean `git show --check`, and excluded residual `0`. The next role is Reviewer
docs-only closeout gate. Bootstrap and pilot require separate User authorization; real runtime
operations, registry activation, automation, heartbeat, native task mutation, real branch/worktree
mutation, v1-to-v2 migration, retirement, archival, TASK_367A cleanup, fetch, and push remain
unauthorized. Local `master` is one commit ahead of the local `origin/master` tracking ref, but no
fetch occurred and no remote-current SHA is claimed.
