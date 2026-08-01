# TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF

Status: `planned_pending_user_approval`

Type: governance / role-handoff / validation-efficiency contract

Planning base: `4e7ce7ffa040039e8c7ebb659efe8cba5e00eeff`

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Current execution authority: `Current Active Task: None`; execution state `complete`; token owner,
active record, queue, paused task, Quick Fix, and parallel exception are null.

Owner at this gate: permanent Planner. Next gate: explicit User approval.

## Approval Boundary

- Permanent Orchestrator authorized creation of this formal planning package after TASK_368E local
  Integrator acceptance.
- This authorization is planning-only. It does not approve implementation, acquire an execution
  token, enqueue the task, create a branch/worktree, or dispatch Developer.
- Implementation requires explicit User approval of this exact task/plan, then an isolated
  `Developer -> Reviewer -> QA -> Integrator` lane.
- No push, publication, restart, destructive cleanup, product change, retained-lane maintenance,
  or frozen V2 change is authorized.

## Goal

Reduce repeated Reviewer work, oversized role prompts, repeated repository reads, board-history
loading, and event-by-event commentary without weakening ConnLab's fail-closed governance.

The task establishes:

1. opt-in, versioned Reviewer re-gate evidence reuse bound to immutable Git and command evidence;
2. mandatory full re-gate escalation whenever reuse safety cannot be proven;
3. independent final QA on the final reviewed HEAD;
4. deterministic role-local validation sharding without changing WIP=`1` ownership;
5. a lossless split between the compact active board and historical board archive;
6. compact reference-only role handoffs, exact seven-field callbacks, minimal safe reads, and a
   60-second commentary cadence contract;
7. executable helpers and bounded tests that prevent governance prompt/context growth from
   returning silently.

## User-Confirmed Contract

- After a bounded blocker fix, Reviewer re-gate checks the blocker, direct dependencies,
  base/fix/final ancestry, scope, and cleanliness. An unchanged area may reuse a prior passing
  result only when the evidence is bound to exact commits, command identity, relevant environment
  and fixture hashes, and committed evidence content.
- QA remains independent and performs one complete risk-proportionate validation against the final
  reviewed HEAD. Reviewer reuse never substitutes for QA.
- Scope drift, dependency drift, baseline drift, unknown failure, or shared authority/API/schema/
  ownership impact forces `FULL_REGATE`.
- A role may shard tests or run safe commands in parallel locally, but this is validation
  concurrency inside one role on one immutable task HEAD. It is not a second implementation owner,
  worktree, token, or parallel exception.
- Machine execution JSON remains the only machine execution authority. The human active summary is
  generated from and checked against that JSON; it is not a second state store.
- Dispatch capsules contain references and hashes, not copied task/plan/evidence contracts.
- The callback shape is exactly seven fields in this order: `TASK_ID`, `ROLE`, `STATUS`, `EVIDENCE`,
  `COMMIT`, `NEXT`, `BLOCKER`.
- User-visible commentary is emitted only at role start/end, a real blocker, a material direction
  change, or after 60 seconds of otherwise silent active work. An unchanged wait snapshot is not
  repeated.
- A minimal read set is allowed only when every referenced file/blob/hash and current state agrees.
  Any missing, stale, mismatched, ambiguous, or unprovable omission fails closed to a full read.

## Design Decision

Use three focused helpers rather than adding unrelated responsibilities to the existing execution
gate or completed-Markdown archive tool:

1. `connlab_regate_evidence.py` validates versioned Reviewer evidence manifests and deterministic
   shard-result aggregation. It is zero-write.
2. `connlab_handoff_contract.py` validates reference-only capsules, minimal-read eligibility,
   seven-field callbacks, and commentary cadence events. It is zero-write.
3. `connlab_board_context.py` validates JSON/summary agreement and performs an explicitly guarded,
   lossless active-board/history migration. Its inspect/plan/rollback-proof paths are zero-write;
   only an exact Integrator `apply-compaction` action may write the three declared board/archive
   paths.

