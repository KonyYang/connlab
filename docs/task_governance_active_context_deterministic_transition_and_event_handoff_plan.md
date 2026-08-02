# Active Context Deterministic Transition And Event Handoff Implementation Plan

Status: `integration_reconciliation_amendment_pending_user_approval`

Task: `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF`

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

## Pending Post-Transition Dispatch/Idempotency Reconciliation Plan

### 1. Discovery result and authority

Current phase remains Phase 11. Task A is the sole WIP=`1` token owner in
`gate_running/Reviewer`; primary is clean `5cd7f02a...` and the exact lane is clean at the same
recorded candidate `70e5c6a...`. Planner is allowed because two fail-closed post-transition results
require scope/authority design; this is not a routine callback.

Confirmed by User: preserve the atomic transition and separate consumed bootstrap; recognize exact
duplicates with full committed proof; create role-specific `GateDispatch` without widening
`ImplementationDispatch`; bind one current Reviewer dispatch; keep evidence genuine, role gates
independent, Task B stopped, and all operations non-destructive.

Confirmed by repository: primary `5cd7f02a...` has sole parent `329c0343...` and only the board
path; board blob is `972b1c2386145114cb3daa35037913d709bb5180`, byte SHA-256 is
`3e57b913098e565de3fee8f4a0ffdff597e3d7fdfec5232fe63027298f1a2507`, and payload digest is
`f2ddca5a8f84f4f8a966410852983571006f2810028ea0a82e33df8ed7ef0a03`. Board and lane bind
`70e5c6a...`, 32 locks, Developer evidence blob `e9d528a9...`/SHA-256 `1bee1cfe...`, transition
`367e000d...`, plan `5ac92b50...`, bootstrap `b1605205...`, and one real `DEVELOPER_READY`.
Exact probes return zero-write `BLOCKED_TRANSITION_METADATA_BOOTSTRAP` and
`BLOCKED_DISPATCH_STATE`.

Planner inference: duplicate classification must be shared by plan/apply and precede consumed-
bootstrap rejection; GateDispatch is a read-only policy gate, not a transition; existing 496/489-
line gate tests require new bounded modules.

Unresolved authority: ordinary non-bootstrap transition validation still requires scope commit
equal Git base and textual scope equal locks. The current approved scope ref is `d7994d26...`, not
base `15c3120a...`; therefore current code cannot apply a genuine `REVIEWER_BLOCKED` transition.
Changing code first would place Developer writes under `gate_running/Reviewer`; changing the board
manually is prohibited. No compliant ordering exists without explicit User-authorized authority
bridge. This is the only blocking question and no implementation may start before it is resolved.

### 2. Amendment A — duplicate classifier and idempotency order

Create one pure `classify_committed_duplicate` responsibility in
`connlab_execution_transition_proof.py`; the coordinator remains sole CLI/Git reader/state-machine/
writer. `validate_plan` and apply both call the same coordinator-level duplicate proof before any
bootstrap source/consumption validation.

Validation order for an apparent duplicate:

1. parse canonical inputs and structurally validate the current control/bootstrap without treating
   consumption as a planning error;
2. require one exact matching `last_transition` and history entry, target active facts and context;
3. require clean primary at a one-parent board-only commit whose parent is exact source primary;
4. load source-parent board and prove its blob/payload/snapshot; reconstruct candidate package,
   evidence commit/blob/SHA/status, range, lock/scope, transition ID, plan digest and bootstrap ID;
5. render the target and require byte-exact current board blob plus exact commit topology;
6. `plan` returns zero-write `ALREADY_APPLIED`; `apply` does so only with the original expected
   source snapshot and plan digest. Exact uncommitted render returns
   `RECOVERY_TRANSITION_COMMIT_REQUIRED`.

Consumed bootstrap remains present and immutable. Missing/extra/different history, later primary
commit, dirty state, different input, source/candidate/evidence/scope/lock/context drift, partial
write, rewritten ancestry or tampered board returns stable fail-closed codes. Duplicate proof never
falls through into bootstrap creation and never appends history.

### 3. Amendment B — GateDispatch contract

Add `GateDispatch` as a distinct `connlab_execution_gate.ps1` intent with required `GateRole` and
`EvidencePath`, plus optional `DispatchAttestationRef`. Do not route gate roles through
`ImplementationDispatch`; its existing Developer/Quick Fixer behavior and tests remain unchanged.

GateDispatch validates, in order: primary root/master/clean; unique JSON; exact owner/task/lane;
`gate_running/<GateRole>`; role membership in `required_gates`; branch/worktree/index clean; board
HEAD equals physical lane HEAD; base ancestry; exact 35-lock list/digest after scope activation;
scope/evidence/last-transition/context agreement; role-predecessor evidence ref at active HEAD;
exact target evidence path; and optional attestation ref/blob/hash/dispatch identity. It returns
`ALLOW_GATE_DISPATCH` with canonical `dispatch_id` and write-boundary metadata or stable
`BLOCKED_GATE_DISPATCH_*`, always zero-write.

Role boundaries:

| Gate role | Required predecessor evidence | Initial write authority |
|---|---|---|
| Reviewer | current Developer `ready_for_review` | exact Task A Reviewer evidence only |
| QA | current Reviewer `reviewer_pass` | exact Task A QA evidence only |
| Integrator | current QA `qa_pass` when QA required | exact Integrator evidence plus read-only premerge verification; merge/board/maintenance remain separately gated |

Wrong role, omitted required gate, wrong evidence suffix/ref/head/status, dirty primary/lane/index,
board/physical head mismatch, stale transition, scope/lock/context drift or extra write boundary
blocks. Developer and Quick Fixer still use only `ImplementationDispatch`.

### 4. Amendment C — frozen current Reviewer dispatch attestation

After User approval, Planner evidence at the approval commit is the immutable attestation ref. Its
canonical facts are primary `5cd7f02a...`; board blob/hash/payload; Task A token;
`gate_running/Reviewer`; lane/branch/worktree/base/HEAD `70e5c6a...`; ordered 32 locks/digest;
Developer evidence ref/blob/SHA/status; transition/plan/bootstrap IDs; permanent Reviewer thread
ID `019fb3ce-6824-7670-9015-326da4ce178f`; exact Reviewer evidence path; clean Git facts; null
queue/pause/QF/parallel; Task/Plan/Planner refs; and a derived `dispatch_id`.

Only that Reviewer, full review, and exact Reviewer-evidence write are authorized. Same exact
delivery retry reuses the same identity and is not a second authorization; any board/Git/evidence/
thread target/input drift expires it. A block must be genuine `reviewer_blocked`; pass must be
genuine `reviewer_pass`. No Developer byte, board prewrite, manual state reversal, generated
evidence/history, generic bypass, other gate, or Task B action is permitted.

### 5. Exact implementation scope and locks

Developer May Touch after a legal transition to Developer:

1. `scripts/connlab_execution_transition.py` — sole CLI/Git/state/write/recovery coordinator;
2. `scripts/connlab_execution_transition_proof.py` — pure duplicate/transition proof;
3. `tests/unit/test_connlab_execution_transition_proof.py` — pure duplicate matrix;
4. `tests/integration/test_connlab_execution_transition_recovery.py` — bounded reconnect bridge;
5. `tests/integration/test_connlab_execution_transition_candidate_adoption.py` — real-shape plan/
   apply/replay/rollback matrix;
6. `scripts/connlab_execution_gate.ps1` — read-only GateDispatch policy;
7. `tests/unit/test_connlab_gate_dispatch.py` — new bounded gate matrix;
8. `tests/integration/test_connlab_gate_dispatch_recovery.py` — new bounded production-root/Git/
   current-attestation matrix;
9. `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`;
10. `.agents/skills/connlab-lane-orchestrator/SKILL.md`;
11. `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`;
12. Task A Developer evidence.

Role/primary May Touch later: exact Reviewer/QA/Integrator/Planner evidence, this Task/Plan, and
board only via reviewed atomic transition. Existing transition mixed unit (`390`), gate mixed unit
(`496`) and gate recovery (`489`) are read-only regression suites. Active-context/bootstrap/
maintenance/handoff helpers/tests, WIP policy, Planner and other skills/protocols, execution worktree
helpers, registry/bundle, archives/index/audit, Task B/umbrella, V1/V2, product/data/runtime/remote,
and protected lanes are Must Not Touch.

The next legal atomic scope transition must validate current 32-lock digest `93bbeff0...34c16c`
and insert only `scripts/connlab_execution_gate.ps1` after `scripts/run_task.ps1`, gate-dispatch unit
after proof unit, and gate-dispatch recovery after candidate-adoption integration. The resulting
35-lock compact-JSON digest is
`a45c3bcd9051af6570bc386c0384aa11865d346e027f4d9f10afadaa16d51347`. Scope contract ref,
May Touch digest and locks change in that same atomic transition; never ambient planning.

