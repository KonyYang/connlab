# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF

Status: `developer_fix_dispatch_ready`

Type: governance / execution-authority / orchestration-efficiency

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Owner at this gate: permanent Planner legacy transition governance. Next gate: Orchestrator
dispatches Developer for the bounded B1-B5 fail-closed fix pass.

## Approval Boundary

The User explicitly approved Task A only and authorized automatic execution through local
Integrator acceptance. This approval does not approve Task B or revive the superseded umbrella.
Approval base `15c3120a6d889e97d098c2cb9f8c8ef852d74f69` contains the approved Task/Plan/
Planner evidence. Reviewer blocked the clean package at lane HEAD
`1e4d080fb0b17a520aa5afb924fd62ffe4bf2203` with five executable fail-closed findings. This legacy
governance step retains Task A as the sole WIP=`1` token owner, changes only the durable gate from
`gate_running/Reviewer` to `implementation_running/Developer`, and records
`developer_fix_dispatch_ready`. Reviewer re-gate, mandatory QA, and Integrator remain required. No
live board maintenance, push, publication, restart, destructive cleanup, or parallel exception is
authorized.

## User Approval And Activation Boundary

- Approval source: direct User approval recorded by permanent Orchestrator on 2026-08-01.
- Approved scope: this exact Task A and its plan at primary
  `d791e74a9811033058c38ee329bb3be8ee1f6504`.
- Authorized automatic route: isolated Developer -> Reviewer -> mandatory QA -> local Integrator
  acceptance, including bounded fixes inside the frozen scope.
- Approval/worktree base: `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Reviewer final/evidence HEAD is `1e4d080fb0b17a520aa5afb924fd62ffe4bf2203` over the exact
  approved base and Developer package. Lane and primary worktree/index are clean, ancestry is
  continuous, and Reviewer evidence blob `8f8534adc660f71f2fbe435404699e321acc5174` is
  `reviewer_blocked`.
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

The exact branch/worktree is clean at final Developer/evidence HEAD
`1e4d080fb0b17a520aa5afb924fd62ffe4bf2203` over the pinned approval base. The Reviewer-only delta
adds only Reviewer evidence. The permanent Orchestrator may now dispatch Developer for B1-B5;
Reviewer must re-gate the resulting clean checkpoint before mandatory QA.

## Reviewer-Blocked Bounded Fix Contract

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

## Compatibility And Rollback

- Before acceptance, existing manual transitions and full reads remain authoritative.
- Unsupported/missing metadata always retains the old full-read/manual governance path.
- Code rollback is a local Git revert. Board rollback is a separately reviewed exact patch from an
  index-verified archive; the helper only proves/reconstructs into temp and never silently restores
  live authority.
- Existing execution gate stays read-only and schema-compatible. Existing tasks without new
  transition metadata cannot use the helper and fail closed to manual governance.

## Stop Point

Return `developer_fix_dispatch_ready` to Orchestrator. Do not dispatch Developer, edit the lane,
run live migration/maintenance, or perform Task B work in this Planner turn.
