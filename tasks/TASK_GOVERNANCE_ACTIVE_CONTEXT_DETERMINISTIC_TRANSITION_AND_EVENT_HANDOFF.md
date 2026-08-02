# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF

Status: `integration_reconciliation_amendment_pending_user_approval`

Type: governance / execution-authority / orchestration-efficiency

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Owner at this gate: Task A remains the sole token owner in `gate_running/Reviewer`; the exact lane
and primary are clean at the committed atomic transition result, but Reviewer has not been
dispatched.
Next authority: User review of the post-transition dispatch/idempotency reconciliation amendment
below. No board/lane/helper/test/contract/skill/protocol or role-dispatch write is authorized by
this planning checkpoint.

## Pending Post-Transition Dispatch And Idempotency Reconciliation Amendment

### Discovery Gate

Confirmed by User:

- Preserve the successful atomic transition and its one real `DEVELOPER_READY` history entry;
  never reopen the one-use bootstrap or fabricate/backfill role history.
- Exact duplicate recognition must prove the complete committed transition before consumed-
  bootstrap rejection. Gate roles require a new explicit `GateDispatch`; implementation roles
  remain on `ImplementationDispatch`.
- The current Reviewer may be dispatched only through a one-use attestation bound to the exact
  post-transition facts and may write only genuine Reviewer evidence.
- Reviewer, bounded Developer fix, full Reviewer, mandatory QA, and Integrator remain serial;
  Task B stays unapproved/unstarted.

Confirmed by repository:

| Fact | Exact binding |
|---|---|
| Primary | clean `master@1e60af997e5ce042d9e2f9ae8cc7c4b4469a3570`; its planning delta after atomic board-only commit `5cd7f02acd02c03008f29de900e841a185a9d138` is only Task/Plan/Planner evidence; board blob remains `972b1c2386145114cb3daa35037913d709bb5180`, SHA-256 `3e57b913098e565de3fee8f4a0ffdff597e3d7fdfec5232fe63027298f1a2507` |
| Authority | Task A sole token, `gate_running/Reviewer`, active/lane HEAD `70e5c6a7606284e1fc55ac6b0497c6d9756b665f`, payload digest `f2ddca5a8f84f4f8a966410852983571006f2810028ea0a82e33df8ed7ef0a03`, queue empty, paused/Quick Fix/parallel null |
| Transition | ID `367e000d5a4c93e060039b5a3cfd4f1ad88ac096500a994c62d8bdea94399968`; plan digest `5ac92b5060cbde4d647c0d173f9773119bc18ed360de5dd7650f180b8edf2f96`; bootstrap ID `b1605205d969bd5a0110383ede944018786fb7a2c94e708076b72fc33ed4cfb3`; exactly one real history event |
| Evidence | Developer ref at `70e5c6a...`; blob `e9d528a9c2b63b4a87dfcc6eaac74232942eeb54`; SHA-256 `1bee1cfea13e128d92311457ff3d6c3ca02d57167e588f2d90290782a05e6e56`; status `ready_for_review` |
| Read-only probes | identical bootstrap plan returns `BLOCKED_TRANSITION_METADATA_BOOTSTRAP`; production `ImplementationDispatch` returns `BLOCKED_DISPATCH_STATE`; both zero-write |
| Implemented sizes | lane coordinator `460`, proof `300`, existing transition unit `390`, proof unit `153`, recovery `78`, candidate integration `165`, contract `123`; gate `307`; existing gate unit/integration `496/489` |

Planner inference:

- Exact committed duplicate recognition belongs to both `plan` and `apply`, through one shared
  proof classifier that runs before consumed-bootstrap rejection. `plan` reports the durable
  result; identical `apply` replay reports the same result only when its original snapshot/plan
  bindings also match.
- `GateDispatch` is a read-only gate intent, not a transition or second state machine. It needs
  two new bounded test modules because the existing gate unit/integration modules are already
  `496/489` lines.
- The current Reviewer attestation can make the first dispatch reference-exact and drift-expiring,
  but cannot itself change state or repair code.

User-authorized planning resolution:

- The current non-bootstrap transition path still cannot consume a genuine `REVIEWER_BLOCKED`
  because it incorrectly equates the approved scope-contract commit with immutable Git base and
  textual May Touch with the broader lock set. The User has now authorized planning of one exact
  Task-A-only bridge; this is not implementation approval.
- The bridge is unavailable until the permanent Reviewer creates genuine evidence-only checkpoint
  `R`. It then authorizes only the same Developer, while durable authority remains
  `gate_running/Reviewer`, to produce exact fix checkpoint `F`. The repaired existing helper—not a
  manual board edit or second state machine—must atomically validate and adopt `F` before any
  Developer evidence checkpoint `E` is created.

### Amendment A — committed duplicate/idempotency

Both `plan` and `apply` must first classify an apparent exact duplicate without invoking the
ordinary consumed-bootstrap path. The classifier must prove all of:

1. input event/task/lane/source primary/source board/candidate/evidence/status exactly match the
   committed `last_transition` and sole matching history entry;
2. current primary is a clean one-parent commit whose parent is the original source primary and
   whose only changed path is `docs/task_board.md`;
3. source-parent board blob, rendered current board blob, candidate/evidence commit/blob/SHA,
   transition ID, original source snapshot, plan digest, bootstrap ID and complete bootstrap bytes
   recompute exactly;
4. current active state/role/HEAD/evidence/locks/context equal the proven target and the one-use
   bootstrap remains consumed, separate, and unchanged.

Exact `plan` and exact `apply` replay return zero-write `ALREADY_APPLIED` with the original IDs;
apply additionally requires the original expected snapshot and plan digests. An identical
uncommitted replacement remains `RECOVERY_TRANSITION_COMMIT_REQUIRED`. Any stale, divergent,
tampered, partial, rewritten, dirty, different-input, extra-path, extra-history, or later-commit
shape fails closed; no bootstrap is reopened and no event is appended.

### Amendment B — explicit role-specific GateDispatch

Add only `GateDispatch` to `scripts/connlab_execution_gate.ps1`; do not broaden or alias
`ImplementationDispatch`. Normative interface:

```text
powershell -File scripts/connlab_execution_gate.ps1 -Intent GateDispatch \
  -TaskId <task> -Lane <lane> -GateRole <Reviewer|QA|Integrator> \
  -EvidencePath <exact target role evidence path> \
  [-DispatchAttestationRef <path@commit#sha256>] -RepositoryRoot <primary> -Json
```

It validates exact task/token/lane/active role/required gate, clean primary, exact branch/worktree/
index and board-versus-physical HEAD, base ancestry, 35-path lock digest after the approved scope
update, active evidence/context/last-transition binding, exact target role evidence path, and the
role write boundary. Reviewer and QA may initially write only their exact lane evidence path;
Integrator may initially write only Integrator evidence and perform read-only premerge checks—
merge/board/maintenance authority remains separately gated. Developer/Quick Fixer continue to use
only `ImplementationDispatch`. Missing/wrong role/gate/evidence/context/attestation or dirty/drifted
Git facts return stable `BLOCKED_GATE_DISPATCH_*`, zero-write.

### Amendment C — one-time current Reviewer dispatch attestation

