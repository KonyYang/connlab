# Re-gate Evidence Reuse, Baseline Ledger, And Validation Runner Implementation Plan

Status: `planned_pending_user_approval`

Task: `TASK_GOVERNANCE_REGATE_EVIDENCE_REUSE_BASELINE_LEDGER_AND_VALIDATION_RUNNER`

Hard dependency: Task A local Integrator acceptance and separate User approval of B.

Planning base: `cdb96b4ed80143ba40d571615282f0ee95708a0f`

## 1. Outcome And Architecture

Implement an opt-in v1 validation manifest with three bounded components:

- evidence decision helper computes per-command reuse/rerun and Integrator differential/full
  validation from Git-bound facts;
- validation runner validates/executes argv commands and safely aggregates role-local shards;
- baseline-debt helper verifies committed known-failure records from Git blobs instead of full base
  archives.

All decisions default to full validation. QA remains a separate full final safety net. Task A's
accepted transition/context/handoff authority is a locked prerequisite, not B implementation scope.

## 2. Discovery Gate

### Confirmed by User

- Reuse is per command, not one task-wide impact flag.
- Bounded authority/API/persistence fixes rerun affected dependencies while independent unchanged
  frontend commands remain reusable.
- Schema/migration/public-breaking/shared-ownership/unprovable closure and every unknown force full
  re-gate.
- A deterministic Windows runner, read-only frontend runtime, isolated shards, baseline ledger,
  final-full QA, Integrator differential decision, exact TASK_368E replay, >=40% Reviewer command
  reduction, and a real measured medium pilot are mandatory.

### Confirmed by repository

- TASK_368E has an immutable base/Developer/blocker/fix/reviewer/QA/merge chain.
- Its bounded fix changed authority + two backend test modules + Developer evidence; frontend
  product/tests did not change.
- Reviewer reran frontend `8 files / 61 tests` and build; QA later reran the same complete frontend
  checks.
- QA documented a real Windows backslash `--deselect` mismatch and replaced a timed-out full base
  archive with exact unchanged Git-blob proof.
- A lane without `node_modules` used a disposable frontend archive linked to an existing dependency
  tree; no install/lock change was needed, but no reusable executable contract exists.
- Current repository has no command-evidence manifest, deterministic runner, committed debt
  ledger, or Integrator differential decision helper.

### Planner inference

- Seven frozen command groups give a faithful TASK_368E re-gate baseline: four affected backend/
  compile groups plus unchanged disposable XLSX/catalog/external-read compatibility, frontend
  tests, and build; reusing the last three produces `42.9%` fewer Reviewer command executions.
- Impact domains annotate commands; dependency closure and public compatibility determine whether
  a task-wide full re-gate is necessary.
- The pilot can be real and governance-only by replaying TASK_368E's actual Git history and running
  its frozen commands in disposable workspaces; no product edit or new product task is needed.

### Not yet confirmed

- A acceptance commit, B approval/worktree base, implementation/test commits, runtime hashes, and
  measured pilot duration/retries.

These are required later gate outputs. They do not change B's scope, but A acceptance and separate
User approval are hard blockers to implementation.

## 3. Frozen Schemas

### 3.1 Validation manifest

Schema `connlab.validation-manifest`, version 1. Root binds task/lane, baseline/prior review/blocker/
fix/final commits, exact changed/approved paths, dependency-closure digest, public-contract
compatibility, shared-owner proof, environment profile, QA frozen matrix, and commands.

Each command records:

```json
{
  "id": "stable-id",
  "argv": ["py", "-m", "pytest", "tests/unit/test_x.py", "-q"],
  "cwd": ".",
  "covered_paths": ["path"],
  "direct_dependencies": [{"path": "path", "blob": "<git-blob>", "sha256": "<hash>"}],
  "impact_domains": ["authority"],
  "input_sha": "<40-hex>",
  "environment_sha256": "<hash>",
  "fixture_sha256": "<hash>",
  "lock_sha256": "<hash>",
  "prior_result": "pass",
  "prior_result_sha256": "<hash>",
  "evidence_ref": "path@commit#sha256",
  "shard": "backend-1"
}
```

No path/dependency is inferred from imports. Missing declaration or closure uncertainty is global
`FULL_REGATE`.

### 3.2 Result

Result schema binds manifest/command/shard, exact argv/cwd/input, start/end UTC, monotonic duration,
exit, stdout/stderr digests, environment/fixture/lock digests, artifact directory digest, and final
canonical result hash. Aggregate sorts by command then shard and rejects missing/duplicate/stale/
failed inputs.

### 3.3 Baseline debt

Ledger is sorted, versioned, and committed. Stable signature is normalized exception/test outcome,
never an arbitrary substring waiver. `expiry` is an exact date, commit condition, or blob-change
condition. One owner is mandatory. `resolved/superseded` entries cannot suppress failures.