### 6. Responsibilities and ceilings

| Path | Hard ceiling | Responsibility |
|---|---:|---|
| transition coordinator | `460` lines | CLI/Git/state/write/recovery/result; shrink/refactor, no growth |
| transition proof | `360` lines | side-effect-free duplicate/bootstrap/delta identities |
| proof unit | `300` lines | pure duplicate/tamper/replay cases |
| transition recovery | `120` lines | reconnect/commit-boundary compatibility |
| candidate adoption integration | `380` lines | disposable-Git four events plus current duplicate shape |
| execution gate | `360` lines | read-only policy and GateDispatch |
| new gate unit | `320` lines | role/state/gate/evidence/write-boundary matrix |
| new gate integration | `300` lines | production-root/Git cleanliness/attestation/idempotent delivery |
| active-context contract | `160` lines | normative dispatch/transition contract |
| Orchestrator skill | `16384` bytes | concise GateDispatch call order and stop behavior |
| orchestration protocol | `12288` bytes | normative role dispatch route |

No second state machine, shell-eval, new dependency, broad glob authority, or mixed-test growth.

### 7. TDD checkpoints and implementation stop conditions

- G0: exact clean post-Reviewer-blocked Developer authority and 35-lock scope; stop if unavailable.
- G1 RED: new proof/candidate/gate modules reproduce current duplicate and dispatch blockers plus
  normal Reviewer-blocked scope-ref failure; commit only bounded tests.
- G2: pure duplicate classifier/coordinator ordering; existing transition compatibility stays green.
- G3: GateDispatch implementation and new unit/integration GREEN; ImplementationDispatch suites
  remain byte-compatible in meaning.
- G4: contract/skill/protocol compact alignment; budgets/static checks pass.
- G5: complete Task A suite and exact Developer evidence; clean checkpoint only.

Any unexpected path, line/budget excess, nonzero production write, dirty state, unclassified
failure, weakened fail-closed code, or authority mismatch stops and returns Planner/User.

Execution budget is fixed. Developer runs focused RED/GREEN for the two amendment issues and one
final Task A governance regression. Reviewer reviews the complete committed diff and reruns the
focused duplicate, replay, GateDispatch, wrong-role/state/head, dirty/divergent and attestation
negative matrix; one normal bounded fix pass is the maximum. QA runs the complete Task A governance
regression exactly once on the final reviewed HEAD. Evidence-only commits rerun only direct
hash/ancestry/cleanliness checks unless they introduce a new risk. Product/business tests, frontend
build, release, unrelated historical matrices, repeated full-suite evidence churn, migration and
board compression are excluded.

### 8. Validation matrix and serial route

1. current exact plan duplicate and apply replay -> `ALREADY_APPLIED` with original IDs;
2. consumed bootstrap never blocks a fully proven duplicate and never reopens;
3. stale/different/tampered/partial/extra-history/later-commit duplicates block;
4. exact uncommitted render reconnects; interrupted before/temp/fsync/replace/reload rolls back;
5. all four routine events retain role-proportionate deltas and exact duplicate behavior;
6. Reviewer/QA implementation drift and evidence-only impersonation block;
7. GateDispatch positive Reviewer/QA/Integrator cases return exact role/write boundary;
8. GateDispatch wrong task/token/lane/state/role/required gate/head/branch/worktree/index blocks;
9. dirty primary/lane, lock/scope/context/evidence/transition/attestation drift blocks zero-write;
10. ImplementationDispatch still allows only Developer/Quick Fixer and rejects all gate roles;
11. current Reviewer attestation accepts exact facts/same dispatch identity and expires on drift;
12. current Reviewer may write only Reviewer evidence; genuine block/pass status is mandatory;
13. genuine `REVIEWER_BLOCKED` atomically returns to Developer and installs approved scope/locks;
14. bounded fix then `DEVELOPER_READY`; full Reviewer then `REVIEWER_PASS` and GateDispatch QA;
15. QA evidence-only `QA_PASS`; GateDispatch Integrator; no post-QA implementation drift;
16. existing transition/gate/recovery/WIP/active-context/handoff/maintenance suites pass unchanged;
17. full Task A regression, compile, PowerShell AST, static purity/single-state-machine, ceilings,
    exact allowlist, protected hashes, production zero-write and clean-state checks pass;
18. independent full Reviewer, mandatory QA and Integrator merged-tree/ancestry/residual gates pass;
19. no maintenance migration/compression, merge, push, restart, cleanup, Task B or protected-state
    change occurs before the authorized Integrator stage.

This remains the existing Task A lane and permanent role set. No new Task/branch/worktree/thread is
created. The atomic transition commit `5cd7f02a...` is never rolled back or rebuilt; pending User
review, board stays `gate_running/Reviewer` and lane stays clean `70e5c6a...`. The one-time exact
Reviewer attestation resolves only the current dispatch bootstrap and never converts a
`BLOCKED_*` into a generally ignorable result. A second same-class design blocker, more than one
normal bounded fix, third scope expansion or new authority path stops to User immediately.

Required route is current Reviewer dispatch -> genuine `REVIEWER_BLOCKED` -> atomic transition ->
Developer bounded fix -> atomic `DEVELOPER_READY` -> full Reviewer -> atomic `REVIEWER_PASS` ->
GateDispatch QA -> atomic `QA_PASS` -> GateDispatch Integrator. Because item 13 is not executable
with current code and code cannot legally change before item 13, the plan is not implementation-
ready. User must authorize a precise one-time authority bridge or revise the no-manual/no-pre-
transition-Developer constraint. Planner recommends neither without explicit direction.

### 9. Planning stop

Return `integration_reconciliation_amendment_pending_user_approval`. Keep primary board and lane
byte-unchanged, Reviewer undispatched, and Task B unstarted. Do not implement, transition, migrate,
merge, push, restart, clean, reset, restore, delete, or create any execution artifact.

## Approved Routine-Transition Authority Reconciliation Amendment

The User explicitly approved this exact amendment at
`d7994d264db1d7314d916a9773c95722e9201958`:

> I approve Task A's routine-transition authority reconciliation amendment at
> d7994d264db1d7314d916a9773c95722e9201958 and authorize one bounded continuation in the existing
> Developer lane, followed by automatic atomic Developer→Reviewer transition, full Reviewer,
> mandatory QA, and Integrator. Task B remains unapproved and unstarted.

This governance record changes neither the current board nor the clean lane. It authorizes only
the exact pure-support extraction, 13-path candidate allowlist, future atomic 29-to-32 lock
transition, line ceilings, C0-C4 checkpoints, and serial gates below. It does not create a second
state machine, synthesize historical gate events, weaken the approved maintenance bootstrap, or
create a reusable/general gate bypass.

### Discovery Gate

Confirmed by User:

- Preserve the clean `ready_for_review` Developer candidate and do not dispatch Reviewer yet.
- Solve both the one-time legacy active-record metadata gap and the general durable-head versus
  callback-candidate-head transition gap.
- Initialize metadata only with an auditable, single-use, fail-closed attestation; it is not
  `transition_history` and cannot fabricate legacy role events.
- Adopt a proven callback candidate atomically with state/role/evidence/transition history; never
  pre-write board `head_sha`.
- Use role-proportionate delta rules, exact evidence/ancestry/cleanliness proof, zero-write
  failures, complete Task A regression, independent Reviewer, mandatory QA, and Integrator.

Confirmed by repository:

- Primary is clean `master@49911ae626daf646836471246a223496dc7ea771`; board authority remains
  Task A sole owner in `implementation_running/Developer`, durable lane HEAD `3e737616...`, queue
  empty, paused/Quick Fix/parallel null, and payload digest `124cbc003ab8322cf2208d742e9a59d971875ab44773400d3607833cab283be8`.
- The exact lane is clean at `aeb7709128361782800d2da5a473d730d48df652`; base and durable HEAD
  are ancestors. Implementation checkpoint is `dc8f1fef42c874523b5706da3c8d92fa8391c475`.
- `3e737616...aeb77091` contains exactly the six approved bootstrap paths. Developer evidence at
  candidate has blob `104387574e995f2b6caf4bf1ceacfab76a748c64`, SHA-256
  `3d53242ba53f899bd9656e37e33508f6b74d57b711fd5926f39e1a4d67d2157c`, and top-level
  `Developer/ready_for_review`; the seven-field callback is `ALLOW_CALLBACK`.
- Candidate validation records bootstrap `50 passed`, existing Task A `133 passed`, compilation,
  AST, line, allowlist, protected-state, and production zero-write checks.