After the User approves the final planning commit, that immutable Task/Plan/Planner commit plus the
exact User approval message/source-thread digest form the approval contract; no second planning
amendment or board prewrite is required. The one-time dispatch capsule derives one canonical
`dispatch_id` from exact primary/board facts rooted at `5cd7f02a...`,
board blob/SHA/payload, Task A token/state/role, lane/branch/worktree/base/HEAD `70e5c6a...`, ordered
32 locks/digest, current Developer evidence ref/blob/SHA/status, permanent Reviewer thread identity,
exact Reviewer evidence path, final planning ref, User approval digest, clean statuses, and null
queue/pause/Quick Fix/parallel facts. It authorizes only the permanent Reviewer full review and
Reviewer-evidence write. Same-input delivery retry is the same dispatch identity, never a second
authorization; any Git/board/evidence/thread-target/input drift expires it. A genuine block must
produce `reviewer_blocked`; `R` records the exact planning ref and User approval digest so later
validation is durable. No Developer byte, board prewrite, synthesized evidence/history,
manual reversal, generic bypass, QA/Integrator dispatch, or Task B action is permitted.

### Amendment D — one-time Reviewer-blocked atomic authority bridge

This amendment defines exactly three immutable lane checkpoints, resolved only after User approval:

1. `R`: the direct clean descendant of `70e5c6a...` that changes only the exact Task A Reviewer
   evidence path, whose final machine record is `Reviewer/reviewer_blocked` and which binds the
   approved amendment and one-time Reviewer dispatch identity;
2. `F`: a clean linear descendant of `R` whose `R..F` delta is exactly the eleven sorted fix paths
   below, with no merge, role evidence, board, product, migration, archive, or unrelated path;
3. `E`: the direct clean child of `F`, created only after the bridge board commit, changing only the
   exact Task A Developer evidence path to final `Developer/ready_for_review`.

The same permanent Developer receives a single-use bridge dispatch bound to the approval contract,
source primary/board, `70e5c6a...`, `R`, exact lane identity, scope/locks and Reviewer evidence. The
Developer may create `F` but may not write `docs/task_board.md`, role evidence at `E`, or any path
outside `R..F`. The existing transition helper at `F` consumes event `REVIEWER_BLOCKED` in special
mode `task_a_reviewer_blocked_atomic_bridge_v1`; it does not add an event, state, CLI writer, or
general bypass.

Bridge plan/apply validates in order: exact User-approval contract and unconsumed bridge identity;
clean primary with the unchanged board blob/payload; sole Task A token and exact source state/role/
HEAD/context; clean exact branch/worktree/index at `F`; linear ancestry
`15c3120a... -> 70e5c6a... -> R -> F`; exact evidence-only `70e5c6a..R`; exact sorted `R..F` paths and
digest `74a731dd33e912fe3fb55f18ace9cbc0c7e5f7f0ff1b917c74934968de6793d0`;
Reviewer evidence path/commit/blob/SHA/status; approval scope manifest and its subset-of-lock proof;
32-to-35 lock update; helper/proof/gate blobs at `F`; retained context; transition/plan/bridge IDs;
and byte-exact render. Every mismatch returns stable `BLOCKED_TASK_A_REVIEWER_BRIDGE_*` with zero
writes. Apply uses the existing temp/fsync/replace/reload recovery boundary and creates one primary
board-only commit; an exact committed replay may return `ALREADY_APPLIED` only through the complete
duplicate proof. The single-use bridge is consumed by its unique history entry and cannot bind
another task, Reviewer result, `R`, `F`, board, primary, scope, lock set, generation, or later event.

Post-bridge machine authority is exact:

- token owner and Task/lane/branch/worktree/base/required gates stay unchanged;
- `execution_state=implementation_running`, `active.role=Developer`, `active.head_sha=F`;
- `active.evidence` and top-level `evidence` are the exact Reviewer evidence ref at `R`;
- `active.scope_contract_ref` is the final planning Task blob approved by the User, and new frozen
  `active.scope_approval_ref` is the exact Reviewer evidence ref at `R` carrying that approval
  digest; subsequent normal transitions require both and retain them;
  `active.may_touch_digest=b79e6f4b51d447efa3fe451af6155982d8a23d934c895a15cc1bf067a9b74c37`;
  `active.locked_paths` is the exact 35-path list and `locked_paths_digest=a45c3bcd...16d51347`;
- `active.last_transition_id` points to one new canonical bridge transition; `last_transition`
  equals that entry and `transition_history` appends exactly one genuine `REVIEWER_BLOCKED` entry
  with `transition_mode`, source primary/board, expected board HEAD `70e5c6a...`, Reviewer checkpoint
  and evidence commit `R`, adopted fix/lane checkpoint `F`, separate evidence/fix path digests,
  approval/scope/lock/retained-context/helper proofs and the derived bridge/transition/plan IDs;
- the consumed `transition_metadata_bootstrap`, queue, paused, Quick Fix, parallel and residual
  values remain byte-identical. No Reviewer or Developer history is fabricated or backfilled.

After the bridge commit, the authorized Developer creates `E`. Normal `DEVELOPER_READY` is legal
without a preliminary board HEAD write because the helper requires the immediate prior history entry
to be this exact bridge, revalidates `R..F` and the helper blob at `F`, requires `F..E` to be exactly
Developer evidence and the helper/proof/gate blobs to remain unchanged, then carries the already-
adopted fix digest into the new normal event. The atomic transition adopts `E`, writes Developer
evidence, moves to `gate_running/Reviewer`, and replaces `last_transition`; the bridge remains only
as immutable history and is no longer eligible as the immediate predecessor, so the evidence-only
Developer route cannot replay or generalize.

### Exact proposed scope, locks, and ceilings

Future Developer May Touch only after User approves this amendment and exact `R` is proven:

1. `scripts/connlab_execution_transition.py`
2. `scripts/connlab_execution_transition_proof.py`
3. `tests/unit/test_connlab_execution_transition_proof.py`
4. `tests/integration/test_connlab_execution_transition_recovery.py`
5. `tests/integration/test_connlab_execution_transition_candidate_adoption.py`
6. `scripts/connlab_execution_gate.ps1`
7. `tests/unit/test_connlab_gate_dispatch.py` (new)
8. `tests/integration/test_connlab_gate_dispatch_recovery.py` (new)
9. `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
10. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
11. `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
12. Task A Developer evidence

The route-wide effective May Touch manifest is the sorted eleven implementation paths above plus
the exact Task A Developer/Reviewer/QA/Integrator evidence paths and `docs/task_board.md`; its
canonical digest is `b79e6f4b51d447efa3fe451af6155982d8a23d934c895a15cc1bf067a9b74c37`.
`R..F` must contain all and only the first eleven sorted paths; `F..E` must contain only Developer
evidence. Reviewer/QA/Integrator commits remain their exact evidence-only paths and the primary
board remains helper-only. This 16-path manifest is deliberately a strict subset of the 35 locks;
the repaired proof validates both digests and subset coverage and must never require May Touch to
equal Locked Paths.

The unique machine-readable scope authority is:

<!-- CONNLAB_TASK_A_POST_TRANSITION_SCOPE_V1_BEGIN -->
```json
{
  "schema": "connlab.task-a-post-transition-scope",
  "version": 1,
  "bridge_fix_paths": [
    ".agents/skills/connlab-lane-orchestrator/SKILL.md",
    "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
    "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
    "scripts/connlab_execution_gate.ps1",
    "scripts/connlab_execution_transition.py",
    "scripts/connlab_execution_transition_proof.py",
    "tests/integration/test_connlab_execution_transition_candidate_adoption.py",
    "tests/integration/test_connlab_execution_transition_recovery.py",
    "tests/integration/test_connlab_gate_dispatch_recovery.py",
    "tests/unit/test_connlab_execution_transition_proof.py",
    "tests/unit/test_connlab_gate_dispatch.py"
  ],
  "bridge_fix_digest": "74a731dd33e912fe3fb55f18ace9cbc0c7e5f7f0ff1b917c74934968de6793d0",
  "may_touch": [
    ".agents/skills/connlab-lane-orchestrator/SKILL.md",
    "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md",
    "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_integrator.md",
    "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_qa.md",
    "docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_reviewer.md",
    "docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md",
    "docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md",
    "docs/task_board.md",
    "scripts/connlab_execution_gate.ps1",
    "scripts/connlab_execution_transition.py",
    "scripts/connlab_execution_transition_proof.py",
    "tests/integration/test_connlab_execution_transition_candidate_adoption.py",
    "tests/integration/test_connlab_execution_transition_recovery.py",
    "tests/integration/test_connlab_gate_dispatch_recovery.py",
    "tests/unit/test_connlab_execution_transition_proof.py",
    "tests/unit/test_connlab_gate_dispatch.py"
  ],
  "may_touch_digest": "b79e6f4b51d447efa3fe451af6155982d8a23d934c895a15cc1bf067a9b74c37",
  "locked_paths_count": 35,
  "locked_paths_digest": "a45c3bcd9051af6570bc386c0384aa11865d346e027f4d9f10afadaa16d51347"
}
```
<!-- CONNLAB_TASK_A_POST_TRANSITION_SCOPE_V1_END -->

