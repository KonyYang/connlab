# TASK_GOVERNANCE_ACTIVE_CONTEXT_DETERMINISTIC_TRANSITION_AND_EVENT_HANDOFF — QA Evidence

Date: 2026-08-01

ROLE: QA

STATUS: qa_pass

NEXT: Integrator

## Authority And Immutable QA Input

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Why allowed: primary `docs/task_board.md` at
  `62874a215f540666564b51fe595580b083bf587d` records this task as the sole WIP=`1` token owner in
  `gate_running/QA`, with queue empty and paused/Quick Fix/parallel records null. Task B remains
  planned and non-executable.
- Exact worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-active-context-deterministic-transition-and-event-handoff`.
- Exact branch: `lane/task-governance-active-context-deterministic-transition-and-event-handoff`.
- Review base: `15c3120a6d889e97d098c2cb9f8c8ef852d74f69`.
- Immutable reviewed HEAD: `84503d16e2638a827ecd3ef6704d0fe6bfed72ca`.
- Reviewer evidence blob at that HEAD:
  `165ebfab7f198953539a371c7c56e114ccba6a91`; machine status is `reviewer_pass`.
- Base ancestry, final Developer evidence ancestry, branch/HEAD, empty index, and clean worktree were
  independently verified before validation. QA used only this clean reviewed lane and did not use
  ambient primary files as candidate code.
- Read before execution: lane `AGENTS.md`, current primary board, approved Task/Plan and normative
  contract, Developer/Reviewer evidence, role registry, execution/WIP policy, lane operations guide,
  task execution skill, and review checklist.

## Environment

- Windows `Microsoft Windows NT 10.0.26200.0`.
- PowerShell `5.1.26100.8875` with UTF-8 console/file reads.
- Python `3.13.3`; pytest `8.4.2`; Git `2.51.0.windows.1`.
- All mutations exercised by tests occurred only in pytest disposable temporary repositories and
  worktrees. No production board/history/archive/index apply was run.

## Fresh Complete Regression

The complete approved twelve-module Task A matrix was run from the immutable reviewed HEAD:

```text
py -m pytest tests\unit\test_connlab_execution_transition.py tests\integration\test_connlab_execution_transition_recovery.py tests\unit\test_connlab_active_context.py tests\integration\test_connlab_board_closeout_maintenance.py tests\unit\test_connlab_handoff_contract.py tests\unit\test_connlab_active_context_governance.py tests\unit\test_connlab_execution_gate_script.py tests\integration\test_connlab_execution_gate_recovery.py tests\unit\test_execution_wip_and_quick_fix_governance.py tests\unit\test_connlab_lane_worktree_script.py tests\unit\test_markdown_archive_tool.py tests\unit\test_task_scoped_role_thread_lifecycle_governance.py -q
```

Result: `133 passed in 227.13s`.

This matrix covers all four legal transition families and their fail-closed mismatches; transition
recovery; first, second, and third maintenance generations; safe byte-exact rollback; partial-write
recovery; corrupt/conflicting archive/index rejection; active-context inspection; callback/capsule/
read-set/cadence budgets; execution gate, WIP/Quick Fix, worktree, archive, and permanent-role
compatibility.

## Independent R1-R3 And Lifecycle Replays

R1-R3 were rerun as an explicit focused QA command, independently of the aggregate invocation:

```text
py -m pytest tests\integration\test_connlab_execution_transition_recovery.py::test_duplicate_rejects_later_primary_commit_and_dirty_lane tests\unit\test_connlab_active_context.py::test_gate_tuple_and_transition_id_must_be_exact_and_zero_write tests\unit\test_connlab_active_context.py::test_post_qa_unreviewed_helper_drift_is_zero_write tests\integration\test_connlab_board_closeout_maintenance.py::test_recomputed_generation_two_cannot_archive_authority_lines_before_generation_three -q
```

Result: `4 passed in 19.19s`.

- R1: later-primary replay and dirty-lane replay fail closed; source board bytes remain unchanged.
- R2: forged legal tuple/transition ID and post-QA helper drift fail closed with no board/archive/index
  write.
- R3: a recomputed canonical generation-2 archive that removes current authority is rejected before
  generation 3, preserving board/index/archive bytes.

The archive lifecycle and rollback round-trip received a separate focused run:

```text
py -m pytest tests\integration\test_connlab_board_closeout_maintenance.py::test_second_and_third_closeouts_append_contiguous_incremental_generations tests\integration\test_connlab_board_closeout_maintenance.py::test_second_and_third_generation_rollback_is_byte_exact_in_safe_temp_root -q
```

Result: `2 passed in 15.63s`. Generations 1/2/3 remain contiguous and each rollback reconstructs
the exact source bytes only inside a proven safe temporary root.

The complete handoff/cadence budget module was also rerun directly:

```text
py -m pytest tests\unit\test_connlab_handoff_contract.py -q
```

Result: `10 passed in 23.89s`. It covers the `4096`-byte capsule, `2048`-byte dispatch template,
minimal read set, strict ordered seven-field callback `<=1024` bytes, one-transition/one-dispatch
turn budget, first/changed heartbeat timing, unchanged-wait suppression, zero routine Planner
launches, and callback-to-dispatch `<=90s` pilot boundary.

## Compile, Parse, And Quantitative Gates

```text
py -m py_compile scripts\connlab_execution_transition.py scripts\connlab_active_context.py scripts\connlab_handoff_contract.py tests\unit\test_connlab_execution_transition.py tests\integration\test_connlab_execution_transition_recovery.py tests\unit\test_connlab_active_context.py tests\integration\test_connlab_board_closeout_maintenance.py tests\unit\test_connlab_handoff_contract.py tests\unit\test_connlab_active_context_governance.py
```

Result: `PY_COMPILE_OK_9`.

PowerShell AST parsing with `System.Management.Automation.Language.Parser` passed for
`scripts/run_task.ps1`, `scripts/connlab_execution_gate.ps1`, and
`scripts/connlab_lane_worktree.ps1`: `AST_PARSE_OK_3`.

Measured physical lines / UTF-8 file bytes:

| Artifact | Lines | Bytes | Gate |
| --- | ---: | ---: | --- |
| `scripts/connlab_execution_transition.py` | 478 | 29291 | `<500` pass |
| `scripts/connlab_active_context.py` | 497 | 33653 | `<500` pass; low residual margin retained |
| `scripts/connlab_handoff_contract.py` | 334 | 22884 | `<500` pass |
| transition unit test | 394 | 18227 | bounded pass |
| transition recovery test | 77 | 3197 | bounded pass |
| active-context unit test | 368 | 19513 | bounded pass |
| maintenance integration test | 209 | 12968 | bounded pass |
| Orchestrator skill | 120 | 6092 | contract budget pass |
| Planner skill | 103 | 4341 | contract budget pass |
| orchestration protocol | 123 | 6881 | contract budget pass |
| `run_task.ps1` | 115 | 3980 | contract budget pass |

The two largest helpers remain below the hard limit but have little expansion margin. This is the
same non-blocking maintenance risk recorded by Reviewer and does not change this gate.

## Production-Root Zero-Write Inspection

Candidate helpers were executed from the lane against the exact primary root, read-only. No current
localhost/runtime was used and no live board migration was attempted.

Before the reads:

- primary HEAD: `62874a215f540666564b51fe595580b083bf587d`;
- primary status/index: clean;
- board SHA-256: `89e83cc66bb61f0fb550ae8beb4bf3b49c8ac5eea70d28c35ab0e43525f8cd77`;
- `docs/archive/task_board_history`: absent.

Results:

- transition `inspect`: exit `2`, decision `BLOCKED`, reason
  `BLOCKED_TRANSITION_METADATA`, `zero_write=true`. This is the required fail-closed result for the
  legacy pre-integration primary record.
- active-context `inspect`: exit `0`, decision `ALLOW_INSPECT`, `zero_write=true`, metrics
  `2514` lines / `786494` bytes / `153` terminal records.
- `plan-maintenance`: exit `0`, decision `MAINTENANCE_REQUIRED`, `zero_write=true`, generation `1`,
  plan digest `43788ea205de17008dba95fa0367869430cc4ca959f0bf5958d2514f024029a7`, projected compact board
  `111` lines / `18509` bytes / `0` terminal records.

After the reads, primary HEAD/status, board SHA-256, and absent history directory were exactly equal
to the before state. The plan was not applied. Live migration remains Integrator-only after merge.

## Package, Ancestry, And Protected-State Equality

- `git diff --check 15c3120a..84503d16`: passed.
- `git show --check --format=oneline --stat 84503d16...`: passed.
- `15c3120a...` and final Developer evidence `1fd726b0...` are ancestors of the reviewed HEAD.
- Base..reviewed HEAD contains exactly `25` approved paths: the `23` implementation paths plus
  Developer and Reviewer evidence. Exact allowlist comparison passed with `0` missing and `0`
  extra paths.
- Forbidden scan found `0` backend/frontend/product, primary board/history, registry/bundle,
  execution-gate/worktree/task-complete, V2, Task B, package/lock, release, or real-data paths.
- Before tests, all `12` registered worktrees were clean. After all validation and before QA
  evidence, the full primary/lane/worktree/protected-file manifest SHA-256 remained exactly
  `605779bb1172f5eab4481081dfddb1397761b121121cb5b5bc63e72f0ac59612`.
- The protected-only manifest excluding the intentionally advancing QA lane is
  `8e805dc9a758f823d0044bce2b1d94147a40857f6ec2aece36bc95b40a69d6e9` across primary plus the
  other `11` worktrees. It covers exact HEAD/branch/status/index, primary AGENTS/board,
  role registry/bundle, Task B task/plan/Planner evidence, and history listing.

No product/task/plan/board/Developer/Reviewer/Task B/protected-lane file was edited. No production
transition or maintenance apply, archive/index creation, real Create/Retire, merge, push, release,
restart, reset, restore, clean, rebase, stash, discard, or destructive action occurred. Remote
`origin` is configured, but QA did not push.

## QA Conclusion

`qa_pass`.

The immutable reviewed Task A candidate passes the complete regression, explicit R1-R3 safety,
transition/maintenance/recovery, generation and rollback, handoff budget, compilation, PowerShell
parse, quantitative, exact-package, ancestry, protected-state, and production zero-write gates.
Handoff is to Integrator. QA does not merge or perform the first live board migration.