- Production `ImplementationDispatch` returns `BLOCKED_ACTIVE_HEAD_DRIFT`; transition `plan`
  returns `BLOCKED_TRANSITION_METADATA`. Both are stable zero-write results.
- The helper currently validates metadata before planning, requires board `head_sha` to equal the
  candidate, checks the whole base-to-candidate package instead of an event delta, requires the
  scope-contract commit to equal `base_sha`, and requires parsed May Touch paths to equal board
  Locked Paths. The approved Task and later amendments prove these are distinct concepts.
- The original Task A May Touch includes the transition helper/tests/contract, but the approved
  maintenance-bootstrap amendment explicitly locked them read-only. The required new User
  approval is now bound to `d7994d26...` and only the exact scope below.

Planner inference:

- Metadata bootstrap and first candidate adoption must be one transaction; a standalone metadata
  initialization would recreate the prohibited preliminary-authority gap.
- `base_sha`, latest approved scope contract, effective May Touch digest, and board Locked Paths
  digest must be independent frozen fields. Scope amendments do not change the lane's Git base.
- The current blocked candidate `aeb77091...` is a legacy anchor. The post-fix transition
  candidate must descend from it and may add only the newly approved helper/contract/tests plus
  updated Developer evidence.
- Because the uncorrected gate/helper cannot authorize their own repair, exact User approval must
  authorize one same-owner bounded Developer continuation. This is a one-use bootstrap boundary,
  not a reusable exception or parallel owner.

Not yet confirmed:

- The future fix/evidence candidate, transition plan/bootstrap/transition IDs, Reviewer/QA
  evidence commits, retry merge, and final migration hashes.

These are gated future outputs, not approval or scope gaps. No additional product or UX question
exists. Orchestrator may continue only through the exact serial route below after revalidating the
frozen anchors and clean lane.

### Frozen metadata and transition plan schemas

`active` retains schema version 1 and gains the already-designed fields, but their semantics are
corrected:

```json
{
  "scope_contract_ref": "tasks/TASK_...md@<latest-approved-scope-commit>#<sha256>",
  "may_touch_digest": "<canonical-effective-approved-scope-digest>",
  "locked_paths_digest": "<canonical-board-locked-paths-digest>",
  "last_transition_id": "<sha256-after-first-atomic-transition>"
}
```

`base_sha` remains `15c3120...`; it is not required to equal the later scope-contract commit.
May Touch and Locked Paths are independently validated. The effective first-transition scope is
the existing approved six-path package plus exactly seven implementation/contract paths reopened
by this amendment, with the Developer evidence path updated in place: `13` distinct paths total.
The candidate must contain no other delta from durable HEAD `3e737616...`.

The separate canonical `transition_metadata_bootstrap` board record contains schema/version,
purpose, Task/base/original approval/latest amendment refs, primary/source-board/payload anchors,
durable HEAD, blocked candidate/evidence/blob/SHA/status, exact six-path digest, future fix
candidate/delta digest, branch/worktree/clean/ancestry facts, effective scope, source 29-path lock
digest `df114c309a21657d155401a591bb4a05b960ea9ef3854125713fe149509e2907`, approved expanded
32-path lock digest `93bbeff0bc0a085c4e4321f5ceb1bea94e1977383cce2521f05e8ed46734c16c`,
retained-context digest, and `bootstrap_id`. It has no `event`, `from_state`, `to_state`, or
historical gate-result fields and is not part of `transition_history`.

The canonical routine plan contains both `expected_board_head` and `candidate_lane_head`, exact
range paths/digest, evidence path/commit/blob/SHA/current-status record, primary/source-board
digest, task/token/state/role/lane/branch/worktree/base, scope/locks/gates/context, from/to tuple,
optional one-time bootstrap ID, transition ID, and plan digest.

### Exact implementation decomposition and helper interface

Repair the existing state machine through one exact extraction:

- `scripts/connlab_execution_transition.py` remains the sole CLI/parser, primary/board/Git/
  evidence/cleanliness reader, legal state-machine coordinator, atomic board writer/recovery
  coordinator, and stable result-code emitter. It must finish at `<=460` physical lines.
- `scripts/connlab_execution_transition_proof.py` is a new side-effect-free support module. It owns
  immutable proof values, canonical hashing/serialization, effective scope/lock validation,
  durable-to-candidate path classification, event-specific delta validation, Task-A-only metadata-
  bootstrap attestation construction/validation, transition/plan identity construction, and pure
  rendering from already verified facts. It must stay `<=360` physical lines and must not parse a
  CLI, invoke Git/subprocesses, inspect filesystem/worktree state, write/replace files, route roles,
  or mutate authority. It is not a second state machine.

The normative coordinator plan/apply shape becomes:

```text
py scripts/connlab_execution_transition.py plan \
  --repo-root <primary> --event <EVENT> --task-id <TASK_ID> --lane <lane> \
  --expected-primary-head <sha> --expected-board-head <durable-sha> \
  --candidate-lane-head <candidate-sha> \
  --evidence-ref <path@candidate#sha256> --evidence-status <status> \
  [--task-a-legacy-metadata-bootstrap] --json

py scripts/connlab_execution_transition.py apply <same inputs> \
  --expected-snapshot-digest <sha256> --expected-plan-digest <sha256> --json
```

The bootstrap flag is accepted exactly once, only for Task A's frozen anchors and first
`DEVELOPER_READY`. Missing/partial/extra bootstrap facts, existing metadata/history/bootstrap, or
any drift returns `BLOCKED_TRANSITION_METADATA_BOOTSTRAP`. Ordinary tasks and later events cannot
use it.

### Validation and atomic apply order

Plan is always zero-write and validates in this order:

1. resolve exact primary master, unique board markers/JSON/summary, source primary/board/payload,
   Task A sole token/state/role/lane/base, queue/paused/QF/parallel/residual context;
2. read durable `active.head_sha` and require exact `expected_board_head`; never compare it to the
   candidate for equality;
3. resolve exact lane branch/worktree/index, require clean candidate HEAD, prove base -> durable ->
   candidate ancestry and no rewrite/divergence;
4. compute `durable..candidate` paths/digest and apply the event-specific delta policy;
5. resolve evidence at candidate commit, verify path/blob/SHA/status/task/role/current-record and
   candidate ancestry; historical callback blocks below the current envelope cannot impersonate
   current status;
6. validate latest approved scope ref, original base scope, independently hashed May Touch,
   current 29-path and approved 32-path Locked Paths, required gates, retained context, legal
   from/to tuple;
7. on the one legacy path, validate every frozen `49911ae6`/`3e737616`/`aeb77091`/evidence/six-
   path/bootstrap fact and derive `bootstrap_id`;
8. derive exact rendered board, transition ID and plan digest; emit `ALLOW_TRANSITION` zero-write.

Apply rereads steps 1-8, requires exact snapshot and plan digests, then writes one temporary board,
fsyncs, atomically replaces only `docs/task_board.md`, reloads and revalidates the complete result.
The one replacement simultaneously adopts candidate HEAD/evidence, changes state/role, appends
the real current event, sets last-transition fields, initializes metadata/bootstrap, and replaces
the source 29-path lock list with the exact approved 32-path list when needed. No other path is
written. A metadata-only, lock-only, or candidate-HEAD-only write is prohibited.

Injected/pre-replace failure removes the temporary file and preserves source bytes. If replacement
succeeds but process/commit is interrupted, exact reconnect returns
`RECOVERY_TRANSITION_COMMIT_REQUIRED` only when primary HEAD is still the source and the sole dirty
path is the exact rendered board; it never claims `ALREADY_APPLIED`. The Orchestrator may then
exact-stage/commit that proven board or restore only under separately reviewed exact recovery
authority. After the immediate one-path commit, identical complete proof returns zero-write
`ALREADY_APPLIED`; any later/divergent/partial state blocks.

### Role-proportionate candidate delta contract

- `DEVELOPER_READY`: `durable..candidate` must include the exact current Developer evidence and
  only approved implementation/test/contract paths. The helper records the full range, supports an
  implementation checkpoint followed by a later evidence commit, and rejects evidence-only
  impersonation unless immutable task metadata explicitly declares a governance-evidence-only
  task.
- `REVIEWER_BLOCKED`: exact Reviewer evidence path only; status `reviewer_blocked`; no other byte.
- `REVIEWER_PASS`: exact Reviewer evidence path only; status `reviewer_pass`; no other byte.
- `QA_PASS`: exact QA evidence path only; status `qa_pass`; no implementation/helper/test/contract
  byte after the reviewed candidate.

For every event, the evidence commit equals candidate HEAD. A stale ancestor evidence ref, branch
rewrite, non-ancestor candidate, dirty lane/index, path outside scope/locks, wrong role/status,
multiple current-status envelopes, evidence-only path pretending to be another role, or changed
helper after review returns stable `BLOCKED_*` with `changed_paths=[]`.