The helper must require exactly one marker pair and canonical JSON/digests from the approved Task
blob. The historical broad `## Exact May Touch` section remains original-task audit context and is
not the authority for this bounded reconciliation.

Later role/primary May Touch: exact Task A Reviewer/QA/Integrator evidence and
`docs/task_board.md` only through the reviewed atomic helper. The final Task/Plan/Planner planning
commit is frozen after User approval; no second amendment or ambient approval edit is part of this
route. Existing mixed
transition unit, gate unit/integration, active-context/maintenance/handoff helpers/tests, execution
policy, Planner/other skills/protocols, registry/bundle, archive/index/audit, Task B/umbrella,
product/data/runtime/release/remote and protected lanes are Must Not Touch.

The next legal atomic scope transition must validate source 32-lock digest
`93bbeff0bc0a085c4e4321f5ceb1bea94e1977383cce2521f05e8ed46734c16c` and install exactly three
ordered additions—execution gate after `run_task.ps1`, gate-dispatch unit after proof unit, and
gate-dispatch recovery after candidate-adoption integration—yielding 35-lock digest
`a45c3bcd9051af6570bc386c0384aa11865d346e027f4d9f10afadaa16d51347`. No ambient lock edit.

Ceilings: transition coordinator `<=460`, proof `<=360`, proof unit `<=300`, transition recovery
`<=120`, candidate-adoption integration `<=380`, execution gate `<=360`, new gate unit `<=320`,
new gate integration `<=300`, contract `<=160`, Orchestrator skill `<=16384` bytes, and orchestration
protocol `<=12288` bytes. Existing 390/496/489-line mixed tests receive no new matrix.

### TDD checkpoints, gates, and stop

After one-time Reviewer dispatch: D0 authentic clean evidence-only `R`; D1 same-Developer bounded
RED while board remains Reviewer; D2 duplicate/bridge proof and coordinator ordering; D3
GateDispatch plus new bounded tests; D4 contract/skill/protocol alignment; D5 clean exact fix
checkpoint `F`; D6 zero-write bridge plan then atomic bridge apply; D7 evidence-only `E` and normal
`DEVELOPER_READY`. The remaining route is full Reviewer -> `REVIEWER_PASS` -> GateDispatch QA ->
`QA_PASS` -> GateDispatch Integrator. Reviewer/QA evidence deltas remain evidence-only.

Validation must cover plan/apply/reconnect/replay current real shape, every duplicate/tamper/drift,
all three GateDispatch roles and write boundaries, current one-time Reviewer attestation, role/state/
gate/evidence/cleanliness/lock/context negatives, full Task A regression, Python compile,
PowerShell AST, static purity/state-machine checks, ceilings, exact allowlist, protected hashes,
production zero-write probes, independent Reviewer, mandatory QA, and Integrator. No maintenance
migration/compression, merge, push, cleanup, restart, or Task B work belongs to this amendment.

Execution-efficiency boundaries are normative:

- This is one bounded Task A reconciliation amendment, not a new task/Discovery/lane. It solves
  only committed exact duplicate/idempotency and Reviewer/QA/Integrator GateDispatch; the one-time
  current Reviewer attestation is the exact bootstrap for GateDispatch, not a third general feature.
- Do not redesign transition states, maintenance, handoff, board compression, Task B, or any
  product/frontend/release behavior. No new task, branch, worktree, role thread, dependency, or
  authority path is allowed.
- Developer runs focused RED/GREEN plus one final Task A governance regression. Reviewer reviews
  the complete committed diff and concentrates on duplicate/replay/GateDispatch/wrong role/state/
  head/dirty/divergent negatives. QA runs the complete Task A regression exactly once on the final
  reviewed HEAD. Product tests, frontend build, release and unrelated historical matrices are
  forbidden; evidence-only checkpoints do not repeat a full suite without a new risk reason.
- Reviewer may return at most one normal bounded fix pass. A repeated same-class design failure,
  third scope round, new authority path, or out-of-allowlist need stops to User; automation must not
  expand Task A again.
- Atomic commit `5cd7f02a...` remains immutable. Until an approved legal transition, board remains
  `gate_running/Reviewer` and the existing lane remains clean `70e5c6a...`. Every `BLOCKED_*`
  outside the one exact current Reviewer attestation remains blocking; no ignore/force/general
  bypass is introduced.

Definition of Ready is satisfied for User review. The bridge closes the known authority ordering
without another state machine or manual board mutation; no further bootstrap deadlock is known.
Implementation remains prohibited until the User approves this exact amendment. If `R`, `F`, `E`,
scope, locks, approval facts or immediate-predecessor proof cannot meet this contract, stop to User
without another exception or scope expansion.

## Approved Routine Transition Metadata And Candidate-HEAD Reconciliation

### Exact User approval record

The User explicitly approved the amendment at
`d7994d264db1d7314d916a9773c95722e9201958` and stated:

> I approve Task A's routine-transition authority reconciliation amendment at
> d7994d264db1d7314d916a9773c95722e9201958 and authorize one bounded continuation in the existing
> Developer lane, followed by automatic atomic Developer→Reviewer transition, full Reviewer,
> mandatory QA, and Integrator. Task B remains unapproved and unstarted.

This approval activates only the exact pure-support extraction, 13-path durable-to-final candidate
allowlist, first-transition 29-to-32 lock reconciliation, physical-line ceilings, C0-C4 TDD
checkpoints, and serial Reviewer/QA/Integrator route recorded below. It does not authorize a
general gate bypass or any preliminary board write.

### Discovery decision

The approved legacy-maintenance bootstrap package is complete and clean, but the first routine
`DEVELOPER_READY` handoff now exposes two independent fail-closed gaps:

1. the durable Task A active record predates the new frozen transition metadata and therefore the
   helper stops at `BLOCKED_TRANSITION_METADATA`;
2. the helper and production dispatch gate currently treat the durable board lane HEAD and the
   callback candidate lane HEAD as the same value, so a legitimate new candidate stops at
   `BLOCKED_ACTIVE_HEAD_DRIFT` before it can be adopted.

The original Task A scope includes the transition helper, its unit/recovery tests, and the
normative contract. However, the later approved legacy-bootstrap amendment explicitly locked
those paths read-only. Repairing this behavior therefore required the explicit User-approved
scope/authority amendment now recorded at `d7994d26...`. It is not a routine callback and does not
reuse or generalize any prior approval.

### Immutable reconciliation anchors