Do not infer dependencies heuristically. Each reusable validation command declares exact covered
paths and direct dependency paths. Unknown dependency ownership means `FULL_REGATE`.

## Reviewer Re-gate Evidence Contract

Schema name: `connlab.reviewer-regate-evidence`; version: `1`.

Each manifest records at least:

- task/lane/reviewer identity;
- exact `baseline_sha`, `prior_reviewed_sha`, `blocker_evidence_sha`, `fix_sha`, and
  `final_candidate_sha`;
- sorted changed paths and the approved blocker/fix path set;
- declared direct dependency paths with committed content SHA-256 values;
- each prior command as an argv array, working directory, covered paths, dependency paths,
  canonical command-identity digest, relevant environment digest, fixture digest, immutable input
  commit, prior result, result digest, evidence path, evidence commit, and evidence-blob SHA-256;
- explicit impact flags for authority, API, schema, persistence, migration, shared ownership, and
  unknown failure;
- optional shard result references with stable shard IDs.

The helper emits one of:

```text
REUSE_ALLOWED
FULL_REGATE
```

`REUSE_ALLOWED` includes the exact reusable and required command IDs. `FULL_REGATE` includes one or
more stable reason codes and never silently degrades to reuse. Exit `0` means reuse is proven;
exit `2` means full re-gate is mandatory; malformed invocation exits nonzero without writes.

## Mandatory FULL_REGATE Conditions

Any one condition is sufficient:

- missing/unsupported/malformed manifest or required field;
- commit missing, non-full SHA, wrong base, broken ancestry, candidate/board mismatch, or baseline
  drift;
- changed path outside approved blocker/fix scope;
- declared dependency missing, ambiguous, or changed;
- command argv/cwd/selection identity changed;
- relevant OS/runtime/dependency-lock environment changed;
- fixture or input hash changed;
- prior result was not pass, result digest is missing, or committed evidence hash differs;
- a shard is missing, duplicated, failed, or reports a different input commit;
- a new/unknown failure exists;
- authority, API, schema, persistence, migration, or shared-ownership impact is true or unknown;
- worktree/index is dirty, scope ownership is unclear, or reusable omission cannot be proven safe.

No override flag may convert these results to reuse.

## QA And Validation Sharding Contract

- QA always consumes the final Reviewer-pass commit and runs the task's complete frozen
  risk-proportionate QA matrix once.
- QA may read Reviewer evidence as context, but does not treat `REUSE_ALLOWED` as a passed QA test.
- Role-local shards share one immutable input commit and one role/worktree/archive authority.
- Shard IDs are unique and results are aggregated in lexical shard-ID order. Missing, duplicate,
  nonzero, stale-commit, or unknown results fail the aggregate.
- Sharding never writes execution authority, acquires/releases a token, creates a worktree, or
  activates a parallel exception.
- Commands use explicit argv/cwd records. A shell-composed free-form command is not reusable
  evidence.

## Compact Handoff And Read Contract

Reference-only capsule fields are:

```text
TASK_ID, ROLE, STATUS, BOARD_REF, TASK_REF, PLAN_REF, EVIDENCE_REF,
DIRECT_DEPENDENCY_REFS, PRIMARY_HEAD, LANE_BRANCH, WORKTREE, BASE_SHA,
HEAD_SHA, LOCKED_PATHS_DIGEST, GATE_SNAPSHOT_DIGEST, NEXT, STOP_CONDITIONS
```

Every `*_REF` is `path@commit#sha256`. Capsule UTF-8 size is at most `4096` bytes. It must not
contain copied task, plan, evidence, worktree-list, protocol, or test-output bodies.

Minimal safe reads are limited to:

- the board execution JSON and generated active summary;
- current task, plan, and current-role evidence;
- exact direct dependencies named in the capsule.

Hash/state mismatch, escalation flags, missing refs, unknown ownership, or inability to prove a
file irrelevant returns `FULL_READ_REQUIRED`. The full-read fallback includes AGENTS, full board,
execution/parallel/orchestration protocols, current task/plan, all current-task role evidence,
current Git/worktree state, and affected direct dependencies.