### Exact approved May Touch / Must Not Touch / locks

Developer lane May Touch only:

1. `scripts/connlab_execution_transition.py`
2. `scripts/connlab_execution_transition_proof.py` (new pure support module)
3. `tests/unit/test_connlab_execution_transition.py` (compatibility assertions only)
4. `tests/unit/test_connlab_execution_transition_proof.py` (new bounded pure-proof matrix)
5. `tests/integration/test_connlab_execution_transition_recovery.py` (compatibility assertions only)
6. `tests/integration/test_connlab_execution_transition_candidate_adoption.py` (new bounded
   disposable-Git real-shape matrix)
7. `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
8. Task A Developer evidence

Role/primary-only paths after the relevant gate:

9. Task A Reviewer/QA/Integrator/Planner evidence
10. current Task and Plan
11. `docs/task_board.md`, only by the helper's one atomic transition replacement and its exact
   one-path commit

Exact physical-line ceilings and ownership:

| Path | Ceiling | Sole responsibility |
|---|---:|---|
| `scripts/connlab_execution_transition.py` | `460` | CLI/read/state-machine/write/recovery/result coordination |
| `scripts/connlab_execution_transition_proof.py` | `360` | pure proof, digest, bootstrap, delta, identity, and rendering functions |
| `tests/unit/test_connlab_execution_transition.py` | `399` | existing coordinator compatibility assertions only |
| `tests/unit/test_connlab_execution_transition_proof.py` | `360` | new pure proof/bootstrap/delta/spoof/replay matrix |
| `tests/integration/test_connlab_execution_transition_recovery.py` | `120` | existing recovery compatibility assertions only |
| `tests/integration/test_connlab_execution_transition_candidate_adoption.py` | `380` | new disposable-Git four-event/atomic/reconnect matrix |
| `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md` | `160` | normative contract only |

Must Not Touch: active-context/bootstrap/handoff helpers and tests, legacy source attestation,
`run_task.ps1`, execution/worktree/maintenance gates, every other contract/policy/skill/test,
archive/index/audit, registry/bundle, V1/V2, Task B/umbrella, product/data/runtime/release/remote,
and retained/frozen/cancelled lanes. The current board stays byte-unchanged before implementation.
On the first atomic transition only, the ordered operational lock list expands
from 29 to 32 by inserting the proof support after the coordinator, the proof unit test after the
existing transition unit test, and the candidate-adoption integration test after the existing
recovery test; exact compact-JSON SHA-256 becomes `93bbeff0...34c16c`. Any other path/order/digest
blocks zero-write. WIP=`1` remains unchanged; no parallel exception, new task, branch, or worktree.

### Implementation and role sequence after User approval

1. Planner records exact approval in Task/Plan/Planner evidence only; board head/state/role stay
   unchanged. No ambient board metadata or candidate-head update is allowed.
2. Orchestrator revalidates exact anchors. User approval authorizes one same-token/same-lane
   bounded Developer continuation from clean `aeb77091...` despite the known legacy
   `BLOCKED_ACTIVE_HEAD_DRIFT`; any different blocker or drift stops. This exception cannot route
   another task/role or survive the first atomic transition.
3. Developer uses exact checkpoints: C0 clean `aeb77091...`; C1 extraction-preservation creates
   the pure support module and moves only pure responsibilities while existing transition/recovery
   compatibility tests and the full `133` baseline remain green; C2 records RED in the two new
   bounded test modules without pre-overwriting board HEAD; C3 implements candidate/bootstrap/
   atomic-recovery behavior in exactly the seven implementation/contract paths; C4 adds only the
   updated Developer evidence and finishes clean `ready_for_review`. Each checkpoint uses exact-
   path staging and must pass its applicable line/allowlist/diff gates.
4. From that candidate, the repaired existing helper plans/applies the one atomic metadata-
   bootstrap plus `DEVELOPER_READY` adoption and the Orchestrator exact-commits board only.
5. Reviewer performs a full re-gate of the complete Task A package and the new transition matrix.
   Reviewer block/pass uses the repaired atomic candidate adoption with evidence-only delta.
6. Mandatory QA validates the final reviewed candidate, full Task A matrix and production zero-
   write gates; `QA_PASS` is an atomic evidence-only adoption.
7. Integrator verifies ancestry/package/attestations, merges the newly reviewed delta, retries the
   previously approved generation-1 maintenance bootstrap, reruns merged validation, and accepts
   only on complete success. Task B remains stopped.

Reviewer focus is mandatory and exact: verify the coordinator remains the sole CLI/state machine/
writer; statically reject CLI, Git/subprocess, filesystem/worktree read/write, role-routing, or
authority mutation in the proof support; enforce every line ceiling and exact 13-path package;
prove the new real-shape fixtures do not pre-overwrite durable board HEAD; independently exercise
scope/lock/evidence spoof, post-review drift, exact duplicate, interruption/reconnect, and rollback;
and rerun bootstrap `50`, prior Task A `133`, new focused modules, protected-state hashes, and
production zero-write checks. Reviewer failure returns only to the existing Developer lane within
this exact scope; any new path or responsibility returns to Planner/User.

### Validation matrix

1. real-shape `DEVELOPER_READY`: board HEAD prior Developer checkpoint, lane HEAD later
   implementation-plus-evidence candidate; no fixture pre-overwrite; one atomic Reviewer result;
2. real-shape `REVIEWER_BLOCKED`: board reviewed candidate, lane adds only blocked evidence;
3. Developer fix after Reviewer block: implementation checkpoint plus later Developer evidence;
4. real-shape `REVIEWER_PASS`: board Developer candidate, lane adds only pass evidence;
5. real-shape `QA_PASS`: board Reviewer candidate, lane adds only QA evidence;
6. first Task A transition atomically initializes exact metadata/bootstrap and appends only the
   real `DEVELOPER_READY`; no synthetic earlier events;
7. exact bootstrap anchor/task/base/primary/board/durable/candidate/evidence/blob/SHA/status/six-
   path/scope/lock/context positive;
8. each bootstrap fact missing, stale, extra, altered, dirty, rewritten, or replayed blocks zero-
   write; later events/tasks cannot bootstrap;
9. exact duplicate committed transition returns `ALREADY_APPLIED`; divergent duplicate blocks;
10. replaced-but-uncommitted reconnect returns recovery-required, not applied; injected faults
    before/temp/fsync/replace/reload restore or retain exact recoverable bytes;
11. subsequent evidence commit is accepted only when candidate and evidence ref equal the final
    commit and the full range conforms;
12. stale ancestor, divergent/non-ancestor/rewritten candidate, dirty lane/index, wrong branch/
    worktree/base, and primary/source-board drift block;
13. scope/lock digest drift, outside path, evidence hash/blob/status/task/role spoof, missing or
    multiple current envelopes, and evidence-only impersonation block;
14. Reviewer/QA candidate with any implementation/helper/test/contract drift blocks;
15. board write is exactly one atomic `docs/task_board.md` replacement; all failure paths are
    zero-write and preserve queue/paused/QF/parallel/residual/token/branch/worktree/base/locks;
16. `test_connlab_execution_transition_proof.py` covers pure scope/lock/bootstrap/delta/digest/
    spoof/replay behavior; `test_connlab_execution_transition_candidate_adoption.py` covers all
    four real-shape events, duplicate/reconnect/rollback, canonical Windows paths, and exact commit
    topology; existing transition/recovery modules receive compatibility assertions only;
17. unchanged active-context, maintenance, handoff, execution gate/recovery, WIP/Quick Fix,
    worktree/archive/role suites pass, including the approved bootstrap `50` and prior Task A
    `133` baseline;
18. complete Task A regression plus new cases pass; Python compilation, PowerShell AST, all seven
    exact physical-line ceilings, import/static checks proving the support module has no CLI/Git/
    subprocess/filesystem-write/authority-mutation responsibility, exact `13`-path durable-to-final
    candidate allowlist/diff/show, protected hashes, production zero-write checks, callback/cadence/
    budgets all pass;
19. full independent Reviewer re-gate, mandatory QA on final reviewed HEAD, and Integrator merged-
    tree/migration/rollback/clean-closeout gates pass;
20. Task B/umbrella/product/registry/V1/V2/retained lanes/remote/runtime remain unchanged.

### Historical stop point (superseded)

The earlier `developer_dispatch_ready` stop was consumed by the atomic transition committed at
`5cd7f02a...`. It is retained only as audit history and grants no current dispatch authority. The
current planning stop is the pending post-transition amendment above; board and lane remain
unchanged and no role is dispatched.

## Integrator Blocked Result

- Conflict-free local merge: `a42ca37e205127afd87d4cdc1d26ede53830522c`.
- Exact production plan succeeded for generation 1, but exact guarded apply failed closed with
  `BLOCKED_MAINTENANCE_GATES` because the live legacy board has no required Task A
  `transition_history` entries.
- The failure was zero-write: source board unchanged, archive/index absent, token retained, and no
  acceptance claimed. Planner/User reconciliation is required before retry; Integrator will not
  invent transition history or alter the frozen helper/contract ad hoc.

## Approved Integration Reconciliation Amendment

Historical note: this maintenance-bootstrap amendment was implemented and evidenced at candidate
`aeb7709128361782800d2da5a473d730d48df652`. Its preparation/fast-forward stop text below is
retained for audit and superseded by the now-approved routine-transition amendment above.

The User explicitly approved this formal amendment at primary anchor
`3e73761673fd75de4e79028b0b8d0b89979bbd1a` and authorized automatic bounded
Developer -> independent Reviewer -> mandatory QA -> local Integrator continuation. This approval
returns the same Task A token to `implementation_running/Developer` only to prepare the existing
lane for reconciliation; Developer is not dispatched yet and live apply remains prohibited. The
amendment supersedes only the blocked first-migration portion of Step A8; all normal Task A
transition, maintenance, WIP, gate, budget, and safety contracts remain unchanged.

### Discovery Gate

Confirmed by User:

- Use a one-time auditable legacy bootstrap attestation, structurally separate from
  `transition_history`, without fabricating or backfilling role events.
- Bind the exact original Task A Developer/Reviewer/QA evidence, lane ancestry, QA HEAD, local
  merge/package, blocked primary, sole Integrator authority/digest, failed source-board/plan facts,
  and a non-replayable consumption identity.
- Preserve normal gates; prohibit generic bypasses, force flags, manual history/archive/index,
  synthesized callbacks, Task B activation, push/restart, and destructive actions.
- Require a new bounded Developer pass, full Reviewer re-gate, mandatory QA, then Integrator retry
  on a new reviewed HEAD. Live apply is forbidden until the recorded approval and those gates are
  all satisfied.

Confirmed by repository:

- Primary is clean at `75565f7aed80e34844e626519cbc74c4cc49c0a2`; Task A remains sole
  `gate_running/Integrator` owner and legacy Inspect returns `ALLOW_INSPECT` with execution-control
  digest `a1f0422506ffb124e14fac69c3cc51a4b2a56087c981c8c657aa06f9ec0755d4`.
- Merge `a42ca37e205127afd87d4cdc1d26ede53830522c` is an ancestor of primary, has parents
  `fd6036d9fce106ea81991def0ec572dfe20cdcb0` and
  `e958ba37df216c1690434ed7f9f40d4a436a88c5`, tree
  `a59c65dc838bfe66e8a839603d263e4e2c467ad1`, and exact 26-path first-parent package digest
  `765445286739a3fb256f47ad36b41dbddde0fa7e2ea8c5f5018b17323da2dd4a`.
- Exact evidence bindings are:
  - Developer: path `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md`, commit `1fd726b08b7e49a32341d49e4439c889c4c6ab7b`, blob `6bd2703d6f280b9eec2fa01e59173149bd894c98`, SHA-256 `0fa1abdffe4d93182c090ddbf227628aec039d91d50b76b9f5fe9763ef5d3a0e`, status `ready_for_review`;
  - Reviewer: same task prefix plus `_reviewer.md`, commit `84503d16e2638a827ecd3ef6704d0fe6bfed72ca`, blob `165ebfab7f198953539a371c7c56e114ccba6a91`, SHA-256 `de9be8e4c47b04f8538eeb5e2b732932c607486b2b5e2ca9441b6c0803837d70`, status `reviewer_pass`;
  - QA: same task prefix plus `_qa.md`, commit `e958ba37df216c1690434ed7f9f40d4a436a88c5`, blob `49dc936e67a31fd53d616ee0b9e51bc5702819e8`, SHA-256 `49e33a43138dffd9fa7145abac6a2693e9f8f5c589ea22281f30c65b4e199541`, status `qa_pass`.
- Base -> Developer -> Reviewer -> QA -> merge -> primary ancestry is intact. The lane remains
  clean at QA HEAD. The Integrator evidence at primary has blob
  `dac23cd0d720583268920ab9112f402d09bf3717`, SHA-256
  `e2781d373f289f14b9fec2ba57338197958ac21a17e9cd5ac23b9ed0f836f156`.
- Failed generation-1 runtime source-board SHA-256 is
  `922532265c3b27363c091ea6eae32420fdcc6c31832d44988bd5296a7cbcf2f6`; plan digest is
  `519ee4f53e1887c524d59971b40a0e1749f4911cd2b032a41237584caaacc497`; apply returned
  `BLOCKED_MAINTENANCE_GATES` with zero writes and history directory absent.
- Current helper validates routine gate evidence only through actual `transition_history` and its
  generation-1 index schema has no bootstrap consumption record. `connlab_active_context.py` is
  already `497` lines, so new logic cannot be added in place without violating the hard limit.

Planner inference:

- The fixed old source-board hash/plan digest are historical failure anchors, not reusable apply
  inputs. Governance and reviewed code will change before retry, so the retry must derive a new
  source hash/plan digest and bind both into a distinct consumption identity.
- A Task-A-specific module plus a minimal active-context hook is safer than growing the 497-line
  helper or introducing a generic legacy mode. A dedicated immutable consumption file referenced
  by generation 1 index survives compaction without becoming execution authority.
- The existing lane can be fast-forwarded to the approved primary descendant because its QA HEAD
  is already an ancestor through `a42ca37e`; this preserves all history without a new task,
  worktree, reset, rebase, or cherry-pick.

Unresolved execution outputs:

- User approval commit, new Developer/Reviewer/QA heads and evidence blobs, retry merge/source
  HEAD, new source-board hash/plan digest, `bootstrap_id`, `consumption_id`, archive/audit hashes,
  compacted metrics, and final acceptance commit.

These are produced and independently verified by the gated execution sequence. They do not alter
scope and were not planning blockers. The User has now approved the exact amendment; continuation
remains stopped at reconciliation preparation until the lane fast-forward and fresh dispatch gate
are proven.

### Exact historical merge package

The canonical sorted 26-path list hashed above is:

```text
.agents/skills/connlab-lane-orchestrator/SKILL.md
.agents/skills/connlab-planner/SKILL.md
AGENTS.md
docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md
docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_qa.md
docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_reviewer.md
docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md
docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md
docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md
docs/project_management/PARALLEL_EXECUTION_MODEL.md
docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md
docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md
docs/project_management/TASK_EXECUTION_SKILL.md
docs/project_management/TASK_REVIEW_CHECKLIST.md
scripts/connlab_active_context.py
scripts/connlab_execution_transition.py
scripts/connlab_handoff_contract.py
scripts/run_task.ps1
tests/integration/test_connlab_board_closeout_maintenance.py
tests/integration/test_connlab_execution_transition_recovery.py
tests/unit/test_connlab_active_context.py
tests/unit/test_connlab_active_context_governance.py
tests/unit/test_connlab_execution_transition.py
tests/unit/test_connlab_handoff_contract.py
tests/unit/test_execution_wip_and_quick_fix_governance.py
tests/unit/test_task_scoped_role_thread_lifecycle_governance.py
```

The package digest is SHA-256 over UTF-8 bytes of the ordinal-sorted paths, each followed by one
LF, including the final path.

No retry may reintroduce, omit, or reinterpret this already-merged package. The new merge delta is
limited to the amendment paths below.

### Bootstrap attestation and audit contracts

Source attestation path:

```text
docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_legacy-bootstrap-attestation.v1.json
```

Canonical schema `connlab.task-a-legacy-bootstrap-attestation`, version `1`, has exact keys for:

1. `task_id` and `purpose=first_generation_legacy_bootstrap_only`;
2. the three fixed evidence records: role/path/commit/blob/SHA-256/status;
3. base, Developer, Reviewer, and QA ancestry heads;
4. prior merge commit/parents/tree/path count/canonical path-list digest;
5. blocked primary plus exact Integrator evidence ref/blob/SHA-256;
6. sole-owner state/role and fixed execution-control digest;
7. generation `1`, failed runtime source-board hash, failed plan digest, zero-write reason, and
   archive/index absence;
8. `bootstrap_id`, computed over all preceding canonical fields.

It has no routine event/state transition fields. Exact JSON key set, types, lowercase hashes,
canonical serialization, duplicate-key rejection, and `bootstrap_id` recomputation are mandatory.

Successful apply creates exactly one immutable audit record:

```text
docs/archive/task_board_history/task-a-legacy-bootstrap-consumption-<consumption_id>.v1.json
```

The audit record includes schema/version, `bootstrap_id`, attestation path/commit/blob/SHA,
fresh amendment Reviewer/QA evidence refs, current reviewed helper blobs, task/state/role, retry
merge/source HEAD, source-board hash, execution-control digest, generation, archive path,
zero previous-index hash, `consumption_id`, and new plan digest. The generation-1 index line gains
an exact optional pair `bootstrap_consumption_path`/`bootstrap_consumption_sha256`; both must be
present only for this exact first generation and absent for ordinary records. Index validation for
all later generations revalidates the audit bytes/hash and chain.

`consumption_id` is canonical SHA-256 over all audit fields except itself and the new plan digest.
The maintenance plan includes the resulting identity, and the audit stores the final plan digest;
there is no circular digest dependency.

### Helper interface and validation order

Add only these explicit inputs to `plan-maintenance`/`apply-maintenance`:

```text
--legacy-bootstrap-ref <attestation-path@commit#sha256>
--amendment-reviewer-ref <reviewer-path@commit#sha256>
--amendment-qa-ref <qa-path@commit#sha256>
```

Omitting them uses the unchanged normal maintenance path. Supplying any subset blocks. The exact
bootstrap plan order is:

1. run existing primary/master, expected HEAD, board hash, threshold, marker/JSON parsing, index,
   archive path, and history-chain validation;
2. require generation `1`, exact Task A sole `gate_running/Integrator`, empty queue and null
   paused/Quick Fix/parallel state, and current execution-control digest;
3. require `transition_history` property to be absent exactly; a present empty, partial,
   malformed, ambiguous, or complete history uses/blocks under the normal path and cannot bootstrap;
4. require archive/index/consumption audit absent and no link/junction/path conflict;
5. validate the source attestation ref, Git commit/blob/SHA, canonical schema/key set, fixed values,
   and recomputed `bootstrap_id`;
6. independently resolve all three legacy evidence bytes/statuses and prove exact base/lane/gate
   ancestry;
7. prove prior merge parents/tree/26-path count/list digest, merge ancestry, blocked primary and
   Integrator evidence, fixed authority digest, failed source hash/plan digest/reason, and recorded
   archive/index absence;
8. prove current source HEAD descends from blocked primary and differs only through approved
   amendment governance/implementation/gate/merge paths;
9. validate fresh amendment Reviewer and QA refs/status/ancestry and require the current
   `connlab_active_context.py` plus Task-A bootstrap-module blobs to equal the reviewed/QA heads;
10. derive exact current source/board/execution/archive facts, `consumption_id`, audit path/hash,
    and a new maintenance plan digest containing them; emit zero-write plan output.

Apply repeats steps 1-10 from disk/Git, then:

11. require exact expected plan digest and consumption identity, clean primary/index, and no
    intervening commit/status/path change;
12. construct and fsync archive and consumption audit with exclusive creation;
13. atomically replace the index containing the consumption hash binding;
14. atomically replace the board last and revalidate compact authority/metrics;
15. on any failure restore source board and old index bytes, remove only exact helper-created
    archive/audit files whose bytes match the plan, and return zero net writes.

Stable failures are:

| Code | Condition |
| --- | --- |
| `BLOCKED_BOOTSTRAP_INPUTS` | missing/partial bootstrap CLI tuple |
| `BLOCKED_BOOTSTRAP_NOT_LEGACY` | transition history exists or legacy shape differs |
| `BLOCKED_BOOTSTRAP_AUTHORITY` | task/state/role/token/context/execution digest differs |
| `BLOCKED_BOOTSTRAP_REF` | ref/path/commit/blob/SHA or canonical attestation invalid |
| `BLOCKED_BOOTSTRAP_ANCHOR` | evidence, ancestry, merge/package, primary, failed-plan/source facts differ |
| `BLOCKED_BOOTSTRAP_REVIEW` | fresh amendment Reviewer/QA status/ancestry/helper attestation differs |
| `BLOCKED_BOOTSTRAP_CONFLICT` | archive/index/audit path exists unexpectedly or link/path safety fails |
| `BLOCKED_BOOTSTRAP_REPLAY` | other task/commit/board/plan/generation/role/later closeout or divergent reuse |
| `BLOCKED_BOOTSTRAP_PARTIAL` | only a subset of board/archive/index/audit completion exists |
| `BLOCKED_PLAN_STALE` | new plan digest/current facts differ at apply |
| `BLOCKED_MAINTENANCE_WRITE_FAILED` | transaction write/fault failed and rollback completed |

All pre-transaction failures return `zero_write=true`, `changed_paths=[]`. Exact successful retry
returns `APPLIED_MAINTENANCE`. Exact same-input recovery may return `ALREADY_APPLIED` only after
revalidating the whole compact board/archive/index/audit chain and immediate commit topology.

### Single-use survival and future closeouts

- Generation 1 index references the immutable consumption audit hash; its index line is included
  in every future `previous_index_sha256` chain. Compaction cannot remove the external audit.
- Generation 2+ rejects all bootstrap arguments and requires the exact consumed generation-1
  record/audit to remain valid. The historical attestation never authorizes a new apply.
- A matching audit without matching archive/index/compact board is partial failure, not consumed
  success. A matching complete generation with different current commit/board/plan is replay, not
  idempotency.
- Rollback proof reconstructs board bytes only into a proven safe temp root. It never deletes the
  immutable audit/index/archive or restores production automatically. A separately approved Git
  revert/patch is still required for live rollback.

### Exact amendment May Touch

Developer lane:

1. `scripts/connlab_active_context.py`
2. `scripts/connlab_task_a_legacy_bootstrap.py` (new)
3. `tests/unit/test_connlab_task_a_legacy_bootstrap.py` (new bounded module)
4. `tests/integration/test_connlab_task_a_legacy_bootstrap_migration.py` (new bounded module)
5. exact source-attestation JSON path above
6. `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md`

Role/primary governance:

7. the existing Task A Reviewer, QA, Integrator, and Planner evidence paths
8. this Task and Plan
9. `docs/task_board.md`
10. Integrator-only existing generation-1 archive pattern and `index.v1.jsonl`
11. Integrator-only exact consumption-audit pattern above

Must Not Touch / Locked:

- `scripts/connlab_execution_transition.py`, `scripts/connlab_handoff_contract.py`, existing
  contract/policies/protocols/skills/AGENTS, execution gate, worktree/task-complete/Markdown archive
  helpers, registry/bundle, V1/V2, Task B/umbrella, package/lock/release/product/data/runtime paths,
  and all retained/frozen/cancelled lanes.
- Direct board history insertion, synthesized callbacks/events/history, manual archive/index/audit
  creation, force/override/ignore/assume switches, generic legacy acceptance, push/restart, reset,
  restore, clean, rebase, cherry-pick, discard, deletion, or worktree recreation are prohibited.
- Bootstrap paths are exclusively Task A-owned. Board/archive/index/audit writes are exclusively
  Integrator-owned after merge. WIP remains `1`; no parallel exception.

### Non-destructive continuation and role route

1. User approval is recorded at exact primary amendment anchor
   `3e73761673fd75de4e79028b0b8d0b89979bbd1a`; the same Task A token is placed in
   `implementation_running/Developer` as preparation authority, not as a dispatch claim.
2. The current physical lane remains clean at
   `e958ba37df216c1690434ed7f9f40d4a436a88c5`; the execution record's expected target/head is
   `3e73761673fd75de4e79028b0b8d0b89979bbd1a`.
3. Orchestrator reuses the exact existing worktree/branch and fast-forwards it from the physical
   HEAD to that exact approved target. Because QA HEAD -> `a42ca37e` -> approval anchor ancestry is
   proven, this is non-destructive and preserves the old merge; no new task/worktree is created.
   Orchestrator then proves lane/worktree/index clean, exact HEAD equality, and a fresh
   `ImplementationDispatch=ALLOW_DISPATCH`. Any mismatch stops before dispatch.
4. Developer uses TDD, changes only six lane-owned paths above, commits clean, and records
   `ready_for_review`.
5. Reviewer performs a full re-gate of the whole Task A package plus bootstrap adversarial matrix.
6. Mandatory QA reruns the final complete matrix on the immutable reviewed HEAD.
7. Integrator verifies the new reviewed/QA package, merges only the amendment delta, generates a
   fresh plan, applies once, proves audit/index/archive/rollback and merged-tree tests, then closes
   Task A only if every safety/performance gate passes.

Any mismatch returns to Developer for an in-scope fix or Planner/User for scope/authority change.
The local merge `a42ca37e` and all histories remain retained; no destructive reconciliation occurs.

### Amendment validation matrix

1. exact canonical attestation and recomputed `bootstrap_id` pass;
2. each legacy evidence path/commit/blob/SHA/status mismatch blocks zero-write;
3. broken base/Developer/Reviewer/QA ancestry blocks;
4. wrong merge, parent order, tree, path count, package path, or package digest blocks;
5. wrong blocked-primary/Integrator-evidence ref or ancestry blocks;
6. wrong task/token/state/role/execution-control digest/queue/pause/QF/parallel fact blocks;
7. wrong failed runtime board hash, plan digest, generation, reason, or archive absence blocks;
8. any present/empty/partial/synthesized `transition_history` cannot use bootstrap;
9. missing/partial/extra CLI bootstrap refs block;
10. malformed/duplicate-key/noncanonical/extra-field attestation blocks;
11. amendment Reviewer/QA evidence or current helper drift blocks;
12. current source descendant with an unapproved path blocks;
13. other task, board, commit, plan, generation, role, later closeout, or altered attestation replay blocks;
14. exact plan is zero-write and includes bootstrap/consumption/audit facts;
15. stale expected head/board/plan/consumption identity blocks zero-write;
16. successful generation 1 writes exactly board, archive, index, and consumption audit;
17. audit/index bind each other and exact new plan/source/helper/review facts;
18. exact same-input complete retry is zero-write `ALREADY_APPLIED`;
19. audit-only/archive-only/index-only/board-only and every partial combination block;
20. injected failures after archive, audit, index, and board restore prior bytes and remove only exact new files;
21. generation 2/3 validate the consumption chain but reject bootstrap reuse;
22. consumption/audit/index tampering blocks later planning/apply/rollback;
23. first/second/third rollback remains byte-exact in safe temp root;
24. existing normal transition-history positive and complete mismatch matrix remain unchanged;
25. complete pre-amendment Task A `133` tests plus new focused modules pass (`133+` total);
26. Python compilation, PowerShell AST, `<500` helper limits, exact diff/allowlist, protected hashes,
    production zero-write plan, board budgets, and callback/cadence budgets pass;
27. Reviewer full re-gate and mandatory QA pass on the exact amendment HEAD;
28. Integrator merged-tree rerun, new plan/apply, compact summary/JSON agreement, archive/index/audit
    chain, rollback proof, residual ledger, and clean terminal closeout pass;
29. Task B/umbrella/product/registry/V1/V2/retained lanes/remote/runtime remain unchanged.

### Rollback and stop conditions

Before successful apply, every plan/failure is zero-write. During apply, transaction rollback
restores the exact source board/index and deletes only newly created matching archive/audit files.
After successful apply, helper rollback is proof-only into safe temp; live rollback requires a new
reviewed Git action. Integrator must stop without acceptance on any `BLOCKED_*`, test/metric miss,
dirty state, unexpected path, audit mismatch, or partial write.

Historical stop: approval governance required the exact fast-forward and bounded Developer
package. Those steps are now complete at `aeb77091...`; current routing is governed by the pending
routine-transition amendment and remains stopped for User approval.

## Historical Approval And Activation Record

- The User explicitly approved Task A only on 2026-08-01 and authorized the exact automatic route
  `Developer -> Reviewer -> mandatory QA -> local Integrator acceptance`.
- Approved planning HEAD: `d791e74a9811033058c38ee329bb3be8ee1f6504`.
- Immutable approval/worktree base:
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`; primary execution authority pins it before Create.
- Developer completed the historical bounded fixes, Reviewer and QA passed the final R1-R3
  package, and Integrator merged it locally before the first migration failed closed. The original
  approval does not cover the pending bootstrap amendment.