| Fact | Exact binding |
| --- | --- |
| Primary planning anchor | clean `master@49911ae626daf646836471246a223496dc7ea771`; no `MERGE_HEAD` |
| Durable authority | Task A sole token, `implementation_running/Developer`, active `head_sha=3e73761673fd75de4e79028b0b8d0b89979bbd1a`, payload digest `124cbc003ab8322cf2208d742e9a59d971875ab44773400d3607833cab283be8` |
| Candidate lane | clean exact branch/worktree at `aeb7709128361782800d2da5a473d730d48df652`; base `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`; implementation checkpoint `dc8f1fef42c874523b5706da3c8d92fa8391c475` |
| Candidate evidence | `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@aeb7709128361782800d2da5a473d730d48df652`; blob `104387574e995f2b6caf4bf1ceacfab76a748c64`; SHA-256 `3d53242ba53f899bd9656e37e33508f6b74d57b711fd5926f39e1a4d67d2157c`; `Developer/ready_for_review` |
| Candidate delta | exactly six paths: Developer evidence, legacy-bootstrap source attestation, bounded active-context hook, Task-A bootstrap module, and its two bounded tests |
| Validation | external seven-field callback `ALLOW_CALLBACK`; bootstrap `50 passed`; existing Task A `133 passed`; gate `BLOCKED_ACTIVE_HEAD_DRIFT`; transition plan `BLOCKED_TRANSITION_METADATA`; all zero-write |

The primary anchor and candidate are parallel descendants of the durable board anchor: primary
adds only the approved four governance paths, while the candidate adds only the approved six-path
Developer package. The reconciliation must preserve both histories without reset, rebase,
cherry-pick, or preliminary board mutation.

### A. One-time legacy active-record metadata initialization

The first successful `DEVELOPER_READY` transition may initialize missing transition metadata only
as part of the same atomic board replacement that adopts the reviewed callback candidate and
moves to `gate_running/Reviewer`. It must never perform a metadata-only or board-HEAD-only write.

The canonical `transition_metadata_bootstrap` attestation is structurally separate from
`transition_history` and binds:

- exact Task A identity, immutable base, original approved Task blob, latest User-approved Task/
  Plan amendment refs, effective May Touch digest, source 29-path board Locked Paths digest
  `df114c309a21657d155401a591bb4a05b960ea9ef3854125713fe149509e2907`, and approved expanded
  32-path Locked Paths digest `93bbeff0bc0a085c4e4321f5ceb1bea94e1977383cce2521f05e8ed46734c16c`;
- the exact primary anchor, source board hash/payload digest, durable board HEAD, blocked candidate
  `aeb77091...`, Developer evidence path/commit/blob/SHA/status, exact six-path delta, clean branch/
  worktree/index, and base/durable/candidate ancestry;
- the future bounded-fix implementation/evidence candidate as a descendant of `aeb77091...`, with
  no path outside the newly approved amendment delta;
- a canonical `bootstrap_id`, single-use marker, and exact transition plan/ID.

The active `scope_contract_ref`, `may_touch_digest`, `locked_paths_digest`, and
`last_transition_id` are initialized from these proven facts. The first atomic transition must
also replace the source 29-path lock list with the approved 32-path list by inserting only the
three new support/test paths named below. The May Touch contract and board Locked Paths are hashed
independently: they are not required to be textually identical because the approved Task contains
role-owned prose paths while the board contains operational wildcard locks. Every actual delta
must satisfy both the effective approved scope and the expanded locked-path policy. No preliminary
lock, metadata, or board-HEAD write is permitted.

Any different task, primary/source board, durable/candidate HEAD, evidence byte/status, branch,
worktree, base, ancestry, scope, lock, role/state/token, queue/paused/Quick Fix/parallel/residual
context, dirty state, or prior bootstrap/history blocks with zero writes. The bootstrap cannot be
used by another task, another candidate, a later transition, or maintenance generation. It never
creates or represents historical `DEVELOPER_READY`, `REVIEWER_PASS`, or `QA_PASS` events.

### B. General atomic callback candidate-HEAD adoption

Routine transition inputs distinguish:

- `expected_board_head`: the currently durable lane checkpoint recorded in board authority;
- `candidate_lane_head`: the new callback/evidence commit physically checked out in the exact
  lane worktree.

The helper must prove `expected_board_head` is an ancestor of `candidate_lane_head`, the candidate
branch/worktree/index is clean, and the exact range conforms to the event-specific delta contract.
The evidence ref must resolve at the candidate commit and bind its Git blob, SHA-256, current role/
status envelope, task identity, and ancestry. A single atomic board replacement then updates
`active.head_sha`, `execution_state`, `active.role`, `active.evidence`, `last_transition_id`,
`last_transition`, and `transition_history`; on the one legacy transition it also writes the
separate metadata-bootstrap attestation, frozen active metadata, and exact expanded 32-path lock
list. No preliminary unbound board HEAD, metadata, or lock update is permitted.

Event delta rules are normative:

- `DEVELOPER_READY`: implementation/test/contract changes must be inside the effective approved
  scope and locks, followed by the exact Developer evidence candidate; an implementation
  checkpoint followed by a later evidence commit is valid.
- `REVIEWER_BLOCKED` and `REVIEWER_PASS`: the durable-to-candidate delta is evidence-only at the
  exact Task A Reviewer evidence path. No implementation/helper/test/contract drift is allowed.
- `QA_PASS`: the delta is evidence-only at the exact Task A QA evidence path; any post-review
  implementation/helper/test/contract drift blocks.

Stale, rewritten, divergent, dirty, scope/lock drifted, evidence-spoofed, evidence-only
impersonation, post-review implementation drift, or duplicate-conflicting candidates fail closed.
`ALREADY_APPLIED` is valid only after the identical complete board-only transition commit is
proven: exact source parent, exact rendered board blob, exact candidate/evidence/bootstrap/plan/
transition proof, and no other changed path. An identical uncommitted post-replace board returns a
distinct recovery-required result, never `ALREADY_APPLIED`.

### Exact approved bounded scope

Developer May Touch:

1. `scripts/connlab_execution_transition.py`
2. `scripts/connlab_execution_transition_proof.py` (new pure proof/render support module)
3. `tests/unit/test_connlab_execution_transition.py` (compatibility assertions only)
4. `tests/unit/test_connlab_execution_transition_proof.py` (new bounded pure-proof matrix)
5. `tests/integration/test_connlab_execution_transition_recovery.py` (compatibility assertions only)
6. `tests/integration/test_connlab_execution_transition_candidate_adoption.py` (new bounded
   disposable-Git real-shape matrix)
