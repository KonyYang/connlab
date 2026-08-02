# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF

Status: `approved_reconciliation_preparation`

Type: governance / execution-authority / orchestration-efficiency

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Owner at this gate: Task A retains the sole token in `implementation_running/Developer` as a
reconciliation-preparation authority; Developer is not yet dispatched.
Next authority: Orchestrator must non-destructively fast-forward the existing clean lane from
`e958ba37df216c1690434ed7f9f40d4a436a88c5` to the approved amendment anchor
`3e73761673fd75de4e79028b0b8d0b89979bbd1a`, prove the exact clean HEAD, and obtain a fresh
`ALLOW_DISPATCH` before Developer may receive implementation authority.

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

### Amendment implementation scope after separate User approval

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
`3e73761673fd75de4e79028b0b8d0b89979bbd1a`. No role may be dispatched until the exact
fast-forward, clean target HEAD, and fresh `ALLOW_DISPATCH` are proven.

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

## Stop Point

Return `approved_reconciliation_preparation` to Orchestrator. Retain Task A as sole
`implementation_running/Developer` token owner, with the active HEAD expressing the approved
target `3e73761673fd75de4e79028b0b8d0b89979bbd1a`. Do not dispatch Developer until Orchestrator
fast-forwards the existing lane, proves it clean at that exact HEAD, and obtains fresh
`ALLOW_DISPATCH`. Do not edit helper/tests/attestation, run live migration/maintenance, create
archive/index/audit, or perform Task B work in this governance step.