- Task B remains planned and cannot be approved or implemented before A local acceptance and a
  separate User approval. The umbrella remains permanently non-executable.

## 1. Outcome And Architecture

Build three bounded governance helpers behind one normative contract:

- transition helper: validates and applies four routine board state changes without Planner;
- active-context helper: derives the human summary and performs guarded lossless board history
  migration/maintenance;
- handoff helper: validates reference capsules, minimal reads, callback shape, cadence, and budgets.

The existing PowerShell execution gate stays read-only. The board JSON stays the only machine
execution authority. All apply operations use an inspect/plan/apply digest handshake and stable
fail-closed reason codes.

## 2. Discovery Gate

### Confirmed by User

- Split the rejected umbrella; A precedes B.
- Remove Planner from routine gate transitions.
- Enforce one transition/one dispatch/one Orchestrator turn and immediate stop.
- Make board compaction lossless, recurring, Integrator-only, and tested through later closeouts.
- Quantify board/core skill/protocol/dispatch/callback/read/context improvements.
- Retain WIP=`1`, token lifetime, independent roles, isolated worktrees, no push, no destructive
  cleanup, and frozen V2.

### Confirmed by repository

- Primary is clean at revision base; `Inspect=ALLOW_INSPECT`; execution is terminal and ownerless.
- Board is `2466` lines / `781091` bytes and mixes active authority with long terminal history.
- Orchestrator skill is `17304` bytes; Planner skill `3972`; orchestration protocol `14120`;
  `run_task.ps1` `4854` and embeds repeated contract/worktree text.