7. `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
8. `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md`

Role/primary governance May Touch:

9. Task A Reviewer, QA, Integrator, and Planner evidence at their existing exact role paths
10. this Task and Plan
11. `docs/task_board.md` only through the reviewed helper's atomic routine transition; never as an
   ambient Planner/manual candidate-HEAD or metadata-only update

The decomposition is fixed. `scripts/connlab_execution_transition.py` remains the only CLI,
Git/board/evidence reader, legal state-machine coordinator, atomic writer/recovery coordinator, and
stable result-code emitter. `scripts/connlab_execution_transition_proof.py` is side-effect-free and
owns only immutable proof values, canonical hashes/serialization, durable-to-candidate delta and
event validation, Task-A bootstrap validation, transition/plan identity construction, and pure
rendering from already verified inputs. It must not parse a CLI, run Git/subprocesses, inspect a
worktree/filesystem, write/replace files, route roles, or mutate authority; it is not a second state
machine.

Physical-line ceilings are acceptance gates: coordinator `<=460`, proof support `<=360`, existing
unit compatibility module `<=399`, new proof unit module `<=360`, existing recovery compatibility
module `<=120`, new candidate-adoption integration module `<=380`, and normative contract `<=160`.
No other helper or mixed test module may absorb the new matrix.

Must Not Touch / Locked:

- `scripts/connlab_active_context.py`, `scripts/connlab_task_a_legacy_bootstrap.py`, their source
  attestation and bootstrap tests, `scripts/connlab_handoff_contract.py`, `scripts/run_task.ps1`,
  execution gate, worktree/maintenance helpers, all other Task A policies/skills/protocols/tests,
  archive/index/audit, registry/bundle, V1/V2, Task B/umbrella, product/data/runtime/release/remote
  paths, and retained/frozen/cancelled lanes are read-only.
- The current board stays byte-unchanged until the future first atomic transition. On that
  transition only, its ordered lock list expands from 29 to 32 entries by inserting
  `scripts/connlab_execution_transition_proof.py` after the coordinator,
  `tests/unit/test_connlab_execution_transition_proof.py` after the existing transition unit test,
  and `tests/integration/test_connlab_execution_transition_candidate_adoption.py` after the
  existing recovery test. Any other ordering/path/digest blocks zero-write. No parallel exception,
  new task, branch, or worktree is allowed.

Implementation checkpoints are exact: C0 clean `aeb77091...`; C1 pure extraction with current
transition/recovery compatibility plus the full `133` baseline green and no behavior change; C2
RED in the two new bounded test modules without fixture board-HEAD pre-overwrite; C3 the seven-path
implementation/contract checkpoint; C4 Developer evidence-only final checkpoint, clean and
`ready_for_review`. Reviewer must independently prove the coordinator is the sole state machine/
writer, the support module is statically side-effect-free, all ceilings and the exact 13-path
package hold, real-shape fixtures preserve the prior durable board HEAD, bootstrap `50` and Task A
`133` plus new focused/full protected-state suites pass, and duplicate/recovery/role-delta rules
fail closed. QA remains mandatory and Integrator must retry only on the final reviewed/QA ancestry.

### Approved route and stop condition

Under the exact approval above, the same permanent Developer may perform one bounded continuation
in the existing lane from `aeb77091...`. This is a one-time bootstrap continuation under the unchanged
sole `implementation_running/Developer` token, not a generic gate bypass; it exists only because
the legacy gate cannot authorize the helper repair that makes candidate adoption possible. The
approval governance must bind the exact anchors and allowlist above, and any drift returns to
Planner/User.

Developer produces a clean fix/evidence candidate. From durable board HEAD `3e737616...` to that
candidate, the allowlist is exactly the prior six-path package plus the seven implementation/
contract paths above, with the Developer evidence path updated in place: `13` distinct paths and
no other byte. The repaired helper then performs one atomic
metadata-bootstrap plus `DEVELOPER_READY` adoption, after which a full independent Reviewer
re-gate, mandatory QA, and Integrator retry are required. No live migration occurs until the new
Reviewer/QA passes. Task B and the umbrella remain unapproved/non-executable.

## Integrator Blocked Checkpoint

- The exact QA lane was merged locally without conflict by non-fast-forward merge
  `a42ca37e205127afd87d4cdc1d26ede53830522c`; its first-parent delta is the frozen 26-path package.
- Reviewed `plan-maintenance` returned generation 1 and plan digest
  `519ee4f53e1887c524d59971b40a0e1749f4911cd2b032a41237584caaacc497` for source-board SHA-256
  `922532265c3b27363c091ea6eae32420fdcc6c31832d44988bd5296a7cbcf2f6`.
- The exact `apply-maintenance` handshake failed closed with
  `BLOCKED_MAINTENANCE_GATES: required transition evidence is missing or ambiguous` and zero
  writes. The live legacy board has no `transition_history`, while the reviewed helper requires
  exactly one complete `DEVELOPER_READY`, `REVIEWER_PASS`, and `QA_PASS` entry.
- No archive/index was created and the source board bytes remained unchanged. Integrator did not
  synthesize history, weaken the helper, or perform manual migration/rollback.
- Task A is locally merged but not accepted/complete/pushed. The token remains held; Task B and the
  umbrella remain unapproved and non-executable. Evidence:
  `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_integrator.md`.

## User-Approved — One-Time Legacy Bootstrap Attestation Amendment

Historical note: this approved maintenance-bootstrap scope was implemented at clean candidate
`aeb7709128361782800d2da5a473d730d48df652`. Its earlier fast-forward/dispatch preparation text
below is retained as audit history and is superseded for current routing by the pending routine-
transition amendment above.

The User explicitly approved this exact amendment at primary anchor
`3e73761673fd75de4e79028b0b8d0b89979bbd1a` and authorized automatic bounded
Developer -> independent Reviewer -> mandatory QA -> local Integrator continuation. The approval
resolves only the first Task A production migration's legacy-input mismatch. It does not create,
backfill, synthesize, or represent `DEVELOPER_READY`, `REVIEWER_PASS`, or `QA_PASS`
`transition_history`; it does not change the four routine transition contracts or weaken normal
maintenance gates. Task B and the umbrella remain unapproved and non-executable.

### Immutable legacy anchors

The bootstrap attestation schema is Task-A-specific and binds exactly these repository facts:

| Fact | Exact binding |
| --- | --- |
| Developer evidence | `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md@1fd726b08b7e49a32341d49e4439c889c4c6ab7b`; Git blob `6bd2703d6f280b9eec2fa01e59173149bd894c98`; SHA-256 `0fa1abdffe4d93182c090ddbf227628aec039d91d50b76b9f5fe9763ef5d3a0e`; `ready_for_review` |
| Reviewer evidence | `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_reviewer.md@84503d16e2638a827ecd3ef6704d0fe6bfed72ca`; Git blob `165ebfab7f198953539a371c7c56e114ccba6a91`; SHA-256 `de9be8e4c47b04f8538eeb5e2b732932c607486b2b5e2ca9441b6c0803837d70`; `reviewer_pass` |
| QA evidence | `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_qa.md@e958ba37df216c1690434ed7f9f40d4a436a88c5`; Git blob `49dc936e67a31fd53d616ee0b9e51bc5702819e8`; SHA-256 `49e33a43138dffd9fa7145abac6a2693e9f8f5c589ea22281f30c65b4e199541`; `qa_pass` |
| Lane ancestry | base `15c3120a6d889e97d098c2cb9f8c8ef852d74f69` -> Developer `1fd726b08b7e49a32341d49e4439c889c4c6ab7b` -> Reviewer `84503d16e2638a827ecd3ef6704d0fe6bfed72ca` -> QA `e958ba37df216c1690434ed7f9f40d4a436a88c5` |
| Local merge | `a42ca37e205127afd87d4cdc1d26ede53830522c`; parents `fd6036d9fce106ea81991def0ec572dfe20cdcb0` and `e958ba37df216c1690434ed7f9f40d4a436a88c5`; tree `a59c65dc838bfe66e8a839603d263e4e2c467ad1`; exact 26-path first-parent package digest `765445286739a3fb256f47ad36b41dbddde0fa7e2ea8c5f5018b17323da2dd4a` |
| Blocked primary | `75565f7aed80e34844e626519cbc74c4cc49c0a2`; exact Integrator evidence blob `dac23cd0d720583268920ab9112f402d09bf3717`, SHA-256 `e2781d373f289f14b9fec2ba57338197958ac21a17e9cd5ac23b9ed0f836f156` |
| Execution authority | Task A sole owner, `gate_running/Integrator`, queue empty, paused/Quick Fix/parallel null; execution-control digest `a1f0422506ffb124e14fac69c3cc51a4b2a56087c981c8c657aa06f9ec0755d4` |
| Failed migration | generation `1`; runtime source-board SHA-256 `922532265c3b27363c091ea6eae32420fdcc6c31832d44988bd5296a7cbcf2f6`; plan digest `519ee4f53e1887c524d59971b40a0e1749f4911cd2b032a41237584caaacc497`; archive/index absent; `BLOCKED_MAINTENANCE_GATES`; zero writes |

The old source-board hash and plan digest are immutable evidence of the failed attempt, not a
future apply token. Because this planning amendment changes committed governance, an approved
retry must calculate a new source-board hash and plan digest at its new reviewed merge HEAD and
bind those new values into the one-time consumption identity.

### Structural separation and single-use rule

- The committed source attestation is
  `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_legacy-bootstrap-attestation.v1.json`.
  Its schema contains no `event`, `from_state`, `to_state`, `transition_id`, or
  `transition_history` field. It is historical bootstrap input, never routine transition
  authority.
- `bootstrap_id` is the SHA-256 of canonical JSON containing only schema/version plus the exact
  anchors above. Any different task, evidence byte, commit, merge parent/tree/package, primary
  anchor, authority digest, source hash, plan digest, generation, role, or archive state blocks.
- The approved retry derives `consumption_id` from `bootstrap_id`, the fresh reviewed amendment
  HEAD/QA evidence, exact retry merge/source HEAD, current source-board hash, execution-control
  digest, generation `1`, archive path, and zero previous-index hash. The new maintenance plan
  digest includes that consumption identity.
- Successful apply writes one immutable helper-generated audit file matching
  `docs/archive/task_board_history/task-a-legacy-bootstrap-consumption-[0-9a-f]{64}.v1.json` and
  binds its path/hash/identity in the generation-1 index record. Later generations verify this
  record through the index hash chain but can never invoke bootstrap again.
- Exact same-input recovery is `ALREADY_APPLIED` only when compact board, archive, index, audit
  file, source/plan/consumption identities, and immediate commit topology all match. Partial,
  divergent, later-generation, later-closeout, other-task, or already-consumed reuse is blocked.

### Amendment implementation scope under its recorded separate User approval

May Touch:

1. `scripts/connlab_active_context.py` — minimal explicit Task A bootstrap hook only; normal path
   stays byte-for-byte equivalent in behavior and the file remains `<500` lines.
2. `scripts/connlab_task_a_legacy_bootstrap.py` — new Task-A-specific validator/identity module.
3. `tests/unit/test_connlab_task_a_legacy_bootstrap.py` — new bounded unit matrix.
4. `tests/integration/test_connlab_task_a_legacy_bootstrap_migration.py` — new bounded disposable-
   repository plan/apply/recovery/replay matrix.
5. The exact source-attestation JSON path above.
6. Task A Developer, Reviewer, QA, Integrator evidence at their existing exact role paths.
7. This Task, its Plan, Planner evidence, and `docs/task_board.md` for approved governance only.
8. Integrator-only generation-1 archive, `index.v1.jsonl`, compact board, and exact consumption-
   audit path generated by the reviewed helper after merge.

Must Not Touch / Locked Paths:

- No `transition_history` insertion, callback synthesis, normal transition event creation, manual
  archive/index/audit file creation, force/override/ignore flag, or generic legacy bypass.
- `scripts/connlab_execution_transition.py`, `scripts/connlab_handoff_contract.py`, the normative
  contract, AGENTS, skills, policies, protocols, execution gate, worktree/commit/archive helpers,
  registry/bundle, V1/V2, Task B/umbrella, product/data/runtime/release/remote paths, and every
  retained/frozen/cancelled lane are read-only.
- New bootstrap code/tests/attestation are exclusively Task A lane-owned. Production board,
  archive, index, and consumption audit remain Integrator-only. No parallel exception exists.

### Existing-lane continuation and gates

Planner has recorded the explicit User approval and returned the same Task A token to
`implementation_running/Developer` for reconciliation preparation only. The existing physical
lane remains clean at `e958ba37df216c1690434ed7f9f40d4a436a88c5`; its required reconciliation
target is the approved primary descendant
`3e73761673fd75de4e79028b0b8d0b89979bbd1a`. Orchestrator must reuse the existing
lane/worktree and fast-forward it non-destructively to that exact target; the
existing QA HEAD and local merge remain ancestors and are never reset, rebased, discarded, or
recreated. Developer implements only the amendment scope, then full independent Reviewer re-gate,
mandatory QA, and Integrator retry occur on a new reviewed HEAD. Integrator may retry merge and
live generation-1 apply only after those gates pass and while Task A remains the sole
`gate_running/Integrator` owner.

Developer dispatch remains prohibited until Orchestrator proves the exact fast-forward, clean
lane/index at the target HEAD, and a fresh `ImplementationDispatch=ALLOW_DISPATCH`. Live apply
remains prohibited until the subsequent Developer/Reviewer/QA gates pass. Task B remains
`planned_pending_user_approval` and cannot start.

## Historical Original Approval Boundary

The User explicitly approved Task A only and authorized automatic execution through local
Integrator acceptance. This approval does not approve Task B or revive the superseded umbrella.
Approval base `15c3120a6d889e97d098c2cb9f8c8ef852d74f69` contains the approved Task/Plan/
Planner evidence. The historical B1-B5 and final R1-R3 Developer/Reviewer/QA route completed and
the exact QA package was merged locally, but first migration failed closed. That original approval
did not approve the bootstrap amendment; the User subsequently approved it at exact anchor
`3e73761673fd75de4e79028b0b8d0b89979bbd1a`. No live board maintenance, push, publication,
restart, destructive cleanup, or parallel exception is authorized by that approval.

## User Approval And Activation Boundary

- Approval source: direct User approval recorded by permanent Orchestrator on 2026-08-01.
- Approved scope: this exact Task A and its plan at primary
  `d791e74a9811033058c38ee329bb3be8ee1f6504`.
- Authorized automatic route: isolated Developer -> Reviewer -> mandatory QA -> local Integrator
  acceptance, including bounded fixes inside the frozen scope.
- Approval/worktree base: `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Developer bounded-fix final/evidence HEAD is
  `6d449262473e628cdf239c5d9b54ae3a2ff2c4c8`. Lane and primary worktree/index are clean; approved
  base, original Developer package, and Reviewer block are ancestors. Updated Developer evidence
  blob `75b80e0e131a84bb1e3176225e6173dc95dd7700` is `ready_for_review`; Reviewer evidence remains
  byte-identical at blob `8f8534adc660f71f2fbe435404699e321acc5174`.
