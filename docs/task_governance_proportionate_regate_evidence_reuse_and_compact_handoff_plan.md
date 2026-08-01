# Proportionate Re-gate Evidence Reuse And Compact Handoff Implementation Plan

> **For ConnLab permanent roles:** implementation is forbidden until explicit User approval. After
> approval, permanent Developer executes this plan in the recorded isolated lane; independent
> Reviewer, mandatory QA, and Integrator gates remain required. No subagent or current-thread
> implementation dispatch is authorized by this document.

Status: `planned_pending_user_approval`

**Goal:** Add fail-closed Reviewer evidence reuse, final-full QA, deterministic role-local sharding,
compact reference-only handoffs, and lossless active-board/history separation.

**Architecture:** A versioned immutable Reviewer manifest is evaluated by a zero-write decision
helper. Separate zero-write handoff and board-context helpers enforce reference/cadence/read rules;
only the board helper has one explicitly guarded Integrator apply operation. Execution JSON stays
the machine authority, and the human active summary is derived and verified.

**Tech stack:** Python 3.11+, PowerShell 5.1-compatible entry scripts, Git committed blobs/SHA-256,
JSON schemas expressed as validated Python structures, Markdown governance, pytest.

## Global Constraints

- Planning status remains `planned_pending_user_approval` until explicit User approval.
- WIP=`1`; no parallel exception; no token/queue/worktree before approval.
- Reviewer reuse is opt-in and fail-closed; no override converts `FULL_REGATE` to reuse.
- QA runs one complete risk-proportionate validation at final reviewed HEAD.
- No product/API/business schema/persistence/Office/data change.
- No retained/frozen/cancelled lane mutation, V2 activation, push, restart, or destructive cleanup.
- Developer never edits the live primary board or production task-board archive.

---

## 1. Discovery Gate

### Confirmed by User

- Reviewer may reuse exact unchanged prior passing evidence after a blocker fix.
- Reuse binds commits, paths/dependencies, command identity, environment/fixture hashes, prior
  result, and evidence hash.
- Drift, unknowns, or authority/API/schema/shared ownership force full re-gate.
- QA remains independent and final-full.
- Role-local sharding must not alter WIP ownership.
- Board/history, handoffs, reads, commentary, and callbacks must become compact and testable.
- Silence window is 60 seconds; unchanged waits are suppressed.

### Confirmed by Repository

- Primary is clean `master@4e7ce7ffa040039e8c7ebb659efe8cba5e00eeff` and production
  `Inspect=ALLOW_INSPECT`; execution state is `complete`, token/active/queue/paused/Quick Fix/
  parallel records are empty.
- TASK_368E is locally accepted and no remote contains its accepted chain.
- The board is 2465 physical lines / 779616 bytes. Its execution JSON is near the top, while long
  completed history and stale sections titled `Current Mainline`, `Current Validation Snapshot`,
  and `Next Recommended Action` remain in the same active file.
- Existing execution gate enforces token/Git/worktree state but has no Reviewer evidence-reuse
  decision contract.
- Existing completed-Markdown archive helper archives task/plan files, not board history.
- Orchestration already uses immutable lane commits and seven-field callbacks, but `run_task.ps1`
  copies a long instruction body and full worktree list into every prompt.
- Existing tests cover WIP, queue, recovery, worktree, Quick Fix, archive, and permanent roles, but
  not reusable-evidence manifests, final-QA non-substitution, capsule budgets, cadence, minimal
  read fallback, or board round-trip compaction.

### Planner Inference

- A dedicated opt-in manifest is safer than extending execution-control JSON: evidence reuse is a
  gate decision, not execution ownership state.
- Direct dependencies must be declared rather than guessed from imports.
- Board migration must be Integrator-owned on primary after the helper package passes Reviewer/QA;
  otherwise Developer lane board edits would conflict with live gate transitions.
- Three focused helpers keep responsibilities bounded and avoid growing the 307-line execution
  gate or 321-line task/plan archive helper.

### Not Yet Confirmed

- User approval and the resulting approval/worktree base commit.
- Runtime validation totals and final compact-board hashes.
- Developer/Reviewer/QA/Integrator evidence commits.

These are execution outputs, not scope ambiguities. No blocking planning question remains.

### Continue Or Stop