## 4. File-Level Implementation Sequence

### Step B0 — Dependency and activation gate

- Verify A local Integrator acceptance, production `Inspect`, clean primary, no owner/queue, and
  exact A contract/helper hashes.
- Obtain separate User approval of this exact B package.
- Only then record B as sole owner, create its planned branch/worktree from the approval HEAD, and
  dispatch Developer through A's accepted transition/handoff authority.

Stop if A is missing/drifted, B approval is absent, or another owner/lock exists.

### Step B1 — Normative reuse/runner/ledger contract

Files: new B contract, baseline ledger seed, bounded policy/checklist/skill references, static test.

1. Add RED checks for opt-in versioning, per-command decisions, global escalation families,
   final-full QA, no override, runner safety, debt expiry, differential Integrator, quantitative
   pilot, and unchanged A/WIP/V2/product boundaries.
2. Write one normative contract and reference it; do not duplicate full schema in prompts.
3. Seed ledger only with independently evidenced TASK_368E baseline debts and exact Git hashes;
   do not invent or silently waive any failure.
4. Run static and existing governance regression tests.

Stop on any task-global authority/API invalidation, QA substitution, or unowned debt.

### Step B2 — Per-command evidence decision

Files: decision helper and unit/disposable-Git tests.

1. Add RED cases for exact reuse, required rerun, every global full-regate reason, ancestry/path/
   dependency/evidence/hash drift, public compatibility, shared owner, and unknown failure.
2. Verify committed refs/blobs and actual Git diffs; compare each command's covered/dependency set.
3. Treat bounded non-breaking authority/API/persistence change per command. Treat schema/migration,
   incompatible public contract, owner drift, or unproven closure globally.
4. Emit sorted stable decisions/reasons with zero writes and no unsafe switches.
5. Add Integrator decision with exact QA/merge/package/master-drift/environment bindings.

Stop if reuse needs heuristic imports, conversation evidence, partial SHA, or override.

### Step B3 — Deterministic validation runner

Files: runner plus unit/Windows integration tests.

1. Add RED manifest/argv/path/canonical-node/runtime/shard/result cases.
2. Normalize pytest node paths to POSIX form and validate requested/deselected nodes from
   collection before execution; unknown nodes block before the test command.
3. Validate an existing read-only frontend dependency runtime from lock + Node/npm + executable
   hashes. No install, junction mutation of repository paths, or lock/node_modules write.
4. Allocate unique external temp/cache/coverage/frontend cache/dist roots per shard. Reject shared
   output path, repository output, symlink escape, mismatched HEAD, or second owner/worktree.
5. Launch only argv arrays with `shell=False`; record full deterministic result metadata/digests.
6. Allow backend/frontend concurrency within one role and immutable HEAD; aggregate lexically and
   fail closed on missing/duplicate/stale/nonzero/unknown.

Stop if a command requires shell eval, repository dependency mutation, ambiguous node selection,
or shared shard output.

### Step B4 — Baseline-debt ledger helper

Files: helper, ledger, tests.

1. Add RED cases for valid unchanged debt, wrong test ID/signature/blob/evidence/owner/status,
   expiry, unknown failure, and related-source drift.
2. Verify baseline commit and source/test/fixture blobs directly through Git; do not extract a full
   base archive when unchanged.
3. Return `KNOWN_UNCHANGED_DEBT` only for exact active entry; otherwise
   `BASELINE_RECOMPARISON_REQUIRED` and nonzero.
4. Prove helper is zero-write and ledger updates require normal reviewed commits.

Stop if a signature can match unrelated failures or expired/resolved debt can suppress a run.

### Step B5 — Exact TASK_368E replay and medium pilot fixture

Files: four exact fixture JSON files and replay integration test.

1. Bind all eight known commits/evidence blobs, actual fix paths, command identities, dependency/
   runtime/fixture/lock hashes, and QA frozen matrix.
2. Prove Reviewer required the four backend B1/authority/API/compile groups and reused the three
   unchanged XLSX/catalog/external-read, frontend-tests, and frontend-build groups; expected
   executed count `4/7`.
3. Prove QA mode ignores Reviewer reuse and executes all seven frozen groups, including real
   frontend 61 tests/build at final reviewed HEAD.
4. Exercise the runner on real frozen commands in disposable workspaces using the verified
   read-only frontend runtime; record duration, retries, digests, and no-install proof.
5. Prove unchanged baseline debt uses ledger/Git blobs, not a full base archive.

Stop if any replay hash is unavailable/mismatched, actual command identity cannot be bound, or the
measured reduction is below 40%.

### Step B6 — Developer handoff

- Run all new B tests, A regression suites, execution/WIP/role tests, Python compile, exact allowlist,
  diff/check, forbidden product/V2/registry/bundle/retained-lane scans, and zero-write production
  decisions.