- Task B remains `planned_pending_user_approval`, serially blocked until A local acceptance and
  separate User approval. The umbrella remains `superseded_by_split_plans` and non-executable.

## Goal

Make active ConnLab governance small, deterministic, and event-driven while preserving all current
safety gates. The task must:

1. migrate the oversized board to a lossless compact active authority plus immutable history;
2. maintain that split automatically at every future Integrator closeout before token release;
3. replace Planner-mediated routine gate changes with one tested fail-closed transition helper;
4. enforce one transition and one role dispatch per Orchestrator turn;
5. validate reference-only handoffs, minimal reads, seven-field callbacks, cadence, and context
   budgets without changing WIP=`1`, token lifetime, role independence, or worktree isolation.

## User-Confirmed Contract

- Planner is not part of routine Developer/Reviewer/QA gate transitions.
- Orchestrator performs at most one legal transition and one dispatch per turn, then stops.
- A role callback is a wake-up signal, never authority; durable board/evidence/Git facts remain
  authoritative and suppress duplicates.
- Commentary is limited to role start/end, real blocker, material direction change, or one short
  heartbeat after at least 60 seconds of active silence; unchanged waits are suppressed.
- First board migration is byte-exact and reversible. Future closeouts keep the board compact
  automatically without separate User cleanup requests.
- Only Integrator may write production board/history through the compaction helper while the task
  is the sole `gate_running/Integrator` token owner. Token-null planning audits are read-only.

## Authority And State Machine