Stop for User review after this planning commit. Continue only after explicit approval and a fresh
execution gate.

## 2. Alternatives Considered

### A. Extend execution-control JSON with reuse details

Rejected. It mixes task execution ownership with command-level review evidence, grows every board
transition, and makes historical command results look like execution authority.

### B. Versioned per-task Reviewer manifest plus focused helpers (selected)

Selected. It is opt-in, committed, hash-bound, independently testable, and can fail closed without
changing token state. Separate board and handoff helpers keep each interface small.

### C. Parse prose evidence or conversation history heuristically

Rejected. Prose is not a stable machine contract, chat can compact/truncate, and omissions cannot
be proven safe.

## 3. File And Ownership Map

### Developer lane

- Modify `AGENTS.md`: add the validated compact-read/cadence/re-gate exception while preserving all
  token, worktree, and role gates.
- Create `docs/project_management/PROPORTIONATE_REGATE_AND_COMPACT_HANDOFF_CONTRACT.md`: one
  normative schema, decision, board, capsule, cadence, and migration contract.
- Modify the eight listed active governance protocols/checklists and two permanent-role skills so
  they reference, rather than duplicate, the normative contract.
- Modify `scripts/run_task.ps1`: emit a compact reference capsule and omit copied contracts/full
  worktree listings.
- Create `scripts/connlab_regate_evidence.py`: manifest and shard-result validator.
- Create `scripts/connlab_handoff_contract.py`: capsule/read/callback/cadence validator.
- Create `scripts/connlab_board_context.py`: active summary and guarded board-history utility.
- Create five bounded test modules and make one small callback assertion update.
- Create/update only task-prefixed Developer evidence. Do not edit live board/archive paths.

### Primary Planner/Integrator only

- `docs/task_board.md`: planned/approval/gate/compaction/closeout governance.
- `docs/archive/task_board_history/TASK_GOVERNANCE_PROPORTIONATE_REGATE_EVIDENCE_REUSE_AND_COMPACT_HANDOFF_pre_compaction.md`:
  exact byte snapshot, generated only at Integrator migration.
- `docs/archive/task_board_history/index.json`: deterministic migration metadata.
- task/plan/Planner/Integrator evidence and execution transitions.

## 4. Exact Interfaces

### 4.1 Re-gate manifest

Canonical JSON object:

```json
{
  "schema": "connlab.reviewer-regate-evidence",
  "version": 1,
  "task_id": "TASK_XXX",
  "lane": "task-xxx",
  "baseline_sha": "<40-hex>",
  "prior_reviewed_sha": "<40-hex>",
  "blocker_evidence_sha": "<40-hex>",
  "fix_sha": "<40-hex>",
  "final_candidate_sha": "<40-hex>",
  "changed_paths": ["path"],
  "approved_fix_paths": ["path"],
  "direct_dependencies": [{"path": "path", "sha256": "<64-hex>"}],
  "impact": {
    "authority": false,
    "api": false,
    "schema": false,
    "persistence": false,
    "migration": false,
    "shared_ownership": false,
    "unknown_failure": false
  },
  "commands": [{
    "id": "stable-id",
    "argv": ["py", "-m", "pytest", "tests/unit/test_x.py", "-q"],
    "cwd": ".",
    "covered_paths": ["path"],
    "dependency_paths": ["path"],
    "command_identity_sha256": "<64-hex>",
    "environment_sha256": "<64-hex>",
    "fixture_sha256": "<64-hex>",
    "input_sha": "<40-hex>",
    "prior_result": "pass",
    "result_sha256": "<64-hex>",
    "evidence_path": "docs/lane_evidence/file.md",
    "evidence_commit": "<40-hex>",
    "evidence_blob_sha256": "<64-hex>"
  }],
  "shards": []
}
```

Relevant environment digest is canonical JSON of declared OS, Python/Node/PowerShell/Git versions
and dependency-lock hashes. It never records secrets or arbitrary ambient environment variables.

CLI:

```text
py scripts/connlab_regate_evidence.py decide --repo-root <root> --manifest <file> --json
py scripts/connlab_regate_evidence.py aggregate-shards --manifest <file> --results <dir> --json
```

