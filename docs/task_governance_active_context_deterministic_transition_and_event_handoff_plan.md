# Active Context Deterministic Transition And Event Handoff Implementation Plan

Status: `developer_fix_dispatch_ready`

Task: `TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF`

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

## Approval And Activation Record

- The User explicitly approved Task A only on 2026-08-01 and authorized the exact automatic route
  `Developer -> Reviewer -> mandatory QA -> local Integrator acceptance`.
- Approved planning HEAD: `d791e74a9811033058c38ee329bb3be8ee1f6504`.
- Immutable approval/worktree base:
  `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`; primary execution authority pins it before Create.
- Reviewer blocked the clean package at final evidence HEAD
  `1e4d080fb0b17a520aa5afb924fd62ffe4bf2203` with B1-B5. Planner uses legacy governance to retain
  the sole Task A token and record `implementation_running/Developer` plus
  `developer_fix_dispatch_ready`; it does not dispatch Developer.
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

### Step A5 — Developer package handoff and bounded fix (current)

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

### Step A6 — Reviewer gate (blocked; mandatory re-gate after bounded fix)

- Full independent review; A cannot use its own new compact read or transition path to reduce this
  review.
- Reproduce all state transitions, invalid-state families, archive safety, budget checks, and
  no-shell/no-path-escape/no-partial-write properties in disposable repositories.
- Verify production apply is impossible outside sole `gate_running/Integrator` and the deleted
  token-null audit exception is absent.
- Blocking findings return to Developer; Reviewer never fixes or merges.

### Step A7 — Mandatory QA

- Validate final reviewed HEAD from a clean lane/temp worktree/exact archive.
- Run the complete A validation matrix on Windows, including fault injection and second/third
  closeouts.
- Run one event-driven controlled pilot and require callback-to-dispatch <=90 seconds, zero Planner
  launches, one transition/dispatch max, and budget reports.
- QA does not mutate production board/history or product data.

### Step A8 — Integrator merge, first migration, and closeout

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

Stop if migration target/hash/role/token/state changed, or any quantitative target fails.

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

Return `developer_fix_dispatch_ready` to Orchestrator. Reviewer evidence at
`1e4d080fb0b17a520aa5afb924fd62ffe4bf2203`, blob
`8f8534adc660f71f2fbe435404699e321acc5174`, its B1-B5 scope, and ancestry are verified. Planner
does not dispatch Developer, edit the lane, run live migration/maintenance, or perform Task B work.