## Conversation Budget And Cadence

- Start: one concise role-start commentary.
- Progress: no duplicate event commentary. Emit only for a real blocker, direction change, or after
  `60` seconds of silent active work.
- Wait: identical task/status/evidence/head snapshot digests are suppressed.
- End: one concise role-end result before the exact callback.
- Callback: exactly seven nonempty ordered fields; no prose or copied evidence inside the callback.
- Standard dispatch templates and `run_task.ps1 -Preview` output must remain reference-only and at
  most `4096` UTF-8 bytes.

## Active Board And History Migration

- Before compaction, Integrator stores the exact pre-compaction `docs/task_board.md` bytes at:
  `docs/archive/task_board_history/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_pre_compaction.md`.
- Index path:
  `docs/archive/task_board_history/index.json`.
- The index records schema/version, task ID, source commit, source Git blob, source SHA-256, archive
  path/SHA-256, compacted board SHA-256, created timestamp, and rollback-proof result.
- The compact board retains exactly one execution-control block, a marker-delimited generated
  active summary, a short planned-task section, current residual pointers, and the history index.
- Completed lane/task history becomes archive-only reference. Historical text is not current
  execution authority.
- The compact board budget is at most `400` physical lines and `65536` UTF-8 bytes.
- Rollback proof reconstructs the exact pre-compaction bytes into a temporary output and compares
  SHA-256. The helper never overwrites the live board during rollback proof.
- `apply-compaction` is fail-closed and permitted only on clean primary `master`, at the expected
  HEAD/board hash, by this task's sole Integrator owner (or a terminal token-null planning audit),
  with empty queue and null paused/Quick Fix/parallel state.
- `scripts/archive_completed_markdown.py` retains its separate task/plan archive responsibility and
  is not modified.

## Exact May Touch

### Governance policy and role contracts