Output keys: `decision`, `reasons`, `reusable_command_ids`, `required_command_ids`,
`manifest_digest`, `zero_write`. Reason arrays and IDs are sorted.

### 4.2 Handoff contract

CLI:

```text
py scripts/connlab_handoff_contract.py validate-capsule --capsule <file> --repo-root <root> --json
py scripts/connlab_handoff_contract.py resolve-read-set --capsule <file> --repo-root <root> --json
py scripts/connlab_handoff_contract.py validate-callback --input <file> --json
py scripts/connlab_handoff_contract.py validate-cadence --events <file> --json
```

Stable decisions: `CAPSULE_VALID`, `FULL_READ_REQUIRED`, `CALLBACK_VALID`, `CADENCE_VALID`, and
`BLOCKED_*`. Capsule maximum is 4096 UTF-8 bytes. Callback accepts exactly seven ordered lines.
Cadence accepts only start/end/blocker/direction-change or a progress event after at least 60
seconds; repeated wait digests are suppressed.

### 4.3 Board context and history

CLI:

```text
py scripts/connlab_board_context.py inspect --repo-root <root> --json
py scripts/connlab_board_context.py render-summary --repo-root <root>
py scripts/connlab_board_context.py plan-compaction --repo-root <root> --expected-head <sha> --json
py scripts/connlab_board_context.py apply-compaction --repo-root <root> --task-id <TASK_ID> --expected-head <sha> --expected-board-sha256 <hash>
py scripts/connlab_board_context.py prove-rollback --repo-root <root> --index <file> --output <temp-file> --json
```

`inspect`, `render-summary`, `plan-compaction`, and `prove-rollback` do not modify the repository.
`apply-compaction` writes only the live board, exact archive snapshot, and index after primary,
HEAD/hash, clean-state, task/role/token, queue, and null-record guards pass.

Generated summary markers:

```text
<!-- CONNLAB_ACTIVE_SUMMARY_BEGIN -->
<!-- CONNLAB_ACTIVE_SUMMARY_END -->
```

The summary is a pure function of execution JSON plus a short non-executable planned-task pointer.
Any disagreement returns `FULL_READ_REQUIRED` / `BLOCKED_BOARD_SUMMARY_DRIFT`.

## 5. Fail-Closed Decision Rules

Reuse validation order is fixed:

1. parse schema/version and full SHA/hash shapes;
2. verify repository commits/blobs exist;
3. verify `baseline -> prior reviewed -> blocker/fix -> final candidate` ancestry;
4. compare actual Git changed paths with manifest paths and approved fix scope;
5. compare declared direct dependency content at prior/final commits;
6. compare command/environment/fixture identity;
7. verify prior pass/result/evidence committed blob;
8. reject every true/unknown escalation impact;
9. aggregate shard results deterministically;
10. emit reuse only if all checks are proven.

There is no force/ignore/assume flag.

## 6. Board Migration And Rollback

1. Developer tests compaction only in disposable repositories.
2. Reviewer verifies the helper cannot mutate production without exact guards.
3. QA runs round-trip, corruption, stale-HEAD, active-owner, and byte/hash cases in disposable
   repositories.
4. Integrator merges the reviewed lane package without a Developer board copy.
5. Integrator records current primary HEAD and board Git-blob/SHA-256, then runs zero-write
   `plan-compaction`.
6. Integrator runs `apply-compaction` for this exact task while it is the sole `gate_running /
   Integrator` owner, queue empty, paused/Quick Fix/parallel null, and primary clean.
7. The helper writes the exact full pre-compaction board bytes to the locked archive path, writes
   the deterministic index, and replaces the live board with the compact authority view.
8. Integrator runs `prove-rollback` to a temporary path and requires the reconstructed SHA-256 to
   equal the pre-compaction source SHA-256.
9. Integrator runs `inspect`, production execution gate, merged-tree governance tests, and size/
   marker/stale-heading scans.
10. Integrator updates terminal execution JSON and regenerates the summary through the helper,
    then commits closeout. The archive remains immutable history.

Rollback is local Git revert or a separately approved exact patch from the verified archive. The
helper provides proof/output only and never overwrites the live board as a rollback shortcut.

## 7. File-Level Implementation Tasks

### Task 1: Freeze the normative contract

