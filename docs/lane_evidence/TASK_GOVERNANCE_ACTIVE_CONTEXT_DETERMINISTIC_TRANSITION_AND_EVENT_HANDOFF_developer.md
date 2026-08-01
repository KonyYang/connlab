# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF — Developer Evidence

ROLE: Developer
STATUS: ready_for_review

## Authority And Checkpoint

- Primary authority root: `D:\PythonProject\connlab`
- Primary governance HEAD used for every production read: `916f1846dd745d22fc8fb99463442d0691078265`
- Production dispatch snapshot: `65dded27b6ac73b42aa506a3713ae9bf3ec4508b3575cd4ecf1ad7407de2b7c1`
- Lane: `lane/task-governance-active-context-deterministic-transition-and-event-handoff`
- Worktree: `D:\PythonProject\connlab-worktrees\task-governance-active-context-deterministic-transition-and-event-handoff`
- Approved base: `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`
- Core implementation checkpoint: `2707c96942a506b683769688f224c08e985a2036`
- Bounded literal `--input` compatibility checkpoint: `1b0ba8a6bab5943031f786492c95ebfcea961c6b`
- `git show --check` passed; lane was clean immediately after the implementation checkpoint.

The task, approved plan, Planner evidence, lane board copy, execution gate, registry, bundle, V1-Lite/
V2 artifacts, product/runtime code, and archive/index production paths were not modified.

## Implemented Contract

1. Added the normative active-context contract and compact references from existing governance,
   while retaining WIP=1, Quick Fix/reconciliation, explicit parallel exception, permanent-role,
   non-rebase, and frozen-V2 semantics.
2. Added a read-only inspect/plan plus board-only apply transition helper for exactly
   `DEVELOPER_READY`, `REVIEWER_BLOCKED`, `REVIEWER_PASS`, and `QA_PASS`. It validates primary/lane
   HEADs, clean status/index, ancestry, immutable task gate metadata, evidence Git blob/SHA-256/
   callback facts, scope/locks, queue/pause/Quick Fix/parallel/residual facts, markers, and summary.
   Same transitions are idempotent; divergent duplicates and every mismatch fail closed.
3. Added active-board maintenance with all three thresholds, exact first-generation board archive,
   incremental terminal-only later generations, canonical hash-chained JSONL index, path/link guard,
   Integrator-only apply, board-last replacement, injected-failure rollback, and byte-exact rollback
   proof. No production apply was run.
4. Added reference-only dispatch/read-set validation, exact seven-field callback validation with
   literal-or-file input,
   `FULL_READ_REQUIRED`, one-transition/one-dispatch turn budget, zero routine Planner launches,
   heartbeat/unchanged-wait enforcement, and <=90-second pilot validation.
5. Changed `run_task.ps1 -Preview` from a copied prompt/worktree dump to a compact JSON reference
   capsule pinned to primary board/task Git blobs.

## Exact Implementation Paths (23)

```text
.agents/skills/connlab-lane-orchestrator/SKILL.md
.agents/skills/connlab-planner/SKILL.md
AGENTS.md
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

## TDD Evidence

RED was captured before each helper existed:

- `py -m pytest tests\unit\test_connlab_active_context_governance.py -q` -> `3 failed` (missing
  contract/helpers and over-budget Orchestrator skill).
- transition unit/recovery modules -> `7 failed` before helper implementation.
- active-context unit/integration modules -> `9 failed` before helper implementation.
- handoff module -> `6 failed` before helper implementation.

GREEN progression:

- transition unit/recovery -> `8 passed` after terminal-inspect and compatibility hardening.
- active-context unit/integration -> `9 passed`, including first/second/third closeouts and all
  three injected replacement boundaries.
- focused transition/active-context/handoff helpers -> `28 passed`.
- literal callback/file-input focused re-gate -> `11 passed`.
- final new plus existing governance matrix below -> `105 passed`.

## Final Validation

```text
py -m pytest \
  tests/unit/test_connlab_execution_transition.py \
  tests/integration/test_connlab_execution_transition_recovery.py \
  tests/unit/test_connlab_active_context.py \
  tests/integration/test_connlab_board_closeout_maintenance.py \
  tests/unit/test_connlab_handoff_contract.py \
  tests/unit/test_connlab_active_context_governance.py \
  tests/unit/test_connlab_execution_gate_script.py \
  tests/integration/test_connlab_execution_gate_recovery.py \
  tests/unit/test_execution_wip_and_quick_fix_governance.py \
  tests/unit/test_connlab_lane_worktree_script.py \
  tests/unit/test_markdown_archive_tool.py \
  tests/unit/test_task_scoped_role_thread_lifecycle_governance.py -q
=> 105 passed in 84.30s

py -m py_compile <three helpers and six bounded new test modules>
=> passed