The existing `connlab.execution-control` JSON remains the sole machine authority; the human active
summary is a deterministic projection, not a second state store. Existing WIP/token states and
Quick Fix/reconciliation semantics remain unchanged.

The transition helper supports exactly four routine event families:

| Event | Required current state | Evidence status | Result |
| --- | --- | --- | --- |
| `DEVELOPER_READY` | `implementation_running/Developer` | `ready_for_review` | `gate_running/Reviewer` |
| `REVIEWER_BLOCKED` | `gate_running/Reviewer` | `reviewer_blocked` | `implementation_running/Developer` bounded fix |
| `REVIEWER_PASS` | `gate_running/Reviewer` | `reviewer_pass` | `gate_running/QA`, or `gate_running/Integrator` only when approved task metadata says QA is not required |
| `QA_PASS` | `gate_running/QA` | `qa_pass` | `gate_running/Integrator` |

Every transition retains the same task token, lane, branch, worktree, base, locks, queue,
residuals, paused/Quick Fix/parallel facts, and required-gates metadata. It updates only the legal
state/role, exact lane HEAD, evidence ref, transition digest, and derived summary.

Before any write the helper validates expected state/role/token/task/lane, exact primary and lane
HEADs, evidence path/commit/Git blob/SHA-256/status, ancestry, clean primary/lane/index, actual
changed paths against approved scope/locks, queue/paused/Quick Fix/parallel facts, task gate
metadata, legal transition, unique execution markers, and JSON/summary agreement. Missing,
ambiguous, mismatched, dirty, stale, unknown, scope-drift, callback-drift, or evidence-conflict
facts return stable `BLOCKED_*` output and perform zero writes. No force/ignore/assume override
exists.

Planner remains required only for Discovery, formal task/plan work, User or scope change,
unclassifiable blockers, ownership/API/schema/authority replanning, destructive decisions, and
merge/evidence conflicts.

## Helper Interfaces

### Deterministic transition

```text
py scripts/connlab_execution_transition.py inspect --repo-root <primary> --json
py scripts/connlab_execution_transition.py plan --repo-root <primary> --event <EVENT> --task-id <TASK_ID> --lane <lane> --expected-primary-head <sha> --expected-lane-head <sha> --evidence-ref <path@commit#sha256> --evidence-status <status> --json
py scripts/connlab_execution_transition.py apply <same exact inputs> --expected-snapshot-digest <sha256> --json
```

`inspect` and `plan` are zero-write. `apply` may change only `docs/task_board.md`, and only after a
matching plan digest. Output records `decision`, `reason_codes`, `before_digest`, `after_digest`,
`transition_id`, `next_role`, and `changed_paths`. A repeated already-applied transition is an
idempotent zero-write result; a divergent duplicate is blocked.

### Active context and history

```text
py scripts/connlab_active_context.py inspect --repo-root <primary> --json
py scripts/connlab_active_context.py plan-maintenance --repo-root <primary> --expected-head <sha> --expected-board-sha256 <hash> --json
py scripts/connlab_active_context.py apply-maintenance <same inputs> --expected-plan-digest <hash> --json
py scripts/connlab_active_context.py prove-rollback --repo-root <primary> --generation <n> --output <temp-path> --json
```

Production `apply-maintenance` requires clean primary `master`, `gate_running`, active role
`Integrator`, the task being closed as the sole token owner (Task A for the first migration),
accepted Task A helper ancestry, all gates required by the closing task (Task A Reviewer and QA for
the first migration), exact expected HEAD and board hash, empty queue, null paused/Quick Fix/
parallel, and non-conflicting archive/index paths.
Planner, Developer, Reviewer, ordinary terminal audits, and token-null state may only inspect,
plan, or prove rollback.

### Handoff and cadence

```text
py scripts/connlab_handoff_contract.py validate-dispatch --input <json> --repo-root <primary> --json
py scripts/connlab_handoff_contract.py resolve-read-set --input <json> --repo-root <primary> --json
py scripts/connlab_handoff_contract.py validate-callback --input <text> --json
py scripts/connlab_handoff_contract.py validate-cadence --events <jsonl> --json
```

References use `path@commit#sha256`. Invalid refs or any unprovable omission return
`FULL_READ_REQUIRED`; unrelated archive changes alone do not. Callback fields are exactly, in
order: `TASK_ID`, `ROLE`, `STATUS`, `EVIDENCE`, `COMMIT`, `NEXT`, `BLOCKER`.

## Board Migration And Automatic Maintenance

- Trigger maintenance when the board exceeds `400` physical lines, `65536` UTF-8 bytes, or `24`
  terminal-detail records. Below every threshold, the command is zero-write.
- First migration archives the exact current board bytes. Later generations archive only the
  oldest terminal detail needed to restore all budgets.
- Eligible history is only `completed`, `cancelled`, `superseded`, or otherwise formally terminal.
  Execution JSON, active/queue/paused/Quick Fix/parallel records, residual ownership, current and
  proposed tasks, and their direct evidence pointers never move out of the active board.
- Generated immutable path format is
  `docs/archive/task_board_history/generation-<six-digits>-<40-char-source-commit>.md`.
- Versioned append-only index is `docs/archive/task_board_history/index.v1.jsonl`. Each immutable
  generation record binds source commit/blob/SHA-256/byte count/record count, archive path/hash,
  compacted board hash/count,
  previous index hash, and byte-exact rollback proof.
- An existing different archive, malformed/corrupt index, non-contiguous generation, hash/count
  mismatch, or path escape blocks writes. Same-input reruns are idempotent.
- Transaction staging validates all bytes first. On injected/real partial failure, prior board and
  index bytes are restored and only an exact helper-created uncommitted archive may be removed;
  no unrelated file is deleted. The board authority is replaced last.
- Every future Integrator closeout must run `plan-maintenance` and, if required,
  `apply-maintenance` before token release. Second and third closeouts are mandatory tests.

## Context And Conversation Budgets

| Artifact | Hard budget after A |
| --- | --- |
| active `docs/task_board.md` | <=400 lines and <=65536 UTF-8 bytes |
| Orchestrator core skill | <=16384 UTF-8 bytes |
| Planner core skill | <=8192 UTF-8 bytes |
| active orchestration protocol | <=12288 UTF-8 bytes |
| role dispatch template | <=2048 UTF-8 bytes |
| complete dispatch capsule | <=4096 UTF-8 bytes |
| seven-field callback | <=1024 UTF-8 bytes |
| each role minimal-read capsule | <=4096 UTF-8 bytes |

Optional lifecycle series, frozen V2 details, historical prompts, and archive bodies become
on-demand references. The minimal safe read set is board JSON/generated summary, current
task/plan/current-role evidence, and declared direct dependencies. Any unsafe omission fails to a
full read. Implementation evidence must record before/after bytes for board, core skills/protocol,
dispatch/callback/capsules, default per-role resolved read set, and Orchestrator turn item count.

## Exact May Touch

### Contracts and active role policy

1. `AGENTS.md`
2. `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md` (new)
3. `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
4. `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
5. `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
6. `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
7. `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
8. `docs/project_management/TASK_EXECUTION_SKILL.md`
9. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
10. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
11. `.agents/skills/connlab-planner/SKILL.md`

### Helpers and bounded tests

12. `scripts/run_task.ps1`
13. `scripts/connlab_execution_transition.py` (new)
14. `scripts/connlab_active_context.py` (new)
15. `scripts/connlab_handoff_contract.py` (new)
16. `tests/unit/test_connlab_execution_transition.py` (new)
17. `tests/integration/test_connlab_execution_transition_recovery.py` (new)
18. `tests/unit/test_connlab_active_context.py` (new)
19. `tests/integration/test_connlab_board_closeout_maintenance.py` (new)
20. `tests/unit/test_connlab_handoff_contract.py` (new)
21. `tests/unit/test_connlab_active_context_governance.py` (new)
22. `tests/unit/test_execution_wip_and_quick_fix_governance.py` (bounded references/assertions)
23. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` (bounded callback assertion)

