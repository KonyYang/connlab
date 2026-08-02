# Active Context Deterministic Transition And Event Handoff Implementation Plan

Status: `integration_reconciliation_amendment_pending_user_approval`

Task: `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF`

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

## Pending Routine-Transition Authority Reconciliation Amendment

This amendment is planning-only and requires separate User approval. It changes neither the
current board nor the clean candidate lane. It repairs the existing transition state machine; it
does not create a second state machine, synthesize historical gate events, or weaken the approved
maintenance bootstrap.

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
  maintenance-bootstrap amendment explicitly locks them read-only. New User approval is required.

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

- The User's approval of this new amendment; the future fix/evidence candidate, transition plan/
  bootstrap/transition IDs, Reviewer/QA evidence commits, retry merge, and final migration hashes.

These are gated future outputs. No additional product or UX question exists. Recommendation: stop
for User approval; after approval continue only through the exact serial route below.

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
the existing approved six-path package plus exactly the four newly reopened implementation paths
and Developer evidence; the candidate must contain no other delta from durable HEAD `3e737616...`.

The separate canonical `transition_metadata_bootstrap` board record contains schema/version,
purpose, Task/base/original approval/latest amendment refs, primary/source-board/payload anchors,
durable HEAD, blocked candidate/evidence/blob/SHA/status, exact six-path digest, future fix
candidate/delta digest, branch/worktree/clean/ancestry facts, effective scope/lock digests,
retained-context digest, and `bootstrap_id`. It has no `event`, `from_state`, `to_state`, or
historical gate-result fields and is not part of `transition_history`.

The canonical routine plan contains both `expected_board_head` and `candidate_lane_head`, exact
range paths/digest, evidence path/commit/blob/SHA/current-status record, primary/source-board
digest, task/token/state/role/lane/branch/worktree/base, scope/locks/gates/context, from/to tuple,
optional one-time bootstrap ID, transition ID, and plan digest.

### Existing helper interface

Repair `scripts/connlab_execution_transition.py` in place. The normative plan/apply shape becomes:

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
6. validate latest approved scope ref, original base scope, independently hashed May Touch and
   Locked Paths, required gates, retained context, legal from/to tuple;
7. on the one legacy path, validate every frozen `49911ae6`/`3e737616`/`aeb77091`/evidence/six-
   path/bootstrap fact and derive `bootstrap_id`;
8. derive exact rendered board, transition ID and plan digest; emit `ALLOW_TRANSITION` zero-write.

Apply rereads steps 1-8, requires exact snapshot and plan digests, then writes one temporary board,
fsyncs, atomically replaces only `docs/task_board.md`, reloads and revalidates the complete result.
The one replacement simultaneously adopts candidate HEAD/evidence, changes state/role, appends
the real current event, sets last-transition fields, and initializes metadata/bootstrap when
needed. No other path is written.

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

### Exact future May Touch / Must Not Touch / locks

Developer lane May Touch only:

1. `scripts/connlab_execution_transition.py`
2. `tests/unit/test_connlab_execution_transition.py`
3. `tests/integration/test_connlab_execution_transition_recovery.py`
4. `docs/project_management/ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_CONTRACT.md`
5. Task A Developer evidence

Role/primary-only paths after the relevant gate:

6. Task A Reviewer/QA/Integrator/Planner evidence
7. current Task and Plan
8. `docs/task_board.md`, only by the helper's one atomic transition replacement and its exact
   one-path commit

Must Not Touch: active-context/bootstrap/handoff helpers and tests, legacy source attestation,
`run_task.ps1`, execution/worktree/maintenance gates, every other contract/policy/skill/test,
archive/index/audit, registry/bundle, V1/V2, Task B/umbrella, product/data/runtime/release/remote,
and retained/frozen/cancelled lanes. Existing board Locked Paths and WIP=`1` remain unchanged; no
parallel exception, new task, branch, or worktree.

### Implementation and role sequence after User approval

1. Planner records exact approval in Task/Plan/Planner evidence only; board head/state/role stay
   unchanged. No ambient board metadata or candidate-head update is allowed.
2. Orchestrator revalidates exact anchors. User approval authorizes one same-token/same-lane
   bounded Developer continuation from clean `aeb77091...` despite the known legacy
   `BLOCKED_ACTIVE_HEAD_DRIFT`; any different blocker or drift stops. This exception cannot route
   another task/role or survive the first atomic transition.
3. Developer uses TDD on the four reopened implementation paths, updates Developer evidence, and
   commits a clean candidate descendant of `aeb77091...`.
4. From that candidate, the repaired existing helper plans/applies the one atomic metadata-
   bootstrap plus `DEVELOPER_READY` adoption and the Orchestrator exact-commits board only.
5. Reviewer performs a full re-gate of the complete Task A package and the new transition matrix.
   Reviewer block/pass uses the repaired atomic candidate adoption with evidence-only delta.
6. Mandatory QA validates the final reviewed candidate, full Task A matrix and production zero-
   write gates; `QA_PASS` is an atomic evidence-only adoption.
7. Integrator verifies ancestry/package/attestations, merges the newly reviewed delta, retries the
   previously approved generation-1 maintenance bootstrap, reruns merged validation, and accepts
   only on complete success. Task B remains stopped.

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
16. helper unit and disposable recovery suites cover all four events, duplicate/reconnect/
    rollback, canonical Windows paths and exact commit topology;
17. unchanged active-context, maintenance, handoff, execution gate/recovery, WIP/Quick Fix,
    worktree/archive/role suites pass, including the approved bootstrap `50` and prior Task A
    `133` baseline;
18. complete Task A regression plus new cases pass; Python compilation, PowerShell AST, helper
    `<500` line ceiling or approved extraction, exact allowlist/diff/show, protected hashes,
    production zero-write checks, callback/cadence/budgets all pass;
19. full independent Reviewer re-gate, mandatory QA on final reviewed HEAD, and Integrator merged-
    tree/migration/rollback/clean-closeout gates pass;
20. Task B/umbrella/product/registry/V1/V2/retained lanes/remote/runtime remain unchanged.

### Stop point

Return `integration_reconciliation_amendment_pending_user_approval`. Keep the board and lane
unchanged. Do not initialize metadata, alter board HEAD/state/role, edit helper/tests/contract,
dispatch Developer/Reviewer/QA/Integrator, migrate, create archive/index/audit, merge, push,
restart, or clean until the User approves this exact amendment.

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
retained for audit and superseded by the pending routine-transition amendment above.

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
  on a new reviewed HEAD. Live apply is forbidden before User approval and those gates.

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

## 9. Stop Point

Return `integration_reconciliation_amendment_pending_user_approval`. Task A keeps the sole token
in `implementation_running/Developer`; durable board HEAD remains `3e737616...` and clean callback
candidate remains `aeb77091...`. Planner does not initialize metadata, pre-adopt the candidate,
dispatch a role, edit/advance the lane, merge, run live migration/maintenance, create archive/
index/audit, or perform Task B work.