1. `AGENTS.md`
2. `docs/project_management/PROPORTIONATE_REGATE_AND_COMPACT_HANDOFF_CONTRACT.md` (new)
3. `docs/project_management/EXECUTION_WIP_AND_QUICK_FIX_POLICY.md`
4. `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
5. `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
6. `docs/project_management/PARALLEL_LANE_OPERATIONS_GUIDE.md`
7. `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
8. `docs/project_management/TASK_EXECUTION_SKILL.md`
9. `docs/project_management/TASK_REVIEW_CHECKLIST.md`
10. `.agents/skills/connlab-lane-orchestrator/SKILL.md`
11. `.agents/skills/connlab-planner/SKILL.md`

### Executable helpers

12. `scripts/run_task.ps1`
13. `scripts/connlab_regate_evidence.py` (new)
14. `scripts/connlab_handoff_contract.py` (new)
15. `scripts/connlab_board_context.py` (new)

### Bounded tests

16. `tests/unit/test_connlab_regate_evidence.py` (new)
17. `tests/integration/test_connlab_regate_evidence_recovery.py` (new)
18. `tests/unit/test_connlab_handoff_contract.py` (new)
19. `tests/unit/test_connlab_board_context.py` (new)
20. `tests/unit/test_connlab_proportionate_regate_governance.py` (new)
21. `tests/unit/test_task_scoped_role_thread_lifecycle_governance.py` (bounded callback assertion)

### Primary-only board/history migration and task governance

22. `docs/task_board.md`
23. `docs/archive/task_board_history/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_pre_compaction.md` (new; Integrator only)
24. `docs/archive/task_board_history/index.json` (new; Integrator only)
25. `tasks/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF.md`
26. `docs/task_governance_proportionate_regate_evidence_reuse_and_compact_handoff_plan.md`
27. `docs/lane_evidence/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_planner.md`
28. `docs/lane_evidence/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_developer.md`
29. `docs/lane_evidence/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_reviewer.md`
30. `docs/lane_evidence/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_qa.md`
31. `docs/lane_evidence/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_integrator.md`

No additional path is authorized without Planner/User scope reconciliation.

## Phase Ownership

- Planner/Integrator on primary own `docs/task_board.md` and live archive migration.
- Developer may implement helpers, contracts, skills/protocols, and bounded tests only in the
  isolated lane. Developer must not edit the live board or generate the production archive.
- Reviewer and QA are read-only over the committed lane except their own evidence.
- Integrator merges only the reviewed package, runs guarded board migration on primary, validates
  the merged tree, records residuals, and closes execution state.

## Must Not Touch

- `backend/**`, `frontend/**`, product/API/persistence/schema/migration/Office/business tests, and
  all real databases or operator files.
- `docs/project_management/ROLE_THREAD_REGISTRY.md`; role identities do not change.
- `docs/project_management/ACTIVE_TASK_THREAD_BUNDLE.md` and all V1-Lite/V2 artifacts.
- `docs/project_management/CONTROLLED_LANE_ORCHESTRATION_V2.md`,
  `.agents/skills/connlab-controlled-lane/**`, `scripts/connlab_controlled_lane.ps1`, V2 tests,
  registry, heartbeat, pilot, and corrective work.
- `scripts/connlab_execution_gate.ps1`, `scripts/connlab_lane_worktree.ps1`,
  `scripts/task_complete_commit.ps1`, and `scripts/archive_completed_markdown.py`; existing behavior
  is regression-tested read-only.
- existing completed task/plan/evidence archives except the two new task-board-history paths.
- TASK_368E or any retained/frozen/cancelled lane/worktree/branch/evidence.
- package/lock files, dependencies, release output, push, publication, restart, remote-state
  mutation, destructive cleanup, reset, restore, discard, or force worktree removal.

## Locked Paths

After approval/token acquisition, every May Touch path above is exclusively locked to this task.
The live board and new history archive paths are additionally locked to primary Planner/Integrator;
they are never Developer-lane scratch files. No parallel exception is permitted for this global
governance task.

## Acceptance

1. Exact unchanged, fully bound Reviewer evidence can produce `REUSE_ALLOWED`.
2. Every missing/drift/impact/unknown condition above produces `FULL_REGATE` with stable reasons.
3. QA final-full validation cannot be marked satisfied by Reviewer reuse.
4. Shard aggregation is deterministic and fail-closed without changing execution ownership.
5. Compact capsules are reference-only, within budget, and resolve only verified refs.
6. Invalid refs or unsafe omissions produce `FULL_READ_REQUIRED`.
7. Callback validation accepts exactly seven fields and rejects missing, extra, reordered, or
   duplicate fields.
8. Cadence validation enforces start/end/blocker/direction/60-second events and suppresses
   unchanged waits.
9. Active human summary agrees exactly with execution JSON.
10. Board archive round-trip reproduces the exact original SHA-256; compact board meets line/byte
    budgets and contains no stale historical `Current` section.
11. Existing WIP/token/queue/preemption/recovery/worktree/archive/permanent-role tests pass.
12. Reviewer, QA, Integrator, worktree isolation, no-push, and non-destructive rules remain intact.

## Required Gates

This is a global governance change and is not a Quick Fix. Required route after approval:

```text
Planner -> User approval -> isolated Developer -> Reviewer -> mandatory QA -> Integrator
```

## Planned Lane Identity

- Lane: `task-governance-proportionate-regate-evidence-reuse-and-compact-handoff`
- Branch: `lane/task-governance-proportionate-regate-evidence-reuse-and-compact-handoff`
- Sibling worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-proportionate-regate-evidence-reuse-and-compact-handoff`
- Planning base: `4e7ce7ffa040039e8c7ebb659efe8cba5e00eeff`
- Worktree creation base: the future approval-only primary commit containing the approved task,
  plan, Planner evidence, and board authority; its full SHA must be recorded before Create.
- WIP: `1`; parallel exception: none.

No branch/worktree exists or is authorized at this planning gate.

## Stop Point

Commit this planning package locally and return to User review. Do not approve, activate, queue,
take a token, create a worktree, or dispatch implementation.