### Task-owned and primary-only paths

24. `tasks/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF.md`
25. `docs/task_governance_active_context_deterministic_transition_and_event_handoff_plan.md`
26. `docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_planner.md`
27. Task A Developer/Reviewer/QA/Integrator evidence with the same exact task prefix.
28. `docs/task_board.md` (Planner/Integrator primary only; Developer lane must not edit it)
29. `docs/archive/task_board_history/index.v1.jsonl` (Integrator append-only; records immutable)
30. Helper-generated archive names matching exactly
    `docs/archive/task_board_history/generation-[0-9]{6}-[0-9a-f]{40}.md` (Integrator only)

No other path is authorized without Planner/User scope reconciliation.

## Must Not Touch

- `backend/**`, `frontend/**`, product/API/schema/database/migration/Office/business tests, real DB,
  Excel, PDF, DOCX, public-drive, or operator files.
- `docs/project_management/ROLE_THREAD_REGISTRY.md`,
  `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md`, and all retained/frozen/cancelled lanes.
- Controlled Lane V2 contract/skill/helper/registry/heartbeat/pilot/corrective/tests.
- `scripts/connlab_execution_gate.ps1`, `scripts/connlab_lane_worktree.ps1`,
  `scripts/task_complete_commit.ps1`, and `scripts/archive_completed_markdown.py`; these are
  regression inputs only.
- package/lock/dependency files, release output, push, publication, restart, reset, restore,
  discard, clean, force removal, or destructive worktree maintenance.
- Task B implementation files; A may reference B's planned dependency only.

## Locked Paths

After approval, every A May Touch policy/helper/test path is exclusively locked to A. Live board,
history index, and generated archives are additionally primary Integrator-owned. No parallel
exception or second implementation owner is permitted.

## Acceptance And Performance

Repository baseline at revision: board `2466` lines / `781091` bytes; Orchestrator skill `305`
lines / `17304` bytes; Planner skill `98` / `3972`; orchestration protocol `303` / `14120`;
`run_task.ps1` `123` / `4854`. User-observed TASK_368E baseline: Developer `~46.3m`, Reviewer
`~23.2m`, bounded fix `~12.2m`, Reviewer re-gate `~13m`, QA `>23m`, routine Planner transitions
`~32m`, and one long Orchestrator turn with a User-confirmed lower bound of `>=200` items plus
repeated reads, callbacks, waits, and context compaction. Implementation must capture the exact
extractable before-count, or retain this lower-bound notation if the source export is truncated.

Acceptance requires:

1. routine transition Planner launches = `0`;
2. at most one transition plus one dispatch per Orchestrator turn, then immediate stop;
3. controlled callback-to-legal-dispatch pilot <=`90s`;
4. active board and all context budgets above pass with recorded before/after bytes/items;
5. first migration byte/hash/record round-trip and rollback proof pass;
6. second/third closeout maintenance, no-threshold zero-write, idempotency, archive conflict,
   corrupt index, and partial-write rollback pass;
7. all four transition families and every listed mismatch fail closed;
8. strict seven-field callback, minimal-read fallback, cadence, unchanged-wait suppression, and
   reference-only dispatch tests pass;
9. existing execution gate/recovery, WIP/Quick Fix, worktree, archive, and permanent-role tests
   pass unchanged in meaning;
10. WIP/token/role/worktree/no-push/non-destructive/V2 invariants remain intact.

Missing a safety or quantitative target blocks Integrator acceptance.

## Planned Lane And Gates

- Lane: `task-governance-active-context-deterministic-transition-and-event-handoff`
- Branch: `lane/task-governance-active-context-deterministic-transition-and-event-handoff`
- Sibling worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-active-context-deterministic-transition-and-event-handoff`
- Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`
- Worktree creation base: `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Route: User approval -> isolated Developer -> independent Reviewer -> mandatory QA -> Integrator.
- Developer hands off a clean exact-path commit; Reviewer performs a full review (A cannot optimize
  its own gate); QA validates final reviewed HEAD and disposable migration/recovery cases;
  Integrator alone merges and runs the guarded first production migration before token release.

The exact branch/worktree is clean at QA HEAD
`e958ba37df216c1690434ed7f9f40d4a436a88c5`; Reviewer and QA passed and local merge `a42ca37e...`
preserves that ancestry. The approved reconciliation target is
`3e73761673fd75de4e79028b0b8d0b89979bbd1a`. That historical fast-forward and bounded Developer
package are now complete at `aeb77091...`; Reviewer remains blocked pending approval and atomic
application of the routine-transition amendment above.

## Historical Reviewer-Blocked Bounded Fix Contract

- B1: make rollback proof output new, non-link, exclusive, temp-root-only and block repository,
  existing-target, escape, link/junction, board/index/archive, and unsafe-parent destinations.
- B2: bind the complete compact dispatch capsule to exact board/task/lane/Git/gate/scope/lock/
  evidence/action/stop-condition authority and fail closed on omissions or contradictions.
- B3: require and validate frozen transition metadata and parse one unambiguous current evidence
  machine status; complete the zero-write mismatch and duplicate matrix.
- B4: validate real Reviewer/QA evidence ancestry and the accepted helper checkpoint; make
  maintenance idempotency depend on exact board/index/archive/plan/clean-state agreement and
  validate every frozen index proof field.
- B5: measure every heartbeat from the previous permitted material event, including the first;
  reject unchanged, misordered, mixed, or negative timelines while retaining the <=90s pilot.
- Fix paths are limited to `scripts/connlab_active_context.py`,
  `scripts/connlab_execution_transition.py`, `scripts/connlab_handoff_contract.py`, and
  `scripts/run_task.ps1` only if B2 capsule generation requires it; the corresponding already
  approved Task A bounded tests; and Developer evidence. The frozen contract/policies/skills,
  Task/Plan/board, archive/index production paths, execution gate, and all other paths are not
  Developer fix paths.

## Historical Bounded Fix Handoff

- Fix checkpoint: `de9a4e0f89730a5f408460852ad3b6f53ceb1000`; clean final evidence HEAD:
  `6d449262473e628cdf239c5d9b54ae3a2ff2c4c8`.
- Developer claims all seven direct B1-B5 reproductions pass, the expanded helper matrix passes
  `41`, and the complete approved matrix passes `129`; compilation, PowerShell AST, line ceilings,
  production zero-write checks, and protected-state equality also pass.
- Reviewer must independently re-run every B1-B5 adversarial case and the complete safety/
  performance gate. No claim is accepted or waived by this transition. A pass routes to mandatory
  QA; any remaining or new in-scope blocker returns to Developer.

## Compatibility And Rollback

- Before acceptance, existing manual transitions and full reads remain authoritative.
- Unsupported/missing metadata always retains the old full-read/manual governance path.
- Code rollback is a local Git revert. Board rollback is a separately reviewed exact patch from an
  index-verified archive; the helper only proves/reconstructs into temp and never silently restores
  live authority.
- Existing execution gate stays read-only and schema-compatible. Existing tasks without new
  transition metadata cannot use the helper and fail closed to manual governance.

## Historical Stop Point (superseded)

The earlier `developer_dispatch_ready` stop was consumed by the atomic transition committed at
`5cd7f02a...`. It is retained only as audit history and grants no current dispatch authority. The
current stop is the pending post-transition amendment and authority decision above; board remains
`gate_running/Reviewer` and the clean lane remains `70e5c6a...`.