**Files:** create the contract doc; modify AGENTS and the listed policies/checklists/skills; create
`tests/unit/test_connlab_proportionate_regate_governance.py`.

**Interfaces:** produces the exact schemas, decisions, size/cadence budgets, role boundaries, and
full-read/full-regate rules consumed by every later task.

- [ ] Write static tests asserting one normative contract reference, Reviewer-only reuse, final-full
  QA, WIP=`1`, exact seven fields, 60 seconds, 4096-byte capsule, 400-line/65536-byte board budgets,
  and unchanged V2/role registry boundaries.
- [ ] Run `py -m pytest tests/unit/test_connlab_proportionate_regate_governance.py -q`; require RED
  because the contract/references do not exist.
- [ ] Add the contract and narrow references; do not duplicate full schema prose across skills.
- [ ] Rerun the focused test; require PASS.
- [ ] Run existing `test_execution_wip_and_quick_fix_governance.py` and
  `test_task_scoped_role_thread_lifecycle_governance.py`; require PASS.

Stop on any role/token/Quick Fix/V2 semantic change.

### Task 2: Implement Reviewer evidence decision and shard aggregation

**Files:** create `scripts/connlab_regate_evidence.py`, unit test, and recovery integration test.

**Interfaces:** consumes the v1 manifest; produces stable JSON decision/reason output and no writes.

- [ ] Add RED unit cases for exact reuse, every drift/impact trigger, unknown failure, evidence hash,
  command/environment/fixture identity, sorted reasons, and zero-write behavior.
- [ ] Add RED disposable-Git integration cases for continuous ancestry, broken ancestry, changed
  dependency blob, stale evidence commit, and final candidate mismatch.
- [ ] Run both new modules; require RED due missing helper.
- [ ] Implement typed immutable records, canonical JSON hashing, Git committed-blob reads, ancestry/
  path checks, stable reasons, and exit `0/2` behavior.
- [ ] Add shard aggregation: unique IDs, same immutable input SHA, sorted output, missing/duplicate/
  nonzero/stale result failure.
- [ ] Rerun both modules and `py -m py_compile scripts/connlab_regate_evidence.py`; require PASS.

Stop if safe validation would require heuristic imports, shell evaluation, secrets, or repository
mutation.

### Task 3: Implement compact handoff/read/callback/cadence validation

**Files:** create `scripts/connlab_handoff_contract.py` and its unit test; modify `scripts/run_task.ps1`
and the small permanent-role callback test.

**Interfaces:** consumes capsule/callback/cadence JSON or text; produces stable zero-write decisions.

- [ ] Add RED tests for valid reference-only capsule, >4096 bytes, copied contract bodies, missing/
  mismatched refs, escalation flags, full-read fallback, exact seven fields/order, extra prose,
  60-second cadence, direction/blocker exceptions, and unchanged wait suppression.
- [ ] Add RED `run_task.ps1 -Preview` fixture asserting the prompt contains refs/digests but no full
  worktree list or copied task/plan/evidence body and stays within 4096 bytes.
- [ ] Implement canonical refs, Git blob/SHA-256 checks, minimal/full read decisions, callback parser,
  and cadence state-digest rules.
- [ ] Replace the long `run_task.ps1` prompt with the compact capsule. Preserve `StartTask`, queue
  zero-write behavior, primary-root resolution, Preview, and no-direct-implementation semantics.
- [ ] Run the new handoff test, callback test, existing run-task governance tests, and PowerShell
  parser check; require PASS.

Stop if compacting removes a gate, scope, stop condition, worktree identity, or full-read fallback.

### Task 4: Implement active board context and guarded history migration

**Files:** create `scripts/connlab_board_context.py` and unit test. Production archive/board paths
remain untouched in Developer lane.

**Interfaces:** parses exactly one execution block; renders deterministic summary; plans/applies
guarded compaction; proves byte-exact rollback.

- [ ] Add RED disposable-repository tests for marker uniqueness, JSON/summary agreement, planned
  pointer, stale historical headings, line/byte budgets, clean/dirty primary, wrong HEAD/hash,
  wrong role/token/task, nonempty queue, paused/QF/parallel records, archive/index hashes, and exact
  rollback bytes.