- Execution gate is a 307-line read-only validator and has no safe write transition interface.
- Current protocols route callbacks but still permit long turns/waits and Planner-mediated board
  transitions. Existing archive helper handles completed task/plan Markdown, not board history.
- Existing tests cover token/queue/recovery/Quick Fix/worktree/archive/permanent roles but not the
  requested state mutation, recurring compaction, budgets, or cadence.

### Planner inference

- A new Python transition helper is safer than adding writes to the PowerShell gate.
- Routine task/plan statuses should remain broad lifecycle status; board JSON + derived summary
  carry gate state, avoiding four-file Planner commits for every mechanical handoff.
- Active metadata must carry exact task gate/scope references so the helper never infers QA or
  scope from prose.
- Archive generation must replace the live board last and retain an immutable hash chain.

### Not yet confirmed

- Final accepted archive/index hashes, independently verified after-size metrics, and QA pilot
  timing.

These are execution outputs, not scope ambiguities. Definition of Ready is satisfied for User
review, not implementation.

## 3. Frozen Data Contracts

### 3.1 Active transition metadata

Newly activated tasks record these additional active fields while keeping execution schema v1
compatible with the existing read-only gate:

```json
{
  "required_gates": ["Reviewer", "QA", "Integrator"],
  "scope_contract_ref": "tasks/TASK_X.md@<commit>#<sha256>",
  "may_touch_digest": "<sha256>",
  "locked_paths_digest": "<sha256>",
  "last_transition_id": "<sha256-or-null>"
}
```

