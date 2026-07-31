# TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH — Reviewer Evidence

Status: `reviewer_pass`
Role: permanent Reviewer
Date: 2026-07-31
Next: permanent QA

## Authorization And Review Boundary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary dispatch HEAD: `f465b5f576229544f773095bb1086961152e6be8`.
- Review base: `a1968c4999a33c6bee18c9185882ea3b927c2004`.
- Implementation checkpoint: `41a604d15f7472e4d8efc4673dbd8c9272c1e45d`.
- First-gate review HEAD: `ee3aca6fc3712a166f7ce30d644a5954ae5d0dde`.
- Prior Reviewer evidence HEAD: `ee2c179659c9636093cc2c3dc37c38a79f07bb7a`.
- Developer fix checkpoint: `7cb4d6db7f978875de73c1f6b0fec5e557f4e565`.
- Full re-gate review HEAD: `56ed70647b0eaa51fabf404c40caaf42acc69337`.
- Second Reviewer block/evidence HEAD: `090fdc254edadaeb91a003890d3a920adcd9c739`.
- Second Developer fix checkpoint: `911713b85b28d172b8919fac1f127a2e3b843246`.
- Final full re-gate review HEAD: `cafdf89144ce3a03403c3d6758f430655533e4b5`.
- Branch: `lane/task-governance-wip1-and-proportionate-quick-fix-fast-path`.
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-wip1-and-proportionate-quick-fix-fast-path`.

Reviewer read `AGENTS.md`, the current primary board, approved task/plan, Planner and twice-updated
Developer evidence, `TASK_REVIEW_CHECKLIST.md`, the normative policy, changed
protocols/skills/scripts, and all five approved test modules. The final full re-gate covered only
committed `a1968c4999a33c6bee18c9185882ea3b927c2004..cafdf89144ce3a03403c3d6758f430655533e4b5`
and focused separately on
`090fdc254edadaeb91a003890d3a920adcd9c739..cafdf89144ce3a03403c3d6758f430655533e4b5`.
No implementation file, other evidence, primary file, product lane, retained worktree, V2 state,
remote, runtime, or service was modified.

## Final Full Re-Gate Findings (Current)

### Blocking

- None.

### Non-Blocking

- None.

The second narrow fix closes both reproduced `ALLOW_INSPECT` gaps. General validation now requires
the complete canonical queue record, validates field types, task/position/sequence uniqueness,
stored position order, timestamp/sequence consistency, and equal-priority FIFO order. It also
requires the complete secondary role/branch/worktree/HEAD record for every parallel exception and
validates canonical types, lane-derived branch, absolute distinct worktree, 40-hex HEAD, owner
consistency, and disjoint locks. Actual secondary dispatch still verifies live clean branch/
worktree/HEAD Git facts before allowing implementation.

## Final Full Re-Gate Validation

Reviewer-owned disposable `Inspect` matrix:

- queue containing only `task_id + queue_position` -> `BLOCKED_QUEUE_INVALID`;
- complete two-record queue -> `ALLOW_INSPECT`;
- duplicate task -> `BLOCKED_QUEUE_TASK_DUPLICATE`;
- duplicate position -> `BLOCKED_QUEUE_POSITION_DUPLICATE`;
- stored out-of-order queue -> `BLOCKED_QUEUE_FIFO_INVALID`;
- string rather than integer enqueue sequence -> `BLOCKED_QUEUE_INVALID`;
- complete parallel record -> `ALLOW_INSPECT`;
- each independently missing `secondary_role`, `secondary_branch`, `secondary_worktree`, or
  `secondary_head_sha` -> `BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE`.

Fresh complete required suite:

```powershell
py -m pytest tests\unit\test_connlab_execution_gate_script.py tests\integration\test_connlab_execution_gate_recovery.py tests\unit\test_execution_wip_and_quick_fix_governance.py tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
```

Result: `66 passed in 40.93s`.

Fresh representative first-review path rerun covered Reviewer/QA/Integrator `gate_running`
dispatch rejection, untouched pre-merge Resume rejection, real merge checkpoint Resume success,
stale-lane authority rejection, live secondary Git-fact dispatch, QF-1/QF-4, run-task queue/no
Codex, and worktree Create queue/no-write. Result: `11 passed in 11.86s`.

Additional checks:

- all three PowerShell scripts parse with zero AST errors;
- helper/script line counts are `307`, `123`, and `305`; test module line counts are `496`, `489`,
  `340`, `219`, and `49`, all within the approved 500-line limit;
- `git diff --check` for original base through final review HEAD and `git show --check` for the
  second implementation/evidence commits pass;
- the full committed range remains the exact 18 implementation/evidence paths plus this Reviewer
  evidence path; the second focused fix contains only helper, bounded unit test, and Developer
  evidence;
- primary is clean on `master` at
  `f465b5f576229544f773095bb1086961152e6be8`; all frozen V2, cancelled browser-release, and
  retained TASK_368B/C worktrees retain their prior clean HEADs; protected product/V2 diff is
  empty;
- lane-local production helper and `run_task -Preview` both resolve authority to
  `D:\PythonProject\connlab` and fail closed with `BLOCKED_MARKERS_MISSING` until Integrator
  reconciles the candidate block; neither writes or routes;
- the candidate board block preserves WIP `1`, the exact task/branch/worktree/base, empty queue,
  null pause/Quick Fix/parallel records, and primary dispatch SHA. Read-only `git merge-tree`
  reports only the expected changed-in-both `docs/task_board.md`, so Integrator can reconcile live
  primary facts without authority loss.

## Second Gate Findings (Historical)

### Blocking 1 — `Inspect` still accepts incomplete queue and parallel authority records

The first Developer fix closes the prior owner/state, dispatch, reconciliation, root-resolution,
terminal-residual, and basic parallel-proof reproductions. However, the general authority validator
still does not enforce the complete record shapes frozen by the approved plan:

1. `scripts/connlab_execution_gate.ps1:152-159` treats a queue record containing only `task_id` and
   `queue_position` as complete. The approved plan requires task/lane, durable enqueue
   sequence/time, dependencies, locks, requested priority, position, and evidence. An independent
   disposable repository with only `{"task_id":"TASK_Q","queue_position":1}` returned exit `0`,
   `ALLOW_INSPECT`, and `allowed: true`.
2. `scripts/connlab_execution_gate.ps1:190-198` does not require the recorded secondary role,
   branch, worktree, or HEAD for a parallel exception. Those facts are checked later only for
   `ImplementationDispatch` at lines 225-233. An independent disposable repository with a valid
   primary owner and the current `_parallel()` record—but no `secondary_role`,
   `secondary_branch`, `secondary_worktree`, or `secondary_head_sha`—also returned exit `0`,
   `ALLOW_INSPECT`, and `allowed: true`.

This violates the approved complete-FIFO schema, the explicit secondary-owner Git-fact gate, and
restart/cross-conversation fail-closed authority. It also leaves two approved negative scenarios
outside the executable matrix even though all committed tests pass. Developer must require the
complete frozen queue fields and complete secondary role/Git fields during general validation, and
add bounded `Inspect` regressions for both records. No product or unrelated governance change is
needed.

### Non-Blocking

- None.

## Full Re-Gate Closure And Validation

The following first-gate issues are independently closed:

- `gate_running` under Reviewer, QA, or Integrator blocks `ImplementationDispatch` with
  `BLOCKED_DISPATCH_STATE`.
- active/owner mismatch, ownerless parallel exception, duplicate queued task identity,
  reconciling without accepted Quick Fix proof, empty terminal residual closeout, incomplete
  residual records, and incomplete base parallel proof all fail `Inspect` with stable
  `BLOCKED_*` codes.
- positive reconciliation creates a new clean merge checkpoint after current `master` is merged
  into the original lane; accepted Quick Fix and master ancestry plus validation evidence are
  required before `ALLOW_RESUME`. An untouched checkpoint and missing acceptance remain blocked.
- merge-conflict/failure fixtures preserve both histories/evidence and owner-null
  `paused_preempted`; no rebase/reset/restore/discard path was introduced.
- dynamic QF-1 semantically neutral button copy is allowed; QF-4 API/schema/authority scope is
  rejected.
- dynamic queue paths start no Codex process and create no branch/worktree.
- a lane-local production invocation resolves `authority_root` to `D:\PythonProject\connlab` and
  currently fails closed with `BLOCKED_MARKERS_MISSING` because the primary dispatch board has not
  yet integrated the candidate schema. `run_task -Preview` fails closed for the same primary fact;
  neither invocation writes.

Fresh independent validation at review HEAD
`56ed70647b0eaa51fabf404c40caaf42acc69337`:

```powershell
py -m pytest tests\unit\test_connlab_execution_gate_script.py tests\integration\test_connlab_execution_gate_recovery.py tests\unit\test_execution_wip_and_quick_fix_governance.py tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
```

Result: `57 passed in 37.09s`.

Reviewer-owned disposable authority matrix results:

- `active_owner_mismatch` -> `BLOCKED_ACTIVE_OWNER_MISMATCH`
- `idle_secondary_owner` -> `BLOCKED_PARALLEL_PRIMARY_REQUIRED`
- `duplicate_queue_identity` -> `BLOCKED_QUEUE_TASK_DUPLICATE`
- `reconciling_without_acceptance` -> `BLOCKED_QUICK_FIX_NOT_ACCEPTED`
- `terminal_without_residual` -> `BLOCKED_TERMINAL_RESIDUAL_REQUIRED`
- `parallel_incomplete_proof` -> `BLOCKED_PARALLEL_EXCEPTION_INCOMPLETE`
- `residual_incomplete` -> `BLOCKED_RESIDUAL_INCOMPLETE`
- `gate_running_dispatch` -> `BLOCKED_DISPATCH_STATE`
- `queue_missing_frozen_fields` -> **unexpected `ALLOW_INSPECT`**
- `parallel_missing_secondary_git` -> **unexpected `ALLOW_INSPECT`**

Additional validation:

- all three PowerShell scripts parse with zero AST errors;
- helper/script line counts are `268`, `123`, and `305`; five test modules are at or below the
  approved 500-line ceiling (`500`, `489`, `340`, `219`, `49`);
- `git diff --check` for base through re-gate HEAD and `git show --check` for both fix commits pass;
- full committed range contains the exact 18 implementation/evidence paths plus this Reviewer
  evidence path; the focused fix range contains only ten approved paths;
- primary remains clean on `master` at
  `f465b5f576229544f773095bb1086961152e6be8`; all registered frozen V2,
  cancelled browser-release, and retained TASK_368B/C worktrees retain their prior HEADs and are
  clean; protected V2/product diff is empty;
- read-only `git merge-tree` still identifies only the expected changed-in-both board governance
  reconciliation. The lane candidate preserves the primary dispatch SHA and can be reconciled by
  Integrator after this blocker is closed; it must not be treated as live authority now.

## First Gate Findings (Historical)

### Blocking 1 — Write-capable dispatch and resume are not state-transition safe

`scripts/connlab_execution_gate.ps1:387-426` authorizes `ImplementationDispatch` whenever the
requested task is the token owner and the active worktree/HEAD are clean. It does not restrict the
intent to an implementation-writing state or validate the current gate role. Therefore the same
task can receive a new write-capable implementation dispatch while its immutable HEAD is under
Reviewer, QA, or Integrator review.

Disposable-repository reproduction used the committed test fixture with:

```text
execution_state: gate_running
execution_token_owner: TASK_ORIGINAL
active.role: Reviewer
```

Observed result:

```json
{"code":"ALLOW_DISPATCH","allowed":true,"execution_state":"gate_running","execution_token_owner":"TASK_ORIGINAL"}
```

`scripts/connlab_execution_gate.ps1:482-486` has a second transition bypass. `Resume` checks only
that state is `reconciling` and owner matches. It does not require the accepted Quick Fix record,
accepted-on-master proof, current-master merge ancestry, a new reconciliation checkpoint,
preserved branch/worktree cleanliness, or validation evidence.

Disposable reproduction set `reconciling(TASK_ORIGINAL)` with a complete pause record but
`quick_fix: null`, left the original lane at its pre-merge base, and performed no merge. Observed:

```json
{"code":"ALLOW_RESUME","allowed":true,"execution_state":"reconciling","execution_token_owner":"TASK_ORIGINAL"}
```

This violates token/gate immutability, non-destructive reconciliation, and cross-conversation
fail-closed requirements. Developer must make dispatch intent role/state-specific and require
durable, Git-verifiable reconciliation completion before `ALLOW_RESUME`.

### Blocking 2 — The general schema validator accepts contradictory execution authority

The invariant layer at `scripts/connlab_execution_gate.ps1:277-343` validates only owner nullness,
queue-position uniqueness, a subset of pause/Quick Fix fields, and shallow parallel fields. It
does not enforce the complete state shapes frozen by the task/plan. Independent disposable
reproductions returned `ALLOW_INSPECT` for all of these contradictory records:

1. `implementation_running` owner `TASK_OWNER` with `active.task_id: TASK_OTHER`;
2. `idle` with owner `null` but a populated secondary parallel owner/exception;
3. two queue records for the same task at positions `1` and `2`;
4. `reconciling` without a Quick Fix acceptance record (and, as Blocking 1 proves, it can also
   return `ALLOW_RESUME`).

The validator also does not enforce terminal/failure residual closeout: `residuals` records are
not schema-checked, and the current tests accept `complete(null)` with an empty residual set and do
not prove the required preempting-failure histories/evidence ownership.

This makes `ALLOW_INSPECT` and the snapshot digest unsafe as a restart/recovery authority. Developer
must enforce active-owner/role/state consistency, unique and complete FIFO task records, complete
terminal/failure residual ownership, Quick Fix/reconciling proof, and a parallel exception only
alongside a valid primary owner and exact structured independence/approval/end-condition facts.

### Blocking 3 — Production authority resolution can read a stale worktree board copy

`scripts/connlab_execution_gate.ps1:25-27,218-225` treats the helper's own `$PSScriptRoot` parent
as the production repository root and rejects another production root unless the test-only switch
is supplied. `scripts/run_task.ps1:20,44-48` and
`scripts/connlab_lane_worktree.ps1:77-81,126-132` invoke the adjacent helper without pinning the
primary worktree.

Because every lane contains a versioned copy of `docs/task_board.md`, invoking the entry scripts
from a lane reads that lane's potentially stale execution block rather than the primary board that
the policy declares the sole execution authority. The safe Reviewer preview in this exact lane
demonstrated the issue: it read the lane candidate board and returned `ALLOW_RESUME` for the old
Developer/`implementation_running` snapshot while the actual role chain was already at Reviewer.

Developer must make production gate calls resolve and verify the authoritative primary worktree
board, or explicitly fail closed when invoked from a non-primary/stale copy. Add a disposable
two-worktree regression in which primary and lane board states differ; the stale lane must never
authorize routing/Create/dispatch.

### Blocking 4 — The claimed 27-scenario executable matrix does not cover the unsafe negatives

All committed tests pass, but several approved scenarios are represented only by string-presence
assertions or by permissive snapshots:

- `tests/integration/test_connlab_execution_gate_recovery.py:272-290` calls `Resume` on the
  untouched pre-merge base and expects success; it performs no master merge and records no new
  reconciliation checkpoint.
- There is no negative that forbids `ImplementationDispatch` during Reviewer/QA/Integrator
  `gate_running`.
- There is no executable merge-conflict/reconciliation-failure path proving owner-null
  `paused_preempted` plus preservation of both histories/evidence.
- The terminal test at `tests/integration/test_connlab_execution_gate_recovery.py:315-361` does
  not reject missing cancellation/failure residual ownership.
- The parallel test does not reject a secondary owner without a valid primary owner or duplicate
  queued task identities.
- `tests/unit/test_execution_wip_and_quick_fix_governance.py:63-73` checks policy substrings only;
  it does not exercise a positive lightweight semantically-neutral button-label capsule or a
  dynamic QF-4 rejection.
- `run_task` queue-only and worktree Create gating are checked statically, not through an
  executable no-Codex/no-Create queue path.

Developer must add bounded dynamic regressions for the reproduced failures and complete the
approved scenario matrix. Passing string assertions are not sufficient for a gate intended to
prevent writes across conversations and restarts.

### Non-Blocking

- None separately recorded. The findings above block QA.

## Scope And Protected-State Review

The base-to-review-HEAD range contains exactly the approved 18 paths: the 17 implementation paths
listed in Developer evidence plus that Developer evidence file. No product/backend/frontend/API/
schema/database/Office/Matrix/Fee/LTR/runtime path changed.

No diff exists under Controlled Lane V2 protocol/skill/helper/registry/test paths,
`ACTIVE_TASK_THREAD_BUNDLE.md`, `ROLE_THREAD_REGISTRY.md`, or `scripts/task_complete_commit.ps1`.
The helper is read-only in its implemented commands and its reported `zero_write` behavior was
observed on disposable fixtures.

All registered primary, frozen V2, cancelled browser-release, retained TASK_368B/TASK_368C, and
current governance worktrees were re-read after tests. Their recorded HEADs were unchanged and
every status count was zero.

The new helper is 492 physical lines, below but close to the 500-line hard limit. Other changed
scripts and bounded tests are below 500 lines.

## Primary Board Reconciliation Review

Primary remains clean at exact dispatch HEAD
`f465b5f576229544f773095bb1086961152e6be8`. The lane candidate JSON records that SHA as
`last_governance_commit` and preserves the primary bootstrap facts: WIP `1`, this task as sole
owner, base/worktree identity, empty queue, and null pause/Quick Fix/parallel exception.

Read-only `git merge-tree` confirms `docs/task_board.md` is an expected changed-in-both conflict;
Integrator can reconcile the candidate block with current primary facts by exact primary-owned
board editing without losing the dispatch record. That reconciliation is not authorized at this
Reviewer gate and does not close the helper blockers above.

## Independent Validation

```powershell
py -m pytest tests\unit\test_connlab_execution_gate_script.py -q
```

Result: `13 passed in 8.17s`.

```powershell
py -m pytest tests\integration\test_connlab_execution_gate_recovery.py -q
```

Result: `11 passed in 12.60s`.

```powershell
py -m pytest tests\unit\test_execution_wip_and_quick_fix_governance.py -q
```

Result: `6 passed in 0.06s`.

```powershell
py -m pytest tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
```

Result: `9 passed in 0.48s`.

Total approved suite: `39 passed`. These green results do not cover the reproduced blocking
states.

Additional results:

- Windows PowerShell `ScriptBlock.Create(...)` parsing passed for all three changed scripts.
- Lane `Inspect` and `run_task -Preview` exited zero and performed no writes; the preview also
  exposed the stale lane-board authority problem in Blocking 3.
- `git diff --check` for base through review HEAD: passed.
- `git show --check` for implementation and Developer-evidence commits: passed.
- exact 18-path allowlist and forbidden/protected-path scans: passed.
- pre-evidence lane worktree/index, including untracked files: clean.

## First Gate Conclusion And Handoff (Historical)

- Conclusion: `reviewer_blocked`
- Blocking findings: four, with one shared required fix theme — complete fail-closed transition,
  schema, authority-root, and executable-negative enforcement
- Next role: permanent Developer
- QA must not start until a clean fix checkpoint closes every reproduced path and Reviewer re-gate
  passes.

## Second Gate Conclusion And Handoff (Historical)

- Conclusion: `reviewer_blocked`
- Blocking findings: one — general validation accepts incomplete frozen queue records and
  incomplete parallel secondary role/Git facts
- Next role: permanent Developer
- QA must not start. Developer should make the bounded schema/test correction above and return the
  same task for another full Reviewer re-gate.

## Final Full Re-Gate Conclusion And Handoff

- Conclusion: `reviewer_pass`
- Blocking findings: none
- Non-blocking findings: none
- Reviewed implementation HEAD: `cafdf89144ce3a03403c3d6758f430655533e4b5`
- Next role: permanent QA
- QA should use the immutable final Reviewer-evidence descendant produced by this gate and the
  exact clean lane; Integrator remains prohibited until QA passes.