- [ ] Run `py -m pytest tests/unit/test_connlab_board_context.py -q`; require RED.
- [ ] Implement zero-write inspect/render/plan/prove paths and exact three-path apply.
- [ ] Require no overwrite of an existing different archive/index, no symlink/path escape, no
  partial write, and atomic same-directory replacement for each generated file.
- [ ] Rerun tests and `py -m py_compile scripts/connlab_board_context.py`; require PASS.
- [ ] Run `plan-compaction` only against production and record output in Developer evidence; do not
  run production apply.

Stop on any production write, unexplained historical loss, or mismatch between archived and source
bytes.

### Task 5: Developer package validation and handoff

**Files:** all Developer-owned May Touch paths plus Developer evidence only.

- [ ] Run all five new bounded modules.
- [ ] Run existing execution-gate script, recovery, lane-worktree, WIP/Quick Fix, permanent-role,
  and Markdown archive tests read-only.
- [ ] Run Python compilation for the three helpers and PowerShell parse for `run_task.ps1`.
- [ ] Run production zero-write helper inspect/plan commands, execution `Inspect`, `git diff --check`,
  exact allowlist, forbidden-path, V2/registry/bundle hash, and no-product-path scans.
- [ ] Confirm no live board/archive product migration occurred in the lane.
- [ ] Exact-path stage only Developer-owned paths, commit locally, leave lane/index clean, record
  base/HEAD/path/results in Developer evidence, and stop `ready_for_review`.

### Task 6: Reviewer gate

- [ ] Review exact base..Developer HEAD and all helper security/fail-closed boundaries.
- [ ] Independently reproduce one valid reuse and each escalation family.
- [ ] Verify no command shell execution, path escape, secret capture, board partial write, or override
  flag exists.
- [ ] Verify reference-only prompts retain every authority/gate/stop fact.
- [ ] Verify board migration is primary Integrator-only and old archive helper is unchanged.
- [ ] Write Reviewer evidence and stop on blocking findings; no code fix or merge.

Because this task defines future evidence reuse, Reviewer must perform a full review; it cannot use
the feature under review to reduce its own gate.

### Task 7: Mandatory QA gate

- [ ] Validate final Reviewer-pass HEAD from a clean lane/temp worktree/exact archive.
- [ ] Run the complete new test suite plus all existing governance regression modules.
- [ ] Run disposable Git/board migration round-trip, corruption, stale state, and deterministic shard
  tests on Windows PowerShell/Python.
- [ ] Prove Reviewer reuse cannot satisfy or suppress QA's final complete matrix.
- [ ] Prove token/board/worktree state and frozen V2/registry/bundle remain unchanged.
- [ ] Record environment/commands/results in QA evidence and stop `qa_pass` or `qa_fail`.

### Task 8: Integrator merge, board migration, and closeout

- [ ] Verify Developer/Reviewer/QA ancestry, exact package, clean primary/lane, and no blocker.
- [ ] Merge locally only within approved authority.
- [ ] Run zero-write board compaction plan, verify expected HEAD/source blob/SHA-256, then run the
  one guarded `apply-compaction` operation.
- [ ] Prove archive SHA/index/rollback and compact-board JSON/summary/size/stale-heading contracts.
- [ ] Run merged-tree new/existing governance suites, Python/PowerShell checks, execution `Inspect`,
  and exact protected-state checks.
- [ ] Update board/task/plan/evidence to terminal accepted state, regenerate human summary from JSON,
  record residual ledger and remote-not-pushed state, and commit locally.
- [ ] Retire only a clean integrated worktree through the non-force helper if separately safe under
  normal closeout; otherwise retain with named owner. Never push or destructively clean.

## 8. Validation Matrix