The A helper requires these fields; legacy active records receive `BLOCKED_TRANSITION_METADATA`
and stay on existing manual governance. It never guesses `qa_required` from chat or prose.

### 3.2 Transition plan

Canonical plan JSON contains schema/version, event, from/to state and role, token/task/lane,
branch/worktree/base/old+new lane HEAD, primary HEAD, evidence path/commit/blob/SHA/status, ancestry
proof, clean digests, changed paths, scope/locks digests, queue/paused/QF/parallel digests, board
JSON/summary digests, next role, and plan digest. Keys and arrays are canonical/sorted.

### 3.3 Dispatch and callback

Dispatch is a JSON capsule <=4096 bytes whose refs are `path@commit#sha256`. It includes exact
task/role/lane/branch/worktree/base/head, board/task/plan/evidence/direct-dependency refs,
scope/locks/gate snapshot digests, next action, and stop conditions. Callback is exactly seven
ordered nonempty lines and <=1024 bytes.

### 3.4 Archive index

`connlab.task-board-history-index`, version 1, is append-only JSONL with one immutable monotonic
generation record per line. Every entry
binds previous index hash, source commit/blob/hash/bytes/records, archive path/hash/records,
compacted board hash/bytes/records, moved record IDs, retained authority record IDs, and rollback
proof hash. Archive content is historical/non-authoritative.

## 4. File-Level Implementation Sequence

### Step A1 — Normative contract and executable static checks

Files: create the A contract and governance static test; make bounded references in AGENTS,
execution/parallel/orchestration policies, execution/review rules, and Planner/Orchestrator skills.

1. Add RED assertions for one normative contract, Planner mechanical exclusion, exact transitions,
   one-handoff turn limit, Integrator-only board writes, recurring closeout maintenance, budgets,
   WIP/token/role/no-push/V2 invariants, and on-demand optional history.
2. Write the contract once; replace copied long prompts with short references where safe.
3. Keep lifecycle/V2 documents unchanged and reachable on demand.
4. Run new static checks plus existing WIP/Quick Fix and permanent-role modules.

Stop if any rule weakens execution ownership, Quick Fix fail-closed behavior, role independence, or
full-read fallback.

### Step A2 — Deterministic transition helper

Files: new transition helper plus unit and disposable-Git recovery tests.