PowerShell AST parse: run_task.ps1, connlab_execution_gate.ps1,
connlab_lane_worktree.ps1
=> AST_PARSE_OK_3

git diff --check
git diff --cached --check
git show --check --format=oneline --stat 2707c96942a506b683769688f224c08e985a2036
=> passed (Git emitted only expected LF/CRLF checkout warnings before staging)
```

The allowlist scan found exactly the 23 implementation paths above, no unexpected/missing path,
no `backend/` or `frontend/` path, and no board/registry/bundle/V2/execution-gate/task-complete path.
All new helpers are below the 500 physical-line hard limit: transition `375`, active context `385`,
handoff `220`. New bounded tests remain below 400 lines.

## Production Zero-Write Evidence

Against primary HEAD `916f1846...`:

- transition `inspect`: `ALLOW_INSPECT`, zero-write, digest before/after
  `65dded27b6ac73b42aa506a3713ae9bf3ec4508b3575cd4ecf1ad7407de2b7c1`.
- active-context `inspect`: `ALLOW_INSPECT`, `2514` lines, `786301` bytes, `153` eligible terminal
  details, zero-write.
- `plan-maintenance`: `MAINTENANCE_REQUIRED`, generation `1`, plan digest
  `1a72acdd8141c52dfda5bb4c00aa36a47e78c9534396c806a8e0d8fa92a714e0`, projected compact board
  `111` lines / `18383` bytes / `0` terminal details, zero-write.
- primary board SHA-256 before/after remained
  `cba5eafe2ea1d7f883930106d20c96f61fd3155eb32214e94134e557bfe5905e`; primary status remained
  clean; no archive or index was created.
- final `run_task.ps1 -Preview`: valid `connlab.orchestrator-trigger.v1`, `1482` bytes, two immutable
  refs, no worktree dump, board hash unchanged.

## Quantitative Evidence

| Artifact / behavior | Approved baseline | Implemented / measured |
| --- | ---: | ---: |
| board | 2466 lines / 781091 bytes | dispatch-time 2514 / 786301; planned 111 / 18383 |
| Orchestrator skill | 305 / 17304 | 120 / 6092 |
| Planner skill | 98 / 3972 | 103 / 4341 |
| orchestration protocol | 303 / 14120 | 123 / 6881 |
| `run_task.ps1` | 123 / 4854 | 115 / 3980 |
| preview reference capsule | prior copied prompt/worktree list | 1482 bytes, 16 logical items removed to compact JSON |
| validated complete capsule | n/a | 1046 bytes |
| dispatch template | n/a | 75 bytes |
| default five-ref read capsule | n/a | 701 bytes |
| seven-field callback | n/a | 162 bytes |
| Orchestrator routine turn | >=200 historical lower-bound items | <=1 transition + <=1 dispatch |
| routine Planner launches | historical repeated launches | 0 |
| controlled simulated callback -> dispatch | n/a | 45 seconds (<=90) |

The cadence tests also reject a second transition/dispatch, heartbeat under 60 seconds, unchanged
waits, and pilot latency over 90 seconds. Mandatory independent QA still owns the real controlled
pilot after Reviewer pass.

## Protected Equality And Safety

- Excluding primary and this active lane, registered protected worktrees before/after:
  count `10`, clean count `10`, canonical HEAD/status digest
  `0d32345b60e5757b452d8e621a1d059edaa45a06b174759795d6f48c2596908a` both times.
- Base/head Git blobs are byte-identical for the role registry, active bundle, V2 protocol/skill/
  helper, execution gate, task-complete helper, lane board, approved task, approved plan, and Planner
  evidence. Representative protected blobs: registry `c5083212...`, bundle `3635fa07...`, V2
  protocol `037c7930...`, execution gate `88b8c018...`, lane board `b5d12ab2...`.
- No real Create/Retire, production transition apply, production maintenance apply, archive/index
  generation, real data access, product/API/schema write, install, restart, release, push, merge,
  reset, restore, clean, rebase, discard, or destructive cleanup occurred.

## Reviewer Focus

Reviewer should independently reproduce the four-event matrix and mismatches; inspect general
terminal state; test task-metadata QA omission; inspect archive eligibility so proposed/active lines
cannot be removed; reproduce corrupt/non-contiguous/conflict/path-link/fault rollback cases; and
verify primary-root/ref/blob/working-board validation plus all byte budgets. Mandatory QA and the
real <=90-second pilot remain required before Integrator may merge or run first production apply.

## Seven-Field Implementation-Package Callback

```text
TASK_ID: TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF
ROLE: Developer
STATUS: ready_for_review
EVIDENCE: docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md
COMMIT: 1b0ba8a6bab5943031f786492c95ebfcea961c6b
NEXT: Reviewer
BLOCKER: none
```

The external role callback reports the final evidence-checkpoint HEAD, because a commit cannot
self-reference its own SHA inside its tracked contents.

## Bounded Reviewer Fix Pass — B1-B5

- Required clean start: branch
  `lane/task-governance-active-context-deterministic-transition-and-event-handoff` at
  `1e4d080fb0b17a520aa5afb924fd62ffe4bf2203`; original base remained
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Reviewer authority: primary `b246e194c075f0f6a3038d043fe459a43876a088` and exact Reviewer
  evidence at the task-owned Reviewer path. No Reviewer evidence or normative contract changed.
- Focused RED: the seven direct B1-B5 reproductions failed before implementation (`7 failed`),
  including live/existing rollback output, cross-task capsule, missing transition metadata,
  historical-status substring, event-name-only maintenance, corrupt idempotent rerun, and a
  one-second first heartbeat.
- Fix checkpoint: `de9a4e0f89730a5f408460852ad3b6f53ceb1000`.

### Reviewer Finding Closure Map

1. **B1:** `prove-rollback` now requires `--temp-root`, proves a pre-existing temp root outside the
   repository, rejects symlink/junction traversal, escape and every existing target, and uses
   exclusive `xb` creation. Safe first/second/third-generation outputs remain byte-exact.
2. **B2:** the <=4096-byte capsule now requires typed task/token/state/role/lane/branch/worktree/
   base/head, gate/scope/lock digests, evidence status, named next action and stop conditions. It
   parses the pinned primary board and binds task/plan/evidence refs plus clean primary/lane Git
   facts; cross-task, stale, unrelated, incomplete and drifted inputs return `FULL_READ_REQUIRED`
   or a stable block.
3. **B3:** routine transitions require `scope_contract_ref`, `may_touch_digest`,
   `locked_paths_digest`, and `last_transition_id`, bind the scope ref to the approved lane base,
   recompute canonical task May Touch/lock digests, and parse exactly one machine evidence record.
   Exact duplicate transitions remain zero-write; divergent task/lane/primary/status/context
   duplicates block.
4. **B4:** maintenance requires complete Developer/Reviewer/QA transition entries, evidence Git
   refs/commit/blob/SHA/status/ancestry, retained-context binding, and the accepted active-context
   helper blob. The versioned index recomputes source/archive/compact/count/rollback/plan/hash-chain
   facts. `ALREADY_APPLIED` additionally requires the exact compact board, index/archive chain,
   plan digest and expected clean/maintenance-only status. Corrupt, non-contiguous, escaped,
   junction, conflict, partial-write, and second/third rollback cases are executable negatives.
5. **B5:** every heartbeat, including the first, is measured from the immediately preceding
   permitted material event and requires >=60 seconds plus a changed state. Mixed/negative order,
   duplicate lifecycle events and dispatch-before-transition block; the 45-second
   callback-to-dispatch positive remains within the <=90-second budget.

### Fix-Pass Validation

- Focused Reviewer reproductions: `7 passed`; focused expanded helper matrix: `41 passed`.
- Complete approved 12-module matrix with added negatives: `129 passed in 206.49s`.
- Python compilation: all three helpers and six bounded Task A test modules passed.
- PowerShell AST: `run_task.ps1`, `connlab_execution_gate.ps1`, and
  `connlab_lane_worktree.ps1` -> `AST_PARSE_OK_3`.
- Helper physical lines: active context `494`, transition `452`, handoff `334`; all `<500`.
- Production zero-write inspect/plan at primary
  `b246e194c075f0f6a3038d043fe459a43876a088`: `ALLOW_INSPECT` then
  `MAINTENANCE_REQUIRED`; board `2514` lines / `786622` bytes / `153` terminal records; planned
  compact board `111` / `18656`; plan digest
  `261a9d80fe95f9b9b783bd5f13889e948b5978ecc3a51af8282cd244d6ecd24e`. HEAD, board SHA-256
  `8dba8027cb99fe4c760ccc8f7304ebebc83dff007ccc33e5629756e94ccb2ec1`, and clean status were
  identical before/after; no production archive/index was created.
- Exact implementation diff contains only three approved helpers and four bounded tests. No
  `run_task.ps1`, task/plan/board, normative policy/skill, Reviewer evidence, product, V2,
  registry/bundle, or protected-lane path changed.
- Ten protected worktrees remained clean at their exact registered HEADs; canonical digest for
  this fix pass was `4f350b88c6dc4c026fd9a43d01ef700d6c75e0bd3f29c7f00ed8c2299ca3f130`
  before and after.

## Seven-Field Bounded-Fix Callback

```text
TASK_ID: TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF
ROLE: Developer
STATUS: ready_for_review
EVIDENCE: docs/lane_evidence/TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF_developer.md
COMMIT: de9a4e0f89730a5f408460852ad3b6f53ceb1000
NEXT: Reviewer
BLOCKER: none
```

The external callback below reports the final evidence-checkpoint HEAD.