- Record command counts, Planner transitions, context bytes, wall-clock, retries, runner outputs,
  runtime hashes, and repository cleanliness.
- Exact-stage B lane paths, commit locally, leave lane/index clean, write Developer evidence, stop.

### Step B7 — Reviewer gate

- Full review of B; evidence reuse is not used to reduce the feature's own first review.
- Independently reproduce command-local decisions, escalation families, no-shell runner, Windows
  node selection, runtime verification, shard isolation, ledger expiry, exact replay, and
  differential Integrator decisions.
- Verify A transition/context paths and product/retained/V2/remote state unchanged.
- Blocking findings return to Developer.

### Step B8 — Mandatory QA

- Validate final reviewed B HEAD from a clean isolated input.
- Run the entire frozen B/A governance matrix and full TASK_368E pilot matrix; QA cannot reuse
  Reviewer outcomes as its own pass.
- Explicitly rerun frontend 61 tests/build with verified read-only runtime and no dependency install.
- Record all execution/result digests, environment, isolation, timing, retries, and one-owner proof.

### Step B9 — Integrator differential decision, pilot, and closeout

1. Verify package/ancestry/QA/clean/locks and run the decision helper before merge.
2. Merge locally only if authorized and conflict-free.
3. If differential predicates all pass, run ancestry, package/allowlist, protected paths,
   merge-sensitive smoke, execution gate, board/residual closeout, and necessary merged-tree
   integration checks. Otherwise run full validation.
4. Run/confirm the controlled medium TASK_368E replay with actual commands. Record Reviewer
   `4/7` executed and `3/7` reused (`42.9%` execution reduction), QA `7/7` executed, no archive/
   install, wall-clock, context, Planner transitions, retries, and result hashes in Integrator
   evidence.
5. Do not accept if >=40% reduction or any safety/performance target is missed. Close board/token
   through A's accepted helper and recurring maintenance contract; no push/destructive cleanup.

## 5. Validation Matrix

1. exact immutable independent command -> reuse;
2. covered path/direct dependency change -> rerun;
3. unrelated bounded authority/API/persistence change does not invalidate independent frontend;
4. schema/migration/public breaking/owner drift/unproven closure -> full;
5. missing/malformed/stale/mismatched/unknown/evidence/ancestry/environment facts -> full;
6. no force/ignore/assume/override CLI or manifest field;
7. TASK_368E four affected groups rerun; three unchanged XLSX/catalog/external-read, frontend-test,
   and frontend-build groups reuse in Reviewer;
8. QA executes all seven groups (`7/7`), including final frontend 61 tests/build;
9. Reviewer executes `4/7`, reuses `3/7`, and reduces command execution by `3/7 = 42.9%`;
10. Windows node paths canonicalize; invalid deselect blocks pre-execution;
11. argv-only execution resists shell metacharacter injection;
12. frontend runtime hash match passes read-only; mismatch/missing blocks without install;
13. shard temp/cache/coverage/frontend cache/dist are unique and outside repository;
14. same immutable HEAD/role/token permits backend/frontend concurrency; mismatch blocks;
15. result records/digests deterministic; missing/duplicate/stale/failed aggregate blocks;
16. unchanged active debt resolves by ledger/Git blob without base archive;
17. ledger drift/expiry/resolved/unknown requires fresh baseline comparison;
18. exact QA/clean merge/no drift -> differential Integrator checks;
19. conflict/package/dependency/environment/fixture/lock/unknown drift -> full Integrator validation;
20. medium real-command pilot metrics exist and meet targets;
21. A transition/context/handoff, WIP/token/worktree/role/V2/product/remote invariants pass.

## 6. Migration And Rollback

The feature is opt-in. No existing task manifest means full Reviewer validation. Ledger seed is
additive and cannot suppress unlisted failures. Rollback is local Git revert of B helpers/contracts/
ledger; removing a manifest returns to full re-gate. No data/schema migration, dependency install,
board-history mutation, or product rollback exists. A accepted authority remains intact.

## 7. Performance Evidence

All role evidence uses a common before/after table: manifest commands required/reused/executed;
Planner transitions; resolved context bytes; wall-clock; retry/failure count; frontend install
count; base archive count; shard concurrency/HEAD/token. Integrator acceptance requires Reviewer
execution <=4/7, QA 7/7, install=0, base archive=0 for unchanged debt, Planner routine transitions
=0 under A, and all hashes/results recorded.

## 8. Exact Scope And Gates

The B Task's enumerated May Touch/Must Not Touch/Locked Paths, serial dependency, lane identity, and
gates are normative. Any product path, A helper change, shared owner, unlisted fixture/test, remote/
runtime mutation, or performance waiver requires Planner/User reconciliation.

## 9. Stop Point

B remains planning-only. Wait for A local Integrator acceptance, then obtain separate User approval
before Step B0 or any implementation action.
