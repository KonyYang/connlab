# TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH QA Evidence

## Gate result

- Status: `qa_pass`
- Role: permanent QA / Smoke Owner
- Current phase: `Phase 11`
- Why allowed: the task retains the sole execution token, the implementation is on its isolated lane, and the mandatory Reviewer gate recorded `reviewer_pass` with no blocker.
- Validation object: clean reviewed chain only; no primary ambient files were used.
- Original base: `a1968c4999a33c6bee18c9185882ea3b927c2004`
- Reviewed implementation head: `cafdf89144ce3a03403c3d6758f430655533e4b5`
- Reviewer pass head / QA input HEAD: `216478f78cf29d4c344f74ae7ba123adc69a7479`
- Primary dispatch head: `f465b5f576229544f773095bb1086961152e6be8`
- Lane: `lane/task-governance-wip1-and-proportionate-quick-fix-fast-path`
- Worktree: `D:\PythonProject\connlab-worktrees\task-governance-wip1-and-proportionate-quick-fix-fast-path`

## Inputs and environment

QA read the repository `AGENTS.md`, current primary `docs/task_board.md` read-only, the task, plan, Developer evidence, Reviewer evidence, role registry, and applicable parallel-lane / QA rules before validation.

- OS: `Microsoft Windows NT 10.0.26200.0`
- Windows PowerShell: `5.1.26100.8875`
- Python: `3.13.3`
- Git: `2.51.0.windows.1`
- Initial branch/HEAD: exact expected branch and `216478f78cf29d4c344f74ae7ba123adc69a7479`
- Initial worktree/index: clean; no merge state
- Ancestry: `a1968c49..cafdf891..216478f7` verified with `git merge-base --is-ancestor`

## Fresh regression

All commands ran from the clean reviewed lane.

```text
py -m pytest tests\unit\test_connlab_execution_gate_script.py -q
31 passed in 22.51s

py -m pytest tests\integration\test_connlab_execution_gate_recovery.py -q
16 passed in 18.68s

py -m pytest tests\unit\test_execution_wip_and_quick_fix_governance.py -q
9 passed in 2.86s

py -m pytest tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
10 passed in 2.04s
```

Result: `66 passed` across the five required modules.

The Windows PowerShell parser accepted all three scripts with zero parser errors:

```text
AST_OK scripts\connlab_execution_gate.ps1
AST_OK scripts\run_task.ps1
AST_OK scripts\connlab_lane_worktree.ps1
```

## Independent disposable repository/worktree smoke

The fresh pytest runs above exercise real disposable Git repositories and worktrees under pytest-owned temporary roots. They independently passed the required state transitions and negative cases:

- idle normal start; second task queued; ownership retained through Reviewer, QA, and Integrator;
- dirty-lane preemption blocked and clean-checkpoint preemption allowed;
- overlapping or nested Quick Fix rejected;
- standalone and preempting Quick Fix lifecycle, cancellation, terminal failure, and owner invariants;
- accepted-on-master, non-rebase merge, reconciliation checkpoint, and `Resume`;
- reconciliation conflict/failure returns ownerless `paused_preempted` while both histories remain preserved;
- parallel execution rejected without approval; complete approved exception limited to two owners; secondary branch/HEAD/clean Git facts required;
- restart/cross-conversation state reload remains stable;
- complete FIFO queue record accepted, while missing/malformed/duplicate/type/order and incomplete-proof cases fail closed;
- a stale lane board cannot replace primary authority;
- a semantically neutral button-label change takes the dynamic QF-1 path;
- API/schema/authority changes are dynamically rejected from QF-4;
- the `run_task` queue path launches no Codex process;
- the worktree `Create` queue path creates no branch or worktree.

No test mutation escaped its disposable temporary root.

## Production-root fail-closed smoke

Because primary does not yet contain the merged structured marker JSON, lane-local production entry was required to resolve primary and fail closed. Only read-only `Inspect` / `Preview` operations were used; no real `Create` or `Retire` was run.

```text
scripts\connlab_execution_gate.ps1 -Intent Inspect ... -Json
exit 2; code=BLOCKED_MARKERS_MISSING; allowed=false; zero_write=true
authority_root=D:\PythonProject\connlab

scripts\run_task.ps1 -Task TASK_GOVERNANCE_WIP1_AND_PROPORTIONATE_QUICK_FIX_FAST_PATH -Preview
exit 2; code=BLOCKED_MARKERS_MISSING; allowed=false; zero_write=true
authority_root=D:\PythonProject\connlab

scripts\connlab_lane_worktree.ps1 -Action Inspect -Lane task-governance-wip1-and-proportionate-quick-fix-fast-path -Json -DryRun
branch/path/HEAD resolved to the reviewed lane; status entries=0
```

This is intentionally not an authorization claim: the lane candidate never treated its own marker copy as production authority, and `run_task -Preview` launched no Codex process.

## Scope, integrity, and protected-state checks

- `git diff --check a1968c4999a33c6bee18c9185882ea3b927c2004..216478f78cf29d4c344f74ae7ba123adc69a7479`: passed.
- `git show --check --format=fuller --stat` for the reviewed implementation head and Reviewer pass head: passed.
- Base through reviewed implementation contains exactly 17 implementation paths plus Developer and Reviewer role evidence (`19` total paths). The task-defined implementation package is exactly 18 paths when counted as the 17 implementation paths plus Developer evidence; Reviewer evidence is the separate role evidence.
- `cafdf891..216478f7` changes only the Reviewer evidence.
- No `backend/`, `frontend/`, product, Controlled Lane V2, active bundle, role registry, or `scripts/task_complete_commit.ps1` path changed.
- Line counts: gate `307`, run-task `123`, lane-worktree `305`, and bounded tests `496`, `489`, `340`, `219`, `49`; all are within the 500-line hard limit.
- Before/after snapshots covered every registered current, retained, frozen, and cancelled worktree. All 9 worktrees retained exact HEAD, branch, clean status, empty index, and no merge state throughout the read-only validation; the only subsequent mutation was this required QA evidence and its exact-path commit.
- Protected primary files were byte-stable by SHA-256 and length: `AGENTS.md`, `docs/task_board.md`, active bundle, role registry, `scripts/task_complete_commit.ps1`, and frozen `scripts/connlab_controlled_lane.ps1`.
- Primary board remained at SHA-256 `0C370086E2C592FB0B09612326B7FF6C5C74CA07F18540399EF304431760A82F` and length `773429`.

## Limitations and handoff

- QA changed only this evidence file.
- No merge, push, restart, reset, restore, clean, delete, real worktree lifecycle action, or product/retained-worktree mutation was performed.
- Remote status: not pushed by QA.
- Blocker: none.
- Next role: `Integrator`.