1. exact fully bound unchanged evidence -> `REUSE_ALLOWED`;
2. absent/malformed/unsupported manifest -> `FULL_REGATE`;
3. baseline/candidate/ancestry mismatch -> `FULL_REGATE`;
4. changed path outside approved fix set -> `FULL_REGATE`;
5. missing/changed/ambiguous direct dependency -> `FULL_REGATE`;
6. command argv/cwd/selection identity drift -> `FULL_REGATE`;
7. OS/runtime/lockfile environment drift -> `FULL_REGATE`;
8. fixture/input hash drift -> `FULL_REGATE`;
9. prior non-pass/result/evidence hash mismatch -> `FULL_REGATE`;
10. unknown failure -> `FULL_REGATE`;
11. authority/API/schema/persistence/migration/shared ownership true or unknown -> `FULL_REGATE`;
12. shard results sort deterministically on one immutable HEAD;
13. missing/duplicate/failed/stale shard fails closed;
14. sharding leaves execution token/owner/worktree count unchanged;
15. QA requires final reviewed HEAD and complete frozen matrix despite Reviewer reuse;
16. valid capsule is reference-only and <=4096 bytes;
17. missing/hash-mismatched ref -> `FULL_READ_REQUIRED`;
18. callback accepts exactly seven ordered fields and rejects any shape drift;
19. commentary cadence permits start/end/blocker/direction/>=60s and suppresses unchanged waits;
20. run-task Preview is compact and retains gate/stop/identity refs;
21. active summary equals execution JSON; mismatch fails closed;
22. board full snapshot/archive/index hashes and byte-exact rollback pass;
23. compact board <=400 lines/65536 bytes with one execution block and no stale historical Current
    sections;
24. wrong task/role/token/HEAD/hash/dirty/nonempty queue/paused/QF/parallel blocks apply;
25. existing execution gate/recovery/WIP/Quick Fix/worktree/permanent-role/archive suites pass;
26. V2, registry, bundle, product paths, retained lanes, remote state, and real data remain unchanged.

## 9. Exact May Touch / Must Not Touch / Locked Paths

The task file's enumerated lists and phase ownership are normative and incorporated here verbatim by
reference. Any additional path, board write by Developer, execution-gate modification, V2/registry/
bundle change, product path, or retained-lane operation is a scope blocker requiring Planner/User.

## 10. Compatibility And Rollback

- Existing tasks without a manifest always receive full Reviewer re-gate; behavior is backward
  compatible and fail-closed.
- Existing callback consumers continue the same seven fields, now validated strictly.
- Existing execution JSON schema/version and gate helper remain unchanged.
- Existing completed-Markdown archive remains unchanged.
- If compact reads fail, roles perform the current full reads.
- If board migration fails before replacement, no live file changes. If post-merge acceptance finds
  a defect, local Git revert restores code/policy; the immutable archive and rollback proof preserve
  the old board bytes. No automatic destructive restore exists.

## 11. Risk Register

- False reuse misses a regression: mitigated by opt-in manifests and mandatory full-regate reasons.
- Stale/spoofed evidence: mitigated by Git committed blobs, SHA-256, ancestry, and prior-result checks.
- Dependency omission: mitigated by declarative exact dependencies and full-regate on unknowns.
- Board split creates two authorities: mitigated by execution JSON as machine authority, generated
  human summary, and archive explicitly non-authoritative.
- Prompt compaction drops a gate: mitigated by required capsule fields, refs/digests, and full-read
  fallback.
- Parallel shards hide failure: mitigated by one input SHA and deterministic fail-closed aggregate.
- Board migration conflicts with live transitions: mitigated by sole Integrator ownership and exact
  HEAD/hash/clean-state guards.

## 12. Planned Lane And Gate State

- Lane: `task-governance-proportionate-regate-evidence-reuse-and-compact-handoff`
- Branch: `lane/task-governance-proportionate-regate-evidence-reuse-and-compact-handoff`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-governance-proportionate-regate-evidence-reuse-and-compact-handoff`
- Planning base: `4e7ce7ffa040039e8c7ebb659efe8cba5e00eeff`
- Worktree creation base: future exact approval-governance HEAD, recorded before Create.
- WIP=`1`; no parallel exception.
- Required route: User approval -> Developer -> Reviewer -> QA -> Integrator.

No branch/worktree/token/queue/dispatch is authorized by this plan.

## 13. Self-Review

- Spec coverage: all binding Discovery requirements map to interfaces, tasks, and validation rows.
- Placeholder scan: no `TBD`, `TODO`, or unspecified implementation action remains.
- Type/field consistency: manifest, capsule, callback, decision, reason, and board fields use one
  spelling throughout.
- Scope check: one governance task with three cohesive helpers and one guarded migration; no product
  subsystem or independent feature is included.

## 14. Stop Point

Return the committed planning package to User. Do not execute Task 1, activate a lane, or offer an
implementation mode before explicit approval.