1. Add RED cases for all four event families and every required guard.
2. Parse one board block; validate active metadata, Git refs/blobs, evidence status, scope, locks,
   ancestry, clean primary/lane/index, and human summary equality.
3. `plan` emits canonical zero-write output. `apply` rereads everything, requires the exact plan
   digest, mutates only board JSON/summary, writes atomically, and verifies after bytes.
4. A duplicate exact transition returns `ALREADY_APPLIED` with zero writes; stale or divergent
   duplicate returns `BLOCKED_DUPLICATE_CONFLICT`.
5. Exercise interruption/restart, stale primary/lane/evidence, dirty index, scope drift, invalid QA
   route, queue/pause/QF/parallel changes, and write-fault rollback.

Stop if safe routing needs heuristic status parsing, callback authority, or any write outside board.

### Step A3 — Active summary and recurring board maintenance

Files: new active-context helper plus unit/integration tests. Developer uses only disposable repos.

1. Add RED tests for unique markers, JSON-summary equivalence, active/proposed/residual retention,
   terminal eligibility, line/byte/24-record thresholds, and zero-write below threshold.
2. Implement deterministic summary rendering and a migration planner that moves oldest eligible
   terminal records only.
3. Implement immutable unique generation names, chained index, byte/hash/count proofs, path/symlink
   guards, no overwrite, idempotency, and transactional rollback with board replacement last.
4. Test first migration, second and third closeouts, exact rollback, corrupt/truncated index,
   conflicting archive, non-contiguous generation, injected failures at every replace boundary,
   and no active/queue/paused/QF/parallel/residual loss.
5. Against production, Developer may run only `inspect` and `plan-maintenance`; no apply.

Stop on any unproven byte loss, second authority, unsafe archive overwrite, or production write.

### Step A4 — Compact event handoff and run-task preview

Files: handoff helper/tests, bounded `run_task.ps1`, skills/protocol references, callback test.

1. Add RED cases for capsule/ref/hash/state validation, 4096/2048/1024 budgets, exact callback
   order, full-read fallback, 60-second cadence, unchanged waits, and copied-contract rejection.
2. Make `run_task.ps1 -Preview` emit only a reference capsule; omit full worktree lists and copied
   policy/prompt bodies while preserving StartTask/queue/read-only stop semantics.
3. Specify Orchestrator loop: read minimal facts, plan/apply at most one transition, dispatch at
   most one role, stop; never wait in that same turn.
4. Record role-start/end/blocker/direction/heartbeat event digests and suppress identical waits.
5. Measure all before/after byte and item budgets in deterministic test output/evidence.

Stop if compacting removes task identity, authority, scope/locks, gate, stop conditions, or full-
read fallback.

### Step A5 — Developer package handoff and bounded fix (completed)

- Run all new A modules; existing execution gate/recovery, WIP/Quick Fix, worktree, Markdown
  archive, and permanent-role regression suites; Python compilation; PowerShell parse; diff/check,
  allowlist, forbidden-product, protected V2/registry/bundle hashes, and production zero-write
  inspect/plan.
- Record exact baseline/after metrics and simulated callback-to-dispatch timing.
- Exact-path stage task-owned lane files only, commit locally, leave lane/index clean, write
  Developer evidence `ready_for_review`, and stop.
- On Reviewer block, change only the approved helper/test subset named in the Task's bounded-fix
  contract plus Developer evidence. Close B1-B5 with adversarial regressions, rerun the complete
  `105`-test baseline and every safety/performance gate, commit cleanly, and return to full Reviewer
  re-gate. Do not weaken the frozen contract or edit primary board/history.

### Step A6 — Historical Reviewer gate (completed)

- Full independent review; A cannot use its own new compact read or transition path to reduce this
  review.
- Reproduce all state transitions, invalid-state families, archive safety, budget checks, and
  no-shell/no-path-escape/no-partial-write properties in disposable repositories.
- Verify production apply is impossible outside sole `gate_running/Integrator` and the deleted
  token-null audit exception is absent.
- Blocking findings return to Developer; Reviewer never fixes or merges.

### Step A7 — Historical mandatory QA (completed)

- Validate final reviewed HEAD from a clean lane/temp worktree/exact archive.
- Run the complete A validation matrix on Windows, including fault injection and second/third
  closeouts.
- Run one event-driven controlled pilot and require callback-to-dispatch <=90 seconds, zero Planner
  launches, one transition/dispatch max, and budget reports.
- QA does not mutate production board/history or product data.

### Step A8 — Historical Integrator merge and blocked first migration

1. Verify exact package, ancestry, Reviewer/QA pass, clean primary/lane, protected paths, and no
   remote/destructive action.
2. Merge locally under existing authorization.
3. While A remains sole token owner in `gate_running/Integrator`, run exact production
   `plan-maintenance`, confirm current board source hash and archive/index non-conflict, then run one
   guarded `apply-maintenance`.
4. Prove byte-exact rollback into temp, index chain, active summary, budgets, existing execution
   gate, and merged-tree A regressions.
5. Record metrics/residuals, then release token in the normal terminal closeout commit. Do not
   retire a dirty/unintegrated worktree or push.

The merge completed, but the first migration stopped at `BLOCKED_MAINTENANCE_GATES` with zero
writes. The pending amendment above replaces only the retry portion. Stop if migration target/
hash/role/token/state changed, or any quantitative target fails.

## 5. Validation Matrix

1. each valid routine event produces the exact next state/role and retains token/task/lane/locks;
2. Reviewer pass uses QA unless immutable approved metadata explicitly omits QA;
3. missing/wrong state, role, owner, task, lane, primary HEAD, or lane HEAD blocks zero-write;
4. missing/wrong evidence path/commit/blob/hash/status or broken ancestry blocks zero-write;
5. dirty primary/lane/index, scope drift, lock drift, queue/pause/QF/parallel drift blocks;
6. JSON-summary mismatch, duplicate markers, malformed metadata, unknown callback/event blocks;
7. exact duplicate transition is zero-write; divergent duplicate blocks;
8. injected write interruption restores original board bytes;
9. first board migration archives byte-exact source and produces chained index/rollback proof;
10. active/queue/paused/QF/parallel/residual/current/proposed facts never enter terminal archive;
11. under all thresholds is zero-write; each individual threshold triggers deterministic plan;
12. second and third closeouts compact correctly and keep generation/index continuity;
13. same generation is idempotent; different existing archive, corrupt index, path escape blocks;
14. partial failure restores board/index and removes only the exact new helper-owned artifact;
15. compact board <=400 lines/65536 bytes and has one JSON block/one derived summary;
16. Orchestrator turn performs <=1 transition and <=1 dispatch and contains no same-turn wait;
17. callback accepts only seven ordered fields and <=1024 bytes;
18. dispatch/template/capsule/minimal-read and core file budgets pass;
19. invalid ref/unsafe omission -> `FULL_READ_REQUIRED`; unrelated archive drift alone does not;
20. cadence accepts start/end/blocker/direction/>=60s and suppresses unchanged waits;
21. controlled pilot has zero Planner routine turns and <=90s callback-to-dispatch;
22. execution gate/recovery, WIP/Quick Fix/reconciliation, worktree/archive/role suites pass;
23. product/V2/registry/bundle/retained lanes/remote/runtime remain unchanged.

## 6. Migration And Rollback

No in-place production migration occurs before merge and QA. The first production apply is one
Integrator action with exact source facts. The immutable archive is historical; the compact board
remains authority. Rollback requires Git revert or a separately approved exact patch whose bytes
are reconstructed and hash-verified from the index into a temp path. Neither Planner nor helper
silently restores production authority.

## 7. Performance Evidence

Developer, Reviewer, QA, and Integrator evidence must include a common metrics table: board/core
files/dispatch/callback/capsule/default resolved read-set bytes; Orchestrator items/turn; transition
Planner launches; callback-to-dispatch duration; writes/no-op count; retries. Baseline includes the
repository values and TASK_368E durations in the task. Acceptance requires every hard budget and
the <=90-second pilot target; correctness alone is insufficient.

## 8. Exact Scope And Gates

The Task file's enumerated May Touch, Must Not Touch, Locked Paths, lane identity, and role gates
are normative. Any additional path, execution-gate write change, product/V2/registry/bundle change,
parallel owner, live Developer board write, unreviewed compaction, push, or destructive action is
a Planner/User blocker.

## 9. Historical Stop Point (superseded)

The prior `developer_dispatch_ready` stop was consumed by the atomic transition committed at
`5cd7f02a...`. It is retained only as audit history. Current authority is the pending amendment
above: Task A remains the sole token owner in `gate_running/Reviewer`, lane `70e5c6a...` remains
clean, and no role may be dispatched until the User resolves the recorded authority ordering.
